import socket

server_ip = '18.217.109.178'
server_port = 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Example data to send
data_to_send = b"Hello from client"

client_socket.sendall(data_to_send)
client_socket.close()
