from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmSupplier, CmWorkOrderSupplier

def supplier(context):
    '''
    api/kmms/supplier    자재공급처

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
        if action in ['findAll']:
            useYn = gparam.get('useYn')    
            searchText = gparam.get('searchText')

            sql = ''' 
                with cte as (
		        SELECT t.supplier_pk
		               , t.supplier_nm
		               , t.supplier_cd
		               , t.ceo_nm
		               , t.charger_nm
		               , t.business_class_nm
		               , t.supplier_dsc
		               , t.nation
		               , t.zip_code
		               , t.address1
		               , t.address2
		               , t.phone
		               , t.fax
		               , t.homepage
		               , t.email_addr
		               , t.charger_tel
		               , t.charger2_nm
		               , t.charger2_tel
		               , t.comp_type
		               , ct.code_cd as comp_type_cd
		               , ct.code_nm as comp_type_nm
		               , t.local
		               , t.use_yn
		               , t.del_yn
		               , t.insert_ts
		               , t.update_ts
		               , t.inserter_id
		               , t.updater_id
		               , t.inserter_nm
		               , t.updater_nm
		               , t.site_id
		        FROM   cm_supplier t
		        left outer join cm_base_code ct on t.comp_type = ct.code_cd and ct.code_grp_cd = 'COMP_TYPE'
		        where 1=1
            '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                    '''
            if searchText:
                sql += ''' AND ( UPPER(t.supplier_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
                                or UPPER(t.supplier_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''

            sql += ''' 
                        )
		            SELECT *
		            FROM (
			            table cte
	                         order by supplier_nm ASC 

		            ) sub
		            RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		            WHERE total_rows != 0
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc) 
 

        elif action == 'findOne':
            supplierPk = gparam.get('supplierPk')

            sql = ''' 
            
                SELECT t.supplier_pk
		       , t.supplier_nm
		       , t.supplier_cd
		       , t.ceo_nm
		       , t.charger_nm
		       , t.business_class_nm
		       , t.supplier_dsc
		       , t.nation
		       , t.zip_code
		       , t.address1
		       , t.address2
		       , t.phone
		       , t.fax
		       , t.homepage
		       , t.email_addr
		       , t.charger_tel
		       , t.charger2_nm
		       , t.charger2_tel
		       , t.comp_type
		       , ct.code_cd as comp_type_cd
		       , ct.code_nm as comp_type_nm
		       , t.local
		       , t.use_yn
		       , t.del_yn
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		       , t.inserter_nm
		       , t.updater_nm
		       , t.site_id
		    FROM  cm_supplier t
		        left outer join cm_base_code ct on t.comp_type = ct.code_cd and ct.code_grp_cd = 'COMP_TYPE'
		    where t.del_yn = 'N'
                and t.supplier_pk = %(supplierPk)s
            '''

            dc = {}
            dc['supplierPk'] = supplierPk

            items = DbUtil.get_row(sql, dc)


        elif action in ['save']:
            id = CommonUtil.try_int(posparam.get('supplier_pk'))
            supplier_cd = posparam.get('supplier_cd')
            supplier_nm = posparam.get('supplier_nm')
            ceo_nm = posparam.get('ceo_nm')
            phone = posparam.get('phone')
            comp_type = posparam.get('comp_type')
            business_class_nm = posparam.get('business_class_nm')
            nation = posparam.get('nation')
            local = posparam.get('local')
            charger_nm = posparam.get('charger_nm')
            charger_tel = posparam.get('charger_tel')
            charger2_nm = posparam.get('charger2_nm')
            charger2_tel = posparam.get('charger2_tel')
            fax = posparam.get('fax')
            zip_code = posparam.get('zip_code')
            address1 = posparam.get('address1')
            address2 = posparam.get('address2')
            email_addr = posparam.get('email_addr')
            use_yn = posparam.get('use_yn')
  
            if id:
                c = CmSupplier.objects.get(id=id)

            else:
                c = CmSupplier()

            c.SupplierCode = supplier_cd
            c.SupplierName = supplier_nm
            c.CeoName = ceo_nm
            c.Phone = phone
            c.CompType = comp_type
            c.Nation = nation
            c.BusinessClassName = business_class_nm
            c.Local = local
            c.ChargerName = charger_nm
            c.ChargerTel = charger_tel
            c.Charger2Name = charger2_nm
            c.Charger2Tel = charger2_tel        
            c.Fax = fax
            c.ZipCode = zip_code
            c.Address1 = address1
            c.Address2 = address2
            c.EmailAddr = email_addr
            c.UseYn = use_yn
            c.DelYn = 'N'
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '공급처의 정보가 수정되었습니다.'}


        elif action == 'delete':
            supplier_pk = CommonUtil.try_int(posparam.get('supplier_pk'))
            if not findDeletableExSupplier(supplier_pk):
                CmSupplier.objects.filter(id=supplier_pk).delete()

            items = {'success': True}
    

        elif action == 'deleteUpdate':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            c = CmSupplier.objects.get(id=exSupplierPk)
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
        source = 'kmms/supplier : action-{}'.format(action)
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