import datetime
from app.views.kmms.reliab_code import CmReliabCodes
from domain import init_once
from configurations import settings
from domain.models.cmms import CmBaseCodeGroup, CmBaseCode, CmEquipCategory, CmEquipClassify, CmExSupplier, CmImportRank, CmProject, CmSupplier, CmEquipment
from .date import DateUtil
from .sql import DbUtil
from .logging import LogWriter
from domain.models.system import MenuFolder, MenuItem, SystemCode, SystemLog, Factory, Unit
from domain.models.definition import Code, CodeGroup, Company ,DASConfig, DASServer, Equipment, EquipmentGroup, Line, Material, Site, TagMaster, TagGroup, MaterialGroup
from domain.models.cmms import CmJobClass, CmProject
from django.contrib.auth.models import User

#from django.core.cache import cache

@init_once
class ComboService(object):

    __dic_func__ = None
    __initialized__ = False

    @classmethod
    def __static_init__(cls):

        if cls.__initialized__:
            return

        # 알파벳 순서대로 소스를 정리해 놓자.
        cls.__dic_func__ = {
            'aas_kind' : cls.aas_kind,
            'asset_kind' : cls.aas_kind,
            'asset_type': cls.asset_type,
            'code_group': cls.code_group,
            'code': cls.code,
            'company': cls.company,
            'das_config' : cls.das_config,
            'das_server' : cls.das_server,
            'device_type' : cls.device_type,
            'depart': cls.depart,
            'data_month' : cls.data_month,
            'data_year' : cls.data_year,
            'equipment' : cls.equipment,
            'equipment_group' : cls.equipment_group,
            'equipment_type' : cls.equipment_type,
            'equip_category' : cls.equip_category,
            'factory' : cls.factory,
            'input_yn' : cls.input_yn,    
            'language' : cls.language,
            'line' : cls.line,
            'line_equipment' : cls.line_equipment,
            'log_type' : cls.log_type,
            'material_group' : cls.material_group,
            'mat_type' : cls.mat_type,
            'material' : cls.material,
            'menu_folder': cls.menu_folder,
            'menu_item': cls.menu_item,
            'model_kind' : cls.model_kind,
            'sap_storage_location' : cls.sap_storage_location,
            'site': cls.site,
            'smt_line' : cls.smt_line,
            'system_code': cls.system_code,
            'system_code_type': cls.system_code_type,
            'tag': cls.tag,            
            'tag_group' : cls.tag_group,
            'unit': cls.unit,
            'user_code': cls.user_code,
            'user_group': cls.user_group,
            'cm_base_code': cls.cm_base_code,
            'cm_code': cls.cm_code,
            'cm_code_group': cls.cm_code_group,      
            'cm_equip_category': cls.cm_equip_category,
            'cm_equip_classify': cls.cm_equip_classify,
            'cm_equipment' : cls.cm_equipment,
            'cm_import_rank': cls.cm_import_rank,
            'cm_project': cls.cm_project,
            'cm_reliab_codes': cls.cm_reliab_codes,
            'cm_supplier': cls.cm_supplier,
            'cm_ex_supplier': cls.cm_ex_supplier,
            'cm_user_info': cls.cm_user_info,
            'cm_job_class': cls.cm_job_class,
            
        }
        cls.__initialized__ = True


    @classmethod
    def get_combo_list(cls, combo_type, cond1, cond2, cond3):
        try:
            items = []

            if combo_type in cls.__dic_func__:
                items = cls.__dic_func__[combo_type](cond1, cond2, cond3)

            else:
                print('combo_type : '+ combo_type)

            return items
        except Exception as ex:
            source = 'ComboService.get_combo_list, combo_type:{}'.format(combo_type)
            LogWriter.add_dblog('error', source , ex)
            raise ex


    @classmethod
    def company(cls, cond1, cond2, cond3):
        q = Company.objects.values('id','Name').filter(DelYn = 'N', UseYn = 'Y')
        items = [{'value': item['id'], 'text': item['Name']} for item in q]
        return items

    @classmethod
    def device_type(cls, cond1, cond2, cond3):
        items =[
            { 'value':'modbus_tcp', 'text':'modbus-tcp' },
            { "value" : "melsec_tcp", "text" : "미쯔비시 melsec-tcp" },
            { "value" : "mewtocol_tcp", "text" : "파라소닉 mewtocol" },
            { 'value':'excel-custom', 'text':'excel-custom' },
        ]
        return items
    

    @classmethod
    def menu_folder(cls, cond1, cond2, cond3):
        q = MenuFolder.objects
        if cond1 == 'null': #1 level
            q = q.filter(Parent_id__isnull=True)
        elif cond1:
            q = q.filter(Parent_id=cond1)
        q = q.values('id', 'FolderName').order_by('_order')
        items = [ {'value' : entry['id'], 'text' : entry['FolderName'] } for entry in q ]
        return items


    @classmethod
    def menu_code(cls, cond1, cond2, cond3):
        items = []
        if cond1:
            query = MenuItem.objects.filter(MenuFolder_id=cond1).values('MenuCode','MenuName')
            items = [ {'value' : entry['MenuCode'], 'text' : entry['MenuName'] } for entry in query ]
        return items


    @classmethod
    def menu_item(cls, cond1, cond2, cond3):
        q = MenuItem.objects.values('MenuCode','MenuName','MenuFolder__FolderName')
        q = q.order_by('MenuFolder___order', 'MenuName')

        items = []
        for item in q:
            value = item['MenuCode']
            text = '{}({})'.format(item['MenuName'],item['MenuFolder__FolderName'])
            dic = { 'value': value, 'text':text }
            items.append(dic)
        return items

    @classmethod
    def model_kind(cls, cond1, cond2, cond3):
        items =[
            { 'value':'TEMPLATE', 'text':'재사용(공유, Template)' },
            { "value" : "INSTANCE", "text" : "특정자산(전용, Instance)" },
        ]
        return items

    @classmethod
    def unit(cls, cond1, cond2, cond3):
        q = Unit.objects.values('id','Name').filter(DelYn='N')
        q = q.order_by('id')
        
        items = [{'value': item['id'], 'text': item['Name']} for item in q]
        return items
     

    @classmethod 
    def point_type(cls, cond1, cond2, cond3):
        q = SystemCode.objects.values('Code','Value')
        q = q.filter(CodeType='SMP_POINT_TYPE')
        
        items = [{'value': item['code'], 'text': item['value']} for item in q]
        return items 

    @classmethod
    def smt_line(cls, cond1, cond2, cond3):
        q = Line.objects.filter(smt_yn='Y').values('id', 'Code', 'Name').order_by('Name')
        items = [ {'value': item['id'],  'text': item['Code'] + '(' + item['Name'] + ')' } for item in q ]
        return items

    @classmethod
    def sap_storage_location(cls, cond1, cond2, cond3):
        items = [
            {'value' : 4000, 'text' : '1st Warehouse(4000)'},
            {'value' : 4001, 'text' : '전자소자(4001)'},
            {'value' : 4002, 'text' : 'Kardex sector1(4002)'},
            {'value' : 4091, 'text' : 'SMD(4091)'},
            {'value' : 4100, 'text' : 'SMD PCB storage(4100)'},
            {'value' : 4310, 'text' : 'HPC#1(4310)'},
            {'value' : 5000, 'text' : '2nd Warehouse(5000)'},
            {'value' : 5002, 'text' : 'Carousel(5002)'},
            {'value' : 5091, 'text' : 'SMD Plant2(5091)'}
        ]

        return items

    @classmethod
    def system_code(cls, cond1, cond2, cond3):
        q = SystemCode.objects.all()
        if cond1:
            if ',' in cond1:
                cond1 = cond1.replace(' ', '')
                cond_list = cond1.split(',')
                q = q.filter(CodeType__in=cond_list)
            else:
                q = q.filter(CodeType=cond1)
        if cond2:
            if ',' in cond2:
                cond2 = cond2.replace(' ', '')
                cond_list = cond2.split(',')
                q = q.filter(Code__in=cond_list)
            else:
                q = q.filter(Code=cond2)
        if cond3:
            if ',' in cond3:
                cond3 = cond3.replace(' ', '')
                cond_list = cond3.split(',')
                q = q.exclude(Code__in=cond_list)
            else:
                q = q.exclude(Code=cond3)
        q = q.values('Code', 'Value').order_by('_ordering')
        items = [ {'value': entry['Code'], 'text':entry['Value']} for entry in q ]
        return items
    

    @classmethod
    def system_code_type(cls, cond1, cond2, cond3):
        sql = '''
        select distinct "CodeType" as value, "CodeType" as text from sys_code sc order by 1
        '''
        items = DbUtil.get_rows(sql)
        return items

        
    @classmethod
    def user_group(cls, cond1, cond2, cond3):
        sql = ''' 
        select 
        id, "Code" , "Name" 
        from user_group ug 
        order by "Name" 
        '''
        data = DbUtil.get_rows(sql)
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in data ]
        return items
    

    @classmethod
    def depart(cls, cond1, cond2, cond3):
        sql = ''' 
        select 
            id, "Code" , "Name"
        from dept d 
        order by "Name"
        '''
        data = DbUtil.get_rows(sql)
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in data ]
        return items

    @classmethod
    def data_month(cls, cond1, cond2, cond3):
        items = []
        for i in range(1, 13):
            text = f"{i}월"
            item = { 'value':str(i), 'text': text }
            items.append(item)
        return items


    @classmethod
    def data_year(cls, cond1, cond2, cond3):
        today = datetime.datetime.today()
        this_year = int(today.strftime('%Y'))
        
        items = []
            
        for i in range(this_year, 2024, -1):
            item = { 'value':str(i), 'text':i }
            items.append(item)
        return items


    # 24.11.07 김하늘 추가
    @classmethod
    def log_type(cls, cond1, cond2, cond3):
        q = SystemLog.objects.values('Type').order_by('Type').distinct()
        items = [{'value': item['Type'], 'text': item['Type']} for item in q]
        return items


    @classmethod
    def tag_group(cls, cond1, cond2, cond3):
        q = TagGroup.objects.values('id', 'Code', 'Name').order_by('Code')
        items = [{'value': item['id'], 'text': item['Code'] + '(' + item['Name'] + ')'} for item in q]
        return items


    # 24.11.08 김하늘 추가. 25.01.09 김하늘 수정(cond3 workcenter -> line)
    @classmethod
    def equipment(cls, cond1, cond2, cond3):
        q = Equipment.objects.all()

        if cond1:
            q = q.filter(EquipmentGroup__EquipmentType=cond1)
        if cond2:
            q = q.filter(EquipmentGroup_id=cond2)
        if cond3:
            q = q.filter(Line_id=cond3)

        q = q.values('id', 'Name', 'Code').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name'], 'code':entry['Code']} for entry in q ]
        return items


    # 24.11.12 김하늘 추가
    @classmethod
    def tag(cls, cond1, cond2, cond3):
        q = TagMaster.objects
        if cond1:
            q = q.filter(Equipment_id=cond1)
        if cond2:
            q = q.filter(tag_group_id=cond2)
        if cond3:
            q = q.filter(DASConfig_id=cond3)

        q = q.values('tag_code', 'tag_name').order_by('tag_code', 'tag_name')
        items = [ {'value': entry['tag_code'], 'text': entry['tag_code'] + '(' + entry['tag_name'] + ')'} for entry in q ]
        return items


    @classmethod
    def das_config(cls, cond1, cond2, cond3):
        query = DASConfig.objects.values('id', 'Name').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in query ]
        return items


    @classmethod
    def das_server(cls, cond1, cond2, cond3):
        query = DASServer.objects.values('id', 'Name').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in query ]
        return items


    @classmethod
    def equipment_group(cls, cond1, cond2, cond3):
        queryset = EquipmentGroup.objects.all().values('id','Name').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in queryset ]
        return items
    

    @classmethod
    def equipment_type(cls, cond1, cond2, cond3):
        queryset = SystemCode.objects.filter(CodeType='equipment_type').values('id','Value').order_by('Value')
        items = [ {'value': entry['id'], 'text':entry['Value']} for entry in queryset ]
        return items

    @classmethod
    def equip_category(cls, cond1, cond2, cond3):
        queryset = CmEquipCategory.objects.all().values('EquipCategoryCode','Remark').order_by('Remark')
        items = [ {'value': entry['EquipCategoryCode'], 'text':entry['Remark']} for entry in queryset ]
        return items


    @classmethod
    def factory(cls, cond1, cond2, cond3):
        query = Factory.objects.values('id', 'Name').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in query ]
        return items

    @classmethod
    def input_yn(cls, cond1, cond2, cond3):

        items = [
            {"text" : "입력(지정)", "value":"Y"},
            {"text" : "미입력(미지정)", "value":"N"}
        ]
        return items


    @classmethod
    def material(cls, cond1, cond2, cond3):
        query = Material.objects.values('id', 'Name').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in query ]
        return items


    @classmethod
    def material_group(cls, cond1, cond2, cond3):
        q = MaterialGroup.objects.values('id', "Name").order_by('Name')
        items = [{'value': item['id'], 'text': item['Name']} for item in q]
        return items


    @classmethod
    def mat_type(cls, cond1, cond2, cond3):
        
        items = [ 
            {"value" : 'product', "text" : "제품"},
            {"value" : 'semi', "text" : "반제품"},
        ]
        return items

    @classmethod
    def language(cls, cond1, cond2, cond3):
        items =[
            {'value': 'ko-KR', 'text':'한글'},
            {'value': 'en-US', 'text':'English'},
        ]

    @classmethod
    def aas_kind(cls, cond1, cond2, cond3):
        # Instance, Type
        items = [
            { "value":"NOT_APPLICABLE", "text" : "NotApplicable"},
            { "value":"INSTANCE", "text" : "Instance(인스턴스)"},
            { "value":"TYPE", "text" : "Type(유형)"}
        ]
        return items

    @classmethod
    def asset_type(cls, cond1, cond2, cond3):
        #equipment, tool, material, product, software, document, person, organization, location, other
        items = [
            { "value":"device", "text" : "센서, 컨트롤러 등 장치"},
            { "value":"Machine", "text" : "생산설비 등 기계"},
            { "value":"material", "text" : "equipment"},
            { "value":"software", "text" : "소프트웨어자산"},
            { "value":"service", "text" : "서비스"},
            { "value":"document", "text" : "document"},
            { "value":"person", "text" : "person"},
            { "value":"organization", "text" : "organization"},
            { "value":"other", "text" : "other"}
        ]
        return items

    # 24.12.16 김하늘 추가
    @classmethod
    def code_group(cls, cond1, cond2, cond3):
        q = CodeGroup.objects.values('Code','Name').filter(DelYn = 'N', UseYn = 'Y')
        if cond1:
            q = q.filter(SystemYn=cond1)
        q = q.order_by('Code')

        items = [{'value': item['Code'], 'text': item['Code'] + '(' + item['Name'] + ')' } for item in q]

        return items

    @classmethod
    def cm_code_group(cls, cond1, cond2, cond3):
        q = CmBaseCodeGroup.objects.values('CodeGroupCode','CodeGrpName')
        if cond1:
            q = q.filter(SystemYn=cond1)
        q = q.order_by('DispOrder')

        items = [{'value': item['CodeGroupCode'], 'text': item['CodeGroupCode'] + '(' + item['CodeGrpName'] + ')' } for item in q]

        return items

    # 24.12.23 김하늘 추가
    @classmethod
    def line(cls, cond1, cond2, cond3):
        q = Line.objects.values('id', 'Code', 'Name').order_by('Name')
        items = [ {'value': item['id'],  'text': item['Code'] + '(' + item['Name'] + ')' } for item in q ]
        return items

    @classmethod
    def line_equipment(cls, cond1, cond2, cond3):

        q=None
        if cond1:
            q = Equipment.objects.filter(Line_id=cond1).values('id', 'Code', 'Name').order_by('id')
        else:
            q = Equipment.objects.all().values('id', 'Code', 'Name').order_by('id')

        items = [ {'value': item['id'],  'text': item['Code'] + '(' + item['Name'] + ')' } for item in q ]
        return items

    @classmethod
    def site(cls, cond1, cond2, cond3):
        q = Site.objects.values('id', 'Code', 'Name').order_by('Name')
        items = [ {'value': item['id'],  'text': item['Code'] + '(' + item['Name'] + ')' } for item in q ]
        return items

    # 25.01.14 김하늘 추가
    @classmethod
    def user_code(cls, cond1, cond2, cond3):
    # def user_code(cls, site_id, cond1, cond2, cond3): # 우린 아직 code에 site 반영X 추후 여쭤보고 진행
        # 25.04.03 김하늘 수정. code_group 추가
        # 25.07.30 김하늘 수정. remark 추가
        q = Code.objects.values('Code', 'Name', 'CodeGroupCode', 'Remark')
        # q = q.filter(Site_id=site_id)
        if cond1:
            if ',' in cond1:
                cond1 = cond1.replace(' ', '')
                cond_list = cond1.split(',')
                q = q.filter(CodeGroupCode=cond_list)
            else:
                q = q.filter(CodeGroupCode=cond1)
        if cond2:
            if ',' in cond2:
                cond2 = cond2.replace(' ', '')
                cond_list = cond2.split(',')
                q = q.filter(Code__in=cond_list)
            else:
                q = q.filter(Code=cond2)
        if cond3:
            if ',' in cond3:
                cond3 = cond3.replace(' ', '')
                cond_list = cond3.split(',')
                q = q.exclude(Code__in=cond_list)
            else:
                q = q.exclude(Code=cond3)
        q = q.filter(DelYn='N', UseYn='Y')
        q = q.order_by('DispOrder', 'Name')
        items = [ {'value': entry['Code'], 'text':entry['Name'], 'group':entry['CodeGroupCode'], 'param_desc':entry['Remark']} for entry in q ]
        return items
    
    @classmethod
    def cm_job_class(cls, cond1, cond2, cond3):
        query = CmJobClass.objects.values('id', 'JobClassName').order_by('JobClassName')
        items = [ {'value': entry['id'], 'text':entry['JobClassName']} for entry in query ]
        return items

    @classmethod
    def code (cls, cond1, cond2, cond3):        
        q = Code.objects.values('Code', 'Name')        
        if cond1:
            if ',' in cond1:
                cond1 = cond1.replace(' ', '')
                cond_list = cond1.split(',')
                q = q.filter(CodeGroupCode=cond_list)
            else:
                q = q.filter(CodeGroupCode=cond1)
        if cond2:
            if ',' in cond2:
                cond2 = cond2.replace(' ', '')
                cond_list = cond2.split(',')
                q = q.filter(Code__in=cond_list)
            else:
                q = q.filter(Code=cond2)
        if cond3:
            if ',' in cond3:
                cond3 = cond3.replace(' ', '')
                cond_list = cond3.split(',')
                q = q.exclude(Code__in=cond_list)
            else:
                q = q.exclude(Code=cond3)
        q = q.filter(DelYn='N', UseYn='Y')
        q = q.order_by('DispOrder', 'Name')
        items = [ {'value': entry['Code'], 'text':entry['Name']} for entry in q ]
        return items

    @classmethod
    def cm_code (cls, cond1, cond2, cond3):        
        q = CmBaseCode.objects.values('CodeCd', 'CodeName')        
        if cond1:
            if ',' in cond1:
                cond1 = cond1.replace(' ', '')
                cond_list = cond1.split(',')
                q = q.filter(CmBaseCodeGroup=cond_list)
            else:
                q = q.filter(CmBaseCodeGroup=cond1)
        if cond2 != 'UseYnAll':
            q = q.filter(UseYn='Y')
        if cond3:
            if ',' in cond3:
                cond3 = cond3.replace(' ', '')
                cond_list = cond3.split(',')
                q = q.filter(Code__in=cond_list)
            else:
                q = q.filter(Code=cond3)
        q = q.order_by('DispOrder', 'CodeName')
        items = [ {'value': entry['CodeCd'], 'text':entry['CodeName']} for entry in q ]
        return items

    @classmethod
    def cm_base_code (cls, cond1, cond2, cond3):        
        q = CmBaseCode.objects.values('id', 'CodeName')        
        if cond1:
            if ',' in cond1:
                cond1 = cond1.replace(' ', '')
                cond_list = cond1.split(',')
                q = q.filter(CmBaseCodeGroup=cond_list)
            else:
                q = q.filter(CmBaseCodeGroup=cond1)
        if cond2:
            if ',' in cond2:
                cond2 = cond2.replace(' ', '')
                cond_list = cond2.split(',')
                q = q.filter(Code__in=cond_list)
            else:
                q = q.filter(Code=cond2)
        if cond3:
            if ',' in cond3:
                cond3 = cond3.replace(' ', '')
                cond_list = cond3.split(',')
                q = q.exclude(Code__in=cond_list)
            else:
                q = q.exclude(Code=cond3)
        q = q.filter(UseYn='Y')
        q = q.order_by('DispOrder', 'CodeName')
        items = [ {'value': entry['id'], 'text':entry['CodeName']} for entry in q ]
        return items

    @classmethod 
    def cm_project(cls, cond1, cond2, cond3):
        query = CmProject.objects.values('ProjCode', 'ProjName').order_by('ProjName')
        items = [ {'value': entry['ProjCode'], 'text':entry['ProjName']} for entry in query ]
        return items

    @classmethod
    def cm_ex_supplier(cls, cond1, cond2, cond3):
        query = CmExSupplier.objects.values('id', 'ExSupplierName').filter(DelYn = 'N', UseYn = 'Y').order_by('ExSupplierName')
        items = [ {'value': entry['id'], 'text':entry['ExSupplierName']} for entry in query ]
        return items

    @classmethod
    def cm_supplier(cls, cond1, cond2, cond3):
        q = CmSupplier.objects.filter(DelYn='N')

        if cond1:
            # Django ORM으로 바꿀 때는 CmBaseCode.CmBaseCodeGroup_id 를 써야 합니다.
            # Django ForeignKey는 자동으로 뒤에 _id를 붙여서 관리하니까요.
            valid_comp_types = CmBaseCode.objects.filter(CmBaseCodeGroup_id=cond1).values_list('CodeCd', flat=True)
            q = q.filter(CompType__in=valid_comp_types)

        if cond2:
            cond2 = cond2.replace(' ', '')
            cond_list = cond2.split(',')
            q = q.filter(CompType__in=cond_list)

        q = q.values('id', 'SupplierName', 'CompType').order_by('SupplierName')

        items = [{'value': entry['id'], 'text': entry['SupplierName']} for entry in q]
        return items

    @classmethod
    def cm_import_rank(cls, cond1, cond2, cond3):
        query = CmImportRank.objects.values('id', 'ImportRankDesc').order_by('ImportRankDesc')
        items = [ {'value': entry['id'], 'text':entry['ImportRankDesc']} for entry in query ]
        return items

    @classmethod
    def cm_equip_category(cls, cond1, cond2, cond3):
        query = CmEquipCategory.objects.values('EquipCategoryCode', 'EquipCategoryDesc').order_by('EquipCategoryDesc')
        query = query.filter(UseYn='Y')
        items = [ {'value': entry['EquipCategoryCode'], 'text':entry['EquipCategoryDesc']} for entry in query ]
        return items

    @classmethod
    def cm_equip_classify(cls, cond1, cond2, cond3):
        sql = '''
        select distinct "equip_class_id" as value, "equip_class_desc" as text from cm_equip_classify
        where "class_type" = 'CLASS'
        '''
        items = DbUtil.get_rows(sql)
        return items

    @classmethod
    def cm_equipment(cls, cond1, cond2, cond3):
        try:
            # 기본 쿼리셋 생성
            q = CmEquipment.objects.filter(UseYn='Y', DelYn='N')
            
            if cond1:
                # cond1이 문자열로 넘어온 경우 쉼표로 구분된 값들을 파싱
                if isinstance(cond1, str):
                    equip_ids = [int(id.strip()) for id in cond1.split(',') if id.strip().isdigit()]
                    if equip_ids:
                        q = q.filter(id__in=equip_ids)
                # cond1이 리스트로 넘어온 경우
                elif isinstance(cond1, list):
                    equip_ids = [int(id) for id in cond1 if str(id).isdigit()]
                    if equip_ids:
                        q = q.filter(id__in=equip_ids)
                # cond1이 단일 값으로 넘어온 경우
                elif str(cond1).isdigit():
                    q = q.filter(id=int(cond1))
            
            # 결과를 value, text 형태로 변환
            items = [{'value': item.id, 'text': item.EquipName} for item in q.order_by('EquipName')]            
            return items
            
        except Exception as ex:
            source = 'ComboService.cm_equipment'
            LogWriter.add_dblog('error', source, ex)
            return []

    @classmethod
    def cm_user_info(cls, cond1, cond2, cond3):
        """
        콤보박스 데이터 조회 (cm_user_info 테이블 사용) -> (user_profile 테이블 사용)
        """
        sql = ''' 
        select 
            up."User_id" as user_pk, au.username as login_id, up."Name" as user_nm
        from user_profile up
        inner join auth_user au on up."User_id" = au.id
        order by up."Name"
        '''
        data = DbUtil.get_rows(sql)
        items = [ {'value': entry['user_pk'], 'text':entry['user_nm']} for entry in data ]
        return items

    @classmethod
    def cm_reliab_codes(cls, cond1, cond2, cond3):
        q = CmReliabCodes.objects.values('ReliabCode','ReliabName')
        if cond1:
            q = q.filter(Types=cond1)
        q = q.order_by('ReliabName')

        items = [{'value': item['ReliabCode'], 'text': item['ReliabCode'] + '(' + item['ReliabName'] + ')' } for item in q]

        return items