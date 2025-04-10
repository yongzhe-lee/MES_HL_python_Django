
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.models.aas import DBAssetAdministrationShell, DBSubModelElementCollection, DBSubmodel, DBPropertyElement, DBSubmodelElement
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

        elif action=="submodel_detail":
            sm_pk = gparam.get('sm_pk')
            aas_pk = gparam.get('aas_pk')
            data = aas_data_service.get_submodel_detail(sm_pk, lang_code, aas_pk)
            result['success'] = True
            result['data'] = data

        elif action=="save_submodel":
            sm_pk = posparam.get('sm_pk');
            lang_code = posparam.get('lang_code')
            displayName = posparam.get('displayName')

            query =DBSubmodel.objects.filter(submodel_pk = sm_pk)
            submodel = None
            if query.count()>0:
                submodel = query[0]
                json_displayname = submodel.displayName

                for dic in json_displayname:
                    if dic.get('language')==lang_code:
                        dic["text"] = displayName


            else:
                submodel = DBSubmodel()
                dic_displayNames = []
                dic_displayNames.append({'language' : lang_code, 'text': displayName})

                submodel.displayName = dic_displayNames
            
            submodel.set_audit(user)
            submodel.save()

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