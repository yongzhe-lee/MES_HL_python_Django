"""
Definition of urls for qm_lims.
"""

from django.urls import path, re_path

from app.views.account import AccountLoginView, AccountLogoutView
from app import forms
from app.views.das import DASDeviceView
from app.views import ApiModuleView, GUITemplatesView, TemplatePathView, FilesView, SystemDefaultRenderer
from app.views.extra import ExtraDefinitionView
from app.views.static import DTResourceView

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

# aas관련
from app.views.aas import AASDefaultRenderer
from app.views.aas import AASView, AssetView

from django.conf import settings
from django.conf.urls.static import static

from app.views.scheduler.kmms import kmms

urlpatterns = [
    # dt resource 관련
    path('dt/resource/<str:filename>', DTResourceView.as_view() , name='dt_resource'),

    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('', SystemDefaultRenderer.home, name='home'),
    
    path('login/', AccountLoginView.as_view(next='/'), name='login'),
    path('logout/', AccountLogoutView.as_view(next='/login'), name='logout'),


    # aas 관련
    path('aas/swagger', AASDefaultRenderer.swagger , name='aas_swagger'),
    path('aas/<str:short_id>', AASView.as_view() , name='aas'),
    path('aas/<str:short_id>/asset', AssetView.as_view() , name='aas_asset_list'),
    path('aas/<str:short_id>/asset/<str:global_asset_id>', AssetView.as_view() , name='aas_asset'),    

    # DAS에서 호출하는 API
    path('api/das_device', DASDeviceView.as_view(), name='das'), # DAS에서 호출한다, 인증관련 이슈

    path('test/', SystemDefaultRenderer.test, name='test'),
    path('setup/', SystemDefaultRenderer.setup, name='setup'),
    # kmms 마이그레이션 화면
    path('setup/kmms/mig', SystemDefaultRenderer.mig, name='kmms_mig'),

    path('api/alive', SystemDefaultRenderer.alive, name="alive"),
    path('api/files/<str:view_name>', FilesView.as_view()),
    path('api/<str:task_name>/<str:view_name>', ApiModuleView.as_view(), name='api'),

    # GUIConfiguration 기반
    path('gui/<str:gui_code>/', GUITemplatesView.as_view(), name='gui1'),
    path('gui/<str:gui_code>/<str:template_key>', GUITemplatesView.as_view(), name='gui2'),

    # templates path 기반
    path('page/<str:folder>/<str:template_name>', TemplatePathView.as_view(), name='page'),
    
    # 사용자정의 api 호출
    path('extra/<str:task>/<str:key>', ExtraDefinitionView.as_view(), name='extra'),
    
    # kmms 스케줄러 api 호출
    path('scheduler/kmms', kmms, name='kmms_scheduler'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
