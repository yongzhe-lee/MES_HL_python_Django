from configurations import settings

from domain.models.system import LabelCode, LabelCodeLanguage, SystemCode
from domain.models.system import MenuFolder, MenuItem

from domain.gui import GUIConfiguration
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.sql import DbUtil


class SystemSetupService():

    def get_folder_menu_list(self):
        if settings.DBMS == 'MSSQL':
            sql = ''' with folder_tree as 
                   (
                     select 
                        id
                        , "FolderName"
                        , convert(varchar,"IconCSS") as "IconCSS"
                        , "Parent_id"
                        , "_order"
                        , 1 as depth
                     from menu_folder mf 
                     where "Parent_id" is null
                     union all
                     select 
                       mf2.id
                       , mf2."FolderName"
                       , convert(varchar,mf2."IconCSS") as "IconCSS"
                       , mf2."Parent_id"
                       , mf2."_order"
                       , t.depth+1 as depth
                     from menu_folder mf2 
                     inner join folder_tree t on t.id = mf2."Parent_id"
                   ) 
				   , menu_tree as 
					(
                    select 
                      id
                      , convert(varchar, '') as menu_code
                      ,"FolderName" as name
                      ,"IconCSS" as css
                      , "Parent_id" as pid
                      , "_order"
                      , depth
                      , convert(varchar, 'folder') as data_div 
                    from folder_tree   
                    union all
                    select 
                    null as id
                    , convert(varchar, mi."MenuCode") as menu_code
                    , mi."MenuName"  as name
                    , convert(varchar, '') as css 
                    , mi."MenuFolder_id" as pid
                    , mi."_order" 
                    , menu_tree.depth+1 as depth 
                    , convert(varchar, 'menu') as data_div 
                    from menu_item mi 
                    inner join menu_tree on mi."MenuFolder_id" = menu_tree.id

                )
                select id, menu_code, name, css, pid, _order, depth, data_div 
                from menu_tree
                '''
        else:
            sql = ''' with recursive menu_tree as 
                (
                   with recursive folder_tree as 
                   (
                     select 
                        id
                        , "FolderName"
                        , "IconCSS"::text
                        , "Parent_id"
                        , "_order"
                        , 1 as depth
                     from menu_folder mf 
                     where "Parent_id" is null
                     union all
                     select 
                       mf2.id
                       , mf2."FolderName"
                       , mf2."IconCSS"::text
                       , mf2."Parent_id"
                       , mf2."_order"
                       , t.depth+1 as depth
                     from menu_folder mf2 
                         inner join folder_tree t on t.id = mf2."Parent_id"
                   ) 
                    select 
                      id
                      , ''::text as menu_code
                      ,"FolderName" as name
                      ,"IconCSS"::text as css
                      , "Parent_id" as pid
                      , "_order"
                      , depth
                      , 'folder' as data_div 
                    from folder_tree   
                    union all
                    select 
                    null as id
                    , mi."MenuCode" as menu_code
                    , mi."MenuName"  as name
                    ,''::text as css 
                    , mi."MenuFolder_id" as pid
                    , mi."_order" 
                    , menu_tree.depth+1 as depth 
                    , 'menu' as data_div 
                    from menu_item mi 
                       inner join menu_tree on mi."MenuFolder_id" = menu_tree.id
                )
                select id, menu_code, name, css, pid, _order, depth, data_div 
                from menu_tree
                
            '''
        items = []
        try:
            items = DbUtil.get_rows(sql, {})
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemSetupService.get_folder_menu_list', ex)
            raise ex

        return items


    def menu_folder(slef, title, css):
        foo = {
                'name': title, 'css':css, 'type':'folder', 'folders':[], 
                #'order':10,
                'menus':[],
             }
        return foo

    def setup_menu(self):

        if MenuFolder.objects.all().count() > 0:
            MenuItem.objects.all().delete();
            MenuFolder.objects.all().delete();

        '''
        기존 사용하는 아이콘 클래스(폴더에만 적용된다, 메뉴아이템에서는 아이콘 없음)
        기준정보 : fa-info-circle
        사용자관리 : fa-user-friends
        시스템관리 : fa-cogs
        권한관리 : fa-desktop
        메시지관리 : fa-globe
        게시판 : fa-clipboard-list
        샘플화면 : fa-vial
        개발tool : fa-tools
        '''
        try:
            menufolders = []

            # 김하늘 수정 24.10.21
            folder = self.menu_folder('시스템관리', 'manufacturing')
            folder['menus'].append('wm_user_group')
            folder['menus'].append('wm_user')
            folder['menus'].append('wm_user_group_menu')
            menufolders.append(folder)
            
            now_time = DateUtil.get_current_datetime()  
            
            menu_order = 10
            for f1 in menufolders:
                try:
                    nodes = f1.get('nodes')
                    name = f1.get('name')
                    css = f1.get('css')
                    #order = f1.get('order')
                    level1_menus = f1.get('menus')
                    subfolders1 = f1.get('folders')

                    # 폴더 저장
                    menufolder1 = MenuFolder(FolderName=name, IconCSS=css, _order=menu_order)
                    menufolder1._created = now_time
                    menufolder1.save()
                    menu_order = menu_order + 10
                except Exception as ex4:
                    print(ex4)

                # 메뉴저장
                menu_order = 10
                if len(level1_menus) > 0:
                    for m1 in level1_menus:
                        try:
                            gui = GUIConfiguration.get_gui_info(m1)
                            url = '/gui/'+m1
                            print(url)
                            menu_name = gui.get('name')
                            gui_templates = gui.get('templates')
                            default_template = gui_templates.get('default')
                            popup = gui_templates.get('popup')

                            menuitem = MenuItem()
                            menuitem.MenuCode = m1
                            menuitem.MenuName = menu_name
                            menuitem.IconCSS = None
                            menuitem.Url = url
                            menuitem.MenuFolder = menufolder1
                            menuitem._order = menu_order 
                            menuitem.Popup = popup
                            menuitem._created = now_time
                            menuitem.save()
                            menu_order = menu_order + 10
                        except Exception as ex3:
                            print(ex3)

                # 하위폴더
                if len(subfolders1)>0:
                    for f2 in subfolders1:
                        try:
                            nodes = f2.get('nodes')
                            name = f2.get('name')
                            css = f2.get('css')
                            order = f2.get('order')
                            menus = f2.get('menus')
                            subfolders2 = f2.get('folders')
                            menufolder2 = MenuFolder(FolderName=name, IconCSS=css, _order=order)
                            menufolder2._created = now_time
                            menufolder2.save()
                        except Exception as ex2:
                            print(ex)

        except Exception as ex:
            print(ex)

        return True


    def setup_systemcode(self):
        '''
        
        '''
        syscode_items =[
            # BOM구분
            {'CodeType':'bom_type', 'Code':'manufacturing', 'Value':'제조BOM', 'Description':'BOM구분'},
            {'CodeType':'bom_type', 'Code':'engineering', 'Value':'설계BOM', 'Description':'BOM구분'},

            #업체구분
            {'CodeType':'company_type', 'Code':'purchase', 'Value':'거래처', 'Description':'업체구분'},
            {'CodeType':'company_type', 'Code':'sale', 'Value':'판매처', 'Description':'업체구분'},
            {'CodeType':'company_type', 'Code':'outsourcing', 'Value':'외주사', 'Description':'업체구분'},
            {'CodeType':'company_type', 'Code':'equip-maker', 'Value':'설비제작사', 'Description':'업체구분'},

            # 부적합유형, 비가동사유 적용범위
            {'CodeType':'coverage', 'Code':'process', 'Value':'공정별', 'Description':'적용범위. 공정에만 적용'},
            {'CodeType':'coverage', 'Code':'all', 'Value':'전체', 'Description':'적용범위. 전체에 적용'},

            #설비구분
            {'CodeType':'equipment_type', 'Code':'manufacturing', 'Value':'생산', 'Description':'설비구분'},
            {'CodeType':'equipment_type', 'Code':'etc', 'Value':'기타', 'Description':'설비구분'},

            # 설비자산성여부
            {'CodeType':'equip_asset_yn', 'Code':'Y', 'Value':'자산성', 'Description':'설비자산성여부'},
            {'CodeType':'equip_asset_yn', 'Code':'N', 'Value':'소모성', 'Description':'설비자산성여부'},

            # 설비정비구분
            {'CodeType':'equip_maint_type', 'Code':'prevention', 'Value':'예방정비', 'Description':'설비정비구분'},
            {'CodeType':'equip_maint_type', 'Code':'failure', 'Value':'고장정비', 'Description':'설비정비구분'},
            
            # 설비가동상태
            {'CodeType':'equip_run_state', 'Code':'R', 'Value':'가동', 'Description':'설비가동상태'},
            {'CodeType':'equip_run_state', 'Code':'X', 'Value':'비가동', 'Description':'설비가동상태'},

            # 설비가동구분
            {'CodeType':'equip_run_type', 'Code':'auto', 'Value':'자동입력', 'Description':'설비가동구분'},
            {'CodeType':'equip_run_type', 'Code':'manual', 'Value':'수입력', 'Description':'설비가동구분'},

           # 설비상태
            {'CodeType':'equip_state', 'Code':'normal', 'Value':'정상', 'Description':'설비상태'},
            {'CodeType':'equip_state', 'Code':'failure', 'Value':'고장', 'Description':'설비상태'},
            {'CodeType':'equip_state', 'Code':'checking', 'Value':'점검중', 'Description':'설비상태'},

            #양식구분
            {'CodeType':'form_type', 'Code':'hmi', 'Value':'HMI양식', 'Description':'양식구분'},
            {'CodeType':'form_type', 'Code':'excel', 'Value':'엑셀양식', 'Description':'양식구분'},
            {'CodeType':'form_type', 'Code':'html', 'Value':'HTML양식', 'Description':'양식구분'},
            {'CodeType':'form_type', 'Code':'file', 'Value':'파일', 'Description':'양식구분'},

            # 작업실적상태
            {'CodeType':'job_state', 'Code':'planned', 'Value':'계획', 'Description':'작업실적상태'},
            {'CodeType':'job_state', 'Code':'ordered', 'Value':'지시', 'Description':'작업실적상태'},
            {'CodeType':'job_state', 'Code':'working', 'Value':'작업중', 'Description':'작업실적상태'},
            {'CodeType':'job_state', 'Code':'finished', 'Value':'완료', 'Description':'작업실적상태'},
            {'CodeType':'job_state', 'Code':'stopped', 'Value':'중지', 'Description':'작업실적상태'},
            {'CodeType':'job_state', 'Code':'canceled', 'Value':'취소', 'Description':'작업실적상태'},
            {'CodeType':'job_state', 'Code':'waiting', 'Value':'대기', 'Description':'제품생산상태'},
            
            #hierarchy_level
            {'CodeType':'hierarchy_level', 'Code':'area', 'Value':'Area', 'Description':'위치레벨'},
            {'CodeType':'hierarchy_level', 'Code':'workcenter', 'Value':'워크센터', 'Description':'위치레벨'},

            #자재입출고 상태
            {'CodeType':'inout_state', 'Code':'waiting', 'Value':'미확인', 'Description':'자재입고상태'}, 
            {'CodeType':'inout_state', 'Code':'confirmed', 'Value':'확인', 'Description':'자재입고상태'},
            {'CodeType':'inout_state', 'Code':'canceled', 'Value':'취소', 'Description':'자재입고상태'},

            #자재입출고 입출구분
            {'CodeType':'inout_type', 'Code':'in', 'Value':'입고', 'Description':'입출구분'},
            {'CodeType':'inout_type', 'Code':'out', 'Value':'출고', 'Description':'입출구분'},
            
            #자재입고구분
            {'CodeType':'input_type', 'Code':'order_in', 'Value':'구매입고', 'Description':'발주구매입고'}, 
            {'CodeType':'input_type', 'Code':'produced_in', 'Value':'생산입고', 'Description':'제품,반제품 생산 후 입고'},
            {'CodeType':'input_type', 'Code':'move_in', 'Value':'이동입고', 'Description':'창고 이동으로 입고'},
            {'CodeType':'input_type', 'Code':'gap_in', 'Value':'실사잉여', 'Description':'재고실사 후 잉여량 입고'},
            {'CodeType':'input_type', 'Code':'etc_in', 'Value':'기타입고', 'Description':'기타'},

            # 언어구분
            {'CodeType':'lang_code', 'Code':'ko-KR', 'Value':'한국어', 'Description':'언어구분'},
            {'CodeType':'lang_code', 'Code':'en-US', 'Value':'영어', 'Description':'언어구분'},
            #{'CodeType':'lang_code', 'Code':'ja-JP', 'Value':'일본어', 'Description':''},
            #{'CodeType':'lang_code', 'Code':'zh-CN', 'Value':'중국어(중국)', 'Description':''},
            #{'CodeType':'lang_code', 'Code':'zh-TW', 'Value':'중국어(대만)', 'Description':''},
            
            # 자재발주 상태
            {'CodeType':'mat_order_state', 'Code':'registered', 'Value':'등록', 'Description':'자재발주 상태'},
            {'CodeType':'mat_order_state', 'Code':'approved', 'Value':'승인', 'Description':'자재발주 상태'},
            {'CodeType':'mat_order_state', 'Code':'rejected', 'Value':'반려', 'Description':'자재발주 상태'},

            # 품목필요량 품목구분
            {'CodeType':'mat_requ_mat_type', 'Code':'product', 'Value':'제품', 'Description':'품목필요량 품목구분'},
            {'CodeType':'mat_requ_mat_type', 'Code':'semi', 'Value':'반제품', 'Description':'품목필요량 품목구분'},
            {'CodeType':'mat_requ_mat_type', 'Code':'material', 'Value':'원부자재', 'Description':'품목필요량 품목구분'},

            # 자재공정투입상태
            {'CodeType':'mat_proc_input_state', 'Code':'requested', 'Value':'요청', 'Description':'자재공정투입상태'},
            {'CodeType':'mat_proc_input_state', 'Code':'executed', 'Value':'실행', 'Description':'자재공정투입상태'},

            # 품목구분
            {'CodeType':'mat_type', 'Code':'product', 'Value':'제품', 'Description':'품목구분'},
            {'CodeType':'mat_type', 'Code':'semi', 'Value':'반제품', 'Description':'품목구분'},
            {'CodeType':'mat_type', 'Code':'raw_mat', 'Value':'원재료', 'Description':'품목구분'},
            {'CodeType':'mat_type', 'Code':'sub_mat', 'Value':'부자재', 'Description':'품목구분'},
                       
            #자재출고구분
            {'CodeType':'output_type', 'Code':'consumed_out', 'Value':'생산투입출고', 'Description':'생산투입 위해 출고'}, 
            {'CodeType':'output_type', 'Code':'shipped_out', 'Value':'제품출하출고', 'Description':'제품출하 출고'}, 
            {'CodeType':'output_type', 'Code':'move_out', 'Value':'이동출고', 'Description':'창고 이동으로 출고'}, 
            {'CodeType':'output_type', 'Code':'gap_out', 'Value':'실사부족', 'Description':'재고실사 후 부족량 입고'}, 
            {'CodeType':'output_type', 'Code':'etc_out', 'Value':'기타출고', 'Description':'기타'}, 
            {'CodeType':'output_type', 'Code':'disposal_out', 'Value':'폐기', 'Description':'폐기'}, 
                                    
            #작업자구분
            {'CodeType':'person_type', 'Code':'production', 'Value':'작업자', 'Description':'작업자구분'},
            {'CodeType':'person_type', 'Code':'sales', 'Value':'영업담당자', 'Description':'작업자구분'},
            {'CodeType':'person_type', 'Code':'office', 'Value':'사무직', 'Description':'작업자구분'},
            
            #비가동사유 계획비계획구분
            {'CodeType':'plan_yn', 'Code':'Y', 'Value':'계획', 'Description':'계획비계획구분'},
            {'CodeType':'plan_yn', 'Code':'N', 'Value':'비계획', 'Description':'계획비계획구분'},
            
            # 생산계획상태
            {'CodeType':'prod_week_term_state', 'Code':'none', 'Value':'미계획', 'Description':'생산계획상태'},
            {'CodeType':'prod_week_term_state', 'Code':'product', 'Value':'제품확정', 'Description':'생산계획상태'},
            {'CodeType':'prod_week_term_state', 'Code':'semi', 'Value':'반제품확정', 'Description':'생산계획상태'},
            {'CodeType':'prod_week_term_state', 'Code':'material', 'Value':'원부자재확정', 'Description':'생산계획상태'},
                       
            #결과값유형
            {'CodeType':'result_type', 'Code':'N', 'Value':'수치값', 'Description':'결과값유형'},
            {'CodeType':'result_type', 'Code':'S', 'Value':'선택형', 'Description':'결과값유형'},
            {'CodeType':'result_type', 'Code':'D', 'Value':'서술형', 'Description':'결과값유형'},
            
            # 출하상태
            {'CodeType':'shipment_state', 'Code':'ordered', 'Value':'지시', 'Description':'출하상태'},
            {'CodeType':'shipment_state', 'Code':'shipped', 'Value':'출하', 'Description':'출하상태'},

            #규격유형
            {'CodeType':'spec_type', 'Code':'x', 'Value':'규격없음', 'Description':'규격유형'},            
            {'CodeType':'spec_type', 'Code':'upper', 'Value':'상한이하', 'Description':'규격유형'},            
            {'CodeType':'spec_type', 'Code':'low', 'Value':'하한이상', 'Description':'규격유형'},            
            {'CodeType':'spec_type', 'Code':'range', 'Value':'범위', 'Description':'규격유형'},            
            {'CodeType':'spec_type', 'Code':'just', 'Value':'정성규격', 'Description':'규격유형'},     
                        
            # 표준시간단위
            {'CodeType':'standard_time_unit', 'Code':'minute', 'Value':'분', 'Description':'표준시간단위'},
            {'CodeType':'standard_time_unit', 'Code':'second', 'Value':'초', 'Description':'표준시간단위'},
            {'CodeType':'standard_time_unit', 'Code':'hour', 'Value':'시간', 'Description':'표준시간단위'},
            {'CodeType':'standard_time_unit', 'Code':'day', 'Value':'일', 'Description':'표준시간단위'},

            #스토리보드 항목구분
            {'CodeType':'story_board_type', 'Code':'menu', 'Value':'메뉴', 'Description':'스토리보드 항목구분'},
            {'CodeType':'story_board_type', 'Code':'hmi', 'Value':'HMI양식', 'Description':'스토리보드 항목구분'},
                        
            #창고구분
            {'CodeType':'storehouse_type', 'Code':'product', 'Value':'제품창고', 'Description':'창고구분'},
            {'CodeType':'storehouse_type', 'Code':'semi', 'Value':'반제품창고', 'Description':'창고구분'},
            {'CodeType':'storehouse_type', 'Code':'material', 'Value':'자재창고', 'Description':'창고구분'},
            {'CodeType':'storehouse_type', 'Code':'defect', 'Value':'부적합품창고', 'Description':'창고구분'},
            {'CodeType':'storehouse_type', 'Code':'process', 'Value':'공정창고', 'Description':'창고구분'},

            # 수주상태
            {'CodeType':'suju_state', 'Code':'received', 'Value':'수주', 'Description':'수주상태'},
            {'CodeType':'suju_state', 'Code':'ordered', 'Value':'지시', 'Description':'수주상태'},
            {'CodeType':'suju_state', 'Code':'planned', 'Value':'계획진행', 'Description':'수주상태'},
            {'CodeType':'suju_state', 'Code':'shipped', 'Value':'납품', 'Description':'수주상태'},
            {'CodeType':'suju_state', 'Code':'canceled', 'Value':'취소', 'Description':'수주상태'},
            {'CodeType':'suju_state', 'Code':'holding', 'Value':'검토중', 'Description':'수주상태'},
            
            # 검사종류
            {'CodeType':'test_class', 'Code':'import', 'Value':'수입검사', 'Description':'검사종류'},
            {'CodeType':'test_class', 'Code':'process', 'Value':'공정검사', 'Description':'검사종류'},
            {'CodeType':'test_class', 'Code':'product', 'Value':'제품검사', 'Description':'검사종류'},
            {'CodeType':'test_class', 'Code':'shipping', 'Value':'출하검사', 'Description':'검사종류'},

            # 검사결과상태
            {'CodeType':'test_result_state', 'Code':'ordered', 'Value':'지시', 'Description':'검사결과상태'},
            {'CodeType':'test_result_state', 'Code':'finished', 'Value':'완료', 'Description':'검사결과상태'},

            # 검사항목사용
            {'CodeType':'test_type', 'Code':'use_item_master', 'Value':'검사항목사용', 'Description':'검사항목사용'},
            {'CodeType':'test_type', 'Code':'no_use_item_master', 'Value':'검사항목미사용', 'Description':'검사항목사용'},

            {'CodeType':'consume_from_house_option', 'Code':'process', 'Value':'공정창고', 'Description':'생산투입자재 자동출고처리'},
            {'CodeType':'consume_from_house_option', 'Code':'master', 'Value':'품목마스터창고', 'Description':'생산투입자재 자동출고처리'},

            {'CodeType':'product_move_to_option', 'Code':'potential_input', 'Value':'가입고', 'Description':'생산완료시 제품창고 입고처리'},
            {'CodeType':'product_move_to_option', 'Code':'input', 'Value':'입고', 'Description':'생산완료시 제품창고 입고처리'},

            {'CodeType':'cycle_base', 'Code':'D', 'Value':'일', 'Description':'주기기준'},
            {'CodeType':'cycle_base', 'Code':'W', 'Value':'주', 'Description':'주기기준'},
            {'CodeType':'cycle_base', 'Code':'M', 'Value':'월', 'Description':'주기기준'},
            {'CodeType':'cycle_base', 'Code':'Q', 'Value':'분기', 'Description':'주기기준'},
            {'CodeType':'cycle_base', 'Code':'H', 'Value':'반기', 'Description':'주기기준'},
            {'CodeType':'cycle_base', 'Code':'Y', 'Value':'년(연)', 'Description':'주기기준'},
            {'CodeType':'cycle_base', 'Code':'X', 'Value':'수시', 'Description':'주기기준'},

            {'CodeType':'batch_work', 'Code':'batch_equip_run', 'Value':'설비가동데이터', 'Description':'설비가동데이터 생성'},
            {'CodeType':'batch_work', 'Code':'batch_inventory_balance', 'Value':'일재고데이터', 'Description':'일재고데이터 마감'},
            {'CodeType':'batch_work', 'Code':'batch_kpi_month_result', 'Value':'KPI월실적', 'Description':'KPI월실적데이터 생성'},
                                                                                       
        ]

        for item in syscode_items:
            codetype = item.get('CodeType')
            code = item.get('Code')
            value = item.get('Value')
            desc = item.get('Description')
            count  = SystemCode.objects.filter(CodeType=codetype,Code=code).count()
            if count==0:
                syscode = SystemCode(CodeType=codetype,Code=code, Value=value, Description=desc )
                syscode.save()

        return True

    def get_folder_list(self):
        items = []
        sql = '''
        select mf."Parent_id" as parent_id 
        ,mf.id as folder_id 
        ,mf."FolderName" as folder_name
        ,mf."IconCSS" as icon_css
        ,mf._order as order
        from menu_folder mf
        order by mf._order
        '''
        try:
            items = DbUtil.get_rows(sql)
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemSetupService.get_folder_list', ex)
            raise ex
        
        return items

    
    # 메뉴 재작업
    def get_folder_tree_list(self):
        ''' 메뉴폴더를 트리형식으로 출력. v_menu_folder로 정리
        '''
        sql = '''  select folder_id as id
        , coalesce(p_folder_id,0) as "Parent_id"
        , folder_name as "FolderName"
        , icon as "IconCSS"
        , folder_order as "_order"
        , path
        , _level as lvl
        '''
        if settings.DBMS == 'MSSQL':
            sql += '''
            , concat(REPLICATE('', (_level - 1)*3), folder_name) as "FolderName2"
            '''
        else:
            sql += '''
            , concat(lpad('', (_level - 1)*3, '-'), folder_name) as "FolderName2"
            '''

        sql += '''
         from v_menu_folder
         order by path 
        '''
        items = []
        try:
            items = DbUtil.get_rows(sql, {})
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemSetupService.get_folder_tree_list', ex)
            raise ex

        return items


    # 김하늘 수정(소스메뉴, 메뉴항목 바인딩 실패 -> field명이 제대로 매핑이 안됨)
    def get_menu_list(self, folder_id):
        items = []
        # sql = ''' select mi."MenuCode"
        # , mi."MenuName"
        # , mi."Url" 
        # , mi."MenuFolder_id"
        # , mi._order
        # , nullif(mi."Popup", 'N') as "Popup"
        # from menu_item mi 
        # inner join menu_folder mf on mf.id = mi."MenuFolder_id"
        # where mi."MenuFolder_id" = %(folder_id)s 
        # order by mi."_order" 
        # '''
        sql = ''' select mi."MenuCode" as menu_code
        , mi."MenuName" as menu_name
        , mi."Url" as url
        , mi."MenuFolder_id" as folder_id
        , mi._order as order
        , nullif(mi."Popup", 'N') as popup
        from menu_item mi 
        inner join menu_folder mf on mf.id = mi."MenuFolder_id"
        where mi."MenuFolder_id" = %(folder_id)s 
        order by mi._order
        '''
        try:
            items = DbUtil.get_rows(sql, {'folder_id':folder_id})
        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemSetupService.get_menu_list', ex)
            raise ex

        return items

    # 김하늘 수정(소스메뉴, 메뉴항목 바인딩 실패 -> field명이 제대로 매핑이 안됨)
    def get_gui_use_list(self, unset, keyword):

        src_menus = GUIConfiguration.get_gui_list()

        sql = ''' select mi."MenuCode" as menu_code
        , mi."MenuName" as menu_name
        , mi."Url" as url
        , mi."MenuFolder_id" as folder_id
        , nullif(mi."Popup",'N') as popup
        , mf."FolderName" as folder_name
        from menu_item mi
        inner join menu_folder mf on mf.id = mi."MenuFolder_id" 
        order by "MenuName" 
        '''
        try:
            db_menus = DbUtil.get_rows(sql, {})
            gui_use_list = []
            #matching = True if not keyword else False
            for k, gui in src_menus.items():
                exists = False
                #gui = GUIConfiguration.get_gui_info(k)
                gui_name = gui.get('name')

                matching = False
                if not keyword:
                    matching = True
                elif keyword in gui_name:
                    matching = True
                elif keyword in k:
                    matching = True

                for m in db_menus:
                    if  m['menu_code'] == k:
                        exists = True
                        break;
                
                if matching:
                    dc = {
                        "menu_code" : k, 
                        'menu_name' : gui_name, 
                        'folder_name' : '', 
                        'popup' : gui.get('popup'), 
                        'exists' : exists
                    }
                    if unset: # 미설정메뉴만
                        if exists:
                            continue
                            #gui_use_list.append({"MenuCode": k, 'MenuName': gui_name, 'FolderName':'', 'exists': exists})
                    else:
                        #설정되었든 아니든 다 나오게
                        if not exists:
                            #gui_use_list.append({"MenuCode": k, 'MenuName': gui_name, 'FolderName':'', 'exists': exists})
                            pass
                        else:  # DB설정 메뉴명을 보여준다.
                            #gui_use_list.append({"MenuCode": k, 'MenuName': m['MenuName'], 'FolderName':m['FolderName'], 'exists': exists})
                            dc['menu_name'] = m['menu_name']
                            dc['folder_name'] = m['folder_name']
                    gui_use_list.append(dc)
            return gui_use_list

        except Exception as ex:
            LogWriter.add_dblog('error', 'SystemSetupService.get_gui_use_list', ex)
            raise ex

        return
