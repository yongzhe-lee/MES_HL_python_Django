from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmStorLocAddr, CmWorkOrderSupplier

def storLocAddrList(context):
    '''
    api/kmms/storLocAddrList    자재보관위치

    findAll 전체목록조회
    insert
    delete
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    action = gparam.get('action', 'read') 

    def findDeletableExSupplier(exSupplierPk):
        q = CmWorkOrderSupplier.objects.filter(CmExSupplier_id=exSupplierPk)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action in ['findAll']:
            searchText = gparam.get('searchText')
            useYn = gparam.get('useYn')    
            equLoc = gparam.get('equLoc')

            sql = ''' 
                with cte as (

		            SELECT t.stor_loc_addr_pk
			            , l.loc_pk as location
			            , l.loc_pk
			            , t.loc_cd
			            , l.loc_nm
			            , t.loc_cell_addr
			            , t.rack_no
			            , t.level_no
			            , t.col_no
			            , t.out_unavail_yn
			            , t.insert_ts
			            , t.inserter_id
			            , t.inserter_nm
			            , t.update_ts
			            , t.updater_id
			            , t.updater_nm
			            , t.use_yn
                        , t.loc_cell_addr AS loc_cell_addr_nm
			            , '{"QR":"StorageAddr","Code":"' || t.loc_cd || ' ' || t.loc_cell_addr || '"}' as qrbarcode
		            FROM   cm_stor_loc_addr t
		            left outer join cm_location l on t.loc_cd = l.loc_cd
		            WHERE 1 = 1
                    '''     

            if searchText:
                sql += ''' AND ( UPPER(l.loc_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
                                 or UPPER(l.loc_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
                                 or UPPER(t.loc_cell_addr) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''

            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                    '''

            if equLoc:
                sql += ''' and l.loc_cd = %(equLoc)s
                    '''

            sql += ''' 
                        )
		            SELECT *
		            FROM (
			            table cte
		            ) sub
		            RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		            WHERE total_rows != 0
            '''

            dc = {}
            dc['searchText'] = searchText
            dc['useYn'] = useYn
            dc['equLoc'] = equLoc

            items = DbUtil.get_rows(sql, dc) 


        elif action in ['save']:
            id = CommonUtil.try_int(posparam.get('stor_loc_addr_pk'))
            loc_cd = posparam.get('loc_cd')
            rack_no = posparam.get('rack_no')
            level_no = posparam.get('level_no')
            col_no = posparam.get('col_no')
            out_unavail_yn = posparam.get('out_unavail_yn')
            use_yn = posparam.get('use_yn')

  
            if id:
                c = CmStorLocAddr.objects.get(id=id)

            else:
                c = CmStorLocAddr()

            c.LocCode = loc_cd
            c.RackNo = rack_no
            c.LevelNo = level_no
            c.ColNo = col_no
            c.OutUnavailYn = out_unavail_yn
            c.UseYn = use_yn

            c.DelYn = 'N'
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '자재보관위치의 정보가 저장되었습니다.'}


        elif action == 'delete':
            stor_loc_addr_pk = CommonUtil.try_int(posparam.get('stor_loc_addr_pk'))
            if not findDeletableExSupplier(stor_loc_addr_pk):
                CmStorLocAddr.objects.filter(id=stor_loc_addr_pk).delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/storLocAddrList : action-{}'.format(action)
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