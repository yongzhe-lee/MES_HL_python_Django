import math

class RegressionCalc(object):
    """ 1차 회귀분석 계산 모듈.
    """
    @classmethod
    def scipy_regression(cls, x_list, y_list):
        """
            from domain.services.calculation.regression import RegressionCalc
            y_list = [90,60,73,65,51,93,88,92,86,78,80,72,74,68,76]
            x_list = [58,65,63,64,68,57,59,56,60,62,61,63,64,64,61]
            result = RegressionCalc.scipy_regression(x_list, y_list)
        """
        from scipy import stats
        result =  stats.linregress(x_list, y_list)
        #slope, intercept, r, p, se = stats.linregress(x, y)
        return result


    @classmethod
    def statsmodels_regression(cls, x_list, y_list):
        """ 
            from domain.services.calculation.regression import RegressionCalc
            y_list = [90,60,73,65,51,93,88,92,86,78,80,72,74,68,76]
            x_list = [58,65,63,64,68,57,59,56,60,62,61,63,64,64,61]
            result = RegressionCalc.statsmodels_regression(x_list, y_list)
        """
        import numpy as np
        import statsmodels.api as sm
        x = sm.add_constant(x_list) 
        result = sm.OLS(endog=y_list, exog=x).fit()

        return result
        #result.summary()


    @classmethod
    def statsmodels_multi_regression(cls, x_list, y_list):
        """ 
            from domain.services.calculation.regression import RegressionCalc
            y = [1,2,3,4,3,4,5,4,5,5,4,5,4,5,4,5,6,5,4,5,4,3,4]
            x = [
                 [4,2,3,4,5,4,5,6,7,4,8,9,8,8,6,6,5,5,5,5,5,5,5],
                 [4,1,2,3,4,5,6,7,5,8,7,8,7,8,7,8,7,7,7,7,7,6,5],
                 [4,1,2,5,6,7,8,9,7,8,7,8,7,7,7,7,7,7,6,6,4,4,4]
                 ]
            
            result = RegressionCalc.statsmodels_multi_regression(x_list, y_list)
        """
        import numpy as np
        import statsmodels.api as sm
        x = np.array(x_list).T
        x = sm.add_constant(x)  
        result = sm.OLS(endog=y_list, exog=x).fit()

        return result
        #result.summary()


    @classmethod
    def manual_regress(cls, x_list, y_list):
        """ 1차 회귀식 직접 계산
            from domain.services.calculation.regression import RegressionCalc
            y_list = [90,60,73,65,51,93,88,92,86,78,80,72,74,68,76]
            x_list = [58,65,63,64,68,57,59,56,60,62,61,63,64,64,61]
            result = RegressionCalc.scipy_regression(x_list, y_list)

            r2, slope, intercept = RegressionCalc.manual_regress(x_list, y_list)
        """
        sumX = 0
        sumY = 0
        sumX2 = 0
        sumY2 = 0
        ssX = 0
        ssY = 0
        sumXY = 0
        sCo = 0
        count = len(x_list)
        for index, x in enumerate(x_list):
            y = y_list[index]
            sumXY += x * y
            sumX += x 
            sumY += y
            sumX2 += x ** 2
            sumY2 += y ** 2 
        ssX = sumX2 - (sumX ** 2) / count
        ssY = sumY2 - (sumY ** 2) / count
        r_up = count * sumXY - sumX * sumY
        r_dn = (count * sumX2 - sumX ** 2) * (count * sumY2 - sumY ** 2)
        print('r_dn='+str(r_dn))
        sCo = sumXY - sumX * sumY / count
        xbar = sumX / count 
        ybar = sumY / count
        r = r_up / math.sqrt(r_dn)
        r2 = r * r 
        intercept = ybar - sCo / ssX * xbar
        slope = sCo / ssX

        return r2, slope, intercept
       

class CurveFit(object):
    """ SqcMate에 구현된 로직을 porting함. 원 로직은 [Numerical Recipe in C] 책이었을 것으로 추정.

        from domain.services.calculation.regression import CurveFit
        fit = CurveFit()
        y_list = [90,60,73,65,51,93,88,92,86,78,80,72,74,68,76]
        x_list = [58,65,63,64,68,57,59,56,60,62,61,63,64,64,61]
        fit.set_data(15, x_list, y_list)
        fit.calc_scatter_regression(x_list, y_list, 1)
        fit.calc_scatter_regression(x_list, y_list, 2)

        fit.calc_scatter_regression(x_list, y_list, 1, 'log', 1, 0). log는 2걔의 변환계수를 가진다. y2 = a * log(y+b)
        fit.calc_scatter_regression(x_list, y_list, 1, 'power', 1, 0, 2). power는 3개의 반환계수를 가진다. y2 = a * (y+b) ^ c

        return 
        fit.equation : 회귀식. 계수는 소수점 4째자리까지만 표시
        fit.coef_list : 회귀식의 차수. 0번째는 무시. 1번째는 상수, 2번째는 1차항의 계수, 3번째는 2차항의 계수, 4번째는 3차항의 계수, 5번째는 4차항의 계수.
        fit.r2 : r-square 값
        
    """
    def __init__(self):
        self.x_list = []
        self.y_list = []
        self.data_count = 0
        self.equ_order = 1  # 회귀식 차수. 최대 4차까지로 제한.
        #self.origin_type = 'ignore' # through 
        #self.fit_type = 'linear'    # log, power
        
        #self.avail = False 
        self.matrix_size = 0 
        self.matrix = [[]]
        self.index_list = []

        self.coef_list = []
        self.r2 = 0
        self.equation = ''
        self.sign_check = 0

           
    def calc_scatter_regression(self, x_list, y_list, equ_order, y_trans='', *ytrans_coef):
        """
            equ_order: 회귀분석식 차수
            y_trans: '  log' 로그변환 y2 = a * log(y+b)
                        'power' 지수변환 y2 = a * (y+b) ^ c
            y_trans_coef: a, b, c
        """
        data_count = len(x_list)
        if data_count <= 1:
            return False
        if data_count <= equ_order:
            return False 
        if equ_order < 1 or equ_order > 4:
            return False
        if data_count != len(y_list):
            return False
        if y_trans == 'log':
            a = ytrans_coef[0]
            b = ytrans_coef[1]
            y2_list = [ a * math.log(y + b) for y in y_list]
                
        elif y_trans == 'power':
            a = ytrans_coef[0]
            b = ytrans_coef[1]
            c = ytrans_coef[2]
            y2_list = [ a * math.pow(y + b, c) for y in y_list]
        else:
            y2_list = y_list

        if not self.set_data(data_count, x_list, y2_list, equ_order):
            return False 

        success = self.do_calc()
        if not success:
            print('do calc false')
            return False 

        print('calc_scatter_regression')
        equation = 'y ='
        for index in range(0, self.equ_order+1):
            order = self.equ_order - index
            var = self.coef_list[order+1]
            var = round(var, 4)
            if order == 0:
                equation += ' + ' + str(var) 
            elif order == 1:
                if index == 0:
                    equation += ' ' + str(var) +' * x'
                else:
                    equation += ' + ' + str(var) +' * x'
            else:
                if index == 0:
                    equation += ' ' + str(var) +' * x' + str(order)
                else:
                    equation += ' + ' + str(var) +' * x' + str(order)
        self.equation = equation
        print(self.equation)
        print(self.r2)

        self.calc_sign_check( self.data_count, self.x_list[1:], self.y_list[1:] )
        print('부호검정: '+ str(self.sign_check) + '%')
        
        return True


    def alloc_vector(self, vector_size):
        """ 편의상 1 base list로 만듬. 0번째 원소는 사용 안함.
        """
        vector = [ None for i in range(0, vector_size + 1) ]
        return vector


    def alloc_matrix(self, matrix_size):
        """ 편의상 1 base list로 만듬. 0번째 원소는 사용 안함.
        """
        matrix = []
        for row in range(0, matrix_size + 1):
            col_list = self.alloc_vector(matrix_size)
            matrix.append( col_list )

        return matrix


    def set_data(self, data_count, x_list, y_list, equ_order = 1):
        if data_count <= 1:
            return False
        if data_count <= equ_order:
            return False 
        if equ_order < 1 or equ_order > 4:
            return False
    
        self.x_list = self.alloc_vector(data_count)  
        self.y_list = self.alloc_vector(data_count)  

        for i in range(0, data_count):
            self.x_list[i+1] = x_list[i]    # zero-base -> one-base 
            self.y_list[i+1] = y_list[i]

        self.data_count = data_count 

        self.equ_order = equ_order
        #self.fit_type = fit_type 
        #self.origin_type = origin_type 
        #self.avail = False

        return True

    
    def make_matrix(self, matrix_size, data_count):
        """
        """
        print('make_matrix')
        
        for i in range(1, matrix_size+1):
            
            for j in range(1, i+1):
                k = i + j - 2
                sum = 0
                for m in range(1, data_count+1):
                    sum += math.pow(self.x_list[m], k)
                
                self.matrix[i][j] = sum 
                self.matrix[j][i] = sum
            sum = 0
            for m in range(1, data_count+1):
                sum += self.y_list[m] * math.pow(self.x_list[m], i-1)
            self.coef_list[i] = sum

        return


    def do_calc(self):
        print('do_calc')
        even_odd = None

        #self.avail = False

        #if self.fit_type in ('log', 'power'):
        #    self.matrix_size = 2
        #else:
        #    self.matrix_size = self.equ_order + 1
        self.matrix_size = self.equ_order + 1
        # Allocate coeficient vectors			
        self.coef_list = self.alloc_vector(self.matrix_size)  
        # Allocate permutation vectors
        self.index_list = self.alloc_vector(self.matrix_size) 
        self.matrix = self.alloc_matrix(self.matrix_size)
        self.make_matrix(self.matrix_size, self.data_count)
        print(self.matrix)
        success = self.ludcmp(even_odd)
        if success:
            success = self.lubksb()

        #self.index_list = []
        #self.matrix = []

        if not success:
            self.coef_list = []
            return False

        #self.avail = True
        self.r2 = self.calc_corr_coef()
        print('do_calc end')

        return True


    def ludcmp(self, even_odd):
        """
        //	ludcmp
        //	Description:
        // 		Given an m_nMatrixSize x m_nMatrixSize matrix m_ppMatrix[1..m_nMatrixSize][1..m_nMatrixSize],
        //		this routine replace it by the LU decomposition or a rowwise permutation of itself.
        // 	Using members:
        //		m_ppMatrix is in/out
        //		m_nMatrixSize is in
        //		m_pIndex 	- an output vector which records the row permutation effected by the partial
        //					  pivoting
        // 	Parameters
        //		pEvenOdd	- output as +-1 depending on whether the number of row interchanges was
        //					  even or odd, respectively
        //	Note:
        //		This routine is used in combination with lubksb(); to solve linear equations or 
        //		invert a matrix, refer to "Numerical Recipes in C", p43
        """
        print('ludcmp')
        vector_list = self.alloc_vector(self.matrix_size)
        even_odd = 1.0 # no row interchanges yet 

        big = None

        # Loop over rows to get the implict scalling information	 
        for i in range(1, self.matrix_size+1):
            big = 0
            for j in range(1, self.matrix_size+1):
                dTemp = math.fabs(self.matrix[i][j])
                if dTemp > big:
                    big = dTemp 
            if big == 0:
                return False # singular matrix
            # No nonzero largest element 
            vector_list[i] = 1.0 / big  # Save the scaling 

        sum = None
        dum = None 
        max = 1 

        for j in range(1, self.matrix_size+1):  # loop over columns of Crout's method
            for i in range(1, j):   # equation 2.3.12 of Recipes except for i = j
                sum = self.matrix[i][j]
                for k in range(1, i):
                    sum -= self.matrix[i][k] * self.matrix[k][j]
                self.matrix[i][j] = sum

            big = 0.0 #  initialize for the search for largest pivot element 
            for i in range(j, self.matrix_size+1):
                sum = self.matrix[i][j]
                for k in range(1, j):
                    sum -=  self.matrix[i][k] * self.matrix[k][j]
                self.matrix[i][j] = sum

                dum = vector_list[i] * math.fabs(sum ) 
                if dum >= big:  # // Is the figure of metric for the pivot 
                    big = dum 
                    max = i 

            if j != max: # Do we need to interchange rows? 
                for k in range(1, self.matrix_size+1):
                    dum = self.matrix[max][k]
                    self.matrix[max][k] = self.matrix[j][k]
                    self.matrix[j][k] = dum

                even_odd = -1 * even_odd # change the parity of pEvenOdd 
                vector_list[max] = vector_list[j]   #  interchange the scale factor

            self.index_list[j] = max 
            if self.matrix[j][j] == 0:
                self.matrix[j][j] = 1e-20

            # If the pivot element is zero the matrix is singular (at least to the precision of
            #	the algorithm). For some applications on singular matrices, it is desirable to
            #	substitute TINY to zero.

            if j != self.matrix_size:   # Now, finally, divide by the pivot element.
                dum = 1.0 / self.matrix[j][j]
                for i in range(j+1, self.matrix_size+1):
                    self.matrix[i][j] *= dum 

        return True


    def lubksb(self):
        """
        	lubksb
        	Description:
        		Solves the set of m_nMatrixSize equations A.X = B.
        	Using members:
        		m_ppMatrix	- input, not as the matrix A but rather as its LU decomposition,
        					  determined by the routine ludcmp();
        		m_pIndex	- input as the permutation vector returned by ludcmp();
        		m_pCoef		- input as the right-hand side vector B, and returns with the solution
        					  vector X.
        """
        print('lubksb')
        sum = None 
        flag = 0
        for i in range(1, self.matrix_size+1):
            pos = self.index_list[i]
            sum = self.coef_list[pos]
            self.coef_list[pos] = self.coef_list[i]
            if flag:
                for j in range(flag, i):
                    sum -= self.matrix[i][j] * self.coef_list[j]
            elif sum != 0:  # A non-zero element was encountered, so from now on 
                flag = i    # we will have to do the sums in the loop above
            self.coef_list[i] = sum 

        # Now we do the backsubstitution, equation 2.3.7 of Recipes
        for i in reversed(range(1, self.matrix_size+1)):
            sum = self.coef_list[i]
            for j in range(i+1, self.matrix_size+1):
                sum -= self.matrix[i][j] * self.coef_list[j]

            if self.matrix[i][i] == 0:
                return False

            self.coef_list[i] = sum / self.matrix[i][i] # Store a component of the solution vector X
        
        print(self.coef_list)

        return True


    def calc_corr_coef(self):
        """ r, r-square 값을 직접 구함.

        """
        sumX = 0
        sumY = 0
        sumX2 = 0
        sumY2 = 0
        sumXY = 0
        sX2 = 0
        sY2 = 0
        sXY = 0
        
        sCo = 0
        count = self.data_count
        for i in range(1, count+1):
            x = self.x_list[i]
            y = self.y_list[i]
            sumX += x 
            sumY += y
            sumX2 += x ** 2
            sumY2 += y ** 2 
            sumXY += x * y
        sX2 = sumX2 - (sumX ** 2) / count
        sY2 = sumY2 - (sumY ** 2) / count
        sXY = sumXY - sumX * sumY / count 
  
        if sX2 * sY2 > 0:
            r = sXY / math.sqrt(sX2 * sY2)
        else:
            r = 0
        r2 = r * r 

        #xbar = sumX / count 
        #ybar = sumY / count
        #intercept = ybar - sXY / sX2 * xbar
        #slope = sXY / ssX

        print(r2)
        return r2

    def median(self, src_list):
        list = sorted(src_list)
        count = len(list)
    
        mid = (count-1) // 2
    
        if count % 2 == 0:
            return (list[mid] + list[mid+1]) / 2
        else:
            return list[mid]

    def calc_sign_check(self, data_count, x_list, y_list):
        """ 부호검정
        """
        sign1_pct_table =	[
	            -1,		-1,		-1,		-1,		-1,
	            -1,		-1,		-1,		0,		0,
	            0,		0,		1,		1,		1,
	            2,		2,		2,		3,		3,
	            3,		4,		4,		4,		5,
	            5,		6,		6,		6,		7,
	            7,		7,		8,		8,		9,
	            9,		9,		10,		10,		11,
	            11,		11,		12,		12,		13,
	            13,		13,		14,		14,		15,
	            15,		15,		16,		16,		17,
	            17,		17,		18,		18,		19,
	            19,		20,		20,		20,		21,
	            21,		22,		22,		22,		23,
	            23,		24,		24,		25,		25,
	            25,		26,		26,		27,		27,
	            28,		28,		28,		29,		29,
	            30,		30,		31,		31,		31,
	            32,
	        ]

        sign5_pct_table =	[
	            -1,		-1,		-1,		-1,		-1,
	            -1,		0,		0,		0,		1,
	            1,		1,		2,		2,		2,
	            3,		3,		4,		4,		4,
	            5,		5,		5,		6,		6,
	            7,		7,		7,		8,		8,
	            9,		9,		9,		10,	    10,
	            11, 	11,		12,		12,		12,
	            13,		13,		14,		14,		15,
	            15,		15,		16,		16,		17,		
	            17,		18,		18,		18,		19,		
	            19,		20,		20,		21,		21,		
	            21,		22,		22,		23,		23,
	            24,		24,		25,		25,		25,
	            26,		26,		27,		27,		28,
	            28,		28,		29,		29,		30,
	            30,		31,		31,		32,		32,
	            32,		33,		33,		34,		34,
	            35,
	    ]

        sign1_percent = 0
        sign5_percent = 0

        sign_check = 0

        mX = self.median(x_list)
        mY = self.median(y_list)
        q1 = 0
        q2 = 0
        q3 = 0
        q4 = 0

        """ 오른쪽 상단부터 시계반대방향으로  1,2,3,4 """
        for i in range(0, data_count):
            x = x_list[i]
            y = y_list[i]
            if x > mX:
                if y > mY:
                    q1 += 1 
                elif y < mY:
                    q4 += 1 
            elif x < mX:
                if y > mY:
                    q2 += 1 
                elif y < mY:
                    q3 += 1 

        sum13 = q1 + q3
        sum24 = q2 + q4
        q_sum = sum13 + sum24 
        """ sign check """
        if q_sum < len(sign1_pct_table):
            if sum13 <= sum24:
                if sum13 <= sign1_pct_table[q_sum]:
                    sign_check = -1
                elif sum13 <= sign5_pct_table[q_sum]:
                    sign_check = -5
            else:
                if sum24 <= sign1_pct_table[q_sum]:
                    sign_check = 1
                elif sum24 <= sign5_pct_table[q_sum]:
                    sign_check = 5

        self.sign_check = sign_check
        self.sign5_percent = sign5_percent

        print('sum13 = ' + str(sum13))
        print('sum24 = ' + str(sum24))
        return