
import socket
import threading
import os
import django
import signal
import sys


def utf16_to_ascii(utf16_str):
    return bytes.fromhex(utf16_str).decode('utf-16')
    
def s32(value):
    return -(value & 0x80000000) | (value & 0x7fffffff)

def decode_A_P(message):
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
        "fuel_evels_percentage": fuel_levels,
        "engine_hours": eh,
        "power_level_volts": pw
    }
    
   # print(decoded_data["Time"])

    return decoded_data
    
    
    
def decode_A_K(message):
 return ""
 
def decode_A_F(message):
 return ""
    

def decode_message(message):
    if message.startswith("A P "):
        return decode_A_P(message)
    elif message.startswith("A K "):
        return decode_A_K(message)
    elif message.startswith("A_F"):
        return decode_A_F(message)
        
        #elif message.startswith("A B ");
    # Add more decoders here for other message types as needed.
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
            
            print(decode_message(decoded_data))
            DataRecord.objects.create(data=decoded_data)
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
