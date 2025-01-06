import os, json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from configurations import settings
from domain.models.extra import ExtraSourceCode
from domain.services.sql import DbUtil

class ExtraDefinitionView(View):

    gparam = {}
    posparam = {}

    def __init__(self):
        pass

    def make_parameter(self, qeury_dic):
        param = {}

        for k in qeury_dic.keys():
            v = qeury_dic.get(k)
            if (k=='Q' or k.startswith('_dic')) and isinstance(v, str):
                param[k] = {}
                try:
                    param[k] = json.loads(v)
                    continue
                except Exception as ex:
                    print(ex)
                    continue

            v = qeury_dic.getlist(k)
            param[k] = v
            if isinstance(v, list):
                if len(v)==1:
                    param[k] = v[0]
                else:
                    param[k] = v

            elif isinstance(v, dict):
                pass

        return param

    def response404(self, request, reason):
        dic_content = {'message': reason}
        content = json.dumps(dic_content, ensure_ascii=False)
        return HttpResponse(status=404, reason=reason, content=content)

    def dispatch(self, request, *args, **kwargs):

        #if request.user.is_anonymous:
        #    return self.response401(request, '로그아웃되었습니다.')

        self.gparam = self.make_parameter(request.GET)
        if request.method=='POST':
            self.posparam = self.make_parameter(request.POST)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        
        success = False
        message = ''
        
        task = kwargs.get('task')
        key = kwargs.get('key')

        #file_path = '{}{}{}.py'.format(settings.EXTRA_CODE_PATH, task, key)
        # 파일이 존재하는지 검사
        #if not os.path.exists(file_path):
            # 파일이 존재하지 않으면 404 에러를 반환한다.
        #    return self.response404(request, '요청하신 파일이 존재하지 않습니다.')

        # 파일에서 읽어온 python 코드를 컴파일한다.
        #source = open('app/views/extra.py', 'r').read()
        
        # table에 저장된 python 코드를  key를 기반으로 가져온다
        try:
            ext_source_code = ExtraSourceCode.objects.get(TaskName=task, AccessKey=key)
            source =  ext_source_code.Source

        except Exception as ex:
            return self.response404(request, '요청하신 파일이 존재하지 않습니다.')


        ext_src = '{}.{}'.format(task, key)
        ast_compiled = compile(source, ext_src, 'exec')
        
        global_vars = {'DbUtil' : DbUtil}
        local_vars = { 'gparam' : self.gparam, 'posparam' : self.posparam, }
        
        # 컴파일된 코드를 실행 
        try:
            exec(ast_compiled, global_vars , local_vars)
            
            # 결과값을 받아야 한다. 결과는 사용자코드내 result라는 변수에 담기로 규칙을 정한다.
            data = local_vars.get('result', None)
            
            success = True
        except Exception as ex:
            success = False
            message = '실행중 오류가 발생했습니다.{}'.format(ex)

        result = {'success' : success, 'data' : data, 'message' : message}
        res_json = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii' : False})
        
        return res_json