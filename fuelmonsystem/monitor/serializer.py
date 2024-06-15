from monitor.models import User, Vehicle, Generator, Sensor, SensorReading, Location, FuelRecord, GPStracker, Trip, Driver
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'userID',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            'driverID',
            'first_name',
            'last_name',
            'licence_no',
            'VIN',
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['VIN', 'model', 'tank_capacity', 'fuel_type', 'sensorID', 'trackerID']

class GeneratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generator
        fields = ['serialnumber', 'tank_capacity', 'fuel_type', 'sensorID', 'trackerID']

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['sensorID']

class GPStrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPStracker
        fields = ['trackerID']

class FuelRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelRecord
        fields = ['recordID', 'vehicle', 'generator', 'date', 'time', 'fuel_level']

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = "__all__"

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['locationID', 'trackerID', 'coordinates']


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['tripID', 'departure', 'destination','volumeToBeUsed', 'date', 'VIN']