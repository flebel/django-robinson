from django.core.management.base import BaseCommand, CommandError
from robinson.models import Photo
import glob
import os


# Look for files with a 'JPG' or 'JPEG' extension (case insensitive.)
# Note that glob does not support regular expressions, hence the duplication.
JPEG_EXTENSIONS = ('[jJ][pP][gG]', '[jJ][pP][eE][gG]')

class Command(BaseCommand):
    args = 'path_to_files'
    help = 'Imports all files with the JPG/JPEG (case insensitive) extension within the given directory (NOT recursive).'

    def handle(self, *args, **options):
        if not args:
            raise CommandError('The path to the files must be specified.')
        # Convert the given directory into an absolute path and
        # normalize its case
        directory = os.path.realpath(os.path.normcase(args[0]))
        self.run(directory)

    def run(self, directory):
        files = []
        for extension in JPEG_EXTENSIONS:
            file_glob = "%s.%s" % (os.path.join(directory, '*'), extension)
            files.extend(glob.glob(file_glob))
        files.sort()
        for file in files:
            photo = Photo()
            # Set the estimated location to a specific flag as a way to
            # determine if the photo has valid geolocation data
            photo.estimated_location = Photo.UNDEFINED_ESTIMATED_LOCATION
            photo.filename = os.path.split(file)[-1]
            photo.set_file(file)
            photo.save()

