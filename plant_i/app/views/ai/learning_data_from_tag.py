import math
import numpy as np
import pandas as pd
import json

from configurations import settings
from domain.services.logging import LogWriter
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.ai.data_processing import DataProcessingService

def learning_data_from_tag(context):
    '''
    작성명 : 데이터분석 회귀
    작성자 : 김태영
    작성일 : 2023-08-17
    비고 :

    -수정사항-
    수정일             작업자     수정내용
    2024-01-08         이인호     학습데이터 조회방식 일부수정
    '''
    items=[]
    posparam = context.posparam
    gparam = context.gparam
    action = gparam.get('action', 'read')
    data_svc = DataProcessingService()

    try:
        if action == 'read_tag_data':
            tag_codes = gparam.get('tag_codes')
            tag_list = tag_codes.split(',')
            items = data_svc.get_data_from_tag(tag_list)
            
        elif action == 'tag_list':
            equ_id = gparam.get('equ_id')
            keyword = gparam.get('keyword')
            
            sql = '''
            select 
            t.tag_code 
            ,t.tag_name 
            ,t."Equipment_id" as equ_id
            ,t."LastValue" as last_value
            ,t."LastDate" as last_date
            from tag t 
            where 1=1 
            '''
            if equ_id:
                sql+='''
                and t."Equipment_id" = %(equ_id)s 
                '''
            if keyword:
                sql+='''
                and t.tag_name ilike concat('%%',%(keyword)s,'%%') 
                '''
            sql +='''
            order by t.tag_name
            '''
            
            dc = {'equ_id':equ_id, 'keyword':keyword}
            items = DbUtil.get_rows(sql,dc)
            
        #변수통계값
        elif action == 'get_statistical_value':
            tag_codes = gparam.get('tag_codes')
            tag_list = tag_codes.split(',')
            data = data_svc.get_data_from_tag(tag_list)
            df = pd.DataFrame.from_dict(data)
            
            # 요약 통계를 담을 빈 데이터프레임 생성
            summary = pd.DataFrame(columns=['index', 'val_name', 'data_cnt', 'missing_cnt', 'category_cnt', 'average', 'standard_deviation', 'q1', 'q2', 'q3'])

            # 각 컬럼에 대해 요약 통계 계산
            for column in df.columns:
                summary = summary.append({
                    'index': df.columns.get_loc(column),
                    'val_name': column,
                    'data_cnt': df[column].count(),
                    'missing_cnt': df[column].isna().sum(),
                    'category_cnt': df[column].nunique(),
                    'average': df[column].mean() if df[column].dtype in ['float64', 'int64'] else None,
                    'standard_deviation': df[column].std() if df[column].dtype in ['float64', 'int64'] else None,
                    'q1': df[column].quantile(0.25) if df[column].dtype in ['float64', 'int64'] else None,
                    'q2': df[column].quantile(0.50) if df[column].dtype in ['float64', 'int64'] else None,
                    'q3': df[column].quantile(0.75) if df[column].dtype in ['float64', 'int64'] else None
                }, ignore_index=True)
                
            #데이터프레임 -> dict array로 변환
            #items = summary.to_dict('records')
            items = summary.to_json(orient='records', force_ascii=False)
         
        #
        elif action == 'get_numcol_boxhist':
            tag_codes = gparam.get('tag_codes')
            tag_list = tag_codes.split(',')
            data = data_svc.get_data_from_tag(tag_list)
            df = pd.DataFrame.from_dict(data)

            num_df = df.select_dtypes(include=['int64','float64'])

            nrow = len(num_df.columns)
            
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(nrows=nrow, ncols=2, figsize=(20, 20))

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
            
            chart_url = data_svc.plt_url(fig)
            
            items = {'success':True, 'chart_url':chart_url}
        
        #상관관계 히트맵
        elif action == 'get_heatmap':
            import matplotlib.pyplot as plt
            import seaborn as sns
            #from matplotlib.figure import Figure

            tag_codes = gparam.get('tag_codes')
            tag_list = tag_codes.split(',')
            data = data_svc.get_data_from_tag(tag_list)
            df = pd.DataFrame.from_dict(data)

            #num_df = df.select_dtypes(include=['int64','float64'])

            corr_df = df.corr()
            # seaborn을 사용하여 heatmap 출력

            fig = plt.figure(figsize=(15,10))
            sns.heatmap(corr_df, annot=True, cmap='PuBu')
            #fig = Figure()
           
            chart_url = data_svc.plt_url(fig)
            #plt.show()

            return {'success':True, 'chart_url': chart_url}

    except Exception as ex:
        source = 'learning_data_from_tag : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex

    return items

