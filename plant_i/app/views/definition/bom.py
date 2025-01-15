import datetime

from django.db import transaction
from django.db.models import Q

from domain.services.common import CommonUtil
from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.definition import BOM, BOMComponent, Material
from domain.services.definition.bom import BOMService
from configurations import settings

def bom(context):

    items = []
    gparam = context.gparam
    posparam = context.posparam
    request = context.request

    action = gparam.get('action')
    bom_service = BOMService()
    try:
        if action=='read':
            mat_type = gparam.get('mat_type', '')
            mat_group = gparam.get('mat_group', '')
            bom_type = gparam.get('bom_type', '')
            mat_name = gparam.get('mat_name', '')
            not_past_flag = gparam.get('not_past_flag', '')
            items = bom_service.get_bom_list(mat_type, mat_group, bom_type, mat_name, not_past_flag)

        elif action=='detail':
            id = gparam.get('id')
            items = bom_service.get_bom_detail(id)

        elif action=='bom_delete':
            id = posparam.get('id')
            count = BOM.objects.filter(id=id).delete()
            items = {'success': True, 'count': count}

        elif action=='save':
            id = posparam.get('id')
            Material_id = posparam.get('Material_id')
            StartDate = posparam.get('StartDate') + ' 00:00:00'
            EndDate = posparam.get('EndDate') + ' 23:59:59'
            BOMType = posparam.get('BOMType')
            Version = posparam.get('Version')
            bom = None
            
            bom_chk = BOM.objects.filter(Material=Material_id, BOMType=BOMType, Version=Version)

            if id:
                print('update')
                bom = BOM.objects.get(id=id)
                bom_chk = bom_chk.exclude(id=id)

            else:
                bom = BOM()

            duplicate_flag = bom_service.bom_duplicate_check(id, Material_id, StartDate, EndDate, BOMType )
            if duplicate_flag:
                items = {'success': False, 'id': bom.id, 'message' : '기간이 겹치는 동일 제품의 \n BOM이 존재합니다.'}

            else:

                if bom_chk : 
                    return {'success': False, 'id': bom.id, 'message' : '중복된 BOM버전이 존재합니다. '}

                bom.Name = posparam.get('Name')
                bom.Material_id = Material_id
                bom.BOMType = BOMType
                bom.OutputAmount = posparam.get('OutputAmount')
                bom.Version = posparam.get('Version')
                bom.StartDate = StartDate
                bom.EndDate = EndDate
                bom.save()

                items = {'success': True, 'id': bom.id}

        elif action in ('bom_replicate', 'bom_revision'):
            id = posparam.get('id')
            today = DateUtil.get_today_string()
            yesterday = DateUtil.get_yesterday()
            now = DateUtil.get_current_datetime()

            src_bom = BOM.objects.get(id=id)

            with transaction.atomic():
                if action == 'bom_revision':
                    src_bom.EndDate = yesterday 
                    src_bom.save()
                    new_version = str(round(CommonUtil.try_float(src_bom.Version,0) + 1, 1))
                    new_name = src_bom.Name + ' V' + str(new_version)
                else:
                    new_version = str(round(CommonUtil.try_float(src_bom.Version,0) + 0.1, 1))
                    new_name = src_bom.Name + '_Copy'

                new_bom = BOM()
                new_bom.Name = new_name
                new_bom.Material_id = src_bom.Material_id
                new_bom.BOMType = src_bom.BOMType
                new_bom.OutputAmount = src_bom.OutputAmount
                new_bom.Version =   new_version

                if action == 'bom_revision':
                    new_bom.StartDate = today
                    new_bom.EndDate = '2100-12-31'

                    duplicate_flag = bom_service.bom_duplicate_check(src_bom.id, src_bom.Material_id, today, '2100-12-31', src_bom.BOMType )
                    if duplicate_flag:
                        return {'success': False, 'id': src_bom.id, 'message' : '기간이 겹치는 동일 제품의 \n BOM이 존재합니다.'}
                else:
                    bom_check = BOM.objects.filter(Material_id = src_bom.Material_id).filter(Q(StartDate = '1900-01-01') | Q(EndDate = '1900-01-01'))

                    if bom_check:
                        return {'success': False, 'id': src_bom.id, 'message' : '복제된 BOM중 수정되지 않은 BOM이 \n 존재하여 복제를 수행할 수 없습니다.'}

                    new_bom.StartDate = '1900-01-01'
                    new_bom.EndDate = '1900-01-01'

                new_bom.save()
                new_id = new_bom.id 
                sql = '''
                INSERT INTO bom_comp("BOM_id", "Material_id" , "Amount" , _order , "Description" , "_created" , "_creater_id" )
	            SELECT %(new_pk)s AS bom_pk, "Material_id" , "Amount" , _order , "Description" , now() , %(user_pk)s
	            FROM bom_comp bc 
	            WHERE "BOM_id" = %(bom_pk)s
                '''
                now_time = DateUtil.get_current_datetime().strftime('%Y-%m-%d %H:%M:%S')
            
                dc = {}
                dc['bom_pk'] = id
                dc['new_pk'] = new_id
                dc['now_date'] = now_time   
                dc['user_pk'] = request.user.id
                ret = DbUtil.execute(sql, dc)

                items = {
                    'success': True, 
                    'new_id':new_id
                }

        elif action=='material_detail':
            id = gparam.get('id')
            items = bom_service.get_bom_material_detail(id)

        elif action=='bom_comp_list':
            id = gparam.get('id')
            items = bom_service.get_bom_material_list(id)

        elif action=='material_list':
            id = gparam.get('id')
            items = bom_service.get_bom_material_tree_list(id)

        elif action=='material_save':
            id = posparam.get('id')
            bom_pk = posparam.get('BOM_id')
            mat_pk = posparam.get('Material_id')
            amount = posparam.get('Amount')
            _order = posparam.get('_order')
            description = posparam.get('Description')      

            bom_component = None
            if id:
                bom_component = BOMComponent.objects.get(id=id)
            else:
                if not bom_service.is_safe_child(bom_pk, mat_pk):
                    items = {'success':False, 'message':'Parent is in Children.' }
                    return items

                if len(BOMComponent.objects.filter(BOM_id=bom_pk).filter(Material_id=mat_pk)) != 0:
                    items = {'success':False, 'message':'이미 존재하는 품목입니다.' }
                    return items

                bom_component = BOMComponent()
                bom_component.BOM_id = bom_pk
                # order 순서를 계산해야된다

            bom_component.Material_id = mat_pk
            bom_component.Amount = amount
            bom_component._order = CommonUtil.try_int(_order, 0)
            bom_component.Description = description
            bom_component.save()

            items = {'success':True, 'id' : bom_component.id}

        elif action=='material_delete':
            success = False
            id = posparam.get('id')
            if id:
                bom_component = BOMComponent.objects.filter(id=id).delete()
                success = True

            items = {'success': success}
        
        elif action=='save_bom_comp_all':
            
            bom_pk = posparam.get('bom_id')
            lines = posparam.get('lines')
            
            lines = lines.split(chr(10))

            BOMComponent.objects.filter(BOM_id=bom_pk).delete()
            bom_component = None
            for index, line in enumerate(lines):
                cols = line.split(chr(9))  #sep=tab
                if len(cols) < 2:
                    continue
                mat_code = cols[0]
                amount = cols[1]
                amount = CommonUtil.try_float(amount, 0)
                if len(cols) > 2:
                    description = cols[2]    
                else:
                    description = ''
            
                bom_component = None

                q = Material.objects.filter(Code=mat_code)
                mat = q.first()
                if not mat:
                    continue

                mat_pk = mat.id

                if not bom_service.is_safe_child(bom_pk, mat_pk):
                    items = {'success':False, 'message':'Parent is in Children.' }
                    return items

                bom_component = BOMComponent()
                bom_component.BOM_id = bom_pk

                bom_component.Material_id = mat_pk
                bom_component.Amount = amount
                bom_component._order = index + 1
                bom_component.Description = description
                bom_component.save()

            items = {'success':True, 'id' : bom_pk}

        elif action == 'save_bom_comp_order':
            #list = json.loads(posparam.get('list'))
            ids = posparam.get('Q')
            index = 1
            for item in ids:
                pk = item.get('id')
                work_index = index
                BOMComponent.objects.filter(id=pk).update(_order = index)
                index += 1

            items = {'success':True}
    except Exception as ex:
        source = '/api/definition/bom'
        LogWriter.add_dblog('error', source, ex)
        if action == 'bom_delete' or 'material_delete':
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
