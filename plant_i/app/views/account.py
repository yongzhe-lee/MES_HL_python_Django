from sqlite3 import Date
import time
import jwt
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from configurations import settings
from domain.models.system import LoginLog

from domain.services.logging import LogWriter
from domain.services.system import SystemService
from domain.services.date import DateUtil
from app import forms

login_page_template = 'app/login.html'


class AccountLoginView(LoginView):

    http_method_names = ['get','post']
    next = '/'


    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *arg, **kwargs):
        use_mobile_login = settings.USE_MOBILE_LOGIN
        system_title = SystemService.get_system_title()
        data = { 'system_title': system_title, 'use_mobile_login': use_mobile_login }
        year = DateUtil.get_current_year()
        resp = render(request, login_page_template, data)
        return resp


    def post(self, request, *arg, **kwargs):

        remote_addr = request.META.get('REMOTE_ADDR')
        username=request.POST['username']
        password = request.POST['password']
        go_mobile = request.POST.get('go_mobile', None)
        go_touch = request.POST.get('go_touch', None)

        loginuser = authenticate(username=username, password=password)

        if loginuser:

            login(self.request, loginuser)
            
            try:
                loginlog = LoginLog(Type='login', User=loginuser, IPAddress = remote_addr )
                loginlog.save()

                # 스마트공장 1번가 로그 수집
                LogWriter.add_sf_log('접속', loginuser.id, request)

            except Exception as ex:
                source = 'AccountLoginView post loginlog.save'
                LogWriter.add_dblog('error', source, ex )


            request.session.set_expiry(0)

            resp = None
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                start_url = '/'
                if go_mobile:
                    start_url = '/mobile'
                elif go_touch:
                    start_url = '/touch_pc'

                dic_data ={'loginResult' : "OK", 'next': start_url, 'is_app' : False}
                agent = request.META.get('HTTP_USER_AGENT')
                is_app_idx =agent.find('sf21mes_')
                if is_app_idx > 0 :
                    dic_data['is_app'] =True
                    dic_data['app_data'] = self.issue_token(loginuser)

                return JsonResponse(dic_data, safe=False, json_dumps_params={'ensure_ascii':False})

            else:
                url = 'home'
                if go_mobile: 
                    url = 'mobile'
                resp = HttpResponseRedirect(reverse(url, kwargs=kwargs))

            return resp
        else:
            #code = 'NOID'
            code = 'ETC'
            resp = None
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                resp = JsonResponse({'loginResult' : code,'loginResultMsg':''})
            else:
                system_title = SystemService.get_system_title()
                data =  { 'loginResult' : code, 'system_title': system_title }
                resp = render(request, login_page_template, data)

            return resp

    def issue_token(self, loginuser):
        curr_int_time = int(time.time())
        expire_ts = curr_int_time + 3600*24*7 # 일주일 만료
        payload = {
            'username': loginuser.username,
            'expire':expire_ts
        }
        refresh_token_byte = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        refresh_token = refresh_token_byte.decode('utf-8')

        # refesh token을 db에 저장
        loginuser.userprofile.token = refresh_token
        loginuser.userprofile.save()

        payload['expire'] = curr_int_time + 1800 # 30분만료 60*30
        access_token_byte = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        access_token = access_token_byte.decode('utf-8')

        token_data = {'access_token': access_token, 'refresh_token' : refresh_token, 'userid': loginuser.username, 'username':loginuser.userprofile.Name}
        return token_data



class AccountLogoutView(LogoutView):
    http_method_names = ['get','post']
    next = '/login'

    def get(self, request, *arg, **kwargs):
        user = request.user
        remote_addr = request.META.get('REMOTE_ADDR')
        system_title = SystemService.get_system_title()
        use_mobile_login = settings.USE_MOBILE_LOGIN
        data = { 
            'system_title': system_title, 
            'use_mobile_login': use_mobile_login
        }

        if user.is_anonymous:
            return render( request, login_page_template, data)
        try:
            loginlog = LoginLog(Type='logout',User=user, IPAddress = remote_addr )
            loginlog.save()

            # 스마트공장 1번가 로그 수집
            LogWriter.add_sf_log('종료', user.id, request)
        except Exception as ex:
            source = 'AccountLogoutView get loginlog.save'
            LogWriter.add_dblog('error', source, ex )

        logout(request)

        return redirect('/login')


    def post(self, request, *arg, **kwargs):
        user = request.user
        remote_addr = request.META.get('REMOTE_ADDR')
        system_title = SystemService.get_system_title()
        use_mobile_login = settings.USE_MOBILE_LOGIN
        data = { 
            'system_title': system_title, 
            'use_mobile_login': use_mobile_login
        }

        if user.is_anonymous:
            return render( request, login_page_template, data)
        try:
            loginlog = LoginLog(Type='logout',User=user, IPAddress = remote_addr )
            loginlog.save()

            # 스마트공장 1번가 로그 수집
            LogWriter.add_sf_log('종료', user.id, request)
        except Exception as ex:
            source = 'AccountLogoutView get loginlog.save'
            LogWriter.add_dblog('error', source, ex )

        logout(request)

        return redirect('/login')