from domain.services.logging import LogWriter


class BoxPlot(object):
    @classmethod
    def boxplot_factor(cls, option, data_list):
        """ option 1, 전체 min(q0), max(q5) return:
            opition 2 :  iqr 구해서 1.5*iqr 내의 min, max return
        """
        try:
            n = len(data_list)

            data = sorted(data_list)

            n1 = (n+1) / 4
            n2 = (n+1) / 4*2
            n3 = (n+1) /4*3
            ns = [ n1, n2, n3 ]
            q = [ None, None, None, None, None ]
            j = 1

            for index, n in enumerate(ns):
                f = n % 1
                d = int(n - f)
                if f > 0:
                    q[index+1] = data[d-1] + ( data[d] - data[d-1]) * f * (index+1) 
                else:
                    q[index+1] = data[d]

            if option == '1': 
                min = data[0]
                max = data[n-1] 

                box_data = [ min, q[1], q[2], q[3], max ]
                outlier = []

            elif option == '2':

                iqr = q[3] - q[1]
                iqr1_5 = iqr * 1.5
                min = q[1] - iqr1_5
                max = q[3] + iqr1_5
                lowerWhisker = max
                upperWhisker = min            

                for value in data:
                    if value > min and value < q[1] and value < lowerWhisker:
                        lowerWhisker = value
                    if value > q[3] and value < max and value > upperWhisker:
                        upperWhisker = value
                box_data = [ lowerWhisker, q[1], q[2], q[3], upperWhisker ]
                outlier =  [ x for x in data if x < min or x > max ]

            return {
                'box_data': box_data,
                'outlier': outlier,
            }
        except Exception as ex:
            LogWriter.add_dblog('error', 'BoxPlot.boxplot_factor', ex)
            raise ex