from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

from domain.models.definition import Unit

def unit(context):
    '''
    /api/definition/unit
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    action = gparam.get('action', 'read')
    try:
        if action =='read':
            ''' 
            site_id가 유저마다 매핑되어 있지 않음
            shutdownHistoryNo은 lims 소스에서도 사용되고 있지 않기 때문에 누락
            '''

            keyword = gparam.get('srch_keyword')
            use_yn = 'Y' if gparam.get('srch_use_yn') == 'on' else 'N'
            plant_id = CommonUtil.try_int(gparam.get('srch_plant_id'))

            sql = '''
            select
                u.id as unit_id,
                u.code as unit_code,
                u.name as unit_name,
                p.id as plant_id,
                p.name as plant_name,
                u.remark as rmk,
                u.useyn as use_yn,
                u.disporder as display_order,
                u._creater_id,
                up.name as _creater,
                date_format(u._created, '%%Y-%%m-%%d %%H:%%i') as _craeted,
                u._modifier_id,
                uu.name as _modifier,
                date_format(u._modified, '%%Y-%%m-%%d %%H:%%i') as _modified
            from unit u
            inner join plant p on u.plant_id = p.id
            left join user_profile up on u._creater_id = up.user_id
            left join user_profile uu on u._modifier_id = uu.user_id
            where u.delyn != 'Y'
            '''

            if use_yn:
                sql += " and u.useyn = %(use_yn)s"
                
            if keyword:
                sql += '''
                and (
                    upper(u.code) like concat('%%', upper(%(keyword)s), '%%')
                    or upper(u.name) like concat('%%', upper(%(keyword)s), '%%')
                    or upper(u.remark) like concat('%%', upper(%(keyword)s), '%%')
                )
                '''
                
            if plant_id and plant_id > 0:
                sql += " and p.id = %(plant_id)s"
    
            sql += " order by u.disporder"

            dc = {
                'use_yn': use_yn,
                'keyword': keyword,
                'plant_id': plant_id,
            }
    
            result = DbUtil.get_rows(sql, dc)
            
        elif action == 'save':
            unit_code = posparam.get('unit_code')
            unit_name = posparam.get('unit_name')
            plant_id = CommonUtil.try_int(posparam.get('plant_id'))
            rmk = posparam.get('rmk')
            disp_order = CommonUtil.try_int(posparam.get('display_order'))
            use_yn = 'Y' if posparam.get('use_yn') == 'on' else 'N'
            unit_id = CommonUtil.try_int(posparam.get('unit_id'))
            
            # 신규등록일 경우 중복 체크
            if unit_id is None:
                unit_name_query = Unit.objects.filter(Name=unit_name)
                if unit_name_query.count() > 0:
                    return {'success': False, 'message': '중복된 데이터가 있습니다.'}
            
            unit = None
            unit_query = Unit.objects.filter(id=unit_id)
            if unit_query.count() == 0:
                unit = Unit()
                unit.DelYn = 'N'
            else:
                unit = unit_query.first()
                
            unit.Code = unit_code
            unit.Name = unit_name
            unit.Plant_id = plant_id
            unit.Remark = rmk
            unit.DispOrder = disp_order
            unit.UseYn = use_yn
            unit.set_audit(user)
            unit.save()

            result = {'success': True, 'message': '저장되었습니다.'}
            
        elif action == 'delete':
            unit_id = CommonUtil.try_int(posparam.get('unit_id'))
            
            unit_query = Unit.objects.filter(id=unit_id, DelYn='N')
            if unit_query.count() == 0:
                return {'success': False, 'message': '이미 삭제된 공정입니다.'}
            
            unit = unit_query.first()
            unit.DelYn = 'Y'
            unit.set_audit(user)
            unit.save()
            
            result = {'success': True, 'message': '삭제되었습니다.'}
            
    except Exception as ex:
        source = '/api/definition/unit, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)

    return result