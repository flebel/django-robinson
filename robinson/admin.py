from django import forms
from django.contrib import admin
from robinson.models import *
from sorl.thumbnail.admin import AdminImageMixin


class ExifTagInline(admin.TabularInline):
    can_delete = False
    extra = 0
    max_num = 0
    model = ExifTag
    readonly_fields = ('key', 'value')

class ExifTagSubstituteAdmin(AdminImageMixin, admin.ModelAdmin):
    model = ExifTagSubstitute
    list_display = ('key', 'original_value', 'substitute_value', 'active')
    list_filter = ('active',)
    save_on_top = True
admin.site.register(ExifTagSubstitute, ExifTagSubstituteAdmin)

class PhotoAdmin(AdminImageMixin, admin.ModelAdmin):
    inlines = (ExifTagInline,)
    model = Photo
    list_display = ('__unicode__', 'filename', 'get_location', 'get_location_accuracy', 'latitude', 'longitude', 'get_elevation')
    list_filter = ('location_accuracy',)
    save_on_top = True
admin.site.register(Photo, PhotoAdmin)

