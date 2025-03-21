import sys, time
import requests

from configurations import settings
from domain.models.system import SystemLog, SFLog
from django.db.models import ProtectedError
from django.db import IntegrityError
from domain import init_once
from domain.services.date import DateUtil
from domain.models.interface import IFLog

@init_once
class LogWriter:

    dic_table = {}

    @classmethod
    def __static_init__(cls):
        cls.dic_table = cls.table_name_load()
        return


    @classmethod
    def table_name_load(cls):
        dc = {}

        dc['UserGroupMenu'] = '사용자그룹메뉴'
        dc['UserProfile'] = '사용자프로필'

        dc['user_profile'] = '사용자프로필'
        dc['login_log'] = '로그인로그'
        dc['doc_result'] = '문서결과'

        return dc


    @classmethod
    def parse_foreign_model(cls, err_msg):
        index = err_msg.find('foreign key:', 0)
        start = index + 14
        index = err_msg.find('.', start)
        return err_msg[start:index]

    @classmethod
    def parse_foreign_model_in_integrity_err(cls, err_msg):
        start = err_msg.find('제약 조건 - ', 0) + 8
        end = err_msg.find('테이블', start) - 1
        return err_msg[start:end].strip('"')

    @classmethod
    def get_table_name(cls, model_name):
        
        #table_name = LogWriter.dic_table.get(model_name, model_name)
        table_name = cls.dic_table.get(model_name, model_name)
        return table_name


    @classmethod
    def parse_foreign_table(cls, err_msg):
        model_name = cls.parse_foreign_model(err_msg)
        table_name = cls.get_table_name(model_name)
        return table_name

    @classmethod
    def parse_foreign_table_in_integrity_err(cls, err_msg):
        model_name = cls.parse_foreign_model_in_integrity_err(err_msg)
        table_name = cls.get_table_name(model_name)
        return table_name

    @classmethod
    def delete_err_message(cls, ex):
        try:
            table_name = ''

            if isinstance(ex, ProtectedError):
                err_msg = ex.args[0]
                table_name = cls.parse_foreign_table(err_msg)
                if not table_name:
                    raise e
            elif isinstance(ex, IntegrityError):
                err_msg = ex.__cause__.pgerror
                table_name = cls.parse_foreign_table_in_integrity_err(err_msg)
                if not table_name:
                    raise e

            message = table_name + ' 데이터에서 사용되고 있기 때문에 삭제할 수 없습니다.'

        except Exception as e:
            LogWriter.add_dblog('error', 'LogWriter.delete_message' , e)
            message = '이 데이터를 다른 곳에서 사용되고 있기 때문에 삭제할 수 없습니다.'
        return message


    @classmethod
    def add_dblog(cls, logtype, source, ex=None):
        if isinstance(ex, KeyError):
            message = 'KeyError:' + str(ex)
            #message = str(type(ex)) + ':' + str(ex)
        else:
            message = ex
        SystemLog.add_log(logtype, source, message)
        return

    @classmethod
    def add_sf_log(cls, use_type, user_id, request):


        '''
        use_type :  조회/변경, 접속/종료
        user_id : 유저pk

        json 데이터로 보낼경우 
        https://log.smart-factory.kr/apisvc/sendLogData.json

        dic_data = {
            "crtfcKey" : crtfcKey,
            "logDt" : "로그일시",
            "useSe" : "접속구분",
            "sysUser" : "사용자",
            "conectIp" : "IP번호",
            "dataUsgqty" : "데이터사용량(숫자)"
        }

        json 문자열로 보낼경우 아래 주소
        https://log.smart-factory.kr/apisvc/sendLogDataJSON.do
        logData = '{~~}'
        crtfcKey = settings.SF_LOG_KEY
        if crtfcKey =='':
            return
        '''

        crtfcKey = settings.SF_LOG_KEY
        if crtfcKey =='':
            return


        result = True
        try:
            now =  DateUtil.get_current_datetime()
            dataUsgqty = sys.getsizeof(request.GET) + sys.getsizeof(request.POST)
            ip_addr = request.META.get('REMOTE_ADDR')
            sflog =  SFLog(logDt=now,useSe=use_type, sysUser= user_id,conectIp=ip_addr,dataUsgqty=dataUsgqty)
            sflog.save()
        except Exception as ex:
            print(ex)
            result = False

        return result

    @classmethod
    def do_send_sf_log(cls):
        
        crtfcKey = settings.SF_LOG_KEY
        if crtfcKey =='':
            return

        while True:
            try:
                query = SFLog.objects.filter(SendYN='N')
                for sflog in query:
                    logDt = sflog.logDt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                    dic_data = {
                        "crtfcKey" : crtfcKey,
                        "logDt" : logDt,
                        "useSe" : sflog.useSe,
                        "sysUser" : sflog.sysUser,
                        "conectIp" : sflog.conectIp,
                        "dataUsgqty" : sflog.dataUsgqty
                    }

                    url = 'https://log.smart-factory.kr/apisvc/sendLogData.json'
                    res = requests.post(url, dic_data)
                    if res.status_code==200: 
                        dic_result = res.json().get('result', None)
                        if dic_result:
                            result_cd = dic_result.get('recptnRsltCd')
                            print('do_send_sf_log - result code:', result_cd)
                            SFLog.objects.filter(id=sflog.id).update(SendYN='Y')

                # 1분간 정지
                time.sleep(60)

            except Exception as ex:
                print(ex)

        return


    @classmethod
    def add_interface_log(cls, task, method, contents, equ_cd=None, mat_cd=None, rev_no=None, is_success='Y', user=None):

        if_log = IFLog()
        if_log.task = task
        if_log.method = method
        if_log.contents = contents
        if_log.equ_cd = equ_cd
        if_log.mat_cd = mat_cd
        if_log.rev_no = rev_no
        if_log.is_success = is_success

        if user:
            if_log._creater_id = user.id

        if_log.log_date = DateUtil.get_current_datetime()

        if_log.save()

        return if_log
