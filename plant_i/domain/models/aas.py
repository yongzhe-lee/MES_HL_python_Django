
from django.db import models
from django.contrib.auth.models import User

from basyx.aas.model.base import MultiLanguageNameType, MultiLanguageTextType, Reference
from domain.services.date import DateUtil

ModelingKindChoices = [
    ('Instance', 'Instance'),
    ('Template', 'Template'), 
]

AssetKindChoices = [
    ('Type','Type'),
    ('Instance','Instance')
]

'''
# 사용안함, JSON필드로 대체함
class LanguageItem(models.Model):
    lang_item_pk = models.AutoField(primary_key=True, db_column='lang_item_pk')
    category = models.CharField(max_length=50)
    StringType = models.CharField(max_length=50)
    SourceTableName = models.CharField('원인데이터테이블', max_length=50, null=True)
    SourceDataPk = models.IntegerField('원인데이터PK', null=True)
    name = models.CharField(max_length=200)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'lang_item'


class LanguageText(models.Model):
    lang_text_pk = models.AutoField(primary_key=True, db_column='lang_text_pk')
    language = models.CharField(max_length=10)
    text = models.CharField(max_length=2000)
    LanguageItem = models.ForeignKey(LanguageItem, db_column='lang_item_pk', on_delete=models.DO_NOTHING, null=True)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'lang_text'
'''


class DBResource(models.Model):
    resource_pk = models.AutoField(primary_key=True, db_column='res_pk')
    content_type = models.CharField(max_length=50)    
    StringType = models.CharField(max_length=50)
    path = models.CharField(max_length=2000)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'resource'
        

class DBReferenceKey(models.Model):
    key_pk = models.AutoField(primary_key=True, db_column='key_pk')
    #type = models.CharField(max_length=50) # asset, data_element, submodel_element, submodel, aas....
    type = models.SmallIntegerField(null=True)
    value = models.CharField(max_length=2000)
    Reference = models.ForeignKey('DBReference', on_delete=models.DO_NOTHING, db_column='ref_pk')
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'keys'

class DBReference(models.Model):
    reference_pk = models.AutoField(primary_key=True, db_column='ref_pk')
    type = models.CharField(max_length=50)
    referredSemanticId = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='reference_referredSemanticId', null=True) 
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'reference'

class DBExtensionSupplementalSemanticId(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    Extension = models.ForeignKey('DBExtension', on_delete=models.DO_NOTHING, db_column='ext_pk')
    Reference = models.ForeignKey('DBReference', on_delete=models.DO_NOTHING, db_column='ref_pk')
    class Meta:
        db_table = 'extension_supplementalSemanticId'

class DBExtension(models.Model):
    extension_pk = models.AutoField(primary_key=True, db_column='ext_pk')
    name = models.CharField(max_length=200)
    SourceTableName = models.CharField('원인데이터테이블', max_length=50)
    SourceDataPk = models.IntegerField('원인데이터PK', null=True)
    semanticId = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, related_name='extension_semanticsId', null=True)
    valueType = models.CharField(max_length=50, null=True)
    value = models.CharField(max_length=2000, null=True)
    referTo = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, related_name='extension_referTo', null=True)
    supplementalSemanticIds = models.ManyToManyField(DBReference, through = DBExtensionSupplementalSemanticId, related_name='extension_supplementalSemanticId', related_query_name='extension_supplementalSemanticId' )
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'extension'
        
############################################################################################################################################
# Data Specification
class DBDataSpecificationIEC61360(models.Model):
    '''
    '''
    id = models.AutoField(primary_key=True)
    #preferredName = models.CharField(max_length=200)
    #shortName = models.CharField(max_length=200)
    unit = models.CharField(max_length=200)
    unitId = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, related_name='data_spec_unitId', null=True)
    sourceOfDefinition = models.CharField(max_length=2000, null=True)
    symbol = models.CharField(max_length=2000, null=True)
    dataType = models.CharField(max_length=50, null=True)
    #definition = models.CharField(max_length=2000, null=True)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'dataspec_iec61360'


class DBDataSpecificationContent(models.Model):
    '''
    '''
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'dataspec_content'


class DBEmbeddedDataSpecification(models.Model):
    id = models.AutoField(primary_key=True)
    dataSpecification = models.ForeignKey(DBReference,db_column='ref_pk', on_delete=models.DO_NOTHING)
    dataSpecificationContent = models.ForeignKey(DBDataSpecificationContent, on_delete=models.DO_NOTHING)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'embedded_dataspec'

class DBAssetSpecificassetIds(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    spec_asset_pk = models.ForeignKey('DBSpecificAssetId', on_delete=models.DO_NOTHING, db_column='spec_asset_pk')
    asset_info_pk = models.ForeignKey('DBAssetInformation', on_delete=models.DO_NOTHING, db_column='asset_info_pk')
    
    class Meta:
        db_table='asset_specificassetids'
        

class DBAssetInformation(models.Model):
    asset_pk = models.AutoField(primary_key=True, db_column='asset_pk')
    asset_kind = models.CharField(max_length=50, null=True) #    TYPE = 0    INSTANCE = 1    NOT_APPLICABLE = 2
    asset_type = models.CharField(max_length=50, null=True)
    
    globalAssetId = models.CharField(max_length=2000, null = True)
    path = models.CharField(max_length=2000, null = True)
    defaultThumbnail = models.ForeignKey(DBResource, on_delete=models.DO_NOTHING, null=True)
    SpecificAssetIds = models.ManyToManyField('DBSpecificAssetId', through=DBAssetSpecificassetIds, related_name='asset_specificassetids', related_query_name='asset_specificassetids' )

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'asset_info'

class SpecificAssetIdSupplementalSemanticId(models.Model):
    '''
    맵핑 테이블    
    '''
    id = models.AutoField(primary_key=True)
    SpecificAssetId = models.ForeignKey('DBSpecificAssetId', on_delete=models.DO_NOTHING, db_column='spec_asset_pk')
    Reference = models.ForeignKey('DBReference', on_delete=models.DO_NOTHING, db_column='ref_pk')
    class Meta:
        db_table = 'specificassetid_supplementalSemanticId'
    

class DBSpecificAssetId(models.Model):
    spec_asset_pk = models.AutoField(primary_key=True, db_column='spec_asset_pk')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=2000)
    semanticId = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, related_name='specificAssetId_semanticId', db_column='semantic_id', null=True)
    externalSubject = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, related_name='specificAssetId_externalSubject', db_column='external_subject_id', null=True)
    supplementalSemanticIds = models.ManyToManyField(DBReference, through=SpecificAssetIdSupplementalSemanticId, related_name='specificAssetId_supplementalSemanticId', related_query_name='specificAssetId_supplementalSemanticId')

    #AssetInformations = models.ManyToManyRel(DBAssetInformation, related_name='assetinformation_specificassetids')
    AssetInformation = models.ForeignKey(DBAssetInformation, on_delete=models.DO_NOTHING, null=True, db_column='asset_pk')

    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'specific_asset'



class QualifierSupplementalSemanticIds(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    qualifier_pk = models.ForeignKey('DBQualifier', on_delete=models.DO_NOTHING, db_column='qualifier_pk')
    reference_pk = models.ForeignKey('DBReference', on_delete=models.DO_NOTHING, db_column='ref_pk')
    
    class Meta:
        db_table = 'qualifier_supplementalSemanticIds'


class DBQualifier(models.Model):
    
    '''
    Asset Administration Shell (AAS)에서 "Qualifier"는 자산이나 자산의 특정 특성에 대한 추가 정보나 조건을 제공하는 메타데이터 요소입니다. 
    Qualifier는 자산에 대한 상세 정보를 보다 명확하게 표현하는 데 도움을 줍니다.
    Qualifier는 일반적으로 두 가지 주요 구성 요소, 즉 "Type"과 "Kind"를 포함합니다.  
    
    Qualifier Type
    "Type"은 Qualifier가 나타내는 데이터의 유형을 지정합니다. 
    이는 데이터의 성격과 어떤 정보를 포함하는지를 정의하는데 사용됩니다. 
    예를 들어, Type은 온도, 압력, 속도, 위치, 시리얼 번호, 제조업체 등 구체적인 특성을 나타낼 수 있습니다. 
    Type은 Qualifier가 어떤 종류의 데이터를 다루고 있는지를 명확히 해주며, 이를 통해 데이터를 적절하게 해석하고 사용할 수 있습니다.

    Qualifier Kind
    "Kind"는 Qualifier의 적용 범위나 사용 목적을 나타냅니다. 
    Kind는 데이터가 어떤 목적으로 사용되는지, 어떤 상황에서 유효한지를 정의합니다. 
    예를 들어, Kind는 데이터가 상수 값인지, 측정치인지, 또는 계산된 값인지 등을 지정할 수 있습니다. 
    이는 데이터의 처리와 해석 방식에 영향을 미치며, 데이터를 어떻게 활용할 것인지에 대한 지침을 제공합니다.    
    '''
    qaulifier_pk = models.AutoField(primary_key=True, db_column='qaulifier_pk')
    kind = models.CharField(max_length = 200)  # TemplateQualifier, ConceptQualifier, ValueQualifier
    type = models.CharField(max_length = 200)
    value_type = models.CharField(max_length = 200)
    value = models.CharField(max_length = 2000)
    value_id = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, null=True, related_name='qualifier_valueId', db_column = 'value_id')
    semanticId = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, null=True, related_name='qualifier_semanticId', db_column='semantic_id')
    supplementalSemanticIds = models.ManyToManyField(DBReference, through=QualifierSupplementalSemanticIds, related_name='qualifier_supplementalSemanticIds')

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'qualifier'

class SubmodelelementEmbeddedDataSpecifications(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    SubmodelElement = models.ForeignKey('DBSubmodelElement', on_delete=models.DO_NOTHING, db_column='sme_pk')
    embedded_data_specification_pk = models.ForeignKey(DBEmbeddedDataSpecification, on_delete=models.DO_NOTHING, db_column='embedded_data_specification_pk')
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'submodelelement_embeddedDataSpecifications'

class SubmodelElementExtensions(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    SubmodelElement = models.ForeignKey('DBSubmodelElement', on_delete=models.DO_NOTHING, db_column='sme_pk')
    extension_pk = models.ForeignKey(DBExtension, on_delete=models.DO_NOTHING, db_column='extension_pk')

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    
    class Meta:
        db_table = 'submodelelement_extensions'

class DBSubmodelElement(models.Model):
    '''
    자산의 서브모델 내에서 특정 정보를 표현하는 데 사용되는 구성 요소입니다. 
    서브모델 자체는 자산의 특정 측면이나 기능을 표현하기 위해 설계된 구조적 요소로, 
    자산의 디지털 표현을 완성하는 데 중요한 역할을 합니다. 
    서브모델 엘리먼트는 이러한 서브모델 내에서 세부 정보를 모듈화하고 표준화하는 데 기여합니다.
    
    Submodel Element의 주요 유형
    Property: 단일 값을 가진 기본 정보 요소입니다. 예를 들어, 기계의 최대 작동 온도 또는 장비의 제조연도와 같은 특정 데이터를 포함할 수 있습니다.

    Collection
    여러 서브모델 엘리먼트를 그룹화하는 데 사용됩니다. 이는 관련된 다양한 프로퍼티나 다른 서브모델 엘리먼트를 하나의 컬렉션으로 조직화할 수 있게 해줍니다.

    Operation
    특정 작업이나 기능을 나타내며, 입력 매개변수와 출력을 가질 수 있습니다. 예를 들어, 장비의 특정 부품을 교체하는 절차를 실행하거나, 데이터 분석 결과를 계산하는 데 사용될 수 있습니다.

    Event
    자산에서 발생하는 이벤트를 나타내는 요소로, 특정 조건이나 상황이 발생했을 때 정보를 제공합니다. 예를 들어, 경고 또는 알람이 발생하는 시점을 기록할 수 있습니다.

    File
    자산과 관련된 파일 정보를 나타냅니다. 이는 구성 파일, 매뉴얼, 설계 도면 등 다양한 형태의 디지털 문서를 포함할 수 있습니다.

    Reference Element
    다른 서브모델 엘리먼트나 외부 요소를 참조하는 데 사용됩니다. 이를 통해 서브모델 엘리먼트 간의 관계를 정의하고, 정보의 연결성을 향상시킬 수 있습니다.        
    
    catagory
    "constant", "parameter", "variable"
    '''

    sme_pk = models.AutoField(primary_key=True, db_column='sme_pk')
    id_short = models.CharField(max_length=200, null =True, unique=True)
    category = models.CharField(max_length=50, null=True) #"constant", "parameter", "variable" measurement, info
    ModelKind = models.CharField(max_length=50, null=True) #models.SmallIntegerField(null=True) # 0 : Template, 1: Instance
    model_type = models.CharField(max_length=50) # Property, Collection, Operation, Event, File, Reference Element    
    semancticId = models.ForeignKey(DBReference, related_name='submodelelement_semancticId',db_column='semanctic_id', on_delete = models.DO_NOTHING)
    embeddedDataSpecifications = models.ManyToManyField(DBEmbeddedDataSpecification, through=SubmodelelementEmbeddedDataSpecifications, related_name='submodelelement_embeddedDataSpecifications', related_query_name='submodelelement_embeddedDataSpecifications')
    Extensions= models.ManyToManyField(DBExtension, through=SubmodelElementExtensions, related_name='submodelelement_extensions', related_query_name='submodelelement_extensions')


    #displayName = models.ForeignKey('LanguageItem', db_column='disp_name_pk', on_delete = models.DO_NOTHING, null=True, related_name=  'submodelelement_displayName')
    #description = models.ForeignKey('LanguageItem', db_column='desc_pk', on_delete = models.DO_NOTHING, null=True, related_name=  'submodelelement_description')
    displayName = models.JSONField(null=True);
    description = models.JSONField(null=True);


    Submodel = models.ForeignKey('DBSubmodel', on_delete=models.DO_NOTHING, null=True, db_column='sm_pk')

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'submodel_element'

class DBDataElement(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)
    class Meta:
        abstract = True
        db_table = 'data_element'
         
class DBMultiLanguageProperty(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)
    valueId = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, null=True, related_name='multiLanguageProperty_valueId_reference')
    #value = models.ForeignKey(LanguageItem, on_delete=models.DO_NOTHING, null=True, related_name='multiLanguageProperty_value_languageItem')
    value = models.JSONField(null=True);


    class Meta:
        db_table = 'multilang_prpt_element'
    
    
class DBPropertyElement(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)

    value = models.CharField(max_length=2000)
    contentType = models.CharField(max_length=500)
    valueType = models.CharField(max_length = 200)
    value = models.CharField(max_length = 2000)
    valueId = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, null=True, related_name='propertyElement_valueId_reference', db_column="value_id")

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
        db_table = 'property_element'

class DBBlobElement(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)
    value = models.TextField(max_length=2000) # BlobType
    mimeType = models.CharField(max_length=500) # ContentType

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
        db_table = 'blob_element'

class DBFileElement(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)
    value = models.CharField(max_length=2000) # PathType
    content_type = models.CharField(max_length=500) # ContentType
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
        db_table = 'file_element'
        
class DBCapabilityElement(DBSubmodelElement):

    class Meta:
        db_table = 'capa_element'

class DBRangeElement(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)
    valueType = models.CharField(max_length = 200)
    max = models.CharField(max_length = 2000)
    min = models.CharField(max_length = 2000)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
        db_table = 'range_element'
        
class DBReferenceElement(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)
    value = models.ForeignKey(DBReference, on_delete=models.DO_NOTHING, null=True, related_name='referenceelement_value', related_query_name='referenceelement_value')

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
        db_table = 'reference_element'
        


class DBEntityElement(models.Model):
    SubmodelElement = models.OneToOneField(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='sme_pk', primary_key=True)
    entityType = models.CharField(max_length=200) # CoManagedEntity, SelfManagedEntity
    statements = models.ManyToManyField(DBSubmodelElement, related_name='entityelement_statements', related_query_name='entityelement_statements')
    globalAssetId = models.CharField(max_length=2000)
    specificAssetId = models.ForeignKey(DBSpecificAssetId, on_delete=models.DO_NOTHING, null=True)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
         db_table = 'entity_element'

class DBSubModelElementCollection(models.Model):
    sme_pk = models.IntegerField(primary_key=True, db_column='sme_pk')
    value = models.ForeignKey(DBSubmodelElement, on_delete=models.DO_NOTHING, db_column='value_pk')
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
        db_table = 'submodel_element_collection'

class SubmodelExtensions(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    submodel_pk = models.ForeignKey('DBSubmodel', on_delete=models.DO_NOTHING, db_column='submodel_pk')
    extension_pk = models.ForeignKey(DBExtension, on_delete=models.DO_NOTHING, db_column='extension_pk')
    
    class Meta:
        db_table = 'submodel_extensions'


class SubmodelQualifiers(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    submodel_pk = models.ForeignKey('DBSubmodel', on_delete=models.DO_NOTHING, db_column='submodel_pk')
    qualifier_pk = models.ForeignKey(DBQualifier, on_delete=models.DO_NOTHING, db_column='qualifier_pk')
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return    

    class Meta:
        db_table = 'submodel_qualifiers'

class SubmodelEmbeddedDataSpecifications(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    submodel_pk = models.ForeignKey('DBSubmodel', on_delete=models.DO_NOTHING, db_column='submodel_pk')
    DataSpecification = models.ForeignKey(DBEmbeddedDataSpecification, on_delete=models.DO_NOTHING, db_column='data_spec_pk')
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return    

    class Meta:
        db_table = 'submodel_embeddedDataSpecifications'

class DBSubmodel(models.Model):
    submodel_pk = models.AutoField(primary_key=True, db_column='sm_pk')
    id = models.CharField(max_length=2000, unique=True)
    id_short = models.CharField(max_length=200, null =True, unique=True)
    kind = models.CharField(max_length=50, null =True) #SmallIntegerField(null=True) # 0 : Template, 1: Instance
    category = models.CharField(max_length=100, null=True)
    semanticId = models.ForeignKey(DBReference, on_delete=models.CASCADE, null=True, related_name='submodel_semanticId', db_column='semantic_id')
    assetAdministrationShell = models.ForeignKey('DBAssetAdministrationShell', on_delete=models.CASCADE, null=True, db_column='aas_pk')
    Qualifiers= models.ManyToManyField(DBQualifier, through=SubmodelQualifiers, related_name='submodel_qualifiers', related_query_name = 'submodel_qualifiers')
    EmbeddedDataSpecifications = models.ManyToManyField(DBEmbeddedDataSpecification, through=SubmodelEmbeddedDataSpecifications, related_name='submodel_embeddedDataSpecifications', related_query_name='submodel_dataspecs')
    Extensions = models.ManyToManyField(DBExtension, through=SubmodelExtensions, related_name='submodel_extensions', related_query_name='submodel_extensions')

    #displayName = models.ForeignKey('LanguageItem', db_column='disp_name_pk', on_delete = models.DO_NOTHING, null=True, related_name=  'submodel_displayName')
    #description = models.ForeignKey('LanguageItem', db_column='desc_pk', on_delete = models.DO_NOTHING, null=True, related_name=  'submodel_description')

    displayName = models.JSONField(null=True);
    description = models.JSONField(null=True);

    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'submodel'

class DBAdministration(models.Model):
    admin_pk = models.AutoField(primary_key=True, db_column='admin_pk')
    version = models.CharField(max_length=200)
    revision = models.CharField(max_length=200, null=True)
    templateId = models.CharField(max_length=2000, null=True)
    creator = models.ForeignKey(DBReference, on_delete = models.DO_NOTHING, null=True)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta:
        db_table = 'administration'


class AASExtensions(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    aas_pk = models.ForeignKey('DBAssetAdministrationShell', on_delete=models.DO_NOTHING, db_column='aas_pk')
    extension_pk = models.ForeignKey(DBExtension, on_delete=models.DO_NOTHING, db_column='extension_pk')
    

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'aas_extensions'


class AASDataSpecification(models.Model):
    '''
    맵핑 테이블
    '''
    id = models.AutoField(primary_key=True)
    aas_pk = models.ForeignKey('DBAssetAdministrationShell', on_delete=models.DO_NOTHING, db_column='aas_pk')
    dataspec_pk = models.ForeignKey(DBEmbeddedDataSpecification, on_delete=models.DO_NOTHING, db_column='dataspec_pk')
    

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'aas_dataspecs'

###################################################################################
# AssetAdministrationShell
###################################################################################
class DBAssetAdministrationShell(models.Model) :
    aas_pk = models.AutoField(primary_key=True)
    id = models.CharField(max_length=2000, unique=True)
    category = models.CharField(max_length=50, null=True)
    id_short = models.CharField(max_length=200, null =True, unique=True)
    Administration = models.ForeignKey(DBAdministration, db_column='admin_pk', on_delete=models.DO_NOTHING, null=True)
    AssetInformation = models.ForeignKey(DBAssetInformation, db_column='asset_pk', on_delete=models.DO_NOTHING, null=True)
    derivedFrom = models.ForeignKey('self', db_column='base_aas_pk', on_delete=models.CASCADE, null=True, related_name='aas_derivedFrom')
    embeddedDataSpecifications = models.ManyToManyField(DBEmbeddedDataSpecification, through=AASDataSpecification, related_name='aas_dataspecs', related_query_name='aas_dataspecs')
    Extensions = models.ManyToManyField(DBExtension, through=AASExtensions, related_name='aas_extensions', related_query_name='aas_extensions')

    #displayName = models.ForeignKey('LanguageItem', db_column='disp_name_pk', on_delete = models.DO_NOTHING, null=True, related_name= 'aas_displayName')
    #description = models.ForeignKey('LanguageItem', db_column='desc_pk', on_delete = models.DO_NOTHING, null=True, related_name= 'aas_description')

    displayName = models.JSONField(null=True);
    description = models.JSONField(null=True);

    #dispaly_name : MultiLanguageTextType = None   


    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'aas'



'''
Asset Type
물리적 자산
  - 특정 기계, 장비, 또는 장치 등을 나타냅니다.
    이러한 자산은 공장의 생산 라인에서 직접적인 제조 역할을 수행할 수 있습니다.

소프트웨어 자산
  - 시스템을 운영하거나 제어하는데 사용되는 소프트웨어 또는 애플리케이션입니다.
    예를 들어, ERP(Enterprise Resource Planning) 시스템, SCM(Supply Chain Management) 소프트웨어 등이 있습니다.

인적 자산
  - 기술, 경험, 또는 특정 업무를 수행할 수 있는 개인 또는 팀을 포함합니다. 
    이러한 자산은 특히 서비스 산업에서 중요하게 여겨집니다.

지식 자산 
  - 특정 기술이나 프로세스에 대한 지식, 특허, 브랜드, 라이선스 등이 포함됩니다. 
    이들은 경쟁 우위를 확보하고 혁신을 촉진하는 데 중요한 역할을 합니다.

정보 자산 
  - 데이터베이스, 문서, 기록 등 기업의 운영에 필요한 정보를 포함합니다. 
    정보 보안은 이러한 자산의 중요한 관리 포인트입니다.

서비스 자산
  = 고객에게 제공되는 서비스나 그 기능을 나타냅니다
    예를 들어, 유지보수 서비스, IT 지원 서비스 등이 이에 해당됩니다.


Modeling Kind(Type)
Instance
 - 실제로 존재하는 특정 자산의 인스턴스를 나타내며, 이는 개별 자산에 대한 구체적인 데이터와 정보를 포함합니다. 
   예를 들어, 특정 제조 기계나 소프트웨어 인스턴스 등이 이에 해당합니다.
Template 
 - 재사용 가능한 정의 또는 구조로서, 유사한 자산에 대해 일관된 정보와 구조를 제공합니다. 
   템플릿은 설계, 설치, 유지보수 등 여러 자산에 걸쳐 공통적으로 사용될 수 있는 기준 또는 모델을 정의하는 데 사용됩니다.

'''