from configurations import settings
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter


class AttachFileService():
    def get_attach_file(self, TableName, DataPk, attach_name='basic', limit=None):
        items = []
        try:
            sql = ''' select id
             , "TableName"
             , "DataPk"
             , "AttachName"
             , "FileIndex"
             , "FileName"
             , "PhysicFileName"
             , "ExtName"
             , "FilePath"
             , "_created"
             , "ExtName" as "fileExt"
             , "FileName" as "fileNm"
             , "FileSize" as "fileSize"
             , id as "fileId"
             from attach_file 
             where 1 = 1 
             and "TableName" = %(TableName)s
             and "DataPk" = %(DataPk)s
             and "AttachName" = %(attach_name)s
             '''
            sql += ''' order by id desc
            '''
            if limit:
                if settings.DBMS == 'MS_SQL':
                    sql+=''' offset 0 rows fecth next %(limit)s rows only
                    '''
                else:
                    sql+=''' limit %(limit)s
                    '''
            dc = {}
            dc['TableName'] = TableName
            dc['DataPk'] =  CommonUtil.try_int( DataPk )
            dc['limit'] = limit
            dc['attach_name'] =  attach_name 
            
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','FileService.get_attach_file', ex)
            raise ex

        return items

    def get_attach_file_detail(self, file_id):
        sql=''' select id
        , TableName
        , DataPk
        , AttachName
        , FileIndex
        , FileName
        , PhysicFileName
        , ExtName
        , FilePath
        , _created
        , FileSize
        from attach_file 
        where id = %(file_id)s
        '''
        try:
           items = DbUtil.get_row(sql, {'file_id': file_id})

        except Exception as ex:
            LogWriter.add_dblog('error','FileService.get_attach_file_detail', ex)
            raise ex
        
        return items

    def updateDataPk(self, fileId, DataPk):
        items = []
        dc = {}
        dc['fileId'] = fileId
        dc['DataPk'] = DataPk
        
        sql = '''
         update attach_file
         set DataPk = %(DataPk)s
         where id in ( %(fileId)s )
         '''

        try:
            items = DbUtil.execute(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','FileService.updateDataPk', ex)
            raise ex

        return items
