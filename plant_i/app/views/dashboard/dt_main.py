from django.db import transaction
from domain.services.sql import DbUtil
from domain.models.user import Depart, User
# from domain.models.kmms import PreventiveMaintenance  
from domain.models.cmms import CmEquipChkMaster
from domain.services.kmms.pi_master import PIService
# from domain.services.file import FileService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import json
from domain.services.common import CommonUtil
from domain.services.mqtt import FacadeMQTTClient
from domain.services.interface.equipment import IFEquipmentResultService

def dt_main(context):
    '''
    /api/dashboard/dt_main
    
    작성명 : Digital TwIN
    작성자 : 최성열
    작성일 : 
    비고 :
    '''
    
    items = []
    items2 = []
    items3 = []
    items4 = []

    result = {}
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    
    #당일 품목별 합부 수
    if action=='selectEquip':
        equ_cd = gparam.get('equ_cd') 
        #list로 만들고 any로 조회하면 됨
        equ_cd_list = [x.strip() for x in equ_cd.split(',')]

        #합부쿼리
        sql = ''' 
            select mat_cd,
                case state 
                    when '0' then '합격'
                    when '1' then '불합격'
                    else '기타'
                end as 판정,
                --state,
                count(*)
            from if_equ_result 
            where equ_cd = ANY(%(equ_cd_list)s)
            and data_date::date = CURRENT_DATE
            and is_alarm = false
            group by mat_cd,state 
        '''
        
        dc = {}
        dc['equ_cd_list'] = equ_cd_list

        items = DbUtil.get_rows(sql, dc)
        result['qualitydata'] = items

        #CT쿼리
        sql = ''' 
        with time_diff as (
          select 
            mat_cd,
            data_date,
            lag(data_date) over (partition by mat_cd order by data_date) as prev_date,
            extract(epoch from data_date - lag(data_date) over (partition by mat_cd order by data_date)) as seconds_per_piece
          from if_equ_result
          where equ_cd = ANY(%(equ_cd_list)s)
            and data_date::date = current_date
            and is_alarm = false
        )
        select 
          mat_cd,
          round(avg(seconds_per_piece)) as avg_seconds
        from time_diff
        where seconds_per_piece is not null
        group by mat_cd
        order by mat_cd;
        '''
       
        dc = {}
        dc['equ_cd_list'] = equ_cd_list

        items2 = DbUtil.get_rows(sql, dc)
        result['ctdata'] = items2

        
        #알람쿼리
        sql = ''' 
        select eah.equ_cd,eah.details,to_char(eah.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_time
        from equ_alarm_hist eah
        inner join if_equ_result ier on eah.rst_id = ier.id
        where ier.equ_cd = ANY(%(equ_cd_list)s)
        order by eah.data_date desc
        limit 10
        '''

        dc = {}
        dc['equ_cd_list'] = equ_cd_list

        items3 = DbUtil.get_rows(sql, dc)
        result['alarmdata'] = items3

        result['success'] = True
    elif action=='selectHome':
        equ_cd = gparam.get('equ_cd') 
        #전체 합부쿼리        
        sql = ''' 
            select equ."Name" as equ_name,equ_cd,mat_cd,
                case state 
                    WHEN '0' THEN '합격'
                    WHEN '1' THEN '불합격'
                    ELSE '기타'
                end AS 판정,
                --state,
                count(*)
            from if_equ_result ier
                inner join equ on ier.equ_cd = equ."Code"
            where 1=1
                and data_date::date = CURRENT_DATE
                and is_alarm = false
                and equ_cd like %(equ_cd)s
            group by equ.id,equ."Name" ,equ_cd,mat_cd,state 
            order by equ.id,equ."Name" ,equ_cd,mat_cd,state
        '''
        
        dc = {}
        dc['equ_cd'] = f"%{equ_cd}%"
        items = DbUtil.get_rows(sql, dc)
        result['qualityHomeData'] = items

        
        #CT쿼리
        sql = ''' 
            with time_diff as (
              select 
                equ.id,
                equ."Name" as equ_name,
                mat_cd,
                data_date,
                lag(data_date) over (partition by mat_cd order by data_date) as prev_date,
                extract(epoch from data_date - lag(data_date) over (partition by mat_cd order by data_date)) as seconds_per_piece
              from if_equ_result ier
  	            inner join equ on ier.equ_cd = equ."Code"
              where equ_cd like %(equ_cd)s
                and data_date::date = current_date
                and is_alarm = false
            )
            select 
              id, equ_name, mat_cd,
              round(avg(seconds_per_piece)) as avg_seconds
            from time_diff
            where seconds_per_piece is not null
            group by id,equ_name,mat_cd
            order by id,equ_name,mat_cd;
         '''
       
        dc = {}
        dc['equ_cd'] = f"%{equ_cd}%"
        items2 = DbUtil.get_rows(sql, dc)
        result['ctHomeData'] = items2

        result['success'] = True
    elif action == 'tagmaster':
        #태그마스터
        sql = ''' 
            select tag_code,tag_name,equ."Name" as equ_name
            from tag
            inner join equ on equ.id = tag."Equipment_id"
        '''
        
        dc = {}
        items = DbUtil.get_rows(sql, dc)
        result['data'] = items
        result['success'] = True    
    elif action == 'newsubscribe':

        equ_cd = gparam.get('equ_cd', 'read')    
        dt_topic = "dt_" + equ_cd
        # 기존 구독 모두 취소
        FacadeMQTTClient.unsubscribe_all()

        # 새 설비 구독
        if_equ_rst_servide = IFEquipmentResultService()
        FacadeMQTTClient.set_topic_handler(dt_topic, if_equ_rst_servide.dt_equipment_topic_handler)
        FacadeMQTTClient.apply_topic_handler()

        result['success'] = True    
    elif action == 'getpayload':
        equ_cd = gparam.get('equ_cd', 'read')    
        dt_topic = "dt_" + equ_cd

        payload = IFEquipmentResultService.topic_payloads.get(dt_topic)
        if payload is None:
            result['data'] = "payload is None"
            result['success'] = False    
            return 

        result = payload

    return result

#deleted by choi : 2025/08/17
#                : 새로운 api method는 안되나????
def get_topic_payload(context):
    '''
    /api/dashboard/get_topic_payload
    
    작성명 : Digital TwIN
    작성자 : 최성열
    작성일 : 
    비고 :
    '''

    gparam = context.gparam;
    posparam = context.posparam
    topic = gparam.get('topic', 'read')    

    payload = IFEquipmentResultService.topic_payloads.get(topic)
    if payload is None:
        return JsonResponse({'error': 'No data'}, status=404)
    return JsonResponse(payload)