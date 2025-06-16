from domain.models.user import UserGroup 
from domain.services.logging import LogWriter
from domain.services.system import SystemService

def usergroup(context):
    '''
    api/system/usergroup
    '''
    items = []
    posparam = context.posparam
    gparam = context.gparam
    request = context.request
    action = context.gparam.get('action', 'read')
    system_service = SystemService()

    try:
        if action=='read':
            super_user = request.user.is_superuser
            if not super_user:
                super_user = request.user.userprofile.UserGroup.Code == 'dev'

            items = system_service.get_usergroup_list(super_user)

        elif action=='detail':
            group_id = context.gparam.get('id')
            items = system_service.get_usergroup_detail(group_id)

        elif action=='save':
            #id=&code=dummy&name=asdf&description=asdfasdf&disabled=on&created=asdfas
            id = posparam.get('id')
            code = posparam.get('code')
            name = posparam.get('name')
            description = posparam.get('description')
            #disabled = posparam.get('disabled', None)

            #if disabled:
            #    disabled = False
            #else:
            #    disabled = True

            if id:
                usergroup = UserGroup.objects.get(id=id)
            else:
                usergroup = UserGroup()

            usergroup.Code = code
            usergroup.Name = name
            usergroup.Description = description
            #usergroup.Disabled = disabled
            usergroup.save()

            items = {'success':True}

        elif action == 'delete':
            id = posparam.get('id')

            if id:
                usergroup = UserGroup.objects.filter(id=id)
                #user = UserProfile.objects.filter(UserGroup_id = id)
                #if user:
                #    return {'success':False, 'message': '해당 그룹에 사용자가 존재합니다.'}
                #else:
                usergroup.delete()
                items = {'success':True}
            
        else:
            raise Exception("action : " + action)

    except Exception as ex:
        source = 'usergroup : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        #raise ex
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items

    return items



