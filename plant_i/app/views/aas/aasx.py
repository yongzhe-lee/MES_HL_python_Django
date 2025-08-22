import uuid
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from configurations import settings


def aasx(context):
    request = context.request
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action', 'read')
    source = f'/api/aas/aasx?action={action}'
    result = {}
    try:
        if action == 'aas_list':
            sql = '''
            with recursive at1 as(
              select
               a1.aas_pk
               , a1.id
               , a1.id_short
               , a1.description
               , a1."displayName"
               , a1.parent_aas_pk as parent_pk
               , 0 as lvl
               , a1._created
              from aas a1
              where a1.parent_aas_pk is null
              union all
              select
              a2.aas_pk
              , a2.id
              , a2.id_short
              , a2.description
              , a2."displayName"  
              , a2.parent_aas_pk as parent_pk
              , at1.lvl+1
              , a2._created
              from aas a2
              inner join at1 on at1.aas_pk = a2.parent_aas_pk      
            )        
            select 
            a.aas_pk 
            , null::numeric as sm_pk
            , a.parent_pk
            , a.id
            , a.id_short
            , a.description
            , a."displayName"
            , 'aas' as gubun
            , to_char(a._created, 'yyyy-mm-dd hh24:mi:ss') as created
            , a.lvl as lvl
            from at1 a 
            '''
            items = DbUtil.get_rows(sql)
            result['success'] = True
            result['items'] = items            

        elif action == 'aasx_file_detail':

            aasx_file = request.FILES.get('file', None)
            if aasx_file is None:
                raise Exception('No file uploaded.')

            ext = aasx_file.name.split('.')[-1]
            ext = ext.lower()


            filename = '%saasx\\%s.%s' % (settings.FILE_UPLOAD_PATH, uuid.uuid4(), ext)
        
            upload_file = open(filename, mode='ab')
            upload_file.write(aasx_file.read())
            upload_file.close()





    except Exception as e:
        LogWriter.add_dblog('error', source, e)
        result['success'] = False
        result['message'] = str(e)
    
    return result