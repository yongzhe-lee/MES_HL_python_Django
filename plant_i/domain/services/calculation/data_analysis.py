import math
import numpy as np
import uuid
import pandas as pd
from io import BytesIO

from configurations import settings

from domain.models.system import AttachFile
from domain.models.da import DsData, DsColumn, DsDataTable
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

class DaService(object):
    """ 데이터분석 모듈.
    from domain.services.calculation.data_analysis import DaService
    
    dd = DaService()
    dd.load_data(rows)
    dd.show_box_and hist plot(colum_list)
    dd.show_scatter(x_column_list, y_column_list)
    dd.calc_regression(x_column_list, y_column)
        

    """
    def __init__(self, table_name, data_pk):
        self.table_name = table_name
        self.data_pk = data_pk

    def set_data_pk(self, table_name, data_pk):
        self.table_name = table_name
        self.data_pk = data_pk

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

    def read_csv(self, file_name):
        df = pd.read_csv(file_name)
        row_count = df.shape[0]
        for column in df.columns:
            col_data = df[column]
            for i in range(row_count):
                data = col_data[i]
                dt = DsDataTable()
                dt.DsData_id = self.data_pk
                dt.Type = str(i)
                dt.Code = column
                if data != 'nan':
                    dt.Char1 = data
                    dt.Number1 = CommonUtil.try_float(data)
                dt.save()
        return df


    def read_csv2(self):
        ''' 첨부된 csv 파일 읽고 DsDataTable에 저장. df 리턴
        '''
        dd_id = self.data_pk

        sql = ''' select id
        , "TableName"
        , "DataPk"
        , "AttachName"
        , "FileIndex"
        , "FileName"
        , "PhysicFileName"
        , "ExtName"
        , "FilePath"
        , "_created"
        , "FileSize"
        from attach_file 
        where "TableName" = %(table_name)s
        and "DataPk" = %(data_pk)s
        order by id desc 
        '''
        dc = {}
        dc['table_name'] = self.table_name
        dc['data_pk'] = dd_id
        row = DbUtil.get_row(sql, dc)
        if not row:
            return

        PhysicFileName = row.get('PhysicFileName')
        #FileName = row.get('FileName')
        file_name = settings.FILE_UPLOAD_PATH + 'ds_data\\' + PhysicFileName
        df = pd.read_csv(file_name)
        #dcData = df.to_dict()

        #dd = DsData.objects.get(id=dd_id)
        #dd.DcData = dcData
        #dd.save()

        #return df

        #q = DsDataTable.objects.filter(DsData_id=dd_id)
        #q.delete()

        row_count = df.shape[0]
        for column in df.columns:
            sql = ''' select 1 from ds_col where "DsData_id" = 4
            and "VarName" = %(code)s
            '''
            dc = {}
            dc['code'] = column
            row = DbUtil.get_row(sql, dc)
            if row:
                continue

            col_data = df[column]
            for i in range(row_count):
                data = col_data[i]
                dt = DsDataTable()
                dt.DsData_id = dd_id
                dt.RowIndex = i
                dt.Code = column
                dt.Char1 = data
                dt.Number1 = CommonUtil.try_float(data)
                dt.save()
        return df

    def read_table_data(self):
        ''' table에서 데이터 읽어서 df를 만들어 준다.
        '''
        #dd = DsData.objects.get(id=self.data_pk)
        #dcData = dd.DcData
        #df = None
        #if dcData:
        #    df = pd.DataFrame(dcData)
        #return df

        sql = ''' select "RowIndex", "Code", "Number1", "Char1"
        , count(*) over (partition by "RowIndex") as g_cnt
        , row_number() over (partition by "RowIndex" order by id) as g_idx
        from ds_data_table
        where "DsData_id" = %(data_pk)s
        order by "RowIndex"
        '''
        dc = {}
        dc['table_name'] = self.table_name
        dc['data_pk'] = self.data_pk
        rows = DbUtil.get_rows(sql, dc)
        old_index = 0
        new_rows = []
        new_row = {}
        for row in rows:
            index = row['RowIndex']
            g_idx = row['g_idx']
            if g_idx == 1:
                new_row = {}
            if row['Number1']:
                new_row[row['Code']] = row['Number1']
            else:
                new_row[row['Code']] = row['Char1']
            if g_idx == row['g_cnt']:
                new_rows.append(new_row)
        df = pd.DataFrame(new_rows)
        for col_name in df.columns:
            try:
                if str(df[col_name].dtype) == 'object':
                    df[col_name] = df[col_name].astype('float64')
            except Exception as e:
                pass
        return df

    def make_col_info(self, df):
        dd_id = self.data_pk
        row_count = df.shape[0]

        q = DsColumn.objects.filter(DsData_id=dd_id)
        q.delete()

        try:
            dtypes = df.dtypes
            for index, key in enumerate(df.columns):
                col = df[key]
                MissingCount = row_count - col.count()

                dc = DsColumn()
                dc.DsData_id = dd_id
                dc.VarIndex = index
                dc.VarName = key
                dc.DataCount = row_count
                dc.MissingCount = MissingCount
                min, max, median, std = None, None, None, None
                Q1, Q2, Q3 = None, None, None

                dtype = str(dtypes[key])

                if dtype in ['int64', 'float64']:
                    try:
                        max = col.max()
                    except:
                        max = None
                    try:
                        min = col.min()
                    except:
                        min = None
                    try:
                        median = col.median()
                    except:
                        median = None
                    try:
                        mean = col.mean()
                    except:
                        mean = None
                    try:
                        std = col.std()
                    except:
                        std = None
                    #skew = col.skew()
                    #mad = col.mad()
                    try:
                        Q1 = col.quantile(0.25)
                    except:
                        Q1 = None
                    try:
                        Q3 = col.quantile(0.75)
                    except:
                        Q3 = None
                    dc.Mean = CommonUtil.try_float( mean )
                    dc.Std = CommonUtil.try_float(std)
                    dc.Q1 = CommonUtil.try_float(Q1)
                    dc.Q2 = CommonUtil.try_float(median)
                    dc.Q3 = CommonUtil.try_float(Q3)
                else:
                    distinct_count = len(col.value_counts())
                    dc.CategoryCount = distinct_count
                dc.save()
        except Exception as ex:
            print (ex)
        return True

    def xy_columns(self):
        '''
        '''
        sql = ''' 	select "VarName", "X", "Y"
	    from ds_col 
	    where "DsData_id" = %(dd_id)s
	    and 1 in ("X", "Y")
	    order by "VarIndex"
        '''
        dc = {}
        dc['dd_id'] = self.data_pk
        rows = DbUtil.get_rows(sql, dc)

        x_vars = []
        y_vars = []
        for row in rows:
            if row['X'] == 1:
                x_vars.append(row['VarName'])
            elif row['Y'] == 1:
                y_vars.append(row['VarName'])
        return x_vars, y_vars

    def load_data(self, rows):
        '''
        '''
        df = pd.DataFrame(rows)
        return df


    def calc_corr(self, df):
        ''' 상관관계 계산
        '''
        corr_df = df.corr()
        return corr_df

    def sns_heatmat(self, df):
        import matplotlib.pyplot as plt
        import seaborn as sns
        #from matplotlib.figure import Figure

        corr_df = df.corr()
        # seaborn을 사용하여 heatmap 출력

        fig = plt.figure(figsize=(15,10))
        sns.heatmap(corr_df, annot=True, cmap='PuBu')
        #fig = Figure()
        hm_plt = self.plt_url(fig)
        #plt.savefig("plot.png")

        ## Generate the figure **without using pyplot**.
        #fig = Figure()
        #ax = fig.subplots()
        #ax.heatmap(corr_df, annot=True, cmap='PuBu')
        #hm_plt = self.plt_url(fig)
      
    def aaa(self, df):
        cate=[]
        cont=[]
        for i in df.columns:
            if df[i].dtype=='O':
                cate.append(i)
            else:
                cont.append(i)

        for cont_var_name in cont: 
            # hint. plt.boxplot()을 이용합니다. 
            plt.boxplot(data[cont_var_name])
            plt.title(cont_var_name)
            plt.show()

    def sns_pair_plot(self, df, x_vars=None, y_vars=None, hue_column=None):
        ''' 모든 데이터의 상관관계를 시각화
        '''
        import seaborn as sns

        if x_vars and y_vars:
            if hue_column:
                sns.pair_plot(df, x_vars=x_vars, y_vars=yx_vars, hue=hue_column)
            else:
                sns.pair_plot(df)

        if hue_column:
            sns.pair_plot(df, hue=hue_column)
        else:
            sns.pair_plot(df)
     
    def sns_count_plot(self, df, hue_column=None):
        ''' 범주형 데이터에 대해 히스토그램을 그려본다.
        '''
        import seaborn as sns

        cate=[]
        for i in df.columns:
            if df[i].dtype=='O':
                cate.append(i)

        for i in cate: #범주형 데이터에 대한 변수명 리스트입니다.
            # Hint. sns.countplot을 이용합니다. hue 옵션을 사용합니다.
            sns.countplot(x=i, data=data, hue=hue_column)
            plt.xticks(rotation=45)
            plt.show()

    def outliers(self, data,x):
        ''' 연속형 데이터별 이상치 후보군의 비율을 출력
        '''
        down=data[x].quantile(q=0.25)
        up=data[x].quantile(q=0.75)
        iqr=up-down
        return [x,round(len(data[(data[x]>up+1.5*iqr)|(data[x]<down-1.5*iqr)])/len(data),2)]


    def outliers_check(self, data,x):
        ''' 연속형 데이터의 이상치 여부를 체크
        '''
        down=data[x].quantile(q=0.25)
        up=data[x].quantile(q=0.75)
        iqr=up-down
        return data[(data[x]>up+1.5*iqr)|(data[x]<down-1.5*iqr)].reset_index(drop=True)

    
    def save_model_joblib(self, model, file_name):
        ''' 모델을 파일로 저장.
        '''
        import joblib
        joblib.dump(model, file_name)
        return True

    def load_model_joblib(self, file_name):
        ''' 모델을 파일에서 load. 모델 리턴
        '''
        import joblib
        model = joblib.load(file_name)
        return model

    
    def save_model_pickle(self, model, file_name):
        ''' 모델을 파일로 저장
        '''
        import pickle
        with open(file_name, 'wb') as f:
            pickle.dump(model, f)

        return True

    def load_model_pickle(self, file_name):
        ''' 모델을 파일에서 load. 모델 리턴
        '''
        import pickle
        model = None
        with open(file_name, 'rb') as f:
            model = pickle.load(f)
        return model