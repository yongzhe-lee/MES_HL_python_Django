import os
import uuid

from django.db import  transaction
from django.http import JsonResponse, HttpResponse

from domain.services.common import CommonUtil
from domain.services.logging import LogWriter
from domain.models.system import AttachFile

from configurations import settings


def upload(context, request):
    ''' /api/files/upload
    '''
    items=[]
    ctxrequest = context.request
    gparam = request.GET
    posparam = request.POST

    DataPk = CommonUtil.try_int(posparam.get('dataPk'), 0)

    tableName = posparam.get('tableName')
    attachName = posparam.get('attachName')
    onlyOne = posparam.get('onlyOne', 0)

    others = posparam.get('others')   #folder_name
    accepts = posparam.get('accepts')
    fileIndex = posparam.get('fileIndex', 0)
    
    action = gparam.get('action', 'save_file')

    try:
        if action == 'save_file':
            files = request.FILES['uploadfile']
            allowedDuple = 'Y' if posparam.get('allowedDuple') == 'true' else 'N'

            if files:
                if files.size > 52428800: #50mb
                    message = 'Exceeded the allowed size'
                    return HttpResponse(status=500, reason=message)
                ext = files.name.split('.')[-1]
                ext = ext.lower()
                if accepts:
                    if not ext in accepts.split(','):
                        message = 'This file is not allowed to upload.'
                        return HttpResponse(status=500, reason=message)

                if ext in ['py', 'js', 'aspx', 'asp', 'jsp', 'php', 'cs', 'ini', 'htaccess','exe','dll']:
                    message = 'This file is not allowed to upload.'
                    return HttpResponse(status=500, reason=message)

                path = settings.FILE_UPLOAD_PATH + others + "\\"
                if not os.path.exists(path):
                    os.makedirs(path)

                # 2021-04-06 업무룰로 인한 추가
                if attachName is None:
                    attachName = 'basic'
            
                try:

                    with transaction.atomic():

                        # 1.파일저장
                        file_name = '%s.%s' % (uuid.uuid4(), ext)
                        upload_file = open(path + file_name, mode='ab')
                        upload_file.write(files.read())
                        upload_file.close()

                        # attachFile 정보 저장
                        attachFile = None
                        if onlyOne:
                            q = AttachFile.objects.filter(TableName=tableName)
                            q = q.filter(AttachName=attachName)
                            q = q.filter(DataPk=DataPk)
                            q = q.order_by('-id')
                            attachFile = q.first()
                        if not attachFile:
                            af_query = AttachFile.objects.filter(TableName=tableName, AttachName=attachName, DataPk=DataPk, FileName=files.name)
                            if allowedDuple == 'N':
                                if af_query.exists():
                                    message = '이미 동일한 파일이 존재합니다.'
                                    return JsonResponse({
                                        'message': message,
                                        'success': False
                                        }, safe=False, json_dumps_params={'ensure_ascii':False})
                            count = af_query.count()

                            attachFile = AttachFile()
                            attachFile.TableName = tableName
                            attachFile.DataPk = DataPk
                            attachFile.AttachName = attachName
                    
                        attachFile.PhysicFileName = file_name
                        attachFile.FileIndex = 0
                        attachFile.FileIndex = count
                        attachFile.FileName = files.name
                        attachFile.ExtName = ext
                        attachFile.FilePath = path
                        attachFile.FileSize = int(files.size)
                        attachFile.set_audit(ctxrequest.user)
                        attachFile.save()

                    items = {
                        'success': True,
                        'fileExt': ext,
                        'fileNm': files.name,
                        'fileSize': files.size,
                        'fileId': attachFile.id,
                        'TableName' : attachFile.TableName,
                        'AttachName' : attachFile.PhysicFileName,
                        'FileIndex' : attachFile.FileIndex
                    }
                    return JsonResponse(items, safe=False, json_dumps_params={'ensure_ascii':False})

                except Exception as ex:
                    print(str(ex))
                    return HttpResponse(status=500, reason='No uploaded files')
            else:
                return HttpResponse(status=500, reason='No uploaded files')
        elif action == 'remove_file':
            file_name = posparam.get('fileName')

            af_query = AttachFile.objects.filter(TableName=tableName, AttachName=attachName, DataPk=DataPk, FileName=file_name, FileIndex=fileIndex)
            af_query.delete()
            
            items = {
                'success': True,
                'message': '삭제되었습니다'
            }
            
            return JsonResponse(items, safe=False, json_dumps_params={'ensure_ascii':False})
        
        elif action == 'call_attach_file':
            af_query = AttachFile.objects.filter(TableName=tableName, AttachName=attachName, DataPk=DataPk)
            af_query = af_query.order_by('FileIndex')
            af_list = af_query.values()
            items = {
                'data': list(af_list),
                'success': True
            }
            return JsonResponse(items, safe=False, json_dumps_params={'ensure_ascii':False})

    except Exception as ex:
        source = 'files/upload : action-{}'.format('')
        LogWriter.add_dblog('error', source , ex)
        raise ex

    # 문제 발생시 reason 을 한글이 아닌 영문으로 리턴해야 js 라이버러리가 제대로 동작
    return HttpResponse(status=500, reason='No uploaded files')
