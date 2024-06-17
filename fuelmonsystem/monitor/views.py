from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from monitor.models import User, Vehicle, Generator, Sensor, SensorReading, Location, FuelRecord,GPStracker, Trip, Driver
from monitor.serializer import UserSerializer,FuelRecordSerializer, VehicleSerializer, GeneratorSerializer, SensorSerializer, GPStrackerSerializer, LocationSerializer, SensorReadingSerializer, TripSerializer, DriverSerializer
from django.contrib.auth import authenticate, login, update_session_auth_hash
from .token import get_user_token
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .report_decoder import decode_message
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re

from .models import ReceivedData

# Create your views here.
class LoginView(APIView):
    @staticmethod
    def post(request):
        email = request.data.get('email')
        password = request.data.get('password')
        print('Data: ', email, password)
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            userID = User.objects.get(email=email)
            print(userID)
            user_info = UserSerializer(instance=userID, many=False).data
            print(user_info)
            response = {
                'token': get_user_token(userID),
                'user': user_info
            }

            return Response(response)
        else:
            response = {
                'msg': 'Invalid username or password',
            }

            return Response(response)

class RegisterUser(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        data = request.data
        print(request.data)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            email = data['email']
            user = User.objects.filter(email=email)
            if user:
                message = {'status': False, 'message': 'Username already exists'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            message = {'save': True}
            return Response(message)

        message = {'save': False, 'errors': serializer.errors}
        return Response(message)


class RegisterDriver(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        data = request.data
        print(request.data)
        serializer = DriverSerializer(data=data)
        if serializer.is_valid():
            license_no = data['licence_no']
            user = User.objects.filter(license_no=license_no)
            if user:
                message = {'status': False, 'message': 'Username already exists'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            message = {'save': True}
            return Response(message)

        message = {'save': False, 'errors': serializer.errors}
        return Response(message)
    
class DriverList(APIView):
    """
    get users list
    """
    def get(self, request, format=None):
        drivers = Driver.objects.all()
        serializer = DriverSerializer(drivers, many=True)
        return Response(serializer.data)
    
class UserList(APIView):
    """
    get users list
    """
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
class VehicleList(APIView):
    """
    list all vehicle or register a vehicle
    """
    def get(self, request, format=None):
        vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = VehicleSerializer(data=request.data)
        if serializer .is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST )
    
class GeneratorList(APIView):
    """
    list all generators or register a generator
    """
    def get(self, request, format=None): 
        generators = Generator.objects.all()
        serializer = GeneratorSerializer(generators, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = GeneratorSerializer(data=request.data)
        if serializer .is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST )
    
class SensorList(APIView):
    """
    list all sensors or register sensor
    """
    def get(self, request, format=None):
        sensors = Sensor.objects.all()
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = SensorSerializer(data=request.data)
        if serializer .is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LocationList(APIView):
    """
    list tracked locations 
    """
    def get(self, request, format=None):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)
    
    # def post
    
class GPStrackerList(APIView):
    """
    list all GPStracker or register GPStracker
    """
    def get(self, request, format=None):
        trackers = GPStracker.objects.all()
        serializer = GPStrackerSerializer(trackers, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = GPStrackerSerializer(data=request.data)
        if serializer .is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SensorReadingView(APIView):
    permission_classes = [AllowAny]
    """
    list and post all SensorReadings
    """
    def get(self, request, format=None):
        readings = SensorReading.objects.all()
        serializer = SensorReadingSerializer(readings, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = SensorReadingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FuelRecordList(APIView):
    """
    get fuel record list 
    """
    def get(self, request, format=None):
        fuelrecords = FuelRecord.objects.all()
        serializer = FuelRecordSerializer(fuelrecords, many=True)
        return Response(serializer.data)

class TripView(APIView):
    """
    get and set trips
    """
    def get(self, request, format=None):
        trips = Trip.objects.all()
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class ReportDecoder(APIView):
#     decode_message(message)



# @csrf_exempt
def capture_device_data(request):
    if request.method == 'POST':
        raw_data = request.body.decode('utf-16')
        # Process the raw data here
        print("Start Here")
        print(parsed_data)
        print("Ends Here")
        parsed_data = parse_device_data(raw_data)
        # You can store parsed_data in the database or perform other actions
        return JsonResponse({'status': 'success', 'data': parsed_data})
    return JsonResponse({'status': 'failure', 'message': 'Only POST requests are allowed'}, status=400)

def parse_device_data(raw_data):
    # This is a placeholder for the parsing logic
    # Split the string and extract the needed parts
    return raw_data  # Replace with actual parsed data



def received_data_view(request):
    received_data = ReceivedData.objects.all()
    return render(request, 'socketapp/received_data.html', {'received_data': received_data})


@csrf_exempt  # Only for testing purposes. Ensure CSRF protection in production.
def custom_request_view(request):
    if request.method not in ['POST', 'GET']:
        try:
            # Capture the request body
            body = request.body.decode('utf-8')
            
            # Log the request body for debugging purposes
            print(f"Received custom request: {body}")
            
            # Extract data using a regular expression or string manipulation
            # Example regular expression to extract data
            pattern = re.compile(r"A P (?P<device>\w+):(?P<id>\w+) (?P<data>.*)")
            match = pattern.match(body)
            
            if match:
                device = match.group('device')
                device = match.group('id')
                data = match.group('data')
                
                # Save extracted data to the database
                print(f"Received data: {data}")
                print(device,device,device)
                # your_model_instance = YourModel(device=device, device_id=device_id, data=data)
                # your_model_instance.save()
                
                return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid data format'}, status=400)
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
