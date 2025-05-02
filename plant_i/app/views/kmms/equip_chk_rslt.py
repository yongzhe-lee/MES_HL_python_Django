from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipChkRslt

def equip_chk_rslt(context):
    '''
    api/kmms/equip_chk_rslt    설비점검결과
    김태영 

    findAll
    findOne
    searchEquipChkUserDept
    searchChkEquipChkRslt
    searchOne
    selectEquipResult
    insert
    updateResultEquipChkRslt
    updateChkRsltCountInfo
    deleteByChkRslts
    delete
    deleteByChkSche
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':
            chkSchePk = CommonUtil.try_int(gparam.get('chkSchePk'))
            chkRsltPk = CommonUtil.try_int(gparam.get('chkRsltPk'))
            unCheckedEquipPk = CommonUtil.try_int(gparam.get('unCheckedEquipPk'))
            deptPk = CommonUtil.try_int(gparam.get('deptPk'))
            chkRsltPkIsNull = gparam.get('chkRsltPkIsNull')
            searchText = gparam.get('searchText')
            chkStatusCd = gparam.get('chkStatusCd')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')

            sql = ''' select t.chk_rslt_pk, t.chk_sche_pk, ecs.chk_sche_no
			, d.id as dept_pk, d."Name" as dept_nm
			, ecs.chk_sche_dt, ecs.chk_dt, ecs.chk_sche_type
			, ecm.chk_mast_no, ecm.chk_mast_nm, ecm.per_number, ecm.last_chk_date, ecm.work_text
			, t.equip_pk, e.equip_nm, e.equip_cd, l.loc_nm
			, ec.equip_category_desc, es.code_nm as equip_status_nm, e.equip_dsc
			, t.chk_rslt, t.rslt_dsc, t.chk_req_type, t.chk_item_tot, t.abn_item_cnt
			, t.insert_ts, t.inserter_id, t.inserter_nm
			, t.update_ts, t.updater_id, t.updater_nm
			, e.equip_class_path, e.equip_class_desc
            , cu."User_id" as chk_user_pk, fn_user_nm(cu."Name", 'N') as chk_user_nm
			, ct.code_cd as cycle_type_cd, ct.code_nm as cycle_type_nm
			, concat(ecm.per_number, ct.code_dsc) as cycle_display_nm
			, cs.code_cd as chk_status_cd, cs.code_nm as chk_status_nm
			, count(t.chk_rslt_pk) as tot_count
			, sum(case when t.chk_rslt = 'N' then 1 else 0 end) as normal_count
			, sum(case when t.chk_rslt = 'A' then 1 else 0 end) as abNormal_count
			, sum(case when t.chk_rslt = 'C' then 1 else 0 end) as unableCheck_count
			, ecm.daily_report_cd, ecm.daily_report_type_cd
			from cm_equip_chk_rslt t
		    inner join cm_equip_chk_sche ecs on ecs.chk_sche_pk = t.chk_sche_pk
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
		    left join dept d on d.id = ecs.dept_pk
		    inner join cm_equipment e on t.equip_pk = e.equip_pk
		    left join cm_base_code cs on cs.code_cd = ecs.chk_status 
		    and cs.code_grp_cd = 'CHK_STATUS'
		    left join user_profile cu on cu."User_id" = ecs.chk_user_pk
		    left join cm_base_code ct on ct.code_cd = ecm.cycle_type
		    and ct.code_grp_cd = 'CYCLE_TYPE'
		    left join cm_location l on e.loc_pk = l.loc_pk
		    left join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
		    left join cm_base_code es on e.equip_status = es.code_cd 
		    and es.code_grp_cd = 'EQUIP_STATUS'
		    where ecm.factory_pk = %(factory_pk)s
            '''
            if chkRsltPkIsNull == 'Y':
                sql += ''' AND t.chk_rslt_pk IS null
                '''
            if chkSchePk > 0:
                sql += ''' AND t.chk_sche_pk = %(chkSchePk)s
                '''
            if chkRsltPk > 0:
                sql += ''' AND t.chk_rslt_pk = %(chkRsltPk)s
                '''
            if searchText:
                sql += ''' AND (UPPER(ecm.chk_mast_nm) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
				    OR
				    UPPER(e.equip_nm) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
				    OR
				    UPPER(e.equip_cd) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
   			    )
                '''
            if deptPk > 0:
                sql += ''' AND d.id = %(deptPk)s
                '''
            if chkStatusCd:
                sql += ''' AND cs.code_cd = %(chkStatusCd)s
                '''
            if startDate and endDate:
                sql += ''' and (ecs.chk_sche_dt >= to_date(%(startDate)s, 'YYYYMMDD') 
                AND ecs.chk_sche_dt <= to_date(%(endDate)s, 'YYYYMMDD'))
   		        '''
            if unCheckedEquipPk > 0:
                sql += ''' AND ecs.chk_dt is null
			    AND ecs.chk_user_pk is null
			    AND cs.code_cd = 'CHK_STATUS_N'
			    AND t.equip_pk = %(unCheckedEquipPk)s
                '''
            sql += ''' group by t.chk_rslt_pk, t.chk_sche_pk, ecs.chk_sche_no, d.id, d."Name"
			, ecs.chk_sche_dt, ecs.chk_dt, ecs.chk_sche_type
			, ecm.chk_mast_no, ecm.chk_mast_nm, ecm.per_number, ecm.last_chk_date, ecm.work_text
			, t.equip_pk, e.equip_nm, t.chk_rslt, t.rslt_dsc, t.chk_req_type, t.chk_item_tot
			, t.abn_item_cnt, t.insert_ts, t.inserter_id, t.inserter_nm, t.update_ts, t.updater_id, t.updater_nm
			, cu."User_id", cu."Name"
			-- , cu.del_yn
			, ct.code_cd, ct.code_nm, ct.code_dsc, cs.code_cd, cs.code_nm
			, e.equip_cd, l.loc_nm, ec.equip_category_desc, e.equip_class_path, e.equip_class_desc
			, es.code_nm, e.equip_dsc, ecm.daily_report_cd, ecm.daily_report_type_cd
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk
            dc['chkRsltPk'] = chkRsltPk
            dc['searchText'] = searchText
            dc['deptPk'] = deptPk
            dc['chkStatusCd'] = chkStatusCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['unCheckedEquipPk'] = unCheckedEquipPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'findOne':
            chkRsltPk = CommonUtil.try_int( gparam.get('chkRsltPk') )

            sql = ''' select t.chk_rslt_pk, t.chk_sche_pk, ecs.chk_sche_no
			, d.id as dept_pk, d."Name" as dept_nm
			, ecs.chk_sche_dt, ecs.chk_dt, ecs.chk_sche_type
			, ecm.chk_mast_no, ecm.chk_mast_nm, ecm.per_number, ecm.last_chk_date, ecm.work_text
			, t.equip_pk, e.equip_nm, e.equip_cd, l.loc_nm
			, ec.equip_category_desc, es.code_nm as equip_status_nm, e.equip_dsc
			, t.chk_rslt, t.rslt_dsc, t.chk_req_type, t.chk_item_tot, t.abn_item_cnt
			, t.insert_ts, t.inserter_id, t.inserter_nm
			, t.update_ts, t.updater_id, t.updater_nm
			, e.equip_class_path, e.equip_class_desc
            , cu."User_id" as chk_user_pk, fn_user_nm(cu."Name", 'N') as chk_user_nm
			, ct.code_cd as cycle_type_cd, ct.code_nm as cycle_type_nm
			, concat(ecm.per_number, ct.code_dsc) as cycle_display_nm
			, cs.code_cd as chk_status_cd, cs.code_nm as chk_status_nm
			, count(t.chk_rslt_pk) as tot_count
			, sum(case when t.chk_rslt = 'N' then 1 else 0 end) as normal_count
			, sum(case when t.chk_rslt = 'A' then 1 else 0 end) as abNormal_count
			, sum(case when t.chk_rslt = 'C' then 1 else 0 end) as unableCheck_count
			, ecm.daily_report_cd, ecm.daily_report_type_cd
			from cm_equip_chk_rslt t
		    inner join cm_equip_chk_sche ecs on ecs.chk_sche_pk = t.chk_sche_pk
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
		    left join dept d on d.id = ecs.dept_pk
		    inner join cm_equipment e on t.equip_pk = e.equip_pk
		    left join cm_base_code cs on cs.code_cd = ecs.chk_status 
		    and cs.code_grp_cd = 'CHK_STATUS'
		    left join user_profile cu on cu."User_id" = ecs.chk_user_pk
		    left join cm_base_code ct on ct.code_cd = ecm.cycle_type
		    and ct.code_grp_cd = 'CYCLE_TYPE'
		    left join cm_location l on e.loc_pk = l.loc_pk
		    left join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
		    left join cm_base_code es on e.equip_status = es.code_cd 
		    and es.code_grp_cd = 'EQUIP_STATUS'
		    where t.chk_rslt_pk = %(chkRsltPk)s
            and ecm.factory_pk = %(factory_pk)s
            group by t.chk_rslt_pk, t.chk_sche_pk, ecs.chk_sche_no, d.id, d."Name"
			, ecs.chk_sche_dt, ecs.chk_dt, ecs.chk_sche_type
			, ecm.chk_mast_no, ecm.chk_mast_nm, ecm.per_number, ecm.last_chk_date, ecm.work_text
			, t.equip_pk, e.equip_nm, t.chk_rslt, t.rslt_dsc, t.chk_req_type, t.chk_item_tot
			, t.abn_item_cnt, t.insert_ts, t.inserter_id, t.inserter_nm, t.update_ts, t.updater_id, t.updater_nm
			, cu."User_id", cu."Name"
			-- , cu.del_yn
			, ct.code_cd, ct.code_nm, ct.code_dsc, cs.code_cd, cs.code_nm
			, e.equip_cd, l.loc_nm, ec.equip_category_desc, e.equip_class_path, e.equip_class_desc
			, es.code_nm, e.equip_dsc, ecm.daily_report_cd, ecm.daily_report_type_cd
            '''

            dc = {}
            dc['chkRsltPk'] = chkRsltPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'searchEquipChkUserDept':
            chkSchePk = CommonUtil.try_int( gparam.get('chkSchePk') )

            sql = ''' SELECT chk_user_pk, dept_pk
		    FROM cm_equip_chk_sche
		    WHERE chk_sche_pk = %(chkSchePk)s
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk

            items = DbUtil.get_row(sql, dc)

        elif action == 'searchChkEquipChkRslt':
            chkSchePk = CommonUtil.try_int( gparam.get('chkSchePk') )

            sql = ''' select count(*) AS chk_rslt_cnt
		    from cm_equip_chk_rslt t
		    inner join cm_equip_chk_sche ecs on ecs.chk_sche_pk = t.chk_sche_pk
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
		    where ecm.factory_pk = %(factory_pk)s
		    and t.chk_sche_pk = %(chkSchePk)s
		    and t.CHK_RSLT IS NULL
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'searchOne':
            chkSchePk = CommonUtil.try_int(gparam.get('chkSchePk'))
            chkRsltPk = CommonUtil.try_int(gparam.get('chkRsltPk'))
            unCheckedEquipPk = CommonUtil.try_int(gparam.get('unCheckedEquipPk'))
            deptPk = CommonUtil.try_int(gparam.get('deptPk'))
            chkRsltPkIsNull = gparam.get('chkRsltPkIsNull')
            searchText = gparam.get('searchText')
            chkStatusCd = gparam.get('chkStatusCd')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')

            sql = ''' select t.chk_sche_pk, ecs.chk_sche_no, d.id as dept_pk, d."Name" as dept_nm
			, ecs.chk_sche_dt, ecs.chk_dt, ecs.chk_sche_type, ecm.chk_mast_no, ecm.chk_mast_nm
			, ecm.per_number, ecm.last_chk_date, ecm.work_text
			, t.rslt_dsc, t.chk_req_type
			, cu."User_id" as chk_user_pk, fn_user_nm(cu."Name", 'N') as chk_user_nm
			, ct.code_cd as cycle_type_cd, ct.code_nm as cycle_type_nm
			, concat(ecm.per_number, ct.code_dsc) as cycle_display_nm
			, cs.code_cd as chk_status_cd, cs.code_nm as chk_status_nm
			, count(t.chk_rslt_pk) as tot_count
			, sum(case when t.chk_rslt = 'N' then 1 else 0 end) as normal_count
			, sum(case when t.chk_rslt = 'A' then 1 else 0 end) as abNormal_count
			, sum(case when t.chk_rslt = 'C' then 1 else 0 end) as unableCheck_count
			, ecs.insert_ts AS sch_insert_ts
			, ecm.daily_report_cd, ecm.daily_report_type_cd
			from cm_equip_chk_rslt t
            inner join cm_equip_chk_sche ecs on ecs.chk_sche_pk = t.chk_sche_pk
            inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
            left join dept d on d.id = ecs.dept_pk
            inner join cm_equipment e on t.equip_pk = e.equip_pk
            left join cm_base_code cs on cs.code_cd = ecs.chk_status 
            and cs.code_grp_cd = 'CHK_STATUS'
            left join user_profile cu on cu."User_id" = ecs.chk_user_pk
            left join cm_base_code ct on ct.code_cd = ecm.cycle_type
            and ct.code_grp_cd = 'CYCLE_TYPE'
            left join cm_location l on e.loc_pk = l.loc_pk
            left join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
            left join cm_base_code es on e.equip_status = es.code_cd 
            and es.code_grp_cd = 'EQUIP_STATUS'
            where ecm.factory_pk = %(factory_pk)s
             '''
            if chkRsltPkIsNull == 'Y':
                sql += ''' AND t.chk_rslt_pk IS null
                '''
            if chkSchePk > 0:
                sql += ''' AND t.chk_sche_pk = %(chkSchePk)s
                '''
            if chkRsltPk > 0:
                sql += ''' AND t.chk_rslt_pk = %(chkRsltPk)s
                '''
            if searchText:
                sql += ''' AND (UPPER(ecm.chk_mast_nm) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
				    OR
				    UPPER(e.equip_nm) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
				    OR
				    UPPER(e.equip_cd) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
   			    )
                '''
            if deptPk > 0:
                sql += ''' AND d.id = %(deptPk)s
                '''
            if chkStatusCd:
                sql += ''' AND cs.code_cd = %(chkStatusCd)s
                '''
            if startDate and endDate:
                sql += ''' and (ecs.chk_sche_dt >= to_date(%(startDate)s, 'YYYYMMDD') 
                AND ecs.chk_sche_dt <= to_date(%(endDate)s, 'YYYYMMDD'))
   		        '''
            if unCheckedEquipPk > 0:
                sql += ''' AND ecs.chk_dt is null
			    AND ecs.chk_user_pk is null
			    AND cs.code_cd = 'CHK_STATUS_N'
			    AND t.equip_pk = %(unCheckedEquipPk)s
                '''
            sql += ''' group by t.chk_sche_pk, ecs.chk_sche_no, d.id, d."Name"
                , ecs.chk_sche_dt, ecs.chk_dt, ecs.chk_sche_type
                , ecm.chk_mast_no, ecm.chk_mast_nm, ecm.per_number, ecm.last_chk_date, ecm.work_text
                , t.rslt_dsc, t.chk_req_type, cu."User_id", cu."Name" 
                -- , cu.del_yn
                , ct.code_cd, ct.code_nm, ct.code_dsc, cs.code_cd, cs.code_nm
                , ecs.insert_ts, ecm.daily_report_cd, ecm.daily_report_type_cd
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk
            dc['chkRsltPk'] = chkRsltPk
            dc['searchText'] = searchText
            dc['deptPk'] = deptPk
            dc['chkStatusCd'] = chkStatusCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['unCheckedEquipPk'] = unCheckedEquipPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'selectEquipResult':
            chkSchePk = CommonUtil.try_int(gparam.get('chkSchePk'))
            chkRsltPk = CommonUtil.try_int(gparam.get('chkRsltPk'))
            unCheckedEquipPk = CommonUtil.try_int(gparam.get('unCheckedEquipPk'))
            deptPk = CommonUtil.try_int(gparam.get('deptPk'))
            chkRsltPkIsNull = gparam.get('chkRsltPkIsNull')
            searchText = gparam.get('searchText')
            chkStatusCd = gparam.get('chkStatusCd')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')

            sql = ''' select t.chk_rslt_pk, t.chk_sche_pk, ecs.chk_sche_no
			, d.id as dept_pk, ecs.chk_dt, ecm.chk_mast_nm
			, t.equip_pk, e.equip_nm, t.chk_rslt, t.rslt_dsc
			, t.chk_req_type, t.chk_item_tot, t.abn_item_cnt
			, sum(case when t.chk_rslt = 'N' then 1 else 0 end) as fail_count
			, wo.work_order_pk, wo.work_order_no
			, t.insert_ts, t.inserter_id, t.inserter_nm
			, t.update_ts, t.updater_id, t.updater_nm
			from cm_equip_chk_rslt t
            inner join cm_equip_chk_sche ecs on ecs.chk_sche_pk = t.chk_sche_pk
            inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
            left join dept d on d.id = ecs.dept_pk
            inner join cm_equipment e on t.equip_pk = e.equip_pk
            left join cm_base_code cs on cs.code_cd = ecs.chk_status 
            and cs.code_grp_cd = 'CHK_STATUS'
            inner join work_order wo on t.chk_rslt_pk = wo.chk_rslt_pk
            where ecm.factory_pk = %(factory_pk)s
            '''
            if chkRsltPkIsNull == 'Y':
                sql += ''' AND t.chk_rslt_pk IS null
                '''
            if chkSchePk > 0:
                sql += ''' AND t.chk_sche_pk = %(chkSchePk)s
                '''
            if chkRsltPk > 0:
                sql += ''' AND t.chk_rslt_pk = %(chkRsltPk)s
                '''
            if searchText:
                sql += ''' AND (UPPER(ecm.chk_mast_nm) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
				    OR
				    UPPER(e.equip_nm) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
				    OR
				    UPPER(e.equip_cd) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
   			    )
                '''
            if deptPk > 0:
                sql += ''' AND d.id = %(deptPk)s
                '''
            if chkStatusCd:
                sql += ''' AND cs.code_cd = %(chkStatusCd)s
                '''
            if startDate and endDate:
                sql += ''' and (ecs.chk_sche_dt >= to_date(%(startDate)s, 'YYYYMMDD') 
                AND ecs.chk_sche_dt <= to_date(%(endDate)s, 'YYYYMMDD'))
   		        '''
            if unCheckedEquipPk > 0:
                sql += ''' AND ecs.chk_dt is null
			    AND ecs.chk_user_pk is null
			    AND cs.code_cd = 'CHK_STATUS_N'
			    AND t.equip_pk = %(unCheckedEquipPk)s
                '''
            sql += ''' group by t.chk_rslt_pk, t.chk_sche_pk, ecs.chk_sche_no
			, d.id, ecs.chk_dt, ecm.chk_mast_nm, t.equip_pk, e.equip_nm
			, t.chk_rslt, t.rslt_dsc, t.chk_req_type, t.chk_item_tot, t.abn_item_cnt
			, t.insert_ts, t.inserter_id, t.inserter_nm
			, t.update_ts, t.updater_id, t.updater_nm
			, wo.work_order_pk, wo.work_order_no
			Having MAX(case when t.chk_rslt = 'N' then 1 else 0 end) 
                = coalesce(%(chkRslt)s, MAX(case when t.chk_rslt = 'N' then 1 else 0 end))
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk
            dc['chkRsltPk'] = chkRsltPk
            dc['searchText'] = searchText
            dc['deptPk'] = deptPk
            dc['chkStatusCd'] = chkStatusCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['unCheckedEquipPk'] = unCheckedEquipPk
            dc['chkRslt'] = chkRslt
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'insert':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            chkItemTot = CommonUtil.try_int(posparam.get('chkItemTot'))
            abnItemCnt = CommonUtil.try_int(posparam.get('abnItemCnt'))

            chkRslt = posparam.get('chkRslt')
            rsltDsc = posparam.get('rsltDsc')
            chkReqType = posparam.get('chkReqType')
            method = posparam.get('method')
            guide = posparam.get('guide')
            dailyReportItemCd = posparam.get('dailyReportItemCd')

            c = CmEquipChkRslt()

            c.CmEquipChkSche_id = chkSchePk
            c.CmEquipment_id = equipPk
            c.ChkRslt = chkRslt
            c.RsltDsc = rsltDsc
            c.ChkReqType = chkReqType
            c.ChkItemTot = chkItemTot
            c.AbnItemCnt = abnItemCnt
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비점검결과가 등록되었습니다.'}

        elif action == 'updateResultEquipChkRslt':
            chkRsltPk = CommonUtil.try_int(posparam.get('chkRsltPk'))
            
            sql = ''' update cm_equip_chk_rslt
		    set chk_rslt = (
			    select (case when sum(case when v.chk_item_rslt = 'A' then 1 else 0 end) > 0 then 'A'
				    when sum(case when v.chk_item_rslt = 'C' then 1 else 0 end) = count(*) then 'C' else 'N' end)
			    from cm_equip_chk_item_rslt v
			    where v.chk_rslt_pk  = %(chkRsltPk)s
		    )
		    where chk_rslt_pk = %(chkRsltPk)s
            '''

            dc = {}
            dc['chkRsltPk'] = chkRsltPk

            ret = DbUtil.execute(sql, dc)

            return {'success': True, 'message': '설비 점검 항목 정보가 수정되었습니다.'}

        elif action == 'updateChkRsltCountInfo':
            chkRsltPk = CommonUtil.try_int(posparam.get('chkRsltPk'))
            chkItemTot = CommonUtil.try_int(posparam.get('chkItemTot'))
            abnItemCnt = CommonUtil.try_int(posparam.get('abnItemCnt'))
            chkRslt = posparam.get('chkRslt')
            
      #       sql = ''' update cm_equip_chk_rslt
		    # set chk_rslt = %(chkRslt)s
		    # , chk_item_tot = %(chkItemTot)s
		    # , abn_item_cnt = %(abnItemCnt)s
		    # where chk_rslt_pk = %(chkRsltPk)s
      #       '''

      #       dc = {}
      #       dc['chkRsltPk'] = chkRsltPk
      #       dc['chkItemTot'] = chkItemTot
      #       dc['abnItemCnt'] = abnItemCnt
      #       dc['chkRslt'] = chkRslt

            #ret = DbUtil.execute(sql, dc)

            cr = CmEquipChkRslt.objects.get(id=chkRsltPk)
            cr.ChkRslt = chkRslt
            cr.ChkItemTot = chkItemTot
            cr.AbnItemCnt = abnItemCnt
            cr.save()

            return {'success': True, 'message': '설비점검결과가 수정되었습니다.'}

        elif action == 'delete':
            chkRsltPk = CommonUtil.try_int(posparam.get('chkRsltPk'))
            CmEquipChkRslt.objects.filter(id=chkRsltPk).delete()

            items = {'success': True}
    

        elif action == 'deleteByChkRslts':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkRsltPks = gparam.get('chkRsltPks')
            pk_list = chkRsltPks.split(',')

            q = CmEquipChkRslt.objects.filter(CmEquipChkSche_id=chkSchePk)
            q = q.exclude(id__in=pk_list)
            q.delete()

            items = {'success': True}

        elif action == 'deleteByChkSche':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))

            q = CmEquipChkRslt.objects.filter(CmEquipChkSche_id=chkSchePk)
            q.delete()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/equip_chk_rslt : action-{}'.format(action)
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