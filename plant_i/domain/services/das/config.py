from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class DASConfigService():

    def __init__(self):
        return

    def get_das_config_list(self, server, equipment):
        items = []

        dic_param = {
            'server': server,
            'equipment':equipment,
            }

        sql = '''
            select 
                dc.id,
                dc."Name",
                dc."Description",
                dc."Handler",
                dc."DeviceType",
                dc."Configuration",
                dc."ConfigFileName",
                dc."Topic",
                dc."Equipment_id",
                e."Name" as equipment_name,
                dc."Server_id" ,
                dc.is_active,
                to_char(dc._created ,'yyyy-mm-dd hh24:mi:ss') as created,
                ds."Name" as server_name
            from das_config dc
                left outer join das_server ds on dc."Server_id" = ds.id 
                left outer join equ e on e.id = dc."Equipment_id"
            where 1=1
        '''
        if server:
            sql+='''
            and dc."Server_id"=%(server)s
            '''
        if equipment:
            sql+='''
            and dc."Equipment_id"=%(equipment)s
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','DASConfigService.get_das_config_list', ex)
            raise ex

        return items


    def get_das_config_detail(self, id):
        items = []

        dic_param = {'id': id}

        sql = '''
            select 
                dc.id,
                dc."Name",
                dc."Description",
                dc."Handler",
                dc."DeviceType",
                dc."Configuration",
                dc."ConfigFileName",
                dc."Topic",
                dc."Equipment_id",
                e."Name" as equipment_name,
                dc."Server_id" ,
                --case when dc.is_active is true then 'Y' else 'N' end as is_active,
                dc.is_active,
                to_char(dc._created ,'yyyy-mm-dd hh24:mi:ss') as created,
                ds."Name" as server_name
            from das_config dc
                left outer join das_server ds on dc."Server_id" = ds.id 
                left outer join equ e on e.id = dc."Equipment_id"
            where dc.id=%(id)s
        '''
        data = {}
        try:
            items = DbUtil.get_rows(sql, dic_param)
            if len(items)>0:
                data = items[0]

        except Exception as ex:
            LogWriter.add_dblog('error','DASConfigService.get_das_config_detail', ex)
            raise ex

        return data