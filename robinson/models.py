from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from robinson import apis, utils
from robinson.exceptions import UnknownLocationError
from sorl.thumbnail import ImageField
from tagging.fields import TagField
import os
import pyexiv2
import uuid


def get_photo_upload_path(instance, filename):
    """
    Uses a random UUID to avoid filename collisions.
    """
    extension = os.path.splitext(filename)[1]
    return 'photos/%s%s' % (uuid.uuid4(), extension)

class ExifTag(models.Model):
    KEY_LENGTH = 256
    key = models.CharField(blank=False, max_length=KEY_LENGTH, null=False, verbose_name=_('Key'))
    value = models.TextField(blank=True, help_text=_("The human representation of the EXIF tag's value."), null=True, verbose_name=_('Value'))
    photo = models.ForeignKey('Photo')

    class Meta:
        unique_together = ('key', 'photo')

    @property
    def substituted_value(self):
        """
        Returns the substituted EXIF tag's value if an instance of
        ExifTagSubstitute matches the EXIF tag's key and current value,
        else returns the actual value of the tag.
        """
        # TODO: This code has room for improvement as a query is made for every
        # EXIF tag *displayed*, but for now it is the least of my concerns
        # as this project is deployed on an extremely low traffic site
        try:
            return ExifTagSubstitute.objects.filter(key=self.key, original_value=self.value).latest('pk').substitute_value
        except ObjectDoesNotExist:
            return self.value

class ExifTagSubstitute(models.Model):
    key = models.CharField(blank=False, max_length=ExifTag.KEY_LENGTH, null=False, verbose_name=_('Key'))
    original_value = models.TextField(blank=True, help_text=_("EXIF tag's value to replace."), null=True, verbose_name=_('Original value'))
    substitute_value = models.TextField(blank=True, null=True, verbose_name=_('Substitute value'))
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name=_('Active'))

    class Meta:
        verbose_name = 'EXIF tag substitute'
        verbose_name_plural = 'EXIF tag substitutes'

    def __unicode__(self):
        return self.key

class Photo(models.Model):
    IMPORT_ESTIMATED_LOCATION = 'UNDEFINED'
    # Room has been left in between the keys to make my life easier
    # in a few months from now ;-)
    LOCATION_ACCURACY_CHOICES = (
        (0, _('Way off!')),
        (10, _('Within 100 kilometers')),
        (20, _('Within 50 kilometers')),
        (30, _('Within 25 kilometers')),
        (40, _('Within 15 kilometers')),
        (50, _('Within 5 kilometers')),
        (60, _('Within 1 kilometer')),
        (70, _('Within 500 meters')),
        (80, _('Within 100 meters')),
        (90, _('Within 50 meters')),
        (100, _('Within 25 meters')),
        (110, _('Within 5 meters')),
    )
    LOCATION_ACCURACY_IN_METERS = {
        0: None,
        10: 100*1000,
        20: 50*1000,
        30: 25*1000,
        40: 15*1000,
        50: 5*1000,
        60: 1000,
        70: 500,
        80: 100,
        90: 50,
        100: 25,
        110: 5,
    }
    REQUIRED_EXIF_KEYS = ('Exif.GPSInfo.GPSAltitude',
                          'Exif.GPSInfo.GPSLatitude',
                          'Exif.GPSInfo.GPSLatitudeRef',
                          'Exif.GPSInfo.GPSLongitude',
                          'Exif.GPSInfo.GPSLongitudeRef')
    file = ImageField(upload_to=get_photo_upload_path, verbose_name=_('Photo'))
    name = models.CharField(blank=True, max_length=200, verbose_name=_('Name'))
    location = models.CharField(blank=True, help_text=_('You are required to specify a location if the JPEG file does not contain geolocation EXIF metadata.<br/>In the event that a JPEG file contains geolocation EXIF metadata, this location will be reverse geocoded and used as the location where the photo was taken.'), max_length=200, verbose_name=_('Location'))
    location_accuracy = models.SmallIntegerField(choices=LOCATION_ACCURACY_CHOICES, default=LOCATION_ACCURACY_CHOICES[-1][0], help_text=_('The estimated accuracy of the location.'), verbose_name=_('Location accuracy'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    tags = TagField()
    # The following fields are automatically set at save time
    filename = models.CharField(editable=False, max_length=256, verbose_name=_('Original filename'))
    estimated_location = models.CharField(blank=True, editable=False, max_length=200, null=True, verbose_name=_('Estimated location'))
    elevation = models.FloatField(blank=True, editable=False, null=True, verbose_name=_('Elevation (m)'))
    latitude = models.FloatField(blank=True, editable=False, null=True, verbose_name=_('Latitude'))
    longitude = models.FloatField(blank=True, editable=False, null=True, verbose_name=_('Longitude'))

    def __unicode__(self):
        name = self.name
        if not self.name:
            return self.get_location()
        return '%s (%s)' % (unicode(name), self.get_location())

    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        new_filename = os.path.split(self.file.name)[-1]
        temporary_file_path = self.file.file.file.name
        # Safeguard against the unsatisfactory bug fix for issue #1
        # https://github.com/flebel/django-robinson/issues/1
        if (self.pk):
            raise ValidationError(_('It is not possible to update the file of an existing instance. See issue #1 at https://github.com/flebel/django-robinson/issues/1 for more details.'))
        else:
            self.filename = new_filename
        metadata = pyexiv2.ImageMetadata(temporary_file_path)
        metadata.read()
        # Use the Geocoding and Elevation APIs to get the elevation,
        # latitude and longitude coordinates from the location specified
        if self.location:
            try:
                location = apis.geocode(self.location)
                self.estimated_location = location['formatted_address']
                self.latitude = location['geometry']['location']['arg'][0]
                self.longitude = location['geometry']['location']['arg'][1]
                elevation = apis.elevation(self.latitude, self.longitude)
                self.elevation = elevation
            except UnknownLocationError as e:
                raise ValidationError(e)
        # Set the elevation, latitude and longitude from the EXIF metadata if it
        # contains these informations
        elif set(self.REQUIRED_EXIF_KEYS).issubset(set(metadata.exif_keys)):
            self.elevation = metadata['Exif.GPSInfo.GPSAltitude'].value
            latitude_tuple = utils.get_latitude_tuple(metadata)
            latitude = utils.dms_to_decimal(latitude_tuple)
            longitude_tuple = utils.get_longitude_tuple(metadata)
            longitude = utils.dms_to_decimal(longitude_tuple)
            self.latitude = latitude * utils.get_latitude_ref_multiplier(metadata)
            self.longitude = longitude * utils.get_longitude_ref_multiplier(metadata)
            # Geocode the coordinates to estimate the address or place name
            latlon = '%f,%f' % (self.latitude, self.longitude)
            location = apis.geocode(latlon)
            self.estimated_location = location['formatted_address']
        else:
            # Raise the exception only if we are not importing photos from the
            # management command
            if not self.estimated_location == Photo.IMPORT_ESTIMATED_LOCATION:
                raise ValidationError(_("No EXIF GPS metadata was present in the file. " +
                    "Please enter a valid location."))
        # Get the instance's pk before we save it so that we can know its state
        # when we create the ExifTag instances for that photo a few lines below
        pk = self.pk
        super(Photo, self).save(*args, **kwargs)
        # https://github.com/flebel/django-robinson/issues/1
        # The following condition fixes a bug where there would be a
        # ValidationError: [u'Select a valid choice. That choice is not one of
        # the available choices.'] exception thrown when updating an instance
        # of the Photo model that is referred from ExifTag instances
        # For now, the unsatisfactory solution is that the EXIF tags are saved
        # only when the Photo instance is initially created
        if pk is None:
            for key in metadata.exif_keys:
                ExifTag.objects.create(key=key, value=metadata[key].human_value, photo=self)

    def is_valid(self):
        """
        Returns True if the estimated_location is valid.
        """
        return not self.estimated_location == Photo.IMPORT_ESTIMATED_LOCATION

    def set_invalid(self):
        """
        Sets a flag in the estimated_location field because the geolocation
        data is invalid.
        """
        self.estimated_location = Photo.IMPORT_ESTIMATED_LOCATION

    def set_file(self, file):
        """
        Sets the photo's file to the file for which the path and filename
        is given as an argument.
        """
        filename = os.path.split(file)[-1]
        with open(file) as content:
            self.file.save(filename, File(content), False)

    def get_elevation(self):
        """
        Returns the elevation with its unit suffix.
        """
        if self.elevation:
            return unicode(round(self.elevation, 2)) + ' m'
    get_elevation.short_description = _('Elevation')

    def get_location(self):
        """
        Returns the estimated location unless a location was manually
        specified.
        """
        if self.location:
            return self.location
        return self.estimated_location
    get_location.short_description = _('Location')

    def get_location_accuracy(self):
        """
        Proxies a call to get_location_accuracy_display() so that we are
        able to set the short_description in the admin for the field.
        """
        return self.get_location_accuracy_display();
    get_location_accuracy.short_description = _('Location accuracy')

