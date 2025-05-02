from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
#from django.db import transaction
from domain.models.definition import Material
from domain.services.definition.material import MaterialService

def material(context):
    '''
    /api/definition/material
    
    작성명 : 품목정보
    작성자 : 
    작성일 : 
    비고 :

    -수정사항-
    수정일             작업자     수정내용

    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request

    material_service = MaterialService()
    
    action = gparam.get('action', 'read')
    source = f'/api/definition/material?action={action}'
    try:
        if action =='read':

            factory = gparam.get('srch_factory')            
            keyword = gparam.get('keyword')

            sql = '''
            SELECT 
                m.id AS material_id
                , m."Factory_id" AS factory_id
                , f."Code" AS factory_code
                , f."Name" AS factory_name
                , m."Code" AS material_code
                , m."Name" AS material_name
                , m.bare_pcb_cd
                , m.panel_mag
                , m.pcb_array
                , m.sap_top_bottom
                , m.solder_paste
                , m.sub_pcb_cd
                , m.top_bottom
                , m.use_yn
                /* ItemType 같은 field 2번 생성하심. 나중에 여쭤보고 삽입 */
                -- , m."Type" AS material_type
                , m."Standard" AS standard
                , mg."Name" AS mat_grp_nm
                , m.mat_type
                , c."Name" AS item_type_nm
                , m."BasicUnit" AS basic_unit
                , m."CycleTime" AS cycle_time
                , m."in_price" AS in_price
                , m."out_price" AS out_price
                , m.supplier_pk as supplier
                , co."Name" as supplier_nm
            FROM  material m
                left join mat_grp mg on mg.id=m.mat_grp_id 
                INNER JOIN factory f on m."Factory_id" = f.id
                left join code c on UPPER(c."CodeGroupCode") = 'MTRL_TYPE' and m."ItemType" = c."Code"
                left join company co on m.supplier_pk = co.id
            WHERE 1=1
            '''
            if factory:
                sql += ''' 
                AND f.id = %(factory)s
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

            sql += '''
            ORDER BY m."Name"
            '''

            dc = {}
            dc['factory'] = factory
            dc['keyword'] = keyword
            
            result = DbUtil.get_rows(sql, dc)

        if action =='read_modal':

            keyword = gparam.get('keyword')            
            ItemType = gparam.get('ItemType')   
            Supplier = gparam.get('Supplier')

            result = material_service.get_material_modal(keyword, ItemType, Supplier)        

        elif action == 'detail':
            id = gparam.get('id')
            
            sql = '''
                SELECT 
                m.id AS material_id
                , m."Factory_id" AS factory_id
                , f."Code" AS factory_code
                , f."Name" AS factory_name
                , m."Code" AS material_code
                , m."Name" AS material_name
                /* ItemType 같은 field 2번 생성하심. 나중에 여쭤보고 삽입 */
                -- , m."Type" AS material_type
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
            FROM  material m
                INNER JOIN factory f on m."Factory_id" = f.id
                left join code c on UPPER(c."CodeGroupCode") = 'MTRL_TYPE' and m."ItemType" = c."Code"
                left join company co on m.supplier_pk = co.id
                    and m.id = %(id)s
            '''

            dc = {}
            dc['id'] = id
            
            result = DbUtil.get_row(sql, dc)

        elif action == 'save':
            id = CommonUtil.try_int(posparam.get('material_id'))
            factory_id = CommonUtil.try_int(posparam.get('factory_id'))
            material_code = posparam.get('material_code') 
            material_name = posparam.get('material_name') 
            standard = posparam.get('standard')
            mat_grp_id = posparam.get('mat_grp_id')
            item_type = posparam.get('item_type')
            supplier = posparam.get('supplier')
            basic_unit = posparam.get('basic_unit')
            cycle_time = CommonUtil.blank_to_none(posparam.get('cycle_time'))
            in_price = CommonUtil.blank_to_none(posparam.get('in_price'))
            out_price = CommonUtil.blank_to_none(posparam.get('out_price'))

            try:
                if id:
                    material = Material.objects.filter(id = id).first()
                else:
                    material = Material()
                
                material.Factory_id = factory_id
                material.Code = material_code
                material.Name = material_name
                material.Standard = standard
                material.MAterialGroup_id = mat_grp_id
                material.ItemType = item_type
                material.supplier_pk = supplier
                material.BasicUnit = basic_unit
                material.CycleTime = cycle_time
                material.in_price = in_price
                material.out_price = out_price
                material.set_audit(request.user)
                material.save()

                result = {'success' : True}

            except Exception as ex:
                source = 'api/definition/material, action:{}'.format(action)
                LogWriter.add_dblog('error', source, ex)
                raise ex

        elif action == 'delete':
            id = posparam.get('material_id')

            if id:
                material = Material.objects.filter(id = id).first()
                material.delete()

            result = {'success' : True}

        elif action=="smt_mat_info_excel":
            import openpyxl

            mat_file = "c:\\temp\\SMT 제품 정보.xlsx"
            workbook = openpyxl.load_workbook(mat_file)
            sheet = workbook['제품']

            dic_mat_grp = {}

            for row in sheet.iter_rows(min_row=3, max_row=sheet.max_row):
                mat_cd = row[0].value
                mat_nm = row[1].value
                mat_grp = row[2].value

                print(mat_cd)

                if mat_grp not in dic_mat_grp:
                    dic_mat_grp[mat_grp] = mat_grp



            for mg in dic_mat_grp:
                print(mg)

            workbook.close()
            

    except Exception as ex:
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False, 'message':str(ex) }

    return result