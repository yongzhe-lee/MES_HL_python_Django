from domain.services.interface.mes import MESInterfaceService

def mes (context):
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action', 'read')

    user  = context.request.user
    source = f'/api/interface/mes?action={action}'
    result = {}

    mes_service = MESInterfaceService()

    try:
        if action=="read":
            pass
        elif action=="production_plan":
            fromDate = gparam.get("fromDate")
            toDate = gparam.get("toDate")
            line = gparam.get("line")
            product = gparam.get("product")
            result = mes_service.get_production_plan_all(fromDate, toDate, line, product)
            
        elif action=="workorder_list":
            line = gparam.get("line")
            result = mes_service.get_workorder_list(line)

        elif action=="active_workorder":
            equ_cd  = gparam.get("equ_cd")
            result = mes_service.get_active_workorder(equ_cd)

            pass
        elif action=="lot_history":
            lot= gparam.get('lot')
            result = mes_service.get_lot_history(lot)
        else:
            print(action)


    except Exception as e:
        result = {'success': False, 'message': str(e)}


    return result



