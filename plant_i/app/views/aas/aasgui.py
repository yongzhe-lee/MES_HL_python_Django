
from re import sub
from django.db import DatabaseError, transaction

from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.models.aas import DBAdministration, DBAssetAdministrationShell, DBSubModelElementCollection, DBSubmodel, DBPropertyElement, DBSubmodelElement
from domain.models.aas import DBReference, AASSubmodelReferences, DBReferenceKey
from domain.services.aas.data import AASDataService
from domain.services.common import CommonUtil

def aasgui(context) :
    '''
    /api/aas/aasgui?action=
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    action = gparam.get('action')
    lang_code = user.userprofile.lang_code
    if lang_code is None:
        lang_code = 'ko-KR'

    method = request.method
    result = {}
    source = f'/api/aas/aasgui?action={action}'
    aas_data_service = AASDataService()

    try:

        if action=="aas_read":
            keyword = gparam.get('keyword')
            aas_items = aas_data_service.get_aas_list(keyword, lang_code)
            result['success'] = True
            result['items'] = aas_items

        elif action=="aas_detail":
            aas_pk = gparam.get('aas_pk')
            data = aas_data_service.get_aas_detail(aas_pk, lang_code)
            result['success'] = True
            result['data'] = data

        elif action=="aas_save":

            p_aas_pk = posparam.get('p_aas_pk')
            aas_pk = posparam.get('aas_pk')
            
            id_short = posparam.get('id_short')

            id = aas_data_service.make_id_with_short_id(id_short,"aas")

            language = posparam.get('lang_code')
            displayName = posparam.get('displayName')
            description = posparam.get('description')
            version = posparam.get("version", "1")
            revision = posparam.get('revision',"0")

            if not id_short:
                raise Exception("id_shor is null")
            
            if not displayName:
                displayName ="이름없음"


            aas = None
            administrative = None
            if aas_pk:
                aas = DBAssetAdministrationShell.objects.get(aas_pk = aas_pk)
                aas.id = id
                aas.id_short = id_short

                multi_lang_name =  aas_data_service.set_multi_language_text(aas.displayName, language, displayName)
                aas.displayName = multi_lang_name
                aas.description = aas_data_service.set_multi_language_text(aas.description, language, description)

                if p_aas_pk:
                    aas.derivedFrom.aas_pk = p_aas_pk

                #administrative = aas.Administration 버전과 리비젼은 여기서 하지 않는다.
                with transaction.atomic():
                    if not aas.Administration:
                        administrative = DBAdministration()
                        administrative.version = version
                        administrative.revision = revision
                        administrative.set_audit(user)

                        administrative.save()

                        aas.Administration = administrative
                
                    aas.set_audit(user)
                    aas.save()


            else:
                with transaction.atomic():
                    administrative = DBAdministration()
                    administrative.version = version
                    administrative.revision = revision
                    administrative.set_audit(user)
                    administrative.save()

                    aas = DBAssetAdministrationShell()
                    aas.Administration = administrative
                    aas.id = id 
                    aas.id_short = id_short
                    aas.displayName = [{'language' : lang_code, 'text': displayName}]
                    aas.description = [{'language' : lang_code, 'text': description}]

                    # AAS트리구조설정
                    if p_aas_pk:
                        base_aas = DBAssetAdministrationShell.objects.get(aas_pk = p_aas_pk)
                        aas.derivedFrom = base_aas

                    aas.set_audit(user)
                    aas.save()


            result['success'] = True
            result['aas_pk'] = aas.aas_pk


        elif action=="aas_delete":
            aas_pk = posparam.get('aas_pk')

            if aas_pk is None:
                raise Exception("삭제할 AAS의 PK가 없습니다.")

            aas = DBAssetAdministrationShell.objects.get(aas_pk = aas_pk)
            aas._status = 'D'  # 삭제 상태로 변경
            aas.set_audit(user)
            aas.save()

        elif action=="submodel_detail":
            sm_pk = gparam.get('sm_pk')
            aas_pk = gparam.get('aas_pk')

            data = aas_data_service.get_submodel_detail(sm_pk, lang_code, aas_pk)
            result['success'] = True
            result['data'] = data

        elif action=="save_submodel":
            aas_pk = posparam.get('aas_pk')
            sm_pk = posparam.get('sm_pk')
            kind = posparam.get('kind')  # Instance or Type
            category = posparam.get('category')  # VARIABLE, COLLECTION, etc.
            id_short = posparam.get('id_short')
            id = aas_data_service.make_id_with_short_id(id_short,"submodel")
            
            language = posparam.get('lang_code')
            displayName = posparam.get('displayName')
            description = posparam.get('description')

            if not id_short:
                raise Exception("id_shor is null")
            
            if not displayName:
                displayName ="이름없음"

            if not aas_pk:
                raise Exception("AAS PK가 입력되지 않았습니다.")



            submodel = None
            if sm_pk:
                # 기존 submodel 수정
                submodel = DBSubmodel.objects.get(submodel_pk = sm_pk)
                submodel.displayName = aas_data_service.set_multi_language_text(submodel.displayName, language, displayName)
                submodel.description = aas_data_service.set_multi_language_text(submodel.description, language, description)
                submodel.kind = kind
                submodel.category = category
                submodel.set_audit(user)

                with transaction.atomic():
                    if submodel.id_short != id_short:
                        # id_short가 변경된 경우, DBReferenceKey와 DBReference도 업데이트해야 한다.
                        # 기존 중복체크
                        sm_id_exist = DBSubmodel.objects.filter(id_short=id_short).exclude(submodel_pk=sm_pk).exists()
                        if sm_id_exist:
                            raise Exception(f"Submodel id_short '{id_short}' already exists.")
                        else:
                            # 기존 중복이 없으면 DBReferenceKey에 등록되어 있는 정보도 업데이트 해야 한다.
                            DBReferenceKey.objects.filter(type="SUBMODEL", value=submodel.id, Reference__type="ModelReference").upate(value=submodel.id)
                            submodel.id_short = id_short
                            submodel.id = id

                    submodel.save()

            else:
                # 신규 submodel 등록, id_short 중복체크
                id_short_exist = DBSubmodel.objects.filter(id_short=id_short).exists()
                if id_short_exist:
                    raise Exception(f"Submodel id_short '{id_short}' already exists.")

                submodel = DBSubmodel()
                submodel.id =id
                submodel.id_short = id_short
                submodel.kind = kind
                submodel.category = category
                dic_displayNames = []
                dic_displayNames.append({'language' : language, 'text': displayName})
                submodel.displayName = dic_displayNames
                submodel.set_audit(user)

                with transaction.atomic():

                    # submodel 저장
                    submodel.save()

                    # aas와
                    query = DBReferenceKey.objects.filter(type="SUBMODEL", value=id, Reference__type="ModelReference")  
                    if query.count()>0:
                        reference = query.first().reference

                        q = AASSubmodelReferences.objects.filter(aas_id=aas_pk, reference = reference)
                        if q.count()==0:
                            # aas submodel reference가 없으면 생성
                            aas_submodel_ref = AASSubmodelReferences(aas_id=aas_pk, reference=reference)
                            aas_submodel_ref.set_audit(user)
                            aas_submodel_ref.save()
                    else:

                        reference = DBReference()
                        reference.type = "ModelReference"
                        reference.set_audit(user)
                        reference.save()

                        keys = DBReferenceKey(Reference = reference)
                        keys.type = "SUBMODEL"
                        keys.value = id
                        keys.set_audit(user)
                        keys.save()

                        aas_submodel_ref = AASSubmodelReferences(aas_id=aas_pk, reference=reference)
                        aas_submodel_ref.set_audit(user)
                        aas_submodel_ref.save()




            result['success'] = True
            result["sm_pk"] = submodel.submodel_pk

        elif action=="search_submodel_list":
            keyword = gparam.get('keyword')


        elif action=="property_detail":
            sme_pk = gparam.get('data_pk')
            data = aas_data_service.get_property_detail(sme_pk, lang_code)
            result['success'] = True
            result['data'] = data

        elif action=='save_property':
            sm_pk = posparam.get('sm_pk')
            sme_pk = posparam.get('sme_pk')
            id_short = posparam.get('id_short')
            lang_code = posparam.get('lang_code')
            displayName = posparam.get('displayName')
            description = posparam.get('description')
            valueType = posparam.get('valueType')
            value = posparam.get('value')

            category = 'VARIABLE' #= posparam.get('category')

            if sm_pk is None:
                raise Exception("submodel pk가 입력되지 않았습니다.")

            submodel_element = None
            prpt_element = None
            if sme_pk:
                submodel_element = DBSubmodelElement.objects.get(sme_pk = sme_pk)
                submodel_element.id_short = id_short
                submodel_element.ModelKind = "INSTANCE"

                submodel_element.set_audit(user)
                submodel_element.save()

                prpt_element = DBPropertyElement.objects.get(SubmodelElement=submodel_element)

                arr_displayName = submodel_element.displayName
                arr_description = submodel_element.description

                CommonUtil.find_and_set_multilanguage_text(submodel_element.displayName, lang_code,  displayName)
                CommonUtil.find_and_set_multilanguage_text(submodel_element.description, lang_code,  description)

                prpt_element.valueType = valueType
                prpt_element.value = value

                prpt_element.set_audit(user)
                prpt_element.save()


            else:
                submodel_element = DBSubmodelElement()
                submodel_element.category = category
                submodel_element.id_short = id_short
                submodel_element.displayName = [{'language' : lang_code, 'text': displayName}]
                submodel_element.description = [{'language' : lang_code, 'text': description}]
                submodel_element.set_audit(user)
                submodel_element.save()

                prpt_element = DBPropertyElement(SubmodelElement = submodel_element)
                prpt_element.valueType = valueType
                prpt_element.value = value
                prpt_element.set_audit(user)
                prpt_element.save()


            result['success'] = True
            result['data'] = submodel_element.sme_pk


        elif action=="submodel_element_collection_detail":
            sme_pk = gparam.get('data_pk')
            data = aas_data_service.get_submodel_element_collection_detail(sme_pk, lang_code)
            result['success'] = True
            result['data'] = data

        elif action=="save_submodel_element_collection":

            # sm_pk(submodel)는 넘어올수도 있고, 안 넘어 올수도 있다. 
            # 컬렉션 밑에 컬렉션이면 sm_pk는 없다.
            
            # sm_pk 가 넘어 오는 경우는 submodel 바로 하위의 컬렉션
            # sm_pk가 없는 경우는 컬렉션 하위의 컬렉션을 등록하거나 수정하는 경우이다.

            # 컬렉션 밑에 컬렉션을 등록하는 경우에는 submodel_element_collection_values 에 추가해야한다.
            # 이 경우는 submodel_element, submodel_element_collection, submodel_element_collection_values 에 다 등록해야 한다.


            sm_pk = posparam.get('sm_pk')
            sme_pk = posparam.get('sme_pk')
            lang_code = posparam.get('lang_code')
            displayName = posparam.get('displayName')
            description = posparam.get('description')
            id_short = posparam.get('id_short')
            valueType = posparam.get('valueType')
            value = posparam.get('value')

            submodel_element = None
            submodel_element_collection = None
            if sm_pk:
                # 1. sm_pk가 있으면 부모가 submodel 바로 하위의 컬렉션이다. 

                if sme_pk is None:
                    # 기존 서브모델 하위의 신규 컬렉션 등록
                    submodel_element = DBSubmodelElement()
                    submodel_element.displayName = []
                    submodel_element.description = []
                    CommonUtil.find_and_set_multilanguage_text(submodel_element.displayName, lang_code, displayName);
                    CommonUtil.find_and_set_multilanguage_text(submodel_element.description, lang_code, description);
                    submodel_element.set_audit(user)
                    submodel_element.save()

                    submodel_element_collection =  DBSubModelElementCollection(sme_pk = submodel_element.sme_pk)
                    submodel_element_collection.set_audit(user)
                    submodel_element_collection.save()

                else:
                    # 기존 서브모델 하위의 기존 컬렉션 수정
                    submodel_element = DBSubmodelElement.objects.get(sme_pk = sme_pk)
                    CommonUtil.find_and_set_multilanguage_text(submodel_element.displayName, lang_code, displayName);
                    CommonUtil.find_and_set_multilanguage_text(submodel_element.description, lang_code, description);
                    submodel_element.set_audit(user)
                    submodel_element.save()


            else:
                # 2. sm_pk가 없으면 부모가 collection 인 경우 이다.
                # 컬렉션인 경우 상위 컬렉션이 번호와 현재컬렉션 번호를 다 체크해야한다.
                # 부모 컬렉션 PK : p_sme_pk , 본인 컬렉션 PK sme_pk 
                p_sme_pk = posparam.get('p_sme_pk')
                if p_sme_pk is None:
                    raise Exception("부모없이 컬렉션을 등록하려 했습니다.")

                parent_collection = DBSubModelElementCollection(sme_pk=p_sme_pk)

                if sme_pk is None:
                    submodel_element = DBSubmodelElement()
                    submodel_element.displayName = []
                    submodel_element.description = []
                    CommonUtil.find_and_set_multilanguage_text(submodel_element.displayName, lang_code, displayName);
                    CommonUtil.find_and_set_multilanguage_text(submodel_element.description, lang_code, description);
                    submodel_element.set_audit(user)
                    submodel_element.save()
                    submodel_element_collection =  DBSubModelElementCollection(sme_pk = submodel_element.sme_pk)
                    submodel_element_collection.set_audit(user)
                    submodel_element_collection.save()

                    # submodel_element_collection_values 있는지 체크필요
                    parent_collection.values.add(submodel_element_collection)
                    parent_collection.set_audit(user)
                    parent_collection.save()
                    


            submodel_element.id_short = id_short
            #submodel_element.Submodel_sm_pk = sm_pk
            submodel_element.modelType = 'Collection'
            submodel_element.set_audit(user)
            submodel_element.save()

            result['data'] = submodel_element.sme_pk
            result['success'] = True



        elif action=='submodel_element_list':
            sm_pk = gparam.get('sm_pk')
            sme_elements = aas_data_service.get_submodel_element_list(sm_pk, lang_code)
            result['success'] = True
            result['items'] = sme_elements

        elif action=="submodel_element_collection_items":
            sme_pk = gparam.get('sme_pk')
            items = aas_data_service.get_submodel_element_collection_items(sme_pk, lang_code)
            result['success'] = True
            result['items'] = items

        else:

            category = posparam.get('category')
            description = posparam.get('description')
            id_short = posparam.get('id_short')
            aas_id = posparam.get('aas_id')
            asset_pk = posparam.get('asset_pk')
            disp_name_pk = posparam.get('disp_name_pk')
            desc_pk = posparam.get('desc_pk')

            aas = DBAssetAdministrationShell()
            aas.category = category
            aas.displayName.id = disp_name_pk
            if desc_pk:
                aas.description.id = desc_pk

            aas.set_audit(user)
            aas.save()

    except Exception as ex:
        LogWriter.add_dblog("error", source, ex)
        result['message'] = str(ex)
        result['success'] = False


    return result