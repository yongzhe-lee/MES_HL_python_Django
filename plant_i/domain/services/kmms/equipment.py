from configurations import settings
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class EquipmentService():
	def __init__(self):
		return

	def searchEquipment(self, keyword, equip_status, loc_pk, equip_category_id, equip_class_path, supplier_pk, use_yn, environ_equip_yn):
		items = []
		dic_param = {'keyword': keyword, 'equip_status': equip_status, 'loc_pk': loc_pk, 'equip_category_id': equip_category_id, 'equip_class_path': equip_class_path, 'supplier_pk': supplier_pk, 'use_yn': use_yn, 'environ_equip_yn': environ_equip_yn}

		sql = ''' 
        with cte as (

		select t.equip_pk
		, cm_fn_get_incineration(l.loc_pk) as incinerator

		, t.equip_cd
		, t.equip_nm
		, l.loc_pk
		, l.loc_cd
		, l.loc_nm
		, l.up_loc_pk
		, ul.loc_cd as up_loc_cd
		, ul.loc_nm as up_loc_nm
		, case when ul.loc_nm is null then l.loc_nm
			   else ul.loc_nm ||  ' \ '  || l.loc_nm
		  end as up_loc_path
		, t.equip_status
		, t.equip_status as equip_status_cd
		, es.code_nm as equip_status_nm
		, ir.import_rank_cd as import_rank_nm
		, t.import_rank_pk
		, ir.import_rank_cd
		, ec.equip_category_id
		, ec.equip_category_desc
		, ec.remark as equip_category_remark
		, t.ccenter_cd
		, cc.ccenter_nm
		, t.dept_pk
		, d."Code"
		, d."Name"
		, t.up_equip_pk
		, eu.equip_nm as up_equip_nm
		, eu.equip_cd as up_equip_cd
		, t.disposed_type
		, t.disposed_type as disposed_type_cd
		, dt.code_nm as disposed_type_nm
		, t.disposed_date
		, t.breakdown_dt
		, t.warranty_dt
		, t.install_dt
		, t.asset_nos
		, t.environ_equip_yn
		, count(epm.mtrl_pk) as mtrl_cnt
		, t.use_yn
		, t.supplier_pk
		, s.supplier_nm
		, t.make_dt
		, t.buy_cost
		, t.maker_pk
		, sm.supplier_nm as maker_nm
		, t.mtrl_pk
		, m.mtrl_cd
		, m.mtrl_nm
		, t.model_number
		, t.serial_number
		, t.equip_dsc
		, t.photo_file_grp_cd
		, t.doc_file_grp_cd
		, t.equip_class_path
		, t.equip_class_desc
		, to_char(t.insert_ts, 'YYYY-MM-DD') as insert_ts
		, t.inserter_id
		, t.inserter_nm
		, t.update_ts
		, t.updater_id
		, t.updater_nm
		, t.factory_pk
		, t.system_cd
		, sc.code_nm as system_nm
		, t.process_cd
		, bc.code_nm as process_nm
		, cm_fn_get_incineration(l.loc_pk) as incinerator
		, STRING_AGG(esv.equip_spec_value,',') as equip_spec

		from cm_equipment t
		inner join cm_location l on t.loc_pk = l.loc_pk
		inner join dept d on t.dept_pk = d.id
		inner join cm_base_code es on t.equip_status = es.code_cd and es.code_grp_cd = 'EQUIP_STATUS'
		left outer join cm_equip_category ec on t.equip_category_id = ec.equip_category_id
		left outer join cm_import_rank ir on t.import_rank_pk = ir.import_rank_pk
		left outer join cm_cost_center cc on t.ccenter_cd = cc.ccenter_cd
		left outer join cm_supplier s on t.supplier_pk = s.supplier_pk
		left outer join cm_equipment eu on t.up_equip_pk = eu.equip_pk
		left outer join cm_base_code dt on t.disposed_type = dt.code_cd and dt.code_grp_cd = 'DISPOSE_TYPE'
		left outer join cm_supplier sm on t.maker_pk = sm.supplier_pk
		left outer join cm_material m on t.mtrl_pk = m.mtrl_pk
		left outer join cm_location ul on l.up_loc_pk = ul.loc_pk
		left outer join cm_base_code bc on bc.code_grp_cd = 'EQUIPMENT_PROCESS' and bc.code_cd = t.process_cd
		left outer join cm_base_code sc on sc.code_grp_cd = 'EQUIP_SYSTEM' and sc.code_cd = t.system_cd
		left outer join cm_equip_spec esv on t.equip_pk = esv.equip_pk

		left outer join cm_equip_part_mtrl epm on t.equip_pk = epm.equip_pk
		where t.del_yn = 'N'
		'''
		if use_yn:
			sql += '''
			AND t.use_yn = %(use_yn)s
			'''
		if keyword:
			sql += ''' 
			AND (
				UPPER(t.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

					OR ('NCA' = 'NCL' AND UPPER(l.loc_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%'))
					OR ('NCA' = 'NCA' AND UPPER(t.asset_nos) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%'))

			)
			'''
		if equip_status:
			sql += '''
			AND t.equip_status = %(equip_status)s
			'''
		if loc_pk:
			sql += '''
			AND (
				l.loc_pk = %(loc_pk)s
				OR
				l.loc_pk IN ( select loc_pk from (select * from cm_fn_get_loc_path(1)) x where %(loc_pk)s = path_info_pk)
			)
			'''
		if environ_equip_yn:
			sql += '''
			and t.environ_equip_yn = %(environ_equip_yn)s
			'''
		if equip_category_id:
			sql += '''
			and t.equip_category_id = %(equip_category_id)s
			'''
		if equip_class_path:
			sql += '''
			AND t.equip_class_path LIKE CONCAT('%%',CAST(%(equip_class_path)s as text),'%%')
			'''
		if supplier_pk:
			sql += '''
			AND t.supplier_pk = %(supplier_pk)s
			'''

		sql +=	'''
			AND t.equip_status NOT IN ('ES_DISP')
		group by t.equip_pk
		, t.equip_cd
		, t.equip_nm
		, l.loc_pk
		, l.loc_cd
		, l.loc_nm
		, t.equip_status
		, es.code_nm
		, t.import_rank_pk
		, ir.import_rank_cd
		, ec.equip_category_id
		, ec.equip_category_desc
		, t.ccenter_cd
		, cc.ccenter_nm
		, t.breakdown_dt
		, t.warranty_dt
		, t.disposed_type
		, t.disposed_type
		, dt.code_nm
		, t.disposed_date
		, t.install_dt
		, t.dept_pk
		, d."Code"
		, d."Name"
		, t.asset_nos
		, t.environ_equip_yn
		, t.up_equip_pk
		, eu.equip_nm
		, eu.equip_cd
		, t.use_yn
		, t.supplier_pk
		, s.supplier_nm
		, t.make_dt
		, t.buy_cost
		, t.maker_pk
		, sm.supplier_nm
		, t.mtrl_pk
		, m.mtrl_cd
		, m.mtrl_nm
		, t.model_number
		, t.serial_number
		, t.equip_dsc
		, t.photo_file_grp_cd
		, t.doc_file_grp_cd
		, t.equip_class_path
		, t.equip_class_desc
		, t.insert_ts
		, t.inserter_id
		, t.inserter_nm
		, t.update_ts
		, t.updater_id
		, t.updater_nm
		, l.up_loc_pk
		, ul.loc_nm
		, ul.loc_cd
		, t.factory_pk
		, t.process_cd
		, bc.code_nm
		, t.system_cd
		, sc.code_nm
		, ec.remark

		)

		SELECT sub.*, c.*
		, concat(dx.business_nm, ',', dx.team_nm, ',', dx.ban_nm) as dept_path_nm
		, dx.business_nm as business_nm
		, (select count(*) from cm_pm pm where pm.equip_pk = sub.equip_pk and pm.del_yn = 'N') as pm_count
		, (select count(distinct ecm.chk_mast_pk) from cm_equip_chk_mast ecm
				inner join cm_chk_equip ce on ecm.chk_mast_pk = ce.chk_mast_pk
				where ce.equip_pk = sub.equip_pk and ecm.del_yn = 'N') as insp_count

		, coalesce(x.wo_count, 0) as wo_count
		, coalesce(x.broken_wo_cnt, 0) as broken_wo_cnt

		FROM (
			table cte

				order by equip_cd ASC,equip_nm asc

		) sub

		left outer join (
			select wo.equip_pk
			, count(distinct case when wo.wo_status = 'WOS_CL' then wo.work_order_pk else null end) as wo_count
			, count(distinct case when wo.maint_type_cd = 'MAINT_TYPE_BM'
									 and ((date(wo.start_dt) >= ((current_date - '1 years'::interval)::date+1) AND date(wo.start_dt) <= current_date)
											OR
											(date(wo.end_dt) >= ((current_date - '1 years'::interval)::date+1) AND date(wo.end_dt) <= current_date)) then wo.work_order_pk
									else null end
					) as broken_wo_cnt
			from cm_work_order wo
			where wo.wo_status not in ('WOS_RW', 'WOS_DL')
			AND ((date(wo.start_dt) >= ((current_date - '5 years'::interval)::date+1) AND date(wo.start_dt) <= current_date)
						OR
						(date(wo.end_dt) >= ((current_date - '5 years'::interval)::date+1) AND date(wo.end_dt) <= current_date))
			group by wo.equip_pk
		) x on sub.equip_pk = x.equip_pk

		left outer join (
			with x as (
				select unnest(path_info_pk) as path_pk from cm_v_dept
			)
			select d.id as dept_pk
			, max(case when d.business_yn = 'Y' then d."Name" else '' end) as business_nm
			, max(case when d.team_yn = 'Y' then d."Name" else '' end) as team_nm
			, max(case when coalesce(d.business_yn, 'N') = 'N' and  coalesce(d.team_yn, 'N') = 'N' then d."Name" else '' end) as ban_nm
			from x
			inner join dept d on x.path_pk = d.id
			group by d.id
		) dx on sub.dept_pk = dx.dept_pk

		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0         
        '''
        
		sql += ''' 
			ORDER BY 1
			--LIMIT 5;
			'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'EquipmentService.searchEquipment', ex)
			raise ex

		return items

	def get_equipment_findAll(self, keyword,dept_pk):
		sql = ''' 
			
		with cte as (

			select t.equip_pk
			, cm_fn_get_incineration(l.loc_pk) as incinerator

			, t.equip_cd
			, t.equip_nm
			, l.loc_pk
			, l.loc_cd
			, l.loc_nm
			, l.up_loc_pk
			, ul.loc_cd as up_loc_cd
			, ul.loc_nm as up_loc_nm
			, case when ul.loc_nm is null then l.loc_nm
				   else ul.loc_nm ||  ' \ '  || l.loc_nm
			  end as up_loc_path
			, t.equip_status
			, t.equip_status as equip_status_cd
			, es.code_nm as equip_status_nm
			, ir.import_rank_cd as import_rank_nm
			, t.import_rank_pk
			, ir.import_rank_cd
			, ec.equip_category_id
			, ec.equip_category_desc
			, ec.remark as equip_category_remark
			, t.ccenter_cd
			, cc.ccenter_nm
			, t.dept_pk
			, d."Code"
			, d."Name"
			, t.up_equip_pk
			, eu.equip_nm as up_equip_nm
			, eu.equip_cd as up_equip_cd
			, t.disposed_type
			, t.disposed_type as disposed_type_cd
			, dt.code_nm as disposed_type_nm
			, t.disposed_date
			, t.breakdown_dt
			, t.warranty_dt
			, t.install_dt
			, t.asset_nos
			, t.environ_equip_yn
			, count(epm.mtrl_pk) as mtrl_cnt
			, t.use_yn
			, t.supplier_pk
			, s.supplier_nm
			, t.make_dt
			, t.buy_cost
			, t.maker_pk
			, sm.supplier_nm as maker_nm
			, t.mtrl_pk
			, m.mtrl_cd
			, m.mtrl_nm
			, t.model_number
			, t.serial_number
			, t.equip_dsc
			, t.photo_file_grp_cd
			, t.doc_file_grp_cd
			, t.equip_class_path
			, t.equip_class_desc
			, t.insert_ts
			, t.inserter_id
			, t.inserter_nm
			, t.update_ts
			, t.updater_id
			, t.updater_nm
			, t.site_id
			, t.system_cd
			, sc.code_nm as system_nm
			, t.process_cd
			, bc.code_nm as process_nm
			, cm_fn_get_incineration(l.loc_pk) as incinerator
			, STRING_AGG(esv.equip_spec_value,',') as equip_spec

			from cm_equipment t
			inner join cm_location l on t.loc_pk = l.loc_pk
			inner join dept d on t.dept_pk = d.id	
			inner join cm_base_code es on t.equip_status = es.code_cd and es.code_grp_cd = 'EQUIP_STATUS'
			left outer join cm_equip_category ec on t.equip_category_id = ec.equip_category_id
			left outer join cm_import_rank ir on t.import_rank_pk = ir.import_rank_pk
			left outer join cm_cost_center cc on t.ccenter_cd = cc.ccenter_cd
			left outer join cm_supplier s on t.supplier_pk = s.supplier_pk
			left outer join cm_equipment eu on t.up_equip_pk = eu.equip_pk
			left outer join cm_base_code dt on t.disposed_type = dt.code_cd and dt.code_grp_cd = 'DISPOSE_TYPE'
			left outer join cm_supplier sm on t.maker_pk = sm.supplier_pk
			left outer join cm_material m on t.mtrl_pk = m.mtrl_pk
			left outer join cm_location ul on l.up_loc_pk = ul.loc_pk
			left outer join cm_base_code bc on bc.code_grp_cd = 'EQUIPMENT_PROCESS' and bc.code_cd = t.process_cd
			left outer join cm_base_code sc on sc.code_grp_cd = 'EQUIP_SYSTEM' and sc.code_cd = t.system_cd
			left outer join cm_equip_spec esv on t.equip_pk = esv.equip_pk

			left outer join cm_equip_part_mtrl epm on t.equip_pk = epm.equip_pk
			where t.del_yn = 'N'
			AND t.use_yn = 'Y'
			AND t.equip_status NOT IN (
					'ES_DISP'
            )
		'''
		if keyword:
			sql += ''' 
			AND (
				UPPER(t.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

					OR ('NCA' = 'NCL' AND UPPER(l.loc_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%'))
					OR ('NCA' = 'NCA' AND UPPER(t.asset_nos) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%'))

			)
		'''

		if dept_pk:
			sql += ''' 
				AND t.dept_pk =  %(dept_pk)s
				OR
				t.dept_pk IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
			)
			'''

		sql += '''
		group by t.equip_pk
		, t.equip_cd
		, t.equip_nm
		, l.loc_pk
		, l.loc_cd
		, l.loc_nm
		, t.equip_status
		, es.code_nm
		, t.import_rank_pk
		, ir.import_rank_cd
		, ec.equip_category_id
		, ec.equip_category_desc
		, t.ccenter_cd
		, cc.ccenter_nm
		, t.breakdown_dt
		, t.warranty_dt
		, t.disposed_type
		, t.disposed_type
		, dt.code_nm
		, t.disposed_date
		, t.install_dt
		, t.dept_pk
		, d."Code"
		, d."Name"
		, t.asset_nos
		, t.environ_equip_yn
		, t.up_equip_pk
		, eu.equip_nm
		, eu.equip_cd
		, t.use_yn
		, t.supplier_pk
		, s.supplier_nm
		, t.make_dt
		, t.buy_cost
		, t.maker_pk
		, sm.supplier_nm
		, t.mtrl_pk
		, m.mtrl_cd
		, m.mtrl_nm
		, t.model_number
		, t.serial_number
		, t.equip_dsc
		, t.photo_file_grp_cd
		, t.doc_file_grp_cd
		, t.equip_class_path
		, t.equip_class_desc
		, t.insert_ts
		, t.inserter_id
		, t.inserter_nm
		, t.update_ts
		, t.updater_id
		, t.updater_nm
		, l.up_loc_pk
		, ul.loc_nm
		, ul.loc_cd
		, t.site_id
		, t.process_cd
		, bc.code_nm
		, t.system_cd
		, sc.code_nm
		, ec.remark

		)

		SELECT sub.*, c.*
		, concat(dx.business_nm, ',', dx.team_nm, ',', dx.ban_nm) as dept_path_nm
		, dx.business_nm as business_nm
		, (select count(*) from cm_pm as pm where pm.equip_pk = sub.equip_pk and pm.del_yn = 'N') as pm_count
		, (select count(distinct ecm.chk_mast_pk) from cm_equip_chk_mast ecm
				inner join cm_chk_equip ce on ecm.chk_mast_pk = ce.chk_mast_pk
				where ce.equip_pk = sub.equip_pk and ecm.del_yn = 'N') as insp_count

		, coalesce(x.wo_count, 0) as wo_count
		, coalesce(x.broken_wo_cnt, 0) as broken_wo_cnt

		FROM (
			table cte
				order by equip_cd ASC,equip_nm asc				

		) sub

		left outer join (
			select wo.equip_pk
			, count(distinct case when wo.wo_status = 'WOS_CL' then wo.work_order_pk else null end) as wo_count
			, count(distinct case when wo.maint_type_cd = 'MAINT_TYPE_BM'
									 and ((date(wo.start_dt) >= ((current_date - '1 years'::interval)::date+1) AND date(wo.start_dt) <= current_date)
											OR
											(date(wo.end_dt) >= ((current_date - '1 years'::interval)::date+1) AND date(wo.end_dt) <= current_date)) then wo.work_order_pk
									else null end
					) as broken_wo_cnt
			from cm_work_order wo
			where wo.wo_status not in ('WOS_RW', 'WOS_DL')
			AND ((date(wo.start_dt) >= ((current_date - '5 years'::interval)::date+1) AND date(wo.start_dt) <= current_date)
						OR
						(date(wo.end_dt) >= ((current_date - '5 years'::interval)::date+1) AND date(wo.end_dt) <= current_date))
			group by wo.equip_pk
		) x on sub.equip_pk = x.equip_pk

		left outer join (
			with x as (
				select unnest(path_info_pk) as path_pk from cm_v_dept
			)
			select d.id as dept_pk
			, max(case when d.business_yn = 'Y' then d."Name" else '' end) as business_nm
			, max(case when d.team_yn = 'Y' then d."Name" else '' end) as team_nm
			, max(case when coalesce(d.business_yn, 'N') = 'N' and  coalesce(d.team_yn, 'N') = 'N' then d."Name" else '' end) as ban_nm
			from x
			inner join dept d on x.path_pk = d.id
			group by d.id
		) dx on sub.dept_pk = dx.dept_pk

		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        '''
		data = {}
		try:
			data = DbUtil.get_rows(sql, {'keyword':keyword,'dept_pk':dept_pk})
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equipment_findAll', ex)
			raise ex

		return data

	def get_equipment_selectAll(self, keyword,dept_pk):
		sql = ''' 
			
		select t.equip_pk
		, t.equip_cd
		, t.equip_nm
		, t.loc_pk
		, l.loc_nm
		, t.dept_pk
		, d."Name" as dept_nm
		, es.code_nm as equip_status_nm 
		, t.import_rank_pk
		, ir.import_rank_desc as import_rank_nm
		, ec.remark as _equip_category_remark
		, t.asset_nos
		, t.environ_equip_yn
		, t.warranty_dt as _warranty_dt
		from cm_equipment t		
			inner join cm_location l on t.loc_pk = l.loc_pk		
			inner join cm_base_code es on t.equip_status = es.code_cd and es.code_grp_cd = 'EQUIP_STATUS'		
			inner join dept d on t.dept_pk = d.id
			left outer join cm_equip_category ec on t.equip_category_id = ec.equip_category_id
			left outer join cm_import_rank ir on t.import_rank_pk = ir.import_rank_pk
		where t.del_yn = 'N'
			AND t.use_yn = 'Y'
			AND t.equip_status NOT IN ('ES_DISP')
		'''
		if keyword:
			sql += ''' 
			AND (
				UPPER(t.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

					OR ('NCA' = 'NCL' AND UPPER(l.loc_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%'))
					OR ('NCA' = 'NCA' AND UPPER(t.asset_nos) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%'))

			)
		'''

		if dept_pk:
			sql += ''' 
				AND t.dept_pk =  %(dept_pk)s
				OR
				t.dept_pk IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
			
			'''

		data = {}
		try:
			data = DbUtil.get_rows(sql, {'keyword':keyword,'dept_pk':dept_pk})
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equipment_selectAll', ex)
			raise ex

		return data

	def get_equipment_findOne(self, equip_pk):
		sql = ''' 
			
		WITH cte AS (

			select t.equip_pk
			, cm_fn_get_incineration(l.loc_pk) as incinerator

			, t.equip_cd
			, t.equip_nm
			, l.loc_pk
			, l.loc_cd
			, l.loc_nm
			, l.up_loc_pk
			, ul.loc_cd as up_loc_cd
			, ul.loc_nm as up_loc_nm
			, case when ul.loc_nm is null then l.loc_nm
				   else ul.loc_nm ||  ' / '  || l.loc_nm
			  end as up_loc_path
			, t.equip_status
			, t.equip_status as equip_status_cd
			, es.code_nm as equip_status_nm
			, ir.import_rank_cd as import_rank_nm
			, t.import_rank_pk
			, ir.import_rank_cd
			, ec.equip_category_id
			, ec.equip_category_desc
			, ec.remark as equip_category_remark
			, t.ccenter_cd
			, cc.code_nm as ccenter_nm
			, t.dept_pk
			, d."Code"
			, d."Name"
			, t.up_equip_pk
			, eu.equip_nm as up_equip_nm
			, eu.equip_cd as up_equip_cd
			, t.disposed_type
			, t.disposed_type as disposed_type_cd
			, dt.code_nm as disposed_type_nm
			, t.disposed_date
			, t.breakdown_dt
			, t.warranty_dt
			, t.install_dt
			, t.asset_nos
			, t.environ_equip_yn
			, count(epm.mtrl_pk) as mtrl_cnt
			, t.use_yn
			, t.supplier_pk
			, s.supplier_nm
			, t.make_dt
			, t.buy_cost
			, t.maker_pk
			, sm.supplier_nm as maker_nm
			, t.mtrl_pk
			, m.mtrl_cd
			, m.mtrl_nm
			, t.model_number
			, t.serial_number
			, t.equip_dsc
			, t.photo_file_grp_cd
			, t.doc_file_grp_cd
			, t.equip_class_path
			, t.equip_class_desc
			, t.insert_ts
			, t.inserter_id
			, t.inserter_nm
			, t.update_ts
			, t.updater_id
			, t.updater_nm
			, t.site_id
			, t.system_cd
			, sc.code_nm as system_nm
			, t.process_cd
			, bc.code_nm as process_nm
			, cm_fn_get_incineration(l.loc_pk) as incinerator
			, STRING_AGG(esv.equip_spec_value,',') as equip_spec

			from cm_equipment t
			inner join cm_location l on t.loc_pk = l.loc_pk
			inner join dept d on t.dept_pk = d.id
			inner join cm_base_code es on t.equip_status = es.code_cd and es.code_grp_cd = 'EQUIP_STATUS'
			left outer join cm_equip_category ec on t.equip_category_id = ec.equip_category_id
			left outer join cm_import_rank ir on t.import_rank_pk = ir.import_rank_pk
			left outer join cm_base_code cc on t.ccenter_cd = cc.code_cd and cc.code_grp_cd = 'COST_CENTER'
			left outer join cm_supplier s on t.supplier_pk = s.supplier_pk
			left outer join cm_equipment eu on t.up_equip_pk = eu.equip_pk
			left outer join cm_base_code dt on t.disposed_type = dt.code_cd and dt.code_grp_cd = 'DISPOSE_TYPE'
			left outer join cm_supplier sm on t.maker_pk = sm.supplier_pk
			left outer join cm_material m on t.mtrl_pk = m.mtrl_pk
			left outer join cm_location ul on l.up_loc_pk = ul.loc_pk
			left outer join cm_base_code bc on bc.code_grp_cd = 'EQUIPMENT_PROCESS' and bc.code_cd = t.process_cd
			left outer join cm_base_code sc on sc.code_grp_cd = 'EQUIP_SYSTEM' and sc.code_cd = t.system_cd
			left outer join cm_equip_spec esv on t.equip_pk = esv.equip_pk

			left outer join cm_equip_part_mtrl epm on t.equip_pk = epm.equip_pk
			where t.del_yn = 'N'
			
				AND t.equip_pk = %(equip_pk)s

			group by t.equip_pk
			, t.equip_cd
			, t.equip_nm
			, l.loc_pk
			, l.loc_cd
			, l.loc_nm
			, t.equip_status
			, es.code_nm
			, t.import_rank_pk
			, ir.import_rank_cd
			, ec.equip_category_id
			, ec.equip_category_desc
			, t.ccenter_cd
			, cc.code_nm
			, t.breakdown_dt
			, t.warranty_dt
			, t.disposed_type
			, t.disposed_type
			, dt.code_nm
			, t.disposed_date
			, t.install_dt
			, t.dept_pk
			, d."Code"
			, d."Name"
			, t.asset_nos
			, t.environ_equip_yn
			, t.up_equip_pk
			, eu.equip_nm
			, eu.equip_cd
			, t.use_yn
			, t.supplier_pk
			, s.supplier_nm
			, t.make_dt
			, t.buy_cost
			, t.maker_pk
			, sm.supplier_nm
			, t.mtrl_pk
			, m.mtrl_cd
			, m.mtrl_nm
			, t.model_number
			, t.serial_number
			, t.equip_dsc
			, t.photo_file_grp_cd
			, t.doc_file_grp_cd
			, t.equip_class_path
			, t.equip_class_desc
			, t.insert_ts
			, t.inserter_id
			, t.inserter_nm
			, t.update_ts
			, t.updater_id
			, t.updater_nm
			, l.up_loc_pk
			, ul.loc_nm
			, ul.loc_cd
			, t.site_id
			, t.process_cd
			, bc.code_nm
			, t.system_cd
			, sc.code_nm
			, ec.remark

			)
			SELECT cte.*
			, cm_fn_get_dept_path_names(cte.dept_pk) as dept_path_nm
			, cm_fn_get_dept_business_nm(cte.dept_pk) as business_nm
			, '{"QR":"Asset","Code":"' || cte.equip_cd || '","AssetNo":"' || coalesce (cte.asset_nos,'') || '","SiteId":"' || cte.Site_Id || '"}' as qrbarcode
			FROM cte
        '''
		data = {}
		try:
			data = DbUtil.get_row(sql, {'equip_pk':equip_pk})
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equipment_findOne', ex)
			raise ex

		return data

	def getEquipPmList(self, equip_pk):
		sql = ''' 
			
		with cte as (
			SELECT p.pm_pk
				 , p.equip_pk
				 , p.pm_no 							/* pm번호 */
				 , p.pm_nm 							/* PM명 */
				 , p.dept_pk
				 , d."Name"						  	/* PM부서 */
				 , p.pm_user_pk
				 , cm_fn_user_nm(pmu."Name", pmu.del_yn) as pm_user_nm		/* PM 담당자 */
				 , p.pm_type
				 , pt.code_nm as pm_type_nm	 		/* PM유형 */
				 , p.per_number 					/* 주기 */
				 , p.cycle_type
				 , ct.code_nm as cycle_type_nm		/* 주기단위 */
			     , p.next_chk_date
			     , p.last_work_dt					/* 최근 일정생성일 */
				 , p.use_yn	 						/* 사용여부 */
			from cm_pm p
			inner join cm_equipment t on p.equip_pk = t.equip_pk
			left outer join dept d on p.dept_pk = d.id
			left outer join user_profile pmu on p.pm_user_pk = pmu."User_id"
			left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
			left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
			where t.del_yn = 'N'
    		and t.use_yn = 'Y'
 			and t.equip_pk = %(equip_pk)s
			order by p.pm_pk asc
		)
		SELECT COUNT(*) OVER() AS total_rows,
				*
		FROM (
			table cte

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        '''
		data = {}
		try:
			data = DbUtil.get_rows(sql, {'equip_pk':equip_pk})
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equipment_findOne', ex)
			raise ex

		return data

	def get_equipment_log(self, equip_pk):
		sql = ''' 
			
			SELECT INSERTER_NM, log_type, log_history, log_date
			from  (
					SELECT E.INSERTER_NM, '불용처리' as log_type, '불용처리 = ' || B.CODE_NM  AS log_history, TO_CHAR(E.INSERT_TS, 'YYYY-MM-DD HH24:MI') AS log_date
					FROM cm_equipment E
					INNER JOIN cm_base_code B ON E.DISPOSED_TYPE = B.CODE_CD AND B.CODE_GRP_CD = 'DISPOSE_TYPE'
					WHERE EQUIP_PK = %(equip_pk)s
					UNION ALL
					SELECT INSERTER_NM, '정보' as log_type, '설비정보 생성' AS log_history, TO_CHAR(INSERT_TS ,'YYYY-MM-DD HH24:MI') AS log_date
					FROM cm_equipment
					WHERE EQUIP_PK = %(equip_pk)s
					UNION ALL
					SELECT UPDATER_NM, '정보' as log_type, '설비정보 수정' AS log_history, TO_CHAR(UPDATE_TS, 'YYYY-MM-DD HH24:MI') AS log_date
					FROM cm_equipment
					WHERE EQUIP_PK = %(equip_pk)s
					AND UPDATE_TS IS NOT NULL
					UNION ALL
					SELECT INSERTER_NM, log_type, log_history, log_date
					FROM (
						SELECT INSERTER_NM, '관리부서' as log_type, '설비부서 변경 : ' || EQUIP_DEPT_BEF || ' to ' || EQUIP_DEPT_AFT AS log_history, TO_CHAR(INSERT_TS, 'YYYY-MM-DD HH24:MI') AS log_date
						FROM cm_equip_dept_hist
						WHERE EQUIP_PK = %(equip_pk)s
						ORDER BY INSERT_TS DESC
					) AS EQUIP_DEPT_HIST
					UNION ALL
					SELECT INSERTER_NM, log_type, log_history, log_date
					FROM (
						SELECT INSERTER_NM, '설비위치' as log_type, '설비위치 변경 : ' || EQUIP_LOC_BEF || ' to ' || EQUIP_LOC_AFT AS log_history, TO_CHAR(INSERT_TS ,'YYYY-MM-DD HH24:MI') AS log_date
						FROM cm_equip_loc_hist
						WHERE EQUIP_PK = %(equip_pk)s
						ORDER BY INSERT_TS DESC
					) AS EQUIP_LOC_HIST
			) total
			ORDER BY log_date DESC
        '''
		data = {}
		try:
			data = DbUtil.get_rows(sql, {'equip_pk':equip_pk})
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equipment_log', ex)
			raise ex

		return data

	# 설비 위치 변경이력 조회
	def get_equip_loc_hist(self, equip_pk):
		items = []
		sql = '''
			SELECT equip_pk
				, equip_loc_hist_pk
				, equip_loc_bef
				, equip_loc_aft
				, TO_CHAR(INSERT_TS, 'YYYY-MM-DD HH24:MI') AS insert_ts
				, inserter_nm 
			FROM cm_equip_loc_hist
			WHERE equip_pk = %(equip_pk)s
		'''

		try:
			items = DbUtil.get_rows(sql, {'equip_pk':equip_pk})
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equip_loc_hist', ex)
			raise ex

		return items

	# 설비 관리부서 변경이력 조회
	def get_equip_dept_hist(self, equip_pk):
		items = []
		sql = '''
			SELECT equip_pk
				, equip_dept_hist_pk
				, equip_dept_bef
				, equip_dept_aft
				, TO_CHAR(INSERT_TS, 'YYYY-MM-DD HH24:MI') AS insert_ts
				, inserter_nm 
			FROM cm_equip_dept_hist
			WHERE equip_pk = %(equip_pk)s
		'''
		
		try:
			items = DbUtil.get_rows(sql, {'equip_pk':equip_pk})
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equip_dept_hist', ex)
			raise ex

		return items
		
	# kmms - 설비정보 - 불용설비 조회
	def get_equipment_disposed(self, keyword, srchCat, srch_dept, start_date, end_date):
		items = []
		dic_param = {'keyword':keyword, 'srchCat':srchCat, 'srch_dept':srch_dept, 'start_date':start_date, 'end_date':end_date}

		sql = '''
			SELECT e.equip_pk, e.equip_cd , e.equip_nm , e.loc_pk , l.loc_nm ,
			equip_status , 
			bc.code_nm as equip_status_nm, bc2.code_nm as diposed_type_nm,
			disposed_type ,disposed_date 
			FROM cm_equipment e
				left join cm_location l on e.loc_pk = l.loc_pk 
				left join cm_base_code bc on e.equip_status = bc.code_cd and bc.code_grp_cd = 'EQUIP_STATUS'
				left join cm_base_code bc2 on e.disposed_type = bc2.code_cd and bc2.code_grp_cd = 'DISPOSE_TYPE'
			WHERE disposed_type is not null
			and e.disposed_date between %(start_date)s and %(end_date)s
		'''		

		if keyword:
			sql += ''' 
            AND (e."equip_nm" LIKE CONCAT('%%', %(keyword)s, '%%')
				or e."equip_cd"  LIKE CONCAT('%%', %(keyword)s, '%%'))
			'''

		if srchCat : 
			sql += ''' 
            AND e."equip_category_id" = %(srchCat)s
            '''

		if srch_dept:
			sql += ''' 
            AND e."dept_pk" = %(srch_dept)s
            '''


		try:
			items = DbUtil.get_rows(sql, dic_param)
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equipment_disposed', ex)
			raise ex

		return items

	# kmms - 설비정보 - 설비별작업이력 조회
	def get_equipment_workhistory(self, keyword, manage_dept, loc_pk, start_dt, end_dt, maint_type_cd, equip_category_id, equip_class_path, work_dept, srch_environ_equip_only,):
		items = []
		dic_param = {'keyword':keyword, 'manage_dept':manage_dept, 'loc_pk':loc_pk, 'start_dt':start_dt, 'end_dt':end_dt, 'maint_type_cd':maint_type_cd, 'equip_category_id':equip_category_id, 'equip_class_path':equip_class_path, 'work_dept':work_dept, 'srch_environ_equip_only':srch_environ_equip_only,}

		sql = '''
		with cte as (
		
		select t.work_order_pk
				, t.work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
				, t.work_charger_pk
				, cm_fn_user_nm(wcu."Name", wcu.del_yn) as work_charger_nm
				, mt.code_cd as maint_type_cd
				, mt.code_nm as maint_type_nm
				, ws.code_cd as wo_status_cd
				, ws.code_nm as wo_status_nm
				, t.plan_start_dt
				, t.plan_end_dt
				, t.start_dt
				, t.end_dt
				, t.want_dt
				, t.equip_pk
				, e.equip_cd
				, e.equip_nm
				, ed.id as equip_dept_pk
				, ed."Name" as equip_dept_nm
				, to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
				, t.pm_pk
				, p.pm_no
				, p.pm_nm
				, pt.code_nm                        AS pm_type_nm
				, p.work_text as pm_work_text
				, t.chk_rslt_pk
				, ecs.chk_sche_pk
				, ecs.chk_sche_no
				, ecm.chk_mast_nm
				, ecm.chk_mast_pk
				, ecs.chk_sche_dt
				, l.loc_nm
				, t.req_info
				, t.wo_type
				, t.rqst_insp_yn
				, t.rqst_dpr_yn
				, wt.code_nm as wo_type_nm
				, t.breakdown_dt
				, t.breakdown_min
				, wsc.code_cd as work_src_cd
				, wsc.code_nm as work_src_nm
				, t.tot_cost
				, t.mtrl_cost
				, t.labor_cost
				, t.outside_cost
				, t.etc_cost
				, t.problem_cd
				, wp.reliab_nm as problem_nm
				, t.cause_cd
				, wc.reliab_nm as cause_nm
				, t.remedy_cd
				, wr.reliab_nm as remedy_nm
				, prj.proj_cd
				, prj.proj_nm
				, t.wo_file_grp_cd
				, t.req_info_img_grp_cd
				, t.work_text_img_grp_cd
				, t.pm_req_type
				, t.req_dept_busi_cd
				, t.appr_line
				, t.appr_line_next
				, t.work_order_approval_pk
				, woa.reg_dt
				, woa.rqst_dt
				, woa.rqst_user_nm
				, woarqstd.id as rqst_dept_pk
				, woarqstd."Name" as rqst_dept_nm
				, woa.cancel_dt
				, woa.cancel_user_nm
				, woa.accept_dt
				, woa.appr_dt
				, woa.finish_dt
				, substring(t.appr_line, 1,2) as wo_start_type
				, cm_fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
				, t.insert_ts
				, e.environ_equip_yn
				, e.equip_status as equip_stauts_cd
				, e.import_rank_pk
				, ir.import_rank_cd
				, e.up_equip_pk
				, ue.equip_nm AS up_equip_name
				, ec.equip_category_id
				, ec.equip_category_desc
        		, ec.remark
				, e.equip_class_path
				, e.equip_class_desc
				, av.code_nm as first_asset_status
				, av.code_cd as first_asset_status_cd
				, cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
				, (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
				, (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm
				, l.loc_nm
				, es.ex_supplier_nm
				, woa.cancel_reason
				, t.cost_type
				, (select code_nm from cm_base_code where code_cd = t.cost_type and code_grp_cd = 'WO_COST_TYPE') as cost_type_nm

		from cm_work_order t
			inner join cm_work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
			inner join cm_base_code mt on t.maint_type_cd = mt.code_cd and mt.code_grp_cd = 'MAINT_TYPE'
			inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS'
			inner join cm_equipment e on t.equip_pk = e.equip_pk
			inner join cm_location l on e.loc_pk = l.loc_pk
			left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
			left outer join dept ed on e.dept_pk  = ed.id
			left outer join dept wd on t.dept_pk = wd.id
			left outer join dept rd on t.req_dept_pk = rd.id
			left outer join user_profile wcu on t.work_charger_pk = wcu."User_id"
			left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC'
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
			left outer join cm_pm p on t.pm_pk = p.pm_pk
			left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
			left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
			left outer join user_profile pmu on p.pm_user_pk = pmu."User_id"
			left outer join user_profile wou on t.WORK_CHARGER_PK = wou."User_id"
			left outer join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
			left outer join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
			left outer join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
			left outer join cm_base_code wsc on t.work_src_cd = wsc.code_cd and wsc.code_grp_cd = 'WORK_SRC'
			left outer join cm_project prj on t.proj_cd = prj.proj_cd
			left outer join user_profile woarqstu on woa.rqst_user_pk = woarqstu."User_id"
			left outer join dept woarqstd on woarqstu."Depart_id" = woarqstd.id
			left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''

		if keyword:
			sql += '''
			AND (
				UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
			)
			'''
		if manage_dept:
			sql += '''
			AND (
				ed.id = %(manage_dept)s
				OR
				ed.id IN ( select dept_pk from cm_v_dept_path where %(manage_dept)s = path_info_pk)
			)
			'''
		if loc_pk:
			sql += '''
			AND (
				l.loc_pk = %(loc_pk)s
				OR
				l.loc_pk IN ( select loc_pk from (select * from cm_fn_get_loc_path('1')) x where %(loc_pk)s = path_info_pk)
			)
			'''
		if start_dt and end_dt:
			sql += '''
				AND (
					(date(t.start_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.start_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
					OR
					(date(t.end_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.end_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
				)
			'''
		if maint_type_cd:
			sql += '''
    		AND mt.code_cd = %(maint_type_cd)s
			'''
		if equip_category_id:
			sql += '''
			AND ec.equip_category_id = %(equip_category_id)s
			'''
		if equip_class_path:
			sql += '''
			AND e.equip_class_path LIKE CONCAT('%%',CAST(%(equip_class_path)s as text),'%%')
			'''
		if work_dept:
			sql += '''
			AND (
				wd.id = %(work_dept)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(work_dept)s = path_info_pk)
			)
			'''
		if srch_environ_equip_only == 'Y':
			sql += '''
    		AND e.environ_equip_yn = 'Y'
			'''

		sql += '''
			AND ws.code_cd <> 'WOS_DL'
		)
		SELECT *
		FROM (
			table cte

	            limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		order by pm_no desc, work_order_no desc

		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equipment_workhistory', ex)
			raise ex

		return items

	def equip_check_disposed(self, equipPk):
		items = []
		dic_param = {'equipPk':equipPk}

		sql = '''
			/* findAll [equip-check-mast-mapper.xml] */
			with cte as (
				select t.chk_mast_pk
					, t.chk_mast_nm
					, t.chk_mast_no
					, d.id
					, d."Name"
					, t.chk_user_pk
					, cm_fn_user_nm(cu."Name", cu.del_yn) as chk_user_nm
					, (case when (t.chk_mast_no ~ E'^[0-9]+$') = true then cast(t.chk_mast_no as integer) else 999999 end) as chk_mast_no_sort
					, t.last_chk_date
					, t.first_chk_date
					, t.sched_start_date
        			, t.next_chk_date
					, t.cycle_type as cycle_type_cd
					, ct.code_nm   as cycle_type_nm
					, concat(t.per_number, ct.code_dsc) as cycle_display_nm
					, t.per_number
					, t.work_text
					, COUNT(DISTINCT eci.chk_item_pk) as equip_chk_item_cnt
					, COUNT(DISTINCT e.equip_pk) as chk_equip_item_cnt
					, t.use_yn
					, t.del_yn
					, t.insert_ts
					, t.inserter_id
					, t.inserter_nm
					, t.update_ts
					, t.updater_id
					, t.updater_nm
					, t.daily_report_cd
					, t.daily_report_type_cd

			FROM   cm_equip_chk_mast t
				INNER JOIN dept d ON t.dept_pk = d.id
				INNER JOIN cm_chk_equip ce on t.chk_mast_pk = ce.chk_mast_pk
				INNER JOIN cm_equipment e on ce.equip_pk = e.equip_pk
				LEFT OUTER JOIN user_profile cu on t.chk_user_pk = cu."User_id"
				LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
				LEFT OUTER JOIN cm_equip_chk_item eci on t.chk_mast_pk = eci.chk_mast_pk
				LEFT OUTER JOIN cm_location l on e.loc_pk = l.loc_pk
				LEFT OUTER JOIN dept ed on e.dept_pk = ed.id
			WHERE  t.del_yn = 'N'
				AND t.use_yn = 'Y'
				AND e.equip_pk = %(equipPk)s

			GROUP BY t.chk_mast_pk
				, t.chk_mast_nm
				, t.chk_mast_no
				, d.id
				, d."Name"
				, t.chk_user_pk
				, cu."Name"
				, cu.del_yn
				, t.last_chk_date
				, t.first_chk_date
				, t.sched_start_date
				, t.next_chk_date
				, t.cycle_type
				, ct.code_cd
				, ct.code_nm
				, ct.code_dsc
				, t.per_number
				, t.work_text
				, t.use_yn
				, t.del_yn
				, t.insert_ts
				, t.inserter_id
				, t.inserter_nm
				, t.update_ts
				, t.updater_id
				, t.updater_nm
				, t.daily_report_cd
				, t.daily_report_type_cd

			)
			SELECT chk_mast_pk
					, chk_mast_nm
					, chk_mast_no
					, id
					, "Name"
					, chk_user_pk
					, chk_user_nm
					, chk_mast_no_sort
					, last_chk_date
					, first_chk_date
					, sched_start_date
					, cycle_type_cd
					, cycle_type_nm
					, cycle_display_nm
					, per_number
					, work_text
					, equip_chk_item_cnt
					, chk_equip_item_cnt
					, use_yn
					, del_yn
					, insert_ts
					, inserter_id
					, inserter_nm
					, update_ts
					, updater_id
					, updater_nm
					, daily_report_cd
					, daily_report_type_cd

					, coalesce(sub.next_chk_date
        				, cast(cm_fn_get_work_day(to_char(cm_fn_get_last_insp_date(sub.chk_mast_pk), 'YYYY-MM-DD')) as timestamp)) as next_chk_date

        			, total_rows
			FROM (
				table cte
			) sub
			RIGHT JOIN (select count(*) from cte) c(total_rows) on true
			WHERE total_rows != 0
			order by cast(chk_mast_no as INTEGER)
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
			items = CommonUtil.res_snake_to_camel(items)
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.equip_check_disposed', ex)
			raise ex

		return items

	def equip_chk_sche_disposed(self, equipPk):
		items = []
		dic_param = {'equipPk':equipPk}

		sql = '''
			/* findAll [equip-chk-sche-mapper.xml] */
				
	/* findAll [equip-chk-sche-mapper.xml] */

	with cte as (

	select t.chk_mast_pk
		, ecm.chk_mast_no
		, ecm.chk_mast_nm
		, t.chk_sche_pk
		, t.chk_sche_no
		, t.chk_sche_dt
		, cs.code_cd as chk_status_cd
		, cs.code_nm as chk_status_nm
		, d.id
		, d."Name"
		, ecm.last_chk_date
		, ct.code_cd as cycle_type_cd
		, ct.code_nm as cycle_type_nm
		, concat(ecm.per_number, ct.code_dsc) as cycle_display_nm
		, ecm.per_number
		, t.chk_user_pk
		, cm_fn_user_nm(cu."Name", cu.del_yn) as chk_user_nm
		, t.chk_dt
        , 1 as site_id
		, t.insert_ts
		, t.inserter_id
		, t.inserter_nm
		, t.update_ts
		, t.updater_id
		, t.updater_nm
		, ecm.daily_report_cd
		, ecm.daily_report_type_cd
		, count(distinct case when ecr.chk_rslt='A' then e.equip_pk else null end) as fail_count

	from cm_equip_chk_sche t
		inner join cm_equip_chk_mast ecm on t.chk_mast_pk = ecm.chk_mast_pk
		left outer join cm_base_code ct on ecm.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
		left outer join dept d on t.dept_pk = d.id
		inner join cm_base_code cs on t.chk_status = cs.code_cd and cs.code_grp_cd = 'CHK_STATUS'
		inner join cm_equip_chk_rslt ecr ON t.chk_sche_pk = ecr.chk_sche_pk
		inner join cm_equipment e on ecr.equip_pk = e.equip_pk
		left outer join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
		inner join cm_location l on e.loc_pk = l.loc_pk
		left outer join dept ed on e.dept_pk = ed.id
		left outer join user_profile cu on t.chk_user_pk = cu."User_id"
	where 1 = 1
		AND e.equip_pk = %(equipPk)s
		AND cs.code_cd = 'CHK_STATUS_N'
		AND t.chk_dt IS NULL

	group by t.chk_mast_pk
		, ecm.chk_mast_no
		, ecm.chk_mast_nm
		, t.chk_sche_pk
		, t.chk_sche_no
		, t.chk_sche_dt
		, cs.code_cd
		, cs.code_nm
		, d.id
		, d."Name"
		, ecm.last_chk_date
		, ct.code_cd
		, ct.code_nm
		, ct.code_dsc
		, ecm.per_number
		, t.chk_user_pk
		, cu."Name"
		, cu.del_yn
		, t.chk_dt    
		, t.insert_ts
		, t.inserter_id
		, t.inserter_nm
		, t.update_ts
		, t.updater_id
		, t.updater_nm
		, ecm.daily_report_cd
		, ecm.daily_report_type_cd

	)
	SELECT *
	FROM (
		table cte

	) sub
	RIGHT JOIN (select count(*) from cte) c(total_rows) on true
	WHERE total_rows != 0

		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
			items = CommonUtil.res_snake_to_camel(items)
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.equip_chk_sche_disposed', ex)
			raise ex

		return items

	def equip_child_disposed(self, equipPk):
		items = []
		dic_param = {'equipPk':equipPk}

		sql = '''
			
		/* findAll [equipment-mapper.xml] */

			with cte as (

			select t.equip_pk
			, cm_fn_get_incineration(l.loc_pk) as incinerator

			, t.equip_cd
			, t.equip_nm
			, l.loc_pk
			, l.loc_cd
			, l.loc_nm
			, l.up_loc_pk
			, ul.loc_cd as up_loc_cd
			, ul.loc_nm as up_loc_nm
			, case when ul.loc_nm is null then l.loc_nm
				   else ul.loc_nm ||  ' \ '  || l.loc_nm
			  end as up_loc_path
			, t.equip_status
			, t.equip_status as equip_status_cd
			, es.code_nm as equip_status_nm
			, ir.import_rank_cd as import_rank_nm
			, t.import_rank_pk
			, ir.import_rank_cd
			, ec.equip_category_id
			, ec.equip_category_desc
			, ec.remark as equip_category_remark
			, t.ccenter_cd
			, cc.ccenter_nm
			, t.dept_pk
			, d."Code"
			, d."Name"
			, t.up_equip_pk
			, eu.equip_nm as up_equip_nm
			, eu.equip_cd as up_equip_cd
			, t.disposed_type
			, t.disposed_type as disposed_type_cd
			, dt.code_nm as disposed_type_nm
			, t.disposed_date
			, t.breakdown_dt
			, t.warranty_dt
			, t.install_dt
			, t.asset_nos
			, t.environ_equip_yn
			, count(epm.mtrl_pk) as mtrl_cnt
			, t.use_yn
			, t.supplier_pk
			, s.supplier_nm
			, t.make_dt
			, t.buy_cost
			, t.maker_pk
			, sm.supplier_nm as maker_nm
			, t.mtrl_pk
			, m.mtrl_cd
			, m.mtrl_nm
			, t.model_number
			, t.serial_number
			, t.equip_dsc
			, t.photo_file_grp_cd
			, t.doc_file_grp_cd
			, t.equip_class_path
			, t.equip_class_desc
			, t.insert_ts
			, t.inserter_id
			, t.inserter_nm
			, t.update_ts
			, t.updater_id
			, t.updater_nm
			, t.site_id
			, t.system_cd
			, sc.code_nm as system_nm
			, t.process_cd
			, bc.code_nm as process_nm
			, cm_fn_get_incineration(l.loc_pk) as incinerator
			, STRING_AGG(esv.equip_spec_value,',') as equip_spec

			from cm_equipment t
			inner join cm_location l on t.loc_pk = l.loc_pk
			inner join dept d on t.dept_pk = d.id
			inner join cm_base_code es on t.equip_status = es.code_cd and es.code_grp_cd = 'EQUIP_STATUS'
			left outer join cm_equip_category ec on t.equip_category_id = ec.equip_category_id
			left outer join cm_import_rank ir on t.import_rank_pk = ir.import_rank_pk
			left outer join cm_cost_center cc on t.ccenter_cd = cc.ccenter_cd
			left outer join cm_supplier s on t.supplier_pk = s.supplier_pk
			left outer join cm_equipment eu on t.up_equip_pk = eu.equip_pk
			left outer join cm_base_code dt on t.disposed_type = dt.code_cd and dt.code_grp_cd = 'DISPOSE_TYPE'
			left outer join cm_supplier sm on t.maker_pk = sm.supplier_pk
			left outer join cm_material m on t.mtrl_pk = m.mtrl_pk
			left outer join cm_location ul on l.up_loc_pk = ul.loc_pk
			left outer join cm_base_code bc on bc.code_grp_cd = 'EQUIPMENT_PROCESS' and bc.code_cd = t.process_cd
			left outer join cm_base_code sc on sc.code_grp_cd = 'EQUIP_SYSTEM' and sc.code_cd = t.system_cd
			left outer join cm_equip_spec esv on t.equip_pk = esv.equip_pk
			left outer join cm_equip_part_mtrl epm on t.equip_pk = epm.equip_pk
			where t.del_yn = 'N'
				AND t.up_equip_pk = %(equipPk)s
			group by t.equip_pk
			, t.equip_cd
			, t.equip_nm
			, l.loc_pk
			, l.loc_cd
			, l.loc_nm
			, t.equip_status
			, es.code_nm
			, t.import_rank_pk
			, ir.import_rank_cd
			, ec.equip_category_id
			, ec.equip_category_desc
			, t.ccenter_cd
			, cc.ccenter_nm
			, t.breakdown_dt
			, t.warranty_dt
			, t.disposed_type
			, t.disposed_type
			, dt.code_nm
			, t.disposed_date
			, t.install_dt
			, t.dept_pk
			, d."Code"
			, d."Name"
			, t.asset_nos
			, t.environ_equip_yn
			, t.up_equip_pk
			, eu.equip_nm
			, eu.equip_cd
			, t.use_yn
			, t.supplier_pk
			, s.supplier_nm
			, t.make_dt
			, t.buy_cost
			, t.maker_pk
			, sm.supplier_nm
			, t.mtrl_pk
			, m.mtrl_cd
			, m.mtrl_nm
			, t.model_number
			, t.serial_number
			, t.equip_dsc
			, t.photo_file_grp_cd
			, t.doc_file_grp_cd
			, t.equip_class_path
			, t.equip_class_desc
			, t.insert_ts
			, t.inserter_id
			, t.inserter_nm
			, t.update_ts
			, t.updater_id
			, t.updater_nm
			, l.up_loc_pk
			, ul.loc_nm
			, ul.loc_cd
			, t.site_id
			, t.process_cd
			, bc.code_nm
			, t.system_cd
			, sc.code_nm
			, ec.remark

			)

			SELECT sub.*, c.*
			, concat(dx.business_nm, ',', dx.team_nm, ',', dx.ban_nm) as dept_path_nm
			, dx.business_nm as business_nm
			, (select count(*) from cm_pm as pm where pm.equip_pk = sub.equip_pk and pm.del_yn = 'N') as pm_count
			, (select count(distinct ecm.chk_mast_pk) from cm_equip_chk_mast ecm
					inner join cm_chk_equip ce on ecm.chk_mast_pk = ce.chk_mast_pk
					where ce.equip_pk = sub.equip_pk and ecm.del_yn = 'N') as insp_count

			, coalesce(x.wo_count, 0) as wo_count
			, coalesce(x.broken_wo_cnt, 0) as broken_wo_cnt

			FROM (
				table cte

			) sub

			left outer join (
				select wo.equip_pk
				, count(distinct case when wo.wo_status = 'WOS_CL' then wo.work_order_pk else null end) as wo_count
				, count(distinct case when wo.maint_type_cd = 'MAINT_TYPE_BM'
										 and ((date(wo.start_dt) >= ((current_date - '1 years'::interval)::date+1) AND date(wo.start_dt) <= current_date)
												OR
												(date(wo.end_dt) >= ((current_date - '1 years'::interval)::date+1) AND date(wo.end_dt) <= current_date)) then wo.work_order_pk
										else null end
						) as broken_wo_cnt
				from cm_work_order wo
				where wo.wo_status not in ('WOS_RW', 'WOS_DL')
				AND ((date(wo.start_dt) >= ((current_date - '5 years'::interval)::date+1) AND date(wo.start_dt) <= current_date)
							OR
							(date(wo.end_dt) >= ((current_date - '5 years'::interval)::date+1) AND date(wo.end_dt) <= current_date))
				group by wo.equip_pk
			) x on sub.equip_pk = x.equip_pk

			left outer join (
				with x as (
					select unnest(path_info_pk) as path_pk from cm_v_dept
				)
				select d.id as dept_pk
				, max(case when d.business_yn = 'Y' then d."Name" else '' end) as business_nm
				, max(case when d.team_yn = 'Y' then d."Name" else '' end) as team_nm
				, max(case when coalesce(d.business_yn, 'N') = 'N' and  coalesce(d.team_yn, 'N') = 'N' then d."Name" else '' end) as ban_nm
				from x
				inner join dept d on x.path_pk = d.id
				group by d.id
			) dx on sub.dept_pk = dx.dept_pk

			RIGHT JOIN (select count(*) from cte) c(total_rows) on true
			WHERE total_rows != 0

		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)	
			items = CommonUtil.res_snake_to_camel(items)
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.equip_chk_sche_disposed', ex)
			raise ex

		return items

	def pm_equip_disposed(self, equipPk):
		items = []
		dic_param = {'equipPk':equipPk}

		sql = '''
        	/* findAll [pm-mapper.xml] */
	        with cte as (
            SELECT t.pm_pk
                   , t.pm_no
                   , t.pm_nm
                   , e.equip_pk
                   , e.equip_cd
                   , e.equip_nm
                   , e.import_rank_pk
		           , ir.import_rank_cd 				   AS import_rank_nm
                   , d.id
                   , d."Name"
                   , pu."User_id"                        AS pm_user_pk
                   , cm_fn_user_nm(pu."Name", pu.del_yn)                        AS pm_user_nm
                   , (case when (t.pm_no ~ E'^[0-9]+$') = true then cast(t.pm_no as integer) else 999999 end) as pm_no_sort
                   , pt.code_cd                        AS pm_type_cd
                   , pt.code_nm                        AS pm_type_nm
                   , ct.code_cd                        AS cycle_type_cd
                   , ct.code_nm                        AS cycle_type_nm
                   , Concat(t.per_number, ct.code_dsc) AS cycle_display_nm
                   , t.per_number
                   , t.last_work_dt
                   , t.sched_start_dt
                   , t.first_work_dt
                   , t.next_chk_date
                   , t.work_text
                   , t.work_expect_hr
                   , t.use_yn
                   , t.del_yn
                   , t.insert_ts
                   , t.inserter_id
                   , t.inserter_nm
                   , t.update_ts
                   , t.updater_id
                   , t.updater_nm
	               , eqd."Name" as mdept_nm
		           , l.loc_nm
	               , ec.equip_category_desc
			        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
			        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm

	        FROM   cm_pm t
	               INNER JOIN cm_equipment e ON t.equip_pk = e.equip_pk
	               INNER JOIN cm_location l ON e.loc_pk = l.loc_pk
	               LEFT OUTER JOIN dept d ON t.dept_pk = d.id
	               LEFT OUTER JOIN cm_base_code pt ON t.pm_type = pt.code_cd AND pt.code_grp_cd = 'PM_TYPE'
	               LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
	               LEFT OUTER JOIN user_profile pu ON t.pm_user_pk = pu."User_id"
	               LEFT OUTER JOIN dept eqd ON e.dept_pk = eqd.id
		           LEFT OUTER JOIN cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
			        left outer join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
	        WHERE  t.del_yn = 'N'
		        AND t.use_yn = 'Y'
		        AND e.equip_pk = %(equipPk)s
	        )
            SELECT *
                , CAST(cm_fn_get_work_day(to_char(cm_fn_get_last_pm_date(sub.pm_pk), 'YYYY-MM-DD')) AS timestamp) as next_chk_date

                , (select count(*)
                     from cm_work_order wo
			        where wo.pm_pk = sub.pm_pk
		           ) as wo_count

	        FROM (
		        table cte order by pm_no ASC 
	        ) sub
	        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
	        WHERE total_rows != 0
		
        '''

		try:
			items = DbUtil.get_rows(sql, dic_param)	
			items = CommonUtil.res_snake_to_camel(items)
    
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.equip_chk_sche_disposed', ex)
			raise ex

		return items

