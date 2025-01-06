from domain.services.sql import DbUtil
from domain.gui import GUIConfiguration
from domain.services.system import SystemService
from domain.services.logging import LogWriter
from domain.models.user import UserGroupMenu


def menus(context):
    result = {'success': True}
    gparam = context.gparam
    posparam = context.posparam
    action  = gparam.get('action','read')
    request = context.request
    user = request.user
    try:
        if action == 'read':
            group_id = None
            user_id = None
            systemservice = SystemService()
            if user.is_authenticated:
            #    user_id = user.id
            #    group_id = user.userprofile.UserGroup_id
                #group_code = user.userprofile.UserGroup.Code
                #items = systemservice.get_web_menu_list(group_code, group_id, user_id)
                result = systemservice.get_web_menu_list(user)
    
            dc_folder ={}  #폴더만 저장
            folder1 = [] #폴더, 메뉴 모두 저장.

            for m in result:
                id = m.get('id')
                menu_code=m.get('menu_code')
                pid = m.get('pid')
                name = m.get('name')
                menu_yn = m.get('menu_yn')
                isbookmark = m.get('isbookmark')
                popup = m.get('popup')
                depth = m.get('depth')

                url = ''
                css = m.get('css')
                if id:
                    # 폴더인 경우
                    p_nodes = []
                    folder = {
                        'objId': menu_code,
                        'objNm': name, 
                        'objUrl': url, 
                        'menuIconCls': css, 
                        'nodes': p_nodes,
                        'ismanual' : False, 
                        'isbookmark': False, 
                        'menuDepth':depth
                     }
                    dc_folder[id] = folder
                    if not pid: # 1 레벨 폴더
                        folder1.append(folder)
                    else:
                        #p_folder = dc_folder.get(pid)
                        ''' 마지막 폴더를 찾아서 nodes에 추가
                        '''
                        p_folder = dc_folder.get(pid)
                        if p_folder is not None:
                            p_folder['nodes'].append(folder)
                else:
                    # 메뉴인 경우
                    url = '/gui/' + menu_code
            
                    item = {
                        'objId': menu_code,
                        'objNm': name, 
                        'objUrl': url, 
                        'menuIconCls':css, 
                        'nodes':[],
                        'ismanual':False, 
                        'isbookmark': isbookmark, 
                        'popup': popup, 
                        'menuDepth':2
                    }
                    p_folder = dc_folder.get(pid)
                    if p_folder is not None:
                        p_folder['nodes'].append(item)

            return folder1
    except Exception as ex:
        source = '/api/system/menus, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}

    return result

    


