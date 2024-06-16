def utf16_to_ascii(utf16_str):
    return bytes.fromhex(utf16_str).decode('utf-16')

def decode_A_P(message):
    parts = message.split(' ')
    if len(parts) < 5:
        raise ValueError("Unexpected message format: not enough parts in the message")
        
    #print(parts);
    #['A', 'P', '6666:869731053615829', '230320064050|7DE9478|1921F540|2E|0|0|40000000,S2D7|4C1,1.00,C128,1:0:FFFF:EH17:PW11.4||CR50A_1.27|', '1C57']
    
    
    #Decode DeviceID and Imei (Index 2 of message parts list), get 2 elements
    dev_id_and_imei = str(parts[2]).split(':')
    print()
    print()
    device_id = dev_id_and_imei[0]
    imei = dev_id_and_imei[1]
    print(device_id)
    print(imei)
    
    #Decode Data (Index 3 of message parts list), get 5 elements
    report_data = str(parts[3]).split(',')
    #print(len(report_data))
    print()
   
   
    ##Decode Location (index 0 of report data) 7 elements
    location_data = str(report_data[0]).split("|")
    ###Loc_data__Time(index 0)
    time = location_data[0]
    print(time)
    
    ###Loc_data__Latitude (index 1)     ###Loc_data__Longitude (index 2)
    latitude_hex = location_data[1]
    longitude_hex = location_data[2]
    print(latitude_hex)
    print(longitude_hex)
   
    
    ###Loc_data__Altitude (index 3)
    altitude_hex = location_data[3]
    print(location_data[3])
    
    ###Loc_data__Course (ind deg) (index 4)
    course_hex =  location_data[4]
    print(location_data[4])
    
    ###Loc_data__Speed (in km/hour) (index 1)
    speed_hex =  location_data[5]
    print(location_data[5])
    
    ###Loc_data__Alarm
    alarm_hex = location_data[6]
    print(alarm_hex)
    print()

    
    ##Decode  Trailer Id and Status (index 1 of report Data)
    trailer_id_and_status = str(report_data[1]).split("|")
    ###Trailer__ID
    trailler_id = trailer_id_and_status[0]
    print(trailler_id)
    ###Trailer__status
    status = trailer_id_and_status[1]
    print(status)
    print()
    
    
    ##Decode Mileage (index 2 of report data)
    mileage = report_data[2]
    print(mileage)
    print()
    
    
    
    ##Decode ADvalue (index 3 of report data)
    ad_value = report_data[3]
    print(ad_value)
    print()
    
    
    ##Decode Sensor values ( index 4 of report data)
    sensor_readings = str(report_data[4]).split('|')
    
    fuel_eh_power_n_readings = str(sensor_readings[0]).split(':')
    ###Fuel1 Fuel2 Fuel3
    fuel1_level = fuel_eh_power_n_readings[0];
    fuel2_level = fuel_eh_power_n_readings[1];
    fuel3_level = fuel_eh_power_n_readings[2];
    print(fuel1_level)
    print(fuel2_level)
    print(fuel3_level)
    
    ###EH (engine work time in Minutes)
    engine_work_time_mn = fuel_eh_power_n_readings[3];
    print(engine_work_time_mn)
    
    ###PW (power level in Volts )
    power_volts =  fuel_eh_power_n_readings[4]
    print(power_volts)
    
    
    ##Decode Trailler
    camera_info = sensor_readings[1]
    firmware_version = sensor_readings[2]
    ack = sensor_readings[3]
    print(camera_info)
    print(firmware_version)
    print(ack)
    
    
    
  
    
    #Decode Cyclic Redundancy Check (CRC) (From Index 4 of message parts list) 
    crc = parts[4]
    print(crc)
    print()
    print()
    print()    
    
    
   

    #convert time
    yy, mm, dd, hh, mi, ss = time[:2], time[2:4], time[4:6], time[6:8], time[8:10], time[10:12]
    formatted_time = f"20{yy}-{mm}-{dd} {hh}:{mi}:{ss}"
    print(formatted_time)
    
    # Convert latitude and longitude
    print("Latitude")
    print(latitude_hex)
    latitude = int(latitude_hex, 16) / 1000 / 3600
    longitude = int(longitude_hex, 16) / 1000 / 3600

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
    
    
    
    

def decode_message(message):
    if message.startswith("A P "):
        return decode_A_P(message)
        #elif message.startswith("A B ");
    # Add more decoders here for other message types as needed.
    else:
        raise ValueError("Unsupported message type")





def main():
    # Example usage
    messages = [
    "A P Device0001:862205059415127 240612143151|FEAAA002|7AF0220|29|161|E74|0,S0|40200102,110.01,C124,0:0:FFFF:EH0:PW3.9||CR50_1.35| 1E44"]
     #  "A P 6666:869731053615829 230320064050|7DE9478|1921F540|2E|0|0|40000000,S2D7|4C1,1.00,C128,1:0:FFFF:EH17:PW11.4||CR50A_1.27| 1C57"
        # Add more example messages here
    #]


    for msg in messages:
        try:
            decoded_message = decode_message(msg)
            print(decoded_message)
        except ValueError as e:
            print(f"Error decoding message '{msg}': {e}")

if __name__ == "__main__":
    main()
