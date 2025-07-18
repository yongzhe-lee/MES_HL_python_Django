import json
from turtle import pos

import requests
from datetime import datetime
from django.db import transaction
from configurations import settings

from sklearn.linear_model import LinearRegression
from domain.models.da import DsMaster, DsModel, DsModelColumn, DsModelData, DsModelMetric, DsModelParam, DsModelTrain, DsTagCorrelation
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
# from sklearn.metrics import accuracy_score
import sklearn.metrics as metrics

# 24.07.23 김하늘 추가 시각화를 위한 import
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import to_hex
import plotly
import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px


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
                    text=graph.get('text', None),                    # hover용 text
                    hovertemplate=graph.get('hovertemplate', None),  # hovertemplate 지원
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
                    text=graph.get('text', None),                    # hover용 text
                    hovertemplate=graph.get('hovertemplate', None),  # hovertemplate 지원
                    meta={'auto_x': False} 
                )
            elif dims == 2 and graph['data'].shape[1] == 2:  # 2차원 데이터
                x, y = graph['data'][:, 0], graph['data'][:, 1]
                return go.Scatter(
                    x=x,
                    y=y,
                    mode=graph['mode'],
                    name=graph['name'],
                    text=graph.get('text', None),                    # hover용 text
                    hovertemplate=graph.get('hovertemplate', None),  # hovertemplate 지원
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
                    text=graph.get('text', None),                    # hover용 text
                    hovertemplate=graph.get('hovertemplate', None),  # hovertemplate 지원
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
            # tickmode='linear' if auto_x else 'auto',  # x값이 자동 생성된 경우에만 linear 설정
            tickmode='auto',  # x값이 자동 생성된 경우에만 linear 설정
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
                    'color': pca_result['X_test'], 
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
            accuracy = metrics.accuracy_score(y_test, predictions)
            print(f'기본모델 test Accuracy: {accuracy:.2f}')
            pca_accuracy = metrics.accuracy_score(y_test, pca_predictions)
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
            (삭제) 데이터파일목록조회 : ds_data_list   ->  ds_model_tree_list로 대체
            row데이터조회 : ds_rows_list
            데이터파일내용조회 : ds_model_info. prop_data 없으면 csv파일 읽기.
            파일에서 데이터 읽어서 DB저장   make_db_from_file
            DB에서 읽어서 컬럼정보 만들고 저장 make_col_info
            데이터가 범주형인 컬럼 리스트: cate_col_list
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
            통합태그목록조회: integrated_tag_list
            태그집합저장 : save_model_tag
            태그집합조회(데이터 없이 태그만 있을 때) : model_tag_list
            태그집합 데이터 생성: gather_tag_data
            모델(데이터)삭제: delete_ds_model
            학습정보조회: ds_train_info
            모델학습요청: start_learning
            모델성능지표조회: model_metric_list
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
                    e.id AS equip_id,
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
                    CAST(NULL AS INTEGER) AS equip_id,
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
                    --CAST(NULL AS INTEGER) AS master_id,  -- 자료형 맞춤
                    md."DsMaster_id" AS master_id,
                    mt."DsModel_id" AS model_id,
                    mt.id AS train_id,
                    CAST(NULL AS INTEGER) AS equip_id,
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
                LEFT JOIN ds_model md ON md.id = mt."DsModel_id"
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

        if action == 'integrated_tag_list':
            mm_id = CommonUtil.try_int(gparam.get('mm_id'))
            equ_id = None

            if mm_id:
                mm = DsMaster.objects.get(id=mm_id)
                equ_id = mm.Equipment_id
            
            if equ_id:
                # 추후에 설비별로 분기 나눠줄 것(mes, qms, 점도데이터 사용 여부 등)
                # 해당 태그가 아예 존재하지 않을 때 전체 코드 생기는 거 분기해서 처리할 것
                sql = '''
                with PLC as (
                    -- SELECT
                    --    'PLC' AS data_source,
                    --    'ALL_PLC' AS var_code,
                    --    'PLC태그 전체' AS var_name
	                -- UNION all
	                SELECT
		                'PLC' as data_source
                        , 'tag_dat' as table_name
		                , t.tag_code as var_code
		                , t.tag_name as var_name
	                FROM tag t
	                -- tag에 data_src_id 다 들어가기 전까지 보류
	                --	LEFT OUTER JOIN data_src ds ON t.data_src_id = ds.id
	                --	WHERE ds."SourceType" = 'PLC'
	                WHERE 1=1
		                AND tag_code NOT ILIKE '%%.em.%%'
		                AND t."Equipment_id" = %(equ_id)s
	                ),
                EM as (
                    -- SELECT
                    --    'EM' AS data_source,
                    --    'ALL_EM' AS var_code,
                    --    'EM태그 전체' AS var_name	
   	                -- UNION all     
	                SELECT
		                'EM' AS data_source
                        , 'em_tag_dat' as table_name
		                , t.tag_code AS var_code
		                , t.tag_name AS var_name
	                FROM tag t
	                -- tag에 data_src_id 다 들어가기 전까지 보류
	                --	LEFT OUTER JOIN data_src ds ON t.data_src_id = ds.id
	                --	WHERE ds."SourceType" = 'EM'
	                WHERE 1=1
		                AND tag_code LIKE '%%.em.%%'
		                AND t."Equipment_id" = %(equ_id)s	
	                ),	
                MES as (
	                SELECT * 
	                FROM (
	                    VALUES
	                        ('MES', 'if_equ_result', 'id', 'MES검사결과품번(식별용)'),
	                        ('MES', 'if_equ_result', 'mat_cd', '품목코드'),
	                        ('MES', 'if_equ_result', 'bom_ver', 'BOM_VER'),
	                        ('MES', 'if_equ_result', 'data_date', '데이터생성일시'),
	                        ('MES', 'if_equ_result', 'state', 'MES검사결과(합부)')
                    ) as ier(data_source, table_name, var_code, var_name)
                ),
                MES_ITEM as (
	                -- SELECT * 
	                -- FROM (
	                --    values
	                --        ('MES_ITEM', 'test_item_cd', '테스트코드'),
	                --        ('MES_ITEM', 'test_item_val', '테스트값'),
	                --        ('MES_ITEM', 'min_val', '테스트하한값'),
	                --        ('MES_ITEM', 'max_val', '테스트상한값')
                    -- ) as ieri(data_source, var_code, var_name)

                    SELECT
	                    'MES_ITEM' AS data_source,
                        'if_equ_result_item' AS table_name,
  	                    eri.test_item_cd AS var_code,
  	                    '테스트 항목 코드' || ROW_NUMBER() OVER (ORDER BY eri.test_item_cd) AS var_name
                    FROM if_equ_result_item eri 
                    LEFT JOIN if_equ_result er ON er.id = eri.rst_id 
                    WHERE er.equ_cd = (SELECT equ."Code" FROM equ WHERE equ.id = %(equ_id)s)
                    GROUP BY test_item_cd
                ),
                QMS as (
	                SELECT * 
	                FROM (
	                    VALUES
	                        ('QMS', 'if_qms_defect', 'mat_cd', '품목코드'),
	                        ('QMS', 'if_qms_defect', 'bom_ver', 'BOM_VER'),
	                        ('QMS', 'if_qms_defect', 'state', 'QMS검사결과(합부)')
                    ) as iqr(data_source, table_name, var_code, var_name)
                ),
                Viscosity as (
	                SELECT * 
	                FROM (
	                    VALUES
	                        ('Viscosity', 'visco_chk_result', 'storage_temp', '보관규격체크'),
	                        ('Viscosity', 'visco_chk_result',  'agi_cond', '교반조건체크'),
	                        ('Viscosity', 'visco_chk_result',  'clean_check', '세척확인'),
	                        ('Viscosity', 'visco_chk_result',  'refr_in_date', '냉장고입고일자'),
	                        ('Viscosity', 'visco_chk_result',  'visc_value', '점도값')
                    ) as visc(data_source, table_name, var_code, var_name)
                ),
                Tention as (
	                SELECT * 
	                FROM (
	                    VALUES
	                        ('Tention', 'ten_chk_result', 'barcode', '바코드'),
	                        ('Tention', 'ten_chk_result',  'tension_value1', 'Tension Value 1'),
	                        ('Tention', 'ten_chk_result',  'tension_value2', 'Tension Value 2'),
	                        ('Tention', 'ten_chk_result',  'tension_value3', 'Tension Value 3'),
	                        ('Tention', 'ten_chk_result',  'tension_value4', 'Tension Value 4'),
	                        ('Tention', 'ten_chk_result',  'tension_value5', 'Tension Value 5'),
	                        ('Tention', 'ten_chk_result',  'Result', '점도값'),
	                        ('Tention', 'ten_chk_result',  'worker_id', '작업자'),
	                        ('Tention', 'ten_chk_result',  'defect_reason', '불량사유')
                    ) as tent(data_source, table_name, var_code, var_name)
                )
                select * from PLC
                union all
                select * from EM
                union all
                select * from MES
                union all
                select * from MES_ITEM
                union all
                select * from QMS
                union all
                select * from Viscosity
                union all
                select * from Tention
                ''';

                dc = {}
                dc['equ_id'] = equ_id
        
                items = DbUtil.get_rows(sql, dc) 
            else:
                items = []

        if action == 'save_ds_model':
            # md_id = posparam.get('id')
            mm_id = CommonUtil.try_int(posparam.get('mm_id'))
            md_id = CommonUtil.try_int(posparam.get('id'))
            Name = posparam.get('Name')
            Description = posparam.get('Description')
            Type = posparam.get('Type')
            DataVersion = posparam.get('DataVersion', '')
            # StartedAt = posparam.get('StartedAt', '') + ' 00:00:00'
            # EndedAt = posparam.get('EndedAt', '') + ' 23:59:59'
            StartedAt = posparam.get('StartedAt', None)
            EndedAt = posparam.get('EndedAt', None)

            new_file_id = posparam.get('fileId')
            
            if md_id:
                md = DsModel.objects.get(id=md_id)
            else:
                md = DsModel()
            md.Name = Name
            md.Description = Description
            md.Type = Type
            md.DataVersion = DataVersion if DataVersion else datetime.now().strftime("v%Y%m%d-%H%M%S")
            md.StartedAt = StartedAt
            md.EndedAt = EndedAt
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


        elif action =='save_model_tag':
            md_id = posparam.get('md_id')
            # data_source = posparam.get('data_source')
            # var_code = posparam.get('var_code')
            # var_name = posparam.get('var_name')
            # var_index = posparam.get('var_index')

            data = json.loads(posparam.get('data', '{}'))
            model_tag_list = []

            for item in data:  # data는 JSON 배열
                data_source = item['data_source']
                var_code = item['var_code']
                var_index = item['var_index']

                mc = DsModelColumn()

                if data_source in ('PLC', 'EM'):
                    mc.tag_code = var_code
                elif data_source == 'ALARM':
                    mc.alarm_code = var_code

                mc.VarIndex = var_index
                mc.VarName = var_code
                mc.Source = data_source
                mc.DsModel_id = md_id                
                mc.set_audit(user)

                model_tag_list.append(mc)

            # 기존 태그 정보 삭제 (동일 모델)
            DsModelColumn.objects.filter(DsModel_id=md_id).delete()

            # 일괄 저장
            DsModelColumn.objects.bulk_create(model_tag_list)

            # mc = DsModelColumn()
            
            # if data_source in ('PLC', 'EM'):
            #     mc.tag_code = var_code  # FK - tag
            # elif data_source == 'ALARM':
            #     mc.alarm_code = var_code # FK - alarm

            # mc.VarIndex = var_index
            # mc.VarName = var_code
            # mc.Source = data_source
            # mc.DsModel_id = md_id

            items = {'success': True }

        elif action == 'model_tag_list':
            '''
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            sql = ''' 
            SELECT 
                mc.id
                , (mc."VarIndex" + 1) AS var_index
                , mc."Source" AS data_source
                , (case mc."Source" 
                    when 'PLC' then 'tag_dat'
                    when 'EM' then 'em_tag_dat'
                    when 'QMS' then 'if_qms_defect'
                    when 'MES' then 'if_equ_result'
                    when 'MES_ITEM' then 'if_equ_result_item'
                    when 'Viscosity' then 'visco_chk_result'
                    when 'Tention' then 'ten_chk_result'
                    end
                    ) as table_name
                , mc."VarName" AS var_code
                , t.tag_name AS var_name
            FROM ds_model_col mc
            LEFT JOIN tag t ON t.tag_code = mc.tag_code
            WHERE mc."DsModel_id" = %(md_id)s
            ORDER BY mc."VarIndex"  
            '''
            dc = {}
            dc['md_id'] = md_id

            items = DbUtil.get_rows(sql, dc)

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
            sql += ''' FROM ai.ds_model_data dt
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
                , to_char(md."StartedAt", 'yyyy-mm-dd hh24:mi') AS "StartedAt"
                , to_char(md."EndedAt", 'yyyy-mm-dd hh24:mi') AS "EndedAt"
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


        # 진행중
        elif action == 'gather_tag_data':
            ''' 
            tag_data 통합하여 저장하는 쿼리
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            equ_id = CommonUtil.try_int(gparam.get('equ_id'))
            startDt = gparam.get('startDt', '')
            endDt = gparam.get('endDt', '')

            # 우선 screw 버전 하드코딩
            sql = '''
            WITH source_data AS (
	            SELECT 
		            ROW_NUMBER() OVER () - 1 AS row_num
		            , er.id AS id
		            , er.mat_cd AS mat_cd
		            , er.data_date AS data_date     -- 250425부터 존재
	  	            , MAX(CASE WHEN eri.test_item_cd = 'SCREW1_1' THEN eri.test_item_val END) AS SCREW1_1
	  	            , MAX(CASE WHEN eri.test_item_cd = 'SCREW1_2' THEN eri.test_item_val END) AS SCREW1_2
	  	            , MAX(CASE WHEN eri.test_item_cd = 'SCREW1_3' THEN eri.test_item_val END) AS SCREW1_3
	  	            , MAX(CASE WHEN eri.test_item_cd = 'SCREW1_4' THEN eri.test_item_val END) AS SCREW1_4
	  	            , MAX(CASE WHEN eri.test_item_cd = 'SCREW1_5' THEN eri.test_item_val END) AS SCREW1_5
	  	            , MAX(CASE WHEN eri.test_item_cd = 'SCREW1_6' THEN eri.test_item_val END) AS SCREW1_6
	  	            , er.state as state
	            FROM if_equ_result er
	            LEFT JOIN if_equ_result_item eri ON er.id = eri.rst_id
	            WHERE 1=1 
		            AND er.equ_cd = (SELECT equ."Code" FROM equ WHERE equ.id = %(equ_id)s)
	            --	AND state = '1'
		            --AND EXISTS (SELECT 1 FROM equ WHERE equ."Code" = er.equ_cd AND equ.id = %(equ_id)s)
		            AND er.data_date 
			            BETWEEN CAST(%(startDt)s AS TIMESTAMP) 
			            AND CAST(%(endDt)s AS TIMESTAMP)
	            GROUP BY 
		            er.id
		            , er.mat_cd
		            , er.data_date
		            , er.state
            )
            INSERT INTO ai.ds_model_data ("RowIndex", "Code", "Type", "Char1", _created, "DsModel_id")
            SELECT 
	            sd.row_num AS row_index
		        , CASE 
                    WHEN n.num = 0 THEN 'row_num'
		 		    WHEN n.num = 1 THEN 'id'
				    WHEN n.num = 2 THEN 'mat_cd'
				    WHEN n.num = 3 THEN 'data_date'
				    WHEN n.num = 4 THEN 'SCREW1_1'
				    WHEN n.num = 5 THEN 'SCREW1_2'
				    WHEN n.num = 6 THEN 'SCREW1_3'
				    WHEN n.num = 7 THEN 'SCREW1_4'
				    WHEN n.num = 8 THEN 'SCREW1_5'
				    WHEN n.num = 9 THEN 'SCREW1_6'
				    WHEN n.num = 10 THEN 'state'
				    END code
		        , NULL AS "Type" -- type에 PLC 넣을까 고민 아님 그냥 dtype? 
		        , CASE 
			        WHEN n.num = 0 THEN CAST(sd.row_num as text)
		 		    WHEN n.num = 1 THEN CAST(sd.id as text)
				    WHEN n.num = 2 THEN CAST(sd.mat_cd as text)
				    WHEN n.num = 3 THEN TO_CHAR(sd.data_date, 'YYYY-MM-DD HH24:MI:SS')
				    WHEN n.num = 4 THEN sd.screw1_1
				    WHEN n.num = 5 THEN sd.screw1_2
				    WHEN n.num = 6 THEN sd.screw1_3
				    WHEN n.num = 7 THEN sd.screw1_4
				    WHEN n.num = 8 THEN sd.screw1_5
				    WHEN n.num = 9 THEN sd.screw1_6
				    WHEN n.num = 10 THEN sd.state
				    END char1
			    , NOW() AS _created
			    , %(md_id)s AS "DsModel_id"
            FROM 
                source_data sd
                    CROSS JOIN (SELECT GENERATE_SERIES(0, 10) AS num) AS n
            WHERE n.num <> 0    -- row_num 이미 제대로 된걸 가져와서. 쿼리 고치기 귀찮아서 그냥 조건에서만 제외(변경시 루프 숫자 다 고쳐야 함)
            ORDER BY sd.id, n.num
            ;
            '''

            dc = {}
            dc['md_id'] = md_id
            dc['equ_id'] = equ_id
            dc['equ_id'] = startDt
            dc['equ_id'] = endDt
            row = DbUtil.get_row(sql, dc)

            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()
            daService.make_col_info(df)

            items = {'success': True, 'message':''}


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
            ''' 범주형 데이터의 컬럼 정보를 읽는다.
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

        # 시스템 로직이 아닌 쿼리로 데이터 넣어준 경우에만 사용
        elif action == 'make_col_info':
            ''' table 데이터 읽어서 컬럼정보를 만들어서 저장.
            '''
            md_id = CommonUtil.try_int(gparam.get('md_id'))
            #md_id = gparam.get('md_id')

            daService = DaService('ds_model', md_id)
            df = daService.read_table_data()
            daService.make_col_info(df, manual=False)

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
	        FROM ai.ds_model_data
	        WHERE "DsModel_id"  = %(md_id)s
	            AND "RowIndex" IN (
		            SELECT DISTINCT "RowIndex"
		            FROM ai.ds_model_data dt
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
            UPDATE ai.ds_model_data 
            SET 
                "Char1" = CASE 
                            WHEN (UPPER(ai.ds_model_data."Char1") IN ('NAN', '') OR ai.ds_model_data."Char1" IS NULL)
                            THEN CAST(A.new_val AS TEXT)
                            ELSE ai.ds_model_data."Char1"
                          END,
                "Number1" = CASE 
                            WHEN (ai.ds_model_data."Number1" IS NULL OR ai.ds_model_data."Number1" = 'NaN'::float) 
                            THEN A.new_val
                            ELSE ai.ds_model_data."Number1"
                          END
            FROM A
            WHERE ai.ds_model_data."DsModel_id" = A.md_id 
                AND ai.ds_model_data."Code" = A."VarName"
                -- AND ai.ds_model_data."Char1" IS NULL   -- Char1 값이 nan이나 NaN인 경우 업데이트 안됨
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
                axis.set_xticklabels(axis.get_xticklabels(), rotation=45)
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

            # import matplotlib.pyplot as plt

            # #sns.scatterplot(data=df,x="전용면적(평)",y="거래금액(만원)")
            # #plt.savefig("problem_4.png") # 채점을 위한 코드입니다.

            # #df_corr=df.corr(numeric_only=True)
            # #sns.heatmap(df_corr, annot=True)

            # pp = sns.pairplot(stage1_data, x_vars=stage1_data.columns[[14,19,24,29,34]], y_vars=stage1_data.columns[[39,44,49]], diag_kind='hist')

            # #pair plot을 그려줍니다.
            # for ax in pp.axes.flatten():
            #     ax.xaxis.label.set_rotation(90) #xlabel과 ylabel를 회전시킵니다.
            #     ax.yaxis.label.set_rotation(0)
            #     ax.yaxis.label.set_ha('right')

            # #xlabel과 ylabel의 크기를 키웁니다.
            # [plt.setp(item.xaxis.get_label(), 'size', 20) for item in pp.axes.ravel()] 
            # [plt.setp(item.yaxis.get_label(), 'size', 20) for item in pp.axes.ravel()]

            # plt.show()

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

            # 기존 정보를 수정할 건지 여부(mt_id가 있고 모델 학습이 시작되기 전일 때)
            # is_editable = mt_id and q.filter(id=mt_id).exists()
            is_editable = (
                mt_id and
                # q.filter(id=mt_id, TrainStatus='INITIALIZED').exists()
                DsModelTrain.objects.filter(id=mt_id, TrainStatus__in=['INITIALIZED', 'FAILED']).exists()
                # DsModelTrain.objects.filter(id=mt_id, TrainStatus='INITIALIZED').exists()
            )
            is_new = not is_editable

            # 3. 객체 준비
            if is_editable:
                # mt = q.get(id=mt_id)
                mt = DsModelTrain.objects.get(id=mt_id)
                mt.TaskType = task_type  # 기존과 다를 수 있음
                mt.AlgorithmType = algorithm_type
            else:
                # 조건이 동일한 기존 객체 중 가장 마지막 버전 가져오기
                q = DsModelTrain.objects.filter(
                    DsModel_id=md_id,
                    TaskType=task_type,
                    AlgorithmType=algorithm_type
                )
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
 
            items = {'success': True,
                    'mt_id':mt.id,
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
                , mt."Description" AS train_desc
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

        elif action == 'model_metric_list':
            ''' 
            '''
            mt_id = CommonUtil.try_int(gparam.get('mt_id'))

            sql = ''' 
            SELECT 
                mt.id
                , mt."MetricName"
                , mt."MetricValue"
                , mt."DatasetType"
            FROM ds_model_metric mt
            WHERE mt."DsModelTrain_id" = %(mt_id)s
            '''
            dc = {}
            dc['mt_id'] = mt_id
            rows = DbUtil.get_rows(sql, dc)

            items = rows

        elif action == 'delete_ds_model_train':
            mt_id = CommonUtil.try_int(posparam.get('mt_id'))

            mt = DsModelTrain.objects.get(id=mt_id)

            # # 학습 상태가 시작 전이어야 삭제 허용
            # if mt.TrainStatus != 'INITIALIZED':
            #     items = {'success': False, 'message': '이미 학습이 시작된 정보는 삭제할 수 없습니다.'}
            if mt.TrainStatus in ['PENDING', 'TRAINING']:
                items = {'success': False, 'message': '훈련이 진행중인 정보는 삭제할 수 없습니다. 학습이 완료된 후 다시 시도해주세요.'}

            else:
                # 연결된 정보 삭제
                DsModelParam.objects.filter(DsModelTrain_id=mt_id).delete()
                DsModelMetric.objects.filter(DsModelTrain_id=mt_id).delete()
                mt.delete()

                items = {'success': True, 'message': '학습 정보 및 연결된 모든 데이터가 삭제되었습니다.'}

        # 작성중. 모델 학습(ai 서버에 작업 요청)
        elif action == 'start_learning':

            mt_id = posparam.get('mt_id', 0)
            mt = DsModelTrain.objects.get(id=mt_id)

            # if mt.TrainStatus not in ['INITIALIZED', 'FAILED']:
            #     return {'success': False, 'message': '해당 학습은 이미 시작되었거나 완료된 상태입니다.'}


            try:
                # 2. 상태를 준비중으로 변경
                mt.TrainStatus = 'PENDING'
                mt.set_audit(user)
                mt.save()

                # 3. 파라미터 추출
                param_qs = DsModelParam.objects.filter(DsModelTrain_id=mt.id)
                param_dict = {p.ParamKey: p.ParamValue for p in param_qs}

                # 4. AI 서버 요청 구성
                payload = {
                    # 'action': "train",
                    'train_id': mt.id,
                    'model_name': mt.DsModel.Name,
                    'task_type': mt.TaskType,
                    'algorithm': mt.AlgorithmType,
                    'params': param_dict,
                    'request_user': user, # 따로 인증 처리를 하지 않으므로 유저 정보 함께 보내기
                }

                # api_url = 'api/ai/train_model'
                # if settings.AI_API_HOST!="localhost":
                #     api_url = settings.AI_API_HOST + '/api/ai/train_model'

                # response = requests.post(api_url+'?action=train', json=payload)
                # # response = requests.post('10.226.236.34/learning', json=payload)
                # # response.raise_for_status()
                # if response.status_code == 200:
                #     items = {'success': True, "data": mt.id}

            
                #csv을 읽어서 df를 만든다(배포 -> 로컬용)
                # sql = ''' 
                # SELECT 
                #     id
                #     , "TableName"
                #     , "DataPk"
                #     , "AttachName"
                #     , "FileIndex"
                #     , "FileName"
                #     , "PhysicFileName"
                #     , "ExtName"
                #     , "FilePath"
                #     , "_created"
                #     , "FileSize"
                # FROM attach_file 
                # WHERE "TableName" = %(table_name)s
                # AND "DataPk" = %(data_pk)s
                # ORDER BY id DESC 
                # '''
                # dc = {}
                # dc['table_name'] = 'ds_model'
                # # dc['data_pk'] = md_id
                # dc['data_pk'] = 10
                # row = DbUtil.get_row(sql, dc)
                # if not row:
                #     return


                from sklearn.preprocessing import LabelEncoder

                # csv 기반 읽어오기
                # PhysicFileName = row.get('PhysicFileName')
                # file_name = settings.FILE_UPLOAD_PATH + 'ai\\learning_data\\' + PhysicFileName
                # df = pd.read_csv(file_name)

                # table data 읽어오기
                md_id = mt.DsModel_id
                daService = DaService('ds_model', md_id)
                df = daService.read_table_data()

                #데이터 set을  ds_model_data에서 읽어옴
                #전처리도 해야 

                # 데이터 전처리: 결측치 제거
                df.dropna(inplace=True)

                # # '수집시간'을 datetime 형태로 변환하고 인덱스로 설정
                # df['data_date'] = pd.to_datetime(df['data_date'])
                # df.set_index('data_date', inplace=True)
                df.set_index('id', inplace=True)

                # 인코딩 대상 컬럼
                # categorical_cols = ['tag_code', 'mat_cd'] # PLC 데이터 사용 시
                categorical_cols = ['mat_cd']
                label_encoders = {}

                # 각 컬럼에 대해 Label Encoding 적용
                for col in categorical_cols:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col])
                    label_encoders[col] = le  # 나중에 역변환이나 테스트셋에도 재사용 가능

                # # 피벗용 전처리
                # state_mapping = df[['id', 'state']].drop_duplicates().set_index('data_date')
                # # 피벗: 시간(data_date) 기준, tag_code를 컬럼으로 만들고 data_value 값 채우기
                # pivot_df = df.pivot_table(index='id', columns='tag_code', values='data_value')
                # # 피벗된 df에 rst_id, state 다시 병합 (data_date 기준으로)
                # pivot_df = pivot_df.merge(state_mapping, left_index=True, right_index=True)

                # 이후에는 기존과 동일하게 features 지정 가능
                # state를 제외한 나머지 컬럼을 피쳐로

                # features = list(pivot_df.columns.difference(['state', 'id']))  # 분석에 필요 없는 id와 y를 제외한 컬럼(feature)분리
                features = list(df.columns.difference(['state', 'id', 'data_date']))  # 분석에 필요 없는 id와 y를 제외한 컬럼(feature)분리
                # features = ['tag_code', 'data_value', 'rst_id', 'mat_cd'] # 독립변수
                # features = ['tag_code', 'data_value', 'mat_cd']  # rst_id는 feature에서 제거
                # features = ['mat_cd', 'screw1_1', 'screw1_2', 'screw1_3', 'screw1_4', 'screw1_5', 'screw1_6']  # 독립변수 - 로컬(item)
                # features = ['mat_cd', 'SCREW1_1', 'SCREW1_2', 'SCREW1_3', 'SCREW1_4', 'SCREW1_5', 'SCREW1_6']  # 독립변수 - 배포(item)

                target_column = 'state' # 종속변수

                # rst_id로 안묶고 진행할 때
                # # 독립 변수와 종속 변수 분리
                X = df[features]  # 독립 변수
                y = df[target_column]  # 종속 변수

                # # 데이터 표준화(선택사항: 현재는 미사용)
                # scaler = StandardScaler()
                # X_standardized = scaler.fit_transform(X)

                # 훈련 데이터와 테스트 데이터로 분리(표준화)
                # X_train, X_test, y_train, y_test = train_test_split(X_standardized, y, test_size=0.2, random_state=0)
                # 표준화 없이 진행
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

                # # rst_id로 묶어서 진행할 때
                # unique_ids = df['rst_id'].unique()  # rst_id 고유한 값 리스트
                # train_ids, test_ids = train_test_split(unique_ids, test_size=0.2, random_state=0) # rst_id 리스트중 train / test를 나눔 ex) train_ids: 1,2,3 / test_ids = 4

                # train_df = df[df['rst_id'].isin(train_ids)] # train_ids에 속하는 rst_id를 필터링해서 학습 데이터로 사용
                # test_df = df[df['rst_id'].isin(test_ids)] # test_ids에 속하는 rst_id를 필터링해서 예측(테스트) 데이터로 사용

                # X_train = train_df[features]
                # y_train = train_df[target_column]

                # X_test = test_df[features].reset_index(drop=True)
                # y_test = test_df[target_column].reset_index(drop=True)

                #알고리즘에 넣어서 실행

                # 랜덤 포레스트 모델 생성
                # rf_model = RandomForestClassifier(n_estimators=int(param_dict['N_ESTIMATORS']), random_state=int(param_dict['RANDOM_STATE']))

                # AdaBoost 앙상블 모델 생성
                # model = AdaBoostClassifier(base_estimator=rf_model, n_estimators=50, random_state=payload.params.RANDOM_STATE) # base_estimator -> estimators로 바꼈대
                # model = AdaBoostClassifier(estimator=rf_model, n_estimators=int(param_dict['N_ESTIMATORS']), random_state=int(param_dict['RANDOM_STATE']))
                # model = AdaBoostClassifier(n_estimators=int(param_dict['N_ESTIMATORS']), random_state=int(param_dict['RANDOM_STATE']))
                # model = RandomForestClassifier(n_estimators=int(param_dict['N_ESTIMATORS']), random_state=int(param_dict['RANDOM_STATE']), max_depth=int(param_dict['MAX_DEPTH']))
                # model = RandomForestClassifier(n_estimators=int(param_dict['N_ESTIMATORS']), random_state=int(param_dict['RANDOM_STATE']))

                # model = RandomForestClassifier(
                #     n_estimators=int(param_dict.get('N_ESTIMATORS', 50)), 
                #     random_state=int(param_dict.get('RANDOM_STATE', 42)), 
                #     max_depth=int(param_dict.get('MAX_DEPTH', None)),
                #     min_samples_leaf=int(param_dict.get('MIN_SAMPLES_LEAF', None)),
                #     min_samples_split=int(param_dict.get('MIN_SAMPLES_SPLIT', None)),
                #     max_features=int(param_dict.get('MAX_FEATURES', None)),
                #     bootstrap=param_dict.get('BOOTSTRAP', None)
                #     )

                # 기본 파라미터
                rf_params = {
                    'n_estimators': int(param_dict.get('N_ESTIMATORS', 50)),
                    'random_state': int(param_dict.get('RANDOM_STATE', 42)),
                    'bootstrap': str(param_dict.get('BOOTSTRAP', 'True')).lower() in ['true', '1']
                }

                optional_params = ['MAX_DEPTH', 'MAX_FEATURES', 'MIN_SAMPLES_LEAF', 'MIN_SAMPLES_SPLIT']

                for k in optional_params:
                    v = param_dict.get(k)
                    if v is not None:
                        rf_params[k.lower()] = int(v)   # 파라미터로 받았을 때만 model 인자로 추가

                model = RandomForestClassifier(**rf_params) # **변수: 딕셔너리를 풀어서 파라미터로 전달

                # pca_model = AdaBoostClassifier(base_estimator=rf_model, n_estimators=50, random_state=0)
            
                # 모델 훈련(비교)
                # model.fit(X_train, y_train)     # 기본 모델     
                try:
                    model.fit(X_train, y_train)
                except Exception as e:
                    print("에러 발생:", e)
                # pca_model.fit(X_pca, y_train)   # PCA 적용 모델


                # 테스트 데이터에 대한 예측
                # test_predictions = model.predict(X_test) # 기본 모델 예측
                # # pca_X_test = pca_final.transform(X_test)    # 예측을 위해 테스트 데이터도 PCA 진행
                # # pca_predictions = pca_model.predict(pca_X_test) # PCA 모델 예측
            
                # # 예측 결과의 정확도 평가
                # accuracy = metrics.accuracy_score(y_test, test_predictions)
                # precision = metrics.precision_score(y_test, test_predictions)
                # recall = metrics.recall_score(y_test, test_predictions)
                # f1 = metrics.f1_score(y_test, test_predictions)
                # print(f'기본모델 test Accuracy: {accuracy:.2f}\n기본모델 test Precision: {precision:.2f}\n기본모델 test Precision: {recall:.2f}\n기본모델 test Precision: {f1:.2f}\n')
                train_predictions = model.predict(X_train)
                test_predictions = model.predict(X_test)

                # 성능 지표 계산 함수
                def get_metrics(y_true, y_pred, dataset_type):
                    return [
                        {"MetricName": "Accuracy", "MetricValue": metrics.accuracy_score(y_true, y_pred), "DatasetType": dataset_type},
                        {"MetricName": "Precision", "MetricValue": metrics.precision_score(y_true, y_pred, zero_division=0), "DatasetType": dataset_type},
                        {"MetricName": "Recall", "MetricValue": metrics.recall_score(y_true, y_pred, zero_division=0), "DatasetType": dataset_type},
                        {"MetricName": "F1", "MetricValue": metrics.f1_score(y_true, y_pred, zero_division=0), "DatasetType": dataset_type},
                    ]

                # train/test 각각 계산
                train_metrics = get_metrics(y_train, train_predictions, "train")
                test_metrics = get_metrics(y_test, test_predictions, "test")

                # 합쳐서 반환
                metric = train_metrics + test_metrics

                # 기존 metric 삭제 (같은 train_id에 대한 기록 제거)
                DsModelMetric.objects.filter(DsModelTrain_id=mt_id).delete()

                # metric 리스트 저장
                for m in metric:
                    DsModelMetric.objects.create(
                        DsModelTrain_id = mt_id,
                        MetricName = m['MetricName'],
                        MetricValue = float(f"{m['MetricValue']:.4f}"),
                        DatasetType = m['DatasetType']
                    )

                # pca_accuracy = accuracy_score(y_test, pca_predictions)
                # print(f'PCA모델 test Accuracy: {pca_accuracy:.2f}')

                # 실제 데이터 예측 (데이터가 많아서 test_df에서 무작위 rst_id n개 선택하여 샘플링. 우선 한 20개로 진행)
                # num_sample = 20
                # sampled_ids = test_df['rst_id'].drop_duplicates().sample(n=num_sample, random_state=42)
                # sampled_test_df = test_df[test_df['rst_id'].isin(sampled_ids)]

                # X_sampled_test = sampled_test_df[features]
                # sampled_predictions = model.predict(X_sampled_test)
                # 예전 코드
                # # 실제 데이터 예측
                # # 미래 마지막 30개의 관측치 준비(대략 한 사이클에 30개 정도라 치고)
                # future_data = X[-30:]

                # # 값 예측
                # future_predictions = model.predict(future_data)         # 기본모델 - 최근 데이터 30건
                # # pca_future_data = pca_final.transform(future_data)      # 관측데이터 PCA 적용
                # # pca_future_predictions = pca_model.predict(pca_future_data) # PCA 모델 예측

                # # 예측 결과 출력
                # for i, prediction in enumerate(future_predictions, 1):
                #     print(f'기본모델: 5분 후 알람값 예측 {i*10}초: {prediction}')
            
                # # 예측 결과 출력
                # # for i, (basic_pred, pca_pred, real_alarm) in enumerate(zip(future_predictions, pca_future_predictions, y[-30:]), 1):
                # #     print(f'5분 후 알람값 예측 {i*10}초:\n --> 기본모델: {basic_pred}   /   PCA적용모델: {pca_pred}   /   실제 alarm 값: {real_alarm}')
                # for i, (pred_state, real_state) in enumerate(zip(sampled_predictions, sampled_test_df[target_column]), 1):
                #     print(f' 예측값: {pred_state}  /   실제 state 값: {real_state}')

                # # 샘플된 알고리즘에 대한 상태, feature importance.모델설명 그래프
                # title = {'main':'model 예측 추이', 'x':'테스트 데이터(무작위 rst_id가 같은 데이터로 샘플링)', 'y':'예측값(state)'}
                # graph1 = {'data':sampled_predictions, 'mode':'lines+markers', 'name':'모델 예측값'}
                # graph2 = {'data':sampled_test_df[target_column], 'mode':'lines+markers', 'name':'실제 값'}

                #알고리즘에 대한 상태, feature importance.모델설명 그래프
                title = {'main':'model 예측 추이', 'x':'테스트 데이터', 'y':'예측값(state)'}

                graph1 = {
                    'data':y_test, 
                    # 'data': np.column_stack((y_test.index.values, y_test.values)),  # (x, y) 묶기
                    'mode':'lines+markers', 
                    'name':'실제값(0,1)',
                    'text': y_test.index.astype(int).astype(str).values,   # hover용 index
                    'hovertemplate': 'rst_id: %{text}<br>값: %{y}<extra></extra>'
                    }

                graph2 = {
                    'data':test_predictions, 
                    # 'data': np.column_stack((y_test.index.values, test_predictions)),
                    'mode':'lines+markers', 
                    'name':'모델 예측값(0,1)',
                    'text': y_test.index.astype(int).astype(str).values,   # hover용 index
                    'hovertemplate': 'rst_id: %{text}<br>값: %{y}<extra></extra>'
                    } #이게 위로 가야(2번) 예측결과가 잘보임

                pred_plotly = visualize_to_plotly(title, graph1, graph2)

                import matplotlib.pyplot as plt
                import seaborn as sns

                # 특성중요도 그래프
                feature_importances = model.feature_importances_
                feature_importance_df = pd.DataFrame({'Feature': features, 'Importance': feature_importances})
                feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
                # print(feature_importance_df)

                # 시각화 - 특성중요도가 0인 것들은 제외
                feat_fig = plt.figure(figsize=(10, 6))
                sns.barplot(x='Importance', y='Feature', data=feature_importance_df[feature_importance_df['Importance'] > 0])
                plt.title('Feature Importance')

                feat_chart_url = daService.plt_url(feat_fig)

                
                # tree 시각화
                from sklearn.tree import plot_tree

                tree_fig = plt.figure(figsize=(10, 6))
                plot_tree(model.estimators_[(int(param_dict['N_ESTIMATORS']) - 1)], feature_names=features, filled=True, rounded=True)
                # plot_tree(model.estimators_[49], feature_names=features, filled=True, rounded=True)

                tree_chart_url = daService.plt_url(tree_fig)


                # ROC AUR 그래프
                from sklearn.metrics import roc_curve, roc_auc_score

                train_prob = model.predict_proba(X_train) # 테스트 값이 각 클래스로 분류될 확률 ex) [0.92, 0.08]
                test_prob = model.predict_proba(X_test) 

                # ROC Curve - Train
                fpr_train, tpr_train, thresholds_train = roc_curve(y_train, train_prob[:, 1])
                auc_train = roc_auc_score(y_train, train_prob[:, 1])

                fig_train = plt.figure(figsize=(6, 6))
                plt.plot(fpr_train, tpr_train, label=f'ROC Curve (Train AUC = {auc_train:.2f})')
                plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Random Classifier')
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title('ROC Curve (Train Set)')
                plt.legend()
                plt.grid(True)
                plt.tight_layout()

                roc_train_chart_url = daService.plt_url(fig_train)

                # ROC Curve - Test
                fpr_test, tpr_test, thresholds_test = roc_curve(y_test, test_prob[:, 1])
                auc_test = roc_auc_score(y_test, test_prob[:, 1])

                fig_test = plt.figure(figsize=(6, 6))
                plt.plot(fpr_test, tpr_test, label=f'ROC Curve (Test AUC = {auc_test:.2f})')
                plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Random Classifier')
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title('ROC Curve (Test Set)')
                plt.legend()
                plt.grid(True)
                plt.tight_layout()

                roc_test_chart_url = daService.plt_url(fig_test)  # 이미지 URL 저장
                # plt.close(fig_test)

                # 데이터 분포 확인용
                print("y_test 분포:", np.bincount(y_test))
                print("test_prob 샘플:", test_prob[:10, 1])
                print("test_prob[:, 1]:", test_prob[:, 1])

                mt.TrainStatus = 'COMPLETED'
                mt.set_audit(user)
                mt.save()
                # 훈련 및 예측이 완료되면 결과값 서버에 전달
                # 시각화 부분 분리해야 함 특성중요도 그래프 추가할것

                items = {
                    'success':True, 
                    'pca_plotly': pred_plotly,
                    'feat_chart_url': feat_chart_url,
                    'tree_chart_url': tree_chart_url,
                    'roc_train_chart_url': roc_train_chart_url, 
                    'roc_test_chart_url': roc_test_chart_url,
                    # 'metric': metric
                    }

            except Exception as e:
                # 오류 시 상태를 FAILED로 변경

                mt.TrainStatus = 'FAILED'
                mt.set_audit(user)
                mt.save()
                items = {'success': False, 'message': f'AI 서버 요청 실패: {str(e)}',"data": mt.id}
                return items

            # data_svc = DataProcessingService()
            # thread = threading.Thread(target=data_svc.run_model_training)
            # thread.start()
 
    except Exception as ex:
        source = '/api/ai/learning_data, action:{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        # # 24.07.16 김하늘 에러 로그 확인
        # print('error: ', ex)
        items = {'success':False, 'message':ex}

    return items
