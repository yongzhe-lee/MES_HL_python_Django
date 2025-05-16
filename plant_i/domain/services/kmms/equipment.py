from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class EquipmentService():
	def __init__(self):
		return

	def searchEquipment(self, equipment):
		items = []
		dic_param = {'equipment': equipment}

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
		, d.dept_cd
		, d.dept_nm
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
		, t.factory_pk
		, t.system_cd
		, sc.code_nm as system_nm
		, t.process_cd
		, bc.code_nm as process_nm
		, cm_fn_get_incineration(l.loc_pk) as incinerator
		, STRING_AGG(esv.equip_spec_value,',') as equip_spec

		from cm_equipment t
		inner join cm_location l on t.loc_pk = l.loc_pk
		inner join cm_dept d on t.dept_pk = d.dept_pk
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
		, d.dept_cd
		, d.dept_nm
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
				limit 100 offset (1-1)*100

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
			select d.dept_pk
			, max(case when d.business_yn = 'Y' then d.dept_nm else '' end) as business_nm
			, max(case when d.team_yn = 'Y' then d.dept_nm else '' end) as team_nm
			, max(case when coalesce(d.business_yn, 'N') = 'N' and  coalesce(d.team_yn, 'N') = 'N' then d.dept_nm else '' end) as ban_nm
			from x
			inner join cm_dept d on x.path_pk = d.dept_pk
			group by d.dept_pk
		) dx on sub.dept_pk = dx.dept_pk

		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0         
        '''
		if equipment:
			sql += ''' 
			AND a."pm_nm" like CONCAT('%%', %(equipment)s, '%%')
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
			, d.dept_cd
			, d.dept_nm
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
			inner join cm_dept d on t.dept_pk = d.dept_pk
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
		, d.dept_cd
		, d.dept_nm
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
			select d.dept_pk
			, max(case when d.business_yn = 'Y' then d.dept_nm else '' end) as business_nm
			, max(case when d.team_yn = 'Y' then d.dept_nm else '' end) as team_nm
			, max(case when coalesce(d.business_yn, 'N') = 'N' and  coalesce(d.team_yn, 'N') = 'N' then d.dept_nm else '' end) as ban_nm
			from x
			inner join cm_dept d on x.path_pk = d.dept_pk
			group by d.dept_pk
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
		, es.code_nm as equip_status_nm 
		, t.import_rank_pk
		, ir.import_rank_desc as import_rank_nm
		, ec.remark as _equip_category_remark
		, t.asset_nos as _asset_nos
		, t.environ_equip_yn
		from cm_equipment t		
		inner join cm_location l on t.loc_pk = l.loc_pk		
		inner join cm_base_code es on t.equip_status = es.code_cd and es.code_grp_cd = 'EQUIP_STATUS'		
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
			, cc.code_nm as ccenter_nm
			, t.dept_pk
			, d.dept_cd
			, d.dept_nm
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
			inner join cm_dept d on t.dept_pk = d.dept_pk
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
			, d.dept_cd
			, d.dept_nm
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
				 , d.dept_nm					  	/* PM부서 */
				 , p.pm_user_pk
				 , cm_fn_user_nm(pmu.user_nm, pmu.del_yn) as pm_user_nm		/* PM 담당자 */
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
			left outer join cm_dept d on p.dept_pk = d.dept_pk
			left outer join cm_user_info pmu on p.pm_user_pk = pmu.user_pk
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