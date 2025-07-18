import numpy
import json

from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from configurations import settings
from domain.services.calculation.regression import CurveFit


def regression_a(context):
    '''
    /api/tagdata/regression_a
    '''
    items=[]
    posparam = context.posparam
    gparam = context.gparam
    action = gparam.get('action')

    try:
        fit = CurveFit()
        a = float(gparam.get('a', '1'))
        b = float(gparam.get('b', '1'))
        c = float(gparam.get('c', '1'))
        equ_order = int(gparam.get('equ_order', ''))
        decimal_digit = gparam.get('decimal_digit', '')
        y_list = gparam.get('y_list[]', [])
        x_list = gparam.get('x_list[]', [])
        type = gparam.get('type', '')
        data_len = int(gparam.get('data_len', ''))

        for i, (x, y) in enumerate(zip(x_list , y_list)) :
            x_list[i] = float(x)
            y_list[i] = float(y)

        fit.set_data(data_len, x_list, y_list)

        if action == 'changeY2':

            if type == 'log' : 
                fit.calc_scatter_regression(x_list, y_list, equ_order, 'log',a, b)
            elif type == 'power' : 
                fit.calc_scatter_regression(x_list, y_list, equ_order, 'power', a, b, c)
            elif type == 'none' :
                fit.calc_scatter_regression(x_list, y_list, equ_order, '')

            y2= fit.y_list
            y2.pop(0)

            scatter_list = []
            for i, (x, y) in enumerate(zip(x_list , y2)) :   
                if decimal_digit =='':
                    scatter_list.append({'x':x, 'y':y})
                else :
                    y = round(y,int(decimal_digit))
                    y2[i] = y
                    scatter_list.append({'x':x, 'y':y})
            items = [y2, scatter_list]

        elif action == 'calc_regre': #calc_regre

            if type == 'log' : 
                fit.calc_scatter_regression(x_list, y_list, equ_order, 'log', a, b)
            if type == 'power' : 
                fit.calc_scatter_regression(x_list, y_list, equ_order, 'power', a, b, c)
            elif type == 'none' : 
                fit.calc_scatter_regression(x_list, y_list, equ_order, '')            
            y2= fit.y_list
            y2.pop(0)
            equation = fit.equation
            r2 = fit.r2 
            scatter_list = []
            line_list =[]
            new_x_list = sorted(x_list)
            calc_equ = compile(equation, '<string>', 'single')
            for x in numpy.arange(new_x_list[0],new_x_list[-1]+1,0.01):

                if fit.equ_order == 1:
                    parm = {'x': x, 'y': 0}
                elif fit.equ_order == 2:
                    parm = {'x': x,'x2':x**2, 'y': 0}
                elif fit.equ_order == 3:
                    parm = {'x': x,'x2': x**2,'x3': x**3, 'y': 0}
                elif fit.equ_order == 4:
                    parm = {'x': x,'x2': x**2,'x3':x**3,'x4':x**4, 'y': 0}

                exec(calc_equ, parm)
                y = parm['y']

                line_list.append({'x':x, 'y':y})

            for i, (x, y) in enumerate(zip(x_list , y2)) :
                if decimal_digit =='' :
                    scatter_list.append({'x':x, 'y':y})
                else :
                    y = round(y,int(decimal_digit))
                    y2[i] = y
                    scatter_list.append({'x':x, 'y':y})
                    r2 = round(r2,int(decimal_digit))
            
            items = [y2, scatter_list, line_list, equation, r2]


    except Exception as ex:
        source = '/api/tagdata/regression_a : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        items = {'success':False}

    return items
