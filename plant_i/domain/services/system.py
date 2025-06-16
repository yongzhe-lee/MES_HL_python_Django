from configurations import settings

from domain.models.system import MenuItem
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.user import UserGroup
from domain.models.system import SystemOption

class SystemService():
    '''
    label, menu, log, user, bookmark, system_code, storyboard
    '''
    def __init__(self):
        return

    def get_label_list(self, lang_code, gui_code, template_key):
        items = []
        
        sql = '''
        select
        lc."ModuleName" as gui_code
        , lc."TemplateKey" as template_key
        , lc."LabelCode" as label_code
        , lc."Description" as descr
        , lcl."DispText" as text
        from label_code lc 
        left join label_code_lang lcl on lc.id = lcl."LabelCode_id"
        where lcl."LangCode" = %(lang_code)s 
        '''
        if gui_code:
            sql += ''' and lc."ModuleName" = %(gui_code)s 
            and lc."TemplateKey"=%(template_key)s
            '''
        sql += ''' 
        order by lc."ModuleName", lc."TemplateKey"
        '''

        dc = {'lang_code':lang_code, 'gui_code':gui_code, 'template_key':template_key }

        items = DbUtil.get_rows(sql, dc)
        return items

    def get_labelcode_list(self, ModuleName):
        items = []
        
        sql = ''' select lc.id
            , lc."ModuleName"
            , coalesce ((select "MenuName" from menu_item where "MenuCode"=lc."ModuleName" limit 1), 'Common') as menu_name
            , lc."TemplateKey"
            , lc."LabelCode"
            , lc."Description"
            , to_char(_created ,'yyyy-mm-dd hh24:mi:ss') as created
        from label_code lc 
        where lc."ModuleName"=%(ModuleName)s 
        '''
        dc = {'ModuleName': ModuleName }
        items = DbUtil.get_rows(sql, dc)
        return items

    def get_labelcode_detail(self, id):
        items = []
        
        sql = ''' select lc.id
            , lc."ModuleName"
            , coalesce ((select "MenuName" from menu_item where "MenuCode"=lc."ModuleName" limit 1), 'Common') as menu_name
            , (select "MenuFolder_id" from menu_item where "MenuCode"=lc."ModuleName" limit 1) as "MenuFolder_id"
            , lc."TemplateKey"
            , lc."LabelCode"
            , lc."Description"
            , to_char(_created ,'yyyy-mm-dd hh24:mi:ss') as created
        from label_code lc 
        where lc.id=%(id)s 
        '''
        dc = {'id': id }
        items = DbUtil.get_row(sql, dc)
        return items

    def get_labelcode_lang_detail(self, lang_code, gui_code, template_key, label_code):
        result = {}
        
        try:
            sql ='''select lc.id as lable_code_id
            , lcl.id as label_lang_id
            , lc."ModuleName"
            , coalesce ((select MenuName from menu_item where MenuCode=lc.ModuleName limit 1), 'Common') as menu_name
            , lc."TemplateKey"
            , lc."LabelCode"
            , lc."Description"
            , lcl."LangCode"
            , lcl."DispText"
            , to_char(lcl._created ,'yyyy-mm-dd hh24:mi:ss') as disp_created
            from label_code_lang lcl
            inner join label_code lc on lcl.LabelCode_id = lc.id
            where lcl."LangCode" = %(lang_code)s
            and lc."ModuleName" = %(gui_code)s
            and lc."TemplateKey" = %(template_key)s
            and lc."LabelCode" = %(label_code)s
            '''
                
            dc = {
                'lang_code':lang_code, 
                'gui_code': gui_code,
                'template_key':template_key,
                'label_code':label_code
             }
            items = DbUtil.get_rows(sql, dc)
            if len(items)>0:
                result = items[0]
            else:
                menu_name = ''
                queryset = MenuItem.objects.filter(MenuCode=gui_code)
                if queryset.count()>0:
                    menu_name = queryset[0].MenuName
                result = {'menu_name': menu_name, 'ModuleName' : gui_code, 'LangCode': lang_code, 'TemplateKey':template_key, 'DispText': '', 'Description':'', 'lable_code_id': None, 'label_lang_id':None}
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_labelcode_lang_detail', ex)
            raise ex

        return result

    def get_label_lang_detail(self, id):
        items = []
        
        try:
            sql =''' select lcl.id
            , lc."ModuleName"
            , lc."TemplateKey"
            , lcl."LangCode" 
            , lc."LabelCode" 
            , lcl."DispText" 
            , lcl."LabelCode_id"
            , to_char(lcl._created ,'yyyy-mm-dd hh24:mi:ss') as created
            from label_code_lang lcl 
            inner join label_code lc on lcl."LabelCode_id" = lc.id
            where lcl.id = %(id)s
            '''
                
            dc = {'id':id}
            items = DbUtil.get_row(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_label_lang_list', ex)
            raise ex

        return items

    def get_label_lang_list(self, labelcode_id, lang_code):
        items = []
        
        try:
      
            sql =''' select lcl.id
            , lc."ModuleName"
            , lc."TemplateKey"
            , lcl."LangCode" 
            , lc."LabelCode" 
            , lcl."DispText" 
            , lcl."LabelCode_id"
            , to_char(lcl._created ,'yyyy-mm-dd hh24:mi:ss') as created
            , fn_code_name('lang_code', lcl."LangCode") as lang_code_name
            from label_code_lang lcl 
            inner join label_code lc on lcl."LabelCode_id" = lc.id
            where lcl."LabelCode_id" = %(labelcode_id)s
            '''
            if lang_code:
                sql+=''' 
                and "LangCode" = %(lang_code)s
                '''
            dc = {'labelcode_id':labelcode_id, 'lang_code':lang_code}
            items = DbUtil.get_rows(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_label_lang_list', ex)
            raise ex

        return items

    def get_web_menu_list(self, user):
        #message = 'get_web_menu_list group_id :{}, user_id : {}'.format(group_id, user_id)
        #print(message)
        try:
            items = []
            userGroup = user.userprofile.UserGroup
            if userGroup:
                user_group_code = userGroup.Code
                user_group_id = userGroup.id
            else:
                user_group_code = ''
                user_group_id = 1
            lang_code = user.userprofile.lang_code
            sql=''' 
                WITH RECURSIVE tree(id, menu_code, pid, name, depth, path, folder_order, _order) AS (  
                    SELECT 
                        a.folder_id AS id
                        , a.folder_name::text AS menu_code 
                        , a.p_folder_id AS pid
                        , a.folder_name AS name 
                        , _level AS depth
                        , path
                        , path AS folder_order
                        , 0 AS _order
                        , icon::text AS css
                        , 'folder' AS data_div
                        , a.folder_id AS folder_id
                        , ''::text AS popup
                    FROM 
                        v_menu_folder a 
                    UNION ALL 
                    SELECT 
                        NULL AS id
                        , mi."MenuCode"::text AS menu_code
                        , mi."MenuFolder_id" AS pid
                        , mi."MenuName"  AS name
                        , tree.depth + 1
                        , array_append(tree.path, 9000+mi._order) AS path
                        , tree.folder_order
                        , mi._order
                        , NULL AS css
                        , 'menu' AS data_div
                        , mi."MenuFolder_id" AS folder_id
                        , mi."Popup" AS popup
                    FROM 
                        menu_item mi 
                    INNER JOIN 
                        tree ON mi."MenuFolder_id" = tree.id 
                        WHERE 
                            EXISTS (
    --                        SELECT 1 
    --                        WHERE %(group_code)s = 'dev' 
    --                        UNION ALL
    --                        SELECT 1 
    --                        WHERE mi."MenuCode" IN ('wm_user_group_menu', 'wm_user_group', 'wm_user')
    --                            AND (%(super_user)s = true OR %(group_code)s = 'admin' )
    --                        UNION ALL
                            SELECT 1 
                            FROM user_group_menu gm 
                            WHERE gm."MenuCode" = mi."MenuCode" 
                                AND gm."UserGroup_id" = %(group_id)s 
                                AND gm."AuthCode" LIKE '%%R%%'
    --                            AND ( %(group_code)s not IN ('dev') OR %(super_user)s = false )
                        )
                ), 
                M AS (
                    SELECT 
                        tree.id
                        , tree.menu_code
                        , tree.pid
                        , tree.name
                        , tree.depth
                        , tree.folder_order
                        , tree._order
                        , coalesce(tree.css,'') AS css
                        , tree.popup
                        , (bk."MenuCode" is not null) AS isbookmark
                        , data_div
                        , count(*) over (partition by tree.folder_id) AS sub_count
                        , tree.path
                    FROM 
                        tree 
                    LEFT JOIN 
                        bookmark bk ON bk."MenuCode" = tree.menu_code 
                        AND bk."User_id"= %(user_id)s
                    WHERE 1 = 1
                )
                SELECT 
                    M.id
                    , M.menu_code
                    , M.pid
				    , M.name
				    --, coalesce(D."DispText", M.name) AS lang_name
				    , M.depth
                    , M.folder_order
				    , M._order
                    , M.css
                    , M.isbookmark 
                    , M.popup
                    , M.path
                FROM M
                WHERE sub_count > 1 OR depth = 1
                ORDER BY folder_order, _order
            '''

            dc ={}
            dc['super_user'] = user.is_superuser
            dc['group_code'] = user_group_code
            dc['group_id'] = user_group_id
            dc['user_id'] = user.id
            dc['lang_code'] = lang_code
           
            items = DbUtil.get_rows(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_web_menu_list', ex)
            raise ex

        return items

    def get_menu_list(self, folder_id):

        try:
            items = []
            dc ={'folder_id':folder_id}
            sql='''
            with recursive tree as (  
                select a.id
                , a.Parent_id as pid
                , '' as menu_code
                , CONVERT(a.FolderName,varchar(100)) as folder_name
                , CONVERT('',varchar(100)) as menu_name
                , 1 as depth
                , array[a.id] as path
                , false as cycle
                , a._order as ord
                ,'folder' as data_div
                , a.id as folder_id
                , true as is_folder
                from menu_folder a   
                where a.Parent_id is null 
            '''
            if folder_id:
                sql+='''
                and a.id = %(folder_id)s
                '''

            sql+='''
                union all 
                select null as id
                , mi.MenuFolder_id as pid 
                , CONVERT(mi.MenuCode,varchar(100)) as menu_code
                , CONVERT('',varchar(100)) as folder_name
                , mi.MenuName  as menu_name
                , tree.depth+1
                , array_append(tree.path, mi.MenuFolder_id) as path
                , mi.MenuFolder_id = any(tree.path) as cycle
                , mi._order as ord
                ,'menu' as data_div
                , mi.MenuFolder_id as folder_id
                    , false as is_folder
                from menu_item mi 
                inner join tree on mi.MenuFolder_id = tree.id  
            )
            select 
            tree.pid
            , tree.id
            , tree.menu_code
            , tree.folder_name
            , tree.menu_name
            , tree.depth
            , tree.ord
            , tree.is_folder
            from tree
            order by path, tree.ord
            '''
            items = DbUtil.get_rows(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_menu_list', ex)
            raise ex

        return items

    def get_systemlog_list(self, start, end, type, source):
        sql = ''' select id
        , "Type" as type
        , "Source" as source
        , "Message" as message
        , to_char(_created ,'yyyy-mm-dd hh24:mi:ss') as created
        from sys_log sl
        where _created between %(start)s and %(end)s
        '''
        if type:
            sql += '''and "Type" ilike concat('%%',%(type)s,'%%')
            '''
        if source:
            sql += '''and "Source" ilike concat('%%', %(source)s, '%%')
            '''
        sql += ''' order by _created desc
            '''
        items = []
        try:
            dc = {}
            dc['start'] = start
            dc['end'] = end
            dc['type'] = type
            dc['source'] = source
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_systemlog_list', ex)
            raise ex
        return items


    def get_systemlog_detail(self, log_id):             
        sql = ''' select id
        , "Type" as type
        , Source as source
        , "Message" as message
        , to_char(_created ,'yyyy-mm-dd hh24:mi:ss') as created
        from sys_log sl
        where id = %(log_id)s
        '''
        log = {}
        try:
            dc = {'log_id':log_id}
            items = DbUtil.get_row(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_systemlog_detail', ex)
            raise ex

        return items

    def get_loginlog_list(self, start, end, keyword):
        sql = ''' select ll.id
        , ll."Type" as type
        , ll."IPAddress" as addr
        , au.username as login_id
        , up."Name" as name
        , to_char(ll._created ,'yyyy-mm-dd hh24:mi:ss') as created 
        from login_log ll 
        left join auth_user au ON au.id = ll."User_id" 
        left join user_profile up on up."User_id" = ll."User_id" 
        where ll._created between %(start)s and %(end)s
        '''

        if keyword:
            sql += ''' and (au.username ilike concat('%%', %(keyword)s, '%%')
                or up."Name" ilike concat('%%', %(keyword)s, '%%')
            )
            '''

        sql += ''' order by ll._created desc
        '''
        items = []
        try:
            dc = {}
            dc['start'] = start
            dc['end'] = end
            dc['keyword'] = keyword
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_loginlog_list', ex)
            raise ex

        return items

    def get_usergroup_list(self, superuser=False):
        sql = ''' select 
            id
            , "Code" as code 
            , "Name" as name 
            , "Description" as description 
            , "Disabled" as disabled 
            , to_char(_created ,'yyyy-mm-dd hh24:mi:ss') as created
        from user_group ug 
        where 1 = 1
        '''
        if not superuser:
            sql += ''' and "Code" <> 'dev' 
            '''
        sql += ''' order by name
        '''
        items = []
        try:
            items = DbUtil.get_rows(sql)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_usergroup_list', ex)
            raise ex

        return items

    def get_usergroup_detail(self, group_id):

        sql = ''' select 
        id
        , Code as code 
        , Name as name 
        ,Description as description 
        ,Disabled as disabled 
        ,to_char(_created ,'yyyy-mm-dd hh24:mi:ss') as created
        from user_group 
        where id = %(group_id)s
        '''
        group = {}
        try:
            dc={'group_id':group_id}
            items = DbUtil.get_row(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_usergroup_detail', ex)
            raise ex

        return items

    def get_usergroupmenu_list(self, group_id, folder_id=None):

        items = []
        sql = ''' WITH RECURSIVE tree AS (  
            SELECT 
                a.id
                , (CASE 
                    WHEN a.id = CAST(NULLIF(%(folder_id)s, '')AS INTEGER) AND a."Parent_id" IS NOT NULL 
                    THEN NULL 
                    ELSE a."Parent_id" 
                    END) AS parentid
                , '' AS menu_code
                , a."FolderName" AS name
                , 1 AS depth
                , array[a._order] AS path
                , false AS cycle
                --, concat(a."Parent_id", a.id, a."_order") AS ord
                , a."_order" AS ord
                ,'folder' AS data_div
                , a.id AS folder_id
                , true AS is_folder
                , a._order AS folder_ord
                , CAST(null as INTEGER) AS item_ord
            FROM menu_folder a   
            WHERE 1=1
        '''
        if folder_id:
            sql += ''' AND (a.id = %(folder_id)s OR a."Parent_id" = %(folder_id)s)
            '''
        #else:
        #    sql += ''' and a."Parent_id" is null
        #    '''
        sql += ''' UNION ALL 
            SELECT 
                NULL as id
                , mi."MenuFolder_id" AS parentid              
                , mi."MenuCode"::text AS menu_code
                , mi."MenuName" AS name          
                , tree.depth + 1
                , array_append(tree.path, mi._order) AS path
                , mi."MenuFolder_id" = any(tree.path) AS cycle
                --, concat(tree.ord, tree.pid, mi."_order") AS ord
                , mi._order AS ord
                ,'menu' AS data_div
                , mi."MenuFolder_id" AS folder_id
                , false AS is_folder
                , null AS folder_ord
                , mi._order AS item_ord
            FROM menu_item mi 
            INNER JOIN tree ON mi."MenuFolder_id" = tree.id  
            WHERE mi."MenuCode" NOT IN ('wm_user_group', 'wm_user', 'wm_user_group_menu')
        )
        SELECT 
            tree.parentid AS "parentId"
            , tree.id
            , tree.menu_code
            , tree.name
            , tree.depth
            , tree.ord
            , ugm."UserGroup_id"
            , ugm."AuthCode"
            , CASE WHEN tree.is_folder THEN NULL ELSE COALESCE(ugm."AuthCode" LIKE '%%R%%', FALSE) END AS r
            , CASE WHEN tree.is_folder THEN NULL ELSE COALESCE(ugm."AuthCode" LIKE '%%W%%', FALSE) END AS w
            , CASE WHEN tree.is_folder THEN NULL ELSE COALESCE(ugm."AuthCode" LIKE '%%X%%', FALSE) END AS x
            , tree.is_folder
            , ugm.id as ugm_id
        FROM tree 
        LEFT JOIN user_group_menu ugm ON ugm."MenuCode" = tree.menu_code 
        AND ugm."UserGroup_id" = %(group_id)s
        WHERE 1=1
        AND ((tree.id IN (SELECT t2.parentid FROM tree t2)) OR tree.is_folder = FALSE)
        ORDER BY tree.folder_ord, tree.item_ord
        '''        
        
        items = []
        try:
            dc  = {}
            dc['group_id'] = group_id
            dc['folder_id'] = folder_id

            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_usergroupmenu_list', ex)
            raise ex

        return items

    def get_bookmark_list(self, user_id):
        
        sql = '''
        select mi."MenuName" as name 
        , mi."MenuCode" as code 
        , mi."Url" as url
        --, false as ismanual
        , 0 as ismanual
        from bookmark bm 
        inner join menu_item mi on bm."MenuCode" = mi."MenuCode" 
        where bm."User_id" = %(user_id)s
        order by 1
        '''
        items = []
        try:
            dc = {'user_id':user_id}
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_bookmakr_list', ex)
            raise ex

        return items

    def get_storyboard_item_list(self):
        items = []
        sql = ''' 
        SELECT 
	        si.id
	        , (CASE 
		        WHEN si."BoardType" ='menu' 
		        THEN CONCAT(mi."MenuName", '(', mf."FolderName", ')')
		        ELSE df."FormName" 
		        END) AS name
	        , si."BoardType"
	        , fn_code_name('story_board_type', si."BoardType" ) AS "BoardTypeName"
	        , si."Duration"
	        , si."Url"
	        , up."Name" AS writer
	        , TO_CHAR(si._created ,'yyyy-mm-dd hh24:mi:ss') AS created
	        , si."ParameterData"
        FROM storyboard_item si 
        LEFT JOIN menu_item mi ON mi."MenuCode" = si."MenuCode" 
        LEFT JOIN menu_folder mf ON mf.id = mi."MenuFolder_id" 
        LEFT JOIN doc_form df ON df.id = CAST(si."ParameterData" AS integer)
        LEFT JOIN user_profile up ON up."User_id" = si._creater_id 
        ORDER BY id       
        '''
        try:
            items = DbUtil.get_rows(sql)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_storyboard_item_list', ex)
            raise ex

        return items

    def get_system_code_list(self, code_type, keyword):

        
        sql = ''' 
        select
          id 
          ,CodeType  , Code , Value , Description, _ordering 
        from sys_code sc 
        where 1=1
        '''

        if code_type:
            sql += ''' and CodeType = %(code_type)s '''

        if keyword:
            sql += ''' and Value = %(keyword)s '''

        sql+=''' order by CodeType , _ordering , Value 
            '''

        try:
            dc = {'code_type':code_type, 'keyword':keyword}
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_system_code_list', ex)
            raise ex

        return items

    def get_systemlog_list(self, start, end, type, source):
        sql = ''' select id
        , "Type" as type
        , "Source" as source
        , "Message" as message
        , to_char(_created ,'yyyy-mm-dd hh24:mi:ss') as created
        from sys_log sl
        where _created between %(start)s and %(end)s
        '''
        if type:
            sql += '''and "Type" ilike concat('%%',%(type)s,'%%')
            '''
        if source:
            sql += '''and "Source" ilike concat('%%', %(source)s, '%%')
            '''
        sql += ''' order by _created desc
            '''
        items = []
        try:
            dc = {}
            dc['start'] = start
            dc['end'] = end
            dc['type'] = type
            dc['source'] = source
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_systemlog_list', ex)
            raise ex
        return items


    def get_holiday_list(self, keyword, year):
        
        sql = ''' 
        SELECT nation_cd, name_val, repeat_yn, holidate, id
        FROM holiday
        where 1=1
        '''
        if keyword:            
            sql += '''and "name_val" like concat('%%',%(keyword)s,'%%')
            '''
        if year:
            sql += ''' and left(holidate, 4) = %(year)s '''

        sql+=''' order by nation_cd , holidate , name_val 
            '''

        try:
            dc = {'keyword':keyword, 'year':year}
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemService.get_holiday_list', ex)
            raise ex

        return items

    @classmethod
    def get_system_title(cls):
        q = SystemOption.objects.filter(Code='LOGO_TITLE').values('Value')
        option = q.first()
        if option:
            system_title = option.get('Value')
        else:
            system_title = 'Yullin MES21'

        return system_title


    @classmethod
    def get_system_option(cls, Code):
        q = SystemOption.objects.filter(Code=Code).values('Value')
        option = q.first()
        if option:
            Value = option.get('Value')
        else:
            Value = ''

        return Value
