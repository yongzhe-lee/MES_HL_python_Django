import os,psycopg2, pickle
import pandas as pd
import numpy as np
import subprocess
import uuid
from io import BytesIO

from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier
from sklearn.metrics import accuracy_score

from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.models.da import LearningLog
from configurations import settings

class DataProcessingService():
    model_file_path = settings.LEARNING_MODEL_PATH    
    model_filename = 'daeilwoodtech_model.pkl' # 모델명
    bat_file_path = model_file_path + 'learning_model.bat'  # .bat 파일경로
    model = None

    def __init__(self):
        pass
    
    def get_data(self, from_date, to_date, all_yn):
        try:
            sql = '''
            with A as (
                select substring(to_char(td.data_date,'yyyy-mm-dd hh24:mi:ss'),1,18)||'0' as date_val
                ,min(case when td.tag_code = 'AP1' then td.data_value end) as "AP1"
                ,min(case when td.tag_code = 'AP2' then td.data_value end) as "AP2"
                ,min(case when td.tag_code = 'AP3' then td.data_value end) as "AP3"
                ,min(case when td.tag_code = 'AP4' then td.data_value end) as "AP4"
                ,min(case when td.tag_code = 'EC1' then td.data_value end) as "EC1"
                ,min(case when td.tag_code = 'EC2' then td.data_value end) as "EC2"
                ,min(case when td.tag_code = 'EC3' then td.data_value end) as "EC3"
                ,min(case when td.tag_code = 'RAP1' then td.data_value end) as "RAP1"
                ,min(case when td.tag_code = 'RAP2' then td.data_value end) as "RAP2"
                ,min(case when td.tag_code = 'RAP3' then td.data_value end) as "RAP3"
                ,min(case when td.tag_code = 'RAP4' then td.data_value end) as "RAP4"
                ,min(case when td.tag_code = 'LPM_EM_STOP' then td.data_value end) as "LPM_EM_STOP"
                from tag t 
                inner join tag_dat td on td.tag_code = t.tag_code and td.tag_code in 
                ('AP1','AP2','AP3','AP4','EC1','EC2','EC3'
                ,'RAP1','RAP2','RAP3','RAP4','LPM_EM_STOP')
                inner join equ e on e.id = t."Equipment_id" and e."Code" in ('EQ_A_PRESS_2','EQ_B_ETC_5')
                where 1=1
                and td.data_date > '2023-12-18' --실제수집일 이후
                --and td.data_date between %(from_date)s and %(to_date)s 
                group by substring(to_char(td.data_date,'yyyy-mm-dd hh24:mi:ss'),1,18)||'0'
                '''
            if all_yn != 'Y':
                sql += '''
                    order by substring(to_char(td.data_date,'yyyy-mm-dd hh24:mi:ss'),1,18)||'0' desc
			        limit 8640
                '''
            sql +='''
            ), T as (
                select *
                , FIRST_VALUE("LPM_EM_STOP") OVER (PARTITION BY val_1_partition ORDER BY date_val desc) AS alarm_val
                from (
                    select 
                    *, count("LPM_EM_STOP") OVER (ORDER BY date_val desc) AS val_1_partition
                    from A ) as T
                order by date_val desc
            )
            select *
            , case when alarm_val - lead(alarm_val) over(order by date_val desc) > 0 then 1
                   else 0 end as alarm
            from T
            '''
            dc = {
                'from_date':from_date,
                'to_date':to_date,
            }
            return DbUtil.get_rows(sql, dc)
        except Exception as ex:
            source = 'DataProcessingService.get_data'
            LogWriter.add_dblog('error', source , ex)
            return []
        
    def get_data_from_tag(self, tag_list):
        tag_code_list = ''
            
        sql = ''' 
        select substring(to_char(td.data_date,'yyyy-mm-dd hh24:mi:ss'),1,18)||'0' as date_val
        '''
        for tag_code in tag_list:
            if tag_code:
                tag_code_list += '\'' + tag_code  + '\','
                sql += ''' 
                ,min(case when td.tag_code = \'''' + tag_code + '''\' then td.data_value end) as "'''+tag_code+'''"
                '''
        sql += ''' 
        from tag t 
        inner join tag_dat td on td.tag_code = t.tag_code and td.tag_code in 
        ('''+tag_code_list[:-1]+''')
        --inner join equ e on e.id = t."Equipment_id" and e."Code" in ('EQ_A_PRESS_2','EQ_B_ETC_5')
        where 1=1
        --and td.data_date > '2023-12-18'
        group by substring(to_char(td.data_date,'yyyy-mm-dd hh24:mi:ss'),1,18)||'0'
        '''

        return DbUtil.get_rows(sql)
        
    def save_model(self, model):
        # 모델을 파일로 저장
        filename = self.model_file_path + self.model_filename
        with open(filename, 'wb') as file:
            pickle.dump(model, file)
            
    def load_model(self):
        filename = self.model_file_path + self.model_filename

        # 저장된 모델이 있는지 확인
        if os.path.exists(filename):
            # 저장된 모델 불러오기
            with open(filename, 'rb') as file:
                self.model = pickle.load(file)
        else:
            # 랜덤 포레스트 모델 생성
            rf_model = RandomForestClassifier(n_estimators=100, random_state=0)
        
            # AdaBoost 앙상블 모델 생성
            self.model = AdaBoostClassifier(base_estimator=rf_model, n_estimators=50, random_state=0)
            
    def learn_data_model_save(self, ret_data):
        try:
            # 데이터프레임 생성
            data = pd.DataFrame.from_dict(ret_data)
        
            # 데이터 전처리: 결측치 제거
            data.dropna(inplace=True)
        
            # '수집시간'을 datetime 형태로 변환하고 인덱스로 설정
            data['date_val'] = pd.to_datetime(data['date_val'])
            data.set_index('date_val', inplace=True)
        
            # 독립 변수와 종속 변수 분리
            X = data[['AP1','AP2','AP3','AP4','EC1','EC2','EC3','RAP1','RAP2','RAP3','RAP4']]  # 독립 변수
            y = data['alarm']  # 종속 변수
        
            # 훈련 데이터와 테스트 데이터로 분리
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
            
            # 기존 학습모델 로드
            self.load_model()
        
            # 교차 검증
            # cv는 교차 검증을 위한 분할 수입니다.
            #cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        
            # 교차 검증 점수 출력
            #print(f'CV scores: {cv_scores}')
            #print(f'CV average score: {cv_scores.mean():.2f}')
        
            # 모델 훈련
            self.model.fit(X_train, y_train)
            
            # 모델 저장
            self.save_model(self.model)
        
            # 테스트 데이터에 대한 예측
            predictions = self.model.predict(X_test)
        
            # 예측 결과의 정확도 평가
            accuracy = accuracy_score(y_test, predictions)
        
            # 미래 5분 후의 알람값 예측을 위해 마지막 30개의 관측치 준비
            future_data = X[-30:]
            
        except Exception as ex:
            source = 'DataProcessingService.learn_data_model_save'
            LogWriter.add_dblog('error', source , ex)
            return {'success':False, 'accuracy':0, 'predict_list':[]}
    
    def get_predict_list(self):
        try:
            # 기존 학습모델 로드
            self.load_model()
            
            # 최근데이터
            ret_data = self.get_data(DateUtil.get_today_string(),DateUtil.get_today_string()+' 23:59:59','N')
            
            # 데이터프레임 생성
            data = pd.DataFrame.from_dict(ret_data)
        
            # 데이터 전처리: 결측치 제거
            data.dropna(inplace=True)
        
            # '수집시간'을 datetime 형태로 변환하고 인덱스로 설정
            data['date_val'] = pd.to_datetime(data['date_val'])
            data.set_index('date_val', inplace=True)
        
            # 독립 변수와 종속 변수 분리
            X = data[['AP1','AP2','AP3','AP4','EC1','EC2','EC3','RAP1','RAP2','RAP3','RAP4']]  # 독립 변수
            y = data['alarm']  # 종속 변수
        
            # 훈련 데이터와 테스트 데이터로 분리
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        
            # 테스트 데이터에 대한 예측
            predictions = self.model.predict(X_test)
        
            # 예측 결과의 정확도 평가
            accuracy = accuracy_score(y_test, predictions)
        
            # 미래 5분 후의 알람값 예측을 위해 마지막 30개의 관측치 준비
            future_data = X[-30:]
        
            # 미래 값 예측
            predict_list = []
            future_predictions = self.model.predict(future_data)
            for i, prediction in enumerate(future_predictions, 1):
                predict_list.append({'future_time':i*10, 'predictive_val':int(prediction)})
                
            return {'success':True, 'accuracy':accuracy, 'predict_list':predict_list}
        except Exception as ex:
            source = 'DataProcessingService.get_predict_list'
            LogWriter.add_dblog('error', source , ex)
            return {'success':False, 'accuracy':0, 'predict_list':[]}
        
    def run_model_training(self):
        start_time = None
        end_time = None
        status = None
        try:
            # 학습 시작 시간 기록
            start_time = DateUtil.get_current_datetime()

            # .bat 파일 실행
            subprocess.run([self.bat_file_path], shell=True, check=True, cwd=self.model_file_path)

            # 학습 종료 시간 기록 및 상태 업데이트
            end_time = DateUtil.get_current_datetime()
            status = "Completed"
            
        except subprocess.CalledProcessError as ex:
            # .bat 파일 실행 중 오류 발생
            end_time = DateUtil.get_current_datetime()
            status = "Failed"
            source = 'DataProcessingService.run_model_training'
            LogWriter.add_dblog('error', source , ex)

        except FileNotFoundError as ex:
            # .bat 파일을 찾을 수 없음
            end_time = DateUtil.get_current_datetime()
            status = "Failed"
            source = 'DataProcessingService.run_model_training'
            LogWriter.add_dblog('error', source , ex)
            
        except Exception as ex:
            # 에러 처리
            end_time = DateUtil.get_current_datetime()
            status = "Failed"
            source = 'DataProcessingService.run_model_training'
            LogWriter.add_dblog('error', source , ex)

        finally:
            self.record_training_history(start_time, end_time, status)

    def record_training_history(self, start_time, end_time, status):
        # DB에 학습 이력 기록
        ll = LearningLog()
        ll.Type = 'learning_model'
        ll.Message = status
        ll.StartTime = start_time
        ll.EndTime = end_time
        ll.save()
        
    def plt_url(self, fig):
        buf = BytesIO()
        fig.savefig(buf, format="png")
        path = settings.FILE_TEMP_UPLOAD_PATH
        file_name = '%s.%s' % (uuid.uuid4(), 'png')
        chart_file = open(path + file_name, mode='ab')
        chart_file.write(buf.getbuffer())
        #upload_file.write(buf)
        chart_file.close()
        file_url = '/api/files/download?temp_file_name='+file_name
        #items.append({'img_path':file_url})
        return file_url
