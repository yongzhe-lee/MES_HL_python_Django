import os, json
from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.interface.sap import SapInterfaceService

from domain.models.interface import IFSapBOM, IFSapMaterial, IFSapMaterialStock, IFSapPcbRandomNumber

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

        matkl = gparam.get('matkl')
        mtart = gparam.get('mtart')
        bklas = gparam.get('bklas')

        dic_param = {'matkl':matkl, 'mtart':mtart,'bklas':bklas}

        sql= '''
        select 
        id, stab_werks, stab_matnr, stab_maktx, stab_groes, stab_matkl, stab_mtart, stab_meins, stab_bklas, stab_bkbez, stab_zctime, stab_price, stab_peinh
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        , to_char(_created, 'yyyy-mm-dd hh24:mi:ss') as created
        from if_sap_mat
        where 1=1
        '''
        if matkl:
            sql+='''
            and stab_matkl = %(matkl)s
            '''

        if mtart:
            sql+='''
            and stab_mtart = %(mtart)s
            '''

        if bklas:
            sql+='''
            and stab_bklas = %(bklas)s
            '''
        #and upper(matkl) like concat('%%', UPPER(%(matkl)s),'%%')

        sql+='''
        order by stab_maktx asc
        '''
        items = DbUtil.get_rows(sql, dic_param)
        result['items'] = items

    elif action=="sap_bom":

        sql= '''
        select 
        id, stab_werks, stab_matnr, stab_revlv, stab_bmeng, stab_idnrk, stab_mnglg, stab_meins, stab_stufe, stab_datuv, stab_datab, stab_aennr, stab_bklas, stab_bkbez
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        , to_char(_created, 'yyyy-mm-dd hh24:mi:ss') as created
        from if_sap_bom
        '''
        items = DbUtil.get_rows(sql)
        result['items'] = items


    elif action=="sap_stock":

        mat_cd = gparam.get('mat_cd')
        location_cd = gparam.get('location_cd')
        sql = '''
        select 
        id, stab_werks, stab_matnr, stab_maktx, stab_lgort, stab_lgobe, stab_labst
        , stab_insme, stab_speme, stab_mslbq, stab_mkolq, stab_mskuq, stab_meins
        , stab_bklas, stab_bkbez
        , data_date
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        , to_char(_created, 'yyyy-mm-dd hh24:mi:ss') as created
        from if_sap_mat_stock
        where 1=1
        '''
        if mat_cd:
            sql+='''
            and stab_matnr=%(mat_cd)s
            '''
        if location_cd:
            sql+='''
            and stab_lgort=%(stab_lgort)s
            '''
        sql+='''
        order by stab_maktx asc
        '''

        items = DbUtil.get_rows(sql)
        result['items'] = items

    elif action=="search_pcb_random_db":
        rnd_num = gparam.get("rnd_num")

        if not rnd_num :
            result["message"] = 'PCB 난수번호가 입력되지 않았습니다.'
            result['success'] = False
            return result

        sql = '''
        select 
        id, stab_mblnr, stab_zeile, stab_matnr, stab_maktx, stab_menge, stab_abqty, stab_meins, rnd_num
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        from if_sap_pcb_ran
        where rnd_num = %(rnd_num)s
        order by stab_mblnr
        '''

        items = DbUtil.get_rows(sql, {"rnd_num" : rnd_num})

        result['items'] = items

    elif action=="search_pcb_random_sap":
        '''
        중계서버호출하여 가져온다
        '''
        rnd_num = gparam.get("rnd_num")

        if not rnd_num :
            result["message"] = 'PCB 난수번호가 입력되지 않았습니다.'
            result['success'] = False
            return result

        try:

            dic_result = sap_service.get_sap_input_number_by_random([rnd_num])
            items = dic_result['rs']['tables']['STAB']

            IFSapPcbRandomNumber.objects.filter(rnd_num = rnd_num).delete()

            for item in items:
                if_sap_ran = IFSapPcbRandomNumber()
                if_sap_ran.stab_mblnr = item["MBLNR"]
                if_sap_ran.stab_zeile = item["ZEILE"]
                if_sap_ran.stab_matnr = item["MATNR"]
                if_sap_ran.stab_maktx = item["MAKTX"]
                if_sap_ran.stab_menge = item["MENGE"]
                if_sap_ran.stab_abqty = item["ABQTY"]
                if_sap_ran.stab_meins = item["MEINS"]
                if_sap_ran.rnd_num = rnd_num
                if_sap_ran.set_audit(user)
                if_sap_ran.save()


            sql = '''
            select 
            id, stab_mblnr, stab_zeile, stab_matnr, stab_maktx, stab_menge, stab_abqty, stab_meins, rnd_num
            , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
            from if_sap_pcb_ran
            where rnd_num = %(rnd_num)s
            order by stab_mblnr
            '''

            items = DbUtil.get_rows(sql, {"rnd_num" : rnd_num})

            result['items'] = items

        except Exception as ex:
            result['success'] = False
            result['message'] = str(ex)



    elif action=="local_sap_mat":
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



    elif action=="request_sam_bom":
        mat_cd = posparam.get('mat_cd')
        base_date = posparam.get('base_date')
        today = DateUtil.get_current_datetime()

        if base_date is None: 
            base_date = today.strftime("%Y%m%d")

        dic_result = sap_service.get_sap_bom(mat_cd, base_date)
        items = dic_result['rs']['tables']['STAB']

        # 저장하고 다시 조회해서 리턴
        for item in items:
            if_sap_bom = IFSapBOM()
            if_sap_bom.stab_mnglg = item["MNGLG"]
            if_sap_bom.stab_datuv = item["DATUV"]
            if_sap_bom.stab_werks = item["WERKS"]
            if_sap_bom.stab_idnrk = item["IDNRK"]
            if_sap_bom.stab_revlv = item["REVLV"]
            if_sap_bom.stab_stufe = item["STUFE"]
            if_sap_bom.stab_meins = item["MEINS"]
            if_sap_bom.stab_bkbez = item["BKBEZ"]
            if_sap_bom.stab_bklas = item["BKLAS"]
            if_sap_bom.stab_bmeng = item["BMENG"]
            if_sap_bom.stab_datub = item["DATUB"]
            if_sap_bom.stab_aennr = item["AENNR"]
            if_sap_bom.stab_matnr = item["MATNR"]
            if_sap_bom.set_audit(user)
            if_sap_bom.save()


        sql= '''
        select 
        id, stab_werks, stab_matnr, stab_revlv, stab_bmeng, stab_idnrk, stab_mnglg, stab_meins, stab_stufe, stab_datuv, stab_datab, stab_aennr, stab_bklas, stab_bkbez
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        , to_char(_created, 'yyyy-mm-dd hh24:mi:ss') as created
        from if_sap_bom
        '''
        items = DbUtil.get_rows(sql)
        result['items'] = items




    elif action=="local_sap_bom":
        curr_dir = os.getcwd()
        filepath = curr_dir + '/domain/_sql/if/sap_bom.json'
        with open(filepath, 'r', encoding="utf8") as f:
            filedata = f.read()

        dic_result = json.loads(filedata)
        items = dic_result['rs']['tables']['STAB']

        for item in items:
            if_sap_bom = IFSapBOM()
            if_sap_bom.stab_mnglg = item["MNGLG"]
            if_sap_bom.stab_datuv = item["DATUV"]
            if_sap_bom.stab_werks = item["WERKS"]
            if_sap_bom.stab_idnrk = item["IDNRK"]
            if_sap_bom.stab_revlv = item["REVLV"]
            if_sap_bom.stab_stufe = item["STUFE"]
            if_sap_bom.stab_meins = item["MEINS"]
            if_sap_bom.stab_bkbez = item["BKBEZ"]
            if_sap_bom.stab_bklas = item["BKLAS"]
            if_sap_bom.stab_bmeng = item["BMENG"]
            if_sap_bom.stab_datub = item["DATUB"]
            if_sap_bom.stab_aennr = item["AENNR"]
            if_sap_bom.stab_matnr = item["MATNR"]
            if_sap_bom.set_audit(user)
            if_sap_bom.save()


    elif action=="local_sap_stock":
        curr_dir = os.getcwd()
        filepath = curr_dir + '/domain/_sql/if/sap_stock.json'
        with open(filepath, 'r', encoding="utf8") as f:
            filedata = f.read()

        dic_result = json.loads(filedata)
        items = dic_result['rs']['tables']['STAB']

        now = DateUtil.get_current_datetime()

        for item in items:
            if_sap_stock = IFSapMaterialStock()

            if_sap_stock.stab_werks = item["WERKS"]
            if_sap_stock.stab_matnr = item["MATNR"]
            if_sap_stock.stab_maktx = item["MAKTX"]
            if_sap_stock.stab_lgort = item["LGORT"]
            if_sap_stock.stab_lgobe = item["LGOBE"]
            if_sap_stock.stab_labst = item["LABST"]
            if_sap_stock.stab_insme = item["INSME"]
            if_sap_stock.stab_speme = item["SPEME"]
            if_sap_stock.stab_mslbq = item["MSLBQ"]
            if_sap_stock.stab_mkolq = item["MKOLQ"]
            if_sap_stock.stab_mskuq = item["MSKUQ"]
            if_sap_stock.stab_meins = item["MEINS"]
            if_sap_stock.stab_bklas = item["BKLAS"]
            if_sap_stock.stab_BKBEZ = item["BKBEZ"]

            if_sap_stock.data_date = now
            if_sap_stock.set_audit(user)
            if_sap_stock.save()

        result["items"] = items

    elif action=="sap_mat_all_migration":

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