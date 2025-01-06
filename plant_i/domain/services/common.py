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
    