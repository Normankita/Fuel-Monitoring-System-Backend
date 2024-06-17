import logging

class PrintRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Print or log the request details
        print("Request Method:", request.method)
        print("Request Path:", request.path)
        print("GET Parameters:", request.GET)
        print("POST Parameters:", request.POST)
        print("Headers:", request.headers)
        print("Body:", request.body)

        # Get the response from the next middleware or view
        response = self.get_response(request)

        return response
