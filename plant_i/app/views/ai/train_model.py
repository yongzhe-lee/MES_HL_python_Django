from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.services.ai.data_processing import DataProcessingService

from domain.models.da import DsModelTrain

def train_model(context):
    '''
    /api/ai/train_model
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action', 'read')
    data_svc = DataProcessingService()

    try:
        # 나중에 api.views.py에서 json으로 파싱하는 부분 추가 할 것(아래)
        # def dispatch(self, request, *args, **kwargs):
        #     remote_addr = request.META.get('REMOTE_ADDR')
        #     method = request.method

        #     # user 체크 삭제
        #     # if request.user.is_anonymous:
        #     #  return self.response401(request, '로그아웃되었습니다.')

        #     content_type = request.META.get('CONTENT_TYPE', '')
        #     if 'application/json' in content_type:
        #         try:
        #             body = request.body.decode('utf-8')
        #             self.posparam = json.loads(body)
        #         except:
        #             self.posparam = {}
        #     else:
        #         self.gparam = self.make_parameter(request.GET)
        #         self.posparam = self.make_parameter(request.POST)

        #     return super().dispatch(request, *args, **kwargs)

        if action == 'train':
            train_id = posparam.get('train_id')
            model_name = posparam.get('model_name')
            task_type = posparam.get('task_type')
            algorithm = posparam.get('algorithm')
            params = posparam.get('params', {})
            request_user = posparam.get('request_user', {})

            # 여기가 진짜 모델 학습하는 부분
            result = data_svc.새로만들함수(train_id, task_type, algorithm, params)

        # else:
        #     result = {'success': False, 'message': '지원하지 않는 액션입니다.'}
            
    except Exception as ex:
        source = '/api/ai/train_model, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False, 'message':ex}
        
    return result