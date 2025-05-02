from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmExSupplier, CmWorkOrderSupplier

def inspection_report(context):
    '''
    api/kmms/inspection_report   설비전기데이터, 설비진동데이터
    김태영 작업보류

    getDailyElecList
    getElecCheckList
    getDailyElec
    getMaxDailyElecNo
    getMaxDailyElecCrainNo
    getMaxDailyVibNo
    getMaxDailyHighElecNo
    getMaxDailyReportEtcNo
    getMaxDailyEmerElecNo
    insertDailyElec
    updateDailyElec
    deleteCheckList
    insertDailyElecCheckList
    getElecCrainCheckList
    insertDailyElecCrain
    updateDailyElecCrain
    deleteCrainCheckList
    insertDailyElecCrainCheckList
    getDailyElecCrainList
    getDailyElecCrain
    getVibEquipList
    getDailyVib
    getDailyReportVibList
    getDailyVibList
    insertDailyVib
    updateDailyVib
    saveVibration
    getEquipPkByCd
    getUserPkByLoginId
    insertHighElec
    insertHighElecResult
    insertMeasuringPoint
    updateHighElec
    deleteHighElecResult
    deleteMeasuringPoint
    getDailyHighElecList2
    getDailyHighElec
    getDailyHighElecResults
    getMeasuringPoints
    insertEmerElec
    insertEmerElecResult
    updateEmerElec
    deleteEmerElecResult
    getDailyEmerElecList
    getDailyEmerElec
    getDailyEmerElecResults
    insertDailyReportEtc
    getDailyReportEtcList
    getDailyReportEtc
    updateDailyReportEtc
    getDailyReport
    getHighElecReport
    getGreaseLubricantReport
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action in ['findAll', 'countBy']:
            useYn = gparam.get('useYn')
            exSupplierCd = gparam.get('exSupplierCd')
            exSupplierNm = gparam.get('exSupplierNm')
            exSupplierPkNot = gparam.get('exSupplierPkNot')
            searchText = gparam.get('searchText')

            sql = ''' 
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['exSupplierCd'] = exSupplierCd
            dc['exSupplierNm'] = exSupplierNm
            dc['exSupplierPkNot'] = exSupplierPkNot
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            exSupplierPk = CommonUtil.try_int( gparam.get('exSupplierPk') )

            sql = ''' SELECT t.inspection_report_pk
		       , t.inspection_report_nm
		       , t.inspection_report_cd
		       , t.inspection_report_dsc
		       , t.ceo_nm
		       , t.charger_nm
		       , t.business_class_nm
		       , t.nation
		       , t.zip_code
		       , t.address1
		       , t.address2
		       , t.phone
		       , t.fax
		       , t.homepage
		       , t.email_addr
		       , t.use_yn
		       , t.del_yn
		       , t.factory_pk
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		       , t.inserter_nm
		       , t.updater_nm
		    FROM  cm_inspection_report t
		    where t.del_yn = 'N'
            and t.inspection_report_pk = %(exSupplierPk)s
            '''

            dc = {}
            dc['exSupplierPk'] = exSupplierPk

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            id = CommonUtil.try_int(posparam.get('id'))
            exSupplierNm = posparam.get('exSupplierNm')
            chargerNm = posparam.get('chargerNm')
            businessClassNm = posparam.get('businessClassNm')
            exSupplierDsc = posparam.get('exSupplierDsc')
            nation = posparam.get('nation')
            zipCode = posparam.get('zipCode')
            address1 = posparam.get('address1')
            address2 = posparam.get('address2')
            phone = posparam.get('phone')
            fax = posparam.get('fax')
            homepage = posparam.get('homepage')
            emailAddr = posparam.get('emailAddr')
            useYn = posparam.get('useYn')
  
            if id:
                c = CmExSupplier.objects.get(id=id)

            else:
                c = CmExSupplier()

            c.ExSupplierName = exSupplierNm
            c.ChargerName = chargerNm
            c.BusinessClassName = businessClassNm
            c.ExSupplierDsc = exSupplierDsc
            c.Nation = nation
            c.ZipCode = zipCode
            c.Address1 = address1
            c.Address2 = address2
            c.Phone = phone
            c.Fax = fax
            c.Homepage = homepage
            c.EmailAddr = emailAddr
            c.Factory_id = factory_id
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '외부공급처의 정보가 수정되었습니다.'}


        elif action == 'delete':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            CmExSupplier.objects.filter(id=exSupplierPk).delete()

            items = {'success': True}
    

        elif action == 'deleteUpdate':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            c = CmExSupplier.objects.get(id=exSupplierPk)
            c.DelYn = 'Y'
            c.save()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/inspection_report : action-{}'.format(action)
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