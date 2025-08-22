from django.db import transaction
from domain.services.common import CommonUtil
from domain.services.scheduler.kmms import KmmsService
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.shortcuts import render
from django.http import JsonResponse
import json
from django.http import HttpResponse

import os
import uuid
from django.db import transaction
from django.http import JsonResponse
from configurations import settings
import pandas as pd

def kmms(request):
    '''
    scheduler/kmms
    '''
    items = []
    
    # Django 표준 방식으로 파라미터 처리
    action = request.GET.get('action') or request.POST.get('action') or 'read'
    user = request.user
    
    scheduler_Service = KmmsService()

    if action=='exec':
        items = scheduler_Service.execScheduler()

    response_data = {
        'status': 'success',
        'data': items,
        'message': '스케줄러 처리 완료'
    }
    return HttpResponse(
        json.dumps(response_data, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
