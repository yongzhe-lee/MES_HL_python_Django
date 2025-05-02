from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipment
#from django.db import transaction

def equipment2(context):
    '''
    api/kmms/equipment2    설비
    김태영 작업중


    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableExSupplier(equipPk):
        q = CmWorkOrderSupplier.objects.filter(CmEquipment_id=equipPk)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action in ['findAll', 'countBy']:
            useYn = gparam.get('useYn')
            exSupplierCd = gparam.get('exSupplierCd')
            exSupplierNm = gparam.get('exSupplierNm')
            equipPkNot = gparam.get('equipPkNot')
            searchText = gparam.get('searchText')

            sql = ''' 
            -- AND t.factory_pk = %(factory_id)s
            '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                    '''
            if exSupplierNm:
                sql += ''' AND UPPER(t.ex_supplier_nm) = UPPER(%(exSupplierNm)s)
                '''            
            if equipPkNot:
                sql += ''' AND t.ex_supplier_pk <> %(equipPkNot)s
                '''
            if searchText:
                sql += ''' AND ( UPPER(t.ex_supplier_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''

            sql += ''' order by t.ex_supplier_nm
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['exSupplierCd'] = exSupplierCd
            dc['exSupplierNm'] = exSupplierNm
            dc['equipPkNot'] = equipPkNot
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            equipPk = gparam.get('equipPk')

            sql = ''' 
            '''

            dc = {}
            dc['equipPk'] = equipPk

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
                c = CmEquipment.objects.get(id=id)

            else:
                c = CmEquipment()

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
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            if not findDeletableExSupplier(equipPk):
                CmEquipment.objects.filter(id=equipPk).delete()

            items = {'success': True}
    

        elif action == 'deleteUpdate':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            c = CmEquipment.objects.get(id=equipPk)
            c.DelYn = 'Y'
            c.save()

            items = {'success': True}


        elif action == 'findDeletableExSupplier':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            return findDeletableExSupplier(equipPk)


        elif action == 'findReferencedTablesInfo':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
			FROM (
			    select 'workordersupplier.exsupplierpk.lbl' as i18n_code
			    , count(*) as cnt
			    from cm_work_order_supplier
			    where ex_supplier_pk = %(equipPk)s
			) t
			left join cm_i18n t1 on t.i18n_code = t1.lang_code
			where t.cnt > 0
            '''
            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_row(sql, dc)


    except Exception as ex:
        source = 'kmms/equipment2 : action-{}'.format(action)
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