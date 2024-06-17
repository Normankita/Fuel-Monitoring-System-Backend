from django.apps import AppConfig
from django.conf import settings
import threading



class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

class SocketappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socketapp'

    def ready(self):
        # Start socket server when Django starts
        if settings.RUN_SOCKET_SERVER:
            from .socket_handler import start_socket_server
            socket_server_thread = threading.Thread(target=start_socket_server)
            socket_server_thread.start()
            
            
class MyAppConfig(AppConfig):
    name = 'monitor'

    def ready(self):
        # Import the function you want to run
        from .views import custom_request_view
        # Call the function
        custom_request_view()            