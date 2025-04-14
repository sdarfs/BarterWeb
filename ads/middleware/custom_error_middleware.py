from django.shortcuts import render
from django.conf import settings

class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            if settings.DEBUG:
                return render(request, 'errors/500.html', status=500)
            raise e
        if response.status_code == 404:
            return render(request, 'errors/404.html', status=404)
        elif response.status_code == 403:
            return render(request, 'errors/403.html', status=403)
        elif response.status_code == 400:
            return render(request, 'errors/400.html', status=400)
        return response
