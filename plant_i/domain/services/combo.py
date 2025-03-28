import datetime
from domain import init_once
from configurations import settings
from .date import DateUtil
from .sql import DbUtil
from .logging import LogWriter
from domain.models.system import MenuFolder, MenuItem, SystemCode, SystemLog, Factory, Unit
from domain.models.definition import Code, CodeGroup, Company ,DASConfig, DASServer, Equipment, EquipmentGroup, Line, Material, Site, TagMaster, TagGroup
from domain.models.kmms import JobClass, Project
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
            'code_group': cls.code_group,
            'company': cls.company,
            'das_config' : cls.das_config,
            'das_server' : cls.das_server,
            'device_type' : cls.device_type,
            'depart': cls.depart,
            'equipment' : cls.equipment,
            'equipment_group' : cls.equipment_group,
            'equipment_type' : cls.equipment_type,
            'factory' : cls.factory,
            'item_group' : cls.item_group,
            'item_type' : cls.item_type,
            'language' : cls.language,
            'line' : cls.line,
            'log_type' : cls.log_type,
            'material' : cls.material,
            'menu_folder': cls.menu_folder,
            'menu_item': cls.menu_item,
            # 'plant': cls.plant,
            'site': cls.site,
            'system_code': cls.system_code,
            'system_code_type': cls.system_code_type,
            'tag': cls.tag,            
            'tag_group' : cls.tag_group,
            'unit': cls.unit,
            'user_code': cls.user_code,
            'user_group': cls.user_group,
            'auth_user': cls.auth_user,
            'job_class': cls.job_class,
            'code': cls.code,
            'project': cls.project,
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


    # @classmethod
    # def plant(cls, cond1, cond2, cond3):
    #     q = Plant.objects.values('id','Name').filter(DelYn='N')
    #     q = q.order_by('id')
        
    #     items = [{'value': item['id'], 'text': item['Name']} for item in q]
    #     return items


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
    def factory(cls, cond1, cond2, cond3):
        query = Factory.objects.values('id', 'Name').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in query ]
        return items


    @classmethod
    def material(cls, cond1, cond2, cond3):
        query = Material.objects.values('id', 'Name').order_by('Name')
        items = [ {'value': entry['id'], 'text':entry['Name']} for entry in query ]
        return items


    @classmethod
    def item_group(cls, cond1, cond2, cond3):
        q = Material.objects.values('ItemGroup').order_by('ItemGroup').distinct()
        items = [{'value': item['ItemGroup'], 'text': item['ItemGroup']} for item in q]
        return items


    @classmethod
    def item_type(cls, cond1, cond2, cond3):
        q = Material.objects.values('ItemType').order_by('ItemType').distinct()
        items = [ {'value': item['ItemType'], 'text':item['ItemType']} for item in q ]
        return items

    @classmethod
    def language(cls, cond1, cond2, cond3):
        items =[
            {'value': 'ko-KR', 'text':'한글'},
            {'value': 'en-US', 'text':'English'},
        ]

    # 24.12.16 김하늘 추가
    @classmethod
    def code_group(cls, cond1, cond2, cond3):
        q = CodeGroup.objects.values('Code','Name').filter(DelYn = 'N', UseYn = 'Y')
        if cond1:
            q = q.filter(SystemYn=cond1)
        q = q.order_by('Code')

        items = [{'value': item['Code'], 'text': item['Code'] + '(' + item['Name'] + ')' } for item in q]

        return items

    # 24.12.23 김하늘 추가
    @classmethod
    def line(cls, cond1, cond2, cond3):
        q = Line.objects.values('id', 'Code', 'Name').order_by('Name')
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
        q = Code.objects.values('Code', 'Name')
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
        items = [ {'value': entry['Code'], 'text':entry['Name']} for entry in q ]
        return items

    @classmethod
    def auth_user(cls, cond1, cond2, cond3):
        """
        콤보박스 데이터 조회 (auth_user 테이블 사용)
        """
        q = User.objects.filter(
            is_active=True
        ).values(
            'id',
            'username',
            'first_name'
        ).order_by('first_name')

        items = [
            {
                'value': item['id'],
                'text': f"{item['first_name']}"
            } for item in q
        ]
        return items

    @classmethod
    def job_class(cls, cond1, cond2, cond3):
        query = JobClass.objects.values('job_class_pk', 'Name').order_by('Name')
        items = [ {'value': entry['job_class_pk'], 'text':entry['Name']} for entry in query ]
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
    def project(cls, cond1, cond2, cond3):
        query = Project.objects.values('proj_cd', 'proj_nm').order_by('proj_nm')
        items = [ {'value': entry['proj_cd'], 'text':entry['proj_nm']} for entry in query ]
        return items