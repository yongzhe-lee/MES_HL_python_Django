import os, uuid
from django.db import transaction

from domain.services.logging import LogWriter
from domain.models.aas import DBAdministration, DBAssetAdministrationShell, DBFileElement, DBSubModelElementCollection, DBSubmodel, DBPropertyElement
from domain.models.aas import DBSubmodelElement
from domain.models.aas import DBReference, AASSubmodelReferences, DBReferenceKey
from domain.services.aas import AASDataService
from domain.services.aas.aasx import AASXHelper
from domain.services.common import CommonUtil
from configurations import settings


def aasgui(context) :
    '''
    /api/aas/aasgui?action=
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    action = gparam.get('action')


    method = request.method
    result = {}
    source = f'/api/aas/aasgui?action={action}'
    aas_data_service = AASDataService()
    
    try:

        if action=="aas_read":
            keyword = gparam.get('keyword')
            aas_items = aas_data_service.get_aas_list(keyword)
            result['success'] = True
            result['items'] = aas_items

        elif action=="aas_detail":
            aas_pk = gparam.get('aas_pk')
            data = aas_data_service.get_aas_detail(aas_pk)

            #aasx_service = AASXHelper(data['id_short'])
            #json_data = aasx_service.to_json_string()
            #xml_data = aasx_service.to_xml_bytes(True)

            result['success'] = True
            result['data'] = data
            #result['json_data'] = json_data
            #result['xml_data'] = xml_data

        elif action=="aas_save":

            p_aas_pk = posparam.get('p_aas_pk')
            aas_pk = posparam.get('aas_pk')
            
            id_short = posparam.get('id_short')

            if aas_data_service.is_valid_id_short(id_short) == False:
                raise Exception("id_short는 영문, 숫자, 언더바(_)만 허용됩니다.")


            id = aas_data_service.make_id_with_short_id(id_short,"aas")

            language = posparam.get('language')
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

                aas.language = language
                aas.displayName = displayName
                aas.description = description

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
                    aas.language = language
                    aas.displayName = displayName
                    aas.description = description

                    # AAS트리구조설정
                    if p_aas_pk:
                        parent_aas = DBAssetAdministrationShell.objects.get(aas_pk = p_aas_pk)
                        aas.derivedFrom = parent_aas

                    aas.set_audit(user)
                    aas.save()


            result['success'] = True
            result['aas_pk'] = aas.aas_pk
            return result

        elif action=="save_submodel":
            aas_pk = posparam.get('aas_pk')
            sm_pk = posparam.get('sm_pk')
            model_kind = posparam.get('model_kind', 'INSTANCE')  # Instance or Type
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
                submodel.language = language
                submodel.displayName = displayName
                submodel.description = description
                submodel.kind = model_kind
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
                submodel.kind = model_kind
                submodel.category = category
                submodel.displayName = {language : displayName}
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
            return result


        elif action=="property_detail":
            sme_pk = gparam.get('data_pk')
            data = aas_data_service.get_property_detail(sme_pk)
            result['success'] = True
            result['data'] = data
            return result

        elif action=='save_property':
            sm_pk = posparam.get('p_sm_pk')
            p_sme_pk = posparam.get('p_sme_pk')
            sme_pk = posparam.get('sme_pk')

            id_short = posparam.get('id_short')
            language = posparam.get('language')
            displayName = posparam.get('displayName')
            description = posparam.get('description')
            valueType = posparam.get('valueType')
            value = posparam.get('value')
            value_id = posparam.get('value_id')

            category = 'VARIABLE' #= posparam.get('category')

            if not sm_pk :
                if not p_sme_pk:
                    raise Exception("submodel pk가 입력되지 않았습니다.")

            submodel_element = None
            prpt_element = None
            if sme_pk:
                submodel_element = DBSubmodelElement.objects.get(sme_pk = sme_pk)
                submodel_element.id_short = id_short
                submodel_element.ModelKind = "Instance"
                submodel_element.category = category
                submodel_element.language = language
                submodel_element.displayName =  displayName
                submodel_element.description = description
                submodel_element.set_audit(user)
                
                with transaction.atomic():
                    submodel_element.save()
                    prpt_element = DBPropertyElement.objects.get(SubmodelElement=submodel_element)
                    prpt_element.valueType = valueType
                    prpt_element.value = value
                    prpt_element.set_audit(user)
                    prpt_element.save()

            else:
                # 신규 Property 등록
                # id_short 가 중복되는지 체크해야 한다.
                id_short_exist = DBSubmodelElement.objects.filter(id_short=id_short).exists()
                if id_short_exist:
                    raise Exception(f"Property id_short '{id_short}' already exists.")

                # id_short 중복이 없으면 신규 등록
                submodel_element = DBSubmodelElement()
                submodel_element.category = category
                submodel_element.id_short = id_short
                submodel_element.modelType = 'Property'
                submodel_element.language = language
                submodel_element.displayName = displayName
                submodel_element.description = description
                submodel_element.set_audit(user)

                if sm_pk:
                    submodel = DBSubmodel.objects.get(submodel_pk=sm_pk)
                    submodel_element.Submodel = submodel
                
                # value_id 처리 루틴 추가
                if value_id is not None:
                    print(f"Value ID: {value_id}")

                with transaction.atomic():
                    submodel_element.save()

                    prpt_element = DBPropertyElement(SubmodelElement = submodel_element)
                    prpt_element.valueType = valueType
                    prpt_element.value = value
                    prpt_element.set_audit(user)
                    prpt_element.save()

                    if p_sme_pk:
                        # 부모가 collection 인경우에는 values에 추가해야함
                        submodelitem_collection = DBSubModelElementCollection.objects.get(sme_pk = p_sme_pk)
                        submodelitem_collection.values.add(submodel_element)
                        submodelitem_collection.set_audit(user)
                        submodelitem_collection.save()


            result['success'] = True
            result['data'] = submodel_element.sme_pk

        elif action=="submodel_element_collection_detail":
            sme_pk = gparam.get('data_pk')
            data = aas_data_service.get_submodel_element_collection_detail(sme_pk)
            result['success'] = True
            result['data'] = data

        elif action=="save_submodel_element_collection":

            # sm_pk(submodel)는 넘어올수도 있고, 안 넘어 올수도 있다. 
            # 컬렉션 밑에 컬렉션이면 sm_pk는 없다.
            
            # sm_pk 가 넘어 오는 경우는 submodel 바로 하위의 컬렉션
            # sm_pk가 없는 경우는 컬렉션 하위의 컬렉션을 등록하거나 수정하는 경우이다.

            # 컬렉션 밑에 컬렉션을 등록하는 경우에는 submodel_element_collection_values 에 추가해야한다.
            # 이 경우는 submodel_element, submodel_element_collection, submodel_element_collection_values 에 다 등록해야 한다.

            p_sm_pk = posparam.get('p_sm_pk')
            sme_pk = posparam.get('sme_pk')
            p_sme_pk = posparam.get('p_sme_pk')
            language = posparam.get('language')
            displayName = posparam.get('displayName')
            description = posparam.get('description')
            id_short = posparam.get('id_short')
            valueType = posparam.get('valueType')
            value = posparam.get('value')
            category = posparam.get('category')
            ModelKind = posparam.get("model_kind", "INSTANCE") # Instance, Template

            submodel_element = None
            submodel_element_collection = None
            
            if sme_pk:
                # 기존 update
                submodel_element = DBSubmodelElement.objects.get(sme_pk = sme_pk)
                submodel_element.id_short = id_short
                submodel_element.category = category
                submodel_element.ModelKind = ModelKind
                submodel_element.modelType = "Collection"
                submodel_element.language = language
                submodel_element.displayName = displayName
                submodel_element.description = description
                submodel_element.set_audit(user)
                submodel_element.save()

            else:
                # 무조건 신규create
                if p_sm_pk:
                    submodel = DBSubmodel.objects.get(submodel_pk =p_sm_pk )

                    # 기존 서브모델 하위의 신규 컬렉션 등록
                    submodel_element = DBSubmodelElement(Submodel=submodel)
                    submodel_element.category = category
                    submodel_element.id_short = id_short
                    submodel_element.modelType = 'Collection'
                    submodel_element.language = language
                    submodel_element.displayName =  displayName
                    submodel_element.description = description
                    submodel_element.set_audit(user)

                    with transaction.atomic():
                        submodel_element.save()
                        submodel_element_collection =  DBSubModelElementCollection(sme_pk = submodel_element.sme_pk)
                        submodel_element_collection.set_audit(user)
                        submodel_element_collection.save()

                else:
                    if not p_sme_pk:
                        raise Exception("부모없이 등록하려 했습니다.")

                    # 부모컬렉션 조회
                    parent_collection = DBSubModelElementCollection.objects.get(sme_pk=p_sme_pk)

                    submodel_element = DBSubmodelElement()
                    submodel_element.id_short = id_short
                    submodel_element.modelType = 'Collection'
                    submodel_element.language = language
                    submodel_element.displayName = displayName
                    submodel_element.description = description
                    submodel_element.set_audit(user)

                    with transaction.atomic():
                        submodel_element.save()
                        submodel_element_collection =  DBSubModelElementCollection(sme_pk = submodel_element.sme_pk)
                        submodel_element_collection.set_audit(user)
                        submodel_element_collection.save()

                        # submodel_element_collection_values 있는지 체크필요
                        # 부모컬렉션추가
                        parent_collection.values.add(submodel_element_collection)
                        parent_collection.set_audit(user)
                        parent_collection.save()


            result['data'] = submodel_element.sme_pk
            result['success'] = True

        elif action=='submodel_element_list':

            sm_pk = gparam.get('sm_pk')
            sme_elements = aas_data_service.get_submodel_element_list(sm_pk)

            result['success'] = True
            result['items'] = sme_elements

        elif action=="submodel_element_collection_items":
            sme_pk = gparam.get('sme_pk')
            items = aas_data_service.get_submodel_element_collection_items(sme_pk)
            result['success'] = True
            result['items'] = items


        elif action=="save_file_element":

            p_sm_pk = posparam.get('p_sm_pk')
            data_pk = posparam.get('sme_pk')
            p_sme_pk = posparam.get('p_sme_pk')
            language = posparam.get('language')
            displayName = posparam.get('displayName')
            description = posparam.get('description')
            id_short = posparam.get('id_short')
            category = posparam.get('category')
            ModelKind = posparam.get("model_kind", "INSTANCE") # Instance, Template

            file = context.request.FILES.get('file_element', None)
            if not data_pk and not file:
                raise Exception("파일이 첨부되지 않았습니다.")


            submodel_element = None
            if data_pk:
                submodel_element = DBSubmodelElement.objects.get(sme_pk=data_pk)
            else:
                submodel_element = DBSubmodelElement()
                if p_sm_pk:
                    submodel = DBSubmodel.objects.get(submodel_pk=p_sm_pk)
                    submodel_element.Submodel = submodel
                    if p_sme_pk:
                        raise Exception("Submodel과 SubmodelElementCollection 상위개체가 동시에 선택입력되었습니다.")
                else:
                    if not p_sme_pk:
                        raise Exception("부모없이 등록하려 했습니다.")

            submodel_element.id_short = id_short
            submodel_element.category = category
            submodel_element.ModelKind = ModelKind
            submodel_element.modelType = "File"
            submodel_element.language = language
            submodel_element.displayName = displayName
            submodel_element.description = description
            submodel_element.set_audit(user)

            with transaction.atomic():
                submodel_element.save()
                file_element = None

                if data_pk:
                    file_element = DBFileElement.objects.get(SubmodelElement=submodel_element) # 이미 저장되어 있는 경우
                else:
                    file_element = DBFileElement(SubmodelElement=submodel_element) # 신규등록


                # 업데이트의 경우 파일을 첨부하지 않을 수 있다.
                # DBFileElement의 value는 상대경로, path는 절대경로
                if file: 
                    ext = file.name.split('.')[-1].lower()
                    save_folder_path = os.path.join(settings.FILE_UPLOAD_PATH, "aas\\resources")
                    save_path = os.path.join(save_folder_path, file_name)


                    if not os.path.exists(save_folder_path):
                        os.makedirs(save_folder_path)

                    if ext in ['py', 'js', 'aspx', 'asp', 'jsp', 'php', 'cs', 'ini', 'htaccess', 'exe', 'dll']:
                        raise ValueError('업로드가 금지된 확장자입니다.')

                    content_type= CommonUtil.get_content_type_ex(ext)
                    file_name = f'fe_{submodel_element.sme_pk}_{uuid.uuid4()}.{ext}'
                    file_element.content_type = content_type
                    file_element.filename = file.name
                    #file_element.value = f"aas\\resources\\{file_name}"
                    file_element.value = f"/resources/{file_name}" #상대경로
                    file_element.path = save_path

                    with open(save_path, mode='wb') as upload_file:
                        upload_file.write(file.read())

                file_element.set_audit(user)
                file_element.save()

                if p_sme_pk and not data_pk:
                    # 부모컬렉션 조회
                    parent_collection = DBSubModelElementCollection.objects.get(sme_pk=p_sme_pk)
                    parent_collection.values.add(file_element)
                    parent_collection.save()
                

            result['data'] = submodel_element.sme_pk
            result['success'] = True


        elif action=="file_element_detail":
            sme_pk = gparam.get('data_pk')
            data = aas_data_service.get_file_detail(sme_pk)
            result['success'] = True
            result['data'] = data

        elif action=="search_submodel_list":
            keyword = gparam.get('keyword')
            return result


        elif action=="aas_delete":
            aas_pk = posparam.get('aas_pk')

            if aas_pk is None:
                raise Exception("삭제할 AAS의 PK가 없습니다.")

            aas = DBAssetAdministrationShell.objects.get(aas_pk = aas_pk)
            aas._status = 'D'  # 삭제 상태로 변경
            aas.set_audit(user)
            aas.save()

            return result

        elif action=="submodel_detail":
            sm_pk = gparam.get('sm_pk')
            aas_pk = gparam.get('aas_pk')

            data = aas_data_service.get_submodel_detail(sm_pk, aas_pk)
            result['success'] = True
            result['data'] = data

            return result

        else:
           raise Exception("action 오류")

    except Exception as ex:
        LogWriter.add_dblog("error", source, ex)
        result['message'] = str(ex)
        result['success'] = False


    return result