from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmImportRank, CmEquipment
#from django.db import transaction

def import_rank(context):
    '''
    api/kmms/import_rank    중요도등급
    김태영 

    findAll
    findOne
    findDeletableImportRank
    countBy
    insert
    update
    delete
    deleteUpdate
    findReferencedTablesInfo
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableImportRank(importRankPk):
        q = CmEquipment.objects.filter(CmImportRank_id=importRankPk)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action in ['findAll', 'countBy']:
            useYn = gparam.get('useYn')
            importRankCd = gparam.get('importRankCd')
            searchText = gparam.get('searchText')

            sql = ''' SELECT import_rank_pk, import_rank_cd, import_rank_desc
            , concat('[', import_rank_cd , '] ', import_rank_desc) AS import_rank_desc
           , use_yn, del_yn
           , insert_ts, inserter_id, inserter_nm
           , update_ts, updater_id, updater_nm
            FROM cm_import_rank t
            where del_yn = 'N'
            '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                    '''
            if importRankCd:
                sql += ''' AND t.import_rank_cd = %(importRankCd)s
                '''
            if searchText:
                sql += ''' AND ( UPPER(t.import_rank_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''

            sql += ''' order by t.import_rank_nm
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['importRankCd'] = importRankCd
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            importRankPk = CommonUtil.try_int( gparam.get('importRankPk') )

            sql = ''' SELECT import_rank_pk, import_rank_cd, import_rank_desc
            , concat('[', import_rank_cd , '] ', import_rank_desc) AS import_rank_desc
           , use_yn, del_yn
           , insert_ts, inserter_id, inserter_nm
           , update_ts, updater_id, updater_nm
            FROM cm_import_rank t
            where del_yn = 'N'
            and t.import_rank_pk = %(importRankPk)s
            '''

            dc = {}
            dc['importRankPk'] = importRankPk

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            importRankPk = CommonUtil.try_int(posparam.get('importRankPk'))
            importRankCd = posparam.get('importRankCd')
            importRankDesc = posparam.get('importRankDesc')
            useYn = posparam.get('useYn')
  
            if action == 'update':
                c = CmImportRank.objects.get(id=importRankPk)

            else:
                c = CmImportRank()

            c.ImportRankCode = importRankCd
            c.ImportRankDesc = importRankDesc
            c.UseYn = useYn
            c.DelYn = 'N'
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '중요도등급 정보가 수정되었습니다.'}


        elif action == 'delete':
            importRankPk = CommonUtil.try_int(posparam.get('importRankPk'))
            if not findDeletableImportRank(importRankPk):
                CmImportRank.objects.filter(id=importRankPk).delete()

            items = {'success': True}
    

        elif action == 'deleteUpdate':
            importRankPk = CommonUtil.try_int(posparam.get('importRankPk'))
            c = CmImportRank.objects.get(id=importRankPk)
            c.DelYn = 'Y'
            c.save()

            items = {'success': True}


        elif action == 'findDeletableImportRank':
            importRankPk = CommonUtil.try_int(posparam.get('importRankPk'))
            return findDeletableImportRank(importRankPk)


        elif action == 'findReferencedTablesInfo':
            importRankPk = CommonUtil.try_int(posparam.get('importRankPk'))
            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
            FROM (
	            select 'equipment.importrankpk.lbl' as i18n_code, count(*) as cnt 
	            from cm_equipment
	            where import_rank_pk = %(importRankPk)s 
	            and del_yn = 'N'
            ) t
            left join cm_i18n t1 on t.i18n_code = t1.lang_code
            where t.cnt > 0
            '''
            dc = {}
            dc['importRankPk'] = importRankPk

            items = DbUtil.get_row(sql, dc)


    except Exception as ex:
        source = 'kmms/import_rank : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items

    return items