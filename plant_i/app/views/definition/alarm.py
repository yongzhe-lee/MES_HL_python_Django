import os
from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.definition import EquipAlarm, EquipAlarmHistory
from domain.models.cmms import Equipment

def alarm(context):
    '''
    /api/definition/alaram?action=
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    action = gparam.get('action')
    lang_code = user.userprofile.lang_code
    if lang_code is None:
        lang_code = 'ko-KR'

    method = request.method
    result = {}
    source = f'/api/definition/alarm?action={action}'
    result = {'success' : True, "message" : ''}

    try:

        if action=="alarm_list":
            equ_id = gparam.get('equ_id')
            keyword = gparam.get('keyword')
            dic_param = {"equ_id": equ_id, "keyword": keyword }

            sql = '''
            select 
            ln."Name" as line_nm
            , ea.alarm_cd
            , ea.alarm_nm
            , ea.alarm_num
            , e."Code" as equ_cd
            , e."Name" as equ_nm
            , to_char(ea._created, 'yyyy-mm-dd hh24:mi:ss') created
            , to_char(ea._modified, 'yyyy-mm-dd hh24:mi:ss') modified
            from equ_alarm ea 
            inner join equ e on e.id = ea."Equipment_id"
            left join line ln on ln.id = e.line_id
            where 1=1
            '''
            if equ_id:
                sql+='''
                and ea."Equipment_id" =%(equ_id)s
                '''
            if keyword:
                sql+='''
                '''
            sql+='''
            order by ea.alarm_num
            '''
            data = DbUtil.get_rows(sql, dic_param)
            result['data'] = data
            result['success'] = True

        elif action=="alarm_detail":

            alarm_cd = gparam.get('alarm_cd')
            dic_param = {"alarm_cd": alarm_cd }

            sql = '''
            select 
            ln."Name" as line_nm
            , ea.alarm_cd
            , ea.alarm_nm
            , ea.alarm_nm_en
            , ea.alarm_num
            , ea.cause
            , ea.cause_en
            , ea.used_by
            , ea.remedy
            , ea.alarm_detail
            , e."Code" as equ_cd
            , e."Name" as equ_nm
            , ea."_created"
            , to_char(ea._created, 'yyyy-mm-dd hh24:mi:ss') created
            , to_char(ea._modified, 'yyyy-mm-dd hh24:mi:ss') modified
            from equ_alarm ea 
            left join equ e on e.id = ea."Equipment_id"
            left join line ln on ln.id = e.line_id
            where ea.alarm_cd = %(alarm_cd)s
            '''
            
            result['data'] = DbUtil.get_row(sql, dic_param)
            result['success'] = True

        elif action=="alarm_history_list":

            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + ' 23:59:59'
            equ_id = gparam.get('equ_id')
            keyword = gparam.get('keyword')

            sql='''
            select 
            eah.alarm_cd
            , eah.equ_cd
            , e."Name" as equ_nm
            , ll."Name" as line_nm
            , ea.alarm_nm
            , ea.alarm_num
            , eah.details
            , eah.part_number
            , to_char(eah.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_date
            , to_char(eah.start_dt, 'yyyy-mm-dd hh24:mi:ss') as start_dt
            , to_char(eah.end_dt, 'yyyy-mm-dd hh24:mi:ss') as end_dt
            , to_char(eah._created, 'yyyy-mm-dd hh24:mi:ss') as created
            , ea.cause
            , ea.remedy
            from equ_alarm_hist eah 
            left join equ_alarm ea on ea.alarm_cd=eah.alarm_cd
            left join equ e on e."Code"=eah.equ_cd
            left join line ll on ll.id=e.line_id
            where 1=1
            and eah.data_date between %(start_dt)s and %(end_dt)s
            '''
            if equ_id:
                sql+='''
                and ea.id=%(equ_id)s
                '''

            sql+='''
            order by eah.data_date desc, eah.alarm_cd
            '''

            dic_param = {"start_dt": start_dt, "end_dt": end_dt, "equ_id" : equ_id, "keyword":keyword }
            result['data'] = DbUtil.get_rows(sql, dic_param)
            result['success'] = True


        elif action=="alarm_setup_xml":
            '''
            /api/definition/alarm?action=alarm_setup_xml
            '''

            import xml.etree.ElementTree as ET

            curr_dir = os.getcwd()
            config_path = curr_dir + '/domain/_sql/interface/alarm/fuji/'
            filepath = config_path + "e8xxx_KO.xml"

            tree = ET.parse(filepath)
            root = tree.getroot()
            equ_cd = "smt4.mnt"
            equipment = Equipment.objects.get(Code=equ_cd)

            for c in root:
                alarm_number = c.attrib.get('id')
                alarm_code = f"{equ_cd}.alm.{alarm_number}"
                disp = c.find("disp").text
                if disp is None:
                    disp = alarm_code
                mc = c.find("mc").text
                cause = c.find("cause").text
                remedy = c.find("remedy").text
                #print(disp, mc, cause, remedy)

                query = EquipAlarm.objects.filter(alarm_code= alarm_code)
                equ_alarm = None
                if query.exists():
                    equ_alarm = query.first()                    
                else:
                    equ_alarm = EquipAlarm(alarm_code=alarm_code, Equipment = equipment)
                    equ_alarm._created = DateUtil.get_current_datetime()

                equ_alarm.AlarmNumber = alarm_number
                equ_alarm.Name= disp
                equ_alarm.Cause = cause
                equ_alarm.Remedy = remedy
                equ_alarm.UsedBy = mc                
                equ_alarm.set_audit(user)
                equ_alarm.save()

            result['success'] = True

        elif action=="alarm_setup_text":
            '''
            /api/definition/alarm?action=alarm_setup_text
            '''
            curr_dir = os.getcwd()
            config_path = curr_dir + '/domain/_sql/interface/alarm/fuji/'
            filepath = config_path + "ErrorCodeText_E.txt"

            equ_cd = "smt4.mnt"
            equipment = Equipment.objects.get(Code=equ_cd)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                last_part = ""

                alarm_number = ""
                disp = ""
                mc=""
                details = ""
                cause =""
                remedy =""
                is_read_remedy = False

                idx = -1


                for line in f:
                    idx = idx+1


                    if line.startswith('--'):
                        if alarm_number=="":
                            alarm_code = ""
                            alarm_number = ""
                            disp = ""
                            mc=""
                            details=""
                            cause =""
                            remedy =""
                            last_part =""
                            continue


                        query = EquipAlarm.objects.filter(alarm_code= alarm_code)
                        equ_alarm = None
                        if query.exists():
                            equ_alarm = query.first()
                        else:
                            equ_alarm = EquipAlarm(alarm_code=alarm_code, Equipment = equipment)
                            equ_alarm._created = DateUtil.get_current_datetime()
                            equ_alarm.Name= disp
                            equ_alarm.Cause = cause
                            equ_alarm.Remedy = remedy

                        equ_alarm.AlarmNumber = alarm_number
                        equ_alarm.NameEn= disp
                        equ_alarm.CauseEn = cause
                        equ_alarm.UsedBy = mc
                        equ_alarm.Detail = details
                        equ_alarm.set_audit(user)
                        equ_alarm.save()

                        alarm_code=""
                        alarm_number = ""
                        disp = ""
                        mc=""
                        cause =""
                        details =""
                        remedy =""
                        continue


                    if line.startswith('Code:'):
                        alarm_number = line.split(':')[1].strip()
                        alarm_code = f"{equ_cd}.alm.{alarm_number}"
                        last_part = ""
                    elif line.startswith("Display:"):
                        last_part = "disp"
                        disp = "".join(line.split(':')[1:])
                        if len(disp)==0:
                            disp = alarm_number
                    elif line.startswith("Used by:"):
                        last_part = "mc"
                        mc = "".join(line.split(':')[1:])
                    elif line.startswith("Details"):
                        last_part = "details"
                        details = "".join(line.split(':')[1:])
                    elif line.startswith("Cause:"):
                        cause = "".join(line.split(':')[1:])
                        last_part = "cause"
                    elif line.startswith("Remedy:"):
                        remedy = "".join(line.split(':')[1:])
                        last_part = "remedy"
                    else:
                        # 마지막에 읽었던 것이 뭔지 확인
                        if last_part == "disp":
                            disp = disp + line
                        elif last_part == "mc":
                            mc = mc + line
                        elif last_part=="details":
                            details = details + line
                        elif last_part =="cause":
                            cause = cause + line
                        elif last_part =="remedy":
                            remedy = remedy + line
                        else:
                            raise Exception("Unknown line format")

            result['success'] = True
        else:
            print("")

    except Exception as ex:
        LogWriter.add_dblog("error", source, ex)
        result['success'] = False
        result['message'] = str(ex)

    return result

