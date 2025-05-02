from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmPopInfo

def pop_info(context):
    '''
    api/kmms/pop_info    팝업정보
    김태영 

    findAll
    findOne
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

    try:
        if action == 'findAll':
            currDate = gparam.get('currDate')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')
            searchText = gparam.get('searchText')

            sql = ''' SELECT popup_pk, end_date, file_url, notice_yn
		    , popup_conts, popup_height_loc, popup_height_size
		    , popup_title, popup_type, popup_width_loc, popup_width_size
		    , start_date, stop_view_yn
		    FROM cm_pop_info
		    WHERE notice_yn = 'Y'
            '''
            if searchText:
                sql += ''' AND (  UPPER(popup_title) LIKE CONCAT('%',UPPER(%(searchText)s),'%') )
                '''
            if currDate:
                sql += ''' AND to_date(%(currDate)s, 'YYYY-MM-DD') between start_date and end_date
                '''
            if startDate and endDate:
                sql += ''' AND ((date(start_date) >= to_date(%(startDate)s, 'YYYY-MM-DD')
	    			    AND date(start_date) <= to_date(%(endDate)s, 'YYYY-MM-DD'))
	    		    OR (date(end_date) >= to_date(%(startDate)s, 'YYYY-MM-DD')
	    			    AND date(end_date) <= to_date(%(endDate)s, 'YYYY-MM-DD')))
                '''

            dc = {}
            dc['currDate'] = currDate
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            popupPk = CommonUtil.try_int( gparam.get('popupPk') )

            sql = ''' SELECT popup_pk, end_date, file_url, notice_yn
		    , popup_conts, popup_height_loc, popup_height_size
		    , popup_title, popup_type, popup_width_loc, popup_width_size
		    , start_date, stop_view_yn
		    FROM cm_pop_info
		    WHERE notice_yn = 'Y'
            AND popup_pk = #{popupPk}
            '''

            dc = {}
            dc['popupPk'] = popupPk

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            popupPk = CommonUtil.try_int(posparam.get('popupPk'))
            popupHeightSize = CommonUtil.try_int(posparam.get('popupHeightSize'))
            popupWidthSize = CommonUtil.try_int(posparam.get('popupWidthSize'))
            endDate = posparam.get('endDate')
            fileUrl = posparam.get('fileUrl')
            noticeYn = posparam.get('noticeYn')
            popupConts = posparam.get('popupConts')
            popupHeightLoc = posparam.get('popupHeightLoc')
            popupTitle = posparam.get('popupTitle')
            popupType = posparam.get('popupType')
            popupWidthLoc = posparam.get('popupWidthLoc')
            startDate = posparam.get('startDate')
            stopViewYn = posparam.get('stopViewYn')
  
            if action == 'update':
                c = CmPopInfo.objects.get(id=popupPk)

            else:
                c = CmPopInfo()

            c.ExSupplierName = endDate
            c.ChargerName = fileUrl
            c.ChargerName = noticeYn
            c.ChargerName = popupConts
            c.ChargerName = popupHeightLoc
            c.ChargerName = popupHeightSize
            c.ChargerName = popupTitle
            c.ChargerName = popupType
            c.ChargerName = popupWidthLoc
            c.ChargerName = popupWidthSize
            c.ChargerName = startDate
            c.ChargerName = stopViewYn

            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '팝업정보가 수정되었습니다.'}


        elif action == 'delete':
            popupPk = CommonUtil.try_int(posparam.get('popupPk'))
            CmPopInfo.objects.filter(id=popupPk).delete()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/pop_info : action-{}'.format(action)
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