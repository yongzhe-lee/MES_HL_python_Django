import json, importlib, pytz
from tkinter import SE

from dateutil.parser import parse as date_parse
from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from configurations import settings
from domain.models.system import SystemOption, MenuUseLog
from domain.services.account import AccountService
from domain.gui import GUIConfiguration
from domain.models.user import UserGroupMenu
from domain.services.logging import LogWriter
from domain.services.system import SystemService

class MESBaseView(View):

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

    def dispatch(self, request, *args, **kwargs):

        remote_addr = request.META.get('REMOTE_ADDR')
        method = request.method
        if request.user.is_anonymous:
            return self.response401(request, '로그아웃되었습니다.')

        if request.method in ['PUT','DELETE']:
            try:
                self.parms = date_parse.parse(request.body)
            except:
                self.parms = {}
        else:
            self.gparam = self.make_parameter(request.GET)
            self.posparam = self.make_parameter(request.POST)

        return super().dispatch(request, *args, **kwargs)

    def make_response(self, content_resp):
        res = HttpResponse(content_resp)
        return res

    def make_json_response(self, data):
        res_json = JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii':False})
        return res_json

    def response500(self, request, reason, ex):
        dic_content = {'message': reason}
        if ex:
            dic_content['ex'] = str(ex)
            dic_content['message'] = str(ex)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            content = json.dumps(dic_content, ensure_ascii=False)
            res = HttpResponse(status=500, reason=reason, content=content)
            print('response500')
            return res

        return render(request, 'error.html', dic_content)

    def response401(self, request, reason):
        dic_content = {'message': reason}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            content = json.dumps(dic_content, ensure_ascii=False)
            return HttpResponse(status=401, reason=reason, content=content)

        return render(request, '401.html', dic_content)

    def response403(self, request, reason):
        dic_content = {'message': reason}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            content = json.dumps(dic_content, ensure_ascii=False)
            return HttpResponse(status=403, reason=reason, content=content)

        return render( request, '403.html', dic_content)


    def response404(self, request, reason):
        dic_content = {'message': reason}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            content = json.dumps(dic_content, ensure_ascii=False)
            return HttpResponse(status=404, reason=reason, content=content)
        
        return render( request, '404.html', dic_content)

class ApiModuleView(MESBaseView):
    '''
    권한 처리여부 결정할 것
    현재의 경로로 GET/POST Method 이용시 
    '''
    http_method_names = ['get', 'post']

    def check_authority(self, user, task_name, view_name, posparam):
        ''' API 권한이 있는지 user_group_menu를 통해서 통제
        '''
        #return True
        try:
            if task_name == 'common' and view_name == 'labels':
                return True
            if task_name == 'system' and view_name in ['menus','bookmark','storyboard']:
                return True


            group_id = None
            group_code = None
            if user.userprofile.UserGroup:
                group_id = user.userprofile.UserGroup.id
                group_code = user.userprofile.UserGroup.Code
            elif user.is_superuser:
                group_code = '__super_user'
            #menu_code_list = SystemService.get_menu_code_by_taskview(task_name, view_name)
            menu_code_list = GUIConfiguration.get_menu_code_by_taskview(task_name, view_name)

            if type(menu_code_list) is not list:
                return True
            if menu_code_list == ['']:
                return True

            if group_code in [ 'dev', '__super_user']:
                return True
            elif group_code == 'admin' and task_name == 'system' and view_name in ['usergroupmenu', 'usergroup', 'user']:
                return True
            else:
                q = UserGroupMenu.objects.filter(UserGroup_id=group_id)
                q = q.filter(MenuCode__in=menu_code_list)
                q = q.values('AuthCode')
                q = q.order_by('-AuthCode').all()

                auth = ''
                if task_name == 'system' and view_name in ['title_notice']:
                    auth = 'R'
                for item in q:
                    AuthCode = item['AuthCode']
                    if 'W' in AuthCode:
                        auth = 'W'
                        break
                    if 'R' in AuthCode:
                        auth = 'R'
                        continue
            if len(posparam) > 0 and auth != 'W':
                return False
            if auth in ['R', 'W']:
                return True

            LogWriter.add_dblog('info', 'ApiModuleView:'+task_name+'/'+view_name+','+str(group_id), '권한없음')
            return False
        except Exception as ex:
            LogWriter.add_dblog('error', 'ApiModuleView:'+task_name+'/'+view_name+','+str(group_id), ex)
            raise ex

    def api_execute(self, request, *args, **kwargs):
        
        task_name = kwargs.get('task_name',None)
        view_name = kwargs.get('view_name',None)

        if not self.check_authority(request.user, task_name, view_name, self.posparam):
            message = "ApiModuleView error : {}".format(task_name+'/'+view_name)
            ex = Exception(message)
            LogWriter.add_dblog('error', message, ex)
            return self.response403(request,message)

        data = None
        try:
            module_path = 'app.views.{}.{}'.format(task_name, view_name)
            #module_path = 'app.views.{}'.format(task_name)
            func = getattr(importlib.import_module(module_path), view_name, None)

            if func:
               data = func(self)
            else:
                message = "ApiModuleView view_name is not exist : {}".format(view_name)
                LogWriter.add_dblog('error', view_name, message)
                return self.response404(request, message)

        except Exception as ex:
            message = "ApiModuleView error : {}".format(view_name)
            LogWriter.add_dblog('error', message, ex)
            return self.response500(request,message, ex)

        return self.make_json_response(data)

    def get(self, request, *args, **kwargs):
        
        return self.api_execute(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        return self.api_execute(request, *args, **kwargs)

class FilesView(MESBaseView):
    http_method_names = ['get', 'post']
   

    def execute(self, request, *args, **kwargs):


        view_name = kwargs.get('view_name')
        try:
            module_path = 'app.views.files.{}'.format(view_name)
            view_func = getattr(importlib.import_module(module_path), view_name, None)
            if view_func:
                resp = view_func(self, request)
                return resp
            else:
                message = "FilesView view_name is not exist : {}".format(view_name)
                LogWriter.add_dblog('error', message)
                
                return HttpResponse(status=404, reason='view name not found')

        except Exception as ex:
            message = "ApiModuleView error : {}".format(view_name)
            LogWriter.add_dblog('error', message, ex)
            return self.response500(request,message, ex )

    def get(self, request, *args, **kwargs):
        return self.execute(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.execute(request, *args, **kwargs)

    def response500(self, request, reason, ex):
        dic_content = {'message': reason}
        if ex:
            dic_content['ex'] = str(ex)
            dic_content['message'] = str(ex)

        content = json.dumps(dic_content, ensure_ascii=False)
        res = HttpResponse(status=500, reason=reason, content=content)
        return res


    def response401(self, request, reason):
        dic_content = {'message': reason}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            content = json.dumps(dic_content, ensure_ascii=False)
            return HttpResponse(status=401, reason=reason, content=content)

        return render(request, '401.html', dic_content)

class GUITemplatesView(MESBaseView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        userinfo = WebUserInfo(request)
        gui_code = kwargs.get('gui_code', None)
        template_key = kwargs.get('template_key', 'default')
        content_resp = None
        
        if gui_code:
            gui_info = GUIConfiguration.get_gui_info(gui_code)

            if gui_info is None:
                return self.response404(request, '등록된 GUI가 없습니다')

            gparam = self.gparam 
            # params => gparam
            gui_params = gui_info.get('params')
            if gui_params:
                for key, value in gui_params.items():
                    gparam[key] = value

            q = SystemOption.objects.all().values('Code', 'Value')
            sys_options = { item['Code']:item['Value'] for item in q }
            gui = GUIPageInfo(gui_code, gui_info, gparam, sys_options)
            gui.template_key = template_key
            # 현재 로긴한 사용자와 gui_code로 권한체크 시작
            authcode = AccountService.check_user_auth(request.user, gui_code)

            if authcode is None or authcode == '':
                return self.response403(request, '접근 권한이 없습니다')
            else:
                userinfo.set_authcode(authcode)

            templates = gui_info.get('templates')
            template_path = templates.get(template_key, None)
            if template_path:
                try:
                    content_resp = render(request, template_path, 
                        {
                            'gparam' : gparam, 
                            'posparam' : self.posparam, 
                            'userinfo' : userinfo, 
                            'gui' : gui, 
                            'html' : template_path,
                            'sys_options' : sys_options,
                        })
                    # menu_log insert
                    try:
                        if template_key == 'default':
                            log = MenuUseLog()
                            log.MenuCode = gui_code 
                            log.User_id = request.user.id 
                            log.save()
                    except Exception as ex:
                        LogWriter.add_dblog('error', 'MenuUseLog save', ex)

                except Exception as ex:
                    source = 'GUITemplatesView - template_path : {}'.format(template_path)
                    LogWriter.add_dblog('error', source, ex)
                    # 개발의 디버깅을 위해 raise한다
                    #raise ex
                    return self.response500(request, '오류가 발생했습니다.', ex)

            else:
                return self.response404(request, '등록된 템플리트가 없습니다')
        else:
            return self.response404(request, '잘못된 경로입니다')

        httpres = HttpResponse(content_resp)

        return httpres

class TemplatePathView(MESBaseView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        userinfo = WebUserInfo(request)
        #if request.user.is_anonymous:
        #    return HttpResponseRedirect(reverse('login', kwargs=kwargs))
        folder = kwargs.get('folder', None)
        template_name= kwargs.get('template_name', None)
        template_path = 'page/{}/{}.html'.format(folder, template_name)
        httpres = None
        try:
            content_resp = render(request, template_path, {'gparam':self.gparam, 'posparam':self.posparam, 'userinfo':userinfo})
            httpres = HttpResponse(content_resp)
        except Exception as ex:
            reason = str(ex)
            httpres = HttpResponse(status=500, reason=reason)

        return httpres

class GUIPageInfo():
    gui_code = ''
    gui_name = ''
    template_key = ''
    site_name = ''
    mqtt_host = ''
    mqtt_web_port = 9001
    device_topic = ''
    event_topic= ''
    main_app_run = "N"
    hmi_topic = ''
    system_topic = 'mes21_system_event'

    action = ''
    hmi_running_mode = ''
    path_name = ''
    def __init__(self, code, gui, gparam, sys_options):

        self.site_name = settings.SITE_NAME
        self.mqtt_host = settings.MOSQUITTO_HOST
        self.mqtt_web_port = settings.MOSQUITTO_WEBSOCKET_PORT
        self.device_topic = settings.TOPIC_DEVICE_DATA
        self.event_topic = settings.TOPIC_DEVICE_EVENT
        self.hmi_topic  = settings.TOPIC_HMI_DATA        
        self.hmi_running_mode = settings.HMI_RUNNING_MODE
        self.action = gparam.get('action')
        self.gui_code = code
        self.gui_name = gui.get('name','')
        self.path_name = gui.get('path_name','')

        if settings.MAIN_APP_RUN:
            self.main_app_run = "Y"

        # get 파라미터를 클래스 멤버로
        for k,v in gparam.items():
            setattr(self, k, v)

        # 시스템옵션을 멤버로
        for k,v in sys_options.items():
            setattr(self, k, v)

        # 신규추가건은 아래로(오류방지)
        try:
            self.system_topic= settings.TOPIC_SYSTEM_EVENT
        except:
            self.system_topic= "{}_system_event".format(self.site_name)

        return
    
class WebUserInfo():
    #username = ''
    #login_id = ''
    #group_code =''
    #auth_code = ''
    #can_read = False
    #can_write = False
    #ip_address = ''

    def __init__(self, request):
        self.ip_address = request.META.get('REMOTE_ADDR')
        user = request.user
        if user.is_authenticated:
            self.username = user.userprofile.Name
            self.login_id = user.username

            if user.userprofile.UserGroup:
                self.group_code = user.userprofile.UserGroup.Code
        else:
            self.username = 'anonymous'
            self.login_id = 'anonymous'

    def set_authcode(self, authcode):
        self.auth_code = authcode

        if authcode is None:
            return

        if "R" in authcode:
            self.can_read = True

        if "W" in authcode:
            self.can_write = True
        return

    def dump(self):
        dic = {'username': self.username, 'login_id':self.login_id,'group_code':self.group_code, 'auth_code':self.auth_code, 'can_read':self.can_read, 'can_write': self.can_write}
        return json.dumps(dic, ensure_ascii=False)


    '''
    아래 삭제예정    
    '''

class SystemDefaultRenderer():

    #@login_required(login_url='/login')
    @staticmethod
    def home(request):
        """Renders the home page."""
        assert isinstance(request, HttpRequest)
        userinfo = WebUserInfo(request)
        user = request.user

        if user.is_authenticated==False:
            return redirect('login')

        q = SystemOption.objects.all().values('Code', 'Value')
        sys_options = { item['Code']:item['Value'] for item in q }

        q = SystemOption.objects.filter(Code='LOGO_TITLE').values('Value')
        option = q.first()
        if option:
            system_title = option.get('Value')
        else:
            system_title = 'QM-LIMS'

        default_menu_code = AccountService.get_user_default_menu(user)

        if not default_menu_code:
            q = SystemOption.objects.filter(Code='main_menu').values('Value')
            option = q.first()
            if option:
                default_menu_code = option.get('Value')
            else:
                default_menu_code = 'wm_dashboard_summary'

        authcode = AccountService.check_user_auth(user, default_menu_code)

        if authcode is None or authcode == '':
            default_menu_code = 'wm_noauth_default'

        return render(
            request,
            'app/index.html',
            {
                'userinfo' : userinfo,
                'sys_options' : sys_options,
                'system_title': system_title,
                'profiles':'',
                'default_menu_code': default_menu_code,
                'mqtt_host': settings.MOSQUITTO_HOST,
                'mqtt_web_port': settings.MOSQUITTO_WEBSOCKET_PORT,
                'system_topic' : settings.TOPIC_SYSTEM_EVENT,
            }
        )
   
    @staticmethod
    def mobile(request):
        userinfo = WebUserInfo(request)
        if request.user.is_authenticated==False:
            return redirect('login')

        system_title = SystemService.get_system_title()
        data = {
                'userinfo' : userinfo,
                'system_title': system_title,
                'profiles':''
            }
        return render(request, 'app/mobile_index.html', data)

    @staticmethod
    def touch_pc(request):
        userinfo = WebUserInfo(request)
        if request.user.is_authenticated==False:
            return redirect('login')

        system_title = SystemService.get_system_title()
        data = {
                'userinfo' : userinfo,
                'system_title': system_title,
                'profiles':''
            }
        #return render(request, 'app/mobile_index.html', data)
        return render(request, 'touch_pc/touch_home.html', data)

    @staticmethod
    def setup(request):
        """Renders the home page."""
        assert isinstance(request, HttpRequest)

        if request.user.is_authenticated==False:
            return redirect('login')

        return render(
            request,
            'setup.html',
            {
                'SITE_NAME' : settings.SITE_NAME,
                'DEBUG' : settings.DEBUG,
                'MOSQUITTO_HOST' : settings.MOSQUITTO_HOST,
                'TOPIC_DEVICE_DATA':settings.TOPIC_DEVICE_DATA,
                'TOPIC_DEVICE_EVENT':settings.TOPIC_DEVICE_EVENT,
                'TOPIC_HMI_DATA':settings.TOPIC_HMI_DATA,
            }
        )    

    @staticmethod
    def notfound403(request):
        return render(
            request,
            '403.html',
            {
                'title':'403',
                'message':'권한이 없습니다.',
                'year':datetime.now().year,
            }
        )

    @staticmethod
    def notfound404(request):
        return render(
            request,
            '404.html',
            {
                'title':'404',
                'message':'페이지를 찾을수 없습니다',
                'year':datetime.now().year,
            }
        )

    @staticmethod
    def error500(request):
        return render(
            request,
            'error.html',
            {
                'title':'setup',
                'message':'Your application description page.',
                'year':datetime.now().year,
            }
        )

    @staticmethod
    def alive(request):

        now = datetime.now()
        tz = pytz.timezone(settings.TIME_ZONE)
        o = now.astimezone(tz)
        r = o.isoformat()
        if o.microsecond:
            r = r[:23] + r[26:]
        if r.endswith('+00:00'):
            r = r[:-6] + 'Z'

        return JsonResponse({'success': True, 'datetime': r})
    
    @staticmethod
    def test(request):
        """Renders the about page."""
        assert isinstance(request, HttpRequest)
        return render(
            request,
            'sample/test.html',
            {
                'title':'Test',
                'message':'Test Grid page.',
                'year':datetime.now().year,
            }
        )