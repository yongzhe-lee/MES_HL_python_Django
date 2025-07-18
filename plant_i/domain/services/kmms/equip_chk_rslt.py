from configurations import settings
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.services.logging import LogWriter



class EquipCheckRstService():
    def __init__(self):
        return	

    def findAll(self, dcparam):
        items = []
        chkSchePk = CommonUtil.try_int(dcparam.get('chkSchePk'))
        chkRsltPk = CommonUtil.try_int(dcparam.get('chkRsltPk'))
        unCheckedEquipPk = CommonUtil.try_int(dcparam.get('unCheckedEquipPk'))
        deptPk = CommonUtil.try_int(dcparam.get('deptPk',None))
        chkRsltPkIsNull = dcparam.get('chkRsltPkIsNull',None)
        searchText = dcparam.get('searchText',None)
        chkStatusCd = dcparam.get('chkStatusCd',None)
        startDate = dcparam.get('startDate',None)
        endDate = dcparam.get('endDate',None)

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
        , cu."User_id" as chk_user_pk, cm_fn_user_nm(cu."Name", 'N') as chk_user_nm
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
		where 1=1             
        '''
        # and ecm.factory_pk = %(factory_pk)s

        if chkRsltPkIsNull == 'Y':
            sql += ''' AND t.chk_rslt_pk IS null
            '''
        if chkSchePk and chkSchePk > 0:
            sql += ''' AND t.chk_sche_pk = %(chkSchePk)s
            '''
        if chkRsltPk and chkRsltPk > 0:
            sql += ''' AND t.chk_rslt_pk = %(chkRsltPk)s
            '''
        if searchText:
            sql += ''' AND (UPPER(ecm.chk_mast_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			)
            '''
        if deptPk and deptPk > 0:
            sql += ''' AND d.id = %(deptPk)s
            '''
        if chkStatusCd:
            sql += ''' AND cs.code_cd = %(chkStatusCd)s
            '''
        if startDate and endDate:
            sql += ''' and (ecs.chk_sche_dt >= to_date(%(startDate)s, 'YYYYMMDD') 
            AND ecs.chk_sche_dt <= to_date(%(endDate)s, 'YYYYMMDD'))
   		    '''
        if unCheckedEquipPk and unCheckedEquipPk > 0:
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

        dc = {
            'chkSchePk': chkSchePk,
            'chkRsltPk': chkRsltPk,
            'searchText': searchText,
            'deptPk': deptPk,
            'chkStatusCd': chkStatusCd,
            'startDate': startDate,
            'endDate': endDate,
            'unCheckedEquipPk': unCheckedEquipPk
        }

        try:
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'EquipCheckRstService.findAll', ex)
            raise

        return items
    
