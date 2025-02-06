from django.db import transaction
from domain.services.sql import DbUtil
from domain.models.kmms import PreventiveMaintenace
from domain.services.definition.equipment import EquipmentService
# from domain.services.file import FileService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil


def pm_master(context):
    '''
    /api/kmms/pi_master
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    equipment_service = EquipmentService()

    if action=='read':
        site_id = gparam.get('site_id', None)
        use_yn = gparam.get('use_yn', None)
        equip_category_id = gparam.get('equip_category_id', None)
        process_cd = gparam.get('process_cd', None)
        system_cd = gparam.get('system_cd', None)
        start_date = gparam.get('start_date', None)
        end_date = gparam.get('end_date', None)
        keyword = gparam.get('keyword', None)
        cycle_type_cd = gparam.get('cycle_type_cd', None)
        pm_no = gparam.get('pm_no', None)
        pm_type_cd = gparam.get('pm_type_cd', None)
        env_equip_yn = gparam.get('env_equip_yn', None)
        dept_pk = gparam.get('dept_pk', None)
        loc_pk = gparam.get('loc_pk', None)
        pm_user_pk = gparam.get('pm_user_pk', None)
        equip_pk = gparam.get('equip_pk', None)
        pm_pk_not = gparam.get('pm_pk_not', None)

        sql = '''
        with cte as (
            SELECT 
                t.pm_pk
                , t.pm_no
                , t.pm_nm
                , e.equip_pk
                , e.equip_cd
                , e.equip_nm
                , e.import_rank_pk
			    , ir.import_rank_cd 				AS import_rank_nm
                , d.dept_pk
                , d.dept_nm
                , pu.user_pk                        AS pm_user_pk
                , fn_user_nm(pu.user_nm, pu.del_yn) AS pm_user_nm
                , (case 
                    when (t.pm_no ~ E'^[0-9]+$') = true 
                    then cast(t.pm_no as integer) 
                    else 999999 
                    end) as pm_no_sort
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
		        , eqd.dept_nm as mdept_nm
			    , l.loc_nm
		        , ec.equip_category_desc
				, (select code_nm 
                    from code 
                    where code_grp_cd = 'EQUIPMENT_PROCESS' 
                    and code_cd = e.process_cd) as process_nm
				, (select code_nm 
                    from code 
                    where code_grp_cd = 'EQUIP_SYSTEM' 
                    and code_cd = e.system_cd) as system_nm
		    FROM 
                pm t
                INNER JOIN equipment e ON t.equip_pk = e.equip_pk
		        INNER JOIN location l ON e.loc_pk = l.loc_pk
		        LEFT OUTER JOIN dept d ON t.dept_pk = d.dept_pk
		        LEFT OUTER JOIN code pt ON t.pm_type = pt.code_cd AND pt.code_grp_cd = 'PM_TYPE'
		        LEFT OUTER JOIN code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
		        LEFT OUTER JOIN user_info pu ON t.pm_user_pk = pu.user_pk
		        LEFT OUTER JOIN dept eqd ON e.dept_pk = eqd.dept_pk
			    LEFT OUTER JOIN import_rank ir on e.import_rank_pk = ir.import_rank_pk
				LEFT OUTER JOIN equip_category ec on ec.equip_category_id = e.equip_category_id
		    WHERE 1 = 1
                AND t.del_yn = 'N'
            '''
        if site_id:
            sql += '''
            AND t.site_id = %(site_id)s
            '''
        if use_yn:
            sql += '''
            AND t.use_yn = %(use_yn)s
            '''
        if equip_category_id:
            sql += '''
            AND e.equip_pk = %(equip_category_id)s
            '''
        if process_cd:
            sql += '''
            AND e.process_cd = %(process_cd)s
            '''
        if system_cd:
            sql += '''
            AND e.system_cd = %(system_cd)s
            '''
        if start_date != None and end_date != None:
            sql += '''
            AND date(coalesce(t.next_chk_date, cast(fn_get_regular_day(
                t.sched_start_dt::date
                , t.sched_start_dt::date
                , t.per_number
                , ct.code_cd) as date)))
			BETWEEN to_date(%(start_date)s, 'YYYY-MM-DD') 
                AND to_date(%(end_data)s, 'YYYY-MM-DD')
            '''
        if keyword:
            sql += '''
            AND (
				UPPER(t.pm_nm) LIKE CONCAT('%', UPPER(CAST(%(keyword)s AS text)), '%')
				OR
				UPPER(e.equip_nm) LIKE CONCAT('%', UPPER(CAST(%(keyword)s AS text)), '%')
				OR
				UPPER(e.equip_cd) LIKE CONCAT('%', UPPER(CAST(%(keyword)s AS text)), '%')
				OR
				UPPER(t.pm_no) LIKE CONCAT('%', UPPER(CAST(%(keyword)s AS text)), '%')
   			)
            '''
        if cycle_type_cd:
            sql += '''
            AND ct.code_cd = %(cycle_type_cd)s
            '''
        if pm_no:
            sql += '''
            AND t.pm_no = %(pm_no)s
            '''
        if pm_type_cd:
            sql += '''
            AND pt.code_cd = %(pm_type_cd)s
            '''
        if env_equip_yn:
            sql += '''
            AND e.environ_equip_yn = %(env_equip_yn)s
            '''
        if dept_pk and dept_pk > 0 :
            sql += '''
            AND (
				d.dept_pk = %(dept_pk)s
				OR
				d.dept_pk In (
                    select dept_pk 
                    from v_dept_path 
                    where %(dept_pk)s = path_info_pk
                )
			)
            '''
        if loc_pk and loc_pk > 0:
            sql += '''
            AND (
                l.loc_pk = %(loc_pk)s
                OR
                l.loc_pk In (
                    select loc_pk   
                    from (
                        select *
                        from fn_get_loc_path(%(site_id)s)
                    ) x
                    where %(loc_pk)s = path_info_pk
                )
             )
            '''
        if pm_user_pk and pm_user_pk > 0:
            sql += '''
            AND pu.user_pk = %(pm_user_pk)s
            '''
        if equip_pk and equip_pk > 0:
            sql += '''
            AND e.equip_pk = %(equip_pk)s
            '''
        if pm_pk_not and pm_pk_not > 0:
            sql += '''
            AND t.pm_pk <> %(pm_pk_not)s
            '''

        sql += '''
        )
        SELECT *
            , CAST(fn_get_work_day(to_char(fn_get_last_pm_date(sub.pm_pk), 'YYYY-MM-DD')) AS timestamp) as next_chk_date
            , (select
                count(*)
                from work_order wo
 				where wo.pm_pk = sub.pm_pk
			   ) as wo_count
		FROM (
			table cte
		) sub
		RIGHT JOIN 
            (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        '''

        site_id = gparam.get('site_id', None)

        dc = {}
        dc['site_id'] = site_id
        dc['use_yn'] = use_yn
        dc['equip_category_id'] = equip_category_id
        dc['process_cd'] = process_cd
        dc['system_cd'] = system_cd
        dc['start_date'] = start_date
        dc['end_date'] = end_date
        dc['keyword'] = keyword
        dc['cycle_type_cd'] = cycle_type_cd
        dc['pm_no'] = pm_no
        dc['pm_type_cd'] = pm_type_cd
        dc['env_equip_yn'] = env_equip_yn
        dc['dept_pk'] = dept_pk
        dc['loc_pk'] = loc_pk
        dc['pm_user_pk'] = pm_user_pk
        dc['equip_pk'] = equip_pk
        dc['pm_pk_not'] = pm_pk_not

        items = DbUtil.get_rows(sql, dc)

    elif action=='detail':
        id = gparam.get('id', None)
        items = equipment_service.get_equipment_detail(id)

    elif action=='save':
        posparam = context.posparam
        print(posparam)
        id = posparam.get('id','')
        code = posparam.get('Code')
        name = posparam.get('Name')
        equipment = None
        eh_content = ''
        today = DateUtil.get_today()

        try:
            if id:
                equipment = Equipment.objects.get(id=id)

                q = Equipment.objects.filter(Code=code)
                q = q.exclude(pk=id)
                check_code = q.first()

                name = Equipment.objects.filter(Name=name)
                name = name.exclude(pk=id)
                check_name = name.first()

            else:
                #{'id': '', 'EquipmentGroup_id': '1', 'Code': 'equip-1', 'Name': '설비1', 'ManageNumber': 'ㅁㄴㄻㄴ', 'WorkCenter_id': '2', 
                #'Model': 'ㅁㄴㅇㄹ', 'Maker': 'ㄴ', 'SerialNumber': 'ㅁㄴㄻㄴ', 'ProductionYear': '', 'PurchaseYear': '', 
                #'InstallDate': 'ㄴ', 'SupplierName': 'ㄴㄴ', 
                #'PurchaseCost': 'ㅁㄴㅇㄹ', 'OperationRateYN': 'Y', 'DisposalDate': 'ㅇㅁㄴㅇㄻ', 'Manager': 'ㅁ', 
                #'Description': 'ㅁㄴㅇㄻㄴㅇㄻㄴㅇㄻㄴㅇㄻㄴㅇㄻㄴㅇㄹ', 
                #'csrfmiddlewaretoken': 'xJwIk4wgZG9Gv3tllsxNHec3BBOAWi21dyjjtlUaFO7NJcimoJvawsoMsm01gn8t'}
                equipment = Equipment()

                check_code = Equipment.objects.filter(Code=code).first()
                check_name = Equipment.objects.filter(Name=name).first()

            if check_code:
                items = {'success': False, 'message' : '중복된 설비그룹코드가 존재합니다.'}
                return items

            if check_name:
                items = {'success': False, 'message' : '중복된 설비그룹명이 존재합니다.'}
                return items

            equipment.Code = posparam.get('Code')
            equipment.Name = posparam.get('Name')
            equipment.Line_id = posparam.get('Line_id')
            equipment.MESCode = posparam.get('MESCode')
            equipment.SAPCode = posparam.get('SAPCode')
            equipment.EquipmentGroup_id = posparam.get('EquipmentGroup_id')
            equipment.Description = posparam.get('Description')
            equipment.Maker = posparam.get('Maker')
            equipment.Model = posparam.get('Model')
            equipment.Standard = posparam.get('Standard')
            equipment.Usage = posparam.get('Usage')
            equipment.ManageNumber = posparam.get('ManageNumber')
            equipment.SerialNumber = posparam.get('SerialNumber')
            equipment.Depart_id = posparam.get('Depart_id')
            equipment.ProductionYear = posparam.get('ProductionYear') if posparam.get('ProductionYear') else None
            equipment.AssetYN = posparam.get('AssetYN')
            equipment.DurableYears = posparam.get('DurableYears') if posparam.get('DurableYears') else None
            equipment.PowerWatt = posparam.get('PowerWatt')
            equipment.Voltage = posparam.get('Voltage')
            equipment.Manager = posparam.get('Manager')
            equipment.SupplierName = posparam.get('SupplierName')
            equipment.PurchaseDate = posparam.get('PurchaseDate') if posparam.get('PurchaseDate') else None
            equipment.PurchaseCost = posparam.get('PurchaseCost') if posparam.get('PurchaseCost') else None
            equipment.ServiceCharger = posparam.get('ServiceCharger')
            equipment.ASTelNumber = posparam.get('ASTelNumber')
            equipment.AttentionRemark = posparam.get('AttentionRemark')
            equipment.Inputdate = posparam.get('InputDate') if posparam.get('InputDate') else None
            equipment.InstallDate = posparam.get('InstallDate') if posparam.get('InstallDate') else None
            equipment.DisposalDate = posparam.get('DisposalDate') if posparam.get('DisposalDate') else None
            equipment.DisposalReason = posparam.get('DisposalReason')
            equipment.OperationRateYN = posparam.get('OperationRateYN')
            equipment.set_audit(user)

            equipment.save()

            items = {'success': True, 'id': equipment.id}

        except Exception as ex:
            source = 'api/definition/equipment, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='delete':
        try:
            id = posparam.get('id','')
            Equipment.objects.filter(id=id).delete()
            items = {'success': True}

        except Exception as ex:
            source = 'api/definition/equipment, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
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
            #if action == 'delete':
            #    items = {'success':False, 'message': '삭제중 오류가 발생하였습니다.'}
            #    return items
            #raise ex

    # elif action == 'save_photo':
    #     eq_id = posparam.get('eq_id', '')
    #     file_id = posparam.get('file_id',None)
    #     if eq_id:
    #         fileService = FileService()
    #         file_id_list = file_id.split(',')
    #         for id in file_id_list:
    #             fileService.updateDataPk(id, eq_id)

    #         items = {'success' : True}

    return items