import os, json
from domain.services.sql import DbUtil
from domain.services.sap import SapInterfaceService
from domain.models.interface import IFSapMaterial

def sap(context):
    '''
    /api/interface/sap?action=local_mig
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    result = {'success' : True, 'message' : ''}

    sap_service = SapInterfaceService()
    

    action = gparam.get('action')

    if action=="sap_mat":
        sql= '''
        select 
        id, stab_werks, stab_matnr, stab_maktx, stab_groes, stab_matkl, stab_mtart, stab_meins, stab_bklas, stab_bkbez, stab_zctime, stab_price, stab_peinh
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        from if_sap_mat;
        '''
        items = DbUtil.get_rows(sql)

        result['items'] = items

    elif action=="local_mig":
        curr_dir = os.getcwd()
        filepath = curr_dir + '/domain/_sql/if/sap_mat.json'
        with open(filepath, 'r', encoding="utf8") as f:
            filedata = f.read()

        dic_result = json.loads(filedata)
        items = dic_result['rs']['tables']['STAB']
        for item in items:
            if_sap_mat = IFSapMaterial()
            if_sap_mat.stab_maktx = item["MAKTX"]
            if_sap_mat.stab_bklas = item["BKLAS"]
            if_sap_mat.stab_price = item["PRICE"]
            if_sap_mat.stab_werks = item["WERKS"]
            if_sap_mat.stab_mtart = item["MTART"]
            if_sap_mat.stab_peinh = item["PEINH"]
            if_sap_mat.stab_matkl = item["MATKL"]
            if_sap_mat.stab_bkbez = item["BKBEZ"]
            if_sap_mat.stab_groes = item["GROES"]
            if_sap_mat.stab_zctime= item["ZCTIME"]
            if_sap_mat.stab_matnr= item["MATNR"]
            if_sap_mat.set_audit(user)
            if_sap_mat.save()




    elif action=="migration":

        dic_result = sap_service.get_sap_material("","", "Y");
        if dic_result['message']!="OK": return result

        items = dic_result['rs']['tables']['STAB']
        IFSapMaterial.objects.all.delete()
        for item in items:

            if_sap_mat = IFSapMaterial()

            if_sap_mat.stab_maktx = item["MAKTX"]
            if_sap_mat.stab_bklas = item["BKLAS"]
            if_sap_mat.stab_price = item["PRICE"]
            if_sap_mat.stab_werks = item["WERKS"]
            if_sap_mat.stab_mtart = item["MTART"]
            if_sap_mat.stab_peinh = item["PEINH"]
            if_sap_mat.stab_matkl = item["MATKL"]
            if_sap_mat.stab_bkbez = item["BKBEZ"]
            if_sap_mat.stab_groes = item["GROES"]
            if_sap_mat.stab_zctime= item["ZCTIME"]
            if_sap_mat.stab_matnr= item["MATNR"]

            if_sap_mat.set_audit(user)
            if_sap_mat.save()
        

    return result