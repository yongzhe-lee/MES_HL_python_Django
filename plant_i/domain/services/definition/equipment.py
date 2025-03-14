from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class EquipmentService():

    def __init__(self):
        return

    def get_equipment_pop_search(self, group_id, keyword):
        items = []
        dic_param = {'group_id':group_id, 'keyword':keyword}
        
        sql = '''
        select 
            e.id
            , e."Code"
            , e."Name"
            , eg."Name" as group_name
            , eg."EquipmentType"
            , fn_code_name('equipment_type',  eg."EquipmentType") as "EquipmentTypeName"
        from 
            equ e
        left join 
            equ_grp eg on e."EquipmentGroup_id" = eg.id
        where 1=1  
        '''
        if group_id:
            sql+=''' and e."EquipmentGroup_id"=%(group_id)s
            '''

        if keyword:
            sql+=''' and upper(e."Name") like concat('%%',%(keyword)s,'%%')
            '''
            
        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equipment_list', ex)
            raise ex

        return items


    def get_equipment_list(self, line_id, group_id, equipment):
        items = []
        dic_param = {'line_id':line_id, 'group_id':group_id, 'equipment':equipment}

        sql = ''' 
        SELECT 
            e.id
            , e."Code" AS "Code"
            , e."line_id" AS "Line_id"                             -- new
            , l."Name" AS "line_name"                           -- new
            , e."MESCode" AS "MESCode"                          -- new
            , e."SAPCode" AS "SAPCode"                          -- new
            , e."Name" AS "Name"
            , e."EquipmentGroup_id" AS "EquipmentGroup_id"
            , eg."Name" AS "group_name"  
            , e."Description" AS "Description"
            , e."Maker" AS "Maker"
            , e."Model" AS "Model"
            , e."Standard" AS "Standard"
            , e."Usage" AS "Usage"
            , e."ManageNumber" AS "ManageNumber"
            , e."SerialNumber" AS "SerialNumber"
            , e."Depart_id" AS "Depart_id"
            , e."Depart_id" AS "equip_dept_bef"
            , d."Name" AS "depart_Name"
            , e."ProductionYear" AS "ProductionYear"
            , e."AssetYN" AS "AssetYN"
            , e."DurableYears" AS "DurableYears"
            , e."PowerWatt" AS "PowerWatt"
            , e."Voltage" AS "Voltage"
            , e."Manager" AS "Manager"
            , e."SupplierName" AS "SupplierName"
            , to_char(e."PurchaseDate",'yyyy-mm-dd') AS "PurchaseDate"
            , e."PurchaseCost" AS "PurchaseCost"
            , e."ServiceCharger" AS "ServiceCharger"
            , e."ASTelNumber" AS "ASTelNumber"
            , e."AttentionRemark" AS "AttentionRemark"
            /* , to_char(e."Inputdate",'yyyy-mm-dd') AS Inputdate */
            , e."Inputdate" AS "Inputdate"
            , to_char(e."InstallDate",'yyyy-mm-dd') AS "InstallDate"
            , to_char(e."DisposalDate",'yyyy-mm-dd') AS "DisposalDate"
            , e."DisposalReason" AS "DisposalReason"
            , e."OperationRateYN" AS "OperationRateYN"
            , e."Status"
            , c."Name" AS "StatusNm"
            , e."loc_pk" AS "loc_pk"
            , e."loc_pk" AS "equip_loc_bef"
            , lo."loc_nm" AS "Location"
            , e."import_rank"
            , c2."Name" AS "importRank"
            , to_char(e._created ,'yyyy-MM-dd HH:mm') AS _created 
        FROM 
            equ e
        LEFT JOIN 
            line l ON e."line_id" = l.id
        LEFT JOIN 
            equ_grp eg ON e."EquipmentGroup_id" = eg.id
        LEFT JOIN 
            dept d ON e."Depart_id" = d.id
        LEFT JOIN 
            "location" lo on e.loc_pk = lo.id 
        LEFT JOIN 
    		"code" c on c."Code" = e."Status" and c."CodeGroupCode" = 'EQU_STATUS'
        LEFT JOIN 
    		"code" c2 on c2."Code" = e."import_rank" and c2."CodeGroupCode" = 'IMPORT_RANK'
        WHERE 1 = 1  
        '''
        if line_id:
            sql+=''' 
            AND e."line_id"=%(line_id)s
            '''
        if group_id:
            sql+=''' 
            AND e."EquipmentGroup_id"=%(group_id)s
            '''
        if equipment:
            sql+=''' 
            AND UPPER(e."Name") LIKE CONCAT('%%',UPPER(%(equipment)s),'%%')
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equipment_list', ex)
            raise ex

        return items

    def get_equip_obsolete_list(self, dept_name, equipment):
        items = []
        dic_param = {'dept_name':dept_name, 'equipment':equipment}

        sql = ''' 
        SELECT 
            e.id
            , e."Code" AS "Code" 
            , e."Name" AS "Name"              
            , e."Description" AS "Description"
            , e."loc_pk" AS "loc_pk"
            , lo."loc_nm" AS "Location"
            , e."Status" AS "Status"
            , e."disposed_type" AS "disposed_type"
            , e."Depart_id" AS "Depart_id"
            , to_char(e."DisposalDate",'yyyy-mm-dd') AS "DisposalDate"
            , to_char(e._created ,'yyyy-MM-dd HH:mm') AS _created 
        FROM 
            equ e       
        LEFT JOIN 
            dept d ON e."Depart_id" = d.id
        LEFT JOIN 
            "location" lo on e.loc_pk = lo.id 
        WHERE 1 = 1  and e."DisposalDate" is not null
        '''
        
        if dept_name:
            sql+='''            
            AND UPPER(d."Name") LIKE CONCAT('%%',UPPER(%(dept_name)s),'%%')
            '''
        if equipment:
            sql+=''' 
            AND UPPER(e."Name") LIKE CONCAT('%%',UPPER(%(equipment)s),'%%')
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equip_obsolete_list', ex)
            raise ex

        return items

    def get_equip_modal(self, keyword, depart_id):
        items = []
        dic_param = {'keyword':keyword, 'depart_id':depart_id}

        sql = ''' 
        SELECT 
            e.id
            , e."Code" AS "Code" 
            , e."Name" AS "Name"              
            , e."Description" AS "Description"            
            , lo."loc_nm" AS "Location"
            , e."Status" AS "Status"            
            , e."Depart_id" AS "Depart_id"
            , to_char(e."DisposalDate",'yyyy-mm-dd') AS "DisposalDate"
            , to_char(e._created ,'yyyy-MM-dd HH:mm') AS _created 
            --, ec."remark" as "EquipCategory"
            , 11 as "EquipCategory"
            , e."ManageNumber"
        FROM 
            equ e       
        LEFT JOIN 
            dept d ON e."Depart_id" = d.id
        LEFT JOIN 
            "location" lo on e.loc_pk = lo.id 
        --left join 
            --"equip_category" ec on ec."equip_category_id" = e."equip_category_id"
        WHERE 1 = 1
        '''
        
        if keyword:
            sql+=''' 
                AND (UPPER(e."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
        	        or UPPER(e."Code") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
        	        or UPPER(e."ManageNumber") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
        )
            '''
        if depart_id:
            sql+=''' 
            AND UPPER(d.id) LIKE CONCAT('%%',UPPER(%(depart_id)s),'%%')
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equip_modal', ex)
            raise ex

        return items

    def get_equipment_detail(self, id):
        sql = ''' 
        select 
            e.id
            , e."Code"
            , e."Name"
            , e."Description"
            , e."Maker"
            , e."Model"
            , e."ManageNumber"
            , e."SerialNumber"
            , e."SupplierName"
            , e."ProductionYear"
            , to_char(e."PurchaseDate",'yyyy-mm-dd') as "PurchaseDate"
            , e."Manager"
            , e."PurchaseCost" 
            , e."ServiceCharger"
            , e."InstallDate"
            , e."DisposalDate"
            , e."OperationRateYN"     
            , e."import_rank"
            , e."Status"
            , CASE WHEN e."environ_equip_yn" = 'Y' THEN 'Y' ELSE 'N' end as environ_equip_yn
            , e."loc_pk"
            , loc."loc_nm"
            , e."Depart_id"
            , e."EquipmentGroup_id"
            , eg."Name" as group_name
            , to_char(e._created ,'yyyy-mm-dd hh24:mi') as _created 
         from equ e
            left join equ_grp eg on e."EquipmentGroup_id" =eg.id         
            left join "location" loc on e.loc_pk = loc.id
            left join "code" c on c."Code" = e."Status" and c."CodeGroupCode" = 'EQU_STATUS'
            left join "code" c2 on c2."Code" = e."import_rank" and c2."CodeGroupCode" = 'IMPORT_RANK'
        where 
            e.id = %(id)s
        '''
        data = {}
        try:
            items = DbUtil.get_rows(sql, {'id':id})
            if len(items)>0:
                data = items[0]
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equipment_list', ex)
            raise ex

        return data

    def get_equipment_runtime(self, runType, date_from, date_to, id):
        items = []
        dc = {}
        
        sql = '''
        select 
            er.id
            , to_char(er."StartDate", 'yyyy-mm-dd') as start_date
            , to_char(er."EndDate", 'yyyy-mm-dd') as end_date
	        , e."Name"
	        , e."Code"
	        , er."StartDate"
	        , to_char(er."StartDate",'HH24:MI') as "StartTime"
	        , er."EndDate"
	        , to_char(er."EndDate",'HH24:MI') as "EndTime"
	        , EXTRACT(day from (er."EndDate" - er."StartDate")) * 60 * 24
	            + EXTRACT(hour from (er."EndDate" - er."StartDate")) * 60 
	            + EXTRACT(min from ("EndDate" - "StartDate")) as "GapTime"
            , er."WorkOrderNumber" 
	        , er."Equipment_id" 
	        , er."RunState" 
            , sc."StopCauseName" 
            , er."Description" 
            , er."StopCause_id"
        from 
            equ_grp eg
        inner join 
            equ e on eg.id = e."EquipmentGroup_id"
        left join 
            equ_run er on e.id = er."Equipment_id"
        left join 
            stop_cause sc on sc.id = er."StopCause_id"
        where 1=1
	        --and er."RunState" = %(runType)s
        '''
        if id:
            sql+=''' and er.id = %(id)s
            '''
        else:
            sql+=''' 
            and er."StartDate" <= %(date_to)s
            and er."EndDate" >= %(date_from)s
            '''

        sql+=''' order by e."Name", er."StartDate", er."EndDate"
            '''
        try:
            dc['id'] = id 
            if date_from and date_to:
                dc['date_from'] = date_from + ' 00:00:00'
                dc['date_to'] = date_to + ' 23:59:59'
            dc['runType'] = runType

            items = DbUtil.get_rows(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equipment_list', ex)
            raise ex

        return items


    def get_equipment_stop_list(self, date_from, date_to, equipment):
        items = []

        sql = '''
        select  
            er.id
            , to_char(er."StartDate", 'yyyy-mm-dd') as start_date
            , to_char(er."EndDate", 'yyyy-mm-dd') as end_date           
	        , e."Name"
	        , e."Code"
	        , er."StartDate"
	        , to_char(er."StartDate",'hh24:mi') as "StartTime"
	        , er."EndDate"
	        , to_char(er."EndDate",'hh24:mi') as "EndTime"
	        , EXTRACT(day from (er."EndDate" - er."StartDate")) * 60 * 24
	            + EXTRACT(hour from (er."EndDate" - er."StartDate")) * 60 
	            + EXTRACT(min from ("EndDate" - "StartDate")) as "GapTime"
            , er."WorkOrderNumber" 
	        , er."Equipment_id" 
	        , er."RunState" 
            , sc."StopCauseName" 
            , er."Description" 
        from 
            equ e 
        inner join 
            equ_run er on e.id = er."Equipment_id"
        left join 
            stop_cause sc on sc.id = er."StopCause_id"
        where 
            er."StartDate" <= %(date_to)s and er."EndDate" >= %(date_from)s
        '''

        if equipment:
            sql += '''
            and er."Equipment_id" = %(equipment)s
            '''

        sql += '''
        and er."RunState" = 'X'
        order by e."Name", er."StartDate", er."EndDate"
        '''
        try:
            dc = {}

            dc['date_from'] = date_from
            dc['date_to'] = date_to + ' 23:59:59'
            dc['equipment'] = equipment
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equipment_stop_list', ex)
            raise ex

        return items


    def get_equipment_stop_info(self, run_pk):
        items = []
 
        sql = '''
        select 
            er.id
            , to_char(er."StartDate", 'yyyy-mm-dd') as start_date
            , to_char(er."EndDate", 'yyyy-mm-dd') as end_date   
	        , e."Name"
	        , e."Code"
	        , er."StartDate"
	        , to_char(er."StartDate",'hh24:mi') as "StartTime"
	        , er."EndDate"
	        , to_char(er."EndDate",'hh24:mi') as "EndTime"
	        , EXTRACT(day from (er."EndDate" - er."StartDate")) * 60 * 24
	            + EXTRACT(hour from (er."EndDate" - er."StartDate")) * 60 
	            + EXTRACT(min from ("EndDate" - "StartDate")) as "GapTime"
            , er."WorkOrderNumber" 
	        , er."Equipment_id" 
	        , er."Description" 
	        , er."RunState" 
            , er."StopCause_id"
            , sc."StopCauseName" 
        from 
            equ e
        inner join 
            equ_run er on e.id = er."Equipment_id"         
        left join 
            stop_cause sc on sc.id = er."StopCause_id"
        where 
            er.id = %(run_pk)s
            and er."RunState" = 'X'
            '''
        try:
            dc = {}

            dc['run_pk'] = run_pk
            items = DbUtil.get_row(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_equipment_stop_info', ex)
            raise ex

        return items

    def get_location_list(self):
        items = []

        sql = ''' 
            select a.id, a.loc_cd, a.loc_nm, a.loc_status, a.plant_yn, a.building_yn, a.spshop_yn
	            ,b."loc_nm" as up_loc_nm
            from "location" a
	            left join "location" b on a.up_loc_pk = b.id
            order by a."_created" desc
        '''     

        try:
            items = DbUtil.get_rows(sql)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_location_list', ex)
            raise ex

        return items

    def get_equip_loc_hist(self):
        items = []

        sql = ''' 
            SELECT 
                equip_loc_hist_pk, equip_pk
                , equip_loc_bef, b.loc_nm as beforeLoc
                , equip_loc_aft, b.loc_nm as afterLoc
                , TO_CHAR(a."_created", 'YYYY-MM-DD') as changeDate
                , a."_creator_name" as changer
            FROM equip_loc_hist a
                left join "location" b on a.equip_loc_bef = b.id
                left join "location" c on a.equip_loc_aft = c.id

        '''     

        try:
            items = DbUtil.get_rows(sql)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_location_list', ex)
            raise ex

        return items

    def get_equip_dept_hist(self):
        items = []

        sql = ''' 
            select equip_dept_hist_pk, equip_pk
	            ,equip_dept_bef, b."Name" as beforeDept
	            ,equip_dept_aft, c."Name" as afterDept
	            , a."_created" as changeDate, a."_creator_name" as changer
            from equip_dept_hist a
    	        left join dept b on a.equip_dept_bef = b.id
    	        left join dept c on a.equip_dept_aft = c.id 

        '''     

        try:
            items = DbUtil.get_rows(sql)
        except Exception as ex:
            LogWriter.add_dblog('error','EquipmentService.get_location_list', ex)
            raise ex

        return items