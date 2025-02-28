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
                , m."BasicUnit" AS basic_unit
                , m."CycleTime" AS cycle_time
                , m."in_price" AS in_price
                , m."out_price" AS out_price
                , m.supplier_pk
            FROM
                material m
            INNER JOIN
                factory f on m."Factory_id" = f.id
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

