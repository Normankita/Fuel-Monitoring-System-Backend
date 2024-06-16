# socketapp/socket_handler.py
from django.conf import settings
import socket
import threading

def handle_client(client_socket):
    from .models import ReceivedData  # Import inside function to avoid AppRegistryNotReady

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        # Process the received data as needed
        decoded_data = data.decode()
        print(f"Received data: {decoded_data}")

        # Store received data in a Django model
        if settings.STORE_RECEIVED_DATA:
            ReceivedData.objects.create(data=decoded_data)

    client_socket.close()

def start_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('18.217.109.178', 8000))  # Replace with your desired IP and port
    server_socket.listen(5)

    print("Socket server listening...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

    server_socket.close()

# Conditional initialization of socket server
if settings.RUN_SOCKET_SERVER:
    start_socket_server()
