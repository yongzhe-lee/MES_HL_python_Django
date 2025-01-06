
from domain.gui import GUIConfiguration
from domain.services.system import SystemService
from domain.services.logging import LogWriter
from domain.models.user import UserGroupMenu


def usergroupmenu(context):
    items = []
    gparam = context.gparam
    posparam = context.posparam

    action = gparam.get('action')
    svc = SystemService()

    try:
        if action=='read':
            group_id = gparam.get('group_id', '')
            folder_id = gparam.get('folder_id', '')
            items = svc.get_usergroupmenu_list(group_id, folder_id)

        elif action =='save':
            request = context.request
            item_list = posparam.get('Q')

            group_id = posparam.get('group_id', '')
            #UserGroupMenu.objects.filter(UserGroup_id=group_id).delete()

            for row in item_list:
                menu_code = row.get('menu_code')
                ugm_id = row.get('ugm_id')
                AuthCode = ''
                r = row.get('r', False)
                w = row.get('w', False)

                if r:
                    AuthCode = "R"

                if w:
                    AuthCode += 'W'
                if ugm_id:
                    usergroupmenu = UserGroupMenu.objects.get(id=ugm_id)
                else:
                    usergroupmenu = UserGroupMenu()
                    usergroupmenu.MenuCode = menu_code
                    usergroupmenu.UserGroup_id = group_id
                usergroupmenu.AuthCode = AuthCode
                usergroupmenu._creater_id = request.user.id
                usergroupmenu.save()

            items = { 'success': True }

    except Exception as ex:
        source = 'usergroupmenu : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex

    return items


