import os
import uuid

from django.db import transaction
from django.http import JsonResponse

from domain.services.common import CommonUtil
from domain.services.logging import LogWriter
from domain.models.system import AttachFile
from configurations import settings


def upload(context, request):
    ''' /api/files/upload '''
    ctxrequest = context.request
    gparam = request.GET
    posparam = request.POST

    DataPk = CommonUtil.try_int(posparam.get('dataPk'), 0)
    tableName = posparam.get('tableName')
    attachName = posparam.get('attachName') or 'basic'
    onlyOne = posparam.get('onlyOne', 0)
    others = posparam.get('others') or ''
    accepts = posparam.get('accepts')
    fileIndex = posparam.get('fileIndex', 0)
    allowedDuple = 'Y' if posparam.get('allowedDuple') == 'true' else 'N'
    action = gparam.get('action', 'save_file')

    path = os.path.join(settings.FILE_UPLOAD_PATH, others)
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        if action == 'save_file':
            files = request.FILES.getlist('uploadfile')
            items = []

            for file in files:
                try:
                    if file.size > 52428800:   # 원복(50mb)
                        raise ValueError('파일 용량은 50MB 이하만 가능합니다.')

                    ext = file.name.split('.')[-1].lower()
                    if accepts and ext not in accepts.split(','):
                        raise ValueError('허용되지 않은 파일 형식입니다.')
                    if ext in ['py', 'js', 'aspx', 'asp', 'jsp', 'php', 'cs', 'ini', 'htaccess', 'exe', 'dll']:
                        raise ValueError('업로드가 금지된 확장자입니다.')

                    with transaction.atomic():
                        file_name = f'{uuid.uuid4()}.{ext}'
                        with open(os.path.join(path, file_name), mode='wb') as upload_file:
                            upload_file.write(file.read())

                        attachFile = None
                        if onlyOne:
                            attachFile = AttachFile.objects.filter(
                                TableName=tableName, AttachName=attachName, DataPk=DataPk
                            ).order_by('-id').first()

                        count = 0
                        if not attachFile:
                            af_query = AttachFile.objects.filter(
                                TableName=tableName, AttachName=attachName,
                                DataPk=DataPk, FileName=file.name
                            )
                            if allowedDuple == 'N' and af_query.exists():
                                raise ValueError('이미 동일한 파일이 존재합니다.')
                            count = af_query.count()

                            attachFile = AttachFile(
                                TableName=tableName,
                                DataPk=DataPk,
                                AttachName=attachName
                            )

                        attachFile.PhysicFileName = file_name
                        attachFile.FileName = file.name
                        attachFile.ExtName = ext
                        attachFile.FilePath = path
                        attachFile.FileSize = file.size
                        attachFile.FileIndex = count
                        attachFile.set_audit(ctxrequest.user)
                        attachFile.save()

                        items.append({
                            'success': True,
                            'fileExt': ext,
                            'fileNm': file.name,
                            'fileSize': file.size,
                            'fileId': attachFile.id,
                            'TableName': attachFile.TableName,
                            'AttachName': attachFile.PhysicFileName,
                            'FileIndex': attachFile.FileIndex
                        })

                except Exception as e:
                    items.append({
                        'success': False,
                        'fileNm': file.name,
                        'message': str(e)
                    })

            return JsonResponse(items, safe=False, json_dumps_params={'ensure_ascii': False})

        elif action == 'remove_file':
            file_name = posparam.get('fileName')
            AttachFile.objects.filter(
                TableName=tableName,
                AttachName=attachName,
                DataPk=DataPk,
                FileName=file_name,
                FileIndex=fileIndex
            ).delete()

            return JsonResponse({
                'success': True,
                'message': '삭제되었습니다'
            }, json_dumps_params={'ensure_ascii': False})

        elif action == 'call_attach_file':
            af_query = AttachFile.objects.filter(
                TableName=tableName,
                AttachName=attachName,
                DataPk=DataPk
            ).order_by('-id')
            return JsonResponse({
                'success': True,
                'data': list(af_query.values())
            }, json_dumps_params={'ensure_ascii': False})

    except Exception as ex:
        LogWriter.add_dblog('error', f'files/upload : action-{action}', ex)
        return JsonResponse({
            'success': False,
            'message': f'파일 업로드 실패: {str(ex)}'
        }, status=500, json_dumps_params={'ensure_ascii': False})
