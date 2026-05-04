from django.contrib import admin

from timbre.models import Notification, PriceAssignation, Session, Timbre, Transaction, TypeTimbre

# Register your models here.
admin.site.register([Session, Timbre, TypeTimbre, PriceAssignation,Transaction,Notification])