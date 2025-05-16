from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipPartMtrl
#from django.db import transaction

def equip_part_mtrl(context):
    '''
    api/kmms/equip_part_mtrl    설비부품자재
    김태영 

    findAllEquipBom
    countByEquipBom
    searchOne
    getBomListByMaterial
    update
    delete
    deleteEquipPartMtrl
    insert
    insertNotExists
    findAllByMaterialUse    자재사용설비목록
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action in ['findAllEquipBom', 'xxx']:
            mtrlGroupYn = gparam.get('mtrlGroupYn')
            equipPk = CommonUtil.try_int(gparam.get('equipPk'))
            deptPk = CommonUtil.try_int(gparam.get('deptPk'))

            sql = ''' select t.mtrl_pk, m.mtrl_cd, m.mtrl_nm
            '''
            if mtrlGroupYn:
                sql += ''', t.equip_pk, e.equip_cd, e.equip_nm, t.amt
                '''
            sql += ''' , mc.code_cd as mtrl_class_nm, m.mtrl_dsc
				, m.safety_stock_amt, au.code_nm as amt_unit_nm
				, od.id as dept_pk, od."Code" as dept_cd, od."Name" as dept_nm
				, l.loc_pk, l.loc_cd, l.loc_nm
				, sum(case when abg.code_cd = 'AB_GRADE_A' then mi.inout_qty else 0 end) as a_stock_amt
				, sum(case when abg.code_cd = 'AB_GRADE_B' then mi.inout_qty else 0 end) as b_stock_amt
				, mi.loc_cell_addr
				, mi.inout_uprice
				, m.unit_price
				, m.unit_price_dt
				, s.supplier_nm
				, m.use_yn
		    from cm_equip_part_mtrl t
		    inner join cm_equipment e on t.equip_pk = e.equip_pk
		    inner join cm_material m on t.mtrl_pk = m.mtrl_pk
		    inner join cm_base_code mc on m.mtrl_class_cd_pk = mc.code_pk
		    left join cm_mtrl_inout mi on m.mtrl_pk = mi.mtrl_pk
		    left join cm_location l on mi.inout_loc_cd = l.loc_cd
		    left join dept od on od."Code" = mi.own_dept_cd
		    left join cm_base_code abg on abg.code_cd = mi.ab_grade
		    and abg.code_grp_cd = 'AB_GRADE'
		    left join cm_base_code au on au.code_pk  = m.amt_unit_pk
		    and au.code_grp_cd = 'AMT_UNIT'
		    left join cm_supplier s on s.supplier_pk = m.supplier_pk
		    left join dept ed on ed.id = e.dept_pk
		    where e.del_yn = 'N'
		    and e.disposed_date is null
		    and coalesce(mi.inout_cx_yn, 'N') = 'N'
            AND e.factory_pk = %(factory_pk)s
            '''
            if equipPk:
                sql += ''' and t.equip_pk = %(equipPk)s
                '''
            if deptPk:
                sql += ''' AND (
				    ed.id = %(deptPk)s
				    OR
				    ed.id in (select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
			    )
                '''
            sql += ''' group by t.mtrl_pk, m.mtrl_cd, m.mtrl_nm
            '''
            if mtrlGroupYn:
                sql += ''' , t.equip_pk, e.equip_cd, e.equip_nm, t.amt
                '''
            sql += ''' , mc.code_cd, m.mtrl_dsc, m.safety_stock_amt, au.code_nm
		    , od.id, od."Code" , od."Name" , l.loc_pk, l.loc_cd, l.loc_nm
		    , mi.loc_cell_addr, mi.inout_uprice, m.unit_price
		    , m.unit_price_dt, s.supplier_nm, m.use_yn
            ORDER BY m.mtrl_cd
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['deptPk'] = deptPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getEquipPartMtrls':
            equipPk = CommonUtil.try_int(gparam.get('equipPk'))          

            sql = ''' 
                    select t.equip_pk
			            , t.mtrl_pk
			            , m.mtrl_cd
			            , m.mtrl_nm
			            , t.amt
			        from cm_equip_part_mtrl t
			        inner join cm_material m on t.mtrl_pk = m.mtrl_pk
			        where t.equip_pk = %(equipPk)s		 
            '''

            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getEquipBomTree':
            equip_cd = gparam.get('equip_cd')

            sql = ''' 
                   		WITH RECURSIVE cte AS (
							select e1.equip_pk, e1.equip_cd, e1.equip_nm
							, 1 AS lvl
							, ARRAY[e1.equip_pk] AS path_info
							, ARRAY[cast(e1.equip_cd as text)] AS path_info_code
							, cast(null as bigint) as up_equip_pk
							, cast('' as text) as up_equip_cd
							, cast('' as text) as up_equip_nm
							, cast('' as text) as mtrl_cd
							, cast('' as text) as mtrl_nm
							, (select array_length(ve.path_info, 1) from (select * from cm_fn_get_equip('1', %(equip_cd)s)) ve) as curr_lvl
							, (select ve.path_info from (select * from cm_fn_get_equip('1', %(equip_cd)s)) ve) as curr_path
							from cm_equipment e1
							where e1.del_yn = 'N'
							and e1.up_equip_pk is null
							and e1.equip_pk = (select ve.path_info[1] from (select * from cm_fn_get_equip('1', %(equip_cd)s)) ve)
							UNION all
							select e2.equip_pk, e2.equip_cd, e2.equip_nm
							, s.lvl + 1 as lvl
							, s.path_info || e2.equip_pk as path_info
							, s.path_info_code || cast(e2.equip_cd as text) as path_info_code
							, s.equip_pk as up_equip_pk
							, s.equip_cd as up_equip_cd
							, s.equip_nm as up_equip_nm
							, m.mtrl_cd
							, m.mtrl_nm
							, s.curr_lvl
							, s.curr_path

							from cm_equipment e2
							inner join cte s on s.equip_pk = e2.up_equip_pk
							left outer join cm_equip_part_mtrl epm on e2.equip_pk = epm.equip_pk
							left outer join cm_material m on epm.mtrl_pk = m.mtrl_pk
							where e2.del_yn = 'N'
							and (e2.equip_pk = any (s.curr_path) or s.curr_lvl < (s.lvl + 1))
						)
						, cteall AS (
							select cte.equip_cd as disp_cd
							, equip_nm as disp_nm
							, cte.lvl as disp_lvl
							, cte.path_info_code as disp_path_info
							, cte.up_equip_cd as disp_up_cd
							, 1 as disp_ordr
							, cte.equip_pk
							, cte.curr_lvl
							, cte.curr_path
							from cte
							group by equip_cd, equip_nm, lvl, path_info_code, up_equip_cd, equip_pk, curr_lvl, curr_path
							union all
							select cte.mtrl_cd
							, cte.mtrl_nm
							, cte.lvl
							, cte.path_info_code
							, cte.equip_cd as disp_up_cd
							, 2 as disp_ordr
							, cte.equip_pk
							, cte.curr_lvl
							, cte.curr_path
							from cte
							where cte.lvl >= cte.curr_lvl
							group by mtrl_cd, mtrl_nm, lvl, path_info_code, equip_cd, equip_pk, curr_lvl, curr_path
						)
						select cteall.disp_cd
						, cteall.disp_up_cd
						, concat(cteall.disp_cd || ' : ' || cteall.disp_nm) as disp_nm
						, cteall.disp_lvl
						, cteall.disp_ordr
						, cteall.disp_lvl + (case when cteall.disp_ordr = 1 then 0 else 1 end) as disp_sub_lvl
						, (select count(*) from cteall x where x.disp_up_cd = cteall.disp_cd) as disp_sub_cnt
						from cteall
						where cteall.disp_cd <> ''
						order by cteall.disp_path_info, cteall.disp_ordr, cteall.disp_cd

            '''

            dc = {}
            dc['equip_cd'] = equip_cd

            items = DbUtil.get_rows(sql, dc)
 
        elif action == 'countByEquipBom':
            equipPk = CommonUtil.try_int(gparam.get('equipPk'))
            mtrlPk = CommonUtil.try_int(gparam.get('mtrlPk'))

            sql = ''' select count(*) as cnt
		    from equip_part_mtrl
		    WHERE equip_pk = %(equipPk)s
		    AND	mtrl_pk = %(mtrlPk)s
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['mtrlPk'] = mtrlPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'searchOne':
            equipPk = CommonUtil.try_int(gparam.get('equipPk'))
            mtrlPk = CommonUtil.try_int(gparam.get('mtrlPk'))

            sql = ''' SELECT t.equip_pk, e.equip_cd, e.equip_nm
		       , t.mtrl_pk, m.mtrl_nm
		       , t.amt
		       , l.loc_pk, l.loc_nm
		       , t.del_yn, t.use_yn
		       , t.insert_ts, t.inserter_id, t.inserter_nm
		       , t.update_ts, t.updater_id, t.updater_nm
		    FROM cm_equip_part_mtrl t
            INNER JOIN cm_equipment e ON t.equip_pk = e.equip_pk
            INNER JOIN cm_material m ON t.mtrl_pk = m.mtrl_pk
            INNER JOIN cm_location l ON e.loc_pk = l.loc_pk
            WHERE equip_pk = %(equipPk)s
		    AND	mtrl_pk = %(mtrlPk)s
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['mtrlPk'] = mtrlPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'getBomListByMaterial':
            equipPk = CommonUtil.try_int(gparam.get('equipPk'))
            mtrlPk = CommonUtil.try_int(gparam.get('mtrlPk'))

            sql = ''' select 	t.equip_pk
				, t.equip_cd
				, t.equip_nm
				, l.loc_cd
				, l.loc_nm
				, es.code_cd as equip_status_cd
				, es.code_nm as equip_status_nm
				, ir.import_rank_cd
				, ec.equip_category_id
				, ec.equip_category_desc
				, t.equip_class_path
				, t.equip_class_desc
				, cc.ccenter_nm
				, t.breakdown_dt
				, t.warranty_dt
				, t.disposed_date
				, t.install_dt
		    from cm_equipment t
		    inner join cm_location l on l.loc_pk = t.loc_pk
		    inner join cm_base_code es on es.code_cd  = t.equip_status
		    and es.code_grp_cd = 'EQUIP_STATUS'
		    left join cm_equip_category ec on ec.equip_category_id = t.equip_category_id 
		    left join cm_import_rank ir on ir.import_rank_pk = t.import_rank_pk 
		    left join cm_cost_center cc on cc.ccenter_cd = t.ccenter_cd
		    left join cm_equip_part_mtrl epm on epm.equip_pk = t.equip_pk
		    where epm.mtrl_pk = %(mtrlPk)s
		    and t.use_yn = 'Y' 
		    and t.del_yn = 'N'
		    AND t.factory_pk = %(factory_pk)s
		    order by t.equip_nm
            '''

            dc = {}
            dc['factory_pk'] = factory_id
            dc['mtrlPk'] = mtrlPk

            items = DbUtil.get_row(sql, dc)

        elif action in ['insert', 'update', 'insertNotExists']:
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            mtrlPk = CommonUtil.try_int(posparam.get('mtrlPk'))
            amt = posparam.get('amt')
            useYn = posparam.get('useYn', 'Y')
  
            if action == 'update':
                q = CmEquipPartMtrl.objects.filter(CmEquipment_id=equipPk)
                q = q.filter(CmMaterial_id=mtrlPk)
                c = q.first()
            else:
                if action == 'insertNotExists':
                    q = CmEquipPartMtrl.objects.filter(CmEquipment_id=equipPk)
                    q = q.filter(CmMaterial_id=mtrlPk)
                    if q.first():
                        return {'success': True, 'message': '이미 있는 데이터입니다.'} 

                c = CmEquipPartMtrl()
                c.CmEquipment_id = equipPk
                c.CmMaterial_id = mtrlPk
            c.Amt = amt
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비부품자재의 정보가 수정되었습니다.'}


        elif action == 'delete':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            CmEquipPartMtrl.objects.filter(CmEquipment_id=equipPk).delete()

            items = {'success': True}
    
        elif action == 'deleteEquipPartMtrl':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            mtrlPk = CommonUtil.try_int(posparam.get('mtrlPk'))
            q = CmEquipPartMtrl.objects.filter(CmEquipment_id=equipPk)
            q = q.filter(CmMaterial_id=mtrlPk)
            q.delete()

            items = {'success': True}

        elif action == 'findAllByMaterialUse':
            ''' 자재사용설비목록
            '''
            mtrlPk = CommonUtil.try_int(posparam.get('mtrlPk'))
            sql = ''' with cte as (
			    select 	t.mtrl_pk as materail_pk
				, t.mtrl_pk, m.mtrl_cd, m.mtrl_nm
				, t.equip_pk, e.equip_cd, e.equip_nm
				, es.code_nm as equip_status_nm
				, ec.equip_category_id, ec.equip_category_desc
				, e.equip_class_path, e.equip_class_desc
				, d."Name" as dept_nm
				, e.asset_nos
				, ir.import_rank_cd
				, e.environ_equip_yn
				, l.loc_pk, l.loc_nm
				, t.amt
				, e.use_yn
				, cm_fn_get_dept_path_names(d.id) as dept_path_nm
			    from cm_equip_part_mtrl t
			    inner join cm_equipment e on t.equip_pk = e.equip_pk
			    inner join cm_material m on t.mtrl_pk = m.mtrl_pk
			    inner join cm_location l on e.loc_pk = l.loc_pk
			    inner join cm_base_code es on e.equip_status = es.code_cd and es.code_grp_cd = 'EQUIP_STATUS'
			    inner join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
			    inner join dept d on e.dept_pk = d.id
			    left outer join cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
			    where m.mtrl_pk = %(mtrlPk)s
			    order by e.equip_cd, e.equip_nm
		    )
		    SELECT *
		    FROM (
			    table cte

		    ) sub
		    RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		    WHERE total_rows != 0
            '''
            dc = {}
            dc['mtrlPk'] = mtrlPk

            items = DbUtil.get_row(sql, dc)

    except Exception as ex:
        source = 'kmms/equip_part_mtrl : action-{}'.format(action)
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