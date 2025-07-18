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
from domain.models.cmms import CmChkEquip

from domain.models.cmms import CmEquipChkItem

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
    if action=='selectQuality':
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
    return result