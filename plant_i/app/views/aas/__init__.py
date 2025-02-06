from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

class AASDefaultRenderer(object):

    @staticmethod
    def swagger(request):
        return render(request, 'aas/swagger.html')

