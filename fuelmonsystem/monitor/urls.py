from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from monitor import views

urlpatterns = [
    path('monitor/registeruser', views.RegisterUser.as_view()),
    path('monitor/registerdriver', views.RegisterDriver.as_view()),
    path('login', views.LoginView.as_view()),
    path('users', views.UserList.as_view()),
    path('drivers', views.DriverList.as_view()),
    path('monitor/sensors', views.SensorList.as_view()),
    path('monitor/trackers', views.GPStrackerList.as_view()),
    path('vehicles', views.VehicleList.as_view()),
    # path('monitor/generators', views.GeneratorList.as_view()),
    path('monitor/fuelrecords', views.FuelRecordList.as_view()),
    path('monitor/locations', views.LocationList.as_view()),
    path('trips', views.TripView.as_view()),
    path('monitor/sensor-readings', views.SensorReadingView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

