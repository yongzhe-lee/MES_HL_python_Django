from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmExSupplier, CmWorkOrderSupplier

def ex_supplier(context):
    '''
    api/kmms/ex_supplier    외부공급처?
    김태영 작업중

    findAll 전체목록조회
    findOne 한건조회
    countBy 필요?
    insert
    update
    delete
    deleteUpdate
    findDeletableExSupplier
    findReferencedTablesInfo
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableExSupplier(exSupplierPk):
        q = CmWorkOrderSupplier.objects.filter(CmExSupplier_id=exSupplierPk)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action in ['findAll', 'countBy']:
            useYn = gparam.get('useYn')
            exSupplierCd = gparam.get('exSupplierCd')
            exSupplierNm = gparam.get('exSupplierNm')
            exSupplierPkNot = gparam.get('exSupplierPkNot')
            searchText = gparam.get('searchText')

            sql = ''' SELECT t.ex_supplier_pk
		       , t.ex_supplier_nm
		       , t.ex_supplier_cd
		       , t.ex_supplier_dsc
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
		       , t.factory_pk as site_id
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		       , t.inserter_nm
		       , t.updater_nm
		    FROM  cm_ex_supplier t
		    where t.del_yn = 'N'
            -- AND t.factory_pk = %(factory_id)s
            '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                    '''
            if exSupplierNm:
                sql += ''' AND UPPER(t.ex_supplier_nm) = UPPER(%(exSupplierNm)s)
                '''            
            if exSupplierPkNot:
                sql += ''' AND t.ex_supplier_pk <> %(exSupplierPkNot)s
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
            dc['exSupplierPkNot'] = exSupplierPkNot
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            exSupplierPk = gparam.get('exSupplierPk')

            sql = ''' SELECT t.ex_supplier_pk
		       , t.ex_supplier_nm
		       , t.ex_supplier_cd
		       , t.ex_supplier_dsc
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
		    FROM  cm_ex_supplier t
		    where t.del_yn = 'N'
            and t.ex_supplier_pk = %(exSupplierPk)s
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
            if not findDeletableExSupplier(exSupplierPk):
                CmExSupplier.objects.filter(id=exSupplierPk).delete()

            items = {'success': True}
    

        elif action == 'deleteUpdate':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            c = CmExSupplier.objects.get(id=exSupplierPk)
            c.DelYn = 'Y'
            c.save()

            items = {'success': True}


        elif action == 'findDeletableExSupplier':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            return findDeletableExSupplier(exSupplierPk)


        elif action == 'findReferencedTablesInfo':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
			FROM (
			    select 'workordersupplier.exsupplierpk.lbl' as i18n_code
			    , count(*) as cnt
			    from cm_work_order_supplier
			    where ex_supplier_pk = %(exSupplierPk)s
			) t
			left join cm_i18n t1 on t.i18n_code = t1.lang_code
			where t.cnt > 0
            '''
            dc = {}
            dc['exSupplierPk'] = exSupplierPk

            items = DbUtil.get_row(sql, dc)


    except Exception as ex:
        source = 'kmms/ex_supplier : action-{}'.format(action)
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