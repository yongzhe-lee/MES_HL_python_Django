from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class MaterialService():

    def __init__(self):
        return

    def get_material_modal(self, keyword, mat_type, Supplier):
        items = []
        dic_param = {'keyword':keyword, 'mat_type':mat_type, 'Supplier':Supplier}

        sql = ''' 
        SELECT 
                m.id AS material_id
                , m."Factory_id" AS factory_id
                , f."Code" AS factory_code
                , f."Name" AS factory_name
                , m."Code" AS material_code
                , m."Name" AS material_name        
                , m."Standard" AS standard
                , m."mat_grp_id" AS mat_gpr_id
                , mg."Name" AS mat_grp_nm
                , m."mat_type" AS mat_type
                , c."Name" AS item_type_nm
                , m."BasicUnit" AS basic_unit
                , m."CycleTime" AS cycle_time
                , m."in_price" AS in_price
                , m."out_price" AS out_price
                , m.supplier_pk as supplier
                , co."Name" as supplier_nm
            FROM material m
                INNER JOIN factory f on m."Factory_id" = f.id
                left join mat_grp mg on mg.id=m.mat_grp_id
                left join code c on UPPER(c."CodeGroupCode") = 'MTRL_TYPE' and m."ItemType" = c."Code"
                left join company co on m.supplier_pk = co.id
            WHERE 1=1
        '''
        
        if keyword:
                sql += ''' 
                AND (
                    UPPER(m."Name") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(m."Code") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(mg."Name") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(m."mat_type") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                ) 
                '''
        if mat_type:
            sql += ''' 
            AND m.mat_type = %(ItemType)s
            '''

        if Supplier:
            sql += ''' 
            AND m.supplier_pk = %(Supplier)s
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


# 아래 품목그룸 코드를 mat_grp 테이블에 insert하는 구문을 작성
'''
--품목그룹
ESC_MGH60
ABS_MGH60
ESC-P_MGH60
SPAS
MAS35C
MAS65C
MOC
P/PACK
TOS/TAS
SRR
SPM
Yaw&G
ESC_MGH80
ABS_MGH80
MAS85C
LRR
FPC
ESC_MGH85
FCM
MRR
ABS_MGH100
ESC_MGH100
IDB
AOI
E-Coupling
PCU
'''


sql ='''
insert into mat_grp ("Code","Name", _created) 
values
('ESC_MGH60', 'ESC_MGH60', now()),
('ABS_MGH60', 'ABS_MGH60', now()),
('ESC-P_MGH60', 'ESC-P_MGH60', now()),
('SPAS', 'SPAS', now()),
('MAS35C', 'MAS35C', now()),
('MAS65C', 'MAS65C', now()),
('MOC', 'MOC', now()),
('P/PACK', 'P/PACK', now()),
('TOS/TAS', 'TOS/TAS', now()),
('SRR', 'SRR', now()),
('SPM', 'SPM', now()),
('Yaw&G', 'Yaw&G', now()),
('ESC_MGH80', 'ESC_MGH80', now()),
('ABS_MGH80', 'ABS_MGH80', now()),
('MAS85C', 'MAS85C', now()),
('LRR','LRR' ,now()),
('FPC','FPC' ,now()),
('ESC_MGH85','ESC_MGH85' ,now()),
('FCM','FCM' ,now()),
('MRR','MRR' ,now()),
('ABS_MGH100','ABS_MGH100' ,now()),
('ESC_MGH100','ESC_MGH100' ,now()),
('IDB','IDB' ,now()),
('AOI','AOI' ,now()),
('E-Coupling','E-Coupling' ,now()),
('PCU','PCU' ,now());


'''