# Assuming your data format is something like "A K Device0001:862205059415127 674"

from django.conf import settings
from .models import ReceivedData

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        decoded_data = data.decode().strip()  # Remove any leading/trailing whitespace

        # Example: Parse your data format to extract meaningful information
        # Example assumption: "A K Device0001:862205059415127 674"
        parts = decoded_data.split()
        if len(parts) >= 3:
            device_id = parts[2]
            sensor_value = parts[-1]

            # Example: Store relevant data into ReceivedData model
            if settings.STORE_RECEIVED_DATA:
                try:
                    ReceivedData.objects.create(device_id=device_id, sensor_value=sensor_value, raw_data=decoded_data)
                    print("Data saved successfully.")
                except Exception as e:
                    print(f"Error saving data: {e}")
        else:
            print(f"Invalid data format: {decoded_data}")

    client_socket.close()
