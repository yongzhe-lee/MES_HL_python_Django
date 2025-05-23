from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class HolidayService():
	def __init__(self):
		return

	def findAll(self, keyword, year):
		items = []
		dic_param = {'keyword': keyword, 'year': year}

		sql = ''' 
				/* findAll [holiday-mapper.xml] */
			SELECT id
				   , day_val as day
				   , month_val as month
				   , year_val as year
				   , name_val as name
				   , type_val as type
				   , nation_cd
				   , repeat_yn
			FROM   cm_holiday_custom
			WHERE 1 = 1
				AND nation_cd = 'ko'
				'''
		if keyword:
			sql += ''' 
						AND UPPER(name_val) similar to CONCAT('%%', UPPER(%(keyword)s), '%%')   							
					'''
		if year:
			sql += ''' 
						AND year_val = %(year)s
					'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'holiday.findAll', ex)
			raise ex

		return items

	def findAllHolidayInfoRes(self):
		items = []
		dic_param = {}		

		sql = ''' 
			/* findAllHolidayInfoRes [holiday-mapper.xml] */

		SELECT day_val as day
		       , month_val as month
		       , year_val as year
		       , name_val as name
		       , type_val as type
		       , nation_cd
		       , 'N' as repeat_yn
		FROM   cm_holiday_info
		WHERE 1 = 1
			AND nation_cd = 'ko'
				'''
		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'holiday.findAllHolidayInfoRes', ex)
			raise ex

		return items

	def findAllHolidayCustom(self):
		items = []
		dic_param = {}		

		sql = ''' 
			/* findAllHolidayCustom [holiday-mapper.xml] */

		SELECT day_val as day
				   , month_val as month
				   , year_val as year
				   , name_val as name
				   , type_val as type
				   , nation_cd
				   , repeat_yn
			FROM   cm_holiday_custom
			WHERE 1 = 1
				AND nation_cd = 'ko'
				'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'holiday.findAllHolidayCustom', ex)
			raise ex

		return items