
import socket
import threading
import os
import django
import signal
import sys

import re
import json
import http.client
from urllib.parse import urlparse

#Globals
django_server_url = 'http://127.0.0.1/report/' # Django server URL


def send_data_to_django_server(url, data):
    parsed_url = urlparse(url)
    conn = http.client.HTTPConnection(parsed_url.hostname, parsed_url.port)
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)
    print(json_data)
    conn.request('POST', parsed_url.path, body=json_data, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode()
    print(f"Response from Django server: {response.status}, {response_data}")


def utf16_to_ascii(utf16_str):
    return bytes.fromhex(utf16_str).decode('utf-16')
    
def s32(value):
    return -(value & 0x80000000) | (value & 0x7fffffff)

def compute_anc_compare_crc(received_message, received_crc):
   # received_message = received_message.replace(received_crc , '')
    print(received_message)
    computed_crc = 0;
    
    for c in received_message:
        computed_crc += ord(c);
        
    print()
    print(computed_crc)
    print(int(received_crc, 16));
    print()
        
    computed_crc = 0;
    return (computed_crc == int(received_crc, 16))



def decode_A_report(message):
    parts = message.split(' ')
    if len(parts) < 5:
        raise ValueError("Unexpected message format: not enough parts in the message")
        
    #print(parts);
    #['A', 'P', '6666:869731053615829', '230320064050|7DE9478|1921F540|2E|0|0|40000000,S2D7|4C1,1.00,C128,1:0:FFFF:EH17:PW11.4||CR50A_1.27|', '1C57']
    
    #Decode DeviceID and Imei (Index 2 of message parts list), get 2 elements
    dev_id_and_imei = str(parts[2]).split(':')
    device_id = dev_id_and_imei[0]
    imei = dev_id_and_imei[1]

    #Decode Data (Index 3 of message parts list), get 5 elements
    report_data = str(parts[3]).split(',')
    #print(len(report_data))

    ##Decode Location (index 0 of report data) 7 elements
    location_data = str(report_data[0]).split("|")
    ###Loc_data__Time(index 0)
    time = location_data[0]

    ###Loc_data__Latitude (index 1)     ###Loc_data__Longitude (index 2)
    latitude_hex = location_data[1]
    longitude_hex = location_data[2]
   
    ###Loc_data__Altitude (index 3)
    altitude_hex = location_data[3]
    
    ###Loc_data__Course (ind deg) (index 4)
    course_hex =  location_data[4]
    
    ###Loc_data__Speed (in km/hour) (index 1)
    speed_hex =  location_data[5]
    
    ###Loc_data__Alarm
    alarm_hex = location_data[6]


    ##Decode  Trailer Id and Status (index 1 of report Data)
    trailer_id_and_status = str(report_data[1]).split("|")
    ###Trailer__ID
    trailler_id = trailer_id_and_status[0]

    ###Trailer__status
    status = trailer_id_and_status[1]
    
    ##Decode Mileage (index 2 of report data)
    mileage = report_data[2]
    
    ##Decode ADvalue (index 3 of report data)
    ad_value = report_data[3]
    
    ##Decode Sensor values ( index 4 of report data)
    sensor_readings = str(report_data[4]).split('|')
    
    fuel_eh_power_n_readings = str(sensor_readings[0]).split(':')
    ###Fuel1 Fuel2 Fuel3
    fuel1_level = fuel_eh_power_n_readings[0];
    fuel2_level = fuel_eh_power_n_readings[1];
    fuel3_level = fuel_eh_power_n_readings[2];
    
    ###EH (engine work time in Minutes)
    engine_work_time_mn = fuel_eh_power_n_readings[3];
    
    ###PW (power level in Volts )
    power_volts =  fuel_eh_power_n_readings[4]
    
    ##Decode Trailler
    camera_info = sensor_readings[1]
    firmware_version = sensor_readings[2]
    ack = sensor_readings[3]
    
    #Decode Cyclic Redundancy Check (CRC) (From Index 4 of message parts list) 
    crc = parts[4] 
    
    
    #convert time
    yy, mm, dd, hh, mi, ss = time[:2], time[2:4], time[4:6], time[6:8], time[8:10], time[10:12]
    formatted_time = f"20{yy}-{mm}-{dd} {hh}:{mi}:{ss}"

    
    # Convert latitude and longitude
    latitude = (s32(int(latitude_hex, 16)))/(1000*60*60)
    longitude = (s32(int(longitude_hex, 16)))/(1000*60*60) 
    
    # Convert other data
    altitude = int(altitude_hex, 16)
    course = int(course_hex, 16)
    speed = int(speed_hex, 16) / 1000
    alarm_status = alarm_hex
    
    status = status
    mileage = float(mileage)
    gsm_signal = int(ad_value[2:])
    fuel_levels = [int(fuel1_level, 16)/10 , int(fuel2_level, 16)/10, int(fuel3_level, 16)/10]
    
    eh =  float(engine_work_time_mn[2:])
    pw = float(power_volts[2:])

    decoded_data = {
        "report_type": "position",
        "device_id": device_id,
        "IMEI": imei,
        "time": formatted_time,
        "latitude_degrees": latitude,
        "longitude_degrees": longitude,
        "altitude": altitude,
        "course": course,
        "speed_km_per_hour": speed,
        "alarm_status": alarm_status,
        "status": status,
        "mileage": mileage,
        "gsm_signal": gsm_signal,
        "fuel_levels_percentage": fuel_levels[0],
        "engine_hours": eh,
        "power_level_volts": pw
    }
    #print(decoded_data["Time"])
    return decoded_data
##End of decode_A_report packet decoder
 

    
    
#POSITION
def decode_A_P(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "position"
    return decoded_data;

#LAST LOCATION
def decode_A_L(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "last_location"
    return decoded_data;
    
#POWER CUT
def decode_A_C(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "power_cut"
    return decoded_data;

#POWER BAD CONNECT
def decode_A_J(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "power_bad_connect"
    return decoded_data;
    
#FUEL REFILL
def decode_A_F(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "fuel_refill";
    return decoded_data;

#FUEL LOST
def decode_A_S(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "fuel_lost";
    return decoded_data;
 
#FUEL LEVEL LOW
def decode_A_W(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "fuel_level_low";
    return decoded_data; 

#STOP REPORT
def decode_A_T(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "stop_report";
    return decoded_data;
    
#FUEL SENSOR DAMAGED
def decode_A_E(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "fuel_sensor_damaged";
    return decoded_data;

#TRAILER CONNECTED
def decode_A_Y(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "trailer_connected";
    return decoded_data;
    
#TRAILER DISCONNECTED
def decode_A_X(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "trailer_disconnected";
    return decoded_data;

#FIRMWARE UPDATE SUCCESS
#FIRMWARE UPDATE FAIL
#SNAPSHOT

    
#COMMAND RESPOND
def decode_A_R(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "command_respond";
    return decoded_data;
    
    
#READ YSER CARD REPORT
#FLOW REPORT
#PICTURE UPLOAD SUCCESS
#PICTURE UPLOAD FAIL

#TOP_RPT
def decode_A_1(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "tow_rpt";
    return decoded_data;

#ACC_ON_REPORT
def decode_A_3(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "acc_on";
    return decoded_data;

#ACC_OFF_REPORT
def decode_A_4(message):
    decoded_data = decode_A_report(message)
    decoded_data["report_type"] = "acc_off";
    return decoded_data;
    

#SPEEDING REPORT
#SPEED NORMAL
#PT0_ON
#PTO_OFF
#SOS
#CUT RELAY OPEN
#IDLE_START
#IDLE_STOP
#HARSH ACCELERATE
#EMERGENCE BRAKE
#HARSH CORNER
#FATIGUE DRIVING
#CRASH EVENT
#TANK EMPTY EVENT
#DEVICE RESET


#KEEP ALIVE (Decode HeartBeat packet)
def decode_A_K(message):
    parts = message.split(' ')
    if len(parts) < 4:
        raise ValueError("Unexpected message format: not enough parts in the message")
        
    #print(parts);
    #['A', 'K', 'OEMCODE:COMADDR']
    
    #Decode DeviceID and Imei (Index 2 of message parts list), get 2 elements
    dev_id_and_imei = str(parts[2]).split(':')
    
    device_id =dev_id_and_imei[0]
    imei = dev_id_and_imei[1]
    received_crc = parts[3]
    
    #Compute CRC of the received data and compare with the received CRC
    #if (compute_anc_compare_crc(message, received_crc) == True)

    
    #Decode Data (Index 3 of message parts list), get 5 elements
    report_data = str(parts[3]).split(',')
    #print(len(report_data))

    decoded_data = {
        "report_type": "heartbeat",
        "device_id": device_id,
        "IMEI": imei,
    }
    return decoded_data
##End of heartbeat packet decoder



        
    
#Message decoder selector function
def decode_message(message):
    if message.startswith("A K "): #KEEP ALIVE
        return decode_A_K(message)
    elif message.startswith("A P "):
        return decode_A_P(message)
    elif message.startswith("A L "):
        return decode_A_L(message)
    elif message.startswith("A C "):
        return decode_A_C(message)
    elif message.startswith("A J "):
        return decode_A_J(message)
    elif message.startswith("A F "): #REFILL
        return decode_A_F(message)
    elif message.startswith("A S "): #LOST
        return decode_A_S(message)
    elif message.startswith("A W "): #LEVEL LOW
        return decode_A_W(message)
    elif message.startswith("A T "): #LEVEL LOW
        return decode_A_T(message)
    elif message.startswith("A E "): 
        return decode_A_E(message)
    elif message.startswith("A Y "):
        return decode_A_Y(message)
    elif message.startswith("A X "): 
        return decode_A_X(message)
    elif message.startswith("A R "):
        return decode_A_R(message)
    elif message.startswith("A 1 "):
        return decode_A_1(message)
    elif message.startswith("A 3 "):
        return decode_A_3(message)
    elif message.startswith("A 4 "):
        return decode_A_4(message)
    else:
        raise ValueError("Unsupported message type")
        
        


















# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_tracker.settings')
django.setup()

from locapp.models import DataRecord

# Global flag to indicate server status
running = True
server = None

def handle_client(client_socket):
    while running:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            decoded_data = data.decode('utf-8')
            print(f"Received data: {decoded_data}")
            
            decoded_message = decode_message(decoded_data)
            print(decoded_message)
            send_data_to_django_server(django_server_url, decoded_message)
            #DataRecord.objects.create(data=decoded_data)
        except ConnectionResetError:
            break
    client_socket.close()


def start_server(host='0.0.0.0', port=9999):
    global running, server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Listening on {host}:{port}")

    def signal_handler(sig, frame):
        global running, server
        print('Shutting down server...')
        running = False
        if server:
            server.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while running:
        try:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        except socket.error:
            break

if __name__ == "__main__":
    start_server()
