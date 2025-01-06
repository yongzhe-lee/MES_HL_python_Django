from domain.services.logging import LogWriter
from domain.services.system import SystemService
from domain.models.system import LabelCode, LabelCodeLanguage

def labels(context):
    '''
    공통코드에서 사용하는 경로이다. 시스템메뉴서 사용하는 경로는 아래 경로를 참고한다
    /api/common/labels
    '''
    gparam = context.gparam
    posparam = context.posparam

    action = gparam.get('action', 'read')

    lang_code = gparam.get('lang_code')
    gui_code = gparam.get('gui_code')
    template_key = gparam.get('template_key')
    label_code = gparam.get('label_code')
    system_service = SystemService()
    result = []

    try:
        if action =='read':
            result = system_service.get_label_list(lang_code, gui_code, template_key)
        elif action=='labelcodelang_detail':
            result = system_service.get_labelcode_lang_detail(lang_code, gui_code, template_key, label_code)
        elif action=='save_labelcode_lang':

            # lable_code_id 가 넘어오지 않으면 신규저장이다.
            lable_code_id = posparam.get('lable_code_id')

            gui_code = posparam.get('ModuleName')
            template_key = posparam.get('TemplateKey')
            label_code = posparam.get('LabelCode')
            Description = posparam.get('Description')

            lang_code = posparam.get('LangCode')
            DispText = posparam.get('DispText')

            labelcode = None
            if lable_code_id:
                labelcode = LabelCode.objects.get(id=lable_code_id)
            else:
                labelcode = LabelCode(ModuleName=gui_code, TemplateKey=template_key, LabelCode = label_code, Description=Description )

            labelcode.set_audit(context.request.user)
            labelcode.save();

            query= LabelCodeLanguage.objects.filter(LangCode=lang_code, LabelCode=labelcode)
            labelcode_lang = None
            if len(query)>0:
                labelcode_lang = query[0]
            else:
                labelcode_lang = LabelCodeLanguage(LangCode=lang_code,LabelCode= labelcode)

            labelcode_lang.set_audit(context.request.user)
            labelcode_lang.DispText = DispText
            labelcode_lang.save();

            result = {'success' : True, 'labelcode_lang_id' : labelcode_lang.id}


    except Exception as ex:
        source = '/api/common/labels, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)

    return result