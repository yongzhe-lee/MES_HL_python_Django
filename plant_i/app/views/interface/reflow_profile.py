import os
from configurations import settings
from django.db import DatabaseError, transaction
from domain.services.date import DateUtil
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.models.definition import Material
from domain.models.interface import IFReflowProfile
from domain.models.system import AttachFile

from domain.services.interface.mes import MESInterfaceService

def reflow_profile(context):
    '''
    /api/interface/reflow_profile
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request

    result = {'success' : True, 'message' : '기본오류메시지'}
    action = gparam.get('action')
    source = f'/api/interface/reflow_profile?action={action}'

    ATTACH_TABLENAME = "if_reflow_profile"
    ATTACH_NAME = "reflow_profile"

    try:
        if action == "read":
            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + " 23:59:59"
            equ_cd = gparam.get('equ_cd', "smt4.reflow")
            keyword = gparam.get('keyword')

            line_cd = gparam.get('line_cd')
            dic_param = {
                'start_dt': start_dt,
                "end_dt": end_dt,
                "equ_cd": equ_cd,
                "keyword" :keyword
            }
            sql = '''
            select 
            pp.id
            , pp.data_id
            , to_char(pp.measured_at, 'yyyy-mm-dd') as measured_date
            , to_char(pp.measured_at, 'hh24:mi') as measured_time
            , pp.mat_cd
            , pp.equ_cd
            , pp.pcb_side
            , pp.fan_level
            , pp.max_peak_temp
            , pp.pre_heat_temp
            , pp.delta_cool_temp
            , pp.above_deg_sec
            , pp.flux_dwell_sec
            , pp.delta_peak_temp
            , pp.oxy_conc
            , pp.cbs_pos
            , pp.acceptable
            from if_reflow_profile pp
            left join user_profile up on pp._creater_id = up."User_id"
            where pp.measured_at between %(start_dt)s and %(end_dt)s
            '''

            if equ_cd:
                sql += ' and pp.equ_cd = %(equ_cd)s'

            if keyword:
                sql+='''
                and pp.mat_cd like concat('%', upper(%(keyword)s), '%')
                '''

            sql += ' order by pp.measured_at desc, pp.mat_cd asc'
                
            items = DbUtil.get_rows(sql, dic_param)

            result['items'] = items

        elif action == "detail":
            data_id = gparam.get('data_id')
            sql='''
            select 
            pp.id
            , pp.data_id
            , to_char(pp.measured_at, 'yyyy-mm-dd') as measured_date
            , to_char(pp.measured_at, 'hh24:mi') as measured_time
            , pp.mat_cd
            , pp.equ_cd
            , pp.pcb_side
            , pp.fan_level
            , pp.max_peak_temp
            , pp.pre_heat_temp
            , pp.delta_cool_temp
            , pp.above_deg_sec
            , pp.flux_dwell_sec
            , pp.delta_peak_temp
            , pp.oxy_conc
            , pp.cbs_pos
            , pp.acceptable
            , to_char(pp._created, 'yyyy-mm-dd hh24:mi:ss') as created
            , to_char(pp._modified, 'yyyy-mm-dd hh24:mi:ss') as modified
            , pp.description
            , up."Name" as creator
            , up2."Name" as modifier
            from if_reflow_profile pp
            left join user_profile up on pp._creater_id = up."User_id"
            left join user_profile up2 on pp._modifier_id = up."User_id"
            where pp.data_id = %(data_id)s
            '''
            items = DbUtil.get_rows(sql, {'data_id': data_id})

            dic_data ={}

            for r in items:
                pcb_side = r.get("pcb_side")
                if pcb_side=="TOP":
                    dic_data["measured_date"] = r.get("measured_date")
                    dic_data["measured_time"] = r.get("measured_time")
                    dic_data["t_id"] = r.get("id")
                    dic_data["data_id"] = r.get("data_id")
                    dic_data["mat_cd"] = r.get("mat_cd")
                    dic_data["equ_cd"] = r.get("equ_cd")

                    dic_data["t_fan_level"] = r.get("fan_level")
                    dic_data["t_max_peak_temp"] = r.get("max_peak_temp")
                    dic_data["t_pre_heat_temp"] = r.get("pre_heat_temp")
                    dic_data["t_delta_cool_temp"] = r.get("delta_cool_temp")
                    dic_data["t_above_deg_sec"] = r.get("above_deg_sec")
                    dic_data["t_flux_dwell_sec"] = r.get("flux_dwell_sec")
                    dic_data["t_delta_peak_temp"] = r.get("delta_peak_temp")
                    dic_data["t_oxy_conc"] = r.get("oxy_conc")
                    dic_data["t_cbs_pos"] = r.get("cbs_pos")
                    dic_data["t_acceptable"] = r.get("acceptable")
                    dic_data["description"] = r.get("description")
                    dic_data["created"] = r.get("created")
                    dic_data["creator"] = r.get("creator")
                    dic_data["attach_id"] = r.get("attach_id", None)
                else:
                    dic_data["b_id"] = r.get("id")
                    dic_data["b_fan_level"] = r.get("fan_level")
                    dic_data["b_max_peak_temp"] = r.get("max_peak_temp")
                    dic_data["b_pre_heat_temp"] = r.get("pre_heat_temp")
                    dic_data["b_delta_cool_temp"] = r.get("delta_cool_temp")
                    dic_data["b_above_deg_sec"] = r.get("above_deg_sec")
                    dic_data["b_flux_dwell_sec"] = r.get("flux_dwell_sec")
                    dic_data["b_delta_peak_temp"] = r.get("delta_peak_temp")
                    dic_data["b_oxy_conc"] = r.get("oxy_conc")
                    dic_data["b_cbs_pos"] = r.get("cbs_pos")
                    dic_data["b_acceptable"] = r.get("acceptable")


            sql = '''
            select id, "FileName" from attach_file where "TableName"='if_reflow_profile' and "AttachName"='reflow_profile' and "DataPk"=%(data_id)s
            '''
            file_items = DbUtil.get_rows(sql, {"data_id" : data_id})

            result['data'] = dic_data
            result["file_items"] = file_items

            result['success'] = True

        elif action=="save_profile":

            file = context.request.FILES.get('profile_file', None)

            t_id = posparam.get('t_id')
            b_id = posparam.get('b_id')
            data_id = posparam.get('data_id')

            str_measured_at = posparam.get('measured_at')
            measured_at = DateUtil.string_to_datetime(str_measured_at, '%Y-%m-%d %H:%M') # yyyy-MM-dd HH:mm

            mat_cd = posparam.get('mat_cd')

            if mat_cd:
                query = Material.objects.filter(Code=mat_cd)
                if(query.count()==0):
                    raise Exception(f"존재하지 않는 품번: {mat_cd}")

            else:
                raise Exception("품번이 입력되지 않았습니다.")


            equ_cd = posparam.get('equ_cd', "smt4.reflow")

            t_fan_level = posparam.get('t_fan_level')
            b_fan_level = posparam.get('b_fan_level')

            t_max_peak_temp = posparam.get('t_max_peak_temp')
            b_max_peak_temp = posparam.get('b_max_peak_temp')

            t_pre_heat_temp= posparam.get('t_pre_heat_temp')
            b_pre_heat_temp= posparam.get('b_pre_heat_temp')

            t_delta_cool_temp = posparam.get('t_delta_cool_temp')
            b_delta_cool_temp = posparam.get('b_delta_cool_temp')

            t_above_deg_sec = posparam.get('t_above_deg_sec')
            b_above_deg_sec = posparam.get('b_above_deg_sec')

            t_flux_dwell_sec = posparam.get('t_flux_dwell_sec')
            b_flux_dwell_sec = posparam.get('b_flux_dwell_sec')

            t_delta_peak_temp = posparam.get('t_delta_peak_temp')
            b_delta_peak_temp = posparam.get('b_delta_peak_temp')

            t_oxy_conc = posparam.get('t_oxy_conc')
            b_oxy_conc = posparam.get('b_oxy_conc')

            t_cbs_pos = posparam.get('t_cbs_pos')
            b_cbs_pos = posparam.get('b_cbs_pos')

            t_acceptable = posparam.get('t_acceptable')
            b_acceptable = posparam.get('b_acceptable')

            description = posparam.get('description')

            t_reflow_profile = None
            if t_id:
                if data_id!=t_id:
                    raise Exception("data id 오류")

                t_reflow_profile = IFReflowProfile.objects.get(id=t_id)
            else:
                # 파일은 TOP데이터에 저장한다.
                if not file:
                    raise Exception("파일이 첨부되지 않았습니다.")

                t_reflow_profile = IFReflowProfile()

            b_reflow_profile = None
            if b_id:
                b_reflow_profile = IFReflowProfile.objects.get(id=b_id)
            else:
                b_reflow_profile = IFReflowProfile()

            t_reflow_profile.MeasuredAt = measured_at
            b_reflow_profile.MeasuredAt = measured_at

            t_reflow_profile.MaterialCode = mat_cd
            b_reflow_profile.MaterialCode = mat_cd

            t_reflow_profile.EquipmentCode = equ_cd
            b_reflow_profile.EquipmentCode = equ_cd

            t_reflow_profile.PCBSide = "TOP"
            b_reflow_profile.PCBSide = "BOTTOM"

            t_reflow_profile.FanLevel = t_fan_level
            b_reflow_profile.FanLevel = b_fan_level

            t_reflow_profile.MaxPeakTemperature = t_max_peak_temp
            b_reflow_profile.MaxPeakTemperature = b_max_peak_temp

            t_reflow_profile.PreHeatingTemperature = t_pre_heat_temp
            b_reflow_profile.PreHeatingTemperature = b_pre_heat_temp

            t_reflow_profile.DeltaCollingTemperature = t_delta_cool_temp
            b_reflow_profile.DeltaCollingTemperature = b_delta_cool_temp

            t_reflow_profile.AboveDegreeSecond = t_above_deg_sec
            b_reflow_profile.AboveDegreeSecond = b_above_deg_sec

            t_reflow_profile.FluxDwellSecond = t_flux_dwell_sec
            b_reflow_profile.FluxDwellSecond = b_flux_dwell_sec

            t_reflow_profile.DeltaPeakTemperature = t_delta_peak_temp
            b_reflow_profile.DeltaPeakTemperature = b_delta_peak_temp

            t_reflow_profile.OxygenConcentration = t_oxy_conc
            b_reflow_profile.OxygenConcentration = b_oxy_conc
            t_reflow_profile.CBSPosition = t_cbs_pos
            b_reflow_profile.CBSPosition = b_cbs_pos
            
            t_reflow_profile.Acceptable = t_acceptable
            b_reflow_profile.Acceptable = b_acceptable

            t_reflow_profile.Description = description

            t_reflow_profile.set_audit(request.user)
            b_reflow_profile.set_audit(request.user)


            with transaction.atomic():
                t_reflow_profile.save()
                b_reflow_profile.save()


                # 파일이 있을때만 처리한다.
                if file:
                    save_folder_path = os.path.join(settings.FILE_UPLOAD_PATH, "reflow_profile\\")
                    ext = file.name.split('.')[-1].lower()
                    attach_file=None

                    query = AttachFile.objects.filter(TableName=ATTACH_TABLENAME, AttachName=ATTACH_NAME, DataPk=t_reflow_profile.id)
                    
                    if query.exists():
                        attach_file = query.first()
                    else:
                        attach_file = AttachFile(TableName=ATTACH_TABLENAME, DataPk=t_reflow_profile.id, AttachName=ATTACH_NAME)
                    
                    filename = 'RP_{}_{}.{}'.format(t_reflow_profile.id, measured_at.strftime('%Y%m%d_%H%M'), ext)
                    file_path = os.path.join(save_folder_path, filename)
                    if not os.path.exists(save_folder_path):
                        os.makedirs(save_folder_path)

                    with open(file_path, 'wb') as f:
                        for chunk in file.chunks():
                            f.write(chunk)

                    attach_file.FileSize = file.size
                    attach_file.FileName = file.name
                    attach_file.PhysicFileName = filename
                    attach_file.ExtName = ext
                    attach_file.FilePath = save_folder_path
                    attach_file.FileIndex = 0
                    attach_file.set_audit(request.user)
                    attach_file.save()

            # data_id TOP기준으로 설정
            t_reflow_profile.data_id = t_reflow_profile.id
            b_reflow_profile.data_id = t_reflow_profile.id
            t_reflow_profile.save()
            b_reflow_profile.save()

            result['success'] = True
            result['message'] = 'Reflow profile saved successfully.'
            result['t_id'] = t_reflow_profile.id
            result['b_id'] = b_reflow_profile.id
            result['data_id'] = t_reflow_profile.id

        elif action == "delete_profile":
            data_id = posparam.get('data_id')
            IFReflowProfile.objects.filter(data_id=data_id).delete()
            result['success'] = True

        elif action=="search_workorder":
            mes_service = MESInterfaceService()
            line_cd = gparam.get("line_cd")
            dic_res = mes_service.get_workorder_list(line_cd)
            items = []

            if dic_res["success"]:
                rows = dic_res['data']
                for r in rows:
                    row = {}
                    for c in r:
                        name = c.get("Name")
                        value = c.get("Value")
                        row[name] = value
                    items.append(row)

            result["success"] = True
            result["items"] = items
        else:
            result["success"] = False
    except Exception as e:
        LogWriter.add_dblog("error", source, str(e))
        result['success'] = False
        result['message'] = str(e)

    return result