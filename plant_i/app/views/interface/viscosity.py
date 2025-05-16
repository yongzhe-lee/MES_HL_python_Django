
from tkinter import E


def viscosity(context):

    gparam = context.gparam
    posparam = context.posparam

    action = gparam.get('action', None)
    result = {'success' : False}
    try:
        if action == 'viscosity':

            data_year = gparam.get('data_year', None)
            data_month = gparam.get('data_month', None)
            line_id = gparam.get('line_id', None)






        else:
            raise ValueError("Invalid action")

    except Exception as e:
        context.error = str(e)

    return result