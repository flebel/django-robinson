from django.db import models
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from robinson import utils
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
    key = models.CharField(blank=False, max_length=256, null=False, verbose_name=_('Key'))
    value = models.TextField(blank=True, help_text=_("The human representation of the EXIF tag's value."), null=True, verbose_name=_('Value'))
    photo = models.ForeignKey('Photo')
    
    class Meta:
        unique_together = ('key', 'photo')

class Photo(models.Model):
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
    REQUIRED_EXIF_KEYS = ('Exif.GPSInfo.GPSAltitude',
                          'Exif.GPSInfo.GPSLatitude',
                          'Exif.GPSInfo.GPSLatitudeRef',
                          'Exif.GPSInfo.GPSLongitude',
                          'Exif.GPSInfo.GPSLongitudeRef')
    file = ImageField(upload_to=get_photo_upload_path, verbose_name=_('Photo'))
    name = models.CharField(blank=True, max_length=200, verbose_name=_('Name'))
    location = models.CharField(blank=True, help_text=_('You are required to specify a location if the JPEG file does not contain geolocation EXIF metadata.'), max_length=200, verbose_name=_('Location'))
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

    def save(self, *args, **kwargs):
        new_filename = os.path.split(self.file.name)[-1]
        temporary_file_path = self.file.file.file.name
        # Do not update the original filename if it is the same as the
        # uploaded filename because that would mean that the file wasn't
        # modified and we would lose the original filename!
        if (not new_filename == os.path.split(temporary_file_path)[-1]):
            self.filename = new_filename
        metadata = pyexiv2.ImageMetadata(temporary_file_path)
        metadata.read()
        # Set the elevation, latitude and longitude from the EXIF data if it
        # contains these informations
        if set(self.REQUIRED_EXIF_KEYS).issubset(set(metadata.exif_keys)):
            self.elevation = metadata['Exif.GPSInfo.GPSAltitude'].value.to_float()
            latitude_tuple = utils.get_latitude_tuple(metadata)
            latitude = utils.dms_to_decimal(latitude_tuple)
            longitude_tuple = utils.get_longitude_tuple(metadata)
            longitude = utils.dms_to_decimal(longitude_tuple)
            self.latitude = latitude * utils.get_latitude_ref_multiplier(metadata)
            self.longitude = longitude * utils.get_longitude_ref_multiplier(metadata)
            # Geocode the coordinates to estimate the address or place name
            latlon = '%f,%f' % (self.latitude, self.longitude)
            location = utils.geocode(latlon)
            self.estimated_location = location['formatted_address']
        elif self.location:
            try:
                # Use the Geocoding and Elevation APIs to get the elevation,
                # latitude and longitude coordinates
                location = utils.geocode(self.location)
                self.estimated_location = location['formatted_address']
                self.latitude = location['geometry']['location']['arg'][0]
                self.longitude = location['geometry']['location']['arg'][1]
                elevation = utils.elevation(self.latitude, self.longitude)
                self.elevation = elevation
            except UnknownLocationError as e:
                raise ValidationError(e)
        else:
            raise ValidationError(_("No EXIF GPS metadata was present in the file. " +
                "Please enter a valid location."))
        super(Photo, self).save(*args, **kwargs)
        # Delete all EXIF tags associated to the photo then add them again.
        # This is required to support to change the JPEG file associated
        # with this model instance. This has to be done after the instance
        # has been saved as we are passing the current photo instance to
        # the ExifTag instances to be created.
        ExifTag.objects.filter(photo=self).delete()
        for key in metadata.exif_keys:
            ExifTag.objects.create(key=key, value=metadata[key].human_value, photo=self)

    def get_elevation(self):
        """
        Returns the elevation with its unit suffix.
        """
        if self.elevation:
            return unicode(self.elevation) + ' m'
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

