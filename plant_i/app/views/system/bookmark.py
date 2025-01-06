from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.system import Bookmark
from domain.services.system import SystemService



def bookmark(context):
    '''
    api/system/bookmark
    '''

    svc = SystemService()
    items = []
    gparam = context.gparam
    action = gparam.get('action', 'read')
    user_id = context.request.user.id
    if user_id is None:
        return items
    try:
        if action=='read':
            items = svc.get_bookmark_list(user_id)
        elif action=='save':
            posparam = context.posparam
            menucode = posparam.get('menucode')
            isbookmark = posparam.get('isbookmark')
            result = True
            if isbookmark=='true':
                Bookmark.objects.filter(User_id=user_id, MenuItem_id=menucode).delete()
                bookmark = Bookmark(User_id=user_id, MenuItem_id=menucode, _created=DateUtil.get_current_datetime())
                bookmark.save()
            else:
                Bookmark.objects.filter(User_id=user_id, MenuItem_id=menucode).delete()

            return {'success': result}
        else:
            raise Exception('action error : ' + action)
    except Exception as ex:
        source = '/api/system/bookmark, action:{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex


    return items

