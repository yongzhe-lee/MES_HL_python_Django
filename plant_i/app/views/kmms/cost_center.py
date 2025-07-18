from django import db
from domain.models.user import Depart
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmCostCenter, CmEquipment

def cost_center(context):
    '''
    api/kmms/cost_center    코스트센터
    김태영 

    findAll
    findOne
    findDeletable
    countBy
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

    def findDeletableCostCenter(ccenterCd):
        q = CmEquipment.objects.filter(CcenterCode=ccenterCd)
        if q.first():
            return 1
        q = Depart.objects.filter(CcenterCode=ccenterCd)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action == 'findAll':
            useYn = gparam.get('useYn')
            searchText = gparam.get('searchText')

            sql = ''' SELECT ccenter_cd, ccenter_nm, remark
		    , insert_ts, inserter_id, inserter_nm
		    , update_ts, updater_id, updater_nm
		    , use_yn
		    FROM cm_cost_center t
    	    where 1 = 1
            '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                    '''
            if searchText:
                sql += ''' AND (
				    UPPER(ccenter_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
    			    OR
    			    UPPER(ccenter_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''

            sql += ''' order by t.ccenter_nm
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 
        elif action == 'countBy':
            ccenterCd = gparam.get('ccenterCd')

            sql = ''' select count(*) as cnt
		    from cost_center
		    WHERE  ccenter_cd = %(ccenterCd)s
            '''

            dc = {}
            dc['ccenterCd'] = ccenterCd

            row = DbUtil.get_row(sql, dc)
            return row['cnt']


        elif action == 'findOne':
            ccenterCd = gparam.get('ccenterCd')

            sql = ''' SELECT ccenter_cd, ccenter_nm, remark
		    , insert_ts, inserter_id, inserter_nm
		    , update_ts, updater_id, updater_nm
		    , use_yn
		    FROM cm_cost_center t
    	    where ccenter_cd = %(ccenterCd)s
            '''

            dc = {}
            dc['ccenterCd'] = ccenterCd

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            id = CommonUtil.try_int(posparam.get('id'))
            ccenterCd = posparam.get('ccenterCd')
            ccenterNm = posparam.get('ccenterNm')
            remark = posparam.get('remark')
            useYn = posparam.get('useYn')
  
            if action == 'update':
                c = CmCostCenter.objects.get(id=ccenterCd)
            else:
                c = CmCostCenter()

            c.CcenterCode = ccenterCd
            c.CcenterName = ccenterNm
            c.Remark = remark
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '코스트센터 정보가 수정되었습니다.'}


        elif action == 'delete':
            ccenterCd = posparam.get('ccenterCd')
            if not findDeletableCostCenter(ccenterCd):
                CmCostCenter.objects.filter(id=ccenterCd).delete()

            items = {'success': True}
    


        elif action == 'findDeletableCostCenter':
            ccenterCd = posparam.get('ccenterCd')
            return findDeletableCostCenter(ccenterCd)

   
    except Exception as ex:
        source = 'kmms/cost_center : action-{}'.format(action)
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