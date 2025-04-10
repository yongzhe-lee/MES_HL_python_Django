from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmBaseCode, CmMaterial, CmEquipment, CmEquipChkItem, CmEquipChkItemMst
from symbol import factor
#from django.db import transaction

def base_code(context):
    '''
    api/kmms/base_code    외부공급처?
    김태영 작업중

    findAll
    findOne
    countBy
    insert
    update
    delete
    selectStatement
    findAll
    exists
    findOne
    searchOne
    findDeletableBaseCodeMtrlClass
    findDeletableBaseCodeDisposedType
    findDeletableBaseCodeAmtUnit
    findDeletableBaseCodeChkItemUnit
    findReferencedTablesMasterCode
    findReferencedTablesInfoByCodeCd
    findReferencedTablesInfoByCodeGrpCd
    equipStatus
    getInoutTypeList
    deleteBy
    insert
    update
    delete
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableBaseCodeMtrlClass(codePk):
        q = CmMaterial.objects.filter(MtrlClassCodePk=codePk)
        if q.first():
            return 1
        else:
            return 0

    def findDeletableBaseCodeDisposedType(codeCd):
        q = CmEquipment.objects.filter(DisposedType=codeCd)
        if q.first():
            return 1
        else:
            return 0

    def findDeletableBaseCodeAmtUnit(codePk):
        q = CmMaterial.objects.filter(AmtUnitPk=codePk)
        if q.first():
            return 1
        else:
            return 0

    def findDeletableBaseCodeChkItemUnit(codePk):
        q = CmEquipChkItem.objects.filter(ChkItemUnitPk=codePk)
        if q.first():
            return 1
        else:
            q = CmEquipChkItemMst.objects.filter(ChkItemUnitPk=codePk)
            if q.first():
                return 1
            else:
                return 0

    try:
        if action in ['findAll', 'searchOne', 'countBy']:
            codeGrpCd = gparam.get('codeGrpCd')
            editYn = gparam.get('editYn')
            useYn = gparam.get('useYn')
            codeNm = gparam.get('codeNm')
            codeCd = gparam.get('codeCd')
            grpCd = gparam.get('grpCd')
            exCodes = gparam.get('exCodes')
            searchText = gparam.get('searchText')

            sql = ''' SELECT t.code_pk
		       , t.code_grp_cd
		       , tg.code_grp_nm
		       , tg.code_grp_dsc
		       , tg.edit_yn
		       	, concat('[', t.code_cd, '] ', t.code_nm) as code_nm
		       	, t.code_nm
		       , t.code_cd
		       , t.code_dsc
		       , t.disp_order
		       , t.use_yn
		       , t.code_nm_en
		       , t.code_nm_ch
		       , t.code_nm_jp
		       , t.grp_cd
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		       , t.inserter_nm
		       , t.updater_nm
				, t.attr1
		    FROM cm_base_code t
		    INNER JOIN cm_base_code_grp tg ON t.code_grp_cd = tg.code_grp_cd
            where 1=1
            '''
            if codeGrpCd:
                sql += ''' AND upper(t.code_grp_cd) = upper(%(codeGrpCd)s)
                    '''
            if editYn:
                sql += ''' AND tg.edit_yn = %(editYn)s
                '''            
            if useYn:
                sql += ''' AND t.use_yn = %(useYn)s
                '''
            if codeNm:
                sql += ''' AND upper(t.t.code_nm) = upper(%(codeNm)s)
                '''
            if grpCd:
                sql += ''' AND upper(t.t.grp_cd) = upper(%(grpCd)s)
                '''
            if exCodes:
                exCodes2 = CommonUtil.convert_quotation_mark_string(exCodes)
                sql += ''' AND t.code_cd not in ( ''' + exCodes2 + ''')
                '''
            if searchText:
                sql += ''' AND (
				UPPER(coalesce(t.code_nm,'')) LIKE CONCAT('%',UPPER(#{searchText}),'%')
    			OR UPPER(coalesce(t.code_cd,'')) LIKE CONCAT('%',UPPER(#{searchText}),'%')
   			)
                '''

            sql += ''' order by t.code_grp_cd, t.code_cd
            '''

            dc = {}
            dc['codeGrpCd'] = codeGrpCd
            dc['editYn'] = editYn
            dc['useYn'] = useYn
            dc['codeNm'] = codeNm
            dc['grpCd'] = grpCd
            dc['searchText'] = searchText

            if action == 'searchOne':
                items = DbUtil.get_row(sql, dc)
            else:
                items = DbUtil.get_rows(sql, dc)

            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            codePk = gparam.get('codePk')

            sql = ''' SELECT t.code_pk
		       , t.code_grp_cd
		       , tg.code_grp_nm
		       , tg.code_grp_dsc
		       , tg.edit_yn
		       	, concat('[', t.code_cd, '] ', t.code_nm) as code_nm
		       	, t.code_nm
		       , t.code_cd
		       , t.code_dsc
		       , t.disp_order
		       , t.use_yn
		       , t.code_nm_en
		       , t.code_nm_ch
		       , t.code_nm_jp
		       , t.grp_cd
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		       , t.inserter_nm
		       , t.updater_nm
				, t.attr1
		    FROM cm_base_code t
		    INNER JOIN cm_base_code_grp tg ON t.code_grp_cd = tg.code_grp_cd
            WHERE t.code_pk = #{codePk}
            '''

            dc = {}
            dc['codePk'] = codePk

            items = DbUtil.get_row(sql, dc)

        elif action == 'exists':
            codeGrpCd = gparam.get('codeGrpCd')
            codeCd = gparam.get('codeCd')
            codePk = CommonUtil.try_int(gparam.get('codePk'))

            sql = ''' select count(*) as cnt
		    FROM cm_base_code
		    WHERE UPPER(code_grp_cd) = UPPER('%(codeGrpCd)s)
		    AND UPPER(code_cd) = UPPER(%(codeCd)s)
            '''
            if codePk:
                sql += ''' and t.code_pk = %(codePk)s
                '''

            dc = {}
            dc['codeGrpCd'] = codeGrpCd
            dc['codeCd'] = codeCd
            dc['codePk'] = codePk

            items = DbUtil.get_row(sql, dc)

        elif action in ['insert', 'update']:
            codePk = CommonUtil.try_int(gparam.get('codePk'))
            codeGrpCd = posparam.get('codeGrpCd')
            codeNm = posparam.get('codeNm')
            codeCd = posparam.get('codeCd')
            codeDsc = posparam.get('codeDsc')
            dispOrder = posparam.get('dispOrder')
            useYn = posparam.get('useYn')
            codeNmEn = posparam.get('codeNmEn')
            codeNmCh = posparam.get('codeNmCh')
            codeNmJp = posparam.get('codeNmJp')
            grpCd = posparam.get('grpCd')
  
            if action == 'update':
                c = CmBaseCode.objects.get(id=codePk)

            else:
                c = CmBaseCode()

            c.CmBaseCodeGroup_id = codeGrpCd
            c.CodeName = codeNm
            c.CodeCd = codeCd
            c.CodeDsc = codeDsc
            c.DispOrder = dispOrder
            c.UseYn = useYn
            c.CodeNameEn = codeNmEn
            c.CodeNameCh = codeNmCh
            c.CodeNameJp = codeNmJp
            c.GroupCode = grpCd
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '기초코드의 정보가 수정되었습니다.'}

        elif action == 'delete':
            codePk = CommonUtil.try_int(gparam.get('codePk'))

            q = CmBaseCode.objects.filter(CmBaseCodeGroup_id=codeGrpCd)
            q = q.exclude(CodeCd__in=codeCd_list)
            q.delete()

            items = {'success': True}

        elif action == 'deleteBy':
            codeGrpCd = posparam.get('codeGrpCd')
            codePks = posparam.get('codePks')
            codeCd_list = codePks.split(',')

            q = CmBaseCode.objects.filter(id=codePk)
            q.delete()

            items = {'success': True}
    
        elif action == 'findDeletableBaseCodeMtrlClass':
            codePk = CommonUtil.try_int(posparam.get('codePk'))
            return findDeletableBaseCodeMtrlClass(codePk)

        elif action == 'findDeletableBaseCodeDisposedType':
            codeCd = posparam.get('codeCd')
            return findDeletableBaseCodeDisposedType(codeCd)

        elif action == 'findDeletableBaseCodeAmtUnit':
            codePk = CommonUtil.try_int(posparam.get('codePk'))
            return findDeletableBaseCodeAmtUnit(codePk)

        elif action == 'findDeletableBaseCodeChkItemUnit':
            codePk = CommonUtil.try_int(posparam.get('codePk'))
            return findDeletableBaseCodeChkItemUnit(codePk)

        elif action == 'findReferencedTablesMasterCode':
            codeGrpCd = posparam.get('codeGrpCd')
            codeCd = posparam.get('codeCd')
            codeCd = posparam.get('codeCd')

            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
			FROM (
					select 'material.mtrlclasscdpk.lbl' as i18n_code, count(*) as cnt 
					from cm_material
					where mtrl_class_cd_pk = %(code_pk)s
					AND upper('MTRL_CLASS') = upper(%(codeGrpCd)s) 
					AND del_yn = 'N'
					union all
					select 'equipment.disposedtype.lbl' as i18n_code, count(*) as cnt 
					from cm_equipment
					where disposed_type = %(codeCd)s
					AND upper('DISPOSE_TYPE') = upper(%(codeGrpCd)s) 
					AND del_yn = 'N'
					union all
					select 'material.amtunitpk.lbl' as i18n_code, count(*) as cnt 
					from cm_MATERIAL
					where amt_unit_pk = %(code_pk)s
					AND upper('AMT_UNIT') =upper(%(codeGrpCd)s)
					AND del_yn = 'N'
					union all
					select 'equipchkitem.chkitemunitpk.lbl' as i18n_code, count(*) as cnt 
					from cm_equip_chk_item
					where chk_item_unit_pk = %(code_pk)s
					AND upper('CHK_ITEM_UNIT') = upper(%(codeGrpCd)s)
					union all
					select 'equipchkitemmst.chkitemunitpk.lbl' as i18n_code, count(*) as cnt 
					from cm_equip_chk_item_mst
					where chk_item_unit_pk = %(code_pk)s
					AND upper('CHK_ITEM_UNIT') = upper(%(codeGrpCd)s)
			) t
			left join cm_i18n t1 on t.i18n_code = t1.lang_code
			where t.cnt > 0
            '''
            dc = {}
            dc['codeGrpCd'] = codeGrpCd
            dc['codeCd'] = codeCd
            dc['codePk'] = codePk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'findReferencedTablesInfoByCodeCd':
            codeGrpCd = posparam.get('codeGrpCd')
            codeCd = posparam.get('codeCd')

            sql = ''' select t.i18n_code
			, coalesce(t1.def_msg, (select code_grp_nm 
            from cm_base_code_grp 
            where code_grp_cd = upper(%(codeGrpCd)s) limit 1)) AS def_msg
			, t.cnt
			FROM (
				select 'mtrlinout.abgrade.lbl' as i18n_code, count(*) as cnt 
				from cm_mtrl_inout
				where ab_grade = %(codeCd)s
                AND 'AB_GRADE' = %(codeGrpCd)s
				union all
				select 'pinvlocmtrl.abgrade.lbl' as i18n_code, count(*) as cnt 
                from cm_pinv_loc_mtrl
				where ab_grade = %(codeCd)s
                AND 'AB_GRADE' = %(codeGrpCd)s
				union all
				select 'alarmactn.actntype.lbl' as i18n_code, count(*) as cnt 
                from cm_alarm_actn
				where actn_type = %(codeCd)s
                AND 'ACTION_TYPE' = %(codeGrpCd)s
				union all
				select 'alarm.alarmack.lbl' as i18n_code, count(*) as cnt 
                from cm_alarm
				where alarm_ack = %(codeCd)s
                AND 'ALARM_ACK' = %(codeGrpCd)s
				union all
				select 'alarmactn.alarmcause.lbl' as i18n_code, count(*) as cnt 
                from cm_alarm_actn
				where alarm_cause = %(codeCd)s
                AND 'ALARM_CAUSE' = %(codeGrpCd)s
				union all
				select 'tagmeastype.alarmdisptype.lbl' as i18n_code, count(*) as cnt 
                from cm_tag_meas_type
				where alarm_disp_type = %(codeCd)s
                AND 'ALARM_DISP_TYPE' = %(codeGrpCd)s
				union all
				select 'alarm.alarmstatus.lbl' as i18n_code, count(*) as cnt 
                from cm_alarm
				where alarm_status = %(codeCd)s
                AND 'ALARM_STATUS' = %(codeGrpCd)s
				union all
				select 'alarm.alarmtype.lbl' as i18n_code, count(*) as cnt 
                from cm_alarm
				where alarm_type = %(codeCd)s
                AND 'ALARM_TYPE' = %(codeGrpCd)s
				union all
				select 'combbsmaster.bbsattrbcd.lbl' as i18n_code, count(*) as cnt 
                from cm_COM_BBS_MASTER
				where BBS_ATTRB_CD = %(codeCd)s
                AND 'BBS_ATTR' = %(codeGrpCd)s AND del_yn = 'N'
				union all
				select 'combbsmaster.bbstypecd.lbl' as i18n_code, count(*) as cnt 
                from cm_COM_BBS_MASTER
				where BBS_TY_CD = %(codeCd)s
                AND 'BBS_TYPE' = %(codeGrpCd)s 
                AND del_yn = 'N'
				union all
				select 'equipchksche.chkstatus.lbl' as i18n_code, count(*) as cnt 
                from cm_EQUIP_CHK_SCHE
				where CHK_STATUS = %(codeCd)s
                AND 'CHK_STATUS' = %(codeGrpCd)s
				union all
				select 'supplier.comptype.lbl' as i18n_code, count(*) as cnt 
                from cm_supplier
				where comp_type = %(codeCd)s
                AND 'COMP_TYPE' = %(codeGrpCd)s
				union all
				select 'equipchkmast.cycletype.lbl' as i18n_code, count(*) as cnt 
                from cm_EQUIP_CHK_MAST
				where CYCLE_TYPE = %(codeCd)s
                AND 'CYCLE_TYPE' = %(codeGrpCd)s 
                AND del_yn = 'N'
				union all
				select 'pm.cycletype.lbl' as i18n_code, count(*) as cnt from PM
				where CYCLE_TYPE = %(codeCd)s
                AND 'CYCLE_TYPE' = %(codeGrpCd)s 
                AND del_yn = 'N'
				-- union all
				-- select 'sysopt.inspcycletype.lbl' as i18n_code, count(*) as cnt 
                -- from cm_sys_opt
				-- where insp_sche_cycle_type = %(codeCd)s
                -- AND 'CYCLE_TYPE' = %(codeGrpCd)s
				-- union all
				-- select 'sysopt.pmcycletype.lbl' as i18n_code, count(*) as cnt 
                -- from cm_sys_opt
				-- where pm_sche_cycle_type = %(codeCd)s
                -- AND 'CYCLE_TYPE' = %(codeGrpCd)s
				union all
				select 'equipment.equipstatus.lbl' as i18n_code, count(*) as cnt 
                from cm_EQUIPMENT
				where equip_status = %(codeCd)s
                AND 'EQUIP_STATUS' = %(codeGrpCd)s AND del_yn = 'N'
				union all
				select 'labelrptform.formkinds.lbl' as i18n_code, count(*) as cnt 
                from cm_label_rpt_form
				where form_kinds = %(codeCd)s
                AND 'FORM_KINDS' = %(codeGrpCd)s
				union all
				select 'helpitem.helpitemtype.lbl' as i18n_code, count(*) as cnt 
                from cm_HELP_ITEM
				where HELP_ITEM_TYPE = %(codeCd)s
                AND 'HELP_ITEM_TYPE' = %(codeGrpCd)s
				union all
				select 'helpitem.helpitemclass.lbl' as i18n_code, count(*) as cnt 
                from cm_HELP_ITEM
				where HELP_ITEM_CLASS = %(codeCd)s
                AND 'HELP_ITEM_CLASS' = %(codeGrpCd)s 
                AND del_yn = 'N'
				union all
				select 'mtrlinout.intype.lbl' as i18n_code, count(*) as cnt 
                from cm_MTRL_INOUT
				where inout_type = %(codeCd)s
                AND 'IN_TYPE' = %(codeGrpCd)s
				union all
				select 'mtrlinout.outtype.lbl' as i18n_code, count(*) as cnt 
                from cm_MTRL_INOUT
				where inout_type = %(codeCd)s
                AND 'OUT_TYPE' = %(codeGrpCd)s
				union all
				select 'mtrlinout.inoutdiv.lbl' as i18n_code, count(*) as cnt 
                from cm_MTRL_INOUT
				where inout_div = %(codeCd)s
                AND 'INOUT_DIV' = %(codeGrpCd)s
				union all
				select 'workorder.maintypecd.lbl' as i18n_code, count(*) as cnt 
                from cm_WORK_ORDER
				where maint_type_cd = %(codeCd)s
                AND 'MAINT_TYPE' = %(codeGrpCd)s
				union all
				select 'tag.meassensor.lbl' as i18n_code, count(*) as cnt 
                from cm_tag
				where meas_sensor = %(codeCd)s
                AND 'MEAS_SENSOR' = %(codeGrpCd)s
				union all
				select 'alarmnotigrp.notigrptype.lbl' as i18n_code, count(*) as cnt 
                from cm_alarm_noti_grp
				where noti_grp_type = %(codeCd)s
                AND 'NOTI_GRP_TYPE' = %(codeGrpCd)s
				union all
				select 'anotimailhist.resulttype.lbl' as i18n_code, count(*) as cnt 
                from cm_anoti_mail_hist
				where result_type = %(codeCd)s
                AND 'NOTI_RESULT_TYPE' = %(codeGrpCd)s
				union all
				select 'anotismshist.resulttype.lbl' as i18n_code, count(*) as cnt 
                from cm_anoti_sms_hist
				where result_type = %(codeCd)s
                AND 'NOTI_RESULT_TYPE' = %(codeGrpCd)s
				union all
				select 'basecode.pinvlocstatus.lbl' as i18n_code, count(*) as cnt 
                from cm_pinv_loc
				where pinv_loc_status = %(codeCd)s
                AND 'PINV_LOC_STATUS' = %(codeGrpCd)s 
                AND del_yn = 'N'
				union all
				select 'pm.pmtype.lbl' as i18n_code, count(*) as cnt 
                from cm_PM
				where PM_TYPE = %(codeCd)s
                AND 'PM_TYPE' = %(codeGrpCd)s 
                AND del_yn = 'N'
				union all
				select 'labelrptform.srcconts.lbl' as i18n_code, count(*) as cnt 
                from cm_label_rpt_form
				where src_conts = %(codeCd)s
                AND 'SRC_CONTS' = %(codeGrpCd)s
				union all
				select 'tag.srcsystem.lbl' as i18n_code, count(*) as cnt 
                from cm_tag
				where src_system = %(codeCd)s
                AND 'SRC_SYSTEM' = %(codeGrpCd)s
				union all
				select 'workorder.wostatus.lbl' as i18n_code, count(*) as cnt 
                from cm_WORK_ORDER
				where wo_status = %(codeCd)s
                AND 'WO_STATUS' = %(codeGrpCd)s
				union all
				select 'workorder.worksrccd.lbl' as i18n_code, count(*) as cnt 
                from cm_work_order
				where work_src_cd = %(codeCd)s
                AND 'WORK_SRC' = %(codeGrpCd)s
				union all
				select 'basecode.nodel.msg.lbl' as i18n_code, 1 as cnt
				where %(codeGrpCd)s IN ('LOGIN_LOG_TYPE', 'MAIL_STATUS', 'MTRL_STOCK_COND'
				 , 'PERIOD_TYPE', 'PRICE_TYPE', 'REQUEST_STATUS', 'REQUEST_TYPE'
				 , 'USER_TYPE', 'WEEK_TYPE', 'WO_STATUS_VIEW', 'WO_TYPE')
			) t
			left join cm_i18n t1 on t.i18n_code = t1.lang_code
			where t.cnt > 0
            '''
            dc = {}
            dc['codeGrpCd'] = codeGrpCd
            dc['codeCd'] = codeCd

            items = DbUtil.get_rows(sql, dc)

        elif action == 'findReferencedTablesInfoByCodeGrpCd':
            codeGrpCd = posparam.get('codeGrpCd')
            codeCd = posparam.get('codeCd')


            dc = {}
            dc['codeGrpCd'] = codeGrpCd
            dc['codeCd'] = codeCd

            items = DbUtil.get_rows(sql, dc)

        elif action == 'equipStatus':
            sql = ''' SELECT t.code_pk
		       , t.code_grp_cd
		       , tg.code_grp_nm
		       , tg.code_grp_dsc
		       , tg.edit_yn
		       	, concat('[', t.code_cd, '] ', t.code_nm) as code_nm
		       	, t.code_nm
		       , t.code_cd
		       , t.code_dsc
		       , t.disp_order
		       , t.use_yn
		       , t.code_nm_en
		       , t.code_nm_ch
		       , t.code_nm_jp
		       , t.grp_cd
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		       , t.inserter_nm
		       , t.updater_nm
				, t.attr1
		    FROM cm_base_code t
		    INNER JOIN cm_base_code_grp tg ON t.code_grp_cd = tg.code_grp_cd
            where t.use_yn = 'Y'
		    and t.code_grp_cd  = 'EQUIP_STATUS'
		    and t.code_cd not in ('ES_BKDN','ES_DISP')
            '''
            items = DbUtil.get_rows(sql)

        elif action == 'getInoutTypeList':
            sql = ''' SELECT t.code_pk
		       , t.code_grp_cd
		       , tg.code_grp_nm
		       , tg.code_grp_dsc
		       , tg.edit_yn
		       	, concat('[', t.code_cd, '] ', t.code_nm) as code_nm
		       	, t.code_nm
		       , t.code_cd
		       , t.code_dsc
		       , t.disp_order
		       , t.use_yn
		       , t.code_nm_en
		       , t.code_nm_ch
		       , t.code_nm_jp
		       , t.grp_cd
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		       , t.inserter_nm
		       , t.updater_nm
				, t.attr1
		    FROM cm_base_code t
		    INNER JOIN cm_base_code_grp tg ON t.code_grp_cd = tg.code_grp_cd
            where t.use_yn = 'Y'
		    and t.code_grp_cd in ('IN_TYPE', 'OUT_TYPE')
            '''
            items = DbUtil.get_rows(sql)

    except Exception as ex:
        source = 'kmms/base_code : action-{}'.format(action)
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