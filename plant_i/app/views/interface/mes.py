from app.views import LogWriter
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

        if action=="production_plan":

            start_dt = gparam.get("start_dt").replace('-','')
            end_dt = gparam.get("end_dt").replace('-','')
            line_cd = gparam.get("line_cd")
            product = gparam.get("product")

            dic_res = mes_service.get_production_plan_all(start_dt, end_dt, line_cd, product)

            result["success"] = dic_res["success"]
            items = []
            if dic_res["success"]:
                items = mes_service.convert_to_array(dic_res)
            else:
                result["message"] = dic_res["message"];

            result["success"] = True
            result["items"] = items
            
        elif action=="workorder_list":
            line_cd = gparam.get("line_cd")

            dic_res = mes_service.get_workorder_list(line_cd)

            result["success"] = dic_res["success"]
            items = []
            if dic_res["success"]:
                items = mes_service.convert_to_array(dic_res)
            else:
                result["message"] = dic_res["message"];

            result["success"] = True
            result["items"] = items


        elif action=="active_workorder":
            line_cd  = gparam.get("line_cd")
            items = mes_service.get_active_workorder(line_cd)
            result["success"] = True
            result["items"] = items

        elif action=="lot_history":
            lot= gparam.get('lot')
            result = mes_service.get_lot_history(lot)

        else:
            print(action)
            raise Exception("action error")


    except Exception as e:
        LogWriter.add_dblog("error", source, e)
        result = {'success': False, 'message': str(e)}

    return result



