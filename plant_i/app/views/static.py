
from django.http import FileResponse, Http404
from app.views import MESBaseView
from configurations import settings
from pathlib import Path
import mimetypes
from django.utils.http import http_date


class DTResourceView(MESBaseView):

    STATIC_ROOT = settings.STATIC_ROOT
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        filename = kwargs.get('filename', None)
        file_path = Path(self.STATIC_ROOT) / 'resource' / 'dt' / filename
        if not file_path.exists():
            raise Http404()

        content_type, _ = mimetypes.guess_type(str(file_path))

        if content_type is None:
            content_type = "application/octet-stream"

        response = FileResponse(open(file_path, "rb"), content_type=content_type)


        tmp_path = str(file_path)

        # MIME 재지정 + Encoding 설정
        if tmp_path.endswith(".js.br") or tmp_path.endswith(".worker.js.br") :
            response["Content-Type"] = "application/javascript"
            response["Content-Encoding"] = "br"
            response["Vary"] = "Accept-Encoding"
        elif str(file_path).endswith(".wasm.br"):
            response["Content-Type"] = "application/wasm"
            response["Content-Encoding"] = "br"
            response["Vary"] = "Accept-Encoding"
        elif str(file_path).endswith(".data.br"):
            response["Content-Type"] = "application/octet-stream"
            response["Content-Encoding"] = "br"
            response["Vary"] = "Accept-Encoding"
        elif tmp_path.endswith(".js"):
            response["Content-Type"] = "application/javascript"


        # COEP/COOP 헤더
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Embedder-Policy"] = "require-corp"

        # 캐시 헤더
        response["Last-Modified"] = http_date(file_path.stat().st_mtime)
        #response["Cache-Control"] = "public, max-age=31536000"

        return response