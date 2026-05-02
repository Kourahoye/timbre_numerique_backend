from django.contrib import admin

from timbre.models import PriceAssignation, Session, Timbre, TypeTimbre

# Register your models here.
admin.site.register([Session, Timbre, TypeTimbre, PriceAssignation])