from fileinput import filename
import os
from django.http import HttpResponse
from configurations import settings
from domain.services.common import CommonUtil
from domain.services.logging import LogWriter

from domain.models.aas import DBFileElement, DBResource
from configurations import settings


def aas(context, request):
    '''
    /api/files/aas?model_type=file&data_pk=3   attach_file에 저장된 파일을 읽는다.
    '''
    gparam = context.gparam


    model_type= gparam.get('model_type', None)
    data_pk = gparam.get('data_pk', None)

    if not model_type or not data_pk:
        raise Exception('model_type and data_pk are required parameters.')

    try:
        if model_type == 'file':
            file_element = DBFileElement.objects.get(SubmodelElement__sme_pk=data_pk)

            #file_name = f'fe_{submodel_element.sme_pk}_{uuid.uuid4()}.{ext}'
            #filepath = os.path.join (settings.FILE_UPLOAD_PATH, file_element.value)
            # DBFileElement의 path는 물리적 전체경로만 저장하고 value는 aasx 파일내 상대경로를 저장한다
            content_type= file_element.content_type
            filename = file_element.filename

            f = open(file_element.path, 'rb')
            resp = HttpResponse(f, content_type=content_type)
            download_filename = CommonUtil.get_utf8_filename(filename)
            resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % download_filename
            return resp
        elif model_type == 'resource':
            # resource.path 물리적 절대경로
            resource = DBResource.objects.get(pk=data_pk)
            path = resource.path.lstrip('/').replace("/","\\")
            filepath = resource.path
            content_type = resource.contentType
            filename = path.split('\\')[-1]

            f = open(filepath, 'rb')
            resp = HttpResponse(f, content_type=content_type)
            download_filename = CommonUtil.get_utf8_filename(filename)
            resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % download_filename

            return resp
        else:
            return HttpResponse("Unsupported model type", status=400)


    except Exception as e:
        LogWriter.add_dblog('error', 'aas', e)
        raise e








