import io
import math
import json
import threading
import urllib, base64
from datetime import datetime
from django.db import transaction
from configurations import settings

from sklearn.linear_model import LinearRegression
from domain.models.da import DsModel, DsModelColumn, DsModelData, DsModelParam, DsModelTrain, DsTagCorrelation
from domain.models.system import AttachFile
from domain.services.logging import LogWriter
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.file.attach_file import AttachFileService
from domain.services.calculation.data_analysis import DaService
# from domain.services.ai.data_processing import DataProcessingService

# 24.07.23 김하늘 추가 알고리즘 라이브러리
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import accuracy_score

# 24.07.23 김하늘 추가 시각화를 위한 import
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import to_hex
import plotly
import plotly.graph_objs as go
import plotly.io as pio


# 24.07.31 김하늘 추가 첨부파일 루트 주소를 가져오기
# from configurations import settings

# 24.08.08 김하늘 추가 PCA처리 메서드 따로 추출
def perform_pca(data, features, target_column, num_components=None, scale_factor=None):
    """
    PCA 수행 및 주성분 시각화 데이터를 반환.

    Args:
        data (pd.DataFrame): 데이터프레임.
        features (list): 독립 변수(특징) 리스트.
        target_column (str): 종속 변수 컬럼 이름.
        num_components (int): 축소할 차원 수(기본값: None, 자동 결정).
        scale_factor (float): 주성분 선분 크기 조정 비율(기본값: 1).

    Returns:
        dict: PCA 결과 및 시각화 데이터.
    """
    
    # 데이터 전처리: 결측치 제거
    data.dropna(inplace=True)

    # # '수집시간'을 datetime 형태로 변환하고 인덱스로 설정
    # data['date_val'] = pd.to_datetime(data['date_val'])
    # data.set_index('date_val', inplace=True)

    # 독립 변수와 종속 변수 분리
    X = data[features]  # 독립 변수
    y = data[target_column]  # 종속 변수

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

# 24.07.23 김하늘 추가 pca 시각화 메서드
def visualize_pca(pca, X, X_pca, X_new):
    plt.scatter(X.iloc[:, 0], X.iloc[:, 1], alpha=0.2, label='Original Data')
    plt.scatter(X_new[:, 0], X_new[:, 1], alpha=0.8, label='Reconstructed Data')

    # 축소된 차원이 1차원인 경우 y값을 0으로 주어 시각화
    if X_pca.shape[1] == 1:
        plt.scatter(X_pca[:, 0], np.zeros_like(X_pca[:, 0]), alpha=0.5, label='PCA Reduced Data (1D)', c='red')

    plt.axis('equal')
    plt.legend()
    plt.title('PCA Visualization')
    
    # 이미지 저장 및 전송
    plt.savefig('PCA.png')
    plt.show()
    
# 24.11.20 김하늘 수정 pca 외 다른 그래프도 처리 가능하도록 수정
def visualize_to_plotly(title, graph1, graph2=None, graph3=None):
    # 차원에 따른 그래프 데이터 처리
    def process_trace(graph):
        """1차원, 2차원 또는 3차원 데이터를 처리하여 Scatter/Scatter3D 트레이스 생성."""
        key = graph.get('key', None)

        if key == 'principal_axes':         # 주성분 축 데이터 처리
            traces = []
            for i, axis in enumerate(graph['data']):   # 각 주성분 축 반복 처리
                dims = axis.shape[1]  # 데이터 차원 확인
                if dims == 1:  # 1D -> 차원 축소된 값
                    x = np.arange(1, len(axis[:, 0]) + 1)  # x 값 자동 생성
                    y = axis[:, 0]
                    return go.Scatter(
                        x=x,
                        y=y,
                        mode='lines',
                        name=f'{graph["name"]} {i + 1}',
                        meta={'auto_x': False} 
                    )
                if dims == 2:  # 2D 주성분 축
                    x, y = axis[:, 0], axis[:, 1]
                    traces.append(go.Scatter(
                        x=x,
                        y=y,
                        mode='lines',
                        name=f'{graph["name"]} {i + 1}',
                        meta={'auto_x': False}  # x값이 자동 생성된 경우를 메타정보로 추가
                    ))
                elif dims == 3:  # 3D 주성분 축
                    x, y, z = axis[:, 0], axis[:, 1], axis[:, 2]
                    traces.append(go.Scatter3d(
                        x=x,
                        y=y,
                        z=z,
                        mode='lines',
                        name=f'{graph["name"]} {i + 1}'
                    ))
                else:
                    raise ValueError(f"Unsupported dimensionality: {dims}D for principal_axes")

            return traces  # 처리된 모든 주성분 축 반환       
        
        else:
            dims = graph['data'].ndim  # 데이터 차원 확인
            if dims == 1 : # 1차원 데이터
                x = np.arange(1, len(graph['data']) + 1)  # x 값 자동 생성
                y = graph['data']
                return go.Scatter(
                    x=x,
                    y=y,
                    mode=graph['mode'],
                    name=graph['name'],
                    meta={'auto_x': True}  # x값이 자동 생성된 경우를 메타정보로 추가
                )
            if dims == 2 and graph['data'].shape[1] == 1:  # 1차원 데이터(np array) -> 차원 축소된 값
                x = np.arange(1, len(graph['data'][:, 0]) + 1)  # x 값 자동 생성
                y = graph['data'][:, 0]
                return go.Scatter(
                    x=x,
                    y=y,
                    mode=graph['mode'],
                    name=graph['name'],
                    meta={'auto_x': False} 
                )
            elif dims == 2 and graph['data'].shape[1] == 2:  # 2차원 데이터
                x, y = graph['data'][:, 0], graph['data'][:, 1]
                return go.Scatter(
                    x=x,
                    y=y,
                    mode=graph['mode'],
                    name=graph['name'],
                    meta={'auto_x': False} 
                )
            elif dims == 2 and graph['data'].shape[1] == 3:  # 3차원 데이터
                x, y, z = graph['data'][:, 0], graph['data'][:, 1], graph['data'][:, 2]
                return go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode='markers',
                    marker= dict(size=2),
                    # marker=dict(size= max(1, 10 - len(graph['data']) // 1000)),   # 데이터가 많을수록 크기 감소
                    name=graph['name']
            )
            else:
                raise ValueError(f"Unsupported data dimensionality: {dims}D")


    # 데이터 처리
    data = []
    for graph in [graph1, graph2, graph3]:
        if graph is not None:
            traces = process_trace(graph)
            if isinstance(traces, list):
                data.extend(traces)  # 리스트면 풀어서 추가
            else:
                data.append(traces)  # 단일 객체면 그대로 추가


    # 레이아웃 설정
    # xaxis 설정
    xaxis = None
    if all(isinstance(trace, go.Scatter) for trace in data):  # 2D Scatter만 포함
        auto_x = all(trace.meta.get('auto_x', False) for trace in data)
        xaxis = dict(
            title=title.get('x', ''),
            tickmode='linear' if auto_x else 'auto',  # x값이 자동 생성된 경우에만 linear 설정
            nticks=20,  # 최대 눈금 개수 제한
        )

    layout = go.Layout(
        title={
            'text': title['main'], 
            'x': 0.5,               # chart title 가운데 정렬
            'xanchor': 'center',    # 중앙에 앵커 설정
            'xref': 'paper',        # **그래프를 기준으로 중앙 정렬
        },
        autosize = True,            # 자동 크기 조정 활성화
        # autosize=False,           # 자동 크기 조정 비활성화
        margin = dict(l=50, r=50, t=50, b=50),  # 좌우 여백 최소화로 제목을 정확히 중앙에 위치
        xaxis = xaxis, 
        yaxis = dict(
            title = title.get('y', '')
        ) if all(isinstance(trace, go.Scatter) for trace in data) else None,
        scene = dict(  # 3D 데이터용 레이아웃
            xaxis_title=title.get('x', ''),
            yaxis_title=title.get('y', ''),
            zaxis_title=title.get('z', '')  # 3D일 경우 z축 제목 추가
        ) if any(isinstance(trace, go.Scatter3d) for trace in data) else None,  # 3D 여부 확인
        showlegend=True  # 강제로 범례 표시
    )
    
    # figure 생성
    fig = go.Figure(data=data, layout=layout)
    
    # Plotly 그래프를 HTML로 변환 (include_plotlyjs = JavaScript 라이브러리 포함 여부 설정)
    # plotly_graph = pio.to_html(fig, full_html=False)  # 라이브러리가 설치되어 있을 때 사용
    # cdn = 라이브러리 포함해서 보내기. 추후에는 false로 해서 내부에 라이브러리 저장하는 방식으로 해야하지 않을까
    plotly_graph = pio.to_html(fig, full_html=False, include_plotlyjs=True, config=dict(responsive=True))

    # Plotly 그래프를 HTML 파일로 저장 (필요시만 활성화)
    # fig.write_html("D:\김하늘\위존\실무\★SF팀\★HL클레무비\개발실무\스터디\plotly_to_html.html")
    # fig.write_html("D:\김하늘\위존\실무\★SF팀\★HL클레무비\개발실무\스터디\plotly_to_html.html", include_plotlyjs='cdn')
    
    return plotly_graph    

def learning_data(context):
    items = []
    posparam = context.posparam
    gparam = context.gparam
    request = context.request
    action = gparam.get('action', 'read')
    user = context.request.user

    # data_svc = DataProcessingService()    # 임시 주석(데이터 가져와야 해서 필요했던 것)

    try:
        # PCA탭에서 조회 버튼을 누르면 pca 설명률 분포를 보여주는 그래프 시각화 
        # action 분리해서 적용버튼 눌렀을 때 사용자의 요구에 맞는 pca를 진행
        if action == 'pca_evr':
            
            '''
            원래는 시스템에서 데이터를 직접 가져와서 분석을 돌리는 방식인 듯함(data_processing.py)
             but,  1. 현재는 해당 데이터의 원본인 file이 없고,
                   2. 쿼리에 해당하는 테이블에 아예 조건에 해당하는 row 자체가 없는 상태.
             --> 아래 과정에서 DB로 날리는 쿼리의 결과가 없어서(데이터가 없어서) 진행이 불가
             다른 테이블(ds_data)에 같은 데이터로 추정되는 데이터가 남아있긴 함

            # to_date = datetime.now()
            # from_date = datetime(2018, 12, 18) # 숫자 포맷팅 01, 02 방식으로 주면 에러 발생함
            # all_yn = "Y"

            # raw_data = data_svc.get_data(from_date, to_date, all_yn)
            # print("raw_data:/n", raw_data)            
            # data = pd.DataFrame.from_dict(raw_data)'''

            ##############################################################################
            
            # 24.08.08 김하늘 추가 data 불러오기(다른 메서드에서 카피)
            
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            daService = DaService('ds_model', md_id)
            num_components = gparam.get('num_components')
            data = daService.read_table_data()

            # 분석에 필요한 컬럼 지정하기            
            # features = ['AP1', 'AP2', 'AP3', 'AP4', 'EC1', 'EC2', 'EC3', 'RAP1', 'RAP2', 'RAP3', 'RAP4'] # 독립변수
            # target_column = 'alarm' # 종속변수

            # 사용자가 선택한 feature와ㅏ target
            x_vars, y_vars = daService.xy_columns()

            if len(x_vars) > 0 and len(y_vars) > 0:
                if len(x_vars) <2 :
                    return {'success':False, 'not_enough_x_vars': True }

                # 지정된 x,y가 있고, x >=2일 때만 PCA 적용 함수 호출
                pca_result = perform_pca(data, x_vars, y_vars, num_components)
            else:
                return {'success':False, 'no_xy_message': True }


            # plt 시각화를 html로 만들어주는 함수 호출
            '''
                [ 예시 ]
                title = { 'main': 전체 그래프 제목, 'x': x축 제목, 'y': y축 제목 }
                graph = { 'data': 데이터, 'mode': chart 종류, 'name': 범례(그래프 개별 명)}

            '''
            title = {'main':'PCA 주성분별 설명 가능한 분산 비율', 'x':'주성분(차원) 수', 'y':'설명 가능 비율'}
            graph1 = {'data':pca_result['explained_variance_ratio'], 'mode':'lines+markers', 'name':'주성분별 설명 비율'}
            graph2 = {'data':pca_result['cumulative_explained_variance'], 'mode':'lines+markers', 'name':'누적 설명 비율'}

            pca_plotly = visualize_to_plotly(title, graph1, graph2)

            items = {'success':True, 'pca_plotly': pca_plotly, 'x_vars_len': len(x_vars) }


        # 사용자 지정 차원으로 축소(pca)
        elif action == 'pca_apply':        
            # 시각화 
            # 시각화를 위해 PCA 축소 결과를 원본 데이터 공간으로 재구성
            # X_new = pca_final.inverse_transform(X_pca)
            
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            daService = DaService('ds_model', md_id)
            num_components = CommonUtil.blank_to_none(gparam.get('num_components'))
            data = daService.read_table_data()

            # # PCA 적용 및 결과 반환
            # features = ['AP1', 'AP2', 'AP3', 'AP4', 'EC1', 'EC2', 'EC3', 'RAP1', 'RAP2', 'RAP3', 'RAP4']
            # target_column = 'alarm'
            
            # 사용자가 선택한 feature와ㅏ target
            x_vars, y_vars = daService.xy_columns()

            if len(x_vars) > 0 and len(y_vars) > 0:
                # num_components를 int로 변환하기
                if num_components != None:
                    num_components = int(num_components)

                # 지정된 x,y가 있을 때만 PCA 적용 함수 호출
                pca_result = perform_pca(data, x_vars, y_vars, num_components)

            else:
                return {'success':False, 'no_xy_message': True }

            new_dim = pca_result['num_components']

            if new_dim < 4 :
                # 새로운 차원이 3차원 이하일 때

                # plt 시각화를 html로 만들어주는 함수 호출
                '''title = {'main':'그래프 제목', 'x':'x축 제목', 'y':'y축 제목'}'''
                title = {'main': 'PCA가 적용된 그래프', 'x': 'PC1', 'y': 'PC2'}

                # 시각화 데이터 준비
                scatter_data = {
                    'data': pca_result['X_pca'], 
                    'name': f'{new_dim}차원 데이터', 
                    'mode': 'markers'
                    }

                pca_plotly = visualize_to_plotly(title, scatter_data)

            else :
                pca_plotly = pca_result

            items = {'success':True, 'pca_plotly': pca_plotly}
            

        # 추후 수정    
        elif action == 'create_model':
        
            # 랜덤 포레스트 모델 생성
            rf_model = RandomForestClassifier(n_estimators=100, random_state=0)

            # AdaBoost 앙상블 모델 생성
            model = AdaBoostClassifier(base_estimator=rf_model, n_estimators=50, random_state=0)
            pca_model = AdaBoostClassifier(base_estimator=rf_model, n_estimators=50, random_state=0)
            
            # 모델 훈련(비교)
            model.fit(X_train, y_train)     # 기본 모델     
            pca_model.fit(X_pca, y_train)   # PCA 적용 모델

            # 테스트 데이터에 대한 예측
            predictions = model.predict(X_test) # 기본 모델 예측
            pca_X_test = pca_final.transform(X_test)    # 예측을 위해 테스트 데이터도 PCA 진행
            pca_predictions = pca_model.predict(pca_X_test) # PCA 모델 예측
            
            # 예측 결과의 정확도 평가
            accuracy = accuracy_score(y_test, predictions)
            print(f'기본모델 test Accuracy: {accuracy:.2f}')
            pca_accuracy = accuracy_score(y_test, pca_predictions)
            print(f'PCA모델 test Accuracy: {pca_accuracy:.2f}')


            # 실제 데이터 예측
            # 미래 5분 후의 알람값 예측을 위해 마지막 30개의 관측치 준비
            future_data = X[-30:]

            # 미래 값 예측
            future_predictions = model.predict(future_data)         # 기본모델
            pca_future_data = pca_final.transform(future_data)      # 관측데이터 PCA 적용
            pca_future_predictions = pca_model.predict(pca_future_data) # PCA 모델 예측

            # # 예측 결과 출력
            # for i, prediction in enumerate(future_predictions, 1):
            #     print(f'기본모델: 5분 후 알람값 예측 {i*10}초: {prediction}')
            
            # 예측 결과 출력
            for i, (basic_pred, pca_pred, real_alarm) in enumerate(zip(future_predictions, pca_future_predictions, y[-30:]), 1):
                print(f'5분 후 알람값 예측 {i*10}초:\n --> 기본모델: {basic_pred}   /   PCA적용모델: {pca_pred}   /   실제 alarm 값: {real_alarm}')

            # 훈련 및 예측이 완료되면 결과값 서버에 전달
            items = {'success':True}
            
            
        ''' 데이터파일저장 : save_ds_model
            데이터파일목록조회 : ds_data_list
            row데이터조회 : ds_rows_list
            데이터파일내용조회 : ds_model_info. prop_data 없으면 csv파일 읽기.
            파일에서 데이터 읽어서 DB저장   make_db_from_file
            DB에서 읽어서 컬럼정보 만들고 저장 make_col_info
            cate_col_list
            데이터컬럼목록(분포)조회 : ds_col_list
            데이터컬럼저장(전처리): save_ds_col_preprocess
            데이터분포그래프조회(수치형) : ds_numcol_boxhist
            범주형데이터히스토그램(범주형) : ds_col_count_plot
            상관관계히트맵(수치형) : ds_heatmap
            데이터컬럼XY지정 : save_ds_col_xy
            데이터산점도조회 : ds_col_scatter
            상관관계값조회 : ds_var_corr_sheet
            회귀분석식 조회 : ds_y_regression_list
            /* 25.02.10 김하늘 추가 */
            모델마스터조회: ds_model_tree_list
        '''
        # 25.02.10 김하늘 추가
        if action == "ds_model_tree_list":
            master_type = gparam.get('master_type')
            keyword = gparam.get('keyword')

            sql = '''
            WITH A AS (
                SELECT 
                    md.id, 
                    md."Name" AS name, 
                    md."Description" AS description, 
                    md."Type" AS type, 
                    md._created
                FROM ds_model md
            ),
            B AS (
                SELECT 
                    A.id,
                    COUNT(mc.*) AS var_count,
                    COUNT(*) FILTER (WHERE mc."X" = 1 OR mc."Y" = 1) AS using_var_count  -- 25.04.14 추가
                FROM A
                INNER JOIN ds_model_col mc ON mc."DsModel_id" = A.id
                GROUP BY A.id
            ),
            F AS (
                SELECT 
                    A.id, 
                    af.id AS file_id, 
                    af."FileName" AS file_name
                FROM A
                INNER JOIN attach_file af ON af."DataPk" = A.id 
                AND af."TableName" = 'ds_model'
            ),
            Master AS (
                SELECT
                    '마스터' AS node_type,
                    CONCAT('MM_', mm.id) AS tree_id,
                    NULL AS tree_master_id,
                    mm.id AS master_id,
                    CAST(NULL AS INTEGER) AS model_id,  -- 자료형 맞춤
                    CAST(NULL AS INTEGER) AS train_id,  -- 자료형 맞춤
                    e."Name" AS equip_name,
                    mm."Name" AS name,
                    mm."Type" AS type,
                    NULL AS ver,
                    NULL AS description,
                    -- NULL AS algorithm_type,
                    mm."_created" AS _created,
                    CAST(NULL AS INTEGER) AS var_count,  -- 자료형 맞춤
                    NULL AS file_name,
                    CAST(NULL AS INTEGER) AS file_id     -- 자료형 맞춤
                FROM ds_master mm
                LEFT OUTER JOIN equ e ON e.id = mm."Equipment_id"
                WHERE 1=1
                '''
            if master_type:
                sql += '''
                AND UPPER(mm."Type") = UPPER(%(master_type)s)
                '''

            sql += '''
            ),
            Model AS (
                SELECT
                    '모델데이터' AS node_type,
                    CONCAT('MD_', md.id) AS tree_id,
                    CONCAT('MM_', md."DsMaster_id") AS tree_master_id,
                    md."DsMaster_id" AS master_id,
                    md.id AS model_id,
                    CAST(NULL AS INTEGER) AS train_id,  -- 자료형 맞춤
                    NULL AS equip_name,
                    md."Name" AS name,
                    COALESCE(tdt."Name", md."Type") AS type,  -- 분석유형 한글명
                    --md."Type" AS type,
                    md."DataVersion" AS ver,
                    md."Description" AS description,
                    -- C."AlgorithmType" AS algorithm_type,
                    md."_created" AS _created,
                    B.var_count AS var_count,  
                    F.file_name AS file_name,  
                    F.file_id AS file_id
                FROM ds_model md
                LEFT JOIN ds_master mm ON mm.id = md."DsMaster_id"
                LEFT JOIN B ON B.id = md.id  
                LEFT JOIN F ON F.id = md.id
                LEFT JOIN code tdt ON tdt."CodeGroupCode" = 'TAGDATA_TYPE'
                    AND tdt."Code" = md."Type"                    

                WHERE 1=1
            '''

            if keyword:
                sql += '''
                AND (
                    UPPER(md."Type") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                    OR UPPER(md."Name") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                    OR UPPER(md."DataVersion") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                    OR UPPER(md."Description") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                )
                '''
            
            sql += '''
            ),
            Train AS (
                SELECT
                    '학습정보' AS node_type,
                    CONCAT('MT_', mt.id) AS tree_id,
                    CONCAT('MD_', mt."DsModel_id") AS tree_master_id,
                    CAST(NULL AS INTEGER) AS master_id,  -- 자료형 맞춤
                    mt."DsModel_id" AS model_id,
                    mt.id AS train_id,
                    NULL AS equip_name,
                    CONCAT('[', COALESCE(ts."Name", mt."TrainStatus"), '] ', mt."AlgorithmType") AS name,
                    COALESCE(tt."Name", mt."TaskType") AS type,  -- 분석유형 한글명
                    mt."Version" AS ver,
                    mt."Description" AS description,
                    mt."_created" AS _created,
                    B.using_var_count AS var_count,
                    --CAST(NULL AS INTEGER) AS var_count,  -- 자료형 맞춤
                    NULL AS file_name,
                    CAST(NULL AS INTEGER) AS file_id     -- 자료형 맞춤
                FROM ds_model_train mt
                LEFT JOIN B ON B.id = mt."DsModel_id"
                LEFT JOIN code ts ON ts."CodeGroupCode" = 'TRAINING_STATUS'
                    AND ts."Code" = mt."TrainStatus"
                LEFT JOIN code tt ON tt."CodeGroupCode" = 'TASK_TYPE'
                    AND tt."Code" = mt."TaskType"
                WHERE 1=1
            '''
            if keyword:
                sql += '''
                AND (
                    UPPER(mt."TaskType") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                    OR UPPER(mt."AlgorithmType") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                    OR UPPER(mt."Version") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                    OR UPPER(mt."Description") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                )
                '''

            sql += '''
            )
            SELECT * FROM Master
            WHERE 1=1
            '''
            if keyword:
                sql += '''
                AND master_id IN (SELECT master_id FROM Model)
                '''

            sql += '''
            UNION ALL
            SELECT * FROM Model
            WHERE 1=1
            '''
            if keyword:
                sql += '''
                --AND model_id IN (SELECT model_id FROM Train)
                AND model_id IN (
                    SELECT model_id FROM Train  -- 손자(DsModelTrain)가 검색 조건에 걸린 경우 (Model 기준에서는 자식)
                    UNION
                    SELECT id FROM ds_model     -- 본인(DsModel)이 검색 조건에 걸린 경우(이 조건이 없으면 손자 검색어 기준으로만 필터링됨)
                    WHERE
                        UPPER("Type") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                        OR UPPER("Name") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                        OR UPPER("DataVersion") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                        OR UPPER("Description") LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                )
                '''

            sql += '''
            UNION ALL
            SELECT * FROM Train

            ORDER BY tree_master_id NULLS FIRST, name ASC;
            '''

            dc = {}
            dc['master_type'] = master_type
            dc['keyword'] = keyword
        
            items = DbUtil.get_rows(sql, dc)  

        if action == 'save_ds_model':
            # md_id = posparam.get('id')
            mm_id = CommonUtil.try_int(posparam.get('mm_id'))
            md_id = CommonUtil.try_int(posparam.get('id'))
            Name = posparam.get('Name')
            Description = posparam.get('Description')
            Type = posparam.get('Type')
            DataVersion = posparam.get('DataVersion', '')

            new_file_id = posparam.get('fileId')
            
            if md_id:
                md = DsModel.objects.get(id=md_id)
            else:
                md = DsModel()
            md.Name = Name
            md.Description = Description
            md.Type = Type
            md.DataVersion = DataVersion if DataVersion else datetime.now().strftime("v%Y%m%d-%H%M%S")
            md.DsMaster_id = mm_id
            md.set_audit(user)
            md.save()
            md_id = md.id

            # set table_name, data_pk
            daService = DaService('ds_model', md_id)

            # attach_file의 dataPk를 업데이트
            if new_file_id:
                fileService = AttachFileService()
                fileService.updateDataPk(new_file_id, md_id)
 
            items = {'success': True, 'md_id':md_id, 'new_file_id':new_file_id }

        elif action == 'ds_data_list':
            keyword = gparam.get('keyword')           
            date_from = gparam.get('date_from')
            date_to = gparam.get('date_to')

            sql=''' 
            with A as (
	            select 
                    dd.id
                    , dd."Name" as name
                    , dd."Description" as description
                    , dd."Type" as type
                    , dd._created
	            from ds_model dd
	            where 1 = 1
            ), B as (
	            select 
                    A.id
	                , count(dc.*) as var_count
	                , count(case when dc."X" = 1 then 1 end) as x_count
	                , count(case when dc."Y" = 1 then 1 end) as y_count
	            from A 
	            inner join ds_model_col dc on dc."DsModel_id" = A.id
	            group by a.id
            ), F as (
	            select 
                    A.id
                    , af.id as file_id
                    , af."FileName" as file_name
                    , af."PhysicFileName" 
	            from A 
	            inner join attach_file af on af."DataPk" = A.id 
	            and af."TableName" = 'ds_data'
            )
            select 
                A.*
                , F.file_id
                , F.file_name
                , F."PhysicFileName" 
                , B.var_count
                , B.x_count
                , B.y_count
            from A 
            left join B on B.id = A.id 
            left join F on F.id = A.id
            order by A._created
            '''
            dc = {}
            items = DbUtil.get_rows(sql, dc)


        elif action == 'ds_rows_list':
            '''
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))

            sql = ''' 
            SELECT 
                mc.id
                , mc."VarIndex"
                , mc."VarName"
            FROM ds_model_col mc
            WHERE mc."DsModel_id" = %(md_id)s
            ORDER BY mc."VarIndex"  
            '''
            dc = {}
            dc['md_id'] = md_id

            xrows = DbUtil.get_rows(sql, dc)

            sql = ''' SELECT dt."RowIndex" '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                sql += ''' 
                , MIN(CASE 
                    WHEN dt."Code" = \'''' + var_name + '''\' 
                    THEN dt."Char1" 
                    END) AS col_''' + str(i+1)
            sql += ''' FROM ds_model_data dt
            WHERE dt."DsModel_id" = %(md_id)s
            GROUP BY dt."RowIndex"
            ORDER BY dt."RowIndex"
            '''
            dc = {}
            dc['md_id'] = md_id

            rows = DbUtil.get_rows(sql, dc)
            items = {
                'success': True,
                'xrows': xrows,
                'rows': rows
            }

        elif action == 'ds_model_info':
            ''' 
            '''
            md_id = gparam.get('md_id')
            sql = ''' 
            select 
                md.id
                , md."Name"
                , md."Description"
                , md."Type"
                , md."DataVersion"
                , md._created
                , (select id as file_id 
                    from attach_file af 
		            where af."DataPk" = md.id 
		            and af."TableName" = 'ds_model' 
                    order by id desc limit 1) as file_id
            from ds_model md
            where md.id = %(md_id)s
            '''
            dc = {}
            dc['md_id'] = md_id
            row = DbUtil.get_row(sql, dc)

            return row
           

        elif action == 'make_db_from_file':
            ''' prop_data 없으면 csv파일 읽어서 prop_data에 저장하고 변수컬럼 저장.
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            # md_id = gparam.get('md_id')
            sql = ''' 
            SELECT 
                md.id
                , md."Name"
                , md."Description"
                , md."Type"
                , md._created
                , (SELECT id as file_id 
                    FROM attach_file af
                    WHERE af."DataPk" = md.id 
		            AND af."TableName" = 'ds_model' order by id desc limit 1) as file_id
            FROM ds_model md
            WHERE md.id = %(md_id)s
            '''
            dc = {}
            dc['md_id'] = md_id
            row = DbUtil.get_row(sql, dc)

            file_id = row['file_id']
            if not file_id:
                return {'success':False, 'message':'파일없음' }

            daService = DaService('ds_model', md_id)

            #q = DsDataTable.objects.filter(DsModel_id=md_id)
            #pd = q.first()
            #if pd:
            #    df = daService.read_table_data()
            #else:
            #    df = daService.read_csv2()

            #df = daService.read_table_data()
            #if not df:
            df = daService.read_csv2()

            daService.make_col_info(df)

            return {'success':True, 'message':'' }


        elif action == 'cate_col_list':
            ''' 컬럼정보를 읽는다.
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))

            sql = ''' 
            SELECT 
                mc.id
                , mc."VarName" AS value
                , mc."VarName" AS text
            FROM ds_model_col mc
            WHERE mc."DsModel_id" = %(md_id)s
                AND mc."CategoryCount" > 0
            ORDER BY mc."VarIndex"  
            '''
            dc = {}
            dc['md_id'] = md_id

            items = DbUtil.get_rows(sql, dc)

            return items

        # 우선 사용 보류. 
        elif action == 'make_col_info':
            ''' table 데이터 읽어서 컬럼정보를 만들어서 저장한다.
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            #md_id = gparam.get('md_id')

            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()
            daService.make_col_info(df)

            return {'success':True, 'message':'' }

        elif action == 'ds_col_list':
            '''
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            sql = ''' 
            SELECT 
                mc.id
                , mc."VarIndex"
                , mc."VarName"
                , mc."DataCount"
                , mc."MissingCount"
                , mc."CategoryCount" 
                , mc."Mean" 
                , mc."Std"
                , mc."Q1"
                , mc."Q2"
                , mc."Q3" 
                , mc."MissingValProcess"
                , mc."DropOutLow"
                , mc."DropOutUpper"
                , mc."X"
                , mc."Y" 
            FROM ds_model_col mc
            WHERE mc."DsModel_id" = %(md_id)s
            ORDER BY mc."VarIndex"  
            '''
            dc = {}
            dc['md_id'] = md_id

            items = DbUtil.get_rows(sql, dc)
         
        elif action == 'save_ds_col_preprocess':
            md_id = posparam.get('md_id')
            Q = posparam.get('Q')
            #Q = json.loads(Q)
            
            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()
            
            # 컬럼별 결측치 처리 방식 & 이상치 기준을 저장하는 딕셔너리 생성
            column_preprocess_info = {}

            for item in Q:
                VarName = item['VarName'] 
                MissingValProcess = CommonUtil.blank_to_none(item['MissingValProcess'])
                DropOutLow = CommonUtil.try_float(item['DropOutLow'])
                DropOutUpper = CommonUtil.try_float(item['DropOutUpper'])

                column_preprocess_info[VarName] = {
                    "MissingValProcess": MissingValProcess,
                    "DropOutLow": DropOutLow,
                    "DropOutUpper": DropOutUpper
                }

                q = DsModelColumn.objects.filter(DsModel_id=md_id, VarIndex=item['VarIndex'])
                dc = q.first()
                if dc:
                    dc.MissingValProcess = MissingValProcess
                    dc.DropOutLow = DropOutLow
                    dc.DropOutUpper = DropOutUpper
                    dc.save()

                # 결측치 처리
                if MissingValProcess == 'drop':
                    df[VarName].dropna(inplace=True)
                elif MissingValProcess == 'mean':
                    df[VarName].fillna(df[VarName].mean(), inplace=True)
                elif MissingValProcess == 'median':
                    df[VarName].fillna(df[VarName].median(), inplace=True)
                elif MissingValProcess == 'mode':
                    # mode()의 return이 배열일 수 있음(최빈값이 여러개)
                    mode_value = df[VarName].mode()
                    df[VarName].fillna(mode_value[0] if not mode_value.empty else None, inplace=True)

                #이상치 제거
                if DropOutLow:
                    df = df[df[VarName] >= DropOutLow]  # ⬅ `VarName`을 컬럼처럼 사용해야 함
                if DropOutUpper:
                    df = df[df[VarName] <= DropOutUpper]
 
            # ds_model_data delete, update
            sql = ''' 
            DELETE 
	        FROM ds_model_data
	        WHERE "DsModel_id"  = %(md_id)s
	            AND "RowIndex" IN (
		            SELECT DISTINCT "RowIndex"
		            FROM ds_model_data dt
		            WHERE "DsModel_id" = %(md_id)s
		            AND "Code" IN (
			            SELECT "VarName" 
			            FROM ds_model_col mc
			            WHERE "DsModel_id" = %(md_id)s
			                AND "MissingValProcess" = 'drop'
		            )
		            -- AND "Char1" IS NULL  -- Char1 값이 nan이나 NaN인 경우 업데이트 안됨
                    AND (dt."Char1" IS NULL OR UPPER(dt."Char1") IN ('NAN', ''))
	            )
            '''
            dc = {}
            dc['md_id'] = md_id
            ret = DbUtil.execute(sql, dc)

            sql = '''
            WITH A AS (
	            SELECT 
                    mc."DsModel_id" AS md_id
                    , "VarName"
                    , (CASE "MissingValProcess" 
                        WHEN 'mean' THEN "Mean" 
                        WHEN 'median' THEN "Q2" 
                        END) new_val
	            FROM ds_model_col mc
	            WHERE "DsModel_id" = %(md_id)s
	                AND "MissingValProcess" IN ('mean', 'median')
            )
            UPDATE ds_model_data 
            SET 
                "Char1" = CASE 
                            WHEN (UPPER(ds_model_data."Char1") IN ('NAN', '') OR ds_model_data."Char1" IS NULL)
                            THEN CAST(A.new_val AS TEXT)
                            ELSE ds_model_data."Char1"
                          END,
                "Number1" = CASE 
                            WHEN (ds_model_data."Number1" IS NULL OR ds_model_data."Number1" = 'NaN'::float) 
                            THEN A.new_val
                            ELSE ds_model_data."Number1"
                          END
            FROM A
            WHERE ds_model_data."DsModel_id" = A.md_id 
                AND ds_model_data."Code" = A."VarName"
                -- AND ds_model_data."Char1" IS NULL   -- Char1 값이 nan이나 NaN인 경우 업데이트 안됨
                AND A.new_val IS NOT NULL 
            '''

            dc = {}
            dc['md_id'] = md_id
            ret = DbUtil.execute(sql, dc)

            daService.make_col_info(df, column_preprocess_info)

            items = {'success': True, 'message':''}

        elif action == 'ds_numcol_boxhist':
            ''' 수치형 데이터에 대해서 히스토그램, 상자수염그림 그리기
            '''
            import matplotlib.pyplot as plt
            #from matplotlib.figure import Figure

            md_id = CommonUtil.try_int(gparam.get('md_id'))

            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()

            num_df = df.select_dtypes(include=['int64','float64'])

            #nrow = math.ceil( len(num_df.columns) / (ncol) )
            nrow = len(num_df.columns)
            
            # fig, ax = plt.subplots(nrows=nrow, ncols=2, figsize=(20, 20))
            fig, ax = plt.subplots(nrows=nrow, ncols=2, figsize=(20, 20), tight_layout=True)
            #plt.subplots_adjust(hspace=0.5)
            #fig, ax = plt.subplots(nrows=nrow, ncols=2)
            #fig.set_figheight(100)
            #fig.set_figwidth(80)
            #fig.tight_layout()
            #fig = Figure()
            #ax = fig.subplots(nrow, ncol)

            for index, key in enumerate(num_df.columns):
                col = num_df[key]
                r = index
                c = 0
                ax1 = ax[r][c]
                ax[r][c].boxplot(col)
                ax[r][c].set_title(key)
                ax[r][c].hlines(y=col.quantile(0.001),color='blue',xmin=0,xmax=2) 
                ax[r][c].hlines(y=col.quantile(0.999),color='red',xmin=0,xmax=2) 

                ax2 = ax[r][c+1]
                ax2.hist(col,bins=10)
                #ax2.vlines(x=col.quantile(0.001),color='blue',ymin=0,ymax=1000) 
                #ax2.vlines(x=col.quantile(0.999),color='red',ymin=0,ymax=1000)
            
            chart_url = daService.plt_url(fig)
            #plt.show()

            return {'success':True, 'chart_url': chart_url}

            import matplotlib.pyplot as plt
            import seaborn as sns

            plt.hist(df_sat["어린이"], bins=10)  # bins: 몇개의 구간으로 나눌 것인가 -> 막대의 수
            plt.show()

            plt.boxplot(df_2018_apr["어린이"])
            plt.show()

            sns.histplot(data=df_sat, x="어른")
            plt.show()

            fig, ax = plt.subplots()
            # 문제 13.

            # ax.hist를 이용해서 가격(price)의 분포를 구합니다. 이때, bins=10, color='indigo'입니다.
            ax.hist(df['price'], bins=10, color='indigo')
            ax.set_xlabel('price')
            ax.set_ylabel('count')
            ax.set_facecolor('white')

            sns.boxplot(data=df_2018_apr, y="어린이")

            ncol = 4
            nrow = 10
            fig, ax = plt.subplots(nrows=nrow, ncols=ncol, figsize=(20, 40))

            for i, X_Feature in enumerate(X_Features):
                row = i // ncol
                col = (i % ncol)
                ax1 = ax[row, col]
                ax1.hist(train_X[X_Feature],bins=100)    
                ax1.set_title(X_Feature)
            plt.show()
           

        elif action == 'ds_col_count_plot':
            ''' 범주형 히스토그램
            '''
            import matplotlib.pyplot as plt
            import seaborn as sns
            #from matplotlib.figure import Figure

            md_id = CommonUtil.try_int(gparam.get('md_id'))

            variables = gparam.get('variables')
            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()
            
            cate=[]
            var_list = variables.split(',')
            if len(var_list) > 0:
                for key in var_list:
                    if df[key].dtype=='O':
                        cate.append(key)
            else:
                for key in df.columns:
                    if df[key].dtype=='O':
                        cate.append(key)

            #fig = plt.figure(figsize=(15,10))
            cate_count = len(cate)
            #fig, ax = plt.subplots(cate_count, 1, constrained_layout=True)
            fig, ax = plt.subplots(cate_count, 1, tight_layout=True)
            plt.subplots_adjust(hspace=0.5)

            for index, key in enumerate(cate): #범주형 데이터에 대한 변수명 리스트입니다.
                # Hint. sns.countplot을 이용합니다. hue 옵션을 사용합니다.
                #sns.countplot(x=i, data=df, hue=hue_column)
                if cate_count == 1:
                    axis = ax
                else:
                    axis = ax[index]
                sns.countplot(x=key, data=df, ax=axis)
                #ax[index].set_title(key)
                #plt.xticks(rotation=45)
            #plt.subplots_adjust(hspace=10)

            chart_url = daService.plt_url(fig)
            #plt.show()

            return {'success':True, 'chart_url': chart_url}


        elif action == 'ds_heatmap':
            ''' 상관관계 히트맵
            '''
            import matplotlib.pyplot as plt
            import seaborn as sns
            #from matplotlib.figure import Figure

            md_id = CommonUtil.try_int(gparam.get('md_id'))
            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()

            #num_df = df.select_dtypes(include=['int64','float64'])

            # corr() 실행 전 숫자형 컬럼만 선택
            df_numeric = df.select_dtypes(include=['number'])
            corr_df = df_numeric.corr()
            # corr_df = df.corr()

            # seaborn을 사용하여 heatmap 출력
            fig = plt.figure(figsize=(15,10))
            # fig = plt.figure(figsize=(15,10), tight_layout=True)
            sns.heatmap(corr_df, annot=True, cmap='PuBu')
            #fig = Figure()
           
            chart_url = daService.plt_url(fig)
            #plt.show()

            return {'success':True, 'chart_url': chart_url}


        elif action == 'save_ds_col_xy':
            '''
            사용자가 선택한 독립변수(x)와 종속변수(y) 간의 회귀분석
            '''
            md_id = CommonUtil.try_int(posparam.get('md_id'))
            Q = posparam.get('Q')
            #Q = json.loads(Q)

            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()

            x_cols = []
            y_cols = []
            non_numeric_x_cols = []  # 수치형이 아닌 X 변수 리스트
            non_numeric_y_cols = []  # 수치형이 아닌 Y 변수 리스트

            for item in Q:
                q = DsModelColumn.objects.filter(DsModel_id=md_id)
                q = q.filter(VarIndex=item['VarIndex'])
                dc = q.first()
                dc.X = 1 if item['X'] else None
                dc.Y = 1 if item['Y'] else None
                dc.save()

                if item['X']:
                   x_cols.append(item['VarName'])
                if item['Y']:
                   y_cols.append(item['VarName'])

            items = { 'success': True }

            simplelinear = LinearRegression()
            multilinear = LinearRegression()

            #corr = df[x_cols + y_cols].corr()

            # 25.03.07 김하늘 추가
            # df에서 수치형 컬럼만 선택 (casting 오류 방지)
            df_numeric = df.select_dtypes(include=[np.number])

            # x_cols와 y_cols에서 수치형 컬럼만 유지
            valid_x_cols = []
            for col in x_cols:
                if col in df_numeric.columns:
                    valid_x_cols.append(col)
                else:
                    non_numeric_x_cols.append(col)
                    # DsModelColumn에서 X 값을 0으로 변경
                    q = DsModelColumn.objects.filter(DsModel_id=md_id, VarName=col)
                    if q.exists():
                        dc = q.first()
                        dc.X = 0  # 수치형이 아니므로 X 값 초기화
                        dc.save()

            x_cols = valid_x_cols

            valid_y_cols = []
            for col in y_cols:
                if col in df_numeric.columns:
                    valid_y_cols.append(col)
                else:
                    non_numeric_y_cols.append(col)
                    # DsModelColumn에서 Y 값을 0으로 변경
                    q = DsModelColumn.objects.filter(DsModel_id=md_id, VarName=col)
                    if q.exists():
                        dc = q.first()
                        dc.Y = 0  # 수치형이 아니므로 Y 값 초기화
                        dc.save()

            y_cols = valid_y_cols
            # y_cols = [col for col in y_cols if col in df_numeric.columns]

            # 수치형이 아닌 변수 메시지 생성
            if non_numeric_x_cols or non_numeric_y_cols:
                items['message'] = {}
                if non_numeric_x_cols:
                    items['message']['non_numeric_x'] = non_numeric_x_cols
                if non_numeric_y_cols:
                    items['message']['non_numeric_y'] = non_numeric_y_cols

            # if non_numeric_x_cols:
                # items['message'] = non_numeric_x_cols

            q = DsTagCorrelation.objects.filter(DsModel_id=md_id)
            q.delete()

            for y in y_cols:

                # 이미 위에서 수치형 데이터만 배열에 담아두어서 아래 로직이 불필요해짐
                # # y변수를 수치형으로 변환 (변환 실패 시 NaN 처리)
                # df[y] = pd.to_numeric(df[y], errors='coerce')

                # # x_cols도 수치형으로 변환
                # for x in x_cols:
                #     df[x] = pd.to_numeric(df[x], errors='coerce')

                # NaN이 포함된 행 제거
                df_filtered = df.dropna(subset=[y] + x_cols) # 불필요한 데이터 복사x 메모리 효율이 올라감
                #df_filtered = df[[y] + x_cols].dropna()

                # 다중 선형 회귀 모델 학습
                multilinear.fit(df_filtered[x_cols], df_filtered[y])

                # beta_0 = float(multilinear.intercept_) # np.float64 → float 변환
                beta_0 = float(multilinear.intercept_)
                # beta_0 = multilinear.intercept_ if np.isscalar(multilinear.intercept_) else multilinear.intercept_.item()
                # if isinstance(beta_0, np.ndarray):
                #     beta_0 = beta_0[0]  # 배열이면 첫 번째 값만 저장

                beta_i_list = multilinear.coef_
                # if isinstance(beta_i_list, np.ndarray) and beta_i_list.ndim > 1:
                #     beta_i_list = beta_i_list[0]  # 2D 배열이면 1D로 변환
                # coef_가 2D 배열일 경우 1D로 변환
                if beta_i_list.ndim > 1:
                    beta_i_list = beta_i_list.flatten()

                cr = DsTagCorrelation()
                cr.DsModel_id = md_id
                cr.YVarName = y
                cr.XVarName = 'intercept_'
                cr.MultiLinearCoef = beta_0  # ✅ PostgreSQL FLOAT8에 적합한 변환
                # cr.MultiLinearCoef = beta_0
                cr.save()

                for i, x in enumerate(x_cols):
                    cr = DsTagCorrelation()
                    cr.DsModel_id = md_id
                    cr.XVarName = x
                    cr.YVarName = y
                    cr.MultiLinearCoef =float(beta_i_list[i]) # np.array → float 변환
                    # cr.MultiLinearCoef =float(beta_i_list[i]) # np.array → float 변환

                    try:
                        corr = df_filtered[x].corr(df_filtered[y])
                    except Exception as e:
                        print(f"상관계수 계산 오류 (X: {x}, Y: {y}): {e}")
                        corr = None

                    cr.r = corr
                    
                    #if corr and (corr > 0.5 or 1==1):  #0.5
                    if True:  #0.5
                        try:
                            # X == Y 체크 (여기서 미리 걸러야 함)
                            if x == y:
                                print(f"X == Y (X: {y}, Y: {y}) → 단순 회귀 분석을 수행하지 않음.")
                                continue  # 다음 Y 변수로 넘어감

                            # 단순 선형 회귀 학습
                            simplelinear.fit(df_filtered[[x]], df_filtered[[y]])
                            beta_0 = float(simplelinear.intercept_)
                            beta_1 = float(simplelinear.coef_[0])  # coef_는 배열이므로 item만 빼서 가져옴
                            # beta_0 = simplelinear.intercept_.flatten()[0]
                            # beta_1 = simplelinear.coef_.flatten()[0]  # coef_는 배열이므로 item만 빼서 가져옴
                            # beta_1 = simplelinear.coef_ 

                            equ = f"y = {beta_1}*x + {beta_0}"  # f-string 사용하여 가독성 향상
                            # equ = 'y = ' + str(beta_1) + '*x +' + str(beta_0)
                            cr.RegressionEquation = equ
                        except Exception as e:
                            print(f"단순 선형 회귀 오류 (X: {x}, Y: {y}): {e}")
                    cr.save()

            return items

        elif action == 'ds_col_scatter':
            '''
            '''
            import seaborn as sns

            md_id = CommonUtil.try_int(gparam.get('md_id'))
            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()

            #num_df = df.select_dtypes(include=['int64','float64'])
            x_vars, y_vars = daService.xy_columns()
            #x_vars = ['Age','Fare']
            #y_vars = ['Fare']
            
            #fig = Figure() # sns에서는 이 구문을 실행하지 않아야 새 창이 안 뜸.
            #ax = fig.subplots()

            if len(x_vars) > 0 and len(y_vars) > 0:
                # 지정된 x,y가 있을 때만 산점도 실행
                pp = sns.pairplot(df, x_vars=x_vars, y_vars=y_vars, diag_kind='hist')
            else:
                return {'success':False, 'no_xy_message': True }
                # pp = sns.pairplot(df, diag_kind='hist') # 그래프가 별도 창에 표시된다.

            scatter_url = daService.plt_url(pp)
            return {'success':True, 'chart_url': scatter_url } 

            import matplotlib.pyplot as plt

            #sns.scatterplot(data=df,x="전용면적(평)",y="거래금액(만원)")
            #plt.savefig("problem_4.png") # 채점을 위한 코드입니다.

            #df_corr=df.corr(numeric_only=True)
            #sns.heatmap(df_corr, annot=True)

            pp = sns.pairplot(stage1_data, x_vars=stage1_data.columns[[14,19,24,29,34]], y_vars=stage1_data.columns[[39,44,49]], diag_kind='hist')

            #pair plot을 그려줍니다.
            for ax in pp.axes.flatten():
                ax.xaxis.label.set_rotation(90) #xlabel과 ylabel를 회전시킵니다.
                ax.yaxis.label.set_rotation(0)
                ax.yaxis.label.set_ha('right')

            #xlabel과 ylabel의 크기를 키웁니다.
            [plt.setp(item.xaxis.get_label(), 'size', 20) for item in pp.axes.ravel()] 
            [plt.setp(item.yaxis.get_label(), 'size', 20) for item in pp.axes.ravel()]

            plt.show()

        elif action == 'ds_var_corr_sheet':
            ''' 상관계수 조회
                가로축 : x1, x2
                세로축 : y변수
                cell 1: r 값.
                cell 2: 다중회귀식

            '''
            # md_id = gparam.get('md_id')
            md_id = CommonUtil.try_int(gparam.get('md_id'))

            sql = ''' 
            SELECT 
                mc.id
                , mc."VarIndex"
                , mc."VarName"
            FROM ds_model_col mc
            WHERE mc."DsModel_id" = %(md_id)s
            AND mc."X" = 1
            ORDER BY mc."VarIndex"  
            '''
            dc = {}
            dc['md_id'] = md_id

            xrows = DbUtil.get_rows(sql, dc)

            sql = '''
            SELECT 
                tc."YVarName"
                , 1 AS grp_idx
                , '상관계수' AS data_type
                , NULL::NUMERIC AS intercept_ '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                # sql += ''' 
                # ,MIN(CASE 
                #     WHEN tc."XVarName" = \'''' + var_name + '''\' 
                #     THEN tc.r 
                #     END)::TEXT AS x''' + str(i+1)
                sql += ''' 
                ,MIN(CASE 
                    WHEN tc."XVarName" = \'''' + var_name + '''\' 
                    THEN tc.r 
                    END)::TEXT AS col_''' + str(i+1)
            sql += ''' 
            FROM ds_tag_corr tc 
            WHERE tc."DsModel_id" = %(md_id)s
            GROUP BY tc."YVarName" 
            UNION ALL
            SELECT 
                tc."YVarName"
                , 2 AS grp_idx
                , '단일회귀식' AS data_type
                , NULL::NUMERIC AS intercept_ '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                # sql += ''' 
                # ,MIN(CASE 
                #     WHEN tc."XVarName" = \'''' + var_name + '''\' 
                #     THEN tc."RegressionEquation" 
                #     END) AS x''' + str(i+1)
                sql += ''' 
                ,MIN(CASE 
                    WHEN tc."XVarName" = \'''' + var_name + '''\' 
                    THEN tc."RegressionEquation" 
                    END) AS col_''' + str(i+1)
            sql += ''' 
            FROM ds_tag_corr tc 
            WHERE tc."DsModel_id" = %(md_id)s
            GROUP BY tc."YVarName" 
            UNION ALL
            SELECT 
                tc."YVarName"
                , 3 AS grp_idx
                , '다중회귀식계수' AS data_type
            , MIN(CASE 
                WHEN tc."XVarName" = 'intercept_' 
                THEN tc."MultiLinearCoef" 
                end) AS intercept_ '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                # sql += ''' 
                # ,MIN(CASE 
                #     WHEN tc."XVarName" = \'''' + var_name + '''\' 
                #     THEN tc."MultiLinearCoef" 
                #     END)::TEXT AS x''' + str(i+1)
                sql += ''' 
                ,MIN(CASE 
                    WHEN tc."XVarName" = \'''' + var_name + '''\' 
                    THEN tc."MultiLinearCoef" 
                    END)::TEXT AS col_''' + str(i+1)
            sql += '''
            FROM ds_tag_corr tc 
            WHERE tc."DsModel_id" = %(md_id)s
            GROUP BY tc."YVarName" 
            ORDER BY 1, 2
            '''
            dc = {}
            dc['md_id'] = md_id
            rows = DbUtil.get_rows(sql, dc)
            
            items = {
                'success': True,
                'xrows': xrows,
                'rows': rows
            }

        elif action == 'ds_y_regression_list':

            md_id = gparam.get('md_id')

            sql = ''' select dc.id, dc."VarIndex", dc."VarName"
            from ds_col dc
            where dc."DsModel_id" = %(md_id)s
            and dc."X" = 1
            order by dc."VarIndex"  
            '''
            dc = {}
            dc['md_id'] = md_id

            xrows = DbUtil.get_rows(sql, dc)

            sql = ''' select vc."YVarName" '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                sql += ''' 
                ,min(case when vc."XVarName" = \'''' + var_name + '''\' then vc."RegressionEquation" end) as re''' + str(i)
            sql += ''' from ds_var_corr vc 
            where vc."DsModel_id" = %(md_id)s
            group by vc."YVarName" 
            '''
            dc = {}
            dc['md_id'] = md_id
            rows = DbUtil.get_rows(sql, dc)    
            
            items = rows

        elif action == 'delete_ds_model':
            md_id = CommonUtil.try_int(posparam.get('md_id'))

            with transaction.atomic():
                # 하위 종속 테이블 삭제
                DsTagCorrelation.objects.filter(DsModel_id=md_id).delete()
                DsModelData.objects.filter(DsModel_id=md_id).delete()
                DsModelColumn.objects.filter(DsModel_id=md_id).delete()

                # DsModel 삭제 (DsModelTrain은 보존됨)
                DsModel.objects.filter(id=md_id).delete()

            items = {'success': True} 

        # 작성중 모델 설정 저장
        elif action == 'save_ds_model_train':
            mt_id = CommonUtil.try_int(posparam.get('id'))
            md_id = CommonUtil.try_int(posparam.get('md_id'))
            # 설정에 필요한 멤버들
            task_type = posparam.get('TaskType')
            algorithm_type = posparam.get('AlgorithmType')
            description = posparam.get('Description')
            # version = posparam.get('Version')

            # 1. 동일 조건으로 필터링된 기존 훈련 정보
            q = DsModelTrain.objects.filter(
                DsModel_id=md_id,
                TaskType=task_type,
                AlgorithmType=algorithm_type
            )

            # 2. 기존 정보를 수정할 건지 여부(mt_id가 있고 모델 학습이 시작되기 전일 때)
            # is_editable = mt_id and q.filter(id=mt_id).exists()
            is_editable = (
                mt_id and
                # q.filter(id=mt_id, TrainStatus='INITIALIZED').exists()
                DsModelTrain.objects.filter(id=mt_id, TrainStatus='INITIALIZED').exists()
            )
            is_new = not is_editable

            # 3. 객체 준비
            if is_editable:
                # mt = q.get(id=mt_id)
                mt = DsModelTrain.objects.get(id=mt_id)
            else:
                latest = q.order_by('-Version').first()
                mt = DsModelTrain(
                    DsModel_id=md_id,
                    TaskType=task_type,
                    AlgorithmType=algorithm_type,
                    TrainStatus='INITIALIZED',
                    # 동일한 훈련 정보 객체가 있으면 버전에 + 0.1을 더해서 저장. 없으면(신규) default=1
                    # Version=((float(latest.Version) + float(0.1) if latest else 1)
                    Version = round(float(latest.Version) + 0.1, 1) if latest else 1.0
                )

            # 4. 공통 처리
            mt.Description = description
            mt.set_audit(user)

            mt.save()

            # 5. 기존에 저장된 파라미터가 있으면 삭제 후 재저장
            DsModelParam.objects.filter(DsModelTrain_id=mt.id).delete()

            hyperParams = json.loads(posparam.get('hyperParams', '{}'))
            param_list = [
                DsModelParam(
                    DsModelTrain_id=mt.id,
                    ParamKey=k,
                    ParamValue=v
                )
                for k, v in hyperParams.items()
            ]
            DsModelParam.objects.bulk_create(param_list)

            # set table_name, data_pk
            # daService = DaService('ds_model', md_id)
 
            items = {'success': True, 'mt_id':mt.id, 
                     'message': '새 훈련 정보가 생성되었습니다.' if is_new else '기존 훈련 정보가 수정되었습니다.' }

        elif action == 'ds_train_info':
            ''' 
            '''
            mt_id = CommonUtil.try_int(gparam.get('mt_id'))

            sql = ''' 
            SELECT 
                mt.id
                , mt."TaskType"
                , mt."AlgorithmType"
                , mt."Description"
                , mt."Version"
                , mt."TrainStatus"
                , ts."Name" AS status_name
                , mt."ApplyYN"
                , mt._created
                , ( 
                    SELECT json_agg(
                        json_build_object(
                            'ParamKey', mp."ParamKey",
                            'ParamValue', mp."ParamValue"
                            )
                        )
                    FROM ds_model_param mp
                    WHERE mp."DsModelTrain_id" = mt.id
                ) AS param_list
            FROM ds_model_train mt
            LEFT JOIN code ts ON ts."CodeGroupCode" = 'TRAINING_STATUS'
                AND ts."Code" = mt."TrainStatus"
            WHERE mt.id = %(mt_id)s
            '''
            dc = {}
            dc['mt_id'] = mt_id
            row = DbUtil.get_row(sql, dc)

            return row

        # 작성중. 모델 학습(ai 서버에 작업 요청)
        elif action == 'learning_data':
            
            # data_svc = DataProcessingService()
            # thread = threading.Thread(target=data_svc.run_model_training)
            # thread.start()
            
            items = {'success':True}        
    except Exception as ex:
        source = '/api/ai/learning_data, action:{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        # # 24.07.16 김하늘 에러 로그 확인
        # print('error: ', ex)
        items = {'success':False, 'message':ex}

    return items
