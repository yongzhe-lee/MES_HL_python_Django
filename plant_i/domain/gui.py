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
        gui_dc['wm_dt_main'] = cls.gui_item('생산라인현황', 'dashboard/dt_main.html')# 생산라인현황

        gui_dc['wm_storyboard'] = cls.gui_item('스토리보드', 'dashboard/storyboard.html')#스토리보드

        # AAS 관련 메뉴   -> AAS조회,  Asset조회, AASX관리
        gui_dc['wm_aas'] = cls.gui_item('AAS조회', 'aas/aas.html')
        gui_dc['wm_asset'] = cls.gui_item('Asset조회', 'aas/asset.html')
        gui_dc['wm_aasx'] = cls.gui_item('AASX관리', 'aas/aasx.html')

        #################################################  KMMS  #####################################################
        #설비정보
        gui_dc['wm_cm_equipment'] = cls.gui_item('설비마스터', 'kmms/equipment/cm_equipment.html')
        gui_dc['wm_cm_equip_disposed'] = cls.gui_item('불용설비', 'kmms/equipment/cm_equip_disposed.html')
        gui_dc['wm_cm_equip_workhist'] = cls.gui_item('설비별작업이력', 'kmms/equipment/cm_equip_workhist.html')

        #cmms 정비자재
        gui_dc['wm_cm_material'] = cls.gui_item('자재마스터', 'kmms/material/cm_material.html')

        #작업지시
        gui_dc['wm_my_work_request'] = cls.gui_item('작업요청', 'kmms/wo/my_work_request.html')
        gui_dc['wm_work_request_approval'] = cls.gui_item('작업요청승인', 'kmms/wo/work_request_approval.html')
        gui_dc['wm_work_order_approval'] = cls.gui_item('작업지시승인', 'kmms/wo/work_order_approval.html')
        gui_dc['wm_work_order_management'] = cls.gui_item('작업지시 관리', 'kmms/wo/work_order_management.html')
        gui_dc['wm_post_work_management'] = cls.gui_item('사후작업 관리', 'kmms/wo/post_work_management.html')

        #예방정비(PM)
        gui_dc['wm_pm_master'] = cls.gui_item('PM 마스터', 'kmms/pm/pm_master.html')
        gui_dc['wm_pm_schedule'] = cls.gui_item('PM 작업일정', 'kmms/pm/pm_schedule.html')
        gui_dc['wm_pm_work'] = cls.gui_item('PM 마스터별 WO', 'kmms/pm/pm_work_list.html')
        gui_dc['wm_pm_schedule_m'] = cls.gui_item('PM 일정생성(수동)', 'kmms/pm/pm_schedule_m.html')

        #작업이력
        gui_dc['wm_wo_hist'] = cls.gui_item('WO 작업이력 조회', 'kmms/wo/work_order_hist.html')
        gui_dc['wm_wo_cancel'] = cls.gui_item('취소된 WO 목록', 'kmms/wo/work_order_cancel_list.html')
        gui_dc['wm_wo_pending'] = cls.gui_item('미처리 WO 목록', 'kmms/wo/work_order_pending_list.html')

        # 예방점검(PI)
        gui_dc['wm_check_master'] = cls.gui_item('점검마스터관리', 'kmms/check/check_master.html')
        gui_dc['wm_check_schedule'] = cls.gui_item('점검 작업일정', 'kmms/check/check_schedule.html')       
        gui_dc['wm_check_result'] = cls.gui_item('점검 결과 조회', 'kmms/check/check_result.html')
        gui_dc['wm_check_wo_issued'] = cls.gui_item('점검이상 발행WO', 'kmms/check/check_wo_issued.html')
        gui_dc['wm_create_inspection_schedule_manual'] = cls.gui_item('점검 일정생성(수동)', 'kmms/check/check_schedule_m.html')    

        #설비통계        
        gui_dc['wm_facility_monthly_status'] = cls.gui_item('설비별 월간 고장현황', 'kmms/report/facility_monthly_status.html')
        gui_dc['wm_monthly_maintenance_cost'] = cls.gui_item('설비별 월간 정비비용', 'kmms/report/monthly_maintenance_cost.html')
        gui_dc['wm_facility_treatment_status'] = cls.gui_item('기간별 불용처리 설비 현황', 'kmms/report/facility_treatment_status.html')
        gui_dc['wm_facility_mttr_mtbf'] = cls.gui_item('설비별 MTTR/MTBF', 'kmms/report/facility_mttr_mtbf.html')
        gui_dc['wm_category_equipment_status'] = cls.gui_item('카테고리별 설비 현황', 'kmms/report/category_equipment_status.html')
        gui_dc['wm_critical_equipment_status'] = cls.gui_item('중요도별 설비 고장 현황', 'kmms/report/critical_equipment_status.html')
        gui_dc['wm_facility_maintenance_cost'] = cls.gui_item('설비별 정비비용', 'kmms/report/facility_maintenance_cost.html')
        gui_dc['wm_facility_downtime'] = cls.gui_item('설비별 고장시간', 'kmms/report/facility_downtime.html')
        gui_dc['wm_facility_specifications'] = cls.gui_item('설비별 사양 목록', 'kmms/report/facility_specifications.html')
        

        #작업통계
        gui_dc['wm_wo_dept_performance'] = cls.gui_item('부서별 기간별 WO 발행 실적', 'kmms/report/wm_wo_dept_performance.html')
        gui_dc['wm_dept_work_costs'] = cls.gui_item('부서별 기간별 작업비용', 'kmms/report/dept_work_costs.html')
        gui_dc['wm_top_working_hours_wo'] = cls.gui_item('작업시간 상위 WO', 'kmms/report/top_working_hours_wo.html')
        gui_dc['wm_conservation_cost_status'] = cls.gui_item('보전비용 현황', 'kmms/report/conservation_cost_status.html')
        gui_dc['wm_top_wo_in_work_cost'] = cls.gui_item('작업비용 상위 WO', 'kmms/report/top_wo_in_work_cost.html')
        gui_dc['wm_outsourced_tasks_count'] = cls.gui_item('아웃소싱 작업건수', 'kmms/report/outsourced_tasks_count.html')
        gui_dc['wm_dept_pm_rate'] = cls.gui_item('부서별 예방 정비율', 'kmms/report/dept_pm_rate.html')
        gui_dc['wm_team_breakdown_costs'] = cls.gui_item('팀별 고장비용 현황', 'kmms/report/team_breakdown_costs.html')
        gui_dc['wm_dept_overdue_tasks'] = cls.gui_item('부서별 기간별 지연작업 목록', 'kmms/report/dept_overdue_tasks.html')
        gui_dc['wm_dept_task_compliance_rate'] = cls.gui_item('부서별 기간별 작업 준수율', 'kmms/report/dept_task_compliance_rate.html')
        gui_dc['wm_causes_of_each_failure_part'] = cls.gui_item('고장부위별 원인', 'kmms/report/causes_of_each_failure_part.html')
        gui_dc['wm_dept_work_request_stats'] = cls.gui_item('부서별 작업 요청 통계', 'kmms/report/dept_work_request_stats.html')        

        #PM통계
        gui_dc['wm_pm_status_by_category'] = cls.gui_item('카테고리별 PM현황', 'kmms/report/pm_status_by_category.html')
        gui_dc['wm_pm_wo_completion_rate'] = cls.gui_item('부서별 PM WO 완료율', 'kmms/report/pm_wo_completion_rate.html')

        #점검통계
        gui_dc['wm_facility_inspection_master'] = cls.gui_item('설비종류별 점검마스터', 'kmms/report/facility_inspection_master.html')
        gui_dc['wm_inspection_issues'] = cls.gui_item('점검결과 이상 설비목록', 'kmms/report/inspection_issues.html')
        gui_dc['wm_inspection_stats'] = cls.gui_item('점검 수행 통계', 'kmms/report/inspection_stats.html')

        #코드관리
        gui_dc['wm_cm_code'] = cls.gui_item('기초코드', 'kmms/cm_code.html')
        gui_dc['wm_supplier'] = cls.gui_item('공급업체', 'kmms/material/supplier.html')       
        gui_dc['wm_cm_material_loc'] = cls.gui_item('자재보관위치', 'kmms/material/storLocAddrList.html')        
        gui_dc['wm_cm_equip_loc'] = cls.gui_item('설비위치정보', 'kmms/equipment/locList.html')
        gui_dc['wm_cm_equip_group'] = cls.gui_item('설비분류', 'kmms/equipment/equipmentGroupList.html')       
        gui_dc['wm_cm_wo_project'] = cls.gui_item('프로젝트', 'kmms/wo/projectList.html')
        gui_dc['wm_cm_holiday'] = cls.gui_item('휴일 스케줄', 'kmms/holidayCustom.html')

        #사이트 옵션
        gui_dc['wm_proc_opts'] = cls.gui_item('프로세스', 'kmms/proc_opts.html')
        gui_dc['wm_sche_opts'] = cls.gui_item('스케줄링', 'kmms/sche_opts.html')

        #################################################  MES  #####################################################
        #기준정보
        gui_dc['wm_factory'] = cls.gui_item('공장', 'definition/factory.html')
        gui_dc['wm_line'] = cls.gui_item('라인', 'definition/line.html')
        gui_dc['wm_process'] = cls.gui_item('공정', 'definition/process.html')
        gui_dc['wm_material'] = cls.gui_item('품목(자재)', 'definition/material.html') 
        gui_dc['wm_bom'] = cls.gui_item('BOM', 'definition/bom.html')
        gui_dc['wm_defect'] = cls.gui_item('부적합정보', 'definition/defect.html')
        gui_dc['wm_shift'] = cls.gui_item('조교대정보', 'definition/shift.html')
        gui_dc['wm_line_inactive'] = cls.gui_item('라인비가동정보', 'definition/line_inactive.html')
        gui_dc['wm_model_change'] = cls.gui_item('기종변경정보', 'definition/model_change.html')        
        # gui_dc['wm_holiday'] = cls.gui_item('휴일 스케줄', 'definition/holiday.html')#휴일 스케줄
        # gui_dc['wm_company'] = cls.gui_item('업체', 'definition/company.html')#업체 

        # 설비관리
        gui_dc['wm_equip_group'] = cls.gui_item('설비그룹', 'definition/equip_group.html')
        gui_dc['wm_equipment'] = cls.gui_item('설비', 'definition/equipment.html')
        gui_dc['wm_equ_alm'] = cls.gui_item('설비Alarm관리', 'definition/equipment_alaram.html')
        gui_dc['wm_equ_alm_hist'] = cls.gui_item('설비Alarm이력', 'definition/equipment_alaram_history.html')
        gui_dc['wm_tag_group'] = cls.gui_item('태그그룹', 'definition/tag_group.html')
        gui_dc['wm_tag_master'] = cls.gui_item('태그관리', 'definition/tag.html')
        gui_dc['wm_das_config'] = cls.gui_item('데이터수집설정', 'system/das_config.html')

        # 데이터분석
        gui_dc['wm_tag_data_current'] = cls.gui_item('태그데이터현황', 'tagdata/tag_current.html')
        gui_dc['wm_tag_data_list'] = cls.gui_item('태그데이터조회', 'tagdata/tagdata_list.html')
        gui_dc['wm_tag_summary'] = cls.gui_item('데이터통계', 'tagdata/tag_statistics.html')
        gui_dc['wm_tag_trend'] = cls.gui_item('데이터트렌드', 'tagdata/tag_trend.html')
        gui_dc['wm_tag_boxplot'] = cls.gui_item('상자수염그림', 'tagdata/tag_boxplot.html')        
        gui_dc['wm_tag_histogram'] = cls.gui_item('히스토그램', 'tagdata/tag_histogram.html')
        gui_dc['wm_tag_scatter'] = cls.gui_item('산점도', 'tagdata/tag_scatter.html')        
        gui_dc['wm_regression_a'] = cls.gui_item('산점도-회귀분석', 'tagdata/regression_a.html')

        # AI 
        gui_dc['wm_ai_model'] = cls.gui_item('모델 관리', 'ai/model.html')
        gui_dc['wm_ai_tag_group'] = cls.gui_item('AI시스템 운영관리', 'ai/tag_group.html')
        gui_dc['wm_ai_tag'] = cls.gui_item('AI시스템 참조데이터 관리', 'ai/tag.html')
        gui_dc['wm_ai_tagdata_list'] = cls.gui_item('AI시스템 IF 확인', 'ai/tagdata_list.html')
        gui_dc['wm_predictive_conservation'] = cls.gui_item('예지보전 알람', 'ai/predictive_conservation.html')
        gui_dc['wm_learning_data_info'] = cls.gui_item('학습데이터 정보', 'ai/learning_data_info.html')
        gui_dc['wm_learning_data_from_tag'] = cls.gui_item('학습데이터 정보(태그)', 'ai/learning_data_from_tag.html')

        # 업무지원
        gui_dc['wm_calendar'] = cls.gui_item('캘린더', 'definition/meeting_calendar.html')
        gui_dc['wm_board'] = cls.gui_item('공지사항', 'definition/notice_board.html')

        # 시스템코드
        gui_dc['wm_code'] = cls.gui_item('기초코드', 'definition/code.html')         

        # 시스템관리
        gui_dc['wm_user'] = cls.gui_item('사용자', 'system/user.html')
        gui_dc['wm_user_group'] = cls.gui_item('사용자그룹', 'system/user_group.html') 
        gui_dc['wm_user_group_menu'] = cls.gui_item('메뉴권한', 'system/user_group_menu.html')        
        gui_dc['wm_depart'] = cls.gui_item('부서', 'system/depart.html')  
        gui_dc['wm_storyboard_config'] = cls.gui_item('스토리보드설정', 'system/storyboard_config.html')
        gui_dc['wm_login_log'] = cls.gui_item('로그인로그', 'system/login_log.html')
        gui_dc['wm_menu_log'] = cls.gui_item('메뉴로그', 'system/menu_log.html')
        gui_dc['wm_system_log'] = cls.gui_item('시스템로그', 'system/system_log.html')

        # I/F 이력조회, ERP, 생산설비측정데이터, QMS, VAN, 인사정보
        #gui_dc['wm_if_sap'] = cls.gui_item('SAP', 'interface/if_sap.html')
        gui_dc['wm_if_sap_mat'] = cls.gui_item('SAP Material', 'interface/sap/if_sap_mat.html') #품목정보
        gui_dc['wm_if_sap_bom'] = cls.gui_item('SAP BOM', 'interface/sap/if_sap_bom.html') # BOM
        gui_dc['wm_if_sap_stock'] = cls.gui_item('SAP Stock', 'interface/sap/if_sap_stock.html') # 품목별 위치별 재고
        gui_dc['wm_if_sap_pcb_random'] = cls.gui_item('SAP PCB Rand.', 'interface/sap/if_sap_pcb_random.html') # PCB 난수번호별 입고번호조회

        # I/F mes  lot_hostory, Fpy data, ActiveWorkOrder, WorkOrderList, ProductPlanExcel, ProductPlanAll, 
        gui_dc['wm_if_mes_lot_history'] = cls.gui_item('LOT Hist.', 'interface/mes/if_mes_lot_history.html')
        gui_dc['wm_if_mes_fpy'] = cls.gui_item('FPY조회', 'interface/mes/if_mes_fpy_data.html')
        gui_dc['wm_if_mes_workorder'] = cls.gui_item('작업지시', 'interface/mes/if_mes_workorder.html') # 작업지시목록 및 현재 액티브된 워크오더 조회
        gui_dc['wm_if_mes_product_plan'] = cls.gui_item('생산계획', 'interface/mes/if_mes_product_plan.html') # 엑셀데이터포함
        gui_dc['wm_if_mes_oee'] = cls.gui_item('생산계획', 'interface/mes/if_mes_oee.html') # 엑셀데이터포함

        # SMT관련 
        gui_dc['wm_if_mnt_pickup_rate'] = cls.gui_item('마운터 Pickup Rate', 'interface/smt/if_mnt_pickup_rate.html')
        gui_dc['wm_if_viscosity_check'] = cls.gui_item('솔더점도측정', 'interface/smt/if_viscosity_check.html')
        gui_dc['wm_if_tension_check'] = cls.gui_item('스텐실텐션체크', 'interface/smt/if_tension_check.html')
        gui_dc['wm_if_reflow_profile'] = cls.gui_item('Reflow Profile', 'interface/smt/if_reflow_profile.html')

        # 제어PC 데이터
        gui_dc['wm_if_equ_result'] = cls.gui_item('설비실적(측정데이터)', 'interface/if_equ_result.html')

        gui_dc['wm_if_qms'] = cls.gui_item('QMS', 'interface/if_qms.html')
        gui_dc['wm_if_van'] = cls.gui_item('VAN', 'interface/if_van.html')        
        gui_dc['wm_if_topic_data'] = cls.gui_item('TOPIC데이터확인', 'interface/if_topic_data.html')
        gui_dc['wm_if_log'] = cls.gui_item('인터페이스로그확인', 'interface/if_log.html')


        # kendo ui 샘플화면
        gui_dc['wm_sample_test'] = cls.gui_item('샘플화면(test)', 'sample_page/test.html')
        gui_dc['wm_sample_treelist'] = cls.gui_item('샘플1_트리그리드', 'sample_page/tree_list.html')
        gui_dc['wm_sample_form'] = cls.gui_item('샘플2_폼화면', 'sample_page/form.html')
        gui_dc['wm_sample_chart'] = cls.gui_item('샘플3_차트', 'sample_page/chart.html')
        gui_dc['wm_sample_popup'] = cls.gui_item('샘플4_팝업', 'sample_page/popup.html')
        gui_dc['wm_sample_editor'] = cls.gui_item('샘플5_웹에디터', 'sample_page/editor.html')
        gui_dc['wm_sample_spread_sheet'] = cls.gui_item('샘플6_스프레드시트', 'sample_page/spread_sheet.html')
        gui_dc['wm_sample_upload'] = cls.gui_item('샘플7_파일업로드', 'sample_page/upload.html')
        gui_dc['wm_sample_alert_noti'] = cls.gui_item('샘플8_알람_노티', 'sample_page/alert_notification.html')
        gui_dc['wm_sample_export'] = cls.gui_item('샘플9_Export', 'sample_page/export.html')
        gui_dc['wm_sample_design'] = cls.gui_item('샘플10_디자인', 'sample_page/design.html')

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