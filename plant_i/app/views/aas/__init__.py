from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from app.views import MESBaseView

class AASDefaultRenderer(object):

    @staticmethod
    def swagger(request):
        return render(request, 'aas/swagger.html')



class AASView(MESBaseView):
    http_method_names = ['get', 'post']

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle GET requests.
        """
        return JsonResponse({"message": "This is a placeholder for AAS API."})
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle POST requests.
        """
        return JsonResponse({"message": "This is a placeholder for AAS API."})


class AssetView(MESBaseView):
    http_method_names = ['get', 'post']

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle GET requests.
        """
        return JsonResponse({"message": "This is a placeholder for AAS API."})
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle POST requests.
        """
        return JsonResponse({"message": "This is a placeholder for AAS API."})
    