from domain import init_once

@init_once
class GUIConfiguration():

    __dic_gui__ = {}
    __dic_gui_mobile__ = {}
    __dic_view_menu__ = {}

    @classmethod
    def __static_init__(cls):
        # class method 이므로 cls를 붙여줘야한다
        cls.__dic_gui__ = cls.menu_init()
        #cls.mobile_menu_init()
        #cls.taskview_menu_code_map()
        return
    
    @classmethod
    def gui_item(cls, name, template, site='', path_name=''):
        item = {
            'name':name, 
            'templates': {'default':template}, 
            'site': site,
            'popup':'N',
            'path_name': path_name,
        }
        return item
    
    @classmethod
    def menu_init(cls):

        gui_dc = {}

        #################################################  QM-Lims  #####################################################
        ##대시보드
        gui_dc['wm_dashboard'] = cls.gui_item('대시보드', 'dashboard/main_dash.html')#대시보드
        gui_dc['wm_storyboard'] = cls.gui_item('스토리보드', 'dashboard/storyboard.html')#스토리보드

        #기준정보
        gui_dc['wm_factory'] = cls.gui_item('공장', 'definition/factory.html')#라인정보
        gui_dc['wm_line'] = cls.gui_item('라인', 'definition/line.html')#라인정보
        gui_dc['wm_process'] = cls.gui_item('공정', 'definition/process.html')#공정정보
        gui_dc['wm_material'] = cls.gui_item('품목정보', 'definition/material.html') #품목정보
        gui_dc['wm_bom'] = cls.gui_item('BOM', 'definition/bom.html') #BOM
        gui_dc['wm_company'] = cls.gui_item('업체', 'definition/company.html')#업체
        gui_dc['wm_holiday'] = cls.gui_item('휴일 스케줄', 'definition/holiday.html')#휴일 스케줄
        gui_dc['wm_defect'] = cls.gui_item('부적합정보', 'definition/defect.html') #부적합정보
        gui_dc['wm_shift'] = cls.gui_item('조교대정보', 'definition/shift.html')#조교대정보
        gui_dc['wm_line_inactive'] = cls.gui_item('비가동일정정보', 'definition/line_inactive.html')#비가동정보
        gui_dc['wm_model_change'] = cls.gui_item('기종변경정보', 'definition/model_change.html')#기종변경정보


        # 설비관리
        gui_dc['wm_equip_group'] = cls.gui_item('설비그룹', 'definition/equip_group.html')
        gui_dc['wm_equipment'] = cls.gui_item('설비', 'definition/equipment.html')
        gui_dc['wm_tag_group'] = cls.gui_item('태그그룹', 'definition/tag_group.html')
        gui_dc['wm_tag_master'] = cls.gui_item('태그정보', 'definition/tag.html')
        gui_dc['wm_das_config'] = cls.gui_item('데이터수집설정', 'system/das_config.html')

        # 설비보전
        # gui_dc['wm_pm_master'] = cls.gui_item('PM마스터관리', 'kmms/pm/pm_master.html')
        # gui_dc['wm_pm_schedule'] = cls.gui_item('PM일정', 'kmms/pm/pm_schedule.html')
        # gui_dc['wm_work_order'] = cls.gui_item('WO관리', 'kmms/work_order.html')
        # gui_dc['wm_pm_work_list'] = cls.gui_item('PM작업목록조회', 'kmms/pm/pm_work_list.html')
        # gui_dc['wm_pm_result'] = cls.gui_item('PM작업결과등록', 'kmms/pm/pm_work_result.html')
        # gui_dc['wm_pm_result_list'] = cls.gui_item('PM작업결과조회', 'kmms/pm/pm_work_result_list.html')
        # gui_dc['wm_check_master'] = cls.gui_item('점검마스터관리', 'kmms/check/check_master.html')
        # gui_dc['wm_check_schedule'] = cls.gui_item('점검일정관리', 'kmms/check/check_schedule.html')
        # gui_dc['wm_check_work_list'] = cls.gui_item('점검작업조회', 'kmms/check/check_work_list.html')
        # gui_dc['wm_check_result'] = cls.gui_item('점검작업결과등록', 'kmms/check/check_result.html')
        # gui_dc['wm_check_result_list'] = cls.gui_item('점검작업결과조회', 'kmms/check/check_result_list.html')
        # gui_dc['wm_check_work_daily'] = cls.gui_item('일상점검', 'kmms/check/check_work_daily.html')
        # gui_dc['wm_equ_grade'] = cls.gui_item('설비등급관리', 'kmms/equ_grade.html') 


        # 업무지원
        gui_dc['wm_calendar'] = cls.gui_item('캘린더', 'definition/meeting_calendar.html') #캘린더
        gui_dc['wm_board'] = cls.gui_item('공지사항', 'definition/notice_board.html') #캘린더

        
        # 25.01.02 김하늘 추가
        # 시스템코드(대메뉴) -> 코드관리(명칭 변경)
        gui_dc['wm_code'] = cls.gui_item('기초코드', 'system_code/code.html') #부적합정보
        # 코드관리 - 자재관련 코드(중메뉴)
        gui_dc['wm_supplier'] = cls.gui_item('공급업체', 'system_code/supplier.html')# 공급업체
        gui_dc['wm_material_type'] = cls.gui_item('품목유형', 'system_code/material_type.html')# 품목유형(코드)
        gui_dc['wm_material_location'] = cls.gui_item('보관위치', 'system_code/store_location.html')# 보관위치 주소(코드)


        # 시스템관리
        gui_dc['wm_user'] = cls.gui_item('사용자', 'system/user.html') # wm_user 메뉴이름변경불가
        gui_dc['wm_user_group'] = cls.gui_item('사용자그룹', 'system/user_group.html')   # wm_user_group 메뉴이름변경불가
        gui_dc['wm_user_group_menu'] = cls.gui_item('메뉴권한', 'system/user_group_menu.html')  # wm_user_group_menu 메뉴이름변경불가
        gui_dc['wm_storyboard_config'] = cls.gui_item('스토리보드설정', 'system/storyboard_config.html')
        gui_dc['wm_depart'] = cls.gui_item('부서', 'system/depart.html')  
        gui_dc['wm_login_log'] = cls.gui_item('로그인로그', 'system/login_log.html') # 로그인로그
        gui_dc['wm_menu_log'] = cls.gui_item('메뉴로그', 'system/menu_log.html') # 메뉴로그
        gui_dc['wm_system_log'] = cls.gui_item('시스템로그', 'system/system_log.html') # 시스템로그
        # gui_dc['wm_holiday'] = cls.gui_item('휴일 스케줄', 'system/holiday.html')  
        

        #문서/게시판 관리
        #gui_dc['wm_rpt_form'] = cls.gui_item('보고서 설정 관리', 'master/document/rpt_form.html')#보고서 설정 관리

        # 데이터분석
        # 공정데이터 24.11.20 추가 김하늘
        gui_dc['wm_tag_data_current'] = cls.gui_item('태그데이터현황', 'tagdata/tag_current.html')
        gui_dc['wm_tag_boxplot'] = cls.gui_item('상자수염그림', 'tagdata/tag_boxplot.html')
        #gui_dc['wm_tag_brush_trend'] = cls.gui_item('데이터트렌드2', 'tagdata/tag_brush_trend.html')
        gui_dc['wm_tag_data_list'] = cls.gui_item('태그데이터조회', 'tagdata/tagdata_list.html')
        gui_dc['wm_tag_histogram'] = cls.gui_item('히스토그램', 'tagdata/tag_histogram.html')
        gui_dc['wm_tag_scatter'] = cls.gui_item('산점도', 'tagdata/tag_scatter.html')
        gui_dc['wm_tag_summary'] = cls.gui_item('데이터통계', 'tagdata/tag_statistics.html')
        #gui_dc['wm_tag_sync_trend'] = cls.gui_item('데이터트렌드3', 'tagdata/tag_sync_trend.html')
        gui_dc['wm_tag_trend'] = cls.gui_item('데이터트렌드', 'tagdata/tag_trend.html')
        gui_dc['wm_regression_a'] = cls.gui_item('산점도-회귀분석', 'tagdata/regression_a.html')

        # AI    25.01.20 김하늘 추가
        gui_dc['wm_ai_tag_group'] = cls.gui_item('AI시스템 운영관리', 'ai/tag_group.html')
        gui_dc['wm_ai_tag'] = cls.gui_item('AI시스템 참조데이터 관리', 'ai/tag.html')
        gui_dc['wm_ai_tagdata_list'] = cls.gui_item('AI시스템 IF 확인', 'ai/tagdata_list.html')
        gui_dc['wm_predictive_conservation'] = cls.gui_item('예지보전 알람', 'ai/predictive_conservation.html')
        gui_dc['wm_learning_data_info'] = cls.gui_item('학습데이터 정보', 'ai/learning_data_info.html')
        gui_dc['wm_learning_data_from_tag'] = cls.gui_item('학습데이터 정보(태그)', 'ai/learning_data_from_tag.html')

        return gui_dc
 
    @classmethod
    def get_gui_list(cls):
        return  cls.__dic_gui__

    @classmethod
    def get_gui_info(cls, code):
        gui = cls.__dic_gui__.get(code, None)
        if gui is None:
            gui = cls.__dic_gui_mobile__.get(code, None)
        return gui

    @classmethod
    def add_mobile_menu(cls, gui_code, gui_name, template, site=''):
        item = cls.gui_item(gui_name, template, site)
        cls.__dic_gui_mobile__[gui_code] = item
        return item

    @classmethod
    def mobile_menu_init(cls): 
        #cls.add_mobile_menu('mm_mat_lot_mat', 'LOT자재 생산투입', 'pda/myungrang/mat_lot_input.html', 'myungrang')
        #cls.add_mobile_menu('mm_mat_lot_input_snp', '자재LOT 입고등록', 'pda/sealnpack/mat_lot_input_snp.html', 'sealnpackmes')
        return

    @classmethod
    def get_mobile_gui_list(cls):
        return  cls.__dic_gui_mobile__

    @classmethod
    def get_mobile_gui_info(cls, gui_code):
        mobile_gui = cls.__dic_gui_mobile__.get(gui_code, None)
        return mobile_gui

    @classmethod
    def taskview_menu_code_map(cls):
        ''' task, view와 menu_code를 매핑한다.
        API 엔드포인트와 권한을 매핑
        '''
        apiPermissionMap = {};

        apiPermissionMap['das/config'] = ['wm_das_config']


        # files
        apiPermissionMap['files/bom_download'] = ['wm_bom']
        apiPermissionMap['files/download'] = ['wm_file_document']
        apiPermissionMap['files/excel_export'] = ['']
        apiPermissionMap['files/get_hmi_image'] = ['wm_hmi_form_b'] 
        apiPermissionMap['files/haccp_diary'] = ['wm_haccp_dialy']
        apiPermissionMap['files/image'] = ['wm_equip','wm_image_list']
        apiPermissionMap['files/img_down'] = ['']
        apiPermissionMap['files/joborder_export'] = ['']
        apiPermissionMap['files/mes_form'] = ['wm_person_work_schedule','wm_suju_upload' ]
        apiPermissionMap['files/set_name_multi_text'] = ['']
        apiPermissionMap['files/set_name_text'] = ['']

        apiPermissionMap['files/upload'] = ['']

        # support 
        apiPermissionMap['support/calendar'] = ['wm_meeting_calendar']
        apiPermissionMap['support/cust_complain'] = ['']
        apiPermissionMap['support/document'] = ['wm_file_document','wm_sample_js_gantt']
        apiPermissionMap['support/excel_document'] = ['wm_excel_documant_a']
        apiPermissionMap['support/excel_form'] = ['wm_excel_form']
        apiPermissionMap['support/hmi'] = ['wm_hmi_form']
        apiPermissionMap['support/hmi_b'] = ['wm_hmi_form_b', 'wm_dashboard_hmi']
        apiPermissionMap['support/html_document'] = ['wm_html_document_a']
        apiPermissionMap['support/html_form'] = ['wm_html_form']
        apiPermissionMap['support/image_list'] = ['wm_image_list']
        apiPermissionMap['support/notice'] = ['wm_notice_board']
        apiPermissionMap['support/work_calendar'] = ['wm_work_calendar']

        # system
        apiPermissionMap['system/batch_log'] = ['wm_batch_log']
        apiPermissionMap['system/code'] = ['wm_code']
        apiPermissionMap['system/combo'] = ['']
        apiPermissionMap['system/bookmark'] = ['']
        apiPermissionMap['system/das_server'] = ['']
        apiPermissionMap['system/das_config'] = ['wm_das_config']
        apiPermissionMap['system/factory_setup'] = ['']
        apiPermissionMap['system/grid_setting'] = ['']
        apiPermissionMap['system/gui'] = ['']
        apiPermissionMap['system/labelcode'] = ['wm_multi_language']
        apiPermissionMap['system/menu_language'] = ['wm_menu_language']


        cls.__dic_view_menu__ = apiPermissionMap
        return apiPermissionMap

    @classmethod
    def get_menu_code_by_taskview(cls, task_name, view_name):
        ''' definition, material 로 연관된 메뉴코드 리스트를 찾느다.
        '''
        #apiPermissionMap = cls.taskview_menu_code_map()  # DB에서 읽은 걸로 대치?
        apiPermissionMap = cls.__dic_view_menu__  # DB에서 읽은 걸로 대치?
        task_view = task_name + '/' + view_name
        menu_code = None
        if task_view in apiPermissionMap.keys():
            menu_code = apiPermissionMap[task_view]
        return menu_code