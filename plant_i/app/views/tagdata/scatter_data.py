import numpy as np

from configurations import settings
from domain.models.mes import TagMaster
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.services.system_definition.tag_data import TagDataService
from domain.services.calculation.box_plot import BoxPlot
from domain.services.calculation.regression import RegressionCalc
from domain.services.calculation.histogram import HistogramCalc



def scatter_data(context):
    '''산점도 데이터
    '''
    items = []
    gparam = context.gparam
    posparam = context.posparam

    action = gparam.get('action')
    
    try:
        if action =='read':
            start_date = gparam.get('start_date', '')
            end_date = gparam.get('end_date', '')
            tag_codes = gparam.get('tag_codes', '')
            equ_order = gparam.get('equ_order', 1) # 회귀분석 차수
            
            tag_service = TagDataService()
            rows = tag_service.tag_multi_data_list_couple(start_date, end_date, tag_codes)

            tag_code_arr = tag_codes.split(';')

            tag_arr = []
            for tag_code in tag_code_arr:
                tag = TagMaster.objects.filter(tag_code=tag_code).first()
                if tag:
                    tag_arr.append(
                        {
                            'name':tag.tag_name,
                            'code':tag.tag_code,
                            'round_digit':tag.RoundDigit
                        }
                    )

            tag_code_couple = []
            scatter_data = {}

            #for i in range(len(tag_arr)):
            for tag1 in tag_arr:
                #for j in range(len(tag_arr)):
                for tag2 in tag_arr:
                    couple_code = tag1['code']+'_'+tag2['code']
                    tag_code_couple.append(
                        {
                            'x': tag1['code'],
                            'y': tag2['code'],
                            'round_x': tag1['round_digit'],
                            'round_y': tag2['round_digit'],
                            'name_x': tag1['name'],
                            'name_y': tag2['name'],
                            #'couple_name' : tag1['name']+'-'+ tag2['name'],
                            'couple_code' : couple_code,
                        }
                    )
                    scatter_data[couple_code] = []

            for row in rows:
                #scatter_data[row['couple_code']].append([row['x_val'], row['y_val']])
                scatter_data[row['couple_code']].append({'x':row['x_val'], 'y':row['y_val']})

            for value in tag_code_couple:
                xy_datas = scatter_data.get(value['couple_code'])
                round_x = value['round_x']
                round_y = value['round_y']
                min_data = 999999
                max_data = -999999
                x_list = []
                y_list = []
                line_data = []

                for row in xy_datas:
                    x = row['x']
                    x_list.append(x)
                    y_list.append(row['y'])
                    if x < min_data:
                        min_data = x
                    if x > max_data:
                        max_data = x

                if min_data == 999999:
                    min_data = 0
                    max_data = 100
                elif min_data == max_data:
                    min_data = min_data - abs(min_data) * 0.1
                    max_data = max_data + abs(min_data) * 0.1

                r2 = 1
                slope = None
                intercept = None
                p = 0
                first_equation = ''

                if xy_datas:
                    fit = RegressionCalc.scipy_regression(x_list, y_list)
                    r2 = fit.rvalue ** 2
                    slope = fit.slope
                    intercept = fit.intercept
                    p = fit.pvalue  # p < 0.05

                    #fit2 = RegressionCalc.statsmodels_regression(x_list, y_list)
                    #r2 = fit2.rsquared  #fit2.rsquared_adj
                    #slope = fit2.params[1]
                    #intercept = fit2.params[0]
                    #p = fit2.f_pvalue   # fit2.pvalues[1] 

                    if equ_order > 1:
                        pass

                    r2 = round(r2,3)
                    p = round(p,4)
                    
                    first_equation = 'y = ' + str(round(slope,4)) + 'x + ' + str(round(intercept,round_y+2))
 
                    if r2 > 0.5 and p <= 0.05 or 1 == 1:
                        
                        gap = (max_data - min_data) / 20

                        x = min_data 
                        for index in range(1, 20):
                            y = slope * x + intercept
                            #y = round(y, round_y + 2)

                            line_point = {
                                'x':x,
                                'y':y
                            }
                            x = round(min_data + gap * index, round_x + 2)
                            line_data.append(line_point)
                
                data = {
                    'x': value['x'],
                    'y': value['y'],
                    #'name' : value['couple_name'],
                    #'code' : value['couple_code'],
                    'name_x' : value['name_x'],
                    'name_y' : value['name_y'],
                    'round_x' : value['round_x'],
                    'round_y' : value['round_y'],
                    'min_x' :  min_data,
                    'max_x' :  max_data,
                    'r2' :  r2,
                    'p' :  p,
                    'slope' :  slope,
                    'intercept' :  intercept,
                    'first_equation' : first_equation,
                    'scatter_data' :  xy_datas,
                    'line_data' :  line_data,
                }
                items.append(data)


    except Exception as ex:
        source = '/api/tagdata/scatter_data'
        LogWriter.add_dblog('error', source, ex)
        raise ex

    return items