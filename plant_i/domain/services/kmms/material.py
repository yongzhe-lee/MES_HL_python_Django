from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class MaterialService():
	def __init__(self):
		return

	def searchMaterial(self, keyword, useYn, matClassPk, supplierNm, makerNm, matDsc):
		items = []
		dic_param = {'keyword': keyword, 'useYn': useYn, 'matClassPk': matClassPk, 'supplierNm': supplierNm, 'makerNm': makerNm, 'matDsc': matDsc}

		sql = ''' 
				/* findAll [material-mapper.xml] */
				with base as (

					select  t.mtrl_pk
							, t.mtrl_cd
							, t.mtrl_barcode
							, t.mtrl_nm
							, t.mtrl_class_cd_pk as mtrl_class_pk
							, mc.code_nm as mtrl_class_nm
							, t.amt_unit_pk
							, au.code_cd as amt_unit_cd
							, au.code_nm as amt_unit_nm
							, t.mtrl_dsc
							, t.maker_pk
							, mkr.supplier_nm as maker_nm
							, t.safety_stock_amt
							, t.unit_price
							, t.unit_price_dt
							, t.supplier_pk
							, spr.supplier_nm
							, t.delivery_days
							, dt.code_cd as delivery_type_cd
							, dt.code_nm as delivery_type_nm
							, t.photo_file_grp_cd
							, t.attach_file_grp_cd
							, t.erp_mtrl_cd
							, t.allow_add_bom
							, t.use_yn
							, t.del_yn
							, t.insert_ts
							, t.inserter_id
							, t.inserter_nm
							, t.update_ts
							, t.updater_id
							, t.updater_nm
							, t.site_id
							, t.construction_pk
							, cpk.supplier_nm as construction_nm
							, t.equipment_pk
							, epk.supplier_nm as equipment_nm
					from cm_material t
					inner join cm_base_code mc on t.mtrl_class_cd_pk = mc.code_pk and mc.code_grp_cd = 'MTRL_CLASS'
					left outer join cm_equipment e on t.mtrl_pk = e.mtrl_pk
					left outer join cm_base_code au on t.amt_unit_pk = au.code_pk and au.code_grp_cd = 'AMT_UNIT'
					left outer join cm_base_code dt on t.delivery_type = dt.code_cd and dt.code_grp_cd = 'PERIOD_TYPE'
					left outer join cm_supplier mkr on t.maker_pk = mkr.supplier_pk
					left outer join cm_supplier spr on t.supplier_pk = spr.supplier_pk
					left outer join cm_supplier cpk on t.construction_pk = cpk.supplier_pk
					left outer join cm_supplier epk on t.equipment_pk = epk.supplier_pk
					left outer join cm_mtrl_substitute ms on t.mtrl_pk = ms.mtrl_pk
					left outer join cm_material msm on ms.mtrl_substitute_pk = msm.mtrl_pk
					where t.del_yn = 'N'
					'''
		if keyword:
			sql += ''' 
						AND (UPPER(t.mtrl_nm) similar to CONCAT('%%', UPPER(%(keyword)s), '%%')
   							 OR
   							 UPPER(t.mtrl_cd) similar to CONCAT('%%', UPPER(%(keyword)s), '%%'))
					'''
		if useYn:
			sql += ''' 
						AND t.use_yn = %(useYn)s
						'''
		if matClassPk:
			sql += ''' 
						AND t.mtrl_class_cd_pk = %(matClassPk)s
						'''
		if supplierNm:
			sql += ''' 
						AND UPPER(spr.supplier_nm) LIKE CONCAT('%%',UPPER(%(supplierNm)s),'%%')
						'''
		if makerNm:
			sql += ''' 
						AND UPPER(mkr.supplier_nm) LIKE CONCAT('%%',UPPER(%(makerNm)s),'%%')
						'''
		if matDsc:
			sql += ''' 
						AND UPPER(t.mtrl_dsc) LIKE CONCAT('%%',UPPER(%(matDsc)s),'%%')
						'''
					
		sql += ''' 
				GROUP BY t.mtrl_pk
						, t.mtrl_cd
						, t.mtrl_barcode
						, t.mtrl_nm
						, t.mtrl_class_cd_pk
						, mc.code_nm
						, t.amt_unit_pk
						, au.code_cd
						, au.code_nm
						, t.mtrl_dsc
						, t.maker_pk
						, mkr.supplier_nm
						, t.safety_stock_amt
						, t.unit_price
						, t.unit_price_dt
						, t.supplier_pk
						, spr.supplier_nm
						, t.delivery_days
						, dt.code_cd
						, dt.code_nm
						, t.photo_file_grp_cd
						, t.attach_file_grp_cd
						, t.erp_mtrl_cd
						, t.allow_add_bom
						, t.use_yn
						, t.del_yn
						, t.insert_ts
						, t.inserter_id
						, t.inserter_nm
						, t.update_ts
						, t.updater_id
						, t.updater_nm
						, t.site_id
						, t.construction_pk
						, t.equipment_pk
						, cpk.supplier_nm
						, epk.supplier_nm
			)
			, cte as (
				select base.*
				from base
			)
			, ctepage AS (
				SELECT * FROM ( table cte order by mtrl_cd ASC ) sub
				RIGHT JOIN (select count(*) from cte) c(total_rows) on true
				WHERE total_rows != 0
			)
			SELECT ctepage.*
				, coalesce(cte_stock.safety_stock_calc, 0) as safety_stock_cal
				, (select count(*)
					from cm_mtrl_inout submi
					where submi.mtrl_pk = ctepage.mtrl_pk
					and ((date(submi.inout_dt) >= ((current_date - '3 months'::interval)::date+1) AND date(submi.inout_dt) <= current_date)
							OR
						(date(submi.inout_dt) >= ((current_date - '3 months'::interval)::date+1) AND date(submi.inout_dt) <= current_date))) as inout_hist_count
				, (select count(*)
					from cm_equipment sube
					inner join cm_material subm on sube.mtrl_pk = subm.mtrl_pk
					where sube.del_yn = 'N' and subm.del_yn = 'N'
					and sube.mtrl_pk = ctepage.mtrl_pk) as cycle_equip_count
				, (select count(*)
					from cm_equip_part_mtrl subepm where subepm.mtrl_pk = ctepage.mtrl_pk and subepm.del_yn = 'N' ) as use_equip_count
			FROM ctepage
			LEFT OUTER JOIN (
					select m.mtrl_pk
						, round((case UPPER(m.delivery_type)
					 					when 'D' then m.delivery_days 		/* 일 */
										when 'W' then m.delivery_days * 7 	/* 주 */
										when 'M' then m.delivery_days * 30	/* 월 */
										else 0
 									end)
						  		* round(SUM(COALESCE(wm.a_amt, 0) + COALESCE(wm.b_amt, 0)) / 180::numeric, 2)
								* 1) as safety_stock_calc	/* 안전재고 = 평균 제품 납기일(Lead Time) x 일평균 사용 수량 x 안전 지수 */
	    				from cm_MATERIAL m
						left outer join cm_WO_MTRL wm ON wm.MTRL_PK = m.MTRL_PK
			 			left outer join cm_WORK_ORDER wmo on wm.WORK_ORDER_PK = wmo.WORK_ORDER_PK
						where date(wmo.end_dt) >= ((current_date - '6 months'::interval)::date) AND date(wmo.end_dt) <= current_date
						and wo_status = 'WOS_CL'
						group by m.mtrl_pk, m.delivery_type, m.delivery_days
			) cte_stock ON ctepage.mtrl_pk = cte_stock.mtrl_pk
			order by mtrl_cd ASC

			'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'searchMaterial.searchEquipment', ex)
			raise ex

		return items

	def get_material_selectAll(self, keyword, supplier, mtrl_class):
		sql = ''' 			
				select  t.mtrl_pk as _mtrl_pk
					, t.mtrl_cd as _mtrl_cd	            
					, t.mtrl_nm as _mtrl_nm
					, t.mtrl_class_cd_pk as _mtrl_class_pk
					, mc.code_nm as _mtrl_class_nm
					, t.safety_stock_amt as _safety_stock_amt     
					, t.amt_unit_pk as _amt_unit
					, au.code_cd as _amt_unit_cd
					, au.code_nm as _amt_unit_nm	                
					, t.mtrl_dsc as _mtrl_dsc
					, t.unit_price as _unit_price
					, t.unit_price_dt as _unit_price_dt
					, t.supplier_pk as _supplier_pk
					, spr.supplier_nm as _supplier_nm        
				from cm_material t
				inner join cm_base_code mc on t.mtrl_class_cd_pk = mc.code_pk and mc.code_grp_cd = 'MTRL_CLASS'	        
				left outer join cm_base_code au on t.amt_unit_pk = au.code_pk and au.code_grp_cd = 'AMT_UNIT'
				left outer join cm_supplier spr on t.supplier_pk = spr.supplier_pk
				where t.del_yn = 'N'      
				and t.use_yn = 'Y'			
				'''
		if keyword:
			sql += ''' 
			AND (
					UPPER(t.mtrl_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					OR
					UPPER(t.mtrl_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				)
		'''
		if supplier:
			sql += ''' 		
				AND UPPER(spr.supplier_nm) LIKE CONCAT('%%',UPPER(CAST(%(supplier)s as text)),'%%')
		'''
		if mtrl_class:
			sql += ''' 			
			AND t.mtrl_class_cd_pk = %(mtrl_class)s
		'''

		data = {}
		try:
			data = DbUtil.get_rows(sql, {'keyword':keyword,'supplier':supplier,'mtrl_class':mtrl_class})
    
		except Exception as ex:
			LogWriter.add_dblog('error','get_material_selectAll.get_material_selectAll', ex)
			raise ex

		return data

	def get_material_findOne(self, mtrl_pk):
		sql = ''' 
			/* findOne [material-mapper.xml] */

		select 	t.mtrl_pk
				, t.mtrl_cd
                , t.mtrl_barcode
				, t.mtrl_nm
				, t.mtrl_class_cd_pk as mtrl_class_pk
				, mc.code_nm as mtrl_class_nm
				, t.amt_unit_pk
				, au.code_cd as amt_unit_cd
				, au.code_nm as amt_unit_nm
				, t.mtrl_dsc
				, t.maker_pk
				, mkr.supplier_nm as maker_nm
				, t.safety_stock_amt
				, t.unit_price
				, t.unit_price_dt
				, t.supplier_pk
				, spr.supplier_nm
				, t.delivery_days
				, dt.code_cd as delivery_type_cd
				, dt.code_nm as delivery_type_nm
				, t.photo_file_grp_cd
				, t.attach_file_grp_cd
				, t.erp_mtrl_cd
				, t.allow_add_bom
				, t.use_yn
				, t.del_yn
				, t.insert_ts
				, t.inserter_id
				, t.inserter_nm
				, t.update_ts
				, t.updater_id
				, t.updater_nm
				, t.site_id
				, t.construction_pk
				, t.equipment_pk
				, cpk.supplier_nm as construction_nm
				, epk.supplier_nm as equipment_nm
				, coalesce(round((case UPPER(t.delivery_type)
					    when 'D' then t.delivery_days 		/* 일 */
					    when 'W' then t.delivery_days * 7 	/* 주 */
					    when 'M' then t.delivery_days * 30	/* 월 */
					    else 0
				   end)
				   * round(SUM(COALESCE(wo.a_amt, 0) + COALESCE(wo.b_amt, 0)) / 180::numeric, 2)
				   * 1), 0)
				  as safety_stock_calc	/* 안전재고 = 평균 제품 납기일(Lead Time) x 일평균 사용 수량 x 안전 지수 */
				, t.mtrl_barcode
	 			, '{"QR":"Material","Code":"' || t.mtrl_barcode || '","Type":"' || coalesce (mc.code_cd,'') || '","SiteId":"' || t.Site_Id || '"}' as qrbarcode
		from cm_material t
		inner join cm_base_code mc on t.mtrl_class_cd_pk = mc.code_pk and mc.code_grp_cd = 'MTRL_CLASS'
		left outer join cm_equipment e on t.mtrl_pk = e.mtrl_pk
		left outer join cm_base_code au on t.amt_unit_pk = au.code_pk and au.code_grp_cd = 'AMT_UNIT'
		left outer join cm_base_code dt on t.delivery_type = dt.code_cd and dt.code_grp_cd = 'PERIOD_TYPE'
		left outer join cm_supplier mkr on t.maker_pk = mkr.supplier_pk
		left outer join cm_supplier spr on t.supplier_pk = spr.supplier_pk
		left outer join cm_supplier cpk on t.construction_pk = cpk.supplier_pk
		left outer join cm_supplier epk on t.equipment_pk = epk.supplier_pk
		left outer join cm_mtrl_substitute ms on t.mtrl_pk = ms.mtrl_pk
		left outer join cm_material msm on ms.mtrl_substitute_pk = msm.mtrl_pk
		left outer join cm_wo_mtrl wm on t.mtrl_pk = wm.mtrl_pk

		left outer join (select wm.mtrl_pk, COALESCE(wm.a_amt, 0) as a_amt, COALESCE(wm.b_amt, 0) as b_amt--, wmo.work_order_pk
						 from cm_WO_MTRL wm
						 INNER JOIN cm_MATERIAL m ON wm.MTRL_PK = m.MTRL_PK
					 	 INNER JOIN cm_WORK_ORDER wmo on wm.WORK_ORDER_PK = wmo.WORK_ORDER_PK
						 where date(wmo.end_dt) >= ((current_date - '6 months'::interval)::date) AND date(wmo.end_dt) <= current_date
						 and wo_status = 'WOS_CL'
						 ) wo ON  t.mtrl_pk = wo.mtrl_pk

		where t.del_yn = 'N'

		AND t.mtrl_pk = %(mtrl_pk)s

		group by t.mtrl_pk
		, t.mtrl_pk
		, t.mtrl_cd
        , t.mtrl_barcode
		, t.mtrl_nm
		, t.mtrl_class_cd_pk
		, mc.code_nm
		, t.amt_unit_pk
		, au.code_cd
		, au.code_nm
		, t.mtrl_dsc
		, t.maker_pk
		, mkr.supplier_nm
		, t.safety_stock_amt
		, t.unit_price
		, t.unit_price_dt
		, t.supplier_pk
		, spr.supplier_nm
		, t.delivery_days
		, dt.code_cd
		, dt.code_nm
		, t.photo_file_grp_cd
		, t.attach_file_grp_cd
		, t.erp_mtrl_cd
		, t.allow_add_bom
		, t.use_yn
		, t.del_yn
		, t.insert_ts
		, t.inserter_id
		, t.inserter_nm
		, t.update_ts
		, t.updater_id
		, t.updater_nm
		, t.site_id
        , t.delivery_type
		, mc.code_cd
		, t.construction_pk
		, t.equipment_pk
		, cpk.supplier_nm
		, epk.supplier_nm
 
		
        '''
		data = {}
		try:
			data = DbUtil.get_row(sql, {'mtrl_pk':mtrl_pk})
    
		except Exception as ex:
			LogWriter.add_dblog('error','MaterialService.get_material_findOne', ex)
			raise ex

		return data