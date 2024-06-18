import tornado.ioloop
import tornado.tcpserver
import tornado.iostream
import requests

class SimpleTCPServer(tornado.tcpserver.TCPServer):
    async def handle_stream(self, stream: tornado.iostream.IOStream, address):
        print(f"New connection from {address}")
        while True:
            try:
                # Read a line from the client
                data = await stream.read_until(b"\n")
                print(f"Received data: {data.decode().strip()}")
                
                # Send the data to Django backend
                response = requests.post("http://18.217.109.178/api/receive-data/", data={'data': data.decode().strip()})
                print(f"Forwarded data to Django, response status: {response.status_code}")
            except tornado.iostream.StreamClosedError:
                print(f"Connection closed by {address}")
                break

# if __name__ == "__main__":
#     server = SimpleTCPServer()
#     # Listening on a specific IP address and port
#     server.listen(8000, address="18.217.109.178")
#     print("TCP Server listening on 18.217.109.178:8000")
#     tornado.ioloop.IOLoop.current().start()
    
# if __name__ == "__main__":
#     server = SimpleTCPServer()
#     server.listen(8000, address="127.0.0.1")  # or "0.0.0.0" to listen on all interfaces
#     print("TCP Server listening on 127.0.0.1:8000")
#     tornado.ioloop.IOLoop.current().start()    

if __name__ == "__main__":
    server = SimpleTCPServer()
    server.listen(8000)  # Listening on port 8000
    print("TCP Server listening on port 8000")
    tornado.ioloop.IOLoop.current().start()
