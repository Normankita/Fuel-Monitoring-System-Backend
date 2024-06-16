# socket_handler.py

import socket
import threading
from django.conf import settings
from .models import ReceivedData  # Import your model for storing data

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        decoded_data = data.decode()
        print(f"Received data: {decoded_data}")  # Print received data to console

        # Store received data in Django model if enabled
        if settings.STORE_RECEIVED_DATA:
            ReceivedData.objects.create(data=decoded_data)

    client_socket.close()

def start_socket_server():
    if settings.RUN_SOCKET_SERVER:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 8000))  # Bind to all available interfaces on port 8000
        server_socket.listen(5)

        print("Socket server listening on port 8000...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

        server_socket.close()
    else:
        print("Socket server is not enabled in settings.")
