from django.contrib import admin

from myapp.models import *

# Register your models here.

admin.site.register(ContactList)
admin.site.register(Contact)

### IGNORE THESE ###
admin.site.register(Car)
admin.site.register(Year)