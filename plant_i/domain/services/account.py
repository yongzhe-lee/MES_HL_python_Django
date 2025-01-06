from configurations import settings

from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.user import UserGroupMenu

class AccountService():
    def __init__(self):
        '''
        생성자 루틴
        '''
        return

    def get_user_session(self, user_id):

        dic_param = {'user_id':user_id}

        sql = '''
        '''


        return {}

    def get_user_list(self, super_user, group, keyword):
        sql = '''
        select 
            au.id
            , up."Name" as name
            , au.username as login_id
            , up."UserGroup_id" as user_group_id
            , au.email
            , ug."Name" as group_name
            , d."Name" as dept_name
            , d."Name" as dept_name
            , up."Depart_id" as depart_id
            , up.lang_code
            , au.is_active
            , to_char(au.date_joined ,'yyyy-mm-dd hh24:mi') as date_joined
        from auth_user au 
        left join user_profile up on up."User_id" = au.id
        left join user_group ug on ug.id = up."UserGroup_id"
        left join dept d on d.id = up."Depart_id"
        left join prop_data pd on pd."DataPk" = au.id
            and pd."TableName" = 'auth_user'
            and pd."Code" = 'main_menu'
        where is_superuser = false
        '''
        if not super_user:
            sql += ''' and ug."Code" <> 'dev'
        '''
        if group:
            sql+=''' and ug.id = %(group)s
            '''
        if keyword:
            sql +='''and up."Name" like concat('%%', %(keyword)s, '%%')
            '''
        sql +=''' order by ug."Name", up."Name"
        '''
        try:
            dc = {
                'group' : group, 
                'keyword':keyword
            }
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','AccountService.get_user_list', ex)
            raise ex

        return items

    def get_user_detail(self, id):

        dic_param = {'id' : id}
        items = {}
        sql = ''' select 
            au.id
            , up."Name"
            , au.username as login_id
            , au.email
            , ug."Name" as group_name
            , up."UserGroup_id"
            , up."Factory_id"
            , f."Name" as factory_name
            , d."Name" as dept_name
            , up."Depart_id"
            , up.lang_code
            , au.is_active
            , to_char(au.date_joined ,'yyyy-mm-dd hh24:mi') as date_joined
            , pd."Char1" as default_menu
        from auth_user au 
        left join user_profile up on up."User_id" = au.id
        left join user_group ug on up."UserGroup_id" = ug.id 
        left join factory f on up."Factory_id" = f.id 
        left join dept d on d.id = up."Depart_id"
        left join prop_data pd on pd."DataPk" = au.id
            and pd."TableName" = 'auth_user'
            and pd."Code" = 'main_menu'
        where au.id = %(id)s
        '''
        try:
            items = DbUtil.get_row(sql, dic_param)
            #if len(rows)>0:
            #    items = rows[0]

        except Exception as ex:
            LogWriter.add_dblog('error','AccountService.get_user_detail', ex)
            raise ex

        return items

    @classmethod
    def get_user_default_menu(self, user):
        ''' 사용자의 default_menu가 지정되었으면 그 값을 가져온다.
        '''
        sql = ''' select pd."Char1" as default_menu 
        from auth_user u 
        inner join prop_data pd on pd."DataPk" = u.id
        and pd."TableName" = 'auth_user'
        and pd."Code" = 'main_menu'
        where u.id = %(user_id)s
        '''
        dc = {}
        dc['user_id'] = user.id
        row = DbUtil.get_row(sql, dc)
        if row:
            return row['default_menu']
        else:
            return ''


    @classmethod
    def check_user_auth(cls, user, gui_code):
        result = False
        if user.is_superuser:
            return 'RW'
        group_code = user.userprofile.UserGroup.Code

        if group_code in ['dev']:
            return 'RW'

        if group_code in ['admin', 'dev'] and gui_code in ['wm_user_group', 'wm_user', 'wm_user_group_menu']:
            return 'RW'

        if gui_code == 'wm_noauth_default':
            return 'R'

        group_id = user.userprofile.UserGroup.id
        q = UserGroupMenu.objects.filter(UserGroup__id=group_id, MenuCode=gui_code).values('AuthCode')
        authcode = None
        foo = q.first()
        if foo:
            authcode = foo['AuthCode']

        return authcode

