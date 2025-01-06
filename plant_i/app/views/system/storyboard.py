from domain.services.logging import LogWriter
from domain.services.system import SystemService
from domain.models.system import StoryboardItem

def storyboard(context):
    '''
    /api/system/storyboard
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action', 'read')
    systemService = SystemService()

    try:
        if action == 'read':
            # 메뉴와 hmi 전체목록을 가져오고, 선택된 데이터를 별도로 가져온다
            result = systemService.get_storyboard_item_list()

        elif action == 'save':
            BoardType = posparam.get('BoardType')
            MenuCode = posparam.get('MenuCode')
            Duration = posparam.get('Duration')
            ParameterData = posparam.get('ParameterData', None)

            Url = '/gui/{}?action=storyboard'.format(MenuCode)
            if BoardType!='menu':
                #MenuCode = 'hmi_document'
                #MenuCode = 'wm_hmi_form'
                Url = '/gui/{}/detail?pk={}&action=storyboard'.format(MenuCode, ParameterData)
        
            storyboard = StoryboardItem()
            storyboard.BoardType = BoardType
            storyboard.MenuCode = MenuCode
            storyboard.Duration = Duration
            # 24.11.07 김하늘 추가 ParameterData 값 조회 불가로 인한 수정(후에 int 형변환에서 에러 발생)
            # storyboard.ParameterData = ParameterData
            if ParameterData != '':
                storyboard.ParameterData = ParameterData
            storyboard.Url = Url
            storyboard.set_audit(request.user)
            storyboard.save()
            result = {'success' : True}

        elif action == 'delete':
            # 24.11.07 김하늘 어차피 행 선택이 하나만 가능한 것 같아서 수정
            # id_list = posparam.get('id_list')
            # tmp_arr = id_list.split(',')

            # ids = []
            # for str_id in tmp_arr:
            #     id = int(str_id)
            #     StoryboardItem.objects.filter(id=id).delete()
            id = posparam.get('id')
            StoryboardItem.objects.filter(id=id).delete()

            result = {'success': True}

    except Exception as ex:
        source = '/api/system/storyboard, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result