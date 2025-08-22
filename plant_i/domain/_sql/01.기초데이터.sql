
---- TRUNCATE TABLE 명령으로 모든 테이블 삭제
/*

DO $$
DECLARE
    r record;
	v_cnt int;
BEGIN
    FOR r IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
		and tablename like 'cm_%'
		and tablename not in 
			('cm_base_code',
			'cm_base_code_grp',
			'cm_chk_item_template',
			'cm_equip_category',
			'cm_holiday_custom',
			'cm_holiday_info',
			'cm_import_rank',
			'cm_reliab_codes',
			'cm_site_config',
			'cm_sites')
		ORDER BY tablename ASC       -- ★ 정렬 추가
    LOOP
		-- 동적 SQL 실행 결과를 v_cnt로 받기
        EXECUTE format('SELECT count(*) FROM %I', r.tablename) INTO v_cnt;
		if v_cnt > 0 then
			RAISE NOTICE 'table: %, count: %', r.tablename, v_cnt;
			-- EXECUTE format('TRUNCATE TABLE %I RESTART IDENTITY CASCADE', r.table_name);
			-- DELETE 실행
			-- EXECUTE format('DELETE FROM %I', r.tablename);
		end if;			
		
    END LOOP;
END $$;

*/

-- 기초 데이터 insert 구문
-- user_group
SELECT setval('user_group_id_seq', (SELECT MAX(id) FROM user_group), true);
insert into user_group(id, "Code", "Name", "Disabled", "_created")
values
(1, 'dev', 'Developer', false, now() ),
(2, 'admin', 'Admin', false, now() ),
(3, 'user', 'User', false, now() );
alter SEQUENCE user_group_id_seq restart WITH 4;

 -- auth_user
insert into auth_user(id, username, password, is_superuser, first_name, last_name, email, is_staff, is_active, date_joined)
values
(1, 'yullin', 'pbkdf2_sha256$150000$kBud3jic1o9f$lfi+BlZbc3x7GVXbSdqn9hmfu2pRSWt8r4QPe2IiAcs=', true, '','','yullin@yullin.com', true, true, now()),
(2, 'dev', 'pbkdf2_sha256$150000$kBud3jic1o9f$lfi+BlZbc3x7GVXbSdqn9hmfu2pRSWt8r4QPe2IiAcs=', false, '개발자','','dev@yullin.com', true, true, now()),
(3, 'admin', 'pbkdf2_sha256$150000$kBud3jic1o9f$lfi+BlZbc3x7GVXbSdqn9hmfu2pRSWt8r4QPe2IiAcs=', false, '관리자','','admin@yullin.com', true, true, now())
;
alter SEQUENCE auth_user_id_seq restart WITH 4;
   
-- user_profile
insert into user_profile("User_id", "Name", "UserGroup_id", lang_code, del_yn, use_yn, "_created", "_modified")
values
(1, '위존', null, 'ko-KR', 'N','Y',now(), now() ), 
(2,'개발자', 1, 'ko-KR', 'N','Y',now(), now() ),
(3,'관리자', 2, 'ko-KR', 'N','Y',now(), now() );

--site
alter SEQUENCE site_id_seq restart WITH 1;
insert into site(id, "Name", "Code", "_created") values(1, 'HL클레무브송도', 'hlklemove', now());

--factory
insert into factory ("Code", "Name", "Site_id", "_created") values('f1', 'HL클레무브송도공장', 1, now());

-- sys_code
alter SEQUENCE sys_code_id_seq restart WITH 1;
INSERT INTO sys_code ("CodeType","Code","Value","Description","_ordering","_status","_created","_modified","_creater_id","_modifier_id") VALUES
	 ('bom_type','manufacturing','제조BOM','BOM구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('bom_type','engineering','설계BOM','BOM구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('company_type','purchase','매입처','업체구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('company_type','sale','매출처','업체구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('company_type','outsourcing','외주사','업체구분',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('company_type','equip-maker','설비제작사','업체구분',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('company_type','sale-purchase','매입매출처','업체구분',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('coverage','process','공정별','적용범위. 공정에만 적용',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('coverage','all','전체','적용범위. 전체에 적용',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equipment_type','manufacturing','생산','설비구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equipment_type','etc','기타','설비구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_asset_yn','Y','자산성','설비자산성여부',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_asset_yn','N','소모성','설비자산성여부',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_maint_type','prevention','예방정비','설비정비구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_maint_type','failure','고장정비','설비정비구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_run_state','run','가동','설비가동상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_run_state','stop','비가동','설비가동상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_run_type','auto','자동입력','설비가동구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_run_type','manual','수입력','설비가동구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_state','normal','정상','설비상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_state','failure','고장','설비상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('equip_state','checking','점검중','설비상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('form_type','hmi','HMI양식','양식구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('form_type','excel','엑셀양식','양식구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('form_type','html','HTML양식','양식구분',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('form_type','file','파일','양식구분',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('job_state','planned','계획','작업실적상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('job_state','ordered','지시','작업실적상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('job_state','working','작업중','작업실적상태',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('job_state','finished','완료','작업실적상태',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('job_state','stopped','중지','작업실적상태',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('job_state','canceled','취소','작업실적상태',6,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('job_state','waiting','대기','제품생산상태',7,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('hierarchy_level','area','Area','위치레벨',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('hierarchy_level','workcenter','워크센터','위치레벨',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('inout_state','waiting','미확인','자재입고상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('inout_state','confirmed','확인','자재입고상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('inout_state','canceled','취소','자재입고상태',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('inout_type','in','입고','입출구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('inout_type','out','출고','입출구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('input_type','order_in','구매입고','발주구매입고',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('input_type','produced_in','생산입고','제품,반제품 생산 후 입고',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('input_type','move_in','이동입고','창고 이동으로 입고',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('input_type','gap_in','실사잉여','재고실사 후 잉여량 입고',6,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('input_type','return_in','반품입고','반품입고',7,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('input_type','etc_in','기타입고','기타',8,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('lang_code','ko-KR','한국어','언어구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('lang_code','en-US','영어','언어구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_order_state','registered','등록','자재발주 상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_order_state','approved','승인','자재발주 상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_order_state','rejected','반려','자재발주 상태',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_proc_input_state','requested','요청','자재공정투입상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_proc_input_state','executed','실행','자재공정투입상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_requ_mat_type','product','제품','품목필요량 품목구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_requ_mat_type','semi','반제품','품목필요량 품목구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_requ_mat_type','material','원부자재','품목필요량 품목구분',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_type','product','제품','품목구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_type','semi','반제품','품목구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_type','raw_mat','원재료','품목구분',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_type','sub_mat','부자재','품목구분',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('mat_type','sangpum','상품','품목구분',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('output_type','consumed_out','생산투입출고','생산투입 위해 출고',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('output_type','shipped_out','제품출하출고','제품출하 출고',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('output_type','move_out','이동출고','창고 이동으로 출고',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('output_type','gap_out','실사부족','재고실사 후 부족량 입고',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('output_type','etc_out','기타출고','기타',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('output_type','disposal_out','폐기','폐기',6,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('output_type','used_out','소모품사용','폐기',7,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('person_type','production','작업자','작업자구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('person_type','sales','영업담당자','작업자구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('person_type','office','사무직','작업자구분',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('plan_yn','Y','계획','계획비계획구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('plan_yn','N','비계획','계획비계획구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('prod_week_term_state','none','미계획','',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('prod_week_term_state','product','제품확정','',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('prod_week_term_state','semi','반제품확정','',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('prod_week_term_state','material','원부자재확정','',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('result_type','N','수치값','결과값유형',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('result_type','S','선택형','결과값유형',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('result_type','D','서술형','결과값유형',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('haccp_result_type','N','수치값','결과값유형',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('haccp_result_type','YN','YesNo','결과값유형',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('shipment_state','ordered','지시','출하상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('shipment_state','shipped','출하','출하상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('spec_type','x','규격없음','규격유형',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('spec_type','upper','상한이하','규격유형',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('spec_type','low','하한이상','규격유형',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('spec_type','range','범위','규격유형',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('spec_type','just','정성규격','규격유형',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('standard_time_unit','minute','분','표준시간단위',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('standard_time_unit','second','초','표준시간단위',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('standard_time_unit','hour','시간','표준시간단위',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('standard_time_unit','day','일','표준시간단위',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('storehouse_type','product','제품창고','창고구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('storehouse_type','semi','반제품창고','창고구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('storehouse_type','material','자재창고','창고구분',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('storehouse_type','defect','부적합품창고','창고구분',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('storehouse_type','process','공정창고','창고구분',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('storehouse_type','scrap','스크랩창고','창고구분',6,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('story_board_type','menu','메뉴','스토리보드 항목구분',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('story_board_type','hmi','HMI양식','스토리보드 항목구분',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_state','received','수주','수주상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_state','ordered','지시','수주상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_state','planned','계획진행','수주상태',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_state','shipped','납품','수주상태',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_state','canceled','취소','수주상태',5,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_state','holding','검토중','수주상태',6,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_type','sales','외부수주','외부수주',10,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('suju_type','plan','내부계획','내부계획',20,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_class','import','수입검사','검사종류',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_class','process','공정검사','검사종류',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_class','product','제품검사','검사종류',3,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_class','shipping','출하검사','검사종류',4,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_result_state','ordered','지시','검사결과상태',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_result_state','finished','완료','검사결과상태',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_type','use_item_master','검사항목사용','검사유형',1,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('test_type','no_use_item_master','검사항목미사용','검사유형',2,NULL,'2024-11-28 08:28:13.952111+09',NULL,NULL,NULL),
	 ('result_type','Y','날짜형','결과값유형',0,NULL,'2025-01-07 10:52:08.053434+09','2025-01-07 10:52:08.053434+09',NULL,NULL),
	 ('result_type','T','시간형','결과값유형',0,NULL,'2025-01-07 10:52:08.133019+09','2025-01-07 10:52:08.133019+09',NULL,NULL),
	 ('result_type','X','결과없음','결과값유형',0,NULL,'2025-01-07 10:52:08.139035+09','2025-01-07 10:52:08.139035+09',NULL,NULL),
	 ('prod_type','product','제품','제품유형',0,NULL,'2025-01-07 10:52:08.150229+09','2025-01-07 10:52:08.150229+09',NULL,NULL),
	 ('prod_type','semi','반제품','제품유형',0,NULL,'2025-01-07 10:52:08.155001+09','2025-01-07 10:52:08.155001+09',NULL,NULL),
	 ('prod_type','raw_mat','원재료','제품유형',0,NULL,'2025-01-07 10:52:08.160374+09','2025-01-07 10:52:08.160374+09',NULL,NULL),
	 ('comp_kind','C','고객','회사구분',0,NULL,'2025-01-07 10:52:08.166064+09','2025-01-07 10:52:08.166064+09',NULL,NULL),
	 ('comp_kind','S','공급처','회사구분',0,NULL,'2025-01-07 10:52:08.171064+09','2025-01-07 10:52:08.171064+09',NULL,NULL),
	 ('smp_point_cls','Tank','Tank','채취장소유형',0,NULL,'2025-01-07 10:52:08.176729+09','2025-01-07 10:52:08.176729+09',NULL,NULL),
	 ('smp_point_cls','Silo','Silo','채취장소유형',0,NULL,'2025-01-07 10:52:08.181911+09','2025-01-07 10:52:08.181911+09',NULL,NULL),
	 ('inst_state','IS01','정상','시험기기상태',0,NULL,'2025-01-07 10:52:08.187609+09','2025-01-07 10:52:08.187609+09',NULL,NULL),
	 ('inst_state','IS02','고장','시험기기상태',0,NULL,'2025-01-07 10:52:08.19449+09','2025-01-07 10:52:08.19449+09',NULL,NULL),
	 ('inst_state','IS03','수리중','시험기기상태',0,NULL,'2025-01-07 10:52:08.200402+09','2025-01-07 10:52:08.200402+09',NULL,NULL),
	 ('inst_state','IS04','폐기','시험기기상태',0,NULL,'2025-01-07 10:52:08.205893+09','2025-01-07 10:52:08.205893+09',NULL,NULL),
	 ('test_unit_type','LGTH','길이','측정단위종류',0,NULL,'2025-01-07 10:52:08.272947+09','2025-01-07 10:52:08.272947+09',NULL,NULL),
	 ('test_unit_type','CONC','농도','측정단위종류',0,NULL,'2025-01-07 10:52:08.279643+09','2025-01-07 10:52:08.279643+09',NULL,NULL),
	 ('test_unit_type','WT','무게','측정단위종류',0,NULL,'2025-01-07 10:52:08.286173+09','2025-01-07 10:52:08.286173+09',NULL,NULL),
	 ('test_unit_type','DENS','밀도','측정단위종류',0,NULL,'2025-01-07 10:52:08.291163+09','2025-01-07 10:52:08.291163+09',NULL,NULL),
	 ('test_unit_type','VOL','부피','측정단위종류',0,NULL,'2025-01-07 10:52:08.298038+09','2025-01-07 10:52:08.298038+09',NULL,NULL),
	 ('test_unit_type','TIME','시간','측정단위종류',0,NULL,'2025-01-07 10:52:08.305038+09','2025-01-07 10:52:08.305038+09',NULL,NULL),
	 ('test_unit_type','P','압력','측정단위종류',0,NULL,'2025-01-07 10:52:08.310118+09','2025-01-07 10:52:08.310118+09',NULL,NULL),
	 ('test_unit_type','E','기타','측정단위종류',0,NULL,'2025-01-07 10:52:08.317404+09','2025-01-07 10:52:08.317404+09',NULL,NULL);


--라인정보
alter SEQUENCE line_id_seq restart WITH 1;
insert into line ("Code", "Name", _created) values('PCU-01-01', 'HPC#1' , now());
insert into line ("Code", "Name", _created) values('SMT-01', 'SMT#1' , now());
insert into line ("Code", "Name", _created) values('SMT-02', 'SMT#2' , now());
insert into line ("Code", "Name", _created) values('SMT-03', 'SMT#3' , now());
insert into line ("Code", "Name", _created) values('SMT-04', 'SMT#4' , now());


alter SEQUENCE dept_id_seq restart WITH 1;
INSERT INTO dept ("Code","Name","UpDept_id","UpDeptCode","ReqDivCode","LabYN","MfgYN","RoleNo","UseYN","DelYN","ApplyYN",business_yn,tpm_yn, team_yn,"_status","_created","_modified","_creater_id","_modifier_id","Site_id") VALUES
	 ('SFT','SF사업팀',6,'SFS','test','N','Y',1,'Y','N','Y','N','N','N',NULL,'2024-12-23 16:05:20.795725+09','2024-12-23 16:15:20.992958+09',3,3,1),
	 ('FIT','FI팀',7,'DXS','','N','Y',1,'Y','N','Y','N','N','N',NULL,'2024-12-23 16:00:54.927959+09','2025-01-07 15:12:14.068472+09',3,3,1),
	 ('SFS','SF사업부',NULL,NULL,NULL,NULL,NULL,NULL,'Y','N','Y','N','N','N',NULL,'2024-12-23 16:00:54.927+09',NULL,3,NULL,1),
	 ('DXS','DX사업부',NULL,NULL,NULL,NULL,NULL,NULL,'Y','N','Y','N','N','N',NULL,'2024-12-23 16:00:54.927+09',NULL,3,NULL,1),
	 ('SFD','SF개발팀',6,'SFS',NULL,NULL,NULL,NULL,'Y','N','Y','N','N','N',NULL,'2024-12-23 16:00:54.927+09',NULL,3,NULL,1),
	 ('DTT','DT사업팀',6,'SFS',NULL,NULL,NULL,NULL,'Y','N','Y','N','N','N',NULL,'2024-12-23 16:00:54.927+09',NULL,3,NULL,1),
	 ('','테스트 부서',NULL,NULL,NULL,'N','N',NULL,'Y','N','N','N','N','N',NULL,'2025-02-12 17:17:25.638021+09','2025-02-12 17:17:25.638021+09',NULL,NULL,NULL);

--das_server
alter SEQUENCE das_server_id_seq restart WITH 1;
insert into das_server (id, "Code", "Name", "IPAddress","Type","_status", "_created") values (1,'DAS_HPC1', 'DAS HPC#1전용', '10.226.234.30', 'WIN', 'a', now());
insert into das_server (id, "Code", "Name", "IPAddress","Type","_status", "_created") values(2, 'DAS_SMT4', 'DAS SMT#4전용', '10.226.234.31', 'WIN', 'a', now());


/* 메뉴관련 */
truncate table menu_folder cascade;

--메뉴폴더
--alter SEQUENCE menu_folder_id_seq restart WITH 28;
INSERT INTO menu_folder (id,"FolderName","IconCSS",_order,_status,_created,_modified,_creater_id,_modifier_id,"Parent_id") VALUES
	 (1,'대시보드','team_dashboard',100,NULL,'2024-11-25 15:00:19.159507+09','2025-01-15 13:14:32.503551+09',1,NULL,NULL),
	 (2,'AAS관리','description',200,NULL,'2024-11-22 17:01:44.576807+09','2025-01-15 15:47:30.788452+09',1,NULL,NULL),
	 (3,'기준정보','contract_edit',300,NULL,'2024-11-22 17:01:44.576807+09','2025-01-15 15:11:37.48031+09',1,NULL,NULL),
	 (4,'설비관리','construction',400,NULL,'2024-11-22 17:01:51.726933+09','2025-01-15 15:11:18.760593+09',1,NULL,NULL),
	 (6,'작업이력','inventory',511,NULL,'2025-01-08 16:49:52.374771+09',NULL,1,NULL,20),
	 (7,'예방정비(PM)','manage_accounts',520,NULL,'2025-01-08 15:48:46.699764+09','2025-01-15 14:37:50.924932+09',1,NULL,20),
	 (8,'예방점검(PI)','content_paste_search',530,NULL,'2025-01-08 15:49:22.922632+09','2025-01-15 14:39:33.580483+09',1,NULL,20),
	 (9,'데이터분석','search_insights',600,NULL,'2024-11-22 17:02:09.507788+09','2025-01-15 13:47:47.804092+09',1,NULL,NULL),
	 (10,'업무지원','supervisor_account',700,NULL,'2024-11-22 17:02:34.099485+09','2025-01-15 11:29:57.787695+09',1,NULL,NULL),
	 (12,'시스템관리','manufacturing',900,NULL,'2024-11-22 17:02:44.44146+09','2025-01-15 10:58:39.798384+09',1,NULL,NULL),
	 (14,'리포트 및 통계','bar_chart',1000,NULL,'2025-01-09 11:36:32.760762+09','2025-01-15 11:28:03.081531+09',1,NULL,20),
	 (15,'설비통계','inventory',1100,NULL,'2025-01-09 11:41:20.63937+09',NULL,1,NULL,20),
	 (16,'작업통계','inventory',1200,NULL,'2025-01-09 11:41:20.644402+09',NULL,1,NULL,20),
	 (17,'PM통계','inventory',1300,NULL,'2025-01-09 11:41:20.649337+09',NULL,1,NULL,20),
	 (18,'점검통계','inventory',1400,NULL,'2025-01-09 11:41:20.653906+09',NULL,1,NULL,20),
	 (19,'AI','Experiment',610,NULL,'2025-01-21 15:01:46.983179+09','2025-01-21 15:02:14.429179+09',NULL,NULL,NULL),
	 (20,'KMMS','inventory',210,NULL,'2025-01-21 15:01:46.983+09',NULL,1,NULL,NULL),
	 (9999,'샘플페이지','inventory',9999,NULL,'2025-03-31 14:41:51.835379+09','2025-03-31 15:27:48.762236+09',NULL,NULL,NULL),
	 (21,'설비정보','inventory',500,NULL,'2025-03-31 14:41:51.835379+09','2025-04-22 10:37:20.626561+09',NULL,NULL,20),
	 (24,'정비자재','inventory',505,NULL,'2025-04-23 14:47:39.082062+09','2025-04-23 14:49:11.020729+09',NULL,NULL,20),
	 (25,'데이터I/F','inventory',620,NULL,'2025-04-29 11:35:03.543094+09','2025-04-29 11:35:03.543094+09',NULL,NULL,NULL),
	 (11,'코드관리','wysiwyg',1500,NULL,'2025-01-03 10:57:57.374248+09','2025-06-20 15:52:08.718208+09',1,NULL,20),
	 (27,'사이트 옵션','wysiwyg',1600,NULL,'2025-06-19 09:48:54.174171+09','2025-06-20 15:52:23.204347+09',NULL,NULL,20),
	 (5,'작업관리','inventory',510,NULL,'2025-01-08 15:46:00.305887+09','2025-06-23 10:50:09.769594+09',1,NULL,20),
	 (28,'SAP','inventory',621,NULL,'2025-07-08 18:27:32.025329+09','2025-07-08 18:33:55.763652+09',NULL,NULL,25),
	 (29,'MES','inventory',622,NULL,'2025-07-08 18:28:05.121024+09','2025-07-08 18:34:10.258022+09',NULL,NULL,25),
	 (30,'SMT라인','inventory',623,NULL,'2025-07-08 18:28:18.553805+09','2025-07-08 18:34:27.225106+09',NULL,NULL,25) ;


--메뉴
truncate table menu_item cascade;
INSERT INTO menu_item ("MenuCode","MenuName","IconCSS","Url","Popup",_order,_status,_created,_modified,_creater_id,_modifier_id,"MenuFolder_id") VALUES
	 --('wm_mig_user','사용자 Migration',NULL,'/gui/wm_mig_user','N',20,NULL,'2025-08-07 15:51:33.506865+09','2025-08-07 15:51:38.055778+09',1,1,31),
	 --('wm_mig_dept','부서 Migration',NULL,'/gui/wm_mig_dept','N',10,NULL,'2025-08-07 15:51:30.243925+09','2025-08-07 15:51:38.042777+09',1,1,31),
	 ('wm_sample_spreadSheet','샘플6.2_스프레드시트',NULL,'/gui/wm_sample_spreadSheet','N',80,NULL,'2025-08-06 18:26:04.151703+09','2025-08-06 18:26:11.258045+09',1,1,9999),
	 ('wm_if_log','인터페이스로그확인',NULL,'/gui/wm_if_log','N',50,NULL,'2025-07-30 15:56:01.943176+09','2025-07-30 15:56:05.55497+09',3,3,25),
	 ('wm_cm_wo_chk_item','점검항목',NULL,'/gui/wm_cm_wo_chk_item','N',80,NULL,'2025-07-30 13:40:29.956079+09','2025-07-30 13:40:37.999903+09',3,3,11),
	 ('wm_ex_supplier','외주업체',NULL,'/gui/wm_ex_supplier','N',30,NULL,'2025-07-21 19:46:44.252859+09','2025-07-30 13:40:37.9769+09',3,3,11),
	 ('wm_check_wo_issued','점검이상 발행WO',NULL,'/gui/wm_check_wo_issued','N',40,NULL,'2025-07-16 15:20:54.266097+09','2025-07-16 15:21:41.019425+09',3,3,8),
	 ('wm_check_result','점검 결과 조회',NULL,'/gui/wm_check_result','N',30,NULL,'2025-07-16 15:19:51.146965+09','2025-07-16 15:21:40.999601+09',3,3,8),
	 ('wm_if_tension_check','스텐실텐션체크',NULL,'/gui/wm_if_tension_check','N',30,NULL,'2025-07-08 18:31:26.719379+09','2025-07-08 18:31:39.798913+09',3,3,30),
	 ('wm_if_reflow_profile','Reflow Profile',NULL,'/gui/wm_if_reflow_profile','N',10,NULL,'2025-07-08 18:31:18.367633+09','2025-07-08 18:31:39.784555+09',3,3,30),
	 ('wm_if_viscosity_check','솔더점도측정',NULL,'/gui/wm_if_viscosity_check','N',20,NULL,'2025-07-08 18:31:12.967337+09','2025-07-08 18:31:39.792506+09',3,3,30),
	 ('wm_if_mnt_pickup_rate','마운터 Pickup Rate',NULL,'/gui/wm_if_mnt_pickup_rate','N',40,NULL,'2025-07-08 18:30:30.144376+09','2025-07-08 18:31:39.805749+09',3,3,30),
	 ('wm_if_mes_oee','OEE',NULL,'/gui/wm_if_mes_oee','N',50,NULL,'2025-07-08 18:29:45.659391+09','2025-07-08 18:30:23.236457+09',3,3,29),
	 ('wm_if_mes_product_plan','생산계획',NULL,'/gui/wm_if_mes_product_plan','N',10,NULL,'2025-07-08 18:29:43.075516+09','2025-07-08 18:30:23.211457+09',3,3,29),
	 ('wm_if_mes_workorder','작업지시',NULL,'/gui/wm_if_mes_workorder','N',20,NULL,'2025-07-08 18:29:38.433791+09','2025-07-08 18:30:23.217969+09',3,3,29),
	 ('wm_if_mes_fpy','FPY조회',NULL,'/gui/wm_if_mes_fpy','N',40,NULL,'2025-07-08 18:29:34.294351+09','2025-07-08 18:30:23.230592+09',3,3,29),
	 ('wm_if_mes_lot_history','LOT Hist.',NULL,'/gui/wm_if_mes_lot_history','N',30,NULL,'2025-07-08 18:29:31.320481+09','2025-07-08 18:30:23.225525+09',3,3,29),
	 ('wm_if_sap_pcb_random','SAP PCB Rand.',NULL,'/gui/wm_if_sap_pcb_random','N',40,NULL,'2025-07-08 18:28:48.827073+09','2025-07-08 18:29:04.390482+09',3,3,28),
	 ('wm_if_sap_bom','SAP BOM',NULL,'/gui/wm_if_sap_bom','N',20,NULL,'2025-07-08 18:28:38.463414+09','2025-07-08 18:29:04.389407+09',3,3,28),
	 ('wm_if_sap_mat','SAP Material',NULL,'/gui/wm_if_sap_mat','N',10,NULL,'2025-07-08 18:28:35.429485+09','2025-07-08 18:29:04.374451+09',3,3,28),
	 ('wm_if_sap_stock','SAP Stock',NULL,'/gui/wm_if_sap_stock','N',30,NULL,'2025-07-08 18:28:31.566768+09','2025-07-08 18:29:04.390482+09',3,3,28),
	 ('wm_dt_main','생산라인현황',NULL,'/gui/wm_dt_main','N',30,NULL,'2025-06-27 16:53:33.611898+09','2025-06-27 16:53:43.701123+09',3,3,1),
	 ('wm_sche_opts','스케줄링',NULL,'/gui/wm_sche_opts','N',20,NULL,'2025-06-19 09:55:15.584536+09','2025-06-19 09:55:19.862315+09',1,1,27),
	 ('wm_proc_opts','프로세스',NULL,'/gui/wm_proc_opts','N',10,NULL,'2025-06-19 09:55:06.475874+09','2025-06-19 09:55:19.851549+09',1,1,27),
	 ('wm_wo_pending','미처리 WO 목록',NULL,'/gui/wm_wo_pending','N',30,NULL,'2025-05-23 17:35:08.543719+09','2025-05-23 17:35:17.491582+09',3,3,6),
	 ('wm_wo_cancel','취소된 WO 목록',NULL,'/gui/wm_wo_cancel','N',20,NULL,'2025-05-23 17:32:25.256153+09','2025-05-23 17:35:17.374681+09',3,3,6),
	 ('wm_wo_hist','WO 작업이력 조회',NULL,'/gui/wm_wo_hist','N',10,NULL,'2025-05-23 15:31:27.397192+09','2025-05-23 17:35:17.361694+09',3,3,6),
	 ('wm_cm_holiday','휴일 스케줄',NULL,'/gui/wm_cm_holiday','N',90,NULL,'2025-05-22 16:38:33.925766+09','2025-07-30 13:40:38.005072+09',1,3,11),
	 ('wm_pm_schedule_m','PM 일정생성(수동)',NULL,'/gui/wm_pm_schedule_m','N',40,NULL,'2025-05-19 16:36:59.969801+09','2025-05-19 16:43:54.678145+09',1,1,7),
	 ('wm_if_topic_data','TOPIC데이터확인',NULL,'/gui/wm_if_topic_data','N',40,NULL,'2025-04-29 11:36:37.656223+09','2025-07-30 15:56:05.548781+09',3,3,25),
	 ('wm_if_equ_result','설비실적(측정데이터)',NULL,'/gui/wm_if_equ_result','N',30,NULL,'2025-04-29 11:36:03.43116+09','2025-07-30 15:56:05.541758+09',3,3,25),
	 ('wm_if_van','VAN',NULL,'/gui/wm_if_van','N',20,NULL,'2025-04-29 11:35:54.333431+09','2025-07-30 15:56:05.535198+09',3,3,25),
	 ('wm_if_qms','QMS',NULL,'/gui/wm_if_qms','N',10,NULL,'2025-04-29 11:35:49.825704+09','2025-07-30 15:56:05.525149+09',3,3,25),
	 ('wm_cm_code','기초코드',NULL,'/gui/wm_cm_code','N',10,NULL,'2025-04-23 18:21:06.794658+09','2025-07-30 13:40:37.966054+09',1,3,11),
	 ('wm_cm_material','자재마스터',NULL,'/gui/wm_cm_material','N',10,NULL,'2025-04-23 14:49:24.69621+09','2025-04-23 14:49:29.862765+09',1,1,24),
	 ('wm_cm_wo_project','프로젝트',NULL,'/gui/wm_cm_wo_project','N',70,NULL,'2025-04-22 10:39:20.139363+09','2025-07-30 13:40:37.994902+09',1,3,11),
	 ('wm_cm_equip_group','설비분류',NULL,'/gui/wm_cm_equip_group','N',60,NULL,'2025-04-22 10:39:12.71875+09','2025-07-30 13:40:37.989905+09',1,3,11),
	 ('wm_cm_equip_loc','설비위치정보',NULL,'/gui/wm_cm_equip_loc','N',50,NULL,'2025-04-22 10:39:04.054258+09','2025-07-30 13:40:37.984899+09',1,3,11),
	 ('wm_cm_material_loc','자재보관위치',NULL,'/gui/wm_cm_material_loc','N',40,NULL,'2025-04-22 10:38:55.592719+09','2025-07-30 13:40:37.980904+09',1,3,11),
	 ('wm_sample_design','샘플10_디자인',NULL,'/gui/wm_sample_design','N',120,NULL,'2025-04-02 14:02:20.316+09','2025-08-06 18:26:11.301389+09',3,1,9999),
	 ('wm_sample_export','샘플9_Export',NULL,'/gui/wm_sample_export','N',110,NULL,'2025-04-02 14:02:11.948+09','2025-08-06 18:26:11.288506+09',3,1,9999),
	 ('wm_sample_alert_noti','샘플8_알람_노티',NULL,'/gui/wm_sample_alert_noti','N',100,NULL,'2025-04-02 14:02:07.329+09','2025-08-06 18:26:11.279318+09',3,1,9999),
	 ('wm_sample_upload','샘플7_파일업로드',NULL,'/gui/wm_sample_upload','N',90,NULL,'2025-04-02 14:02:02.343+09','2025-08-06 18:26:11.268196+09',3,1,9999),
	 ('wm_sample_spread_sheet','샘플6_스프레드시트',NULL,'/gui/wm_sample_spread_sheet','N',70,NULL,'2025-04-02 14:01:55.159+09','2025-08-06 18:26:11.243564+09',3,1,9999),
	 ('wm_sample_editor','샘플5_웹에디터',NULL,'/gui/wm_sample_editor','N',60,NULL,'2025-04-02 14:01:49.103+09','2025-08-06 18:26:11.231111+09',3,1,9999),
	 ('wm_sample_popup','샘플4_팝업',NULL,'/gui/wm_sample_popup','N',50,NULL,'2025-04-02 14:01:32.741+09','2025-08-06 18:26:11.218037+09',3,1,9999),
	 ('wm_sample_chart','샘플3_차트',NULL,'/gui/wm_sample_chart','N',40,NULL,'2025-04-02 14:01:28.991+09','2025-08-06 18:26:11.208303+09',3,1,9999),
	 ('wm_sample_form','샘플2_폼화면',NULL,'/gui/wm_sample_form','N',30,NULL,'2025-04-02 14:01:24.279+09','2025-08-06 18:26:11.19665+09',3,1,9999),
	 ('wm_sample_treelist','샘플1_트리그리드',NULL,'/gui/wm_sample_treelist','N',20,NULL,'2025-04-02 14:01:15.186+09','2025-08-06 18:26:11.184349+09',3,1,9999),
	 ('wm_sample_test','샘플화면(test)',NULL,'/gui/wm_sample_test','N',10,NULL,'2025-04-02 14:01:08.53+09','2025-08-06 18:26:11.173051+09',3,1,9999),
	 ('wm_cm_equip_workhist','설비별작업이력',NULL,'/gui/wm_cm_equip_workhist','N',30,NULL,'2025-03-31 14:51:10.006381+09','2025-03-31 15:10:05.807803+09',1,1,21),
	 ('wm_cm_equip_disposed','불용설비',NULL,'/gui/wm_cm_equip_disposed','N',20,NULL,'2025-03-31 14:50:43.602806+09','2025-03-31 15:10:05.798405+09',1,1,21),
	 ('wm_cm_equipment','설비마스터',NULL,'/gui/wm_cm_equipment','N',10,NULL,'2025-03-31 14:50:24.768489+09','2025-03-31 15:10:05.791491+09',1,1,21),
	 ('wm_learning_data_info','학습데이터 정보',NULL,'/gui/wm_learning_data_info','N',50,NULL,'2025-01-21 16:54:07.515311+09','2025-01-21 16:54:21.349119+09',3,3,19),
	 ('wm_learning_data_from_tag','학습데이터 정보(태그)',NULL,'/gui/wm_learning_data_from_tag','N',60,NULL,'2025-01-21 15:02:57.467844+09','2025-01-21 16:54:21.356793+09',3,3,19),
	 ('wm_predictive_conservation','예지보전 알람',NULL,'/gui/wm_predictive_conservation','N',40,NULL,'2025-01-21 15:02:45.262656+09','2025-01-21 16:54:21.342407+09',3,3,19),
	 ('wm_ai_tagdata_list','AI시스템 IF 확인',NULL,'/gui/wm_ai_tagdata_list','N',30,NULL,'2025-01-21 15:02:38.986308+09','2025-01-21 16:54:21.334786+09',3,3,19),
	 ('wm_ai_tag','AI시스템 참조데이터 관리',NULL,'/gui/wm_ai_tag','N',20,NULL,'2025-01-21 15:02:33.592389+09','2025-01-21 16:54:21.327939+09',3,3,19),
	 ('wm_ai_model','모델 관리',NULL,'/gui/wm_ai_model','N',10,NULL,'2025-01-21 15:02:29.146251+09','2025-01-21 16:54:21.318884+09',3,3,19),
	 ('wm_ai_tag_group','AI시스템 운영관리',NULL,'/gui/wm_ai_tag_group','N',10,NULL,'2025-01-21 15:02:29.146251+09','2025-01-21 16:54:21.318884+09',3,3,19),
	 ('wm_inspection_stats','점검 수행 통계',NULL,'/gui/wm_inspection_stats','N',1403,NULL,'2025-01-09 14:12:44.31242+09',NULL,1,NULL,18),
	 ('wm_inspection_issues','점검결과 이상 설비목록',NULL,'/gui/wm_inspection_issues','N',1402,NULL,'2025-01-09 14:12:44.30806+09',NULL,1,NULL,18),
	 ('wm_facility_inspection_master','설비종류별 점검마스터',NULL,'/gui/wm_facility_inspection_master','N',1401,NULL,'2025-01-09 14:12:44.301445+09',NULL,1,NULL,18),
	 ('wm_pm_wo_completion_rate','부서별 PM WO 완료율',NULL,'/gui/wm_pm_wo_completion_rate','N',1302,NULL,'2025-01-09 14:12:44.297038+09',NULL,1,NULL,17),
	 ('wm_pm_status_by_category','카테고리별 PM현황',NULL,'/gui/wm_pm_status_by_category','N',1301,NULL,'2025-01-09 14:12:44.288526+09',NULL,1,NULL,17),
	 ('wm_dept_work_request_stats','부서별 작업 요청 통계',NULL,'/gui/wm_dept_work_request_stats','N',110,NULL,'2025-01-09 13:57:44.754036+09','2025-07-24 16:31:07.899273+09',1,3,16),
	 ('wm_dept_task_compliance_rate','부서별 기간별 작업 준수율',NULL,'/gui/wm_dept_task_compliance_rate','N',100,NULL,'2025-01-09 13:57:44.742667+09','2025-07-24 16:31:07.867358+09',1,3,16),
	 ('wm_dept_overdue_tasks','부서별 기간별 지연작업 목록',NULL,'/gui/wm_dept_overdue_tasks','N',90,NULL,'2025-01-09 13:57:44.734652+09','2025-07-24 16:31:07.833316+09',1,3,16),
	 ('wm_team_breakdown_costs','팀별 고장비용 현황',NULL,'/gui/wm_team_breakdown_costs','N',80,NULL,'2025-01-09 13:57:44.730042+09','2025-07-24 16:31:07.808491+09',1,3,16),
	 ('wm_dept_pm_rate','부서별 예방 정비율',NULL,'/gui/wm_dept_pm_rate','N',70,NULL,'2025-01-09 13:57:44.724097+09','2025-07-24 16:31:07.689606+09',1,3,16),
	 ('wm_outsourced_tasks_count','아웃소싱 작업건수',NULL,'/gui/wm_outsourced_tasks_count','N',60,NULL,'2025-01-09 13:57:44.719247+09','2025-07-24 16:31:07.683588+09',1,3,16),
	 ('wm_top_wo_in_work_cost','작업비용 상위 WO',NULL,'/gui/wm_top_wo_in_work_cost','N',50,NULL,'2025-01-09 13:57:44.712973+09','2025-07-24 16:31:07.679177+09',1,3,16),
	 ('wm_conservation_cost_status','정비비용 현황',NULL,'/gui/wm_conservation_cost_status','N',40,NULL,'2025-01-09 13:57:44.708277+09','2025-07-24 16:31:07.672599+09',1,3,16),
	 ('wm_top_working_hours_wo','작업시간 상위 WO',NULL,'/gui/wm_top_working_hours_wo','N',30,NULL,'2025-01-09 13:57:44.703792+09','2025-07-24 16:31:07.667581+09',1,3,16),
	 ('wm_dept_work_costs','부서별 기간별 작업비용',NULL,'/gui/wm_dept_work_costs','N',20,NULL,'2025-01-09 13:57:44.69963+09','2025-07-24 16:31:07.661332+09',1,3,16),
	 ('wm_wo_dept_performance','부서별 기간별 WO 발행 실적',NULL,'/gui/wm_wo_dept_performance','N',10,NULL,'2025-01-09 13:57:44.691621+09','2025-07-24 16:31:07.653336+09',1,3,16),
	 ('wm_facility_specifications','설비별 사양 목록',NULL,'/gui/wm_facility_specifications','N',90,NULL,'2025-01-09 13:17:55.759948+09','2025-06-23 10:54:24.320578+09',1,1,15),
	 ('wm_facility_downtime','설비별 고장시간',NULL,'/gui/wm_facility_downtime','N',80,NULL,'2025-01-09 13:17:55.75257+09','2025-06-23 10:54:24.294087+09',1,1,15),
	 ('wm_facility_maintenance_cost','설비별 정비비용',NULL,'/gui/wm_facility_maintenance_cost','N',70,NULL,'2025-01-09 13:17:55.748069+09','2025-06-23 10:54:24.237795+09',1,1,15),
	 ('wm_critical_equipment_status','중요도별 설비 고장 현황',NULL,'/gui/wm_critical_equipment_status','N',60,NULL,'2025-01-09 13:17:55.742668+09','2025-06-23 10:54:24.205026+09',1,1,15),
	 ('wm_category_equipment_status','카테고리별 설비 현황',NULL,'/gui/wm_category_equipment_status','N',50,NULL,'2025-01-09 13:17:55.738518+09','2025-06-23 10:54:24.164429+09',1,1,15),
	 ('wm_facility_mttr_mtbf','설비별 MTTR/MTBF',NULL,'/gui/wm_facility_mttr_mtbf','N',40,NULL,'2025-01-09 13:17:55.733269+09','2025-06-23 10:54:24.153877+09',1,1,15),
	 ('wm_facility_treatment_status','기간별 불용처리 설비 현황',NULL,'/gui/wm_facility_treatment_status','N',30,NULL,'2025-01-09 13:17:55.725443+09','2025-06-23 10:54:24.144827+09',1,1,15),
	 ('wm_monthly_maintenance_cost','설비별 월간 정비비용',NULL,'/gui/wm_monthly_maintenance_cost','N',20,NULL,'2025-01-09 13:17:55.720707+09','2025-06-23 10:54:24.132344+09',1,1,15),
	 ('wm_facility_monthly_status','설비별 월간 고장현황',NULL,'/gui/wm_facility_monthly_status','N',10,NULL,'2025-01-09 13:17:55.713606+09','2025-06-23 10:54:24.115305+09',1,1,15),
	 ('wm_create_inspection_schedule_manual','점검 일정생성(수동)',NULL,'/gui/wm_create_inspection_schedule_manual','N',50,NULL,'2025-01-08 16:36:44.766997+09','2025-07-16 15:21:41.019425+09',1,3,8),
	 ('wm_check_schedule','점검 작업일정',NULL,'/gui/wm_check_schedule','N',20,NULL,'2025-01-08 16:36:44.5343+09','2025-07-16 15:21:40.999601+09',1,3,8),
	 ('wm_check_master','점검 마스터',NULL,'/gui/wm_check_master','N',10,NULL,'2025-01-08 16:36:44.489528+09','2025-07-16 15:21:40.985029+09',1,3,8),
	 ('wm_pm_work','PM 마스터별 WO',NULL,'/gui/wm_wo_by_pm_master','N',30,NULL,'2025-01-08 16:33:20.666031+09','2025-05-19 16:43:54.675113+09',1,1,7),
	 ('wm_pm_schedule','PM 작업일정',NULL,'/gui/wm_pm_schedule','N',20,NULL,'2025-01-08 16:33:20.66069+09','2025-05-19 16:43:54.670578+09',1,1,7),
	 ('wm_pm_master','PM 마스터',NULL,'/gui/wm_pm_master','N',10,NULL,'2025-01-08 16:33:20.65558+09','2025-05-19 16:43:54.66637+09',1,1,7),
	 ('wm_post_work_management','사후작업 관리',NULL,'/gui/wm_post_work_management','N',50,NULL,'2025-01-08 16:30:34.525007+09','2025-07-08 16:29:50.715054+09',1,3,5),
	 ('wm_work_order_approval','작업지시 승인',NULL,'/gui/wm_work_order_approval','N',30,NULL,'2025-01-08 16:30:34.520756+09','2025-07-08 16:29:50.706477+09',1,3,5),
	 ('wm_work_request_approval','작업요청 승인',NULL,'/gui/wm_work_request_approval','N',20,NULL,'2025-01-08 16:30:34.516291+09','2025-07-08 16:29:50.702577+09',1,3,5),
	 ('wm_work_order_management','작업결과 관리',NULL,'/gui/wm_work_order_management','N',40,NULL,'2025-01-08 16:30:34.511169+09','2025-07-08 16:29:50.711477+09',1,3,5),
	 ('wm_my_work_request','작업요청',NULL,'/gui/wm_my_work_request','N',10,NULL,'2025-01-08 16:30:34.500902+09','2025-07-08 16:29:50.695417+09',1,3,5),
	 ('wm_supplier','공급업체',NULL,'/gui/wm_supplier','N',20,NULL,'2025-01-03 11:05:01.287936+09','2025-07-30 13:40:37.971902+09',3,3,11),
	 ('wm_depart','부서',NULL,'/gui/wm_depart','N',40,NULL,'2024-12-23 12:19:46.352763+09','2024-12-23 12:19:53.275487+09',3,3,12),
	 ('wm_storyboard','스토리보드',NULL,'/gui/wm_storyboard','N',20,NULL,'2024-11-25 15:00:43.246192+09','2025-06-27 16:53:43.693985+09',3,3,1),
	 ('wm_asset','자산관리',NULL,'/gui/wm_dashboard','N',20,NULL,'2024-11-25 15:00:40.379979+09','2025-07-08 13:50:30.577057+09',3,3,2),
	 ('wm_aasx','AASX관리',NULL,'/gui/wm_dashboard','N',30,NULL,'2024-11-25 15:00:40.379979+09','2025-07-08 13:50:30.577057+09',3,3,2),
	 ('wm_dashboard','대시보드',NULL,'/gui/wm_dashboard','N',10,NULL,'2024-11-25 15:00:40.379979+09','2025-06-27 16:53:43.666822+09',3,3,1),
	 ('wm_aas','AAS관리',NULL,'/gui/wm_dashboard','N',10,NULL,'2024-11-25 15:00:40.379979+09','2025-07-08 13:50:30.561156+09',3,3,2),
	 ('wm_regression_a','산점도-회귀분석',NULL,'/gui/wm_regression_a','N',80,NULL,'2024-11-22 17:10:08.706509+09','2024-11-22 17:10:17.344432+09',1,1,9),
	 ('wm_tag_trend','데이터트렌드',NULL,'/gui/wm_tag_trend','N',40,NULL,'2024-11-22 17:10:05.946882+09','2024-11-22 17:10:17.312142+09',1,1,9),
	 ('wm_tag_summary','데이터통계',NULL,'/gui/wm_tag_summary','N',30,NULL,'2024-11-22 17:10:03.213384+09','2024-11-22 17:10:17.304884+09',1,1,9),
	 ('wm_tag_scatter','산점도',NULL,'/gui/wm_tag_scatter','N',70,NULL,'2024-11-22 17:09:59.972834+09','2024-11-22 17:10:17.336552+09',1,1,9),
	 ('wm_tag_histogram','히스토그램',NULL,'/gui/wm_tag_histogram','N',60,NULL,'2024-11-22 17:09:50.213623+09','2024-11-22 17:10:17.328512+09',1,1,9),
	 ('wm_tag_boxplot','상자수염그림',NULL,'/gui/wm_tag_boxplot','N',50,NULL,'2024-11-22 17:09:41.707796+09','2024-11-22 17:10:17.320561+09',1,1,9),
	 ('wm_tag_data_list','태그데이터조회',NULL,'/gui/wm_tag_data_list','N',20,NULL,'2024-11-22 17:09:39.061398+09','2024-11-22 17:10:17.296076+09',1,1,9),
	 ('wm_tag_data_current','태그데이터현황',NULL,'/gui/wm_tag_data_current','N',10,NULL,'2024-11-22 17:09:34.259863+09','2024-11-22 17:10:17.285547+09',1,1,9),
	 ('wm_equip_group','설비그룹',NULL,'/gui/wm_equip_group','N',10,NULL,'2024-11-22 17:09:20.838481+09','2024-11-22 17:09:24.957445+09',1,1,4),
	 ('wm_equipment','설비',NULL,'/gui/wm_equipment','N',20,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_das_config','데이터수집설정',NULL,'/gui/wm_das_config','N',70,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_tag_master','태그관리',NULL,'/gui/wm_tag_master','N',60,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_tag_group','태그그룹',NULL,'/gui/wm_tag_group','N',50,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_factory','공장',NULL,'/gui/wm_factory','N',10,NULL,'2024-11-22 17:07:52.512412+09','2025-05-22 15:47:23.004442+09',1,1,3),
	 ('wm_model_change','기종변경정보',NULL,'/gui/wm_model_change','N',90,NULL,'2024-11-22 17:05:06.581048+09','2025-05-22 15:47:23.051191+09',1,1,3),
	 ('wm_line_inactive','라인비가동정보',NULL,'/gui/wm_line_inactive','N',80,NULL,'2024-11-22 17:05:00.230849+09','2025-05-22 15:47:23.046192+09',1,1,3),
	 ('wm_shift','조교대정보',NULL,'/gui/wm_shift','N',70,NULL,'2024-11-22 17:04:56.656039+09','2025-05-22 15:47:23.040191+09',1,1,3),
	 ('wm_defect','부적합정보',NULL,'/gui/wm_defect','N',60,NULL,'2024-11-22 17:04:53.787407+09','2025-05-22 15:47:23.034245+09',1,1,3),
	 ('wm_bom','BOM',NULL,'/gui/wm_bom','N',50,NULL,'2024-11-22 17:04:44.062137+09','2025-05-22 15:47:23.028741+09',1,1,3),
	 ('wm_material','품목(자재)',NULL,'/gui/wm_material','N',40,NULL,'2024-11-22 17:04:41.46544+09','2025-05-22 15:47:23.024288+09',1,1,3),
	 ('wm_process','공정',NULL,'/gui/wm_process','N',30,NULL,'2024-11-22 17:04:38.218271+09','2025-05-22 15:47:23.01771+09',1,1,3),
	 ('wm_line','라인',NULL,'/gui/wm_line','N',20,NULL,'2024-11-22 17:04:35.779583+09','2025-05-22 15:47:23.011093+09',1,1,3),
	 ('wm_board','공지사항',NULL,'/gui/wm_board','N',20,NULL,'2024-11-22 17:03:52.168896+09','2024-11-22 17:03:55.093085+09',1,1,10),
	 ('wm_calendar','캘린더',NULL,'/gui/wm_calendar','N',10,NULL,'2024-11-22 17:03:46.144348+09','2024-11-22 17:03:55.082601+09',1,1,10),
	 ('wm_system_log','시스템로그',NULL,'/gui/wm_system_log','N',80,NULL,'2024-11-22 17:03:34.6587+09','2024-12-23 12:19:53.310692+09',1,3,12),
	 ('wm_menu_log','메뉴로그',NULL,'/gui/wm_menu_log','N',70,NULL,'2024-11-22 17:03:28.79165+09','2024-12-23 12:19:53.302695+09',1,3,12),
	 ('wm_login_log','로그인로그',NULL,'/gui/wm_login_log','N',60,NULL,'2024-11-22 17:03:22.529364+09','2024-12-23 12:19:53.295048+09',1,3,12),
	 ('wm_storyboard_config','스토리보드설정',NULL,'/gui/wm_storyboard_config','N',50,NULL,'2024-11-22 17:03:17.811259+09','2024-12-23 12:19:53.285883+09',1,3,12),
	 ('wm_user_group_menu','메뉴권한',NULL,'/gui/wm_user_group_menu','N',30,NULL,'2024-11-22 17:03:10.558772+09','2024-12-23 12:19:53.268487+09',1,3,12),
	 ('wm_user_group','사용자그룹',NULL,'/gui/wm_user_group','N',20,NULL,'2024-11-22 17:03:05.113621+09','2024-12-23 12:19:53.241914+09',1,3,12),
	 ('wm_user','사용자',NULL,'/gui/wm_user','N',10,NULL,'2024-11-22 17:02:59.75001+09','2024-12-23 12:19:53.226806+09',1,3,12);


--메뉴권한
alter SEQUENCE user_group_menu_id_seq restart WITH 1 ;
INSERT INTO user_group_menu ("MenuCode","AuthCode","_status","_created","_modified","_creater_id","_modifier_id","UserGroup_id")
select "MenuCode",'RW',NULL,now(),null,1,NULL,1 from menu_item mi  order by "MenuCode";

INSERT INTO user_group_menu ("MenuCode","AuthCode","_status","_created","_modified","_creater_id","_modifier_id","UserGroup_id")
select "MenuCode",'RW',NULL,now(),null,1,NULL,2 from menu_item mi  order by "MenuCode";

-- 유저코드그룹(code_group)
insert into code_group ("Code","Name","SystemYn","Remark","UseYn","DelYn","_created") 
values 
('STOR_LOC_ADDR','보관위치주소','N','로케이션(A-Z), 랙(01-99), 단(01-99), 열(01-99)','Y','N',now())
, ('STOR_TYPE','창고구분','N','창고구분','Y','N',now())
, ('COMP_KIND','업체구분(Company Type))','N','업체 유형 구분 코드','Y','N',now())
, ('years','연도','N','','Y','Y',now())
, ('COMP_TYPE','업체유형','N','업체유형','Y','N',now())
, ('MTRL_TYPE','자재종류','N','자재종류','Y','N',now())
, ('USE_YN','사용여부','Y','','Y','N',now())
, ('PM_TYPE','예방정비유형','Y','','Y','N',now())
, ('EQU_STATUS','설비상태','N','설비상태','Y','N',now())
, ('CYCLE_TYPE','주기단위','N','주기단위','Y','N',now())
, ('WO_STATUS','작업상태','Y','작업상태','Y','N',now())
, ('MAINT_TYPE','보전유형','Y','보전유형','Y','N',now())
, ('WO_TYPE','작업유형','Y','작업유형','Y','N',now())
, ('PC','현상','Y','현상','Y','N',now())
, ('CC','원인','Y','원인','Y','N',now())
, ('RC','조치','Y','조치','Y','N',now())
, ('WORK_SRC','작업구분','Y','작업구분','Y','N',now())
, ('MODEL_TYPE','AI모델유형','Y','AI모델유형','Y','N',now())
, ('TASK_TYPE','AI분석유형','N','AI분석유형','Y','N',now())
, ('TRAINING_STATUS','AI학습상태','Y','AI모델학습상태','Y','N',now())
, ('PARAM_TYPE','AI하이퍼파라미터타입','N','하이퍼파라미터 값 데이터타입','Y','N',now())
-- AI 분석 유형별
, ('AI_OPTIMIZATION',   '최적화',       'N', 'TASK_TYPE=OPTIMIZATION에 해당하는 알고리즘 그룹', 'Y', 'N', NOW())
, ('AI_TEXT_ANALYSIS',  '텍스트 분석',  'N', 'TASK_TYPE=TEXT_ANALYSIS에 해당하는 알고리즘 그룹', 'Y', 'N', NOW())
, ('AI_IMAGE_ANALYSIS', '이미지 분석',  'N', 'TASK_TYPE=IMAGE_ANALYSIS에 해당하는 알고리즘 그룹', 'Y', 'N', NOW())
, ('AI_ANOMALY',        '이상탐지',     'N', 'TASK_TYPE=ANOMALY에 해당하는 알고리즘 그룹',        'Y', 'N', NOW())
, ('AI_CLASSIFICATION', '분류',         'N', 'TASK_TYPE=CLASSIFICATION에 해당하는 알고리즘 그룹', 'Y', 'N', NOW())
, ('AI_REGRESSION',     '회귀',         'N', 'TASK_TYPE=REGRESSION에 해당하는 알고리즘 그룹',     'Y', 'N', NOW())
, ('AI_CLUSTERING',     '군집',         'N', 'TASK_TYPE=CLUSTERING에 해당하는 알고리즘 그룹',     'Y', 'N', NOW())
, ('AI_TIMESERIES',     '시계열 분석',  'N', 'TASK_TYPE=TIMESERIES에 해당하는 알고리즘 그룹',     'Y', 'N', NOW())
, ('AI_OTHERS',         '기타',         'N', 'TASK_TYPE=OTHERS에 해당하는 알고리즘 그룹',         'Y', 'N', NOW())
-- AI 알고리즘별(모델별 param용) 25.07.29 김하늘 추가
, ('RANDOM_FOREST','랜덤포레스트 하이퍼파라미터','N','','Y','N',now())
, ('LOGISTIC_REGRESSION','로지스틱 회귀 하이퍼파라미터','N','','Y','N',NOW())
, ('XGBOOST','XGBoost 하이퍼파라미터','N','','Y','N',NOW())
, ('LIGHTGBM','LightGBM 하이퍼파라미터','N','','Y','N',NOW())
, ('SVM','SVM 하이퍼파라미터','N','','Y','N',NOW())
, ('KNN','KNN 하이퍼파라미터','N','','Y','N',NOW())
, ('NAIVE_BAYES','나이브 베이즈 하이퍼파라미터','N','','Y','N',NOW())
, ('MLP','MLP 하이퍼파라미터','N','','Y','N',NOW())
-- AI 데이터 유형 추가
, ('AI_DATA_SOURCE',	'AI원천데이터',	'Y', 'AI원천데이터유형',	'Y', 'N', now())
;


--유저코드(code)
insert into code("CodeGroupCode", "Code", "Name", "Remark", "DispOrder", "UseYn", "DelYn", "_created") 
values 
	-- 그룹코드: COMP_TYPE (업체유형)
	('COMP_TYPE', 'CLIENT', '고객사', '고객&공급사', 1, 'Y', 'N', NOW())
	,('COMP_TYPE', 'SUPPLIER',	 '공급사', '공급사', 2, 'Y', 'N', NOW())
	,('COMP_TYPE', 'EX_SUPPLIER', '외주사', '외주사', 3, 'Y', 'N', NOW())	

	-- 그룹코드: COMP_KIND (업체구분)
	,('COMP_KIND', 'CS',	'ClientSupplier', '고객&공급사', 1, 'Y', 'N', NOW())
	,('COMP_KIND', 'C',	'Client', '고객사', 2, 'Y', 'N', NOW())
	,('COMP_KIND', 'S',	'Supplier', '공급사', 3, 'Y', 'N', NOW())
	,('COMP_KIND', 'ES',	'ex_supplier', '외주사', 4, 'Y', 'N', NOW())

	-- 그룹코드: MTRL_TYPE (자재종류)
	,('MTRL_TYPE','MA','공압','공압 실린더, 공압 밸브, 진공패드, 에어 유닛 등',1,'Y','N',now())
	,('MTRL_TYPE','MH','유압','유압 실린더, 유압 밸브, 유압 필터, 유압 유닛 등',2,'Y','N',now())
	,('MTRL_TYPE','ME','기계요소','베어링, 메탈, 패킹, 부싱, 가이드 등',3,'Y', 'N',now())
	,('MTRL_TYPE','MT','동력 기기 / 전달','각종 감속기, 펌프 및 동력 전달에 필요한 벨트, 체인, 기어, 풀리 등',4,'Y', 'N',now())
	,('MTRL_TYPE','MS','특수제작','기성품이 아닌 맞춤형으로 모델명이 없는 제작품(롤, 로터, 임펠러 등)',5,'Y', 'N',now())
	,('MTRL_TYPE','EM','모터','AC 모터, DC 모터, 서보 모터, 벡터 모터, 토르크 모터, 기어드 모터 등 ',6,'Y', 'N',now())
	,('MTRL_TYPE','EC','모터 제어 / 주변기기','인버터, DC 제어반, 벡터 제어반, 서보 제어반, 토르크 제어반 등',7,'Y', 'N',now())
	,('MTRL_TYPE','ES','센서 부품','일반 엔코더, 레벨, 근접 센서, 포토 센서 등',8,'Y', 'N',now())
	,('MTRL_TYPE','EI','계장 부품','RTD, TIC, 히터, 로드셀, 계량기, 인디게이터, 레벨 등',9,'Y', 'N',now())
	,('MTRL_TYPE','EE','전기 부품','차단기, 릴레이, M/C, EOCR, 퓨즈, S/W, 경광등 등',10,'Y', 'N',now())
	,('MTRL_TYPE','EP','PLC / HMI / 제어 부품','PLC, 터치판넬, 전력조정기, K-TRON, 타이머 등',11,'Y', 'N',now())
	,('MTRL_TYPE','ET','정보 / 통신 / 영상 / 방송 부품','마이크, 앰프, HDMI, 소리통, 인터폰 등',12,'Y', 'N',now())
	,('MTRL_TYPE','UU','배관 기기','각종 밸브, 게이지, 트랩 등',13,'Y', 'N',now())
	
	-- 그룹코드: STOR_TYPE (창고구분)
	,('STOR_TYPE', 'PRODCUT',	'제품창고', '창고구분', 1, 'Y', 'N', NOW()) 
	,('STOR_TYPE', 'SEMI',	'반제품창고', '창고구분', 2, 'Y', 'N', NOW())
	,('STOR_TYPE', 'MATERIAL',	'자재창고', '창고구분', 3, 'Y', 'N', NOW())
	,('STOR_TYPE', 'DEFECT', '부적합품창고', '창고구분', 4, 'Y', 'N', NOW())
	,('STOR_TYPE', 'PROCESS',	'공정창고', '창고구분', 5, 'Y', 'N', NOW())
	,('STOR_TYPE', 'SCRAP',	'스크랩창고', '창고구분', 6, 'Y', 'N', NOW())

	-- 그룹코드: STOR_LOC_ADDR (보관위치주소)
	,('STOR_LOC_ADDR', 'A010101', 'A셀1랙1단1열', '로케이션(A-Z), 랙(01-99), 단(01-99), 열(01-99)', 1, 'Y', 'N', NOW()) 
	,('STOR_LOC_ADDR', 'A010102', 'A셀1랙1단2열', '로케이션(A-Z), 랙(01-99), 단(01-99), 열(01-99)', 2, 'Y', 'N', NOW())

	-- 그룹코드: USE_YN (사용여부)
	,('USE_YN', 'Y', '사용', '', 1, 'Y', 'N', NOW()) 
	,('USE_YN', 'N', '미사용', '', 2, 'Y', 'N', NOW())

	-- 그룹코드: MODEL_TYPE (모델유형) 25.05.08 수정
	,('MODEL_TYPE', 'Q-factor', 'Q-factor', '모델유형', 1, 'Y', 'N', NOW())
	,('MODEL_TYPE', 'KMMS', 'KMMS', '모델유형', 2, 'Y', 'N', NOW())

	-- 예방정비유형: PM_TYPE
	,('PM_TYPE', 'PM_TYPE_TBM', 'TBM', '', 1, 'Y', 'N', NOW()) 
	,('PM_TYPE', 'PM_TYPE_CBM', 'CBM', '', 2, 'Y', 'N', NOW())
	,('PM_TYPE', 'PM_TYPE_UBM', 'UBM', '', 3, 'Y', 'N', NOW())

	-- 설비중요도: IMPORT_RANK
	,('IMPORT_RANK', 'S', 'S급', NULL, 1, 'Y', 'N', NOW())
	,('IMPORT_RANK', 'A', 'A급', NULL, 2, 'Y', 'N', NOW())
	,('IMPORT_RANK', 'B', 'B급', NULL, 3, 'Y', 'N', NOW())
	,('IMPORT_RANK', 'C', 'C급', NULL, 3, 'Y', 'N', NOW())
	,('IMPORT_RANK', 'D', 'D급', NULL, 3, 'Y', 'N', NOW())

	-- 설비상태: EQU_STATUS
	,('EQU_STATUS', 'O', '가동중', NULL, 1, 'Y', 'N', NOW())
	,('EQU_STATUS', 'B', '고장 I 유휴', NULL, 2, 'Y', 'N', NOW())
	,('EQU_STATUS', 'D', '불용', NULL, 3, 'Y', 'N', NOW())

	-- 주기단위: CYCLE_TYPE
	,('CYCLE_TYPE', 'CYCLE_TYPE_Y', '년', NULL, 1, 'Y', 'N', NOW())
	,('CYCLE_TYPE', 'CYCLE_TYPE_M', '월', NULL, 2, 'Y', 'N', NOW())
	,('CYCLE_TYPE', 'CYCLE_TYPE_W', '주', NULL, 3, 'Y', 'N', NOW())
	,('CYCLE_TYPE', 'CYCLE_TYPE_D', '일', NULL, 4, 'Y', 'N', NOW())

	--작업상태	
	,('WO_STATUS', 'WOS_RW','요청작성중', '', 1, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_RB','요청반려', '', 2, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_RQ','요청완료', '', 3, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_RJ','요청승인반려', '', 4, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_OC','요청승인', '', 5, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_AP','작업승인', '', 6, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_CM','작업완료', '', 7, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_CL','WO완료', '', 8, 'Y', 'N', NOW())
	,('WO_STATUS', 'WOS_DL','취소', '', 9, 'Y', 'N', NOW())

	 --보전유형
	 ,('MAINT_TYPE','MAINT_TYPE_GM','일반작업', '', 1, 'Y', 'N', NOW())
	 ,('MAINT_TYPE','MAINT_TYPE_BM','사후보전', '', 2, 'Y', 'N', NOW())
	 ,('MAINT_TYPE','MAINT_TYPE_PM','예방보전', '', 3, 'Y', 'N', NOW())
	 ,('MAINT_TYPE','MAINT_TYPE_CM','개량보전', '', 4, 'Y', 'N', NOW())
	 ,('MAINT_TYPE','MAINT_TYPE_IM','점검작업', '', 5, 'N', 'N', NOW())

	 --작업유형
	 ,('WO_TYPE','WO','작업요청 WO', '', 1, 'Y', 'N', NOW())
	 ,('WO_TYPE','PM','예방정비 WO', '', 2, 'Y', 'N', NOW())
	 ,('WO_TYPE','DPR','작업일보 WO', '', 3, 'N', 'N', NOW())
	 ,('WO_TYPE','INSP','점검이상 WO', '', 4, 'N', 'N', NOW())	 

	 --현상
	 ,('PC','ARLK','에어 누출','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','ALRM','경보 또는 문제 표시기','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','BRNG','베어링 문제','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','CALB','교정(캘리브레이션) 문제','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','DIRT','먼지 또는 이물질 문제','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','ADJS','장비의 조정 필요','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','CUTO','장비의 절단','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','JAMD','장비 걸림(Jam)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','HUNG','장비PC 또는 프로세서 중단','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','XLUB','과도한 윤활','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','NOIS','과도한 소음','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','VIBR','과도한 진동','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','LLUB','윤활 부족','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','WIRE','느슨하거나 연결 끊어짐 ','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','ALIN','오정렬','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','NAIR','에어 부족','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','NPWR','전원 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','OLLK','오일 누출','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','OPER','운전자 오류','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','XHOT','과열 또는 연기','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','BROK','장비의 일부가 물리적 파손','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','SHRT','단락','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','VNDL','고의적 파손','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','WTLK','누수','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('PC','NOGO','시동 불능','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC01','설계 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')

	  --원인
	 ,('CC','CC02','제작 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC03','시공 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC04','시험 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC05','운전 부주의','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC06','자연열화','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC07','정상마모','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC08','절차서 부적합','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC09','정비 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC10','윤활 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC11','자재 불량','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC12','조건 변화','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC13','타설비 고장파급','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC14','한전 정전','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC15','공업용수 단수','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC16','규격 교환','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC17','설비 노후화','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC18','용량 부족','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC19','프로그램 이상','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('CC','CC20','이물혼입','','1','Y','N','2025-03-26 10:33:25.102663+09')

      --조치
	 ,('RC','RC001','누설 점검','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC002','단순 분해점검 / 조립','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC003','부품 가공 / 연마','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC004','부품 교체','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC005','설정치 변경(조건 조정)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC006','원점 조정','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC007','Overhaul','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC008','용접','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC009','윤활보충 / 교체','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC010','이음 점검','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC011','접촉불량 수리','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC012','조임','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC013','철거 / 제거','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC014','충전 / 보충','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC015','얼라인먼트','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC016','클리닝 / 플러싱','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC017','Painting / 보온','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC018','보증 수리','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC019','Lapping','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC020','열처리','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC021','접지','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC022','보강','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC023','프로그램 수정','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC024','초기화','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC025','재권선(Rewinding)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC026','건조(Dryer)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC027','임시동력(전원) 설치 / 철거','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC028','바이패스(By-Pass)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC029','Jump-Up','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('RC','RC030','블라인드 설치','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC001','유압 Unit','','1','Y','N','2025-03-26 10:33:25.102663+09')

	  --자재종류
	 ,('FC','FC002','Line(배관류)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC003','윤활장치','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC004','축봉장치(Seal, Packing)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC005','Impeller & Rotor','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC006','Shaft / Sleeve','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC007','Gear','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC008','Pulley / Spocket','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC009','Belt / Chain','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC010','Bearing','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC011','Diaphragm','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC012','Bolt / Nut / Key / Ring','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC013','Piston / Plunger','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC014','Casing / Body / Shell / Housing','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC015','Spring / Brake','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC016','Coupling','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC017','Motor','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC018','기초(Foundation)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC019','Screw(Element)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC020','Roll','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC021','Roller / Wheel','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC022','Frame','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC023','Cutter','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC024','Tube','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC025','Tray / 충진물','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC026','Nozzle / Manhole','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC027','Gasket','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC028','Valve','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC029','Hopper / Tank','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC030','Guide','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC031','Filter','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC032','Sight Glass','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC033','Robot','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC034','LM Guide / Rail','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC035','Cam','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC036','Jig','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC037','Chuck','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC038','Cylinder','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC039','Index','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC040','EPC','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC041','Printer','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC042','Switch','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC043','Contactor','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC044','MCCB(차단기)','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC045','과전류계전기','','1','Y','N','2025-03-26 10:33:25.102663+09')
	 ,('FC','FC046','Relay','','1','Y','N','2025-03-26 10:33:25.102663+09')

	 --작업구분
	 ,('WORK_SRC','WS01','사내수리', '', 1, 'Y', 'N', NOW())
	 ,('WORK_SRC','WS02','외주수리', '', 2, 'Y', 'N', NOW())
	 ,('WORK_SRC','WS03','사내/외주수리', '', 3, 'N', 'N', NOW())

	
	-- 모델분석유형
	, ('TASK_TYPE', 'OPTIMIZATION',      '최적화',            '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'TEXT_ANALYSIS',     '텍스트 분석',       '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'IMAGE_ANALYSIS',    '이미지 분석',       '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'ANOMALY',           '이상탐지',           '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'CLASSIFICATION',    '분류',               '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'REGRESSION',        '회귀',               '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'CLUSTERING',        '군집',               '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'TIMESERIES',        '시계열 분석',        '', NULL, 'Y', 'N', NOW())
	, ('TASK_TYPE', 'OTHERS',            '기타',               '', NULL, 'Y', 'N', NOW())

	-- 모델알고리즘종류(전체)
	, ('ALGORITHM_TYPE', 'RANDOM_FOREST',        '랜덤포레스트',         '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'LINEAR_REGRESSION',    '선형회귀',             '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'LOGISTIC_REGRESSION',  '로지스틱 회귀',        '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'XGBOOST',              'XGBoost',              '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'LIGHTGBM',             'LightGBM',             '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'SVM',                  '서포트 벡터 머신',     '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'KNN',                  'K-최근접 이웃',        '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'NAIVE_BAYES',          '나이브 베이즈',        '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'KMEANS',               'K-평균 군집',          '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'TRANSFORMER',          '트랜스포머',           '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'CNN',                  '합성곱 신경망',         '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'RNN',                  '순환 신경망',           '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'LSTM',                 'LSTM',                 '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'MLP',                  '다층 퍼셉트론',         '', NULL, 'Y', 'N', NOW())
	, ('ALGORITHM_TYPE', 'OTHERS',               '기타',                 '', NULL, 'Y', 'N', NOW())
	
	-- 분석유형:분류
	, ('AI_CLASSIFICATION', 'RANDOM_FOREST',       '랜덤포레스트',         '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'LOGISTIC_REGRESSION', '로지스틱 회귀',        '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'XGBOOST',             'XGBoost',              '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'LIGHTGBM',            'LightGBM',             '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'SVM',                 '서포트 벡터 머신',     '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'KNN',                 'K-최근접 이웃',        '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'NAIVE_BAYES',         '나이브 베이즈',        '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'CNN',                 '합성곱 신경망',         '', NULL, 'Y', 'N', NOW())
	, ('AI_CLASSIFICATION', 'MLP',                 '다층 퍼셉트론',         '', NULL, 'Y', 'N', NOW())
	
	-- 분석유형:회귀
	, ('AI_REGRESSION', 'RANDOM_FOREST',       '랜덤포레스트', '', NULL, 'Y', 'N', NOW())
	, ('AI_REGRESSION', 'LINEAR_REGRESSION',   '선형회귀',     '', NULL, 'Y', 'N', NOW())
	, ('AI_REGRESSION', 'XGBOOST',             'XGBoost',      '', NULL, 'Y', 'N', NOW())
	, ('AI_REGRESSION', 'LIGHTGBM',            'LightGBM',     '', NULL, 'Y', 'N', NOW())
	, ('AI_REGRESSION', 'MLP',                 '다층 퍼셉트론', '', NULL, 'Y', 'N', NOW())
	
	-- 분석유형:군집
	, ('AI_CLUSTERING', 'KMEANS', 'K-평균 군집', '', NULL, 'Y', 'N', NOW())
	
	-- 분석유형:시계열 분석
	, ('AI_TIMESERIES', 'LSTM',        'LSTM',         '', NULL, 'Y', 'N', NOW())
	, ('AI_TIMESERIES', 'RNN',         '순환 신경망',   '', NULL, 'Y', 'N', NOW())
	, ('AI_TIMESERIES', 'TRANSFORMER', '트랜스포머',   '', NULL, 'Y', 'N', NOW())
	
	-- 분석유형:이미지 분석
	, ('AI_IMAGE_ANALYSIS', 'CNN', '합성곱 신경망', '', NULL, 'Y', 'N', NOW())
	
	-- 분석유형:텍스트 분석
	, ('AI_TEXT_ANALYSIS', 'RNN',         '순환 신경망', '', NULL, 'Y', 'N', NOW())
	, ('AI_TEXT_ANALYSIS', 'LSTM',        'LSTM',         '', NULL, 'Y', 'N', NOW())
	, ('AI_TEXT_ANALYSIS', 'TRANSFORMER', '트랜스포머',   '', NULL, 'Y', 'N', NOW())

	-- 하이퍼파라미터 값 유형
	, ('PARAM_TYPE', 'STRING', 'string', '', NULL, 'Y', 'N', NOW())
	, ('PARAM_TYPE', 'INT',    'int',    '', NULL, 'Y', 'N', NOW())
	, ('PARAM_TYPE', 'FLOAT',  'float',  '', NULL, 'Y', 'N', NOW())
	, ('PARAM_TYPE', 'BOOL',   'bool',   '', NULL, 'Y', 'N', NOW())
	, ('PARAM_TYPE', 'JSON',   'json',   '', NULL, 'Y', 'N', NOW())

	-- 모델학습상태
	, ('TRAINING_STATUS', 'INITIALIZED', '설정 완료',	'모델 생성(파라미터 저장 완료)',	1, 'Y', 'N', NOW())
	, ('TRAINING_STATUS', 'PENDING',     '학습 대기중',	'학습 요청 완료, 큐에서 대기 중',	2, 'Y', 'N', NOW())
	, ('TRAINING_STATUS', 'TRAINING',    '학습중',		'학습 프로세스 실행 중',			3, 'Y', 'N', NOW())
	, ('TRAINING_STATUS', 'COMPLETED',   '학습 완료',	'학습이 성공적으로 완료됨',			4, 'Y', 'N', NOW())
	, ('TRAINING_STATUS', 'FAILED',      '학습 실패',	'학습 실패 (에러 등 발생)',			5, 'Y', 'N', NOW())
	
	-- AI데이터유형
	, ('AI_DATA_SOURCE', 'PLC', 'PLC태그',	'PLC태그데이터',	1, 'Y', 'N', NOW())	
	, ('AI_DATA_SOURCE', 'EM', '전력량계',	'전력량계 태그데이터',	2, 'Y', 'N', NOW())
	, ('AI_DATA_SOURCE', 'MES', 'MES',		'MES데이터',	3, 'Y', 'N', NOW())	
	, ('AI_DATA_SOURCE', 'QMS', 'QMS',		'QMS데이터',	4, 'Y', 'N', NOW())		
	, ('AI_DATA_SOURCE', 'VISCOSITY', '점도',	'도료의 점성 정도',	5, 'Y', 'N', NOW())	
	, ('AI_DATA_SOURCE', 'TENTION', '장력',		'납을 당기는 정도',	6, 'Y', 'N', NOW())	
	, ('AI_DATA_SOURCE', 'PROFILE', '프로파일',	'프로파일데이터',	7, 'Y', 'N', NOW())	
	, ('AI_DATA_SOURCE', 'USER', '사용자설정',	'사용자설정데이터',	8, 'Y', 'N', NOW())	
	;


-- 유저코드(code) Attr1 사용하는 데이터
INSERT INTO code("CodeGroupCode", "Code", "Name", "Remark", "DispOrder", "UseYn", "DelYn", "_created", "Attr1") VALUES
	-- AI알고리즘별	- RandomForest 파라미터
	('RANDOM_FOREST','N_ESTIMATORS','트리 개수','기본 100',1,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','MAX_DEPTH','최대 깊이','기본 None',2,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','MIN_SAMPLES_SPLIT','최소 분할 샘플 수','기본 2',3,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','MIN_SAMPLES_LEAF','최소 리프 샘플 수','기본 1',4,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','MAX_FEATURES','최대 특성 수','기본 auto',5,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','BOOTSTRAP','부트스트랩 사용여부','기본 True',6,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','RANDOM_STATE','랜덤 시드','기본 42',7,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','MAX_SAMPLES','부트스트랩 샘플 비율','기본 None (전체 샘플)',8,'Y','N',NOW(),'')
	, ('RANDOM_FOREST','CLASS_WEIGHT','클래스 가중치','기본 balanced / 불량 클래스 부족 시, 가중치 조절용(불량 클래스에만 부여)',9,'Y','N',NOW(),'CLASSIFICATION')
	, ('RANDOM_FOREST','CRITERION','분할 기준','기본 squared_error',10,'Y','N',NOW(),'REGRESSION')

	-- 25.07.29 김하늘 추가
	-- AI알고리즘별	- Logistic Regression 파라미터
	, ('LOGISTIC_REGRESSION', 'PENALTY', '정규화 방식', '기본 l2', 1, 'Y', 'N', NOW(), '')
	, ('LOGISTIC_REGRESSION', 'C', '정규화 강도', '기본 1.0 (작을수록 규제 강함)', 2, 'Y', 'N', NOW(), '')
	, ('LOGISTIC_REGRESSION', 'SOLVER', '최적화 알고리즘', '기본 lbfgs', 3, 'Y', 'N', NOW(), '')
	, ('LOGISTIC_REGRESSION', 'MAX_ITER', '최대 반복 횟수', '기본 100', 4, 'Y', 'N', NOW(), '')
	, ('LOGISTIC_REGRESSION', 'CLASS_WEIGHT', '클래스 가중치', '기본 None / balanced 선택 가능', 5, 'Y', 'N', NOW(), 'CLASSIFICATION')

	-- AI알고리즘별	- XGBoost 파라미터
	, ('XGBOOST', 'N_ESTIMATORS', '트리 개수', '기본 100', 1, 'Y', 'N', NOW(), '')
	, ('XGBOOST', 'MAX_DEPTH', '트리 최대 깊이', '기본 6', 2, 'Y', 'N', NOW(), '')
	, ('XGBOOST', 'MIN_CHILD_WEIGHT', '리프 노드 최소 가중치 합', '기본 1', 3, 'Y', 'N', NOW(), '')
	, ('XGBOOST', 'GAMMA', '추가 분할 최소 손실 감소량', '기본 0', 4, 'Y', 'N', NOW(), '')
	, ('XGBOOST', 'LEARNING_RATE', '학습률 (eta)', '기본 0.3', 5, 'Y', 'N', NOW(), '')
	, ('XGBOOST', 'SUBSAMPLE', '데이터 샘플링 비율', '기본 1.0', 6, 'Y', 'N', NOW(), '')
	, ('XGBOOST', 'COLSAMPLE_BYTREE', '특성 샘플링 비율', '기본 1.0', 7, 'Y', 'N', NOW(), '')
	, ('XGBOOST', 'SCALE_POS_WEIGHT', '클래스 불균형 가중치', '기본 1', 8, 'Y', 'N', NOW(), 'CLASSIFICATION')

	-- AI알고리즘별	- LightGBM 파라미터
	, ('LIGHTGBM', 'N_ESTIMATORS', '트리 개수', '기본 100', 1, 'Y', 'N', NOW(), '')
	, ('LIGHTGBM', 'MAX_DEPTH', '트리 최대 깊이', '기본 -1 (제한 없음)', 2, 'Y', 'N', NOW(), '')
	, ('LIGHTGBM', 'LEARNING_RATE', '학습률', '기본 0.1', 3, 'Y', 'N', NOW(), '')
	, ('LIGHTGBM', 'NUM_LEAVES', '리프 노드 수', '기본 31', 4, 'Y', 'N', NOW(), '')
	, ('LIGHTGBM', 'SUBSAMPLE', '데이터 샘플링 비율', '기본 1.0', 5, 'Y', 'N', NOW(), '')
	, ('LIGHTGBM', 'COLSAMPLE_BYTREE', '특성 샘플링 비율', '기본 1.0', 6, 'Y', 'N', NOW(), '')
	, ('LIGHTGBM', 'MIN_CHILD_SAMPLES', '리프 최소 샘플 수', '기본 20', 7, 'Y', 'N', NOW(), '')
	, ('LIGHTGBM', 'CLASS_WEIGHT', '클래스 불균형 가중치', '기본 balanced / 불량 클래스 부족 시, 가중치 조절용(불량 클래스에만 부여)', 8, 'Y', 'N', NOW(), 'CLASSIFICATION')

	-- AI알고리즘별	- SVM 파라미터
	, ('SVM', 'KERNEL', '커널 종류', '기본 rbf', 1, 'Y', 'N', NOW(), '')
	, ('SVM', 'C', '규제 강도', '기본 1.0', 2, 'Y', 'N', NOW(), '')
	, ('SVM', 'GAMMA', '커널 계수', '기본 scale', 3, 'Y', 'N', NOW(), '')
	, ('SVM', 'CLASS_WEIGHT', '클래스 가중치', '기본 None', 4, 'Y', 'N', NOW(), 'CLASSIFICATION')
	, ('SVM', 'EPSILON', '회귀 허용 오차', '기본 0.1', 5, 'Y', 'N', NOW(), 'REGRESSION')

	-- AI알고리즘별	- KNN 파라미터
	, ('KNN', 'N_NEIGHBORS', '최근접 이웃 수', '기본 5', 1, 'Y', 'N', NOW(), '')
	, ('KNN', 'WEIGHTS', '가중치 방식', '기본 uniform', 2, 'Y', 'N', NOW(), '')
	, ('KNN', 'METRIC', '거리 계산 기준', '기본 minkowski', 3, 'Y', 'N', NOW(), '')

	-- AI알고리즘별	- Naive Bayes 파라미터
	, ('NAIVE_BAYES', 'VAR_SMOOTHING', '수치 안정화 계수', '기본 1e-9', 1, 'Y', 'N', NOW(), '')
	
	-- AI알고리즘별	- MLP 파라미터
	, ('MLP', 'HIDDEN_LAYER_SIZES', '은닉층 구조', '기본 (100,)', 1, 'Y', 'N', NOW(), '')
	, ('MLP', 'ACTIVATION', '활성화 함수', '기본 relu', 2, 'Y', 'N', NOW(), '')
	, ('MLP', 'SOLVER', '최적화 알고리즘', '기본 adam', 3, 'Y', 'N', NOW(), '')
	, ('MLP', 'LEARNING_RATE_INIT', '초기 학습률', '기본 0.001', 4, 'Y', 'N', NOW(), '')
	, ('MLP', 'MAX_ITER', '최대 반복 횟수', '기본 200', 5, 'Y', 'N', NOW(), '')
	, ('MLP', 'ALPHA', 'L2 규제 강도', '기본 0.0001', 6, 'Y', 'N', NOW(), '')
;


--품목
--alter SEQUENCE material_id_seq restart WITH 1;

--// 아래 품목그룸 코드를 mat_grp 테이블에 insert하는 구문을 작성
/*
--품목그룹
ESC_MGH60
ABS_MGH60
ESC-P_MGH60
SPAS
MAS35C
MAS65C
MOC
P/PACK
TOS/TAS
SRR
SPM
Yaw&G
ESC_MGH80
ABS_MGH80
MAS85C
LRR
FPC
ESC_MGH85
FCM
MRR
ABS_MGH100
ESC_MGH100
IDB
AOI
E-Coupling
PCU
*/
insert into mat_grp ("Code","Name", _created) 
values
('ESC_MGH60', 'ESC_MGH60', now()),
('ABS_MGH60', 'ABS_MGH60', now()),
('ESC-P_MGH60', 'ESC-P_MGH60', now()),
('SPAS', 'SPAS', now()),
('MAS35C', 'MAS35C', now()),
('MAS65C', 'MAS65C', now()),
('MOC', 'MOC', now()),
('P/PACK', 'P/PACK', now()),
('TOS/TAS', 'TOS/TAS', now()),
('SRR', 'SRR', now()),
('SPM', 'SPM', now()),
('Yaw&G', 'Yaw&G', now()),
('ESC_MGH80', 'ESC_MGH80', now()),
('ABS_MGH80', 'ABS_MGH80', now()),
('MAS85C', 'MAS85C', now()),
('LRR','LRR' ,now()),
('FPC','FPC' ,now()),
('ESC_MGH85','ESC_MGH85' ,now()),
('FCM','FCM' ,now()),
('MRR','MRR' ,now()),
('ABS_MGH100','ABS_MGH100' ,now()),
('ESC_MGH100','ESC_MGH100' ,now()),
('IDB','IDB' ,now()),
('AOI','AOI' ,now()),
('E-Coupling','E-Coupling' ,now()),
('PCU','PCU' ,now());



--업체 정보
alter SEQUENCE company_id_seq restart WITH 1;
INSERT INTO company ("Name","Code","Country","Local","CompanyType","CEOName","Email","ZipCode",addr,"TelNumber","FaxNumber","BusinessType","BusinessItem","Homepage","Description","Manager","ManagerPhone","Manager2","Manager2Phone","UseYn","DelYn","UserText1","UserText2","UserText3","UserText4","UserText5","_status","_created","_modified","_creater_id","_modifier_id","_creater_nm","_modifier_nm","Site_id") VALUES
	 ('위존','wezon','','','S','','','','','','','SW','','','','','','','','Y','N',NULL,NULL,NULL,NULL,NULL,NULL,'2025-03-17 11:10:28.692624+09','2025-03-17 11:10:28.692624+09',1,1,'위존','위존',NULL),
	 ('열린기술','YULLIN','','','S','','','','','','','SW','','','','','','','','Y','N',NULL,NULL,NULL,NULL,NULL,NULL,'2025-03-17 11:10:45.752357+09','2025-03-17 11:11:00.873981+09',1,1,'위존','위존',NULL);


-- AI 모델마스터	25.05.08 수정
alter SEQUENCE ds_master_id_seq restart WITH 1;
INSERT INTO ds_master ("Name", "Type", "_status", "_created", "_modified", "_creater_id", "_modifier_id", "_creater_nm", "_modifier_nm") VALUES
	('hpc1_플래쉬_Q', 'Q-factor', NULL, '2025-02-06 14:18:12.035', '2025-02-06 14:18:12.035', 3, 3, NULL, NULL),
	('hpc1_매거진_Q', 'Q-factor', NULL, '2025-02-06 14:50:59.140', '2025-02-06 14:50:59.140', 3, 3, NULL, NULL),
	('hpc1_ICT_Q', 'Q-factor', NULL, '2025-02-06 14:50:59.140', '2025-02-06 14:50:59.140', 3, 3, NULL, NULL);

-- 휴일 정보
CREATE TABLE cm_holiday_info (
	nation_cd varchar(10) NOT NULL,
	year_val varchar(4) NOT NULL,
	month_val varchar(2) NOT NULL,
	day_val varchar(2) NOT NULL,
	type_val varchar(1) DEFAULT 'H'::character varying NULL,
	name_val varchar(100) NOT NULL,
	CONSTRAINT cm_holiday_info_pk PRIMARY KEY (nation_cd, year_val, month_val, day_val)
);
INSERT INTO cm_holiday_info (nation_cd,year_val,month_val,day_val,type_val,name_val) VALUES
	 ('en','2020','01','01','h','신정'),
	 ('en','2020','01','24','h','설날연휴'),
	 ('en','2020','01','25','h','설날'),
	 ('en','2020','01','27','h','대체 휴일'),
	 ('en','2020','03','01','h','삼일절'),
	 ('en','2020','04','15','h','제21대 국회의원 선거'),
	 ('en','2020','04','30','h','석가탄신일'),
	 ('en','2020','05','05','h','어린이날'),
	 ('en','2020','06','06','h','현충일'),
	 ('en','2020','08','15','h','광복절'),
	 ('en','2020','09','30','h','추석연휴'),
	 ('en','2020','10','01','h','추석'),
	 ('en','2020','10','02','h','추석연휴'),
	 ('en','2020','10','03','h','개천절'),
	 ('en','2020','10','09','h','한글날'),
	 ('en','2020','12','25','h','성탄절'),
	 ('en','2021','01','01','h','신정'),
	 ('en','2021','02','11','h','설날연휴'),
	 ('en','2021','02','12','h','설날'),
	 ('en','2021','03','01','h','삼일절'),
	 ('en','2021','05','05','h','어린이날'),
	 ('en','2021','05','19','h','석가탄신일'),
	 ('en','2021','06','06','h','현충일'),
	 ('en','2021','08','15','h','광복절'),
	 ('en','2021','09','20','h','추석연휴'),
	 ('en','2021','09','21','h','추석'),
	 ('en','2021','09','22','h','추석연휴'),
	 ('en','2021','10','03','h','개천절'),
	 ('en','2021','10','09','h','한글날'),
	 ('en','2021','12','25','h','성탄절'),
	 ('en','2022','01','01','h','1월1일'),
	 ('en','2022','01','31','h','설날'),
	 ('en','2022','02','01','h','설날'),
	 ('en','2022','02','02','h','설날'),
	 ('en','2022','03','01','h','삼일절'),
	 ('en','2022','03','09','h','대통령선거일'),
	 ('en','2022','05','05','h','어린이날'),
	 ('en','2022','05','08','h','부처님오신날'),
	 ('en','2022','06','01','h','전국동시지방선거'),
	 ('en','2022','06','06','h','현충일'),
	 ('en','2022','08','15','h','광복절'),
	 ('en','2022','09','09','h','추석'),
	 ('en','2022','09','10','h','추석'),
	 ('en','2022','09','11','h','추석'),
	 ('en','2022','09','12','h','대체공휴일'),
	 ('en','2022','10','03','h','개천절'),
	 ('en','2022','10','09','h','한글날'),
	 ('en','2022','12','25','h','기독탄신일'),
	 ('en','2023','01','01','h','신정'),
	 ('en','2023','01','22','h','설날'),
	 ('en','2023','03','01','h','삼일절'),
	 ('en','2023','05','05','h','어린이날'),
	 ('en','2023','05','27','h','석가탄신일'),
	 ('en','2023','06','06','h','현충일'),
	 ('en','2023','08','15','h','광복절'),
	 ('en','2023','09','28','h','추석연휴'),
	 ('en','2023','09','29','h','추석'),
	 ('en','2023','10','03','h','개천절'),
	 ('en','2023','10','09','h','한글날'),
	 ('en','2023','12','25','h','성탄절'),
	 ('en','2024','01','01','h','신정'),
	 ('en','2024','02','09','h','설날연휴'),
	 ('en','2024','02','10','h','설날'),
	 ('en','2024','03','01','h','삼일절'),
	 ('en','2024','04','10','h','22대 국회의원 선거'),
	 ('en','2024','05','05','h','어린이날'),
	 ('en','2024','05','15','h','석가탄신일'),
	 ('en','2024','06','06','h','현충일'),
	 ('en','2024','08','15','h','광복절'),
	 ('en','2024','09','16','h','추석연휴'),
	 ('en','2024','09','17','h','추석'),
	 ('en','2024','09','18','h','추석연휴'),
	 ('en','2024','10','03','h','개천절'),
	 ('en','2024','10','09','h','한글날'),
	 ('en','2024','12','25','h','성탄절'),
	 ('en','2025','01','01','h','신정'),
	 ('en','2025','01','28','h','설날연휴'),
	 ('en','2025','01','29','h','설날'),
	 ('en','2025','01','30','h','설날연휴'),
	 ('en','2025','03','01','h','삼일절'),
	 ('en','2025','05','05','h','어린이날,석가탄신일'),
	 ('en','2025','06','06','h','현충일'),
	 ('en','2025','08','15','h','광복절'),
	 ('en','2025','10','03','h','개천절'),
	 ('en','2025','10','06','h','추석'),
	 ('en','2025','10','07','h','추석연휴'),
	 ('en','2025','10','09','h','한글날'),
	 ('en','2025','12','25','h','성탄절'),
	 ('en','2026','01','01','h','신정'),
	 ('en','2026','02','16','h','설날연휴'),
	 ('en','2026','02','17','h','설날'),
	 ('en','2026','02','18','h','설날연휴'),
	 ('en','2026','03','01','h','삼일절'),
	 ('en','2026','05','05','h','어린이날'),
	 ('en','2026','05','24','h','석가탄신일'),
	 ('en','2026','06','06','h','현충일'),
	 ('en','2026','08','15','h','광복절'),
	 ('en','2026','09','24','h','추석연휴'),
	 ('en','2026','09','25','h','추석'),
	 ('en','2026','10','03','h','개천절'),
	 ('en','2026','10','09','h','한글날'),
	 ('en','2026','12','25','h','성탄절'),
	 ('en','2027','01','01','h','신정'),
	 ('en','2027','02','07','h','설날'),
	 ('en','2027','03','01','h','삼일절'),
	 ('en','2027','05','05','h','어린이날'),
	 ('en','2027','05','13','h','석가탄신일'),
	 ('en','2027','06','06','h','현충일'),
	 ('en','2027','08','15','h','광복절'),
	 ('en','2027','09','14','h','추석연휴'),
	 ('en','2027','09','15','h','추석'),
	 ('en','2027','09','16','h','추석연휴'),
	 ('en','2027','10','03','h','개천절'),
	 ('en','2027','10','09','h','한글날'),
	 ('en','2027','12','25','h','성탄절'),
	 ('en','2028','01','01','h','신정'),
	 ('en','2028','01','26','h','설날연휴'),
	 ('en','2028','01','27','h','설날'),
	 ('en','2028','01','28','h','설날연휴'),
	 ('en','2028','03','01','h','삼일절'),
	 ('en','2028','05','02','h','석가탄신일'),
	 ('en','2028','05','05','h','어린이날'),
	 ('en','2028','06','06','h','현충일'),
	 ('en','2028','08','15','h','광복절'),
	 ('en','2028','10','02','h','추석연휴'),
	 ('en','2028','10','03','h','추석,개천절'),
	 ('en','2028','10','04','h','추석연휴'),
	 ('en','2028','10','09','h','한글날'),
	 ('en','2028','12','25','h','성탄절'),
	 ('en','2029','01','01','h','신정'),
	 ('en','2029','02','12','h','설날연휴'),
	 ('en','2029','02','13','h','설날'),
	 ('en','2029','02','14','h','설날연휴'),
	 ('en','2029','03','01','h','삼일절'),
	 ('en','2029','05','05','h','어린이날'),
	 ('en','2029','05','20','h','석가탄신일'),
	 ('en','2029','06','06','h','현충일'),
	 ('en','2029','08','15','h','광복절'),
	 ('en','2029','09','21','h','추석연휴'),
	 ('en','2029','09','22','h','추석'),
	 ('en','2029','10','03','h','개천절'),
	 ('en','2029','10','09','h','한글날'),
	 ('en','2029','12','25','h','성탄절'),
	 ('en','2030','01','01','h','신정'),
	 ('en','2030','02','03','h','설날'),
	 ('en','2030','03','01','h','삼일절'),
	 ('en','2030','05','05','h','어린이날'),
	 ('en','2030','05','09','h','석가탄신일'),
	 ('en','2030','06','06','h','현충일'),
	 ('en','2030','08','15','h','광복절'),
	 ('en','2030','09','11','h','추석연휴'),
	 ('en','2030','09','12','h','추석'),
	 ('en','2030','09','13','h','추석연휴'),
	 ('en','2030','10','03','h','개천절'),
	 ('en','2030','10','09','h','한글날'),
	 ('en','2030','12','25','h','성탄절'),
	 ('en','2031','01','01','h','신정'),
	 ('en','2031','01','22','h','설날연휴'),
	 ('en','2031','01','23','h','설날'),
	 ('en','2031','01','24','h','설날연휴'),
	 ('en','2031','03','01','h','삼일절'),
	 ('en','2031','05','05','h','어린이날'),
	 ('en','2031','05','28','h','석가탄신일'),
	 ('en','2031','06','06','h','현충일'),
	 ('en','2031','08','15','h','광복절'),
	 ('en','2031','09','30','h','추석연휴'),
	 ('en','2031','10','01','h','추석'),
	 ('en','2031','10','02','h','추석연휴'),
	 ('en','2031','10','03','h','개천절'),
	 ('en','2031','10','09','h','한글날'),
	 ('en','2031','12','25','h','성탄절'),
	 ('en','2032','01','01','h','신정'),
	 ('en','2032','02','10','h','설날연휴'),
	 ('en','2032','02','11','h','설날'),
	 ('en','2032','02','12','h','설날연휴'),
	 ('en','2032','03','01','h','삼일절'),
	 ('en','2032','05','05','h','어린이날'),
	 ('en','2032','05','16','h','석가탄신일'),
	 ('en','2032','06','06','h','현충일'),
	 ('en','2032','08','15','h','광복절'),
	 ('en','2032','09','19','h','추석'),
	 ('en','2032','10','03','h','개천절'),
	 ('en','2032','10','09','h','한글날'),
	 ('en','2032','12','25','h','성탄절'),
	 ('en','2033','01','01','h','신정'),
	 ('en','2033','01','31','h','설날'),
	 ('en','2033','02','01','h','설날연휴'),
	 ('en','2033','03','01','h','삼일절'),
	 ('en','2033','05','05','h','어린이날'),
	 ('en','2033','05','06','h','석가탄신일'),
	 ('en','2033','06','06','h','현충일'),
	 ('en','2033','08','15','h','광복절'),
	 ('en','2033','09','07','h','추석연휴'),
	 ('en','2033','09','08','h','추석'),
	 ('en','2033','09','09','h','추석연휴'),
	 ('en','2033','10','03','h','개천절'),
	 ('en','2033','10','09','h','한글날'),
	 ('en','2033','12','25','h','성탄절'),
	 ('en','2034','01','01','h','신정'),
	 ('en','2034','02','19','h','설날'),
	 ('en','2034','02','20','h','설날연휴'),
	 ('en','2034','03','01','h','삼일절'),
	 ('en','2034','05','05','h','어린이날'),
	 ('en','2034','05','25','h','석가탄신일'),
	 ('en','2034','06','06','h','현충일'),
	 ('en','2034','08','15','h','광복절'),
	 ('en','2034','09','26','h','추석연휴'),
	 ('en','2034','09','27','h','추석'),
	 ('en','2034','09','28','h','추석연휴'),
	 ('en','2034','10','03','h','개천절'),
	 ('en','2034','10','09','h','한글날'),
	 ('en','2034','12','25','h','성탄절'),
	 ('en','2035','01','01','h','신정'),
	 ('en','2035','02','07','h','설날연휴'),
	 ('en','2035','02','08','h','설날'),
	 ('en','2035','02','09','h','설날연휴'),
	 ('en','2035','03','01','h','삼일절'),
	 ('en','2035','05','05','h','어린이날'),
	 ('en','2035','05','15','h','석가탄신일'),
	 ('en','2035','06','06','h','현충일'),
	 ('en','2035','08','15','h','광복절'),
	 ('en','2035','09','16','h','추석'),
	 ('en','2035','10','03','h','개천절'),
	 ('en','2035','10','09','h','한글날'),
	 ('en','2035','12','25','h','성탄절'),
	 ('en','2036','01','01','h','신정'),
	 ('en','2036','01','28','h','설날'),
	 ('en','2036','01','29','h','설날연휴'),
	 ('en','2036','03','01','h','삼일절'),
	 ('en','2036','05','03','h','석가탄신일'),
	 ('en','2036','05','05','h','어린이날'),
	 ('en','2036','06','06','h','현충일'),
	 ('en','2036','08','15','h','광복절'),
	 ('en','2036','10','03','h','개천절'),
	 ('en','2036','10','04','h','추석'),
	 ('en','2036','10','09','h','한글날'),
	 ('en','2036','12','25','h','성탄절'),
	 ('en','2037','01','01','h','신정'),
	 ('en','2037','02','15','h','설날'),
	 ('en','2037','03','01','h','삼일절'),
	 ('en','2037','05','05','h','어린이날'),
	 ('en','2037','05','22','h','석가탄신일'),
	 ('en','2037','06','06','h','현충일'),
	 ('en','2037','08','15','h','광복절'),
	 ('en','2037','09','23','h','추석연휴'),
	 ('en','2037','09','24','h','추석'),
	 ('en','2037','09','25','h','추석연휴'),
	 ('en','2037','10','03','h','개천절'),
	 ('en','2037','10','09','h','한글날'),
	 ('en','2037','12','25','h','성탄절'),
	 ('ko','2020','01','01','h','신정'),
	 ('ko','2020','01','24','h','설날연휴'),
	 ('ko','2020','01','25','h','설날'),
	 ('ko','2020','01','27','h','대체 휴일'),
	 ('ko','2020','03','01','h','삼일절'),
	 ('ko','2020','04','15','h','제21대 국회의원 선거'),
	 ('ko','2020','04','30','h','석가탄신일'),
	 ('ko','2020','05','05','h','어린이날'),
	 ('ko','2020','06','06','h','현충일'),
	 ('ko','2020','08','15','h','광복절'),
	 ('ko','2020','09','30','h','추석연휴'),
	 ('ko','2020','10','01','h','추석'),
	 ('ko','2020','10','02','h','추석연휴'),
	 ('ko','2020','10','03','h','개천절'),
	 ('ko','2020','10','09','h','한글날'),
	 ('ko','2020','12','25','h','성탄절'),
	 ('ko','2021','01','01','h','신정'),
	 ('ko','2021','02','11','h','설날연휴'),
	 ('ko','2021','02','12','h','설날'),
	 ('ko','2021','03','01','h','삼일절'),
	 ('ko','2021','05','05','h','어린이날'),
	 ('ko','2021','05','19','h','석가탄신일'),
	 ('ko','2021','06','06','h','현충일'),
	 ('ko','2021','08','15','h','광복절'),
	 ('ko','2021','09','20','h','추석연휴'),
	 ('ko','2021','09','21','h','추석'),
	 ('ko','2021','09','22','h','추석연휴'),
	 ('ko','2021','10','03','h','개천절'),
	 ('ko','2021','10','09','h','한글날'),
	 ('ko','2021','12','25','h','성탄절'),
	 ('ko','2022','01','01','h','신정'),
	 ('ko','2022','01','31','h','설날연휴'),
	 ('ko','2022','02','01','h','설날'),
	 ('ko','2022','02','02','h','설날연휴'),
	 ('ko','2022','03','01','h','삼일절'),
	 ('ko','2022','03','09','h','대통령선거'),
	 ('ko','2022','05','05','h','어린이날'),
	 ('ko','2022','05','08','h','석가탄신일'),
	 ('ko','2022','06','01','h','지방선거'),
	 ('ko','2022','06','06','h','현충일'),
	 ('ko','2022','08','15','h','광복절'),
	 ('ko','2022','09','09','h','추석연휴'),
	 ('ko','2022','09','10','h','추석'),
	 ('ko','2022','10','03','h','개천절'),
	 ('ko','2022','10','09','h','한글날'),
	 ('ko','2022','12','25','h','성탄절'),
	 ('ko','2023','01','01','h','신정'),
	 ('ko','2023','01','22','h','설날'),
	 ('ko','2023','03','01','h','삼일절'),
	 ('ko','2023','05','05','h','어린이날'),
	 ('ko','2023','05','27','h','석가탄신일'),
	 ('ko','2023','06','06','h','현충일'),
	 ('ko','2023','08','15','h','광복절'),
	 ('ko','2023','09','28','h','추석연휴'),
	 ('ko','2023','09','29','h','추석'),
	 ('ko','2023','10','03','h','개천절'),
	 ('ko','2023','10','09','h','한글날'),
	 ('ko','2023','12','25','h','성탄절'),
	 ('ko','2024','01','01','h','신정'),
	 ('ko','2024','02','09','h','설날연휴'),
	 ('ko','2024','02','10','h','설날'),
	 ('ko','2024','03','01','h','삼일절'),
	 ('ko','2024','04','10','h','22대 국회의원 선거'),
	 ('ko','2024','05','05','h','어린이날'),
	 ('ko','2024','05','15','h','석가탄신일'),
	 ('ko','2024','06','06','h','현충일'),
	 ('ko','2024','08','15','h','광복절'),
	 ('ko','2024','09','16','h','추석연휴'),
	 ('ko','2024','09','17','h','추석'),
	 ('ko','2024','09','18','h','추석연휴'),
	 ('ko','2024','10','03','h','개천절'),
	 ('ko','2024','10','09','h','한글날'),
	 ('ko','2024','12','25','h','성탄절'),
	 ('ko','2025','01','01','h','신정'),
	 ('ko','2025','01','28','h','설날연휴'),
	 ('ko','2025','01','29','h','설날'),
	 ('ko','2025','01','30','h','설날연휴'),
	 ('ko','2025','03','01','h','삼일절'),
	 ('ko','2025','05','05','h','어린이날,석가탄신일'),
	 ('ko','2025','06','06','h','현충일'),
	 ('ko','2025','08','15','h','광복절'),
	 ('ko','2025','10','03','h','개천절'),
	 ('ko','2025','10','06','h','추석'),
	 ('ko','2025','10','07','h','추석연휴'),
	 ('ko','2025','10','09','h','한글날'),
	 ('ko','2025','12','25','h','성탄절'),
	 ('ko','2026','01','01','h','신정'),
	 ('ko','2026','02','16','h','설날연휴'),
	 ('ko','2026','02','17','h','설날'),
	 ('ko','2026','02','18','h','설날연휴'),
	 ('ko','2026','03','01','h','삼일절'),
	 ('ko','2026','05','05','h','어린이날'),
	 ('ko','2026','05','24','h','석가탄신일'),
	 ('ko','2026','06','06','h','현충일'),
	 ('ko','2026','08','15','h','광복절'),
	 ('ko','2026','09','24','h','추석연휴'),
	 ('ko','2026','09','25','h','추석'),
	 ('ko','2026','10','03','h','개천절'),
	 ('ko','2026','10','09','h','한글날'),
	 ('ko','2026','12','25','h','성탄절'),
	 ('ko','2027','01','01','h','신정'),
	 ('ko','2027','02','07','h','설날'),
	 ('ko','2027','03','01','h','삼일절'),
	 ('ko','2027','05','05','h','어린이날'),
	 ('ko','2027','05','13','h','석가탄신일'),
	 ('ko','2027','06','06','h','현충일'),
	 ('ko','2027','08','15','h','광복절'),
	 ('ko','2027','09','14','h','추석연휴'),
	 ('ko','2027','09','15','h','추석'),
	 ('ko','2027','09','16','h','추석연휴'),
	 ('ko','2027','10','03','h','개천절'),
	 ('ko','2027','10','09','h','한글날'),
	 ('ko','2027','12','25','h','성탄절'),
	 ('ko','2028','01','01','h','신정'),
	 ('ko','2028','01','26','h','설날연휴'),
	 ('ko','2028','01','27','h','설날'),
	 ('ko','2028','01','28','h','설날연휴'),
	 ('ko','2028','03','01','h','삼일절'),
	 ('ko','2028','05','02','h','석가탄신일'),
	 ('ko','2028','05','05','h','어린이날'),
	 ('ko','2028','06','06','h','현충일'),
	 ('ko','2028','08','15','h','광복절'),
	 ('ko','2028','10','02','h','추석연휴'),
	 ('ko','2028','10','03','h','추석,개천절'),
	 ('ko','2028','10','04','h','추석연휴'),
	 ('ko','2028','10','09','h','한글날'),
	 ('ko','2028','12','25','h','성탄절'),
	 ('ko','2029','01','01','h','신정'),
	 ('ko','2029','02','12','h','설날연휴'),
	 ('ko','2029','02','13','h','설날'),
	 ('ko','2029','02','14','h','설날연휴'),
	 ('ko','2029','03','01','h','삼일절'),
	 ('ko','2029','05','05','h','어린이날'),
	 ('ko','2029','05','20','h','석가탄신일'),
	 ('ko','2029','06','06','h','현충일'),
	 ('ko','2029','08','15','h','광복절'),
	 ('ko','2029','09','21','h','추석연휴'),
	 ('ko','2029','09','22','h','추석'),
	 ('ko','2029','10','03','h','개천절'),
	 ('ko','2029','10','09','h','한글날'),
	 ('ko','2029','12','25','h','성탄절'),
	 ('ko','2030','01','01','h','신정'),
	 ('ko','2030','02','03','h','설날'),
	 ('ko','2030','03','01','h','삼일절'),
	 ('ko','2030','05','05','h','어린이날'),
	 ('ko','2030','05','09','h','석가탄신일'),
	 ('ko','2030','06','06','h','현충일'),
	 ('ko','2030','08','15','h','광복절'),
	 ('ko','2030','09','11','h','추석연휴'),
	 ('ko','2030','09','12','h','추석'),
	 ('ko','2030','09','13','h','추석연휴'),
	 ('ko','2030','10','03','h','개천절'),
	 ('ko','2030','10','09','h','한글날'),
	 ('ko','2030','12','25','h','성탄절'),
	 ('ko','2031','01','01','h','신정'),
	 ('ko','2031','01','22','h','설날연휴'),
	 ('ko','2031','01','23','h','설날'),
	 ('ko','2031','01','24','h','설날연휴'),
	 ('ko','2031','03','01','h','삼일절'),
	 ('ko','2031','05','05','h','어린이날'),
	 ('ko','2031','05','28','h','석가탄신일'),
	 ('ko','2031','06','06','h','현충일'),
	 ('ko','2031','08','15','h','광복절'),
	 ('ko','2031','09','30','h','추석연휴'),
	 ('ko','2031','10','01','h','추석'),
	 ('ko','2031','10','02','h','추석연휴'),
	 ('ko','2031','10','03','h','개천절'),
	 ('ko','2031','10','09','h','한글날'),
	 ('ko','2031','12','25','h','성탄절'),
	 ('ko','2032','01','01','h','신정'),
	 ('ko','2032','02','10','h','설날연휴'),
	 ('ko','2032','02','11','h','설날'),
	 ('ko','2032','02','12','h','설날연휴'),
	 ('ko','2032','03','01','h','삼일절'),
	 ('ko','2032','05','05','h','어린이날'),
	 ('ko','2032','05','16','h','석가탄신일'),
	 ('ko','2032','06','06','h','현충일'),
	 ('ko','2032','08','15','h','광복절'),
	 ('ko','2032','09','19','h','추석'),
	 ('ko','2032','10','03','h','개천절'),
	 ('ko','2032','10','09','h','한글날'),
	 ('ko','2032','12','25','h','성탄절'),
	 ('ko','2033','01','01','h','신정'),
	 ('ko','2033','01','31','h','설날'),
	 ('ko','2033','02','01','h','설날연휴'),
	 ('ko','2033','03','01','h','삼일절'),
	 ('ko','2033','05','05','h','어린이날'),
	 ('ko','2033','05','06','h','석가탄신일'),
	 ('ko','2033','06','06','h','현충일'),
	 ('ko','2033','08','15','h','광복절'),
	 ('ko','2033','09','07','h','추석연휴'),
	 ('ko','2033','09','08','h','추석'),
	 ('ko','2033','09','09','h','추석연휴'),
	 ('ko','2033','10','03','h','개천절'),
	 ('ko','2033','10','09','h','한글날'),
	 ('ko','2033','12','25','h','성탄절'),
	 ('ko','2034','01','01','h','신정'),
	 ('ko','2034','02','19','h','설날'),
	 ('ko','2034','02','20','h','설날연휴'),
	 ('ko','2034','03','01','h','삼일절'),
	 ('ko','2034','05','05','h','어린이날'),
	 ('ko','2034','05','25','h','석가탄신일'),
	 ('ko','2034','06','06','h','현충일'),
	 ('ko','2034','08','15','h','광복절'),
	 ('ko','2034','09','26','h','추석연휴'),
	 ('ko','2034','09','27','h','추석'),
	 ('ko','2034','09','28','h','추석연휴'),
	 ('ko','2034','10','03','h','개천절'),
	 ('ko','2034','10','09','h','한글날'),
	 ('ko','2034','12','25','h','성탄절'),
	 ('ko','2035','01','01','h','신정'),
	 ('ko','2035','02','07','h','설날연휴'),
	 ('ko','2035','02','08','h','설날'),
	 ('ko','2035','02','09','h','설날연휴'),
	 ('ko','2035','03','01','h','삼일절'),
	 ('ko','2035','05','05','h','어린이날'),
	 ('ko','2035','05','15','h','석가탄신일'),
	 ('ko','2035','06','06','h','현충일'),
	 ('ko','2035','08','15','h','광복절'),
	 ('ko','2035','09','16','h','추석'),
	 ('ko','2035','10','03','h','개천절'),
	 ('ko','2035','10','09','h','한글날'),
	 ('ko','2035','12','25','h','성탄절'),
	 ('ko','2036','01','01','h','신정'),
	 ('ko','2036','01','28','h','설날'),
	 ('ko','2036','01','29','h','설날연휴'),
	 ('ko','2036','03','01','h','삼일절'),
	 ('ko','2036','05','03','h','석가탄신일'),
	 ('ko','2036','05','05','h','어린이날'),
	 ('ko','2036','06','06','h','현충일'),
	 ('ko','2036','08','15','h','광복절'),
	 ('ko','2036','10','03','h','개천절'),
	 ('ko','2036','10','04','h','추석'),
	 ('ko','2036','10','09','h','한글날'),
	 ('ko','2036','12','25','h','성탄절'),
	 ('ko','2037','01','01','h','신정'),
	 ('ko','2037','02','15','h','설날'),
	 ('ko','2037','03','01','h','삼일절'),
	 ('ko','2037','05','05','h','어린이날'),
	 ('ko','2037','05','22','h','석가탄신일'),
	 ('ko','2037','06','06','h','현충일'),
	 ('ko','2037','08','15','h','광복절'),
	 ('ko','2037','09','23','h','추석연휴'),
	 ('ko','2037','09','24','h','추석'),
	 ('ko','2037','09','25','h','추석연휴'),
	 ('ko','2037','10','03','h','개천절'),
	 ('ko','2037','10','09','h','한글날'),
	 ('ko','2037','12','25','h','성탄절');

-- base_code_grp - cmms 시스템 코드
delete from cm_base_code_grp;
INSERT INTO cm_base_code_grp (code_grp_cd,code_grp_nm,code_grp_dsc,system_yn,use_yn,disp_order) VALUES
	 ('AB_GRADE','AB등급','자재의 상태 등급(A급 신춤, B급 수리품)','Y','Y',1),
	 ('ACTION_TYPE','처리유형','처리유형','Y','Y',2),
	 ('ALARM_CAUSE','발생원인','발생원인','Y','Y',3),
	 ('ALARM_DISP_TYPE','측정유형 알람표시방식','측정유형 알람표시방식','Y','Y',4),
	 ('ALARM_STATUS','알람-상태','알람-상태','Y','Y',5),
	 ('ALARM_TYPE','알람유형','알람유형','Y','Y',6),
	 ('AMT_UNIT','수량단위','수량단위','Y','Y',7),
	 ('BBS_ATTR','BBS_ATTR','게시판속성','Y','Y',8),
	 ('BBS_SEARCH_COND','게시물목록조회조건','게시물목록조회조건','Y','Y',9),
	 ('BBS_TYPE','BBS_TYPE','게시판유형','Y','Y',10),
	 ('CHK_ITEM_UNIT','설비점검항목단위','설비점검항목단위','Y','Y',11),
	 ('CHK_STATUS','점검일정상태','점검일정상태','Y','Y',12),
	 ('CODE_TYPE','코드구분','','Y','Y',13),
	 ('COMP_TYPE','업체구분','업체구분','Y','Y',14),
	 ('COST_CENTER','코스트센터','','Y','Y',15),
	 ('CYCLE_TYPE','주기유형','주기유형','Y','Y',16),
	 ('DAILY_REPORT_TYPE','점검일지구분','','Y','Y',17),
	 ('DATE_TYPE','기간 유형','','Y','Y',18),
	 ('DISPOSE_TYPE','불용처리유형','불용처리유형','Y','Y',19),
	 ('EQUIP_CHK_ITEM_TYPE','점검항목결과','','Y','Y',20),
	 ('EQUIP_LIFE_CYCLE_TYPE','설비운영정보','설비운영정보','Y','Y',21),
	 ('EQUIP_STATUS','설비상태','설비상태','Y','Y',22),
	 ('EQUIP_SYSTEM','시스템','','Y','Y',23),
	 ('EQUIPMENT_PROCESS','프로세스','','Y','Y',24),
	 ('FAQ_TYPE','FAQ_TYPE','FAQ구분','Y','Y',25),
	 ('FORM_KINDS','양식종류','양식종류(FK_EQ 설비라벨, FK_MT 자재라벨, FK_MI 자재입고라벨, FK_SL 보관위치라벨)','Y','Y',26),
	 ('HELP_ITEM_CLASS','HELP_ITEM_CLASS','헬프항목구분','Y','Y',27),
	 ('HELP_ITEM_TYPE','HELP_ITEM_TYPE','헬프항목유','Y','Y',28),
	 ('IN_TYPE','입고유형','보전자재 입출고유형(입고)','Y','Y',29),
	 ('INOUT_CLASS','입출고AB급','입출고AB급','Y','Y',30),
	 ('INOUT_DIV','입출고구분','입출고구분','Y','Y',31),
	 ('ISA95CLASS','ISA-95 분류','','Y','Y',32),
	 ('LOC_STATUS','위치상태','위치정보의 상태','Y','Y',33),
	 ('LOGIN_LOG_TYPE','로그인유형','로그인유형','Y','Y',34),
	 ('MAIL_STATUS','메일발송상태','MAIL_INFO의 메일발송상태','Y','Y',35),
	 ('MAINT_TYPE','보전유형','보전유형','Y','Y',36),
	 ('MARKER_TYPE','마커 타입','마커 타입 정보','Y','Y',37),
	 ('MEAS_SENSOR','측정센서','측정센서','Y','Y',38),
	 ('MTRL_CLASS','자재종류','자재종류','Y','Y',39),
	 ('MTRL_STOCK_COND','재고부족자재조건','재고부족자재조건','Y','Y',40),
	 ('NOTI_GRP_TYPE','통지유형','','Y','Y',41),
	 ('NOTI_RESULT_TYPE','알람발송결과유형','알람발송결과유형','Y','Y',42),
	 ('OPERATIONS_LOG','시스템 사용기록','시스템 사용기록','Y','Y',43),
	 ('OUT_TYPE','출고유형','보전자재 입출고유형(출고)','Y','Y',44),
	 ('PERIOD_TYPE','주기유형','일,주,월의 주기유형','Y','Y',45),
	 ('PINV_LOC_STATUS','실사상태','실사상태','Y','Y',46),
	 ('PM_TYPE','예방정비유형','예방정비유형','Y','Y',47),
	 ('PRJ_STATUS','프로젝트 상태','프로젝트 상태코드','Y','Y',48),
	 ('SRC_CONTS','콘텐츠 소스','콘텐츠 소스(TEXT, FILE)','Y','Y',49),
	 ('SRC_SYSTEM','태그-소스시스템','태그-소스시스템','Y','Y',50),
	 ('USE_YN','사용유무','','Y','Y',51),
	 ('USER_TYPE','사용자유형 ','사용자유형 (관리자, 파워유저, 작업자, 더미) ','Y','Y',52),
	 ('WEEK_TYPE','요일유형','요일유','Y','Y',53),
	 ('WO_STATUS','작업상태','작업상태','Y','Y',54),
	 ('WO_STATUS_PM','PM WO 조회상태','PM WO 조회상태','Y','Y',55),
	 ('WO_STATUS_VIEW','WO조회상태','WO조회상태','Y','Y',56),
	 ('WO_TYPE','작업유형','작업유형','Y','Y',57),
	 ('WORK_SRC','작업소싱','작업지시서 작업소싱(사내,외주,사내/외주)','Y','Y',58),
	 ('WOS_TYPE','대상구분','','Y','Y',59),
	 ('WS_TYPE','작업구분','','Y','Y',60),
	('VIEW_TYPE','조회유형','','Y','Y',61)
	;

-- base_code
INSERT INTO cm_base_code (code_pk,code_cd,code_nm,code_dsc,grp_cd,code_nm_en,code_nm_ch,code_nm_jp,disp_order,use_yn,insert_ts,inserter_id,inserter_nm,update_ts,updater_id,updater_nm,attr1,code_grp_cd) VALUES
	 (1,'AB_GRADE_A','A급(신품)','A급(신품)',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AB_GRADE'),
	 (2,'AB_GRADE_B','B급(수리품)','B급(수리품)',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AB_GRADE'),
	 (3,'AT01','교체','교체:신품/예비품으로 교체',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ACTION_TYPE'),
	 (4,'AT02','수리(수정)','수리(수정):기존설비 수리 및 청소',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ACTION_TYPE'),
	 (5,'AT03','교정','교정:기존설비 교정',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ACTION_TYPE'),
	 (6,'AT04','정밀검사','정밀검사:전문가에 의한 정밀 검사 조치',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ACTION_TYPE'),
	 (7,'AT05','MR(설비변경) 조치','MR(설비변경) 조치',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ACTION_TYPE'),
	 (8,'AT06','자체 현장 점검','자체 현장 점검, 설비 또는 운전에 특이사항 없음',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ACTION_TYPE'),
	 (9,'LH','Level Hunting','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_CAUSE'),
	 (10,'OI','개방검사','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_CAUSE'),
	 (11,'ME','계기오류','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','ALARM_CAUSE'),
	 (12,'SD','SD/SU','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_CAUSE'),
	 (13,'MA','정비작업','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_CAUSE'),
	 (14,'ETC','기타','',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_CAUSE'),
	 (15,'WD','주의위험 여부','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_DISP_TYPE'),
	 (16,'LK','누출 여부','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_DISP_TYPE'),
	 (17,'ND','불검출 여부','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_DISP_TYPE'),
	 (18,'A','활성','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_STATUS'),
	 (19,'C','해제','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_STATUS'),
	 (20,'LO','LO','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_TYPE'),
	 (21,'HI','HI','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_TYPE'),
	 (22,'LL','LL','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_TYPE'),
	 (23,'HH','HH','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_TYPE'),
	 (24,'LK','누출','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_TYPE'),
	 (25,'ND','불검출','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ALARM_TYPE'),
	 (26,'BOX','Box','박스 단위',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AMT_UNIT'),
	 (27,'BT','Bottle','병 단위',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AMT_UNIT'),
	 (28,'CV','Case','Case',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AMT_UNIT'),
	 (29,'DR','Drum','Drum',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AMT_UNIT'),
	 (30,'EA','EA','each',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AMT_UNIT'),
	 (31,'Pack','Pack','Pack',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'AMT_UNIT'),
	 (32,'BBS_ATTR_V','유효게시판','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'BBS_ATTR'),
	 (33,'BBS_ATTR_G','갤러리','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'BBS_ATTR'),
	 (34,'BBS_ATTR_U','일반게시판','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'BBS_ATTR'),
	 (35,'BBS_SEARCH_COND_T','제목','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'BBS_SEARCH_COND'),
	 (36,'BBS_SEARCH_COND_U','작성자','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'BBS_SEARCH_COND'),
	 (37,'BBS_TYPE_A','일반게시판','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'BBS_TYPE'),
	 (38,'BBS_TYPE_I','공지게시판','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'BBS_TYPE'),
	 (39,'dB','소음(dB)','',NULL,NULL,NULL,NULL,0,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (40,'kΩ','저항(kΩ)','',NULL,NULL,NULL,NULL,0,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (41,'℉','온도(℉)','',NULL,NULL,NULL,NULL,0,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (42,'no_unit','단위없음','',NULL,NULL,NULL,NULL,0,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (43,'℃ ','온도(℃ )','℃ ',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (44,'kPa','압력(kPa)','압력값(kPa)',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (45,'MPa','압력(MPa)','압력(MPa)',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (46,'%','습도(%)','습도',NULL,NULL,NULL,NULL,8,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (47,'Torr (mmHg)','진공도(mmHg)','진공도 Torr (mmHg)',NULL,NULL,NULL,NULL,9,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (48,'bar','압력(bar)','압력값',NULL,NULL,NULL,NULL,9,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (49,'kV','전압(kV)','전압',NULL,NULL,NULL,NULL,10,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (50,'V','전압(V)','전압',NULL,NULL,NULL,NULL,11,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (51,'MΩ','저항(MΩ)','저항값(MΩ)',NULL,NULL,NULL,NULL,12,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (52,'Ω','저항(Ω)','저항(Ω)',NULL,NULL,NULL,NULL,13,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (53,'A','전류(A)','전류값',NULL,NULL,NULL,NULL,14,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_ITEM_UNIT'),
	 (54,'CHK_STATUS_N','미점검','','NP',NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CHK_STATUS'),
	 (55,'CHK_STATUS_NP','점검예정','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','CHK_STATUS'),
	 (56,'CHK_STATUS_P','점검중','','NP',NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','CHK_STATUS'),
	 (57,'CHK_STATUS_Y','점검완료',NULL,NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','CHK_STATUS'),
	 (58,'PC','현상코드',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','CODE_TYPE'),
	 (59,'CC','원인코드',NULL,NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','CODE_TYPE'),
	 (60,'RC','조치코드',NULL,NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','CODE_TYPE'),
	 (61,'FC','고장부위',NULL,NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','CODE_TYPE'),
	 (62,'CP_S','공급사','공급사',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'COMP_TYPE'),
	 (63,'CP_M','제조사','제조사',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'COMP_TYPE'),
	 (64,'CP_B','공급사/제조사','공급사/제조사',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'COMP_TYPE'),
	 (65,'CP_C','시공사',NULL,NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','COMP_TYPE'),
	 (66,'CP_E','장비사',NULL,NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','COMP_TYPE'),
	 (67,'CP390','390센터',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','COST_CENTER'),
	 (68,'CR50B','50B센터',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','COST_CENTER'),
	 (69,'CC001','첫 센터',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','COST_CENTER'),
	 (70,'CYCLE_TYPE_Y','년','년 마다',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CYCLE_TYPE'),
	 (71,'CYCLE_TYPE_M','월','개월 마다',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CYCLE_TYPE'),
	 (72,'CYCLE_TYPE_W','주','주 마다',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CYCLE_TYPE'),
	 (73,'CYCLE_TYPE_D','일','일 마다',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'CYCLE_TYPE'),
	 (74,'None','없음',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','DAILY_REPORT_TYPE'),
	 (75,'DATE_TYPE_REQ','요청일','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DATE_TYPE'),
	 (76,'DATE_TYPE_PLAN','계획일','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DATE_TYPE'),
	 (77,'DATE_TYPE_WORK','작업일','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DATE_TYPE'),
	 (78,'DATE_TYPE_HOPE','희망일','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DATE_TYPE'),
	 (79,'DP1','매각','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DISPOSE_TYPE'),
	 (80,'DP2','대여','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DISPOSE_TYPE'),
	 (81,'DP3','해체','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DISPOSE_TYPE'),
	 (82,'DP4','폐기','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DISPOSE_TYPE'),
	 (83,'DP5','기증','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DISPOSE_TYPE'),
	 (84,'DP6','기타','',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'DISPOSE_TYPE'),
	 (85,'N','정상',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','EQUIP_CHK_ITEM_TYPE'),
	 (86,'A','이상',NULL,NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','EQUIP_CHK_ITEM_TYPE'),
	 (87,'C','점검불가',NULL,NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','EQUIP_CHK_ITEM_TYPE'),
	 (88,'EQUIP_STARTUP','가동','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'EQUIP_LIFE_CYCLE_TYPE'),
	 (89,'EQUIP_BREAKDOWN','고장발생','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'EQUIP_LIFE_CYCLE_TYPE'),
	 (90,'EQUIP_FINISH_FIX','수리완료','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'EQUIP_LIFE_CYCLE_TYPE'),
	 (91,'ES_OPER','가동중','가동중',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'EQUIP_STATUS'),
	 (92,'ES_BKDN','고장','고장',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'EQUIP_STATUS'),
	 (93,'ES_DISP','불용','불용',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'EQUIP_STATUS'),
	 (94,'ES_IDLE','유휴','유휴상태',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'EQUIP_STATUS'),
	 (95,'ES03','어중간한 시스템',NULL,NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','EQUIP_SYSTEM'),
	 (96,'ES13','기타',NULL,NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','EQUIPMENT_PROCESS'),
	 (97,'FAQ_TYPE_M','자재','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FAQ_TYPE'),
	 (98,'FAQ_TYPE_E','설비','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FAQ_TYPE'),
	 (99,'FAQ_TYPE_I','점검','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FAQ_TYPE'),
	 (100,'FAQ_TYPE_P','PM','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FAQ_TYPE'),
	 (101,'FAQ_TYPE_W','W/O','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FAQ_TYPE'),
	 (102,'FAQ_TYPE_A','관리자','',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FAQ_TYPE'),
	 (103,'FAQ_TYPE_T','기타','',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FAQ_TYPE'),
	 (104,'FK_EQ','설비라벨','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FORM_KINDS'),
	 (105,'FK_MT','자재라벨','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FORM_KINDS'),
	 (106,'FK_MI','자재입고라벨','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FORM_KINDS'),
	 (107,'FK_SL','보관위치라벨','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'FORM_KINDS'),
	 (108,'HELP_ITEM_CLASS_M','자재','Material',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_CLASS'),
	 (109,'HELP_ITEM_CLASS_E','설비','Equipment',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_CLASS'),
	 (110,'HELP_ITEM_CLASS_I','점검','Inspection',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_CLASS'),
	 (111,'HELP_ITEM_CLASS_P','PM','PM',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_CLASS'),
	 (112,'HELP_ITEM_CLASS_W','W/O','W/O',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_CLASS'),
	 (113,'HELP_ITEM_CLASS_A','관리자','Admin',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_CLASS'),
	 (114,'HELP_ITEM_CLASS_CONT','컨트롤','화면내 컨트롤 관련 HELP',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_CLASS'),
	 (115,'HELP_ITEM_TYPE_S','시스템','System',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_TYPE'),
	 (116,'HELP_ITEM_TYPE_P','프로그램','Program',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_TYPE'),
	 (117,'HELP_ITEM_TYPE_F','필드','Field',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_TYPE'),
	 (118,'HELP_ITEM_TYPE_PS','프로그램추가속성','프로그램추가속성',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'HELP_ITEM_TYPE'),
	 (119,'IT_BY','구매','구매(입고유형)',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'IN_TYPE'),
	 (120,'IT_MO','이동','이동(입고유형)',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'IN_TYPE'),
	 (121,'IT_CH','조정','조정(입고유형)',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'IN_TYPE'),
	 (122,'IT_RC','실사','실사(입고유형)',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'IN_TYPE'),
	 (123,'IT_RP','자재수리','자재수리(입고유형)',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'IN_TYPE'),
	 (124,'IT_ET','기타','기타(입고유형)',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'IN_TYPE'),
	 (125,'IT_CO','이월','이월',NULL,NULL,NULL,NULL,10,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'IN_TYPE'),
	 (126,'INOUT_CLASS_A','A급','A급',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'INOUT_CLASS'),
	 (127,'INOUT_CLASS_B','B급','B급',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'INOUT_CLASS'),
	 (128,'INOUT_DIV_IN','입고','입고',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'INOUT_DIV'),
	 (129,'INOUT_DIV_OUT','출고','출고',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'INOUT_DIV'),
	 (130,'area','area','area',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ISA95CLASS'),
	 (131,'line','line','line',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ISA95CLASS'),
	 (132,'unit','unit','unit',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'ISA95CLASS'),
	 (133,'NOTREADY','준비안됨','준비안됨',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOC_STATUS'),
	 (134,'OPERATING','작동중','작동중',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOC_STATUS'),
	 (135,'DISPOSE','폐기','폐기',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOC_STATUS'),
	 (136,'OOS','서비스중지','서비스중지(OOS)',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOC_STATUS'),
	 (137,'IN','로그인','로그인','Y',NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOGIN_LOG_TYPE'),
	 (138,'OU','로그아웃','로그아웃','Y',NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOGIN_LOG_TYPE'),
	 (139,'FA','로그인 실패','토큰재발급요청','N',NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOGIN_LOG_TYPE'),
	 (140,'MU','메뉴클릭','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'LOGIN_LOG_TYPE'),
	 (141,'MAIL_STATUS_Y','발송','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAIL_STATUS'),
	 (142,'MAIL_STATUS_N','미발송','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAIL_STATUS'),
	 (143,'MAIL_STATUS_E','발송실패','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAIL_STATUS'),
	 (144,'MAINT_TYPE_GM','일반작업','','WO',NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAINT_TYPE'),
	 (145,'MAINT_TYPE_BM','사후보전','','WO',NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAINT_TYPE'),
	 (146,'MAINT_TYPE_PM','예방보전','','PM',NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAINT_TYPE'),
	 (147,'MAINT_TYPE_CM','개량보전','','WO',NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAINT_TYPE'),
	 (148,'MAINT_TYPE_IM','점검작업','','WO',NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MAINT_TYPE'),
	 (149,'ZONE','구역','구역마커',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MARKER_TYPE'),
	 (150,'LOCATION','위치','위치마커',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MARKER_TYPE'),
	 (151,'EQUIPMENT','설비','설비마커',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MARKER_TYPE'),
	 (152,'MSPHM','pH meter','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (153,'MSGAS','가스 감지기','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (154,'MSLIQ','누액 감지기','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (155,'MSWLV','수위센서','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (156,'MSPRS','압력센서','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (157,'MSTMP','온도센서','',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (158,'MSWGG','유량센서','',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (159,'MSELC','전류계','',NULL,NULL,NULL,NULL,8,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (160,'MSVOT','전압계','',NULL,NULL,NULL,NULL,9,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (161,'MSVIB','진동계','',NULL,NULL,NULL,NULL,10,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (162,'MSFDT','화염검출기','',NULL,NULL,NULL,NULL,11,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (163,'MSMCR','수은주','',NULL,NULL,NULL,NULL,99,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MEAS_SENSOR'),
	 (164,'MA','공압','공압 실린더, 공압 밸브, 진공패드, 에어 유닛 등',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (165,'MH','유압','유압 실린더, 유압 밸브, 유압 필터, 유압 유닛 등',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (166,'ME','기계요소','베어링, 메탈, 패킹, 부싱, 가이드 등',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (167,'MT','동력 기기 / 전달','각종 감속기, 펌프 및 동력 전달에 필요한 벨트, 체인, 기어, 풀리 등',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (168,'MS','특수제작','기성품이 아닌 맞춤형으로 모델명이 없는 제작품(롤, 로터, 임펠러 등)',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (169,'EM','모터','AC 모터, DC 모터, 서보 모터, 벡터 모터, 토르크 모터, 기어드 모터 등 ',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (170,'EC','모터 제어 / 주변기기','인버터, DC 제어반, 벡터 제어반, 서보 제어반, 토르크 제어반 등',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (171,'ES','센서 부품','일반 엔코더, 레벨, 근접 센서, 포토 센서 등',NULL,NULL,NULL,NULL,8,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (172,'EI','계장 부품','RTD, TIC, 히터, 로드셀, 계량기, 인디게이터, 레벨 등',NULL,NULL,NULL,NULL,9,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (173,'EE','전기 부품','차단기, 릴레이, M/C, EOCR, 퓨즈, S/W, 경광등 등',NULL,NULL,NULL,NULL,10,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (174,'EP','PLC / HMI / 제어 부품','PLC, 터치판넬, 전력조정기, K-TRON, 타이머 등',NULL,NULL,NULL,NULL,11,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (175,'ET','정보 / 통신 / 영상 / 방송 부품','마이크, 앰프, HDMI, 소리통, 인터폰 등',NULL,NULL,NULL,NULL,12,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (176,'UU','배관 기기','각종 밸브, 게이지, 트랩 등',NULL,NULL,NULL,NULL,13,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_CLASS'),
	 (177,'MTRL_STOCK_COND_N','없음','없음',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_STOCK_COND'),
	 (178,'MTRL_STOCK_COND_S','재고량기준','재고량기준',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_STOCK_COND'),
	 (179,'MTRL_STOCK_COND_A','안전재고량기준','안전재고량기준',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'MTRL_STOCK_COND'),
	 (180,'NGT-D01','임시 비밀번호 발급 알림','임시 비밀번호 발급 알림',NULL,NULL,NULL,NULL,0,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (181,'NGT-E01','설비 활성 알람 알림','설비상태 Active Alarm 알림',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (182,'NGT-M01','안전재고 부족 알림','자재 안전재고 부족 알림(출고시)',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (183,'NGT-P01','PM 작업 계획일 알림','PM 작업 계획일 3일 전 알림',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (184,'NGT-P02','PM 작업 미실시 알림','PM 작업 미실시 알림(법정점검 설비)',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (185,'NGT-C02','점검 작업 계획일 알림','점검 작업 계획일 3일 전 알림',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (186,'NGT-C01','점검 작업 미실시 알림','점검 작업 미실시 알림(법정점검 설비)',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (187,'NGT-W01','작업지시 요청반려 알림','작업지시 요청 반려시 요청자에게 알림',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (188,'NGT-W02','작업지시 요청완료 알림','작업지시 WO료처리시 요청자에게 알림',NULL,NULL,NULL,NULL,8,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (189,'NGT-W03','작업지시 업무배정 알림','작업지시 업무배정시 담당자에게 알림',NULL,NULL,NULL,NULL,9,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_GRP_TYPE'),
	 (190,'S','전송성공','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_RESULT_TYPE'),
	 (191,'F','전송실패','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_RESULT_TYPE'),
	 (192,'W','전송대기','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_RESULT_TYPE'),
	 (193,'R','수신거부','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_RESULT_TYPE'),
	 (194,'C','전송취소','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'NOTI_RESULT_TYPE'),
	 (195,'MNU_OPN','화면 메뉴 실행','화면 메뉴 실행 액션',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (196,'NEW_SAV','등록(저장)','등록(저장) 액션',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (197,'EDT_SAV','수정(저장)','수정(저장) 액션',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (198,'DEL_SAV','삭제','데이터 삭제 액션',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (199,'FIL_UPL','파일 업로드','파일 업로드 액션',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (200,'FIL_DWN','파일 다운로드','파일 다운로드 액션',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (201,'FIL_DEL','파일 삭제','파일 삭제 액션',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (202,'EXL_DWN','엑셀 다운로드','엑셀 다운로드 액션',NULL,NULL,NULL,NULL,8,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (203,'DAT_SRC','데이터 조회','데이터 조회 액션',NULL,NULL,NULL,NULL,9,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (204,'DTL_POP','상세보기 실행','상세보기 실행 액션',NULL,NULL,NULL,NULL,10,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (205,'EDT_POP','수정팝업 실행','수정팝업 실행 액션',NULL,NULL,NULL,NULL,11,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (206,'URL_LNK','링크이동','링크이동 액션',NULL,NULL,NULL,NULL,12,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OPERATIONS_LOG'),
	 (207,'OT_WO','작업지시','작업지시(출고유형)',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OUT_TYPE'),
	 (208,'OT_MO','이동','이동(출고유형)',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OUT_TYPE'),
	 (209,'OT_CH','조정','조정(출고유형)',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OUT_TYPE'),
	 (210,'OT_RC','실사','실사(출고유형)',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OUT_TYPE'),
	 (211,'OT_RP','자재수리','자재수리(출고유형)',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OUT_TYPE'),
	 (212,'OT_ET','기타','기타(출고유형)',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'OUT_TYPE'),
	 (213,'D','일','일(Day)',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PERIOD_TYPE'),
	 (214,'W','주','주(Week)',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PERIOD_TYPE'),
	 (215,'M','월','월(Month)',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PERIOD_TYPE'),
	 (216,'PINV_PLAN','실사계획','실사계획',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PINV_LOC_STATUS'),
	 (217,'PINV_EXEC','실사실행','실사실행',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PINV_LOC_STATUS'),
	 (218,'PINV_FIN','실사완료','실사완료',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PINV_LOC_STATUS'),
	 (219,'PM_TYPE_TBM','TBM','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PM_TYPE'),
	 (220,'PM_TYPE_CBM','CBM','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PM_TYPE'),
	 (221,'PM_TYPE_UBM','UBM','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PM_TYPE'),
	 (222,'PREP','준비중','프로젝트 상태 코드',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PRJ_STATUS'),
	 (223,'INPR','진행중','프로젝트 상태 코드',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PRJ_STATUS'),
	 (224,'FINS','완료','프로젝트 상태 코드',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PRJ_STATUS'),
	 (225,'DISP','폐기','프로젝트 상태 코드',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'PRJ_STATUS'),
	 (226,'TEXT','텍스트','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'SRC_CONTS'),
	 (227,'FILE','파일','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'SRC_CONTS'),
	 (228,'SPLC','PLC','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'SRC_SYSTEM'),
	 (229,'SSCD','SCADA','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'SRC_SYSTEM'),
	 (230,'SWCR','진동시스템','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'SRC_SYSTEM'),
	 (231,'SETC','기타','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'SRC_SYSTEM'),
	 (232,'Y','사용',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','USE_YN'),
	 (233,'N','미사용',NULL,NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','USE_YN'),
	 (234,'UA','마스터 ','시스템관리자 ',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'USER_TYPE'),
	 (235,'UP','엔지니어 ','결재권한담당자 ',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'USER_TYPE'),
	 (236,'UC','오퍼레이터 ','일반사용자 ',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'USER_TYPE'),
	 (237,'UD','WO작업자 ','아이디,암호가 없는 사용자로 WO에서 작업자로 추가가능 ',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'USER_TYPE'),
	 (238,'MON','Mon.','월요일',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WEEK_TYPE'),
	 (239,'TUE','Tue.','화요일',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WEEK_TYPE'),
	 (240,'WED','Wed.','수요일',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WEEK_TYPE'),
	 (241,'THU','Thu.','목요일',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WEEK_TYPE'),
	 (242,'FRI','Fri.','금요일',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WEEK_TYPE'),
	 (243,'SAT','Sat.','토요일',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WEEK_TYPE'),
	 (244,'SUN','Sun.','일요일',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WEEK_TYPE'),
	 (245,'WOS_RW','요청작성중','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (246,'WOS_RB','요청반려','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (247,'WOS_RQ','요청완료','',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (248,'WOS_RJ','요청승인반려','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (249,'WOS_OC','요청승인','',NULL,NULL,NULL,NULL,7,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (250,'WOS_AP','작업승인','',NULL,NULL,NULL,NULL,8,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (251,'WOS_CM','작업완료','',NULL,NULL,NULL,NULL,9,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (252,'WOS_CL','WO완료','',NULL,NULL,NULL,NULL,10,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (253,'WOS_DL','취소','',NULL,NULL,NULL,NULL,11,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS'),
	 (254,'WOS_CM0,WOS_AP0','작업할(중)','작업할(중)',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS_PM'),
	 (255,'WOS_CL0','완료','완료',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS_PM'),
	 (256,'OW,OJ','작성중(반려)','',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS_VIEW'),
	 (257,'AP,','작업할 대상','',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS_VIEW'),
	 (258,'CM,','완료할 대상','',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS_VIEW'),
	 (259,'CL,','완료','',NULL,NULL,NULL,NULL,5,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS_VIEW'),
	 (260,'DL,','취소된 W/O','',NULL,NULL,NULL,NULL,6,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_STATUS_VIEW'),
	 (261,'WO','작업요청 WO','계획되지 않은(Unplanned) Work Order',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_TYPE'),
	 (262,'PM','예방정비 WO','계획된(Planned) Work Order',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_TYPE'),
	 (263,'DPR','작업일보 WO','일정없이 작업(Unscheduled) 한 Work Order',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_TYPE'),
	 (264,'INSP','점검이상 WO','점검중 이상 확인되어 작업한 Work Order',NULL,NULL,NULL,NULL,4,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WO_TYPE'),
	 (265,'WS01','사내수리','자체 수리',NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WORK_SRC'),
	 (266,'WS02','외주수리','외주 수리',NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WORK_SRC'),
	 (267,'WS03','사내/외주수리','사내+외주 수리',NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,NULL,'WORK_SRC'),
	 (268,'WOS_OC','승인할 대상',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','WOS_TYPE'),
	 (269,'WOS_AP','반려할 대상',NULL,NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','WOS_TYPE'),
	 (270,'WS01','자체수리',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','WS_TYPE'),
	 (271,'WS02','외주수리',NULL,NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','WS_TYPE'),
	 (272,'WS03','사내/외주수리',NULL,NULL,NULL,NULL,NULL,3,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','WS_TYPE'),
	 (273,'xxx','예상일정전체',NULL,NULL,NULL,NULL,NULL,1,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','VIEW_TYPE'),
	 (274,'s','주기시작일만',NULL,NULL,NULL,NULL,NULL,2,'Y','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL,'','VIEW_TYPE');


SELECT setval('cm_base_code_code_pk_seq', (SELECT MAX(code_pk) FROM cm_base_code), true);
INSERT INTO cm_sites (site_id,site_desc,site_manager,status,ccu_count,map_draw_file_cd,insert_ts,inserter_id,update_ts,updater_id) VALUES
	 ('1','위존(강남)','system','A',5,NULL,'2025-01-14 14:57:09.942864+09',1,NULL,1);

--설비 카테고리
INSERT INTO cm_equip_category (equip_category_id,equip_category_desc,remark,use_yn,insert_ts,inserter_id,update_ts,updater_id) VALUES
	 ('A','Architecture','건축','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('X','Auxiliaries','보조장치','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('B','Bes','베스','Y','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('C','Civil','토목','Y','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('D','Duct','덕트','Y','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('E','Electrical','전기 설비','Y','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('F','Fire Fighting','소방 설비','Y','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('HE','Heavy Equipment','중장비','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('H','HVAC','공조 설비','Y','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('I','Instrument','제어 설비','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('L','Laboratory Equipment','실험실 설비','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('M','Machinery','기계 설비','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('O','Office Equipment','사무용 장비(PC와 악세서리)','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('P','Piping','배관','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('R','Rotating','회전 설비','Y','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('SF','Safety Equipment','안전 설비','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('S','Stationary','장치 설비','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('TE','Temporary Equipment','보조장치','N','2025-06-01 00:00:01+09',1,NULL,NULL),
	 ('U','Utilities','유틸리티','N','2025-06-01 00:00:01+09',1,NULL,NULL);

INSERT INTO cm_import_rank (import_rank_pk,import_rank_cd,import_rank_desc,use_yn,del_yn,insert_ts,inserter_id,inserter_nm,update_ts,updater_id,updater_nm) VALUES
	 (4,'S','S 급','N','N','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL),
	 (1,'A','A 급','Y','N','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL),
	 (2,'B','B 급','Y','N','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL),
	 (3,'C','C 급','Y','N','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL),
	 (5,'D','D 급','Y','N','2025-06-01 00:00:01+09',1,'위존',NULL,NULL,NULL);

INSERT INTO chk_item_template (template_id,chk_item,unit,group_code,hash_tag,site_id,insert_ts,inserter_id) VALUES
	 (1,'TELSTAR 송신기의 상태/작동을 확인하십시오. 필요한 경우 리본이나 용지를 교체하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (2,'과부하 설정을 육안으로 검사합니다.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (3,'구성 요소 장착의 보안을 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (4,'녹, 손상 등의 징후가 있는지 제어판의 상태를 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (5,'도징 펌프의 작동을 점검하십시오.','단위없음',NULL,'#pump','1','2025-06-01 00:00:01','1'),
	 (6,'드라이브 V-벨트의 상태를 확인하십시오. 필요한 경우 교체하십시오.','단위없음',NULL,'#velt','1','2025-06-01 00:00:01','1'),
	 (7,'모든 경고등 및 주행등의 작동을 점검하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (8,'모든 모터에서 위상 균형 점검을 수행하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (9,'모든 배선의 보안을 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (10,'모든 열전쌍, 변환기 케이블의 보안을 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (11,'모든 열전쌍이 올바르게 읽고 있는지 확인하십시오. 모든 결함을 수리하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (12,'모든 접촉기, 릴레이, 타이머 등을 육안으로 검사합니다.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (13,'모든 플랜트 히터의 작동을 확인하고 앰프 판독값을 기록합니다.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (14,'시작할 때와 작동할 때 콘덴서를 확인하십시오.','단위없음',NULL,'#condenser','1','2025-06-01 00:00:01','1'),
	 (15,'올바른 설정을 위해 타이머/시계를 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (16,'올바른 작동을 위해 볼 밸브를 확인하고 암에 윤활유를 바르고 올바른 수위로 설정하십시오.','단위없음',NULL,'#lubricate','1','2025-06-01 00:00:01','1'),
	 (17,'유연제 염수통 수위를 확인하십시오. 필요에 따라 소금을 채우고 재고 수준을 보고합니다.','단위없음',NULL,'#softender','1','2025-06-01 00:00:01','1'),
	 (18,'응축기 구동 진동 스위치의 올바른 작동을 확인하십시오.','단위없음',NULL,'#condenser','1','2025-06-01 00:00:01','1'),
	 (19,'응축기 팬 온수기와 온도 조절 장치의 작동을 확인하십시오.','단위없음',NULL,'#heater','1','2025-06-01 00:00:01','1'),
	 (20,'저수위 플로트의 작동을 확인하십시오.','단위없음',NULL,'#water','1','2025-06-01 00:00:01','1'),
	 (21,'절연 및 저항 점검을 수행하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (22,'제상 제어 순서를 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (23,'제어 순서를 확인하십시오. 문제 보고(예: PLC 또는 TELSTAR 등)','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (24,'진동 모니터링 점검을 받으십시오.','단위없음',NULL,'#vibration','1','2025-06-01 00:00:01','1'),
	 (25,'청소 및 염소 처리가 수행되고 있는지 확인하십시오.','단위없음',NULL,'#clean,#chlorination','1','2025-06-01 00:00:01','1'),
	 (26,'케이블이 손상되었거나 과열되었는지 육안으로 검사합니다.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (27,'콘덴서의 내부 상태를 확인하십시오. 녹, 먼지 등','단위없음',NULL,'#condenser,#condition','1','2025-06-01 00:00:01','1'),
	 (28,'콘덴서의 외부 상태를 확인하십시오. 녹, 먼지 등','단위없음',NULL,'#condenser,#condition','1','2025-06-01 00:00:01','1'),
	 (29,'팬 댐퍼의 작동을 확인하십시오.','단위없음',NULL,'#damper','1','2025-06-01 00:00:01','1'),
	 (30,'팬 모터의 작동을 확인하십시오. 그리스 조정 나사.','단위없음',NULL,'#motor, #screw','1','2025-06-01 00:00:01','1'),
	 (31,'팬 샤프트 베어링과 잠금 칼라를 점검하고 윤활하십시오.','단위없음',NULL,'#lubricate','1','2025-06-01 00:00:01','1'),
	 (32,'퓨즈 캐리어의 상태를 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1'),
	 (33,'필요한 경우 콘덴서 드라이브를 점검/조정하십시오.','단위없음',NULL,'#condenser','1','2025-06-01 00:00:01','1'),
	 (34,'화학물질 통의 레벨을 확인하십시오. 필요에 따라 충전하십시오.','단위없음',NULL,'#level','1','2025-06-01 00:00:01','1'),
	 (35,'히터 매트가 작동하는지 확인하십시오.','단위없음',NULL,'#control,#panel','1','2025-06-01 00:00:01','1');

INSERT INTO cm_reliab_codes (id,reliab_cd,reliab_nm,"types",remark,factory_pk,use_yn,insert_ts,inserter_id,update_ts,updater_id) VALUES
	 (2,'001','현상코드명01','PC',NULL,1,'Y','2025-05-27 17:29:04.415041+09',1,'2025-05-27 17:29:04.415041+09',1),
	 (3,'002','현상코드명02','PC',NULL,1,'Y','2025-05-27 17:30:27.492448+09',1,'2025-05-27 17:30:27.492448+09',1),
	 (4,'003','현상코드명03','PC',NULL,1,'Y','2025-05-28 11:06:57.056098+09',1,'2025-05-28 11:06:57.056098+09',1),
	 (5,'004','현상코드명04','PC',NULL,1,'Y','2025-05-28 11:28:43.064278+09',1,'2025-05-28 11:28:43.064278+09',1),
	 (6,'005','현상코드명05','PC',NULL,1,'Y','2025-05-28 11:31:15.104638+09',1,'2025-05-28 11:31:15.104638+09',1),
	 (7,'006','현상코드명06','PC',NULL,1,'Y','2025-05-28 11:32:02.262636+09',1,'2025-05-28 11:32:02.262636+09',1),
	 (8,'007','현상코드명07','PC',NULL,1,'Y','2025-05-28 11:36:46.760683+09',1,'2025-05-28 11:36:46.760683+09',1),
	 (9,'008','현상코드명08','PC',NULL,1,'Y','2025-05-28 11:40:38.39146+09',1,'2025-05-28 11:40:38.39146+09',1),
	 (10,'009','현상코드명09','PC',NULL,1,'Y','2025-05-28 13:18:27.954465+09',1,'2025-05-28 13:18:27.954465+09',1),
	 (12,'01','01','PC',NULL,1,'Y','2025-07-14 14:22:08.309563+09',1,'2025-07-14 14:22:08.309563+09',1),
	 (14,'cc01','원인01','CC',NULL,1,'Y','2025-07-21 15:55:09.032858+09',1,'2025-07-21 15:55:09.032858+09',1),
	 (15,'cc02','원인02','CC',NULL,1,'Y','2025-07-21 15:59:57.324402+09',1,'2025-07-21 15:59:57.324402+09',1),
	 (16,'RC01','조치01','RC',NULL,1,'Y','2025-07-21 16:21:25.10599+09',1,'2025-07-21 16:21:25.10599+09',1),
	 (17,'RC02','조치02','RC',NULL,1,'Y','2025-07-21 16:23:12.330729+09',1,'2025-07-21 16:23:12.330729+09',1),
	 (18,'FC001','유압 Unit','FC','유압 Unit',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (19,'FC002','Line(배관류)','FC','Line(배관류)',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (20,'FC003','윤활장치','FC','윤활장치',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (21,'FC004','축봉장치(Seal, Packing)','FC','축봉장치(Seal, Packing)',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (22,'FC005','Impeller & Rotor','FC','Impeller & Rotor',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (23,'FC006','Shaft / Sleeve','FC','Shaft / Sleeve',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (24,'FC007','Gear','FC','Gear',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (25,'FC008','Pulley / Spocket','FC','Pulley / Spocket',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (26,'FC009','Belt / Chain','FC','Belt / Chain',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (27,'FC010','Bearing','FC','Bearing',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (28,'FC011','Diaphragm','FC','Diaphragm',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (29,'FC012','Bolt / Nut / Key / Ring','FC','Bolt / Nut / Key / Ring',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (30,'FC013','Piston / Plunger','FC','Piston / Plunger',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (31,'FC014','Casing / Body / Shell / Housing','FC','Casing / Body / Shell / Housing',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (32,'FC015','Spring / Brake','FC','Spring / Brake',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (33,'FC016','Coupling','FC','Coupling',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (34,'FC017','Motor','FC','Motor',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (35,'FC018','기초(Foundation)','FC','기초(Foundation)',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (36,'FC019','Screw(Element)','FC','Screw(Element)',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (37,'FC020','Roll','FC','Roll',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (38,'FC021','Roller / Wheel','FC','Roller / Wheel',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (39,'FC022','Frame','FC','Frame',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (40,'FC023','Cutter','FC','Cutter',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (41,'FC024','Tube','FC','Tube',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (42,'FC025','Tray / 충진물','FC','Tray / 충진물',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (43,'FC026','Nozzle / Manhole','FC','Nozzle / Manhole',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (44,'FC027','Gasket','FC','Gasket',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (45,'FC028','Valve','FC','Valve',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (46,'FC029','Hopper / Tank','FC','Hopper / Tank',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (47,'FC030','Guide','FC','Guide',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (48,'FC031','Filter','FC','Filter',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (49,'FC032','Sight Glass','FC','Sight Glass',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (50,'FC033','Robot','FC','Robot',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (51,'FC034','LM Guide / Rail','FC','LM Guide / Rail',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (52,'FC035','Cam','FC','Cam',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (53,'FC036','Jig','FC','Jig',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (54,'FC037','Chuck','FC','Chuck',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (55,'FC038','Cylinder','FC','Cylinder',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (56,'FC039','Index','FC','Index',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (57,'FC040','EPC','FC','EPC',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (58,'FC041','Printer','FC','Printer',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (59,'FC042','Switch','FC','Switch',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (60,'FC043','Contactor','FC','Contactor',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (61,'FC044','MCCB(차단기)','FC','MCCB(차단기)',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (62,'FC045','과전류계전기','FC','과전류계전기',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL),
	 (63,'FC046','Relay','FC','Relay',1,'Y','2025-01-14 14:57:34.571948+09',1,NULL,NULL);
