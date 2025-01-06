from django.db import connection
from configurations import settings
import pyodbc
#from domain.services.logging import LogWriter

# Multi Database인 경우 아래 참고
# from django.db import connections
# with connections['my_db_alias'].cursor() as cursor:

class DbUtil(object):
    """description of class"""

    @classmethod   
    def get_connection(cls):
        #return connection
        try:
            return connection
            #if settings.DBMS != 'MSSQL':
            #    return connection
            #else:
            #    conn = pyodbc.connect(settings.ODBC_CONN_STRING)
            #    return conn
        except Exception as ex:
            #LogWriter.add_dblog('error', 'SystemService.get_connection', ex)
            raise ex


    @classmethod 
    def _dict_fetchall(cls, cursor):
        "Return all rows from a cursor as a dict"
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return [ dict(zip(columns, row)) for row in rows ]


    @classmethod 
    def _dict_fetchone(cls, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row)) 
        else:
            return None

    @classmethod
    def sql_remove_comment(cls, sql):
        """ sql 문에서 주석 처리된 라인을 제거. 주석 라인에 파라미터 있을 경우 에러를 제거
        """
        strings = sql.split(chr(10))
        ret = []
        for item in strings:
            if not item.strip().startswith('--'):
                ret.append(item)
        new_sql = chr(10).join(ret)
        return new_sql

    @classmethod
    def execute_param(cls, cursor, sql, param):
        row_effected = False
        try:
            if settings.DBMS == 'MSSQL':
                import re
                pattern = re.compile(r'[%]\((.+?)\)[s]')
                new_sql = DbUtil.sql_remove_comment(sql)
                match_list = re.findall(pattern, new_sql)
                new_param_list = []
                new_param_dic = {}
                for match in match_list:
                    new_param_list.append(match)
                    new_param_dic[match] = None
                #new_sql = sql
                for key in new_param_dic.keys():
                    key2 = '%(' + key + ')s'
                    new_sql = new_sql.replace(key2, '%s')
                    #new_sql = new_sql.replace(key2, '?')
                new_param = []
                for item in new_param_list:
                    new_param.append(param.get(item))
                row_effected = cursor.execute(new_sql, tuple(new_param))
            else:
                new_sql = ''
                row_effected = cursor.execute(sql, param)
        except Exception as ex:
            #LogWriter.add_dblog('error', 'execute_param', ex + ' sql:'+sql)
            print(ex)
            if new_sql:
                text = new_sql.replace('\n',' ')
            else:
                text = sql.replace('\n',' ')
            print(text)
            raise ex

        return row_effected


    @classmethod
    def get_rows(cls, sql, param=None):
        """Return query resultset in dictionay
        """
        conn = cls.get_connection()
        cursor = conn.cursor()

        if param:
            #cursor.execute(sql, param)
            cls.execute_param(cursor, sql, param)
        else:
            cursor.execute(sql)

        rows = cls._dict_fetchall(cursor)
        cursor.close()
        return rows


    @classmethod
    def get_row(cls, sql, param=None):
        """Return one result or query in dictionay
        """
        conn = cls.get_connection()
        cursor = conn.cursor()

        if param:
            #cursor.execute(sql, param)
            cls.execute_param(cursor, sql, param)
        else:
            cursor.execute(sql)

        #rows = cls._dict_fetchall(cursor)
        row = cls._dict_fetchone(cursor)
        
        cursor.close()
        #if rows:
        #    row = rows[0]
        #else:
        #    row = {}

        return row


    @classmethod
    def get_rows_list(cls, sql, param=None):
        """Return query resultset in list
        """
        conn = cls.get_connection()
        cursor = conn.cursor()

        if param:
            #cursor.execute(sql, param)
            cls.execute_param(cursor, sql, param)
        else:
            cursor.execute(sql)

        rows = cursor.fetchall()
        cursor.close()
        #conn.close()
        return rows


    @classmethod
    def get_row_list(cls, sql, param=None):
        """Return one result or query  in list
        """
        conn = cls.get_connection()
        cursor = conn.cursor()

        if param:
            #cursor.execute(sql, param)
            cls.execute_param(cursor, sql, param)
        else:
            cursor.execute(sql)

        rows = cursor.fetchall()
        cursor.close()
        #conn.close()

        if rows:
            row = rows[0]
        else:
            row = {}

        return row


    @classmethod
    def execute(cls, sql, param=None):
        """Exectue insert, update, delete query and return success(booleand)
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        row_effected = False
        try:
            if param:
                row_effected = cls.execute_param(cursor, sql, param)
            else:
                cursor.execute(sql)
            
            row_effected= True
        finally:
            cursor.close()

        return row_effected



    @classmethod
    def sp_exec(cls, sql, param=None):
        conn = cls.get_connection()
        cursor = conn.cursor()

        result = {}

        output_params = {}
        data_set = []
        if param:
            #cursor.execute(sql, param)
            cls.execute_param(cursor, sql, param)
        else:
            cursor.execute(sql)

        while cursor.description:
            rows = cls._dict_fetchall(cursor)
            #if not rows:
            #    break
            if rows and rows[0].get('rows_type') == 'output':
                output_params = rows[0]
            else:
                data_set.append(rows)
            if not cursor.nextset():
                break

        result['dataSet'] = data_set
        if len(data_set) > 0:
            result['dataTable'] = data_set[0]
        else:
            result['dataTable'] = []
        result['output_params'] = output_params
        
        cursor.close()
        return result


    @classmethod
    def sp_test1(cls):
        sql = '''
             declare @ret integer
             , @out1 varchar(20)
             , @out2 varchar(20)

             exec @ret = test_proc_ty 1, 'aa', @out_param1 = @out1 output, @out_param2 = @out2 output

             select 'output' as rows_type, @ret as return_value, @out1 as out_param1, @out2 as out_param2
             '''

        sp_result = DbUtil.sp_exec(sql)

        return sp_result

    @classmethod
    def sp_test2(cls):
        sql = '''
             declare @ret integer
             , @out1 varchar(20)
             , @out2 varchar(20)

             exec @ret = test_proc_ty %(param1)s, %(param2)s, @out_param1 = @out1 output, @out_param2 = @out2 output

             select 'output' as rows_type, @ret as return_value, @out1 as out_param1, @out2 as out_param2
             '''
        dc = {}
        dc['param1'] = 10 
        dc['param2'] = 'xyz'
        sp_result = DbUtil.sp_exec(sql, dc)

        return sp_result