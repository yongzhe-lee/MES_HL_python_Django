from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class EquipmentGroupService():
    def __init__(self):
        pass

    
    def get_equipment_group_list(self, keyword):
        '''

        '''
        items=[]
        dic_param = {'keyword': keyword}
        if settings.DBMS =='MSSQL' :
            sql = '''
            select eg.id
                , eg."Name" as equipment_group_name
                , eg."Code" as equipment_group_code
                , dbo.fn_code_name('equipment_type', eg."EquipmentType") as equipment_type
            from equ_grp eg 
            where 1=1
            '''
        else : 
            sql = '''
            select eg.id
                , eg."Name" as equipment_group_name
                , eg."Code" as equipment_group_code
                , fn_code_name('equipment_type', eg."EquipmentType"::text) as equipment_type
                , eg."Description" as description
            from equ_grp eg 
            where 1=1
            '''

        if keyword:
            sql += ''' and upper(eg."Name") like concat('%%',upper(%(keyword)s),'%%')
            '''

        sql += ''' order by id desc'''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentGroupService.get_equipment_group_list', ex)
            raise ex

        return items


    def get_equipment_group_detail(self, group_id):
        '''

        '''
        dic_param = { 'group_id': group_id }
        sql = '''
        select eg.id
            , eg."Name" as equipment_group_name
            , eg."Code" as equipment_group_code
            , eg."EquipmentType" as equipment_type
            , eg."Description" as description
        from equ_grp eg 
        where 1=1
        and eg.id = %(group_id)s
        '''

        equipment_group = {}
        try:
            equipment_group = DbUtil.get_row(sql, dic_param)

        except Exception as ex:
            LogWriter.add_dblog('error', 'EquipmentGroupService.get_equipment_group_detail', ex)
            raise ex

        return equipment_group

