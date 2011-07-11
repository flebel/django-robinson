========
Robinson
========

Robinson is a Django application that can be used as the underlying foundation for a project that stores references to JPEG files as model instances. Projects that make use of the files' EXIF metadata can benefit from Robinson's automatic import of EXIF metadata at the time the model is saved. Moreover, Robinson offers built-in geolocation utility methods as well as fully functional admin forms that make it trivial to geocode photos that are missing geolocation EXIF metadata. As of right now, this application forces every photo to have a location, either specified manually through the admin form or automatically imported from the file's EXIF metadata. There are future plans to make it suitable for less specific use cases.

Currently, the following features have been written and are functional:

- Estimates the elevation from the latitude and longitude coordinates
- Geocodes a readable address or place name specified in the admin form when no geolocation data is found in the EXIF metadata
- Reverse geocodes latitude and longitude coordinates to a readable address or place name
- Stores the EXIF metadata of the JPEG files in the database

These are the features that are planned for future versions, in order of priority:

- Write a demo app, deploy and open-source it
- Add an admin form to replace EXIF tag values with hardcoded values, ie. to correct the name of a misidentified third party lens
- Store the weather for the location at the time the photo was taken
- Write a management command to tag photos according to their location (ie. tag by country, state and city)
- Support photos without a specified location, either estimated or with latitude and longitude coordinates
- Move the geocoding and elevation API calls to the client's browser to leverage the 2,500 geolocation requests per day limits
- Add support for multiple maps and users
- Support alternative geocoding, reverse geocoding and elevation APIs (ie. replace django-gmapi with geopy)

Installation
============

#. Add the `django-robinson` directory to your Python path.

#. Add `robinson` to the `INSTALLED_APPS` collection found in the `settings.py` file for your project.

#. Install the following Django apps and repeat the first two steps as necessary:

   * `django-gmapi` **(fork)**: http://code.google.com/r/francoislebel-django-gmapi/
   * `sorl-thumbnail`: https://github.com/sorl/sorl-thumbnail
   * `django-tagging`: http://code.google.com/p/django-tagging/

#. Install `pyexiv2` 0.3.0: http://tilloy.net/dev/pyexiv2/

Configuration
=============

Robinson does not yet have any configurable options.

Management command
==================

`importphotos`: Accepts the path to a directory containing files with a JPG or JPEG extension (case insensitive) as a positional argument and imports all photos in that directory, non recursively. The photos that do not contain geolocation EXIF metadata will be imported but it will be necessary to set their location manually through the admin form.

Issues
======

- A workaround for issue #1 (https://github.com/flebel/django-robinson/issues/1) has made it impossible to update the file associated with an instance of a Photo model; you will need to recreate an instance if you want to update a file
- Google Geocoding and Elevation APIs are subject to a query limit of 2,500 geolocation requests per day, per IP address. The geocoding is done on the server, thus potentially limiting the geolocation requests for other applications sharing the external IP address
- The application is currently limited to a single map which can be edited by any user with the right permissions

