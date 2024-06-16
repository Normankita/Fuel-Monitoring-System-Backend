from django.contrib import admin
from .models import ReceivedData, User,Sensor,GPStracker,Vehicle,Generator,SensorCallibration,SensorReading,FuelRecord,Location, Trip, Driver

# Register your models here.

admin.site.register(User)
admin.site.register(Sensor)
admin.site.register(GPStracker)
admin.site.register(Vehicle)
# admin.site.register(Generator)
admin.site.register(SensorCallibration)
admin.site.register(SensorReading)
admin.site.register(FuelRecord)
admin.site.register(Location)
admin.site.register(Trip)
admin.site.register(Driver)
admin.site.register(ReceivedData)