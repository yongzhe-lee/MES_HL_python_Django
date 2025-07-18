import mimetypes 
import json
from urllib.parse import quote

from  datetime import datetime
#from django.core.cache import cache


class CommonUtil(object):
    """
    """

    @classmethod
    def unique_id(cls):
        import uuid
        ID = str(uuid.uuid4())
        #nowdate = app_methods.get_now()
        #ID = nowdate.strftime('%Y-%m-%d %H-%M-%S')
        return ID


    @classmethod
    def try_float(cls, number, default=None):
        try:
            return float(number)
        except Exception as e:
            return default


    @classmethod
    def try_int(cls, number, default=None):
        try:
            return int(number)
        except Exception as e:
            return default


    @classmethod
    def try_yyyymmdd(cls, date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return date_text
        except Exception as e:
            return None


    @classmethod
    def blank_to_none(cls, text):
        try:
            if text != '':
                return text
            else:
                return None
        except Exception as e:
            return None


    @classmethod
    def get_utf8_filename(cls, filename):
        return quote(filename.encode('utf-8'))

    @classmethod
    def get_content_type(cls, filename):
        content_type=mimetypes.guess_type(filename)[0]
        return content_type
    
    @classmethod
    def load_json_list(cls, json_str):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return None
    
    @staticmethod
    def check_duplicate(model, field_name, value, exclude_id=None):
        """
        특정 모델의 특정 필드에서 중복된 값을 확인하는 함수.

        :param model: Django 모델 클래스
        :param field_name: 중복 체크할 필드 이름 (문자열)
        :param value: 중복 체크할 필드 값
        :param exclude_id: 중복 체크에서 제외할 객체의 ID (선택적)
        :return: 중복이 존재하면 True, 그렇지 않으면 False
        """
        queryset = model.objects.filter(**{f"{field_name}__iexact": value, "DelYn": "N"})
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()
    
    @classmethod
    def convert_quotation_mark_string(cls, input_string):
        # "a,b,c" -> "'a','b','c'"
        elements = input_string.split(',')
    
        # 각 요소에 작은 따옴표를 추가하고 다시 쉼표로 연결합니다.
        result = ",".join(f"'{element}'" for element in elements)
    
        return result


    @classmethod
    def find_and_set_multilanguage_text(cls, jsonArr:list=[], lang_code:str='ko-KR', text:str=''):
        is_find = False
        for dic in jsonArr:
            language = dic.get('language')
            if language==lang_code:
                dic['text'] = text
                is_find = True

        if is_find == False:
            new_dic = {}
            new_dic['language'] = lang_code
            new_dic['text'] = text
            jsonArr.append(new_dic)

        return jsonArr

    # 백엔드 공통 유틸: camel ↔ snake 변환 유틸리티 클래스 (class method 기반)
    @classmethod
    def camel_to_snake_dict(cls, data: dict) -> dict:
        import re
        def camel_to_snake(s): return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
        return {camel_to_snake(k): v for k, v in data.items()}

    @classmethod
    def snake_to_camel_dict(cls, data: dict) -> dict:
        def snake_to_camel(s): 
            parts = s.split('_')
            return parts[0] + ''.join(word.capitalize() for word in parts[1:])
        return {snake_to_camel(k): v for k, v in data.items()}

    @classmethod
    def res_snake_to_camel(cls, data_list: list) -> list:
        """
        리스트 내의 딕셔너리 key를 snake_case에서 camelCase로 변환하여 반환합니다.
        """
        if not isinstance(data_list, list):
            return data_list
        return [cls.snake_to_camel_dict(item) if isinstance(item, dict) else item for item in data_list]


            
    @classmethod
    def get_content_type_ex(cls, extension:str)->str:
       
        content_types = {
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'csv': 'text/csv',
            'zip': 'application/zip',
            'hwp': 'application/x-hwp',
            'png': 'image/png',
            'gif': 'image/gif',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        content_type = content_types.get(extension, 'application/octet-stream')
        return content_type