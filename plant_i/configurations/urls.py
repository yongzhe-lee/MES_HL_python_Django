"""
Definition of urls for qm_lims.
"""

from django.urls import path

from app.views.account import AccountLoginView, AccountLogoutView
from app import forms
from app.views.das import DASDeviceView
from app.views import ApiModuleView, GUITemplatesView, TemplatePathView, FilesView, SystemDefaultRenderer
from app.views.extra import ExtraDefinitionView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

# aas관련
from app.views.aas import AASDefaultRenderer

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('', SystemDefaultRenderer.home, name='home'),
    
    path('login/', AccountLoginView.as_view(next='/'), name='login'),
    path('logout/', AccountLogoutView.as_view(next='/login'), name='logout'),

    # aas 관련
    path('aas/swagger', AASDefaultRenderer.swagger , name='aas_swagger'),

    # DAS에서 호출하는 API
    path('api/das_device', DASDeviceView.as_view(), name='das'), # DAS에서 호출한다, 인증관련 이슈

    path('test/', SystemDefaultRenderer.test, name='test'),
    path('setup/', SystemDefaultRenderer.setup, name='setup'),
    
    path('api/files/<str:view_name>', FilesView.as_view()),
    path('api/<str:task_name>/<str:view_name>', ApiModuleView.as_view(), name='api'),


    # GUIConfiguration 기반
    path('gui/<str:gui_code>/', GUITemplatesView.as_view(), name='gui1'),
    path('gui/<str:gui_code>/<str:template_key>', GUITemplatesView.as_view(), name='gui2'),

    # templates path 기반
    path('page/<str:folder>/<str:template_name>', TemplatePathView.as_view(), name='page'),
    
    # 사용자정의 api 호출
    path('extra/<str:task>/<str:key>', ExtraDefinitionView.as_view(), name='extra')

]