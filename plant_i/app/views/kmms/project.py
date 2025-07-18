from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.services.date import DateUtil
from domain.models.cmms import CmProject

def project(context):
    '''
    api/kmms/project 프로젝트
    김태영 

    findAll 전체목록조회
    findOne 한건조회
        countBy 필요?
    insert
    update
    delete
    deleteUpdate
    findDeletableProject
    findReferencedTablesInfo
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableProject(projCd):
  
        q = CmProject.objects.filter(ProjCode=projCd)
        q = q.filter(Factory_id=1)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action in ['findAll']:
            
            projNm = gparam.get('projNm')
            projPkNot = gparam.get('projPkNot')
            searchText = gparam.get('searchText')
            status = gparam.get('status')

            sql = ''' SELECT t.proj_pk
		       , t.proj_nm
		       , t.proj_cd
		       , t.plan_start_dt
		       , t.plan_end_dt
		       , t.manager_id
		       , cm_fn_user_nm(ui."Name", 'N') as user_nm
		       , t.proj_purpose
		       , coalesce(t.proj_tot_cost, 0) as proj_tot_cost
		       , t.status
		       , bc.code_nm as status_nm
		       , t.factory_pk
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		    FROM   cm_project t
		    left join user_profile ui on t.manager_id = cast(ui."User_id" as integer)
		    left join cm_base_code bc on UPPER(t.status) = upper(bc.code_cd) 
            and upper(bc.code_grp_cd) = 'PRJ_STATUS'
		    where 1=1
            AND t.factory_pk = %(factory_id)s
            '''
            # if siteId:
            #     sql += ''' t.use_yn = %(siteId)s
            #         '''
            if projNm:
                sql += ''' AND UPPER(t.projNm) = UPPER(%(projNm)s)
                '''            
            if projPkNot:
                sql += ''' AND t.proj_pk <> %(projPkNot)s
                '''
            if searchText:
                sql += ''' AND ( UPPER(t.proj_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
                or UPPER(t.proj_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''
            if status:
                sql += ''' and UPPER(t.status) = UPPER(%(status)s)
                    '''
            sql += ''' order by t.proj_nm
            '''

            dc = {}
            # dc['siteId'] = siteId
            dc['projNm'] = projNm
            dc['projPkNot'] = projPkNot
            dc['searchText'] = searchText
            dc['status'] = status
            dc['factory_id'] = factory_id

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'findOne':
            projCd = gparam.get('exSupplierPk')

            sql = ''' SELECT t.proj_pk
		       , t.proj_nm
		       , t.proj_cd
		       , t.plan_start_dt
		       , t.plan_end_dt
		       , t.manager_id
		       , cm_fn_user_nm(ui."Name", 'N') as user_nm
		       , t.proj_purpose
		       , coalesce(t.proj_tot_cost, 0) as proj_tot_cost
		       , t.status
		       , bc.code_nm as status_nm
		       , t.factory_pk
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		    FROM   cm_project t
		    left join user_profile ui on t.manager_id = cast(ui."User_id" as integer)
		    left join cm_base_code bc on UPPER(t.status) = upper(bc.code_cd) 
            and upper(bc.code_grp_cd) = 'PRJ_STATUS'
		    where 1=1
            AND t.factory_pk = %(factory_id)s
            AND t.proj_cd = %(projCd)S
            '''

            dc = {}
            dc['projCd'] = projCd
            dc['siteId'] = siteId

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            projNm = posparam.get('proj_nm')
            projCd = posparam.get('proj_cd')
            planStartDt = posparam.get('plan_start_dt')
            planEndDt = posparam.get('plan_end_dt')
            managerId = CommonUtil.try_int(posparam.get('manager_id'))
            projPurpose = posparam.get('proj_purpose')
            projTotCost = posparam.get('proj_tot_cost')
            status = posparam.get('proj_status')
            inserterId = posparam.get('inserterId')
            
            try:
                c = CmProject.objects.get(ProjCode=projCd)
            except CmProject.DoesNotExist:
                c = CmProject()
                #c.insert_ts = DateUtil.get_current_datetime()
                #c.inserter_id = inserterId

            c.ProjName = projNm
            c.ProjCode = projCd
            c.PlanStartDt = planStartDt
            c.PlanEndDt = planEndDt
            c.ManagerId = managerId
            c.ProjPurpose = projPurpose
            c.ProjTotCost = projTotCost
            if status:
                c.Status = status
            else:
                c.Status = 'PREP'
            c.Factory_id = 1
            c.set_audit(user)
            
            c.save()

            return {'success': True, 'message': '프로젝트의 정보가 저장되었습니다.'}


        elif action == 'delete':
            projCd = posparam.get('proj_cd')

            q = CmProject.objects.filter(ProjCode=projCd)
            q = q.filter(Factory_id=factory_id)
            q.delete()

            items = {'success': True}
    

        elif action == 'deleteUpdate':
            projCd = posparam.get('projCd')
            #factory_pk = posparam.get('factory_pk')
            q = CmProject.objects.filter(ProjCode=projCd)
            q = q.filter(Factory_id=factory_id)
            c = q.first()

            c.DelYn = 'Y'
            c.save()

            items = {'success': True}


        elif action == 'findDeletableProject':
            projCd = posparam.get('projCd')
            return findDeletableProject(projCd)


        elif action == 'findReferencedTablesInfo':
            exSupplierPk = CommonUtil.try_int(posparam.get('exSupplierPk'))
            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
			FROM (
			    select 'workorder.prjpk.lbl' as i18n_code
			    , count(*) as cnt
			    from cm_work_order
			    where proj_cd = %(proj_cd)s
                and factory_pk = %(factory_id)s
			) t
			left join cm_i18n t1 on t.i18n_code = t1.lang_code
			where t.cnt > 0
            '''
            dc = {}
            dc['projCd'] = projCd
            dc['factory_id'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'FindAllUser':
            keyword = gparam.get('keyword')

            sql = ''' 
            /* findAll [user-mapper.xml] */

            with cte as (

            SELECT t."User_id" as user_pk
                , cm_fn_user_nm(t."Name", t.del_yn) as user_nm
                , au.username as login_id
                -- , t.use_lang_cd
                -- , inl.lang_name  as use_lang_nm
                -- , t.user_password
                -- , t.salt
                , t."Depart_id" as dept_pk
                , d."Name" as dept_nm
                -- , t.job_class_pk
                -- , jc.job_class_nm
                -- , jc.wage_cost
                -- , t.user_type as user_type_cd
                -- , ut.code_nm as user_type_nm

            FROM   user_profile t
            inner join dept d on t."Depart_id"  = d.id
            inner join auth_user au on t."User_id" = au.id
            -- left outer join job_class jc on t.job_class_pk = jc.job_class_pk
            -- left outer join i18n_lang inl on t.use_lang_cd = inl.lang_type
            -- left outer join base_code ut on t.user_type = ut.code_cd and ut.code_grp_cd = 'USER_TYPE'
            where t.del_yn = 'N'

                and t.use_yn = 'Y'
            '''
            if keyword:
                sql += ''' 
                AND (
                        UPPER(d."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
                        OR
                        UPPER(t."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
                    )
                '''
            sql += '''
            )
            SELECT *
            FROM (
                table cte

                    order by dept_nm ASC 

                    -- limit 30 offset (1-1)*30

            ) sub
            RIGHT JOIN (select count(*) from cte) c(total_rows) on true
            WHERE total_rows != 0
            '''
            dc = {}
            dc['keyword'] = keyword

            items = DbUtil.get_rows(sql, dc)

    except Exception as ex:
        source = 'kmms/project : action-{}'.format(action)
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