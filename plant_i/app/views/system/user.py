from django.contrib.auth.models import User

from domain.models.system import PropertyData
from domain.services.logging import LogWriter

from domain.services.account import AccountService
from domain.services.date import DateUtil
from domain.services.sql import DbUtil

def user(context):
    '''
    api/system/user

    현재 사용자가 관리자 그룹인지 체크 루틴 필요
    '''
    items = []
    gparam = context.gparam
    posparam = context.posparam
    request = context.request

    action = gparam.get('action', 'read')
    account_service = AccountService()

    try:
        if action=='read':
            group =  gparam.get('group', '')
            keyword =gparam.get('keyword', '')
            super_user = request.user.is_superuser
            if not super_user:
                super_user = request.user.userprofile.UserGroup.Code == 'dev'
            items = account_service.get_user_list(super_user, group, keyword)

        elif action=='detail':
            id = gparam.get('id')
            items = account_service.get_user_detail(id)

        elif action=='save':
            
            user = None
            id = posparam.get('id', '')

            login_id = posparam.get('login_id')
            Name = posparam.get('user_name')
            UserGroup_id = posparam.get('user_group_id')
            email = posparam.get('email', '')
            lang_code = posparam.get('lang_code', '')
            Factory_id = posparam.get('Factory_id', '')
            Dept_id = posparam.get('dept_id', '')
            is_active = False if posparam.get('is_active', 'N') == 'N' else True
            default_menu = posparam.get('default_menu', '') #@@default_menu

            name_chk = User.objects.filter(username=login_id)

            if id:
                name_chk = name_chk.exclude(id = id)
                if name_chk :
                    return {'success':False, 'message':'중복된 사번이 존재합니다.'}

                user = User.objects.get(id=id)

            else:
                if name_chk :
                    return {'success':False, 'message':'중복된 사번이 존재합니다.'}

                user = User()
                user.set_password('1')


            if is_active:
                is_active = True

            user.username = login_id
            user.email = email
            user.date_joined = DateUtil.get_current_datetime()
            user.is_active = is_active
            user.save()

            user.userprofile.Name = Name
            user.userprofile.UserGroup_id = UserGroup_id
            user.userprofile.Factory_id = Factory_id
            user.userprofile.Dept_id = Dept_id
            user.userprofile.lang_code = lang_code
            user.userprofile.save()
            
            #default_menu 저장
            prop_data = PropertyData.objects.filter(DataPk = user.id, TableName='auth_user', Code="main_menu").first()
            if not prop_data:
                prop_data = PropertyData()
                prop_data.DataPk = user.id
                prop_data.TableName = 'auth_user'
                prop_data.Code = "main_menu"
            prop_data.Char1 = default_menu
            prop_data.save()

            items = {'success':True,'id': user.id}

        elif action=='delete':
            id = posparam.get('id', '')
            if id:
                User.objects.filter(id=id).delete()
                items = {'success':True}

        elif action=='pass_setting':
            pass1 = posparam.get('pass1')
            pass2 = posparam.get('pass2')
            id  = posparam.get('id')

            if pass1 == pass2:
                user = User.objects.get(id=id)
                user.set_password(pass1);
                user.save()
                items = {'success':True}
            else:
                items = {'success':False, 'message':'패스워드가 일치하지 않습니다.'}

        elif action == 'user_grp_list':
            
            id = gparam.get('id')
            sql = '''  
            select ug.id as grp_id
            , ug."Name" as grp_name
            , rd."Char1" as grp_check
            from user_group ug 
            left join rela_data rd on rd."DataPk2" = ug.id 
            and "RelationName" = 'auth_user-user_group' 
            and rd."DataPk1" = %(id)s
            where coalesce(ug."Code",'') <> 'dev'
            '''

            dc = {}
            dc['id']=id
            items = DbUtil.get_rows(sql,dc)

        elif action == 'save_user_grp':
            # id = posparam.get('id', '')
            # Q = posparam.get('Q')
            # q = RelationData.objects.filter(DataPk1 = id, TableName1='auth_user', TableName2='user_group')
            # #q = q.filter(RelationName='auth_user-user_group')
            # q.delete()
            # for item in Q:
            #     if item['grp_check']=='Y' :
            #         rd = RelationData()
            #         rd.DataPk1 = id
            #         rd.TableName1 = 'auth_user'
            #         rd.DataPk2 = item.get('grp_id')
            #         rd.TableName2 = 'user_group'
            #         rd.RelationName = 'auth_user-user_group'
            #         rd.Char1 = 'Y'
            #         rd.save()

            items = {'success' : True}

    except Exception as ex:
        source = 'user : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
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
        #raise ex

    return items
 


