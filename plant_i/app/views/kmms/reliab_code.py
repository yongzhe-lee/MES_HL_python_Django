from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmReliabCodes

def reliab_code(context):
    '''
    api/kmms/reliab_code    신뢰도 코드 정보
    김태영 

    findAll 전체목록조회
    findOne 한건조회
    insert
    update
    delete
    findDeletableReliabCodes
    findReferencedTablesInfo
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableReliabCodes(reliabCd, types):
        sql = ''' select 1
        where exists (
            SELECT 1
            FROM cm_work_order
            WHERE problem_cd = %(reliabCd)s
            AND 'PC' = %(types)s
            AND site_id = %(factory_pk)s
            UNION ALL
            SELECT 1
            FROM cm_work_order
            WHERE remedy_cd = %(reliabCd)s
            AND 'RC' = %(types)s
            AND site_id = %(factory_pk)s
            UNION ALL
            SELECT 1
            FROM cm_work_order
            WHERE cause_cd = %(reliabCd)s
            AND 'CC' = %(types)s
            AND site_id = %(factory_pk)s
            UNION ALL
            SELECT 1
            FROM cm_wo_fault_loc t1
            INNER JOIN cm_work_order t2 ON t1.work_order_pk = t2.work_order_pk
            WHERE t1.cause_cd = %(reliabCd)s
            AND 'FC' = %(types)s
            AND t2.site_id = %(factory_pk)s
        )
        '''
        dc = {}
        dc['reliabCd'] = reliabCd
        dc['factory_pk'] = factory_id

        row = DbUtil.get_row(sql, dc)
        if row:
            return 1
        else:
            return 0

    try:
        if action == 'findAll':
            useYn = gparam.get('useYn')
            reliabCd = gparam.get('reliabCd')
            reliabNm = gparam.get('reliabNm')
            types = gparam.get('types')
            searchText = gparam.get('searchText')

            sql = ''' SELECT t.reliab_cd
                 , concat('[', t.reliab_cd, '] ', t.reliab_nm) as reliab_nm
               , t.reliab_nm
             , t."types"
               , t.remark
               , t.factory_pk
               , t.use_yn
               , t.insert_ts
               , t.inserter_id
               , ci."Name" as inserter_nm
               , t.update_ts
               , t.updater_id
               , ui."Name" as updater_nm
            FROM cm_reliab_codes t
            left join user_profile ci on t.inserter_id = ci."User_id"
            left join user_profile ui on t.updater_id = ui."User_id"
        
            '''
            if reliabCd:
                sql += ''' t.reliab_cd = %(reliabCd)s
                    '''
            if reliabNm:
                sql += ''' AND UPPER(t.reliab_code_nm) = UPPER(%(reliabNm)s)
                '''            
            if types:
                sql += ''' AND t.types = %(types)s
                '''
            if useYn:
                sql += ''' AND t.use_yn = %(useYn)s
                    '''
            if searchText:
                sql += ''' AND ( UPPER(t.reliab_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
                OR UPPER(t.reliab_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''

            sql += ''' order by t.insert_ts desc
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['reliabCd'] = reliabCd
            dc['reliabNm'] = reliabNm
            dc['types'] = types
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'findOne':
            reliabCd = gparam.get('reliabCd')

            sql = ''' SELECT t.reliab_cd
                 , concat('[', t.reliab_cd, '] ', t.reliab_nm) as reliab_nm
               , t.reliab_nm
             , t."types"
               , t.remark
               , t.factory_pk
               , t.use_yn
               , t.insert_ts
               , t.inserter_id
               , ci."Name" as inserter_nm
               , t.update_ts
               , t.updater_id
               , ui."Name" as updater_nm
            FROM cm_reliab_codes t
            left join user_profile ci on t.inserter_id = ci."User_id"
            left join user_profile ui on t.updater_id = ui."User_id"
            AND t.reliab_cd = %(reliabCd)s
		    AND t.factory_pk = %(factory_pk)s
            '''

            dc = {}
            dc['reliabCd'] = reliabCd
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            reliabCd = posparam.get('reliabCd')
            types = posparam.get('types')
            reliabNm = posparam.get('reliabNm')
            remark = posparam.get('remark')
            useYn = posparam.get('useYn')
  
            if action == 'update':
                q = CmReliabCodes.objects.filter(ReliabCode=reliabCd)
                q = q.filter(Types=types)
                q = q.filter(Factory_id=factory_id)
                c = q.first()
            else:
                c = CmReliabCodes()
                c.ReliabCode = reliabCd
                c.Types = types
                c.Factory_id = factory_id
            c.ReliabName = reliabNm
            c.Remark = remark
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '코드 정보가 등록되었습니다.'}


        elif action == 'delete':
            reliabCd = posparam.get('reliabCd')
            types = posparam.get('types')
            check = findDeletableReliabCodes(reliabCd, types)
            if check == 1:
                items = {'success': False, 'message': '이미 참조하는 테이블이 있어서 삭제할 수 없습니다.'}
                return items

            q = CmReliabCodes.objects.filter(ReliabCode=reliabCd)
            q = q.filter(Types=types)
            q = q.filter(Factory_id=factory_id)
            q.delete()

            items = {'success': True}
    

        elif action == 'findDeletableReliabCodes':
            reliabCd = posparam.get('reliabCd')
            types = posparam.get('types')
            return findDeletableReliabCodes(reliabCd, types)


        elif action == 'findReferencedTablesInfo':
            reliabCd = posparam.get('reliabCd')
            types = posparam.get('types')
            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
            FROM (
                SELECT 'workorder.problemcd.lbl' as i18n_code, count(*) as cnt
                FROM cm_work_order
                WHERE problem_cd = %(reliabCd)s
                AND 'PC' = %(types)s
                AND factory_pk = %(factory_pk)s
                UNION ALL
                SELECT 'workorder.remedycd.lbl' as i18n_code, count(*) as cnt
                FROM cm_work_order
                WHERE remedy_cd = %(reliabCd)s
                AND 'RC' = %(types)s
                AND factory_pk = %(factory_pk)s
                UNION ALL
                SELECT 'workorder.causecd.lbl' as i18n_code, count(*) as cnt
                FROM cm_work_order
                WHERE cause_cd = %(reliabCd)s
                AND 'CC' = %(types)s
                AND factory_pk = %(factory_pk)s
                UNION ALL
                SELECT 'workorder.causecd.lbl' as i18n_code, count(*) as cnt
                FROM cm_wo_fault_loc t1
                INNER JOIN cm_work_order t2 ON t1.work_order_pk = t2.work_order_pk
                WHERE t1.cause_cd = %(reliabCd)s
                AND 'FC' = %(types)s
                AND t2.factory_pk = %(factory_pk)s
            ) t
            left join cm_i18n t1 on t.i18n_code = t1.lang_code
            where t.cnt > 0
            '''
            dc = {}
            dc['reliabCd'] = reliabCd
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


    except Exception as ex:
        source = 'kmms/reliab_code : action-{}'.format(action)
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