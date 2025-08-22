import os
import tempfile
from django.http import FileResponse, Http404, HttpResponseServerError

from domain.services.aas.aasx import AASXHelper  # 경로 확인
from domain.models.aas import DBAssetAdministrationShell


def aasx(context, request):
    aas_id_short = context.gparam.get('id_short', None)
    if not DBAssetAdministrationShell.objects.filter(id_short=aas_id_short).exists():
        raise Http404("AAS not found")

    helper = AASXHelper(aas_id_short)

    try:
        xml_bytes = helper.to_xml_bytes()
        file_response = helper.to_file_response()
    except Exception as ex:
        return HttpResponseServerError(str(ex))


    return file_response
    