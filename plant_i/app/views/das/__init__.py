import json

from django.views import View
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse

from domain.models.definition import DASServer, DASConfig
from domain.services.das.config import DASConfigService
from domain.services.logging import LogWriter

class DASDeviceView(View):
    '''
    DAS에서 호출
    api/das_device
    '''
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        # 권한처리는 추후에 아이피 제한 정도 루틴을 넣자
        # 토큰처리도 고려필요
        remote_addr = request.META.get('REMOTE_ADDR')
        method = request.method

        #count = DASServer.objects.filter(IPAddress = remote_addr).count()
        #if count == 0:
        #    print(remote_addr)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        '''
        /api/das_device?code=server_code
        '''
        code = request.GET.get('code','')
        items = self.device(code)
        data = {'result': {'items':items}}

        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii':False})

    def device(self, code):

        # das에서 호출된 이력을 저장한다
        #message = "[DAS] requested device data - site : {}".format(site)
        #syslog_model.add_log('info', message)
        if code:
            queryset = DASConfig.objects.filter(Server__Code=code, is_active='Y')
        else:
            queryset = DASConfig.objects.filter(is_active='Y')

        data = []
        for v in queryset:
            item = json.loads(v.Configuration)
            item["config_id"] = v.id
            item["name"] = v.Name
            item["description"] = v.Description
            item["device_type"] = v.DeviceType
            item["equipment"] = v.Equipment.Code
            if item["topic"] is None:
                item["topic"] = v.Topic

            data.append(item)

        return data


