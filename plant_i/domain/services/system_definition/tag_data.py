# 1. 표준 라이브러리
from datetime import datetime, timedelta

from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from configurations import settings

from domain.models.definition import TagMaster, TagData

class TagDataService():
    def __init__(self):
        pass


    def tag_multi_data_list(self, start_date, end_date, tag_codes):
        #start_date = posparam.get('start_time', '')
        #end_date = posparam.get('end_time', '')
        #tag_codes = posparam.get('tag_codes', '')

        items = {}

        sql = '''
        with A as (
            select unnest(string_to_array(%(tag_codes)s, ';')) as tag_code
        )
		select T.tag_code, T.tag_name,  t."LSL" as lsl, t."USL" as usl
		from Tag T 
		inner join A on A.tag_code = T.tag_code 
        '''
        dc = {}
        dc['tag_codes'] = tag_codes
        #dc['tag_group_pk'] = tag_group_pk

        rows = DbUtil.get_rows(sql, dc)
        for row in rows:
            tag = {}
            tag_code = row['tag_code']
            tag['tag_name'] = row['tag_name']
            tag['lsl'] = row['lsl']
            tag['usl'] = row['usl']
            items[tag_code] = tag

        sql = '''
        with A as (
            select unnest(string_to_array(%(tag_codes)s, ';')) as tag_code
        )
		select td.tag_code, td.data_date, to_char(td.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_time, td.data_value
	    from das.tag_dat td 
        inner join A on A.tag_code = td.tag_code
        where 1=1
        and td.data_date between %(date_from)s and %(date_to)s
        order by td.tag_code, td.data_date
        '''

        dc = {}
        dc['date_from'] = start_date
        dc['date_to'] = end_date
        dc['tag_codes'] = tag_codes
        #dc['tag_group_pk'] = tag_group_pk

        rows = DbUtil.get_rows(sql, dc)
        #for row in rows:
        #    tag_code = row['tag_code']
        #    data = items[tag_code]
        #    data['data'] = row

        items['rows'] = rows
        return items


    def tag_multi_data_list2(self, start_date, end_date, tag_codes):
        #start_date = posparam.get('start_time', '')
        #end_date = posparam.get('end_time', '')
        #tag_codes = posparam.get('tag_codes', '')

        items = {}
        if settings.DBMS =='MSSQL' :
            sql = '''
            with A as (
                select value as tag_code from string_split(%(tag_codes)s, ';')
            )
			select T.tag_code, T.tag_name,  t."LSL" as lsl, t."USL" as usl
			from Tag T 
			inner join A on A.tag_code = T.tag_code 
            '''
        else :
            sql = '''
            with A as (
                select unnest(string_to_array(%(tag_codes)s, ';')) as tag_code
            )
			select T.tag_code, T.tag_name,  t."LSL" as lsl, t."USL" as usl
			from Tag T 
			inner join A on A.tag_code = T.tag_code 
            '''
        dc = {}
        dc['tag_codes'] = tag_codes
        #dc['tag_group_pk'] = tag_group_pk

        rows = DbUtil.get_rows(sql, dc)
        for row in rows:
            tag = {}
            tag_code = row['tag_code']
            tag['tag_name'] = row['tag_name']
            tag['lsl'] = row['lsl']
            tag['usl'] = row['usl']
            items[tag_code] = tag

        if settings.DBMS =='MSSQL' :
            sql = '''
            with A as (
                select value as tag_code from string_split(%(tag_codes)s, ';')
            )
			select td.tag_code, td.data_date, Format(td.data_date, 'yyyy-MM-dd HH:mm:ss') as data_time
            , convert(float, round(convert(decimal, td.data_value), T."RoundDigit")) as data_value
	        from das.tag_dat td
            inner join A on A.tag_code = td.tag_code
            inner join tag T on T.tag_code = td.tag_code
            where 1=1
            and td.data_date between %(date_from)s and %(date_to)s
            order by td.tag_code, td.data_date
            '''
        else :
            # 25.06.19 김하늘 전력량계 데이터 별도 수집에 따른 쿼리 수정
            sql = f'''
            with A as (
                select unnest(string_to_array(%(tag_codes)s, ';')) as tag_code
            )
            select * from (
			    select 
                    td.tag_code
                    , td.data_date
                    , to_char(td.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_time
                    , round(td.data_value::decimal, coalesce (T."RoundDigit",2))::float as data_value
	            from das.tag_dat td
                inner join A on A.tag_code = td.tag_code
                inner join tag T on T.tag_code = td.tag_code
                where 1=1
                    and td.data_date between %(date_from)s and %(date_to)s

                union all

			    select 
                    td.tag_code
                    , td.data_date
                    , to_char(td.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_time
                    , round(td.data_value::decimal, coalesce (T."RoundDigit",2))::float as data_value
                from das.em_tag_dat td
                inner join A on A.tag_code = td.tag_code
                inner join tag T on T.tag_code = td.tag_code
                where 1=1
                    and td.data_date between %(date_from)s and %(date_to)s
            ) as merged_data
            order by tag_code, data_date

            '''

        dc = {}
        dc['date_from'] = start_date
        dc['date_to'] = end_date
        dc['tag_codes'] = tag_codes
        #dc['tag_group_pk'] = tag_group_pk

        rows = DbUtil.get_rows(sql, dc)
        for row in rows:
            tag_code = row['tag_code']
            value = items[tag_code]
            if 'data' in value:
                data = value['data']
            else:
                data = []
                value['data'] = data
            data.append(row)

        return items


    def tagdata_delete(self, tag_code, start_time, end_time):
        try:
            ret = False

            sql = '''
            delete from das.tag_dat
            where tag_code = %(tag_code)s
            and data_date between %(date_from)s and %(date_to)s
            '''
            dc = {}
            dc['tag_code'] = tag_code 
            dc['date_from'] = start_time 
            dc['date_to'] = end_time + ':59' 
            
            ret = DbUtil.execute(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'TagDataService.tagdata_delete', ex)
            raise ex
        return ret


    def tagdata_make(self, tag_code, start_time, end_time, interval, values):
        """ 샘플 태그데이터 생성. 
            values
                '1'  - 해당기간동안 1값을 입력
                '1.2;2.1;2.3;1.2' - 값들을 반복해서 입력
                '1*20;0*10;1*35' - 1을 20번, 0을 10번 입력.
        """
        try:
            data_date = datetime.strptime(start_time,'%Y-%m-%d %H:%M')
            end_time = datetime.strptime(end_time,'%Y-%m-%d %H:%M')

            delta = timedelta(minutes=int(interval))

            value_list = []
            value_count = 0

            list1 = values.split(';')
            for item in list1:
                list2 = item.split('*')
                val = CommonUtil.try_float(list2[0])
                if val == None: # 0 허용
                    return False

                if len(list2) >= 2:
                    count = CommonUtil.try_int(list2[1])
                    if not count:   # 0 안됨
                        return False
                    value_list += [val] * count
                elif len(list2) == 1:
                    value_list.append(val)

            value_count = len(value_list)
            value_index = 0
            while data_date <= end_time:
                if value_index == value_count:
                    value_index = 0
                data_value = value_list[value_index]
                value_index += 1
                    
                TagData.save_data(tag_code, data_date, data_value)
                data_date = data_date + delta
        except Exception as ex:
            LogWriter.add_dblog('error', 'TagDataService.tagdata_make', ex)
            raise ex
        return True

    def tagdata_gauss_make(self, tag_code, start_time, end_time, interval, average, stdev):
        """샘플 태그데이터 정규분포 형태로 생성
        """
        try:
            import random as random

            tag = TagMaster.objects.get(pk=tag_code)
            round_digit = CommonUtil.try_int(tag.RoundDigit, 3)

            data_date = datetime.strptime(start_time,'%Y-%m-%d %H:%M')
            end_time = datetime.strptime(end_time,'%Y-%m-%d %H:%M')
            delta = timedelta(minutes=int(interval))

            average = float(average)
            stdev = float(stdev)

            while data_date <= end_time:
                data_value = random.gauss(average, stdev)
                data_value = round(data_value, round_digit)
                TagData.save_data(tag_code, data_date, data_value)
                data_date = data_date + delta
        except Exception as ex:
            LogWriter.add_dblog('error', 'TagDataService.tagdata_gauss_make', ex)
            raise ex
        return True

    def tag_multi_data_list_couple(self, start_date, end_date, tag_codes):
        '''
        작성명 : 테그데이터 조회 1:1 결합
        작성자 : 이인호
        작성일 : 2021-05-06
        비고 :

        -수정사항-
        수정일: 2025-06-19           
        작업자: 김하늘
        수정내용: 전력량계 수집데이터 테이블 추가에 따른 쿼리 수정
        '''
        if settings.DBMS =='MSSQL' :
            sql = '''
                with A as (
                    select value as tag_code from string_split(%(tag_codes)s, ';') 
                )
		        , tag_data_min as(
				    select top (select count(*) from das.tag_dat)
                    t.tag_name, td.tag_code, Format(td.data_date, 'yyyy-MM-dd HH:mm') as data_time
					    , avg(round(td.data_value, T."RoundDigit")) as data_value
				    from das.tag_dat td 
				    inner join A on A.tag_code = td.tag_code
				    inner join tag T on T.tag_code = td.tag_code
				    where 1=1
				    and td.data_date between %(date_from)s and %(date_to)s
				    group by t.tag_name,td.tag_code, Format(td.data_date, 'yyyy-MM-dd HH:mm')
				    order by td.tag_code, Format(td.data_date, 'yyyy-MM-dd HH:mm')
			    )
			    select tdm1.tag_code as code1, tdm2.tag_code as code2
                , concat( tdm1.tag_name, '_', tdm2.tag_name) as couple_name
			    ,concat(tdm1.tag_code, '_', tdm2.tag_code) as couple_code
			    ,tdm1.data_value as x_val
			    ,tdm2.data_value as y_val
			    from tag_data_min tdm1
			    inner join tag_data_min tdm2 on tdm2.data_time = tdm1.data_time
                where tdm2.tag_code != tdm1.tag_code 
			    order by 1
            '''
        else :
            sql = '''
                with A as (
                    select unnest(string_to_array(%(tag_codes)s, ';')) as tag_code
                )
                , tag_dat_part AS (
                    SELECT 
                        t.tag_name,
                        td.tag_code,
                        td.data_date,
                        td.data_value,
                        COALESCE(t."RoundDigit", 2) AS round_digit
                    FROM das.tag_dat td
                    INNER JOIN A ON A.tag_code = td.tag_code
                    INNER JOIN tag t ON t.tag_code = td.tag_code
                    WHERE td.data_date BETWEEN %(date_from)s AND %(date_to)s
                )
                , em_tag_dat_part AS (
                    SELECT 
                        t.tag_name,
                        td.tag_code,
                        td.data_date,
                        td.data_value,
                        COALESCE(t."RoundDigit", 2) AS round_digit
                    FROM das.em_tag_dat td
                    INNER JOIN A ON A.tag_code = td.tag_code
                    INNER JOIN tag t ON t.tag_code = td.tag_code
                    WHERE td.data_date BETWEEN %(date_from)s AND %(date_to)s
                )
                , merged_tag_data AS (
                    SELECT * FROM tag_dat_part
                    UNION ALL
                    SELECT * FROM em_tag_dat_part
                )
		        , tag_data_min as(
				    select 
                        tag_name
                        , tag_code
                        , to_char(data_date, 'yyyy-mm-dd hh24:mi') as data_time
					    , avg(round(data_value::decimal, round_digit))::float as data_value
				    from merged_tag_data
                    GROUP BY tag_name, tag_code, TO_CHAR(data_date, 'yyyy-mm-dd hh24:mi')
                    ORDER BY tag_code, TO_CHAR(data_date, 'yyyy-mm-dd hh24:mi')
			    )
			    select 
                    tdm1.tag_code as code1
                    , tdm2.tag_code as code2
                    , tdm1.tag_name||'_'||tdm2.tag_name as couple_name
			        , tdm1.tag_code||'_'||tdm2.tag_code as couple_code
			        , tdm1.data_value as x_val
			        , tdm2.data_value as y_val
			    from tag_data_min tdm1
			    inner join tag_data_min tdm2 
                    on tdm1.data_time = tdm2.data_time
                where tdm2.tag_code != tdm1.tag_code 
			    order by 1
            '''

        dc = {}
        dc['date_from'] = start_date
        dc['date_to'] = end_date
        dc['tag_codes'] = tag_codes

        rows = DbUtil.get_rows(sql, dc)

        return rows