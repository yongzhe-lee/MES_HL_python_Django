from asyncio.windows_events import NULL
import math
import numpy as np
import pandas as pd
import json
import plotly

#import matplotlib.pyplot as plt
#import seaborn as sns
#from matplotlib.figure import Figure

from sklearn.linear_model import LinearRegression

from configurations import settings
from domain.models.da import DsData, DsColumn, DsVarCorrelation
from domain.models.system import AttachFile
from domain.models.da import DsDataTable
from domain.services.logging import LogWriter
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.file.attach_file import AttachFileService
from domain.services.calculation.data_analysis import DaService

# 24.07.23 김하늘 추가 알고리즘 라이브러리
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier
from sklearn.metrics import accuracy_score

# 24.07.23 김하늘 추가 시각화를 위한 import
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import to_hex
import plotly.graph_objs as go
import plotly.io as pio
import io
import urllib, base64

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

    # '수집시간'을 datetime 형태로 변환하고 인덱스로 설정
    data['date_val'] = pd.to_datetime(data['date_val'])
    data.set_index('date_val', inplace=True)

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
    plotly_graph = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config=dict(responsive=True))

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
            dd_id = gparam.get('dd_id')
            daService = DaService('ds_data', dd_id)
            num_components = gparam.get('num_components')
            data = daService.read_table_data()
            

            # 분석에 필요한 컬럼 지정하기
            # 독립변수
            features = ['AP1', 'AP2', 'AP3', 'AP4', 'EC1', 'EC2', 'EC3', 'RAP1', 'RAP2', 'RAP3', 'RAP4']
            # 종속변수
            target_column = 'alarm'


            # PCA 적용 함수 호출
            pca_result = perform_pca(data, features, target_column, num_components)

            # plt 시각화를 html로 만들어주는 함수 호출
            '''title = {'main':'그래프 제목', 'x':'x축 제목', 'y':'y축 제목'}'''
            title = {'main':'PCA 주성분별 설명 가능한 분산 비율', 'x':'주성분(차원) 수', 'y':'설명 가능 비율'}
            graph1 = {'data':pca_result['explained_variance_ratio'], 'mode':'lines+markers', 'name':'주성분별 설명 비율'}
            graph2 = {'data':pca_result['cumulative_explained_variance'], 'mode':'lines+markers', 'name':'누적 설명 비율'}

            pca_plotly = visualize_to_plotly(title, graph1, graph2)

            items = {'success':True, 'pca_plotly': pca_plotly}


        # 사용자 지정 차원으로 축소(pca)
        elif action == 'pca_apply':        
            # 시각화 
            # 시각화를 위해 PCA 축소 결과를 원본 데이터 공간으로 재구성
            # X_new = pca_final.inverse_transform(X_pca)
            
            # # 시각화 함수 호출하여 pca 결과 확인
            # visualize(pca_final, X, X_pca, X_new)
            
            dd_id = gparam.get('dd_id')
            daService = DaService('ds_data', dd_id)
            num_components = gparam.get('num_components')
            data = daService.read_table_data()

            # PCA 적용 및 결과 반환
            features = ['AP1', 'AP2', 'AP3', 'AP4', 'EC1', 'EC2', 'EC3', 'RAP1', 'RAP2', 'RAP3', 'RAP4']
            target_column = 'alarm'
            
            # 사용자 지정 차원 == null(선택 안함)일 때 누적 설명 비율이 90% 이상인 차원으로 자동 적용
            # num_components를 int로 변환하기
            # print(f"num_components(type): {type(num_components)}")
            if num_components != None:
                num_components = int(num_components)

            pca_result = perform_pca(data, features, target_column, num_components)

            # plt 시각화를 html로 만들어주는 함수 호출
            '''title = {'main':'그래프 제목', 'x':'x축 제목', 'y':'y축 제목'}'''
            title = {'main': 'PCA가 적용된 그래프', 'x': 'PC1', 'y': 'PC2'}

            # 시각화 데이터 준비
            scatter_data = {
                'data': pca_result['X_pca'], 
                'name': f'{num_components}차원 데이터', 
                'mode': 'markers'
                }
            # principal_axes_data = {     
            #     'key': 'principal_axes',  # 메타정보
            #     'data': pca_result['principal_axes'],    # 시각화 함수 내부에서 name & mode 추가
            #     'name': '주성분 축',
            #     }

            pca_plotly = visualize_to_plotly(title, scatter_data)

            items = {'success':True, 'pca_result': pca_plotly}
            

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
            
            
        ''' 데이터파일저장 : save_ds_data
            데이터파일목록조회 : ds_data_list
            로데이터조회 : ds_rows_list
            데이터파일내용조회 : ds_data_info. prop_data 없으면 csv파일 읽기.
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

        '''
        if action == 'save_ds_data':
            dd_id = posparam.get('id')
            Name = posparam.get('Name')
            Description = posparam.get('Description')
            Type = posparam.get('Type')
            new_file_id = posparam.get('fileId')
            dd_id = CommonUtil.try_int(dd_id)
            
            #fileService = FileService()

            old_file_id = -1
            if dd_id:
                #rows = fileService.get_attach_file(self, 'ds_data', dd_id, attach_name='basic')
                #if len(rows) > 0: 
                #    old_file_id = row[0]['id']
                dd = DsData.objects.get(id=dd_id)
            else:
                dd = DsData()
            dd.Name = Name
            dd.Description = Description
            dd.Type = Type
            dd.save()
            dd_id = dd.id

            daService = DaService('ds_data', dd_id)
 
            if new_file_id:
                # fileService = FileService()
                fileService = AttachFileService()
                fileService.updateDataPk(new_file_id, dd_id)
                #if new_file_id != old_file_id:
                #    df = daService.read_csv2()

                #    row = fileService.get_attach_file_detail(self, file_id)
                #    #TableName = row.get('TableName')
                #    #AttachName = row.get('AttachName')
                #    PhysicFileName = row.get('PhysicFileName')
                #    #FileName = row.get('FileName')
                #    file_name = settings.FILE_UPLOAD_PATH + 'ds_data\\' + PhysicFileName

                #    df = pd.read_csv(file_name)
                #    row_count = df.shape[0]
                #    for column in df.columns:
                #        col_data = df[column]
                #        for i in range(row_count):
                #            pd = PropertyData()
                #            pd.TableName = 'ds_data'
                #            pd.DataPk = dd_id 
                #            pd.Type = str(i)
                #            pd.Code = column
                #            pd.Char1 = data[i]
                #            pd.Number1 = CommonUtil.try_float(col_data[i])
                #            pd.save()
 
            items = {'success': True}

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
	            from ds_data dd
	            where 1 = 1
            ), B as (
	            select 
                    A.id
	                , count(dc.*) as var_count
	                , count(case when dc."X" = 1 then 1 end) as x_count
	                , count(case when dc."Y" = 1 then 1 end) as y_count
	            from A 
	            inner join ds_col dc on dc."DsData_id" = A.id
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
            dd_id = gparam.get('dd_id')
            sql = ''' select dc.id, dc."VarIndex", dc."VarName"
            from ds_col dc
            where dc."DsData_id" = %(dd_id)s
            order by dc."VarIndex"  
            '''
            dc = {}
            dc['dd_id'] = dd_id

            xrows = DbUtil.get_rows(sql, dc)

            sql = ''' select dt."RowIndex" '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                sql += ''' 
                ,min(case when dt."Code" = \'''' + var_name + '''\' then dt."Char1" end) as x''' + str(i+1)
            sql += ''' from ds_data_table dt 
            where dt."DsData_id" = %(dd_id)s
            group by dt."RowIndex"
            order by dt."RowIndex"
            '''
            dc = {}
            dc['dd_id'] = dd_id

            rows = DbUtil.get_rows(sql, dc)
            items = {
                'success': True,
                'xrows': xrows,
                'rows': rows
            }

        elif action == 'ds_data_info':
            ''' 
            '''
            dd_id = gparam.get('dd_id')
            sql = ''' select dd.id, dd."Name", dd."Description"
            , dd."Type", dd._created
            , (select id as file_id from attach_file af 
		            where af."DataPk" = dd.id 
		            and af."TableName" = 'ds_data' order by id desc limit 1) as file_id
            from ds_data dd
            where dd.id = %(dd_id)s
            '''
            dc = {}
            dc['dd_id'] = dd_id
            row = DbUtil.get_row(sql, dc)

            return row
           

        elif action == 'make_db_from_file':
            ''' prop_data 없으면 csv파일 읽어서 prop_data에 저장하고 변수컬럼 저장.
            '''
            dd_id = gparam.get('dd_id')
            sql = ''' select dd.id, dd."Name", dd."Description"
            , dd."Type", dd._created
            , (select id as file_id from attach_file af 
		            where af."DataPk" = dd.id 
		            and af."TableName" = 'ds_data' order by id desc limit 1) as file_id
            from ds_data dd
            where dd.id = %(dd_id)s
            '''
            dc = {}
            dc['dd_id'] = dd_id
            row = DbUtil.get_row(sql, dc)

            file_id = row['file_id']
            if not file_id:
                return {'success':False, 'message':'파일없음' }

            daService = DaService('ds_data', dd_id)

            #q = DsDataTable.objects.filter(DsData_id=dd_id)
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
            dd_id = gparam.get('dd_id')
            sql = ''' select dc.id, dc."VarName" as value, dc."VarName" as text
            from ds_col dc
            where dc."DsData_id" = %(dd_id)s
            and dc."CategoryCount" > 0
            order by dc."VarIndex"  
            '''
            dc = {}
            dc['dd_id'] = dd_id

            items = DbUtil.get_rows(sql, dc)

            return items


        elif action == 'make_col_info':
            ''' table 데이터 읽어서 컬럼정보를 만들어서 저장한다.
            '''
            dd_id = gparam.get('dd_id')

            daService = DaService('ds_data', dd_id)
            df = daService.read_table_data()
            daService.make_col_info(df)

            return {'success':True, 'message':'' }

        elif action == 'ds_col_list':
            '''
            '''
            dd_id = gparam.get('dd_id')
            sql = ''' select dc.id, dc."VarIndex", dc."VarName"
            , dc."DataCount", dc."MissingCount", dc."CategoryCount" 
            , dc."Mean" 
            , dc."Std" , dc."Q1" , dc."Q2" , dc."Q3" 
            , dc."MissingValProcess" , dc."DropOutLow" , dc."DropOutUpper" , dc."X" ,dc."Y" 
            from ds_col dc
            where dc."DsData_id" = %(dd_id)s
            order by dc."VarIndex"  
            '''
            dc = {}
            dc['dd_id'] = dd_id

            items = DbUtil.get_rows(sql, dc)
         
        elif action == 'save_ds_col_preprocess':
            dd_id = posparam.get('dd_id')
            Q = posparam.get('Q')
            #Q = json.loads(Q)
            
            daService = DaService('ds_data', dd_id)
            df = daService.read_table_data()

            for item in Q:
                VarName = item['VarName']
                MissingValProcess = item['MissingValProcess']
                DropOutLow = CommonUtil.try_float(item['DropOutLow'])
                DropOutUpper = CommonUtil.try_float(item['DropOutUpper'])

                q = DsColumn.objects.filter(DsData_id=dd_id)
                q = q.filter(VarIndex=item['VarIndex'])
                dc = q.first()
                dc.MissingValProcess = MissingValProcess
                dc.DropOutLow = DropOutLow
                dc.DropOutUpper = DropOutUpper
                dc.save()

                #결측치 대체
                if MissingValProcess == 'drop':
                    #df[VarName].dropna(axis=1, inplace=True)
                    df[VarName].dropna(inplace=True)
                elif MissingValProcess == 'mean':
                    df[VarName].fillna(df[VarName].mean(), inplace=True)
                elif MissingValProcess == 'median':
                    df[VarName].fillna(df[VarName].median(), inplace=True)
                elif MissingValProcess == 'mode':
                    df[VarName].fillna(df[VarName].mode(), inplace=True)

                #이상치 제거
                if DropOutLow:
                    df = df[df[VarName <= DropOutLow]]
                if DropOutUpper:
                    df = df[df[VarName >= DropOutUpper]]
            ''' ds_data_table delete, update

            '''
            sql = ''' delete 
	        from ds_data_table
	        where "DsData_id"  = %(dd_id)s
	        and "RowIndex" in (
		        select distinct "RowIndex"
		        from ds_data_table dt
		        where "DsData_id" = %(dd_id)s
		        and "Code" in (
			        select "VarName" 
			        from ds_col dc
			        where "DsData_id" = %(dd_id)s
			        and "MissingValProcess" = 'drop'
		        )
		        and "Char1" is null
	        )
            '''
            dc = {}
            dc['dd_id'] = dd_id
            ret = DbUtil.execute(sql, dc)

            ''' with A as (
	            select dc."DsData_id" as dd_id, "VarName", case "MissingValProcess" when 'mean' then "Mean" when 'median' then "Q2" end new_val
	            from ds_col dc
	            where "DsData_id" = %(dd_id)s
	            and "MissingValProcess" in ('mean', 'median')
            )
            update ds_data_table 
            set "Char1" = A.new_val
            , "Number1" = A.new_val
            from A
            where ds_data_table."DsData_id" = A.dd_id 
            and ds_data_table."Code" = A."VarName"
            and ds_data_table."Char1" is null
            and A.new_val is not null 
            '''

            dc = {}
            dc['dd_id'] = dd_id
            ret = DbUtil.execute(sql, dc)

            daService.make_col_info(df)

            items = {'success': True, 'message':''}

        elif action == 'ds_numcol_boxhist':
            ''' 수치형 데이터에 대해서 히스토그램, 상자수염그림 그리기
            '''
            import matplotlib.pyplot as plt
            #from matplotlib.figure import Figure

            dd_id = gparam.get('dd_id')
            daService = DaService('ds_data', dd_id)
            df = daService.read_table_data()

            num_df = df.select_dtypes(include=['int64','float64'])

            #nrow = math.ceil( len(num_df.columns) / (ncol) )
            nrow = len(num_df.columns)
            
            fig, ax = plt.subplots(nrows=nrow, ncols=2, figsize=(20, 20))
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

            dd_id = gparam.get('dd_id')
            variables = gparam.get('variables')
            daService = DaService('ds_data', dd_id)
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

            dd_id = gparam.get('dd_id')
            daService = DaService('ds_data', dd_id)
            df = daService.read_table_data()

            #num_df = df.select_dtypes(include=['int64','float64'])

            corr_df = df.corr()
            # seaborn을 사용하여 heatmap 출력

            fig = plt.figure(figsize=(15,10))
            sns.heatmap(corr_df, annot=True, cmap='PuBu')
            #fig = Figure()
           
            chart_url = daService.plt_url(fig)
            #plt.show()

            return {'success':True, 'chart_url': chart_url}


        elif action == 'save_ds_col_xy':
            '''
            '''
            dd_id = posparam.get('dd_id')
            Q = posparam.get('Q')
            #Q = json.loads(Q)

            daService = DaService('ds_data', dd_id)
            df = daService.read_table_data()

            x_cols = []
            y_cols = []
            for item in Q:
                q = DsColumn.objects.filter(DsData_id=dd_id)
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
            q = DsVarCorrelation.objects.filter(DsData_id=dd_id)
            q.delete()

            for y in y_cols:
                multilinear.fit(df[x_cols], df[y])
                beta_0 = multilinear.intercept_
                beta_i_list = multilinear.coef_

                cr = DsVarCorrelation()
                cr.DsData_id = dd_id
                cr.YVarName = y
                cr.XVarName = 'intercept_'
                cr.MultiLinearCoef = beta_0
                cr.save()

                for i, x in enumerate(x_cols):
                    try:
                        corr =df[x].corr(df[y])
                    except Exception as e:
                        corr = None
                    cr = DsVarCorrelation()
                    cr.DsData_id = dd_id
                    cr.XVarName = x
                    cr.YVarName = y
                    cr.r = corr
                    cr.MultiLinearCoef = beta_i_list[i]
                    
                    #if corr and (corr > 0.5 or 1==1):  #0.5
                    if True:  #0.5
                        try:
                            simplelinear.fit(df[[x]], df[y])
                            beta_0 = simplelinear.intercept_
                            beta_1 = simplelinear.coef_ 

                            equ = 'y = ' + str(beta_1) + '*x +' + str(beta_0)
                            cr.RegressionEquation = equ
                        except Exception as e:
                            pass
                    cr.save()

        elif action == 'ds_col_scatter':
            '''
            '''
            import seaborn as sns

            dd_id = gparam.get('dd_id')
            daService = DaService('ds_data', dd_id)
            df = daService.read_table_data()

            #num_df = df.select_dtypes(include=['int64','float64'])
            x_vars, y_vars = daService.xy_columns()
            #x_vars = ['Age','Fare']
            #y_vars = ['Fare']
            
            #fig = Figure() # sns에서는 이 구문을 실행하지 않아야 새 창이 안 뜸.
            #ax = fig.subplots()

            if len(x_vars) > 0 and len(y_vars) > 0:
                pp = sns.pairplot(df, x_vars=x_vars, y_vars=y_vars, diag_kind='hist')
            else:
                pp = sns.pairplot(df, diag_kind='hist') # 그래프가 별도 창에 표시된다.

            scatter_url = daService.plt_url(pp)
            return {'success':True, 'scatter_url': scatter_url} 

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
            dd_id = gparam.get('dd_id')

            sql = ''' select dc.id, dc."VarIndex", dc."VarName"
            from ds_col dc
            where dc."DsData_id" = %(dd_id)s
            and dc."X" = 1
            order by dc."VarIndex"  
            '''
            dc = {}
            dc['dd_id'] = dd_id

            xrows = DbUtil.get_rows(sql, dc)

            sql = ''' select vc."YVarName", 1 as grp_idx, '상관계수' as data_type, null::numeric as intercept_ '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                sql += ''' 
                ,min(case when vc."XVarName" = \'''' + var_name + '''\' then vc.r end)::text as x''' + str(i+1)
            sql += ''' from ds_var_corr vc 
            where vc."DsData_id" = %(dd_id)s
            group by vc."YVarName" 
            union all
            select vc."YVarName", 2 as grp_idx, '단일회귀식' as data_type
            , null::numeric as intercept_ '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                sql += ''' 
                ,min(case when vc."XVarName" = \'''' + var_name + '''\' then vc."RegressionEquation" end) as x''' + str(i+1)
            sql += ''' from ds_var_corr vc 
            where vc."DsData_id" = %(dd_id)s
            group by vc."YVarName" 
            union all
            select vc."YVarName", 3 as grp_idx, '다중회귀식계수' as data_type
            , min(case when vc."XVarName" = 'intercept_' then vc."MultiLinearCoef" end) as intercept_ '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                sql += ''' 
                ,min(case when vc."XVarName" = \'''' + var_name + '''\' then vc."MultiLinearCoef" end)::text as x''' + str(i+1)
            sql += ''' from ds_var_corr vc 
            where vc."DsData_id" = %(dd_id)s
            group by vc."YVarName" 
            order by 1, 2
            '''
            dc = {}
            dc['dd_id'] = dd_id
            rows = DbUtil.get_rows(sql, dc)
            
            items = {
                'success': True,
                'xrows': xrows,
                'rows': rows
            }

        elif action == 'ds_y_regression_list':

            dd_id = gparam.get('dd_id')

            sql = ''' select dc.id, dc."VarIndex", dc."VarName"
            from ds_col dc
            where dc."DsData_id" = %(dd_id)s
            and dc."X" = 1
            order by dc."VarIndex"  
            '''
            dc = {}
            dc['dd_id'] = dd_id

            xrows = DbUtil.get_rows(sql, dc)

            sql = ''' select vc."YVarName" '''
            for i, x in enumerate(xrows):
                var_name = x['VarName']
                sql += ''' 
                ,min(case when vc."XVarName" = \'''' + var_name + '''\' then vc."RegressionEquation" end) as re''' + str(i)
            sql += ''' from ds_var_corr vc 
            where vc."DsData_id" = %(dd_id)s
            group by vc."YVarName" 
            '''
            dc = {}
            dc['dd_id'] = dd_id
            rows = DbUtil.get_rows(sql, dc)    
            
            items = rows
        
    except Exception as ex:
        source = 'learning_data : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        # 24.07.16 김하늘 에러 로그 확인
        print('error: ', ex)
        raise ex
    
    return items
