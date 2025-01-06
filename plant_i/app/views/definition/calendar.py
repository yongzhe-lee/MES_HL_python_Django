
# from domain.models.definition import TagMaster
from domain.models.system import Calendar
# from domain.models.definition import MaterialOrder
from domain.services.logging import LogWriter
from domain.services.definition.meeting_calendar import CalendarService


def calendar(context):
    '''
    /api/definition/calendar
    '''
    items=[]
    posparam = context.posparam
    gparam = context.gparam
    
    action = gparam.get('action', 'read')
    request = context.request
    work_calendar = CalendarService()

    try:
        if action == 'read':
            year_month = gparam.get('year_month')
            items = work_calendar.get_calendar_list(year_month)
        elif action == 'save':
            id = posparam.get('_id')
            # if 'mo' in id:
            #     id = id.replace("mo", "",1)
            #     materialOrder = MaterialOrder.objects.get(id=id)
            #     materialOrder.Description = posparam.get('description')
            #     materialOrder.save()
            #     items = materialOrder.id
            # elif id:
            if id:
                calendar = Calendar.objects.get(id=id)
                calendar.StartTime =  posparam.get('startTime')
                calendar.EndTime = posparam.get('endTime')
                calendar.Color = posparam.get('color')
                calendar.Title = posparam.get('title')
                calendar.Description = posparam.get('description')
                calendar.set_audit(request.user)
                calendar.save()
                items = calendar.id
            else:
                calendar = Calendar()
                calendar.DataDate = posparam.get('datadate')
                calendar.StartTime =  posparam.get('startTime')
                calendar.EndTime = posparam.get('endTime')
                calendar.Title = posparam.get('title')
                calendar.Color = posparam.get('color')
                calendar.Description = posparam.get('description')
                calendar.set_audit(request.user)
                calendar.save()
                items = calendar.id
        elif action == 'delete':
            id = posparam.get('_id')

            if id:
                calendar = Calendar.objects.get(id=id)
                calendar.delete()

    except Exception as ex:
        source = 'calendar : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex

    return items