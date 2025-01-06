import json
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest
from django.db.models import Max 

from domain.models.system import MenuFolder, MenuItem, SystemOption
from domain.gui import GUIConfiguration

from configurations import settings
from domain.services.setup import SystemSetupService
from domain.services.system import SystemService
from domain.services.common import CommonUtil
from domain.services.date import DateUtil
from domain.services.logging import LogWriter


def menu_setup(context):
    '''
    /api/system/menu_setup
    '''
    result = {'success': True}
    gparam = context.gparam
    posparam = context.posparam
    action  = gparam.get('action')
    request = context.request
    setup_sevice = SystemSetupService()

    if action=='auto_save':
        success = setup_sevice.setup_menu()
        result = {'success': success}

    elif action=='folder_list':
        ''' 전체 메뉴폴더 리스트
        '''
        result = setup_sevice.get_folder_list()

    elif action=='submenu_list':
        ''' DB에 등록된 폴더의 메뉴리스트
        '''
        folder_id = gparam.get('folder_id')
        result = setup_sevice.get_menu_list(folder_id)

    elif action=='gui_use_list':
        ''' 소스의 메뉴 리스트
        '''
        unset = gparam.get('unset', '')
        keyword = gparam.get('keyword', '')
        result = setup_sevice.get_gui_use_list(unset, keyword)

    elif action=='folder_order_save':
        ''' 폴더의 순서 저장
        '''
        items = posparam.get('Q')
        order = 10
        for id in items:
            MenuFolder.objects.filter(id=id).update(_order=order)
            order = order + 10

    elif action=='folder_save':
        ''' 폴더정보 저장. 사용안함. see folder_name_save
        '''
        ''' 2024.08.08 lims 폴더 정보 변경(트리그리드)
        '''
        
        result={'success': True}
        
        id = posparam.get('id')
        Parent_id = posparam.get('Parent_id')
        FolderName = posparam.get('FolderName')
        _order = posparam.get('_order')
        IconCSS = posparam.get('IconCSS')
        id = CommonUtil.try_int(id)
        Parent_id = CommonUtil.try_int(Parent_id)

        menu_folder = None
        if id:
            menu_folder = MenuFolder.objects.get(id=id)
        else:
            menu_folder = MenuFolder()
  
        menu_folder.Parent_id = Parent_id
        menu_folder.FolderName = FolderName
        menu_folder.IconCSS = IconCSS
        menu_folder._order = _order
        menu_folder.save()

    elif action=='folder_insert':
        ''' 폴더 추가
        '''
        result={'success': True}
        old_id = posparam.get('old_id')
        Parent_id = posparam.get('Parent_id')
        FolderName = posparam.get('FolderName')
        IconCSS = posparam.get('IconCSS')
        if not IconCSS:
            IconCSS = 'inventory'
        _order = posparam.get('_order')
        old_id = CommonUtil.try_int(old_id)
        Parent_id = CommonUtil.try_int(Parent_id)

        menu_folder = None
        if old_id and not Parent_id:
            foo = MenuFolder.objects.get(id=old_id)
            #IconCSS = foo.IconCSS
            _order = foo._order + 1
        
        menu_folder = MenuFolder()
  
        menu_folder.Parent_id = Parent_id
        menu_folder.FolderName = FolderName
        menu_folder.IconCSS = IconCSS
        menu_folder._order = _order
        menu_folder.save()

    elif action=='folder_name_save':
        ''' 폴더정보 저장
        '''
        result={'success': True}
        id = posparam.get('id')
        Parent_id = posparam.get('Parent_id')
        FolderName = posparam.get('FolderName')
        #IconCSS = posparam.get('IconCSS')
        id = CommonUtil.try_int(id)
        Parent_id = CommonUtil.try_int(Parent_id)

        menu_folder = MenuFolder.objects.get(id=id)
        menu_folder.FolderName = FolderName
        menu_folder.Parent_id = Parent_id
        #menu_folder.IconCSS = IconCSS
        menu_folder.save()

    elif action=='menu_list_save':
        ''' 한 폴더 안의 모든 메뉴목록 정보 저장. 메뉴명과 순서.
        '''
        menus = posparam.get('menus')
        arr_menus = json.loads(menus)

        for dic in arr_menus:
            MenuCode = dic.get('menu_code')
            MenuName = dic.get('menu_name')
            MenuFolder_id = dic.get('folder_id')
            _order = dic.get('_order')

            menuitem = MenuItem.objects.get(MenuCode = MenuCode,MenuFolder_id= MenuFolder_id)
            menuitem.MenuName = MenuName
            menuitem.MenuFolder_id = MenuFolder_id
            menuitem.set_audit(request.user)
            menuitem._order=_order
            menuitem.save()

    elif action=='menu_save':
        ''' 메뉴추가
        '''
        Folder_id = posparam.get('Folder_id')
        MenuCode = posparam.get('MenuCode')
        gui = GUIConfiguration.get_gui_info(MenuCode)

        menu_item = None
        count = MenuItem.objects.filter(MenuCode=MenuCode).count()
        if count>0:
            menu_item = MenuItem.objects.get(MenuCode=MenuCode)
        else:
            menu_item = MenuItem()
            dic_max = MenuItem.objects.filter(MenuFolder__id=Folder_id).aggregate(Max('_order'))

            order_no = dic_max.get('_order__max')
            if order_no is None:
                order_no = 0

            order_no = order_no + 10
            menu_item.Url = '/gui/' + MenuCode
            menu_item._order = order_no
            menu_item._created = DateUtil.get_current_datetime()
            menu_item.MenuCode = MenuCode

        menu_item.MenuName = gui.get('name')
        menu_item.Popup = gui.get('popup')
        menu_item.MenuFolder_id = Folder_id
        menu_item.set_audit(request.user)
        menu_item.save()

    elif action=='folder_delete':
        ''' 폴더 삭제
        '''
        Folder_id = posparam.get('folder_id')
        folder_exist_flag = MenuFolder.objects.filter(Parent__id =Folder_id).exists()
        exist_flag = MenuItem.objects.filter(MenuFolder__id =Folder_id).exists()
        
        if folder_exist_flag:
            result = {'success':False, 'message': '하위 폴더가 존재합니다.'}
        elif exist_flag:
            result = {'success':False, 'message': '하위 메뉴가 존재합니다.'}
        else:
            MenuFolder.objects.filter(id=Folder_id).delete()

    elif action=='menu_delete':
        ''' 메뉴 삭제
        '''
        menus = posparam.get('menus')
        arr_menus = json.loads(menus)

        for dic in arr_menus:
            MenuCode = dic.get('MenuCode')
            Folder_id = dic.get('Folder_id')
            MenuItem.objects.filter(MenuFolder__id =Folder_id, MenuCode=MenuCode).delete()


    return result
