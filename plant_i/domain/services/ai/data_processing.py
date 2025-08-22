import os,psycopg2, pickle
import subprocess
import uuid
from io import BytesIO
from datetime import datetime, timedelta

# 분석, 알고리즘
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier, MLPRegressor
from xgboost import XGBClassifier, XGBRegressor, plot_tree as xgb_plot_tree
from lightgbm import LGBMClassifier, LGBMRegressor, plot_tree as lgb_plot_tree
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# 시각화
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import to_hex
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 기본 한글 폰트
plt.rcParams['axes.unicode_minus'] = False     # 마이너스(-) 깨짐 방지

# 유틸
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.models.da import DsModelTrain
from configurations import settings


class DataProcessingService():
    # 나중에 다시 정리
    # model_file_path = settings.LEARNING_MODEL_PATH    
    # model_filename = 'daeilwoodtech_model.pkl' # 모델명
    # bat_file_path = model_file_path + 'learning_model.bat'  # .bat 파일경로
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
                inner join das.tag_dat td on td.tag_code = t.tag_code and td.tag_code in 
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
        inner join das.tag_dat td on td.tag_code = t.tag_code and td.tag_code in 
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


    # 25.07.29 김하늘 추가 ------------------------------------------------------------
    def encode_categorical_columns(self, df):
        """
        범주형 데이터(LabelEncoder) 인코딩.

        Args:
            df (pd.DataFrame): 원본 데이터프레임.
            -- (폐기) categorical_cols (list): 범주형 컬럼 리스트.

        Returns:
            pd.DataFrame: 인코딩된 데이터프레임.
        """
        try:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns

            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
            return df

        except Exception as ex:
            source = 'DataProcessingService.encode_categorical_columns'
            LogWriter.add_dblog('error', source, ex)
            raise

    def preprocess_data(self, df, x_columns, y_column, task_type, index_column='id', cate_encoding=True, test_size=0.2, random_state=42, stratify=None):
        """
        데이터 전처리 및 학습/테스트 세트 분리 (옵션)

        Args 및 처리 내용:
            공통) 
                - df (pd.DataFrame): 원본 데이터프레임
                - task_type (str): 분석 타입 ('CLASSIFICATION' 또는 'REGRESSION')
            1) 인덱스 설정
                - index_column (str): 인덱스로 설정할 컬럼 이름. 기본값 'id' = MES의 rst_id가 기준
            2) 범주형 데이터(LabelEncoder) 인코딩
                - cate_encoding (bool): 범주형 데이터 인코딩 여부
            3) 데이터 분할
                - x_columns (list): 독립 변수 컬럼 리스트
                - y_column (str): 타겟 변수 컬럼명
                - test_size (float, optional): 테스트 데이터 비율. 
                - random_state (int, optional): 랜덤 시드. 
                - stratify (pd.Series, optional): 층화 분할 기준(y: 데이터 분할 시, 무작위 분할이 아닌 클래스 비율 유지 옵션)

        Returns:
            전처리된 df를 분할한 데이터 세트.
            tuple: (X_train, X_test, y_train, y_test)
        """
        try:
            # x,y 확인
            if x_columns is None or y_column is None:
                raise ValueError(
                    f"변수가 선택되지 않았습니다. 선택된 X변수:{x_columns}\n선택된 y변수:{y_column}"
                )
            # (1) 인덱스 설정
            if index_column in df.columns:
                # df.set_index(index_column, inplace=True)
                df = df.set_index(index_column)
                if index_column in x_columns:
                    # 인덱스로 설정된 컬럼이 x_colums에 속해있다면 제외
                    x_columns.remove(index_column)

            # (2) 범주형 데이터 인코딩
            if cate_encoding:
                # 라벨 인코딩 함수 호출
                self.encode_categorical_columns(df)
                # categorical_cols = df.select_dtypes(include=['object', 'category']).columns

                # for col in categorical_cols:
                #     le = LabelEncoder()
                #     df[col] = le.fit_transform(df[col].astype(str))

            # (3) 데이터 타입 변환 (int64 → int)
            for col in x_columns + [y_column]:
                if df[col].dtype == 'int64':
                    df[col] = df[col].astype(int)

            # (4) X, y 분리
            # X = df.drop(columns=[y_column]) # y컬럼을 제외한 변수
            X = df[list(x_columns)]  # 독립 변수
            y = df[y_column]

            # (5) 분석 타입에 따른 데이터 검증
            if task_type == "CLASSIFICATION":
                # 분류 문제일 때만 정수형 변환
                if y.dtype == 'float64' and (y % 1 == 0).all():
                    y = y.astype(int)
                if not pd.api.types.is_integer_dtype(y) or len(y.unique()) < 2:
                    raise ValueError(
                        "분류 모델에 부적합한 데이터입니다. y는 정수형이어야 하며, 최소 두 개 이상의 클래스가 필요합니다."
                    )
                # 최소 샘플 수 확인
                class_counts = y.value_counts()
                if class_counts.min() < 2:
                    raise ValueError(
                        f"소수 클래스의 샘플 수가 부족합니다. 최소 2개 이상의 샘플이 필요합니다.<br>"
                        f"클래스의 수가 너무 많고 샘플 수는 적은 경우, 분석 모델에 부적합한 데이터일 수 있습니다.<br>"
                        f"클래스별 샘플 수: {class_counts.to_dict()}"
                    )
            elif task_type == "REGRESSION":
                if not pd.api.types.is_numeric_dtype(y):
                    raise ValueError(
                        "회귀 모델에 부적합한 데이터입니다. y는 숫자형이어야 합니다."
                    )
            else:
                raise ValueError(f"지원하지 않는 분석 타입: {task_type}")

            # (6) stratify 여부 자동 판단(분류 문제에서만 사용)
            if stratify is None and task_type == "CLASSIFICATION":
                is_classification = lambda target: (
                    pd.Series(target).dtype == 'O'
                    or (pd.Series(target).nunique() <= 20 and pd.api.types.is_integer_dtype(target))
                )
                stratify = y if is_classification(y) else None

            # (7) 데이터 분리
            X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=test_size, random_state=random_state, stratify=stratify)

            # (8) 클래스 일치 여부 검증 (분류 문제에서만 수행)
            if task_type == "CLASSIFICATION":
                train_classes = set(y_train.unique())
                test_classes = set(y_test.unique())
                if train_classes != test_classes:
                    missing_in_test = train_classes - test_classes
                    missing_in_train = test_classes - train_classes
                    raise ValueError(
                        f"train과 test 데이터의 클래스가 일치하지 않습니다.<br>"
                        f"train에만 있는 클래스: {missing_in_test}<br>"
                        f"test에만 있는 클래스: {missing_in_train}<br>"
                        "데이터를 재구성하거나 전처리가 필요합니다."
                    )

            return X_train, X_test, y_train, y_test

        except Exception as ex:
            source = 'DataProcessingService.preprocess_data'
            LogWriter.add_dblog('error', source, ex)
            raise

    def apply_smote(self, X_train, y_train, random_state=42, k_neighbors=5):
        """
        SMOTE를 사용하여 훈련 데이터를 오버샘플링.

        SMOTE(Synthetic Minority Over-sampling Technique): 
        분류 분석에서 클래스 불균형 문제(특히 소수 클래스)를 해결하기 위한 오버샘플링 기법.
        k-NN(default: k=5) 기반으로 소수 클래스 샘플 주변에서 새로운 샘플을 생성.
        단, 소수 클래스 샘플이 너무 적으면 적용할 수 없음. 
        사용자가 지정하는 k_neighbors 파라미터는 최소 1 이상이어야 하며, 
        소수 클래스 샘플 수는 k_neighbors + 1개 이상 필요.

        Args:
            X_train (pd.DataFrame): 훈련 데이터 독립 변수.
            y_train (pd.Series): 훈련 데이터 종속 변수.
            random_state (int): 랜덤 시드.
            k_neighbors (int): SMOTE의 k_neighbors 파라미터(기본 5, 최소 1).

        Returns:
            tuple: 
                X_resampled (pd.DataFrame): 오버샘플링된 독립 변수
                y_resampled (pd.Series): 오버샘플링된 종속 변수
            예외:
                SMOTE 적용 불가 시, 원본 데이터를 그대로 반환
        """
        try:
            # 클래스별 샘플 개수 확인
            class_counts = y_train.value_counts()
            minority_class = class_counts.idxmin()
            minority_count = class_counts.min()

            # 예외 처리: 소수 클래스 샘플이 너무 적으면 적용 불가
            if minority_count < 2:
                # 샘플이 하나뿐이면 SMOTE 불가능 → 경고 로그 후 원본 반환
                LogWriter.add_dblog(
                    'error',
                    'DataProcessingService.apply_smote',
                    f"SMOTE 적용 건너뜀: 소수 클래스 '{minority_class}'에 {minority_count}개의 샘플만 존재."
                )
                return X_train, y_train

            # k_neighbors 값 보정: 실제 소수 클래스 샘플 수보다 크지 않도록 조정
            if minority_count <= k_neighbors:
                k_neighbors = max(1, minority_count - 1)

            smote = SMOTE(random_state=random_state, k_neighbors=k_neighbors)
            X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

            return X_resampled, y_resampled

        except Exception as ex:
            source = 'DataProcessingService.apply_smote'
            LogWriter.add_dblog('error', source, ex)
            raise

    # 25.08.13 김하늘 추가 이상치 처리 로직(이상치를 제거하지 않고 정상값의 한계 값으로 치환)
    def clip_outliers(self, X_train, X_test, threshold=3):
        """
        IQR(Interquartile Range) 방법을 사용하여 이상치를 경계값으로 clip.
            - 경계는 Train으로만 계산하고, Test에도 동일하게 적용.
            - 행을 삭제하지 않으므로 (X/y 길이 동일), 동기화 이슈가 발생하지 않음.

        Args:
            X_train (pd.DataFrame): 훈련 데이터 독립 변수.
            X_test (pd.DataFrame | None): 테스트 데이터의 독립 변수
            threshold (float): 이상치로 간주할 IQR 배수. 기본값 3.

        Returns:
            tuple:
                X_train_clipped (pd.DataFrame),
                X_test_clipped  (pd.DataFrame or None)
        """
        try:
            # 수치형 컬럼만 clip 대상
            num_cols = X_train.select_dtypes(include=[np.number]).columns

            if len(num_cols) == 0:
                # 수치형이 없으면 원본 그대로 반환
                return X_train, X_test

            # IQR 계산
            Q1 = X_train.quantile(0.25)
            Q3 = X_train.quantile(0.75)
            IQR = Q3 - Q1

            # IQR가 0이거나 비정상인 경우는 경계 무한대로 처리
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR
            lower = lower.where(np.isfinite(lower), -np.inf).fillna(-np.inf)
            upper = upper.where(np.isfinite(upper),  np.inf).fillna( np.inf)

            # Train clip (수치형만 경계 적용, 비수치 컬럼은 그대로)
            X_train_clipped = X_train.copy()
            X_train_clipped[num_cols] = X_train_clipped[num_cols].clip(lower=lower, upper=upper, axis=1)

            # Test도 같은 경계로 clip
            X_test_clipped = None
            if X_test is not None:
                X_test_clipped = X_test.copy()
                X_test_clipped[num_cols] = X_test_clipped[num_cols].clip(lower=lower, upper=upper, axis=1)

            return X_train_clipped, X_test_clipped

        except Exception as ex:
            source = 'DataProcessingService.clip_outliers'
            LogWriter.add_dblog('error', source, ex)
            raise

    def create_model(self, task_type, algo_type, model_params):
        """
        알고리즘 타입에 따라 모델 생성.
        각 알고리즘별 기본 파라미터를 적용.
        일부 특수 파라미터(class_weight, bootstrap 등)는 별도 처리

        Args:
            task_type (str): 분석 타입(예: REGRESSION(회귀), CLASSIFICATION(분류), ...)
            algo_type (str): 알고리즘 타입 (예: 'RANDOM_FOREST', 'XGBOOST', ...).
            model_params (dict): 모델 파라미터.

        Returns:
            object: 생성된 모델 객체.
        """
        try:
            # ---------- 파라미터 전처리 ----------
            processed_params = {}

            for key, value in model_params.items():
                param_name = key.lower()

                # None이면 넘기지 않음
                if value is None:
                    continue

                # 특수 처리: bootstrap (RandomForest 전용)
                if param_name == 'bootstrap' and algo_type == 'RANDOM_FOREST':
                    processed_params[param_name] = str(value).lower() in ['true', '1']

                # 특수 처리: class_weight (분류에서만 적용 & RandomForest, LightGBM만 dict 처리)
                elif param_name == 'class_weight' and algo_type in ['RANDOM_FOREST', 'LIGHTGBM'] and task_type == 'CLASSIFICATION':
                    processed_params[param_name] = {0: 1, 1: int(value)}

                # 나머지 파라미터 처리
                # 문자열이 숫자로 변환 가능한 경우 int or float으로 변환
                elif value.isdigit():
                    processed_params[param_name] = int(value)

                elif value.replace('.', '', 1).isdigit():
                    processed_params[param_name] = float(value)

                else:
                    try:
                        processed_params[param_name] = int(value)
                    except ValueError:
                        processed_params[param_name] = value


            # ---------- 알고리즘별 기본 파라미터 세팅 & 모델 생성 ----------
            if task_type == "CLASSIFICATION":
                if algo_type == "RANDOM_FOREST":
                    processed_params.setdefault('n_estimators', 100)
                    processed_params.setdefault('random_state', 42)
                    processed_params.setdefault('class_weight', 'balanced')  # 지정 없으면 자동 균형 가중치
                    processed_params.setdefault('bootstrap', True)
                    model = RandomForestClassifier(**processed_params)

                elif algo_type == "XGBOOST":
                    processed_params.setdefault('n_estimators', 100)
                    processed_params.setdefault('random_state', 42)
                    processed_params.setdefault('use_label_encoder', False)
                    processed_params.setdefault('eval_metric', 'logloss')
                    model = XGBClassifier(**processed_params)

                elif algo_type == "LIGHTGBM":
                    processed_params.setdefault('n_estimators', 100)
                    processed_params.setdefault('random_state', 42)
                    processed_params.setdefault('class_weight', 'balanced')  # 지정 없으면 자동 균형 가중치
                    processed_params.setdefault('boosting_type', 'gbdt')
                    processed_params.setdefault('objective', 'binary')
                    model = LGBMClassifier(**processed_params)

                elif algo_type == "SVM":
                    processed_params.setdefault('probability', True)
                    processed_params.setdefault('class_weight', 'balanced')
                    model = SVC(**processed_params)

                elif algo_type == "KNN":
                    model = KNeighborsClassifier(**processed_params)

                elif algo_type == "NAIVE_BAYES":
                    model = GaussianNB(**processed_params)

                elif algo_type == "MLP":
                    processed_params.setdefault('hidden_layer_sizes', (100,))
                    processed_params.setdefault('max_iter', 500)
                    model = MLPClassifier(**processed_params)

                elif algo_type == "CNN":
                    raise NotImplementedError("CNN 모델은 별도의 deep learning 프레임워크 필요")

                else:
                    raise ValueError(f"지원하지 않는 분류 알고리즘: {algo_type}")

            elif task_type == "REGRESSION":
                if algo_type == "RANDOM_FOREST":
                    processed_params.setdefault('n_estimators', 100)
                    processed_params.setdefault('random_state', 42)
                    model = RandomForestRegressor(**processed_params)

                elif algo_type == "LINEAR_REGRESSION":
                    model = LinearRegression(**processed_params)

                elif algo_type == "XGBOOST":
                    processed_params.setdefault('n_estimators', 400)
                    processed_params.setdefault('random_state', 42)
                    model = XGBRegressor(**processed_params)

                elif algo_type == "LIGHTGBM":
                    processed_params.setdefault('n_estimators', 400)
                    processed_params.setdefault('random_state', 42)
                    processed_params.setdefault('boosting_type', 'gbdt')
                    processed_params.setdefault('objective', 'regression')
                    model = LGBMRegressor(**processed_params)

                elif algo_type == "MLP":
                    processed_params.setdefault('hidden_layer_sizes', (100,))
                    processed_params.setdefault('max_iter', 500)
                    model = MLPRegressor(**processed_params)

                else:
                    raise ValueError(f"지원하지 않는 회귀 알고리즘: {algo_type}")

            else:
                raise ValueError(f"지원하지 않는 분석 타입: {task_type}")

            return model

        except Exception as ex:
            LogWriter.add_dblog('error', 'DataProcessingService.create_model', ex)
            raise

    def calculate_metrics(self, task_type, y_true, y_pred, dataset_type):
        """
        모델 성능 지표 계산.

        Args:
            task_type (str): 'CLASSIFICATION' 또는 'REGRESSION'
            y_true (pd.Series): 실제 값.
            y_pred (pd.Series): 예측 값.
            dataset_type (str): 'train' 또는 'test'

        Returns:
            list[dict]: 성능 지표 리스트 (Accuracy, Precision, Recall, F1)
        """
        try:
            metrics_list = []

            if task_type == "CLASSIFICATION":
                # 다중 클래스 문제를 처리하기 위해 average 설정 변경
                average_type = 'macro' if len(pd.Series(y_true).unique()) > 2 else 'binary'
                metrics_list = [
                    {"MetricName": "Accuracy", "MetricValue": accuracy_score(y_true, y_pred), "DatasetType": dataset_type},
                    {"MetricName": "Precision", "MetricValue": precision_score(y_true, y_pred, average=average_type, zero_division=0), "DatasetType": dataset_type},
                    {"MetricName": "Recall", "MetricValue": recall_score(y_true, y_pred, average=average_type, zero_division=0), "DatasetType": dataset_type},
                    {"MetricName": "F1", "MetricValue": f1_score(y_true, y_pred, average=average_type, zero_division=0), "DatasetType": dataset_type},
                ]

            elif task_type == "REGRESSION":
                mse = mean_squared_error(y_true, y_pred)
                rmse = np.sqrt(mse)
                mae = mean_absolute_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                metrics_list = [
                    {"MetricName": "MSE", "MetricValue": mse, "DatasetType": dataset_type},
                    {"MetricName": "RMSE", "MetricValue": rmse, "DatasetType": dataset_type},
                    {"MetricName": "MAE", "MetricValue": mae, "DatasetType": dataset_type},
                    {"MetricName": "R2", "MetricValue": r2, "DatasetType": dataset_type},
                ]

            else:
                raise ValueError(f"지원하지 않는 분석 타입: {task_type}")

            return metrics_list

        except Exception as ex:
            source = 'DataProcessingService.calculate_metrics'
            LogWriter.add_dblog('error', source, ex)
            raise

    # 보류 - ai에서 연산한 결과만 받아서 아래 내용을 view로 보낼지 고민중
    # def save_metrics(self, mt_id, y_train, train_pred, y_test, test_pred):
    #     """
    #     계산된 모델 성능 지표를 DB에 저장.

    #     Args:
    #         mt_id (int): 모델 학습 정보 ID
    #         y_train (Series): 훈련 데이터 실제 값
    #         train_pred (Series): 훈련 데이터 예측 값
    #         y_test (Series): 테스트 데이터 실제 값
    #         test_pred (Series): 테스트 데이터 예측 값
    #     """
    #     try:
    #         # 기존 metric 삭제
    #         DsModelMetric.objects.filter(DsModelTrain_id=mt_id).delete()

    #         # train/test 메트릭 계산
    #         train_metrics = self.calculate_metrics(y_train, train_pred, "train")
    #         test_metrics = self.calculate_metrics(y_test, test_pred, "test")
    #         metrics_to_save = train_metrics + test_metrics

    #         # DB 저장
    #         for m in metrics_to_save:
    #             DsModelMetric.objects.create(
    #                 DsModelTrain_id=mt_id,
    #                 MetricName=m["MetricName"],
    #                 MetricValue=float(f"{m['MetricValue']:.4f}"),
    #                 DatasetType=m["DatasetType"],
    #             )

    #     except Exception as ex:
    #         source = 'DataProcessingService.save_metrics'
    #         LogWriter.add_dblog('error', source, ex)
    #         raise
            
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
        
    def run_model_training(self, train_id):
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
            status = "COMPLETED"
            
        except subprocess.CalledProcessError as ex:
            # .bat 파일 실행 중 오류 발생
            end_time = DateUtil.get_current_datetime()
            status = "FAILED"
            source = 'DataProcessingService.run_model_training'
            LogWriter.add_dblog('error', source , ex)

        except FileNotFoundError as ex:
            # .bat 파일을 찾을 수 없음
            end_time = DateUtil.get_current_datetime()
            status = "FAILED"
            source = 'DataProcessingService.run_model_training'
            LogWriter.add_dblog('error', source , ex)
            
        except Exception as ex:
            # 에러 처리
            end_time = DateUtil.get_current_datetime()
            status = "FAILED"
            source = 'DataProcessingService.run_model_training'
            LogWriter.add_dblog('error', source , ex)

        finally:
            self.record_training_history(train_id, start_time, end_time, status)

    def record_training_history(self, train_id, start_time, end_time, status):
        # DB에 학습 이력 기록
        ll = DsModelTrain.objects.get(id=train_id)
        # ll.ModelFilePath = '' # 별도 분리(save 시 진행)
        ll.TrainStatus = status
        ll.StartedAt = start_time
        ll.EndedAt = end_time
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


    def visualize_tree(self, model, features, task_type="CLASSIFICATION", estimator_index=0):
        """
        모델의 트리 시각화를 생성하고 저장.

        Args:
            model (object): 학습된 모델 객체.
            features (list): 독립 변수(Feature) 이름 리스트.
            task_type (str): 분석 타입 ('CLASSIFICATION' 또는 'REGRESSION').
            estimator_index (int): 시각화할 트리의 인덱스 (기본값: 0).

        Returns:
            str: 저장된 트리 시각화 이미지의 URL.
        """
        try:
            # fig = plt.subplots(figsize=(10, 6))
            fig, ax= plt.subplots(figsize=(10, 6))

            # XGBoost 모델 처리 (Graphviz 대신 matplotlib 강제 사용)
            if isinstance(model, (XGBClassifier, XGBRegressor)):
                # xgb_plot_tree(model, num_trees=estimator_index)
                booster = model.get_booster()
                dump_list = booster.get_dump(with_stats=True) # 트리 list
                tree_text = dump_list[estimator_index]
                ax.text(0, 1, tree_text, fontsize=10, family="monospace", va="top")
                ax.axis('off')

            # LightGBM 모델 처리 (Graphviz 없이 matplotlib 강제 사용)
            elif isinstance(model, (LGBMClassifier, LGBMRegressor)):
                booster = model.booster_
                dump_model = booster.dump_model()
                tree_info = dump_model.get("tree_info", [])

                # LightGBM은 트리 정보를 dict 내부의 list로 제공하며,
                # 'tree_info' 키가 없거나 트리 개수가 적을 수도 있으므로 명시적 검증이 필요
                if estimator_index >= len(tree_info):
                    raise ValueError(f"Tree index {estimator_index} is out of range (max index: {len(tree_info)-1})")

                tree_text = str(tree_info[estimator_index])  # dict → 문자열로 변환하여 출력
                ax.text(0, 1, tree_text, fontsize=10, family="monospace", va="top")
                ax.axis('off')

            # Scikit-learn 계열 트리 처리
            elif hasattr(model, "estimators_"):
                if task_type == "CLASSIFICATION":
                    plot_tree(
                        model.estimators_[estimator_index],
                        feature_names=features,
                        filled=True,
                        rounded=True,
                        # class_names=model.classes_ if hasattr(model, "classes_") else None
                        class_names = [str(cls) for cls in model.classes_] if hasattr(model, "classes_") else None
                        , ax=ax
                    )
                elif task_type == "REGRESSION":
                    plot_tree(
                        model.estimators_[estimator_index],
                        feature_names=features,
                        filled=True,
                        rounded=True
                        , ax=ax
                    )
                else:
                    # raise ValueError(f"지원하지 않는 분석 타입: {task_type}")
                    return None # 지원하지 않는 분석
            else:
                # raise ValueError(f"모델 {type(model).__name__}은 트리 시각화를 지원하지 않습니다.")
                return None # 지원하지 않는 모델

            # 이미지 저장 및 URL 반환
            return self.plt_url(fig)

        except Exception as ex:
            source = 'DataProcessingService.visualize_tree'
            LogWriter.add_dblog('error', source, ex)
            raise


    def visualize_roc_curve(self, model, X_train, y_train, X_test, y_test):
        """
        ROC Curve를 생성하고 저장.

        Args:
            model (object): 학습된 모델 객체.
            X_train (pd.DataFrame): 훈련 데이터 독립 변수.
            y_train (pd.Series): 훈련 데이터 종속 변수.
            X_test (pd.DataFrame): 테스트 데이터 독립 변수.
            y_test (pd.Series): 테스트 데이터 종속 변수.

        Returns:
            dict: 훈련 및 테스트 데이터의 ROC Curve 이미지 URL.
        """
        try:
            # 모델이 predict_proba 메서드를 지원하지 않으면 None 반환
            if not hasattr(model, "predict_proba"):
                return None

            # 데이터 검증: y_train과 y_test가 분류 모델에 적합한지 확인
            if not pd.api.types.is_integer_dtype(y_train) or len(y_train.unique()) < 2:
                raise ValueError(
                    "분류 모델에 부적합한 데이터입니다. y_train은 정수형이어야 하며, 최소 두 개 이상의 클래스가 필요합니다."
                )
            if not pd.api.types.is_integer_dtype(y_test) or len(y_test.unique()) < 2:
                raise ValueError(
                    "분류 모델에 부적합한 데이터입니다. y_test는 정수형이어야 하며, 최소 두 개 이상의 클래스가 필요합니다."
                )

            # 다중 클래스 여부 확인
            is_multiclass = len(y_train.unique()) > 2

            if is_multiclass:
                # 다중 클래스 처리
                train_prob = model.predict_proba(X_train)
                test_prob = model.predict_proba(X_test)

                # ROC Curve - Train
                auc_train = roc_auc_score(y_train, train_prob, multi_class='ovr')
                fig_train = plt.figure(figsize=(6, 6))
                plt.title(f'ROC Curve (Train AUC = {auc_train:.2f})')
                plt.xlabel('Classes')
                plt.ylabel('AUC Score')
                plt.bar(range(train_prob.shape[1]), auc_train)
                roc_train_chart_url = self.plt_url(fig_train)

                # ROC Curve - Test
                auc_test = roc_auc_score(y_test, test_prob, multi_class='ovr')
                fig_test = plt.figure(figsize=(6, 6))
                plt.title(f'ROC Curve (Test AUC = {auc_test:.2f})')
                plt.xlabel('Classes')
                plt.ylabel('AUC Score')
                plt.bar(range(test_prob.shape[1]), auc_test)
                roc_test_chart_url = self.plt_url(fig_test)

            else:
                # 이진 분류 처리
                train_prob = model.predict_proba(X_train)[:, 1]
                test_prob = model.predict_proba(X_test)[:, 1]

                # ROC Curve - Train
                fpr_train, tpr_train, _ = roc_curve(y_train, train_prob)
                auc_train = roc_auc_score(y_train, train_prob)
                fig_train = plt.figure(figsize=(6, 6))
                plt.plot(fpr_train, tpr_train, label=f'ROC Curve (Train AUC = {auc_train:.2f})')
                plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Random Classifier')
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title('ROC Curve (Train Set)')
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                roc_train_chart_url = self.plt_url(fig_train)

                # ROC Curve - Test
                fpr_test, tpr_test, _ = roc_curve(y_test, test_prob)
                auc_test = roc_auc_score(y_test, test_prob)
                fig_test = plt.figure(figsize=(6, 6))
                plt.plot(fpr_test, tpr_test, label=f'ROC Curve (Test AUC = {auc_test:.2f})')
                plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Random Classifier')
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title('ROC Curve (Test Set)')
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                roc_test_chart_url = self.plt_url(fig_test)

            return {
                'roc_train_chart_url': roc_train_chart_url,
                'roc_test_chart_url': roc_test_chart_url
            }

        except Exception as ex:
            source = 'DataProcessingService.visualize_roc_curve'
            LogWriter.add_dblog('error', source, ex)
            raise

    def visualize_feature_importance(self, model, features):
        """
        특성 중요도 그래프를 생성하고 저장.

        Args:
            model (object): 학습된 모델 객체.
            features (list): 독립 변수(Feature) 이름 리스트.

        Returns:
            str: 저장된 특성 중요도 그래프 이미지의 URL. (특성 중요도가 없으면 None 반환)
        """
        try:
            # 모델에 feature_importances_ 속성이 있는지 확인
            if not hasattr(model, 'feature_importances_'):
                return None

            # 특성 중요도 계산
            feature_importances = model.feature_importances_
            feature_importance_df = pd.DataFrame({'Feature': features, 'Importance': feature_importances})
            feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

            # 특성 중요도가 0인 항목 제외
            feature_importance_df = feature_importance_df[feature_importance_df['Importance'] > 0]

            # 특성 중요도 시각화
            import seaborn as sns
            import matplotlib.pyplot as plt

            fig = plt.figure(figsize=(10, 6))
            sns.barplot(x='Importance', y='Feature', data=feature_importance_df)
            plt.title('Feature Importance')

            # 그래프 저장 및 URL 반환
            return self.plt_url(fig)

        except Exception as ex:
            source = 'DataProcessingService.visualize_feature_importance'
            LogWriter.add_dblog('error', source, ex)
            raise

    def perform_pca(self, data, features, target, num_components=None, scale_factor=None):
        """
        PCA 수행 및 주성분 시각화 데이터를 반환.

        Args:
            data (pd.DataFrame): 데이터프레임.
            features (list): 독립 변수(특징) 리스트.
            target (str): 종속 변수 컬럼 이름.
            num_components (int): 축소할 차원 수(기본값: None, 자동 결정).
            scale_factor (float): 주성분 선분 크기 조정 비율(기본값: 1).

        Returns:
            dict: PCA 결과 및 시각화 데이터.
        """
        try:
            # 데이터 전처리: 결측치 제거
            data.dropna(inplace=True)

            # # '수집시간'을 datetime 형태로 변환하고 인덱스로 설정
            # data['date_val'] = pd.to_datetime(data['date_val'])
            # data.set_index('date_val', inplace=True)

            # 독립 변수와 종속 변수 분리
            X = data[features]  # 독립 변수
            y = data[target]  # 종속 변수

            # 데이터 표준화
            scaler = StandardScaler()
            X_standardized = scaler.fit_transform(X)

            # 훈련 데이터와 테스트 데이터로 분리
            X_train, X_test, y_train, y_test = train_test_split(X_standardized, y, test_size=0.2, random_state=0)

            # PCA(주성분 분석) 진행
            pca = PCA()
            pca.fit(X_train)
    
            # 설명 가능한 분산 비율 계산
            explained_variance_ratio = pca.explained_variance_ratio_
            cumulative_explained_variance = np.cumsum(explained_variance_ratio)

            # 사용자 지정 차원이 없으면(value == '') 설명률이 90% 이상인 차원으로 축소
            if (num_components == '') or num_components is None:
                num_components = np.argmax(cumulative_explained_variance >= 0.9) + 1
    
            # num_components 값 확인
            print(f"\nNumber of components explaining at least 90% of the variance: {num_components}")

            # 결정된 주성분 수를 사용하여 PCA 다시 적용
            pca_final = PCA(n_components=num_components)
            X_pca = pca_final.fit_transform(X_train)

            # 24.11.25 주성분 선 폐기. PCA로 변환된 차원의 축 자체가 이미 PC선이기 때문(ex. X축 = PC1, Y축 = PC2, Z축 = PC3)
            # # 데이터 평균과 주성분 벡터 가져오기
            # mean = np.mean(X_pca, axis=0)   # PCA 변환된 데이터의 중심(평균)
            # principal_vector = pca_final.components_  # 축소된 주성분 벡터

            # # 동적으로 scale_factor 계산
            # if scale_factor is None:
            #     scale_factor = 10

            # # 주성분 축 계산 (축소된 차원만 순회, 유연한 차원 처리)
            # principal_axes = []

            # # PC선 조정
            # for i in range(num_components):
            #     scale_factor_adjusted = scale_factor * explained_variance_ratio[i]
            #     start = mean  # 데이터 중심
            #     end = mean + principal_vector[i, :num_components] * scale_factor_adjusted
            #     principal_axes.append(np.array([start, end]))

            return {
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'explained_variance_ratio': explained_variance_ratio,
                'cumulative_explained_variance': cumulative_explained_variance,
                'X_pca': X_pca,
                'num_components': num_components,
                # 'principal_axes': principal_axes
            }

        except Exception as ex:
            source = 'DataProcessingService.perform_pca'
            LogWriter.add_dblog('error', source, ex)
            raise