from django.http import HttpResponse

from configurations import settings
from domain.services.file.attach_file import AttachFileService
from domain.services.common import CommonUtil
from domain.services.logging import LogWriter

def download(context, request):
    ''' /api/files/download?file_id=1   attach_file에 저장된 파일을 읽는다.
        /api/files/download?temp_file_name=xxxxx    임시폴더에 저장된 임시파일을 읽는다.
    '''
    try:
        fileService = AttachFileService()
        file_id = request.GET.get('file_id', None)

        if file_id:
            row = fileService.get_attach_file_detail(file_id)
            file_path = row.get('FilePath')+'\\'
            PhysicFileName = row.get('PhysicFileName')
            FileName = row.get('FileName')
            file_name = PhysicFileName
     
        else:
            file_name = request.GET.get('temp_file_name', None)
            file_path = settings.FILE_TEMP_UPLOAD_PATH+'\\'
            FileName = file_name

        # 파일 확장자에 따른 content_type 설정
        extension = file_name.split('.')[-1].lower()
        content_types = {
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'csv': 'text/csv',
            'zip': 'application/zip',
            'hwp': 'application/x-hwp',
            'png': 'image/png',
            'gif': 'image/gif',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        content_type = content_types.get(extension, 'application/octet-stream')

        f = open(file_path + file_name, 'rb')
        resp = HttpResponse(f, content_type=content_type)
        download_filename = CommonUtil.get_utf8_filename(FileName)
        resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % download_filename
        resp['Set-Cookie'] = 'fileDownload=true; path=/'
        return resp

    except Exception as e:
        LogWriter.add_dblog('error', 'download', e)
        raise e
