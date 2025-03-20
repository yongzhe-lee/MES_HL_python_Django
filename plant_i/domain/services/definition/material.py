from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class MaterialService():

    def __init__(self):
        return

    def get_material_modal(self, keyword, ItemType, Supplier):
        items = []
        dic_param = {'keyword':keyword, 'ItemType':ItemType, 'Supplier':Supplier}

        sql = ''' 
        SELECT 
                m.id AS material_id
                , m."Factory_id" AS factory_id
                , f."Code" AS factory_code
                , f."Name" AS factory_name
                , m."Code" AS material_code
                , m."Name" AS material_name        
                , m."Standard" AS standard
                , m."ItemGroup" AS item_group
                , m."ItemType" AS item_type
                , c."Name" AS item_type_nm
                , m."BasicUnit" AS basic_unit
                , m."CycleTime" AS cycle_time
                , m."in_price" AS in_price
                , m."out_price" AS out_price
                , m.supplier_pk as supplier
                , co."Name" as supplier_nm
            FROM material m
                INNER JOIN factory f on m."Factory_id" = f.id
                left join code c on UPPER(c."CodeGroupCode") = 'MTRL_TYPE' and m."ItemType" = c."Code"
                left join company co on m.supplier_pk = co.id
            WHERE 1=1
        '''
        
        if keyword:
                sql += ''' 
                AND (
                    UPPER(m."Name") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(m."Code") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(m."ItemGroup") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(m."ItemType") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                ) 
                '''
        if ItemType:
            sql += ''' 
            AND f.id = %(ItemType)s
            '''

        if Supplier:
            sql += ''' 
            AND f.id = %(Supplier)s
            '''
        sql += '''
        ORDER BY m."Name"
        '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','MaterialService.get_material_modal', ex)
            raise ex

        return items

