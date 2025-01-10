import numpy as np

from configurations import settings
from domain.models.definition import TagMaster
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.services.system_definition.tag_data import TagDataService
from domain.services.calculation.box_plot import BoxPlot
from domain.services.calculation.regression import RegressionCalc
from domain.services.calculation.histogram import HistogramCalc





def boxplot_data(context):
    """ Q1,Q2,Q3,lowerWhisker,upperWhisker
        outlier
    """
    tag_service = TagDataService()
    items = {}
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action')
    
    try:
        if  action =='read':

            start_date = gparam.get('start_time', '')
            end_date = gparam.get('end_time', '')
            tag_codes = gparam.get('tag_codes', '')
            option = gparam.get('option') # 1, 2 

            items = tag_service.tag_multi_data_list2(start_date, end_date, tag_codes)

            result = []
            tag_data = {}
            for tag_code, value in items.items():
                data_name = value['tag_name']
                rows = value['data']
                data = [ row['data_value'] for row in rows ]
                #data.sort()

                ret = BoxPlot.boxplot_factor(option, data)

                box_data = ret['box_data']
                outlier = ret['outlier']
                dc = {
                    'data_name': value['tag_name'],
                    'box_data': box_data,
                    'outlier': outlier,
                }
                result.append(dc)
        
            return result

            data = [1, 2, 3.3, 5.1, 6.3, 2.1, 1.4, 4.3, 10]

            items = BoxPlot.boxplot_factor(option, data)
            
            result = [
                {
                    'data_name': 'abc',
                    'box_data': [1.1, 2.1, 3.5, 4, 7.8],
                    'outlier':[9.0, 10.1],
                },
                {
                    'data_name': 'xxx',
                    'box_data': [1.1, 2.1, 3.5, 4, 7.8],
                    'outlier':[],
                },
                {
                    'data_name': 'zzz',
                    'box_data': [1.1, 2.1, 3.5, 4, 7.8],
                    'outlier':[],
                },
            ]
            return items

    except Exception as ex:
        source = '/api/tagdata/boxplot_data'
        LogWriter.add_dblog('error', source, ex)
        raise ex

    return items


