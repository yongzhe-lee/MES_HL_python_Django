from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmLocation, CmLocMapMarker

def location(context):
    '''
    api/kmms/location    위치 정보
    김태영 작업중

    findAll
    findOne
    searchOne
    findDeletableLocation
    countBy
    countByLocCd 여기까지 
    findByLocAndUpLoc
    findByLocAndUpLocBuilding
    insert
    update
    delete
    deleteUpdate
    findReferencedTablesInfo
    getLocTreeList
    getComboLocation
    getLocations
    getLocFullTreeList
    getAnno
    searchChildren
    setAnnoMst
    updateAnnoMst
    getLocArea
    getLocLineByArea
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableLocation(locPk):
        sql = ''' select 1
		where exists (
			select 1 from cm_location 
            where up_loc_pk = %(locPk)s
			UNION ALL
			select 1 from cm_equipment 
            where loc_pk = %(locPk)s
			UNION ALL
			select 1 from cm_mtrl_inout 
            where inout_loc_cd = (select loc_cd from cm_location 
                where loc_pk =  %(locPk)s 
                )
		)
        '''
        dc = {}
        dc['locPk'] = locPk
        rows = DbUtil.get_rows(sql, dc)
        if len(rows) > 0:
            return 1
        else:
            return 0

    try:
        if action in ['findAll', 'searchOne']:
            useYn = gparam.get('useYn')
            spshopYn = gparam.get('spshopYn')
            plantYn = gparam.get('plantYn')
            locCd = gparam.get('locCd')
            locNm = gparam.get('locNm')
            upLocPk = gparam.get('upLocPk')
            rootInclude = gparam.get('rootInclude')
            isa95Class = gparam.get('isa95Class')
            searchText = gparam.get('searchText')

            sql = ''' SELECT t.loc_pk, t.loc_nm, t.loc_cd
		       , cm_fn_get_loc_plant_nm(t.loc_pk, t.factory_pk) as plant_nm
		       , t.up_loc_pk, ul.loc_cd as up_loc_cd, ul.loc_nm as up_loc_nm
		       , t.plant_yn, t.building_yn
		       , t.spshop_yn, t.out_order
		       , t.factory_pk as factory_pk
		       , s."Name" as factory_name
		       , t.loc_status
		       , b.code_nm AS loc_status_nm
               , t.isa95_class
		       , t.use_yn, t.del_yn
		       , t.insert_ts, t.inserter_id, t.inserter_nm      
               , t.update_ts, t.updater_id, t.updater_nm
		        , af."FileName" as file_org_nm
				, af."PhysicFileName" as file_stre_nm
				, af."ExtName" as file_ext
				, '' file_stre_cours
				, af.id as attach_pk
		    FROM cm_location t
		    left join cm_location ul on t.up_loc_pk = ul.loc_pk
		    left join factory s on t.factory_pk = s.id
		    left join cm_base_code b on t.loc_status = b.code_cd 
		    AND upper(b.code_grp_cd) = upper('LOC_STATUS')
		    left join attach_file af on af."DataPk" = t.loc_pk
		    and af."TableName" = 'cm_location'
		    -- and af.attach_type = 'LOC_IMG'
		    and af."AttachName" = 'LOC_IMG'
		    WHERE  t.del_yn = 'N'
            '''
            if factory_id:
                sql += ''' and t.factory_pk = %(factory_pk)s
                '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                '''
            if spshopYn:
                sql += ''' and t.spshop_yn = %(spshopYn)s
                '''
            if plantYn:
                sql += ''' and t.plant_yn = %(plantYn)s
                '''
            if locCd:
                sql += ''' AND UPPER(t.loc_cd) = UPPER(%(locCd)s)
                '''    
            if locNm:
                sql += ''' AND UPPER(t.loc_nm) = UPPER(%(locNm)s)
                '''                 
            if upLocPk:
                sql += ''' AND t.up_loc_pk = %(upLocPk)s
                '''
            if rootInclude:
                sql += ''' AND (cast(%(rootInclude)s as text) = 'Y')
                '''
            if searchText:
                sql += ''' AND ( UPPER(t.loc_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
                OR	UPPER(t.loc_cd) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
   			    )
                '''
            if isa95Class:
                sql += ''' AND UPPER(t.isa95_class) = UPPER(%isa95Class)s)
                '''   
            if action == 'searchOne':
                sql += ''' limit 1
                '''

            dc = {}
            dc['useYn'] = useYn
            dc['spshopYn'] = spshopYn
            dc['plantYn'] = plantYn
            dc['locCd'] = locCd
            dc['locNm'] = locNm
            dc['upLocPk'] = upLocPk
            dc['rootInclude'] = rootInclude
            dc['searchText'] = searchText
            dc['isa95Class'] = isa95Class
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            locPk = CommonUtil.try_int( gparam.get('locPk') )

            sql = ''' SELECT t.loc_pk, t.loc_nm, t.loc_cd
		       , cm_fn_get_loc_plant_nm(t.loc_pk, t.factory_pk) as plant_nm
		       , t.up_loc_pk, ul.loc_cd as up_loc_cd, ul.loc_nm as up_loc_nm
		       , t.plant_yn, t.building_yn
		       , t.spshop_yn, t.out_order
		       , t.factory_pk as factory_pk
		       , s."Name" as factory_name
		       , t.loc_status
		       , b.code_nm AS loc_status_nm
               , t.isa95_class
		       , t.use_yn, t.del_yn
		       , t.insert_ts, t.inserter_id, t.inserter_nm      
               , t.update_ts, t.updater_id, t.updater_nm
		        , af."FileName" as file_org_nm
				, af."PhysicFileName" as file_stre_nm
				, af."ExtName" as file_ext
				, '' file_stre_cours
				, af.id as attach_pk
		    FROM cm_location t
		    left join cm_location ul on t.up_loc_pk = ul.loc_pk
		    left join factory s on t.factory_pk = s.id
		    left join cm_base_code b on t.loc_status = b.code_cd 
		    AND upper(b.code_grp_cd) = upper('LOC_STATUS')
		    left join attach_file af on af."DataPk" = t.loc_pk
		    and af."TableName" = 'cm_location'
		    -- and af.attach_type = 'LOC_IMG'
		    and af."AttachName" = 'LOC_IMG'
		    WHERE  t.del_yn = 'N'
            and t.loc_pk = %(locPk)s
            '''

            dc = {}
            dc['locPk'] = locPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'countBy':
            locPk = CommonUtil.try_int( gparam.get('locPk') )

            sql = ''' select count(*) as cnt
		    from cm_location
            where t.loc_pk = %(locPk)s
            '''

            dc = {}
            dc['locPk'] = locPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'countByLocCd':
            exLocPk = CommonUtil.try_int( gparam.get('exLocPk') )
            delYn = gparam.get('delYn') 
            locCd = gparam.get('locCd') 

            sql = ''' SELECT count(*) as cnt
            FROM  cm_location t
            WHERE t.del_yn = %(delYn)s
            AND t.factory_pk = %(factory_pk)s
            AND t.loc_cd = %(locCd)s
            '''
            if exLocPk > 0:
                sql += ''' AND t.loc_pk <> %(exLocPk)s
                '''

            dc = {}
            dc['exLocPk'] = exLocPk
            dc['delYn'] = delYn
            dc['locCd'] = locCd
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'findByLocAndUpLoc':
            exLocPk = CommonUtil.try_int( gparam.get('exLocPk') )
            isa95Class = gparam.get('isa95Class') 
            rootInclude = gparam.get('rootInclude') 
            useYn = gparam.get('useYn') 
            searchText = gparam.get('searchText') 
            upLocPk = gparam.get('upLocPk') 

            sql = ''' with cte as (
			    SELECT t.loc_pk
				, t.loc_nm
				, t.loc_cd
				, null as up_loc_pk
				, null as up_loc_cd
				, null as up_loc_nm
				, t.plant_yn
				, t.building_yn
				, t.spshop_yn
				, t.out_order
		        , t.factory_pk
		        -- , s.factory_name
				, t.use_yn
				, t.del_yn
                , t.isa95_class
			    FROM cm_location t
		        WHERE t.up_loc_pk is null
            '''
            if factory_id:
                sql += ''' and t.factory_pk = %(factory_pk)s
                '''
            if isa95Class:
                sql += ''' and t.isa95_class = %(isa95_class)s
                '''
            sql += ''' AND %(rootInclude)s = 'Y'
			    UNION ALL
			    SELECT t.loc_pk
				, t.loc_nm
				, t.loc_cd
				, t2.loc_pk as up_loc_pk
				, t2.loc_cd as up_loc_cd
				, t2.loc_nm as up_loc_nm
				, t.plant_yn
				, t.building_yn
				, t.spshop_yn
				, t.out_order
		        , t.factory_pk
		        -- , s2.factory_name
				, t.use_yn
				, t.del_yn
                , t.isa95_class
			    FROM cm_location t
			    left JOIN cm_location t2 on t.up_loc_pk = t2.loc_pk
			    WHERE t.del_yn = 'N'
                '''
            if factory_id:
                sql += ''' and t.factory_pk = %(factory_pk)s
                '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                '''
            if searchText:
                sql += ''' AND (
					UPPER(t.loc_nm) LIKE CONCAT('%',UPPER(%(searchText)s,'%')
					OR
					UPPER(t.loc_cd) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
	   			)
                '''
            if upLocPk:
                sql += ''' AND t2.loc_pk = %(upLocPk)s
                '''
            if isa95Class:
                sql += ''' and t.isa95_class = %(isa95Class)s
                '''
            sql += ''' )
		    SELECT cte.*
                , cm_fn_get_loc_plant_nm(cte.loc_pk, factory_pk) as plant_nm
		    FROM cte
                '''

            dc = {}
            dc['exLocPk'] = exLocPk
            dc['isa95Class'] = isa95Class
            dc['rootInclude'] = rootInclude
            dc['useYn'] = useYn
            dc['searchText'] = searchText
            dc['upLocPk'] = upLocPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'findByLocAndUpLocBuilding':
            #exLocPk = CommonUtil.try_int( gparam.get('exLocPk') )
            #isa95Class = gparam.get('isa95Class') 
            #rootInclude = gparam.get('rootInclude') 
            useYn = gparam.get('useYn') 
            searchText = gparam.get('searchText') 
            upLocPk = gparam.get('upLocPk') 

            sql = ''' with cte as (
			    SELECT t.loc_pk
				    , t.loc_nm
				    , t.loc_cd
				    , cm_fn_get_loc_plant_nm(t.loc_pk, t.factory_pk) as plant_nm
				    , t2.loc_pk as up_loc_pk
				    , t2.loc_cd as up_loc_cd
				    , t2.loc_nm as up_loc_nm
				    , t.plant_yn
				    , t.building_yn
				    , t.spshop_yn
				    , t.out_order
		            , t.factory_pk
		          --  , s2.factory_name
				    , t.use_yn
				    , t.del_yn
                    , t.isa95_class
			    FROM cm_location t
			    left JOIN cm_location t2 on t.up_loc_pk = t2.loc_pk
			    WHERE t.del_yn = 'N'
                '''
            if factory_id:
                sql += ''' and t.factory_pk = %(factory_pk)s
                '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                '''
            if searchText:
                sql += ''' AND (
					UPPER(t.loc_nm) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
					OR
					UPPER(t.loc_cd) LIKE CONCAT('%',UPPER(%(searchText)s),'%')
	   			)
                '''
            sql += ''' AND ( t.loc_pk <> %(upLocPk)s
					AND t.loc_pk IN ( select loc_pk from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x where %(upLocPk)s = path_info_pk)
				)
			order by t.out_order, t.loc_nm
		    )
		    SELECT *
		    FROM cte
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['searchText'] = searchText
            dc['upLocPk'] = upLocPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action in ['insert', 'update']:
            locPk = CommonUtil.try_int(posparam.get('loc_pk'))
            upLocPk = CommonUtil.try_int(posparam.get('up_loc_pk'))
            locNm = posparam.get('loc_nm')
            locCd = posparam.get('loc_cd')
            plantYn = posparam.get('plant_yn')
            buildingYn = posparam.get('building_yn')
            spshopYn = posparam.get('spshop_yn')
            outOrder = 1
            locStatus = posparam.get('loc_status')
            isa95Class = posparam.get('isa95_class')
            useYn = posparam.get('use_yn')
  
            if locPk:
                c = CmLocation.objects.get(LocPk=locPk)

            else:
                c = CmLocation()

            c.LocName = locNm
            c.LocCode = locCd
            c.Parent_id = upLocPk
            c.PlantYn = plantYn
            c.BuildingYn = buildingYn
            c.SpshopYn = spshopYn
            c.OutOrder = outOrder
            c.LocStatus = locStatus
            c.Isa95Class = isa95Class
            c.Factory_id = factory_id
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '위치의 정보가 수정되었습니다.'}


        elif action == 'delete':
            locPk = CommonUtil.try_int(posparam.get('loc_pk'))
            if not findDeletableLocation(locPk):
                CmLocation.objects.filter(LocPk=locPk).delete()

            items = {'success': True}
    

        elif action == 'deleteUpdate':
            locPk = CommonUtil.try_int(posparam.get('locPk'))
            c = CmLocation.objects.get(id=locPk)
            c.DelYn = 'Y'
            c.save()

            items = {'success': True}


        elif action == 'findDeletableLocation':
            locPk = CommonUtil.try_int(posparam.get('locPk'))
            return findDeletableLocation(locPk)


        elif action == 'findReferencedTablesInfo':
            locPk = CommonUtil.try_int(posparam.get('locPk'))

            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
			 FROM (
			     select 'equipment.locpk.lbl' as i18n_code, count(*) as cnt 
                 from cm_equipment
			     where loc_pk = %(locPk)s 
                 and del_yn = 'N'
			 ) t
			 left join cm_i18n t1 on t.i18n_code = t1.lang_code
			 where t.cnt > 0
            '''
            dc = {}
            dc['locPk'] = locPk

            items = DbUtil.get_row(sql, dc)

   # 사용안함
   #      elif action == 'getLocTreeList':
   #          locPk = CommonUtil.try_int(gparam.get('locPk'))
   #          subCountYn = gparam.get('subCountYn')
   #          useYn = gparam.get('useYn')

   #          sql = ''' select vsl.id as loc_pk
			# , ul.loc_pk as up_loc_pk
   #          '''
   #          if subCountYn != 'Y':
   #              sql += ''' , vsl."label" as loc_nm
   #              '''
   #          else:
   #              sql += ''' , case when coalesce(vsl.sub_count, 0) > 0
			# 			      then concat(vsl."label", '(', vsl.sub_count, ')') else vsl."label" end as loc_nm
   #              '''
   #          sql += ''', vsl.cd as loc_cd
   #          '''
   #          if factory_id:
   #              sql += ''', 1 as factory_pk
   #             --  , (select "Name" from factory where id = %(factory_pk)s as factory_name
   #             '''
   #          else:
   #              sql += ''' , vsl.factory_pk 
   #           --   , (select "Name" from factory where id = vsl.factory_pk) as factory_name
   #           '''

   #          sql += ''' , cast('' as character varying(30)) as plant_cd
			# , l.plant_yn, l.building_yn, l.spshop_yn
			# , vsl.lvl - 1 as lev
			# , l.del_yn, l.use_yn
			# , l.insert_ts, l.inserter_id, l.inserter_nm
			# , l.update_ts, l.updater_id	, l.updater_nm
			# , vsl.sub_count
			# , vsl.path_info
			# , ul.loc_cd  as up_loc_cd
			# , vsl.lvl_type
   #          , l.isa95_class
   #          , coalesce(leq.loc_equip_count, 0) as loc_equip_count
		 #    FROM (select * from cm_fn_get_site_loc_tree(%(factory_pk)s)) vsl
   #          LEFT JOIN cm_location ul on vsl.up_cd = ul.loc_cd 
   #          and vsl.factory_pk = ul.factory_pk
   #          LEFT JOIN cm_location l on vsl.id = l.loc_pk 
   #          and vsl.factory_pk = l.factory_pk
   #          LEFT JOIN (
			#     SELECT loc_pk as equip_loc_pk, count(*) as loc_equip_count
			#     FROM cm_equipment
			#     WHERE del_yn = 'N' 
			#     and use_yn = 'Y'
   #              '''
   #          if factory_id:
   #              sql += ''' AND factory_pk = %(factory_pk)s
   #              '''
   #          sql += ''' AND loc_pk is not null
			#     GROUP BY loc_pk
		 #    ) leq on leq.equip_loc_pk = vsl.id
		 #    WHERE 1 = 1
   #          '''
   #          if factory_id:
   #              sql += ''' AND vsl.factory_pk = %(factory_pk)s
   #              AND vsl.lvl_type = 'location'
   #              '''
   #          if useYn:
   #              sql += ''' AND l.use_yn = %(useYn)s
   #              '''
   #          sql += ''' order by vsl.path_info_ordr
   #          '''
   #          dc = {}
   #          dc['subCountYn'] = subCountYn
   #          dc['useYn'] = useYn
   #          dc['factory_pk'] = factory_id

   #          items = DbUtil.get_rows(sql, dc)

        elif action == 'getComboLocation':
            plantYn = gparam.get('plantYn')
            isa95Class = gparam.get('isa95Class')

            sql = ''' select l.loc_cd, l.loc_nm
		    from cm_location l
		    where 1=1
            '''
            if plantYn:
                sql += ''' and l.plant_yn = %(plantYn)s
                '''
            if isa95Class:
                sql += ''' and l.isa95_class = %(isa95Class)s
                '''
            if factory_id:
                sql += ''' and l.factory_pk = %(factory_pk)s
                '''
            sql += ''' order by l.out_order, l.loc_cd, l.loc_nm
            '''
            dc = {}
            dc['plantYn'] = plantYn
            dc['isa95Class'] = isa95Class
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'getLocations':
            plantYn = gparam.get('plantYn')
            isa95Class = gparam.get('isa95Class')

            sql = ''' SELECT t.loc_pk, t.loc_nm, t.loc_cd
		    , cm_fn_get_loc_plant_nm(t.loc_pk,t.factory_pk) as plant_nm
		    , t.up_loc_pk, ul.loc_cd as up_loc_cd, ul.loc_nm as up_loc_nm
			, t.factory_pk
			, s."Name" as factory_name
		    , t.plant_yn, t.building_yn, t.spshop_yn
		    , t.out_order
		    , t.use_yn, t.del_yn
		    , count(distinct eq.equip_cd) as equip_cnt
            , t.isa95_class
		    FROM cm_location t
		    left join cm_location ul on t.up_loc_pk = ul.loc_pk
		    left join cm_equipment eq on t.loc_pk = eq.loc_pk 
		    and eq.del_yn = 'N'
		    left join factory s on t.factory_pk = s.id
		    where t.factory_pk = %(factory_pk)s
		    group by t.loc_pk, t.loc_nm, t.loc_cd
			   , t.factory_pk, s."Name"
		       , t.up_loc_pk, ul.loc_cd, ul.loc_nm
		       , t.plant_yn, t.building_yn, t.spshop_yn
		       , t.out_order
		       , t.use_yn, t.del_yn
               , t.isa95_class
            '''
            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'getLocFullTreeList':
            companyName = gparam.get('companyName')
            showCodeYn = gparam.get('showCodeYn')
            showCodeYn = gparam.get('showCodeYn')
            subCountYn = gparam.get('subCountYn')
            useYn = gparam.get('useYn')

            sql = ''' SELECT null as loc_pk
			, null as up_loc_pk
            , %(companyName)s as loc_nm
			, 'COMPANY' as loc_cd
			, null as up_loc_cd
			, null::integer as factory_pk
			, null as factory_name
			, null as plant_cd
			, 'N' as plant_yn, 'N' as building_yn, 'N' as spshop_yn
			, 1 as lev
			, 'N' as del_yn, 'Y' as use_yn             
            , null as isa95_class
			, null as insert_ts, null as inserter_id, null as inserter_nm
			, null as update_ts, null as updater_id, null as updater_nm
			, 1 as sub_count 
			, ARRAY[''::text] as path_info
            , ARRAY[''::text] as path_info_desc
			, 'company' as lvl_type 
			, null as file_org_nm, null as file_stre_nm 
			, null as file_ext 
			, null as file_stre_cours 
			, null::integer as attach_pk
            UNION ALL
		    select vsl.id as loc_pk
			    , case when vsl.lvl_type = 'sites' then null else ul.loc_pk end as up_loc_pk
                '''
            if showCodeYn == 'Y':
                if subCountYn == 'Y':
                    sql += ''', case when vsl.lvl_type = 'sites' then vsl."label"
                                 when coalesce(vsl.sub_count, 0) > 0 then vsl."cd" || ' : ' ||  vsl."label" || '(' || vsl.sub_count || ')' 
                                else vsl."cd" || ' : ' || vsl."label" end as loc_nm
                    '''
                else:
                    sql += ''', vsl."cd" || ' : ' || vsl."label" as loc_nm
                    '''
            else:
                if subCountYn == 'Y':
                    sql += ''', case when vsl.lvl_type = 'sites' then vsl."label"
       			            when coalesce(vsl.sub_count, 0) > 0	then vsl."label" || '(' || vsl.sub_count || ')'
       			            else vsl."label" end as loc_nm
                    '''
                else:
                    sql += ''', vsl."label" as loc_nm 
                    '''
            sql += ''', vsl.cd as loc_cd
                , case when vsl.lvl_type = 'sites' then 'COMPANY' else vsl.up_cd end as up_loc_cd
                , vsl.factory_pk
                , (select "Name" from factory where id = vsl.factory_pk) as factory_name
			    , cast('' as character varying(30)) as plant_cd
			    , l.plant_yn, l.building_yn, l.spshop_yn
                , vsl.lvl + 1 as lev
			    , l.del_yn, l.use_yn 
                , l.isa95_class
			    , l.insert_ts, l.inserter_id, l.inserter_nm
			    , l.update_ts, l.updater_id, l.updater_nm
			    , vsl.sub_count 
			    , vsl.path_info
                , vsl.path_info_desc
			    , vsl.lvl_type 
			    , af."PhysicFileName" as file_org_nm
			    , af."FileName" as file_stre_nm 
			    , af."ExtName" as file_ext
			    , '' as file_stre_cours 
			    , af.id as attach_pk
		    from (select * from cm_fn_get_site_loc_tree(1)) vsl
            left join cm_location ul on vsl.up_cd = ul.loc_cd 
            and vsl.factory_pk = ul.factory_pk
            left join cm_location l on vsl.id = l.loc_pk 
            and vsl.factory_pk = l.factory_pk
            left join attach_file af on vsl.id = af.id 
            and af."TableName" = 'cm_location'
            and af."AttachName" = 'LOC_IMG'
		    WHERE 1 = 1
            '''
            if useYn:
                sql += ''' and ( vsl.lvl_type = 'sites' or (vsl.lvl_type = 'location' and l.use_yn = %(useYn)s ) )
                '''
            sql += ''' and vsl.factory_pk = %(factory_pk)s
		    order by path_info
            '''
            dc = {}
            dc['companyName'] = companyName
            dc['showCodeYn'] = showCodeYn
            dc['subCountYn'] = subCountYn
            dc['useYn'] = useYn
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'getAnno':
            locCd = gparam.get('locCd')
            markerType = gparam.get('markerType')

            sql = ''' select loc_cd
	        , marker_type, marker_info
		    from cm_loc_map_marker
		    where loc_cd = %(locCd)s
            '''
            if markerType:
                sql += ''' and marker_type = %(markerType)s
                '''
            dc = {}
            dc['locCd'] = locCd
            dc['markerType'] = markerType

            items = DbUtil.get_rows(sql, dc)

        elif action == 'searchChildren':
            locCd = gparam.get('locCd')
            markerType = gparam.get('markerType')

            sql = ''' select loc_pk, loc_nm
			from cm_location
			where up_loc_pk = %(locCd)s
			and use_yn= 'Y'
			order by loc_pk asc
            '''
            dc = {}
            dc['locCd'] = locCd
    
            items = DbUtil.get_rows(sql, dc)

        elif action == 'setAnnoMst':
            locCd = posparam.get('locCd')
            markerType = posparam.get('markerType')
            markerInfo = posparam.get('markerInfo')

            o = CmLocMapMarker()
            o.LocCode = locCd
            o.MarkerType = markerType
            o.MarkerInfo = markerInfo
            o.set_audit(user)
            o.save()

        elif action == 'updateAnnoMst':
            locCd = posparam.get('locCd')
            markerType = posparam.get('markerType')
            markerInfo = posparam.get('markerInfo')

            q = CmLocMapMarker.objects.filter(LocCode=locCd)
            q = q.filter(MarkerType=markerType)
            o = q.first()

            o.MarkerInfo = markerInfo
            o.set_audit(user)
            o.save()


        elif action == 'getLocArea':
            ''' 위치 목록중 isa-95class=AREA)
            '''

            sql = ''' SELECT T.ID AS LOC_PK
            , T.CD AS LOC_CD
            , T.LABEL AS LOC_NM
            , T.UP_ID AS UP_LOC_PK
            , T.LVL AS LEV
            , T.PATH_INFO_PK
            , T.SUB_COUNT
            FROM (SELECT * from cm_fn_get_loc_area_line(%(factory_pk)s, NULL)) T
            WHERE T.LVL_TYPE = 'area'
            '''
            dc = {}
            dc['factory_pk'] = factory_id
    
            items = DbUtil.get_rows(sql, dc)


        elif action == 'getLocLineByArea':
            ''' Area별 line목록 조회
            '''
            locAreaPk = CommonUtil.try_int(gparam.get('locAreaPk'))

            sql = ''' SELECT T.ID AS LOC_PK
            , T.CD AS LOC_CD
            , T.LABEL AS LOC_NM
            , T.UP_ID AS UP_LOC_PK
            , T.LVL AS LEV
            , T.PATH_INFO_PK
            , T.SUB_COUNT
            FROM (SELECT * from cm_fn_get_loc_area_line(%(factory_pk)s, NULL)) T
            WHERE T.LVL_TYPE = 'line'
            and T.up_id = %(locAreaPk)s
            '''
            dc = {}
            dc['locAreaPk'] = locAreaPk
            dc['factory_pk'] = factory_id
    
            items = DbUtil.get_rows(sql, dc)


    except Exception as ex:
        source = 'kmms/location : action-{}'.format(action)
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