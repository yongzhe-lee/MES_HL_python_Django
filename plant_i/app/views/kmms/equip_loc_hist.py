from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipLocHist
#from django.db import transaction

def equip_loc_hist(context):
    '''
    api/kmms/equip_loc_hist    설비위치 변경이력
    김태영 

    getLocFullPath
    findByEquipPk
    insert
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'getLocFullPath':
            befLocPk = gparam.get('befLocPk')
            aftLocPk = gparam.get('aftLocPk')

            sql = ''' 	with t as (
			    select string_agg(cte1.loc_nm, ',') as bef_loc_path
			    , '' as aft_loc_path
			    from (
				    select x.loc_pk, x.path_info_pk, l.label as loc_nm
				    from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x
				    inner join (select * from cm_fn_get_site_loc_tree(%(factory_pk)s)) l on x.path_info_pk = l.id
				    where x.loc_pk = %(befLocPk)s
				    order by l."lvl"
			    ) cte1
			    union all
			    select '' as bef_loc_path
			    , string_agg(cte2.loc_nm, ',') as aft_loc_path
			    from (
				    select x.loc_pk, x.path_info_pk, l.label as loc_nm
				    from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x
				    inner join (select * from cm_fn_get_site_loc_tree(%(factory_pk)s)) l on x.path_info_pk = l.id
				    where x.loc_pk = %(aftLocPk)s
				    order by l."lvl"
			        ) cte2
		    )
            select 	max(t.bef_loc_path) as bef_loc_path
			, max(t.aft_loc_path) as aft_loc_path
		    from t
            '''

            dc = {}
            dc['befLocPk'] = befLocPk
            dc['aftLocPk'] = aftLocPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'findByEquipPk':
            equipPk = gparam.get('equipPk')

            sql = ''' select 	t.equip_loc_hist_pk
			, t.equip_pk
			, e.equip_cd
			, e.equip_nm
			, t.equip_loc_bef
			, t.equip_loc_aft
			, to_char(t.insert_ts, 'YYYY-MM-DD HH24:MI') as insert_ts
			, t.inserter_id
			, t.inserter_nm
		from cm_equip_loc_hist t
		inner join cm_equipment e on t.equip_pk = e.equip_pk
		where t.equip_pk = %(equipPk)s
		order by t.insert_ts desc
            '''

            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_row(sql, dc)


        elif action == 'insert':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            equipLocBef = posparam.get('equipLocBef')
            equipLocAft = posparam.get('equipLocAft')
            businessClassNm = posparam.get('businessClassNm')

            c = CmEquipLocHist()

            c.CmEquipment_id = equipPk
            c.EquipLocBefore = equipLocBef
            c.EquipLocAfter = equipLocAft
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비위치 변경이력의 정보가 수정되었습니다.'}


    except Exception as ex:
        source = 'kmms/equip_loc_hist : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items

    return items