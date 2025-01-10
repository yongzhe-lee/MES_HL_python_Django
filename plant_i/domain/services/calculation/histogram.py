import math
import numpy as np

class HistogramCalc(object):
    """ 히스토그램 계산 모듈.
    from domain.services.calculation.histogram import HistogramCalc
    data = [5.30, 5.52, 5.12, 5.29, 5.41, 5.27, 5.76, 5.55, 5.39, 5.52, 5.47, 5.45, 
        5.24, 5.35, 5.59, 5.40, 5.26, 5.48, 5.37, 5.54, 5.69, 5.58, 5.32, 
        5.25, 5.22, 5.33, 5.11, 5.42, 5.47, 5.54, 5.34, 5.40, 5.41, 5.56, 5.64, 5.36, 
        5.71, 5.39, 5.49, 5.41, 5.44, 5.62, 5.17, 5.35, 5.48, 5.51, 5.66, 5.46, 5.73, 5.42 ]
    hist_data, hist_mean, hist_sigma, area = HistogramCalc.np_histogram(data, 10)

    pdf_x, pdf_y = HistogramCalc.hist_norm_dist(hist_mean, hist_sigma, 100, area)

    """

    @classmethod
    def np_histogram(cls, data, class_count):
        """
            
        """
        hist, bin_edge = np.histogram(data, class_count)
        foo = []
        sum = 0.0
        count_sum = 0
        for index, item in enumerate(hist):
            x1 = bin_edge[index]
            x2 = bin_edge[index+1]
            dc = {}
            count = int(item)
            count_sum += count
            dc['count'] = count
            dc['x1'] = x1
            dc['x2'] = x2
            x = ( x1 + x2 ) / 2
            sum += x * count
            dc['x'] = x
            x1 = round(x1, 5)
            x2 = round(x2, 5)
            dc['label'] = str(x1) + ' ~ ' + str(x2)
            foo.append(dc)
            
        hist_data = foo
        gap = (bin_edge[len(bin_edge) -1] - bin_edge[0]) / len(hist)
        area = gap * count_sum

        hist_mean = sum / count_sum
        r2_sum = 0
        for item in foo:
            r2_sum += math.pow(hist_mean - item['x'], 2) * item['count']
        #hist_s2 = r2_sum / count_sum
        hist_s2 = r2_sum / ( count_sum - 1 )
        hist_sigma = math.sqrt( hist_s2 )

        return hist_data, hist_mean, hist_sigma, area


    @classmethod
    def hist_norm_dist(cls, m, s, count, area = 1):
        '''
        from domain.services.calculation.histogram import HistogramCalc
        x, y = HistogramCalc.norm_dist(0, 1, 100)
        x, y = HistogramCalc.norm_dist(5.436, 0.151, 100)
        '''
        from scipy.stats import norm
        x = np.linspace(m - 3.0 * s, m + 3.0 * s, count)
        y = norm.pdf(x, m, s)
        y = y * area

        return x, y