import numpy as np

from configurations import settings
from domain.models.mes import TagMaster
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.services.system_definition.tag_data import TagDataService
from domain.services.calculation.box_plot import BoxPlot
from domain.services.calculation.regression import RegressionCalc
from domain.services.calculation.histogram import HistogramCalc





def histogram_data(context):

    items = []
    gparam = context.gparam
    posparam = context.posparam

    action = gparam.get('action')
    
    try:
        if action =='read':
            start_date = gparam.get('start_date', '')
            end_date = gparam.get('end_date', '')
            tag_codes = gparam.get('tag_codes', '')

            tag_service = TagDataService()
            
            rows = tag_service.tag_multi_data_list2(start_date, end_date, tag_codes)
            result = []
            tag_data = {}
            #items = {}
            items = []
            for tag_code, row in rows.items():
                data_list = row.get('data')
                if not data_list:
                    continue
                data = [ item['data_value'] for item in data_list ]

                hist_data, hist_mean, hist_sigma, area = HistogramCalc.np_histogram(data, 10)

                data = {
                    'data_name':row['tag_name'],
                    'lsl':row['lsl'],
                    'usl':row['usl'],
                    'histogram_data':hist_data
                }
                items.append(data)

                #hist, bin_edge = np.histogram(data, 10)

                #foo = []
                #for index, item in enumerate(hist):
                #    x1 = bin_edge[index]
                #    x2 = bin_edge[index+1]
                #    dc = {}
                #    dc['count'] = int(item )
                #    dc['x1'] = x1
                #    dc['x2'] = x2
                #    dc['x'] = ( x1 + x2 ) / 2
                #    x1 = round(x1, 5)
                #    x2 = round(x2, 5)
                #    dc['label'] = str(x1) + ' ~ ' + str(x2)
                #    foo.append(dc)
                #data = {
                #    'data_name':row['tag_name'],
                #    'lsl':row['lsl'],
                #    'usl':row['usl'],
                #    'histogram_data':foo
                #}
                ##items[tag_code] = data
                #items.append(data)

    except Exception as ex:
        source = '/api/tagdata/histogram_data'
        LogWriter.add_dblog('error', source, ex)
        raise ex

    return items


