import datetime

from domain.models.system import Board
from domain.services.definition.board import BoardService
from domain.services.logging import LogWriter
from domain.services.file import FileService
from domain.models.system import AttachFile


def notice(context):
    items =[]
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action')
    
    noticeService = BoardService()
    fileService = FileService()
    try:
        if action == 'read':
            start_dt = gparam.get('srchStartDt') + ' 00:00:00'
            end_dt = gparam.get('srchEndDt') + ' 23:59:59'
            keyword = gparam.get('keyword')
            #notice_yn = gparam.get('notice_yn')
            items = noticeService.get_board_list('notice', keyword, start_dt, end_dt)
        elif action == 'detail':
            items = noticeService.get_board_detail(gparam.get('id'))
        elif action == 'chkCreater':
            items = noticeService.chk_creater(gparam.get('id'), request.user.id)
        elif action == 'delete':
            id = posparam.get('id')
            if id:
                notice = Board.objects.get(id = id)
                notice.delete()
        elif action == 'save':
            try:
                fileId = posparam.get('fileId')

                notice = None
                if posparam.get('id'):
                    notice = Board.objects.get(id = posparam.get('id'))
                else:
                    notice = Board()
                notice.BoardGroup = 'notice'
                notice.Title = posparam.get('title')
                notice.Content = posparam.get('content')
                notice.NoticeYN = posparam.get('notice_yn')
                notice.NoticeEndDate = posparam.get('notice_end_date')
                notice.WriteDateTime = datetime.datetime.now()
                notice.set_audit(request.user) 

                notice.save()
                items = {'id': notice.id}
                
                if fileId:
                    DataPk = notice.id
                    fileIdList = fileId.split(',')
                    for i in fileIdList:
                        fileService.updateDataPk(i, DataPk)

            except Exception as ex:
                source = '/api/support/notice, action:{}', format(action)
                LogWriter.add_dblog('error', source, ex)
                raise ex
        elif action == 'detailFiles':
            attach_name = 'basic'
            TableName = gparam.get('TableName','')
            DataPk = gparam.get('DataPk','0')
            limit = gparam.get('limit',None)
            items = fileService.get_attach_file(TableName, DataPk, attach_name, limit)

        elif action == 'deleteFile':
            id = posparam.get('fileId')
            if id:
                attachFile = AttachFile.objects.get(id=int(id))
                attachFile.delete()
            else:
                return items

    except Exception as ex:
        source = 'notice : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex
    return items


#def upload_setting(context):
#    gparam = context.gparam
#    path = gparam.get('board_type','')
#    items ={
#            'fileExt': 'hwp,doc,docx,ppt,pptx,xls,xlsx,jpg,jpeg,gif,mbp,png,txt,zip,pdf',
#            'fileSize': 100,
#            'maxCnt': 5,
#        }

#    return items;
