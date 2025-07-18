from django.utils.deprecation import MiddlewareMixin
from django.utils.http import http_date

class RemoveCriticalResponseHeader(MiddlewareMixin): 
    def process_response(self, request, response):

        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Embedder-Policy"] = "require-corp"

        #response["Last-Modified"] = http_date(file_path.stat().st_mtime)
        #response["Cache-Control"] = "public, max-age=31536000"

        response['Server'] = ''
        return response
