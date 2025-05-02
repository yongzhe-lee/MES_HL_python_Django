from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmExSupplier, CmWorkOrderSupplier

def mapp_loc_mes(context):
    '''
    api/kmms/mapp_loc_mes    외부업체
    김태영 작업중

    findAll 전체목록조회
    save
    delete
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
 

        

        elif action == 'save':
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

            return {'success': True, 'message': '의 정보가 수정되었습니다.'}


        elif action == 'delete':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            CmExSupplier.objects.filter(id=exSupplierPk).delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/mapp_loc_mes : action-{}'.format(action)
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