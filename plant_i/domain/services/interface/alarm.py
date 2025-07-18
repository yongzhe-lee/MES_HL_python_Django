
from domain.services.sql import DbUtil

class AlarmService():
    def __init__(self):
        pass

    def get_alarm_history_list(self, rst_id):
        dic_param = {'rst_id': rst_id}
        sql = '''
        select 
        bb.alarm_cd
        , cc.alarm_nm 
        , cc.alarm_num 
        , bb.details
        , to_char(aa.data_date, 'yyyy-mm-dd hh24:mi:ss') data_date
        , to_char(aa.start_dt, 'yyyy-mm-dd hh24:mi:ss') start_dt
        , to_char(aa.end_dt, 'yyyy-mm-dd hh24:mi:ss') end_dt
        , bb.module_no
        , bb.part_number
        , bb.equ_cd 
        from if_equ_result aa
        inner join equ_alarm_hist bb on bb.rst_id =aa.id
        left join equ_alarm cc on cc.alarm_cd  = bb.alarm_cd 
        where aa.id = %(rst_id)s
        order by aa.data_date desc
        '''
        items = sql.DbUtil.get_rows(sql, dic_param)
        return items