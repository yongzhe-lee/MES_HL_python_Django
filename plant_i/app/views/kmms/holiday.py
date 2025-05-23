from django import db
from domain.services.kmms.holiday import HolidayService
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmHolidayCustom

def holiday(context):
    '''
    api/kmms/holiday    휴일정보
    '''
    items = []
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    action = gparam.get('action', 'read')

    holiday_service = HolidayService()

    try:
        if action == 'findAll':
            keyword = gparam.get('keyword', None)
            year = gparam.get('year', None)

            items = holiday_service.findAll(keyword, year)

        elif action == 'save':
            id = CommonUtil.try_int(posparam.get('id'), 0)
            NameVal = posparam.get('name')
            YearVal = posparam.get('holiday_year')
            MonthVal = posparam.get('holiday_month')
            DayVal = posparam.get('holiday_day')
            RepeatYn = posparam.get('repeat_yn')

            if id:
                holiday = CmHolidayCustom.objects.get(id=id)
            else:
                holiday = CmHolidayCustom()

            holiday.NationCode = 'ko'
            holiday.NameVal = NameVal
            holiday.YearVal = YearVal
            holiday.MonthVal = MonthVal
            holiday.DayVal = DayVal
            holiday.RepeatYn = RepeatYn
            holiday.set_audit(user)

            holiday.save()

            items = {'success':True, 'message':'휴일 정보가 저장되었습니다.'}

        elif action=='delete':
            try:
                id = posparam.get('id','')
                CmHolidayCustom.objects.filter(id=id).delete()
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

        elif action == 'findAllHolidayInfoRes':
            items = holiday_service.findAllHolidayInfoRes()

        if action == 'findAllHolidayCustom':
            items = holiday_service.findAllHolidayCustom()

    except Exception as ex:
        source = 'kmms/import_rank : action-{}'.format(action)
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
