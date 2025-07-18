-- 아래부터 postgresql임 copilot 정신차리길



---- TRUNCATE TABLE 명령으로 모든 테이블 삭제
DO $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'plant_i'
    LOOP
        EXECUTE format('TRUNCATE TABLE %I RESTART IDENTITY CASCADE', table_name);
    END LOOP;
END $$;


-- 기초 데이터 insert 구문
-- user_group
SELECT setval('user_group_id_seq', (SELECT MAX(id) FROM user_group), true);
insert into user_group(id, "Code", "Name", "Disabled", "_created")
values
(1, 'dev', 'Developer', false, now() ),
(2, 'admin', 'Admin', false, now() );
(3, 'user', 'User', false, now() );

alter SEQUENCE user_group_id_seq restart WITH 3;

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
(3,'관리자', 2, 'ko-KR', 'N','Y',now(), now() )
;

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

/*
-- equip_category
INSERT INTO equip_category (equip_category_id,equip_category_desc,remark,use_yn,"_status","_created","_modified","_creater_id","_modifier_id") VALUES
	 ('D','Duct','덕트','N',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('HE','Heavy Equipment','중장비','N',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('TE','Temporary Equipment','보조장치','N',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('ZZ','ZZ1023','20241023-002','N',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('C','Civil','토목','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('P','Piping','배관','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('F','Fire Fighting','소방 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('S','Stationary','장치 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('SF','Safety Equipment','안전 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('L','Laboratory Equipment','실험실 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('O','Office Equipment','사무용 장비(PC와 악세서리)','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('A','Architecture','건축','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('E','Electrical','전기 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('H','HVAC','공조 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('I','Instrument','제어 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('M','Machinery','기계 설비','Y',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('R','Rotating','회전 설비','N',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('U','Utilities','유틸리티','N',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL),
	 ('X','Auxiliaries','보조장치','N',NULL,'2025-01-07 11:39:04.617+09',NULL,1,NULL);



*/
--das_server
alter SEQUENCE das_server_id_seq restart WITH 1;
insert into das_server (id, "Code", "Name", "IPAddress","Type","_status", "_created") values (1,'DAS_HPC1', 'DAS HPC#1전용', '10.226.234.30', 'WIN', 'a', now());
insert into das_server (id, "Code", "Name", "IPAddress","Type","_status", "_created") values(2, 'DAS_SMT4', 'DAS SMT#4전용', '10.226.234.31', 'WIN', 'a', now());



/* 메뉴관련 */
truncate table menu_folder cascade;

--메뉴폴더
--alter SEQUENCE menu_folder_id_seq restart WITH 24;
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
	 (30,'SMT라인','inventory',623,NULL,'2025-07-08 18:28:18.553805+09','2025-07-08 18:34:27.225106+09',NULL,NULL,25);

--메뉴
truncate table menu_item cascade;
INSERT INTO menu_item ("MenuCode","MenuName","IconCSS","Url","Popup",_order,_status,_created,_modified,_creater_id,_modifier_id,"MenuFolder_id") VALUES
	 ('wm_equip_group','설비그룹',NULL,'/gui/wm_equip_group','N',10,NULL,'2024-11-22 17:09:20.838481+09','2024-11-22 17:09:24.957445+09',1,1,4),
	 ('wm_equipment','설비',NULL,'/gui/wm_equipment','N',20,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_tag_group','태그그룹',NULL,'/gui/wm_tag_group','N',50,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_tag_master','태그관리',NULL,'/gui/wm_tag_master','N',60,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_das_config','데이터수집설정',NULL,'/gui/wm_das_config','N',70,NULL,'2024-11-22 17:09:17.963281+09','2024-11-22 17:09:24.967392+09',1,1,4),
	 ('wm_cm_equipment','설비마스터',NULL,'/gui/wm_cm_equipment','N',10,NULL,'2025-03-31 14:50:24.768489+09','2025-03-31 15:10:05.791491+09',1,1,21),
	 ('wm_cm_equip_disposed','불용설비',NULL,'/gui/wm_cm_equip_disposed','N',20,NULL,'2025-03-31 14:50:43.602806+09','2025-03-31 15:10:05.798405+09',1,1,21),
	 ('wm_cm_equip_workhist','설비별작업이력',NULL,'/gui/wm_cm_equip_workhist','N',30,NULL,'2025-03-31 14:51:10.006381+09','2025-03-31 15:10:05.807803+09',1,1,21),
	 ('wm_tag_data_current','태그데이터현황',NULL,'/gui/wm_tag_data_current','N',10,NULL,'2024-11-22 17:09:34.259863+09','2024-11-22 17:10:17.285547+09',1,1,9),
	 ('wm_tag_data_list','태그데이터조회',NULL,'/gui/wm_tag_data_list','N',20,NULL,'2024-11-22 17:09:39.061398+09','2024-11-22 17:10:17.296076+09',1,1,9),
	 ('wm_tag_summary','데이터통계',NULL,'/gui/wm_tag_summary','N',30,NULL,'2024-11-22 17:10:03.213384+09','2024-11-22 17:10:17.304884+09',1,1,9),
	 ('wm_tag_trend','데이터트렌드',NULL,'/gui/wm_tag_trend','N',40,NULL,'2024-11-22 17:10:05.946882+09','2024-11-22 17:10:17.312142+09',1,1,9),
	 ('wm_tag_boxplot','상자수염그림',NULL,'/gui/wm_tag_boxplot','N',50,NULL,'2024-11-22 17:09:41.707796+09','2024-11-22 17:10:17.320561+09',1,1,9),
	 ('wm_tag_histogram','히스토그램',NULL,'/gui/wm_tag_histogram','N',60,NULL,'2024-11-22 17:09:50.213623+09','2024-11-22 17:10:17.328512+09',1,1,9),
	 ('wm_tag_scatter','산점도',NULL,'/gui/wm_tag_scatter','N',70,NULL,'2024-11-22 17:09:59.972834+09','2024-11-22 17:10:17.336552+09',1,1,9),
	 ('wm_regression_a','산점도-회귀분석',NULL,'/gui/wm_regression_a','N',80,NULL,'2024-11-22 17:10:08.706509+09','2024-11-22 17:10:17.344432+09',1,1,9),
	 ('wm_calendar','캘린더',NULL,'/gui/wm_calendar','N',10,NULL,'2024-11-22 17:03:46.144348+09','2024-11-22 17:03:55.082601+09',1,1,10),
	 ('wm_board','공지사항',NULL,'/gui/wm_board','N',20,NULL,'2024-11-22 17:03:52.168896+09','2024-11-22 17:03:55.093085+09',1,1,10),
	 ('wm_user','사용자',NULL,'/gui/wm_user','N',10,NULL,'2024-11-22 17:02:59.75001+09','2024-12-23 12:19:53.226806+09',1,3,12),
	 ('wm_user_group','사용자그룹',NULL,'/gui/wm_user_group','N',20,NULL,'2024-11-22 17:03:05.113621+09','2024-12-23 12:19:53.241914+09',1,3,12),
	 ('wm_user_group_menu','메뉴권한',NULL,'/gui/wm_user_group_menu','N',30,NULL,'2024-11-22 17:03:10.558772+09','2024-12-23 12:19:53.268487+09',1,3,12),
	 ('wm_depart','부서',NULL,'/gui/wm_depart','N',40,NULL,'2024-12-23 12:19:46.352763+09','2024-12-23 12:19:53.275487+09',3,3,12),
	 ('wm_storyboard_config','스토리보드설정',NULL,'/gui/wm_storyboard_config','N',50,NULL,'2024-11-22 17:03:17.811259+09','2024-12-23 12:19:53.285883+09',1,3,12),
	 ('wm_login_log','로그인로그',NULL,'/gui/wm_login_log','N',60,NULL,'2024-11-22 17:03:22.529364+09','2024-12-23 12:19:53.295048+09',1,3,12),
	 ('wm_menu_log','메뉴로그',NULL,'/gui/wm_menu_log','N',70,NULL,'2024-11-22 17:03:28.79165+09','2024-12-23 12:19:53.302695+09',1,3,12),
	 ('wm_system_log','시스템로그',NULL,'/gui/wm_system_log','N',80,NULL,'2024-11-22 17:03:34.6587+09','2024-12-23 12:19:53.310692+09',1,3,12),
	 ('wm_post_work_management','사후작업 관리',NULL,'/gui/wm_post_work_management','N',50,NULL,'2025-01-08 16:30:34.525007+09','2025-07-08 16:29:50.715054+09',1,3,5),
	 ('wm_pm_work','PM 마스터별 WO',NULL,'/gui/wm_wo_by_pm_master','N',30,NULL,'2025-01-08 16:33:20.666031+09','2025-05-19 16:43:54.675113+09',1,1,7),
	 ('wm_pm_master','PM 마스터',NULL,'/gui/wm_pm_master','N',10,NULL,'2025-01-08 16:33:20.65558+09','2025-05-19 16:43:54.66637+09',1,1,7),
	 ('wm_pm_schedule','PM 작업일정',NULL,'/gui/wm_pm_schedule','N',20,NULL,'2025-01-08 16:33:20.66069+09','2025-05-19 16:43:54.670578+09',1,1,7),
	 ('wm_facility_monthly_status','설비별 월간 고장현황',NULL,'/gui/wm_facility_monthly_status','N',10,NULL,'2025-01-09 13:17:55.713606+09','2025-06-23 10:54:24.115305+09',1,1,15),
	 ('wm_work_order_approval','작업지시 승인',NULL,'/gui/wm_work_order_approval','N',30,NULL,'2025-01-08 16:30:34.520756+09','2025-07-08 16:29:50.706477+09',1,3,5),
	 ('wm_factory','공장',NULL,'/gui/wm_factory','N',10,NULL,'2024-11-22 17:07:52.512412+09','2025-05-22 15:47:23.004442+09',1,1,3),
	 ('wm_work_order_management','작업결과 관리',NULL,'/gui/wm_work_order_management','N',40,NULL,'2025-01-08 16:30:34.511169+09','2025-07-08 16:29:50.711477+09',1,3,5),
	 ('wm_check_master','점검 마스터',NULL,'/gui/wm_check_master','N',10,NULL,'2025-01-08 16:36:44.489528+09','2025-07-16 15:21:40.985029+09',1,3,8),
	 ('wm_my_work_request','작업요청',NULL,'/gui/wm_my_work_request','N',10,NULL,'2025-01-08 16:30:34.500902+09','2025-07-08 16:29:50.695417+09',1,3,5),
	 ('wm_line','라인',NULL,'/gui/wm_line','N',20,NULL,'2024-11-22 17:04:35.779583+09','2025-05-22 15:47:23.011093+09',1,1,3),
	 ('wm_process','공정',NULL,'/gui/wm_process','N',30,NULL,'2024-11-22 17:04:38.218271+09','2025-05-22 15:47:23.01771+09',1,1,3),
	 ('wm_material','품목(자재)',NULL,'/gui/wm_material','N',40,NULL,'2024-11-22 17:04:41.46544+09','2025-05-22 15:47:23.024288+09',1,1,3),
	 ('wm_bom','BOM',NULL,'/gui/wm_bom','N',50,NULL,'2024-11-22 17:04:44.062137+09','2025-05-22 15:47:23.028741+09',1,1,3),
	 ('wm_defect','부적합정보',NULL,'/gui/wm_defect','N',60,NULL,'2024-11-22 17:04:53.787407+09','2025-05-22 15:47:23.034245+09',1,1,3),
	 ('wm_shift','조교대정보',NULL,'/gui/wm_shift','N',70,NULL,'2024-11-22 17:04:56.656039+09','2025-05-22 15:47:23.040191+09',1,1,3),
	 ('wm_line_inactive','라인비가동정보',NULL,'/gui/wm_line_inactive','N',80,NULL,'2024-11-22 17:05:00.230849+09','2025-05-22 15:47:23.046192+09',1,1,3),
	 ('wm_model_change','기종변경정보',NULL,'/gui/wm_model_change','N',90,NULL,'2024-11-22 17:05:06.581048+09','2025-05-22 15:47:23.051191+09',1,1,3),
	 ('wm_supplier','공급업체',NULL,'/gui/wm_supplier','N',20,NULL,'2025-01-03 11:05:01.287936+09','2025-05-22 16:38:38.190636+09',3,1,11),
	 ('wm_check_schedule','점검 작업일정',NULL,'/gui/wm_check_schedule','N',20,NULL,'2025-01-08 16:36:44.5343+09','2025-07-16 15:21:40.999601+09',1,3,8),
	 ('wm_create_inspection_schedule_manual','점검 일정생성(수동)',NULL,'/gui/wm_create_inspection_schedule_manual','N',50,NULL,'2025-01-08 16:36:44.766997+09','2025-07-16 15:21:41.019425+09',1,3,8),
	 ('wm_dashboard','대시보드',NULL,'/gui/wm_dashboard','N',10,NULL,'2024-11-25 15:00:40.379979+09','2025-06-27 16:53:43.666822+09',3,3,1),
	 ('wm_storyboard','스토리보드',NULL,'/gui/wm_storyboard','N',20,NULL,'2024-11-25 15:00:43.246192+09','2025-06-27 16:53:43.693985+09',3,3,1),
	 ('wm_aas','AAS관리',NULL,'/gui/wm_dashboard','N',10,NULL,'2024-11-25 15:00:40.379979+09','2025-07-08 13:50:30.561156+09',3,3,2),
	 ('wm_asset','자산관리',NULL,'/gui/wm_dashboard','N',20,NULL,'2024-11-25 15:00:40.379979+09','2025-07-08 13:50:30.577057+09',3,3,2),
	 ('wm_aasx','AASX관리',NULL,'/gui/wm_dashboard','N',30,NULL,'2024-11-25 15:00:40.379979+09','2025-07-08 13:50:30.577057+09',3,3,2),
	 ('wm_work_request_approval','작업요청 승인',NULL,'/gui/wm_work_request_approval','N',20,NULL,'2025-01-08 16:30:34.516291+09','2025-07-08 16:29:50.702577+09',1,3,5),
	 ('wm_pm_status_by_category','카테고리별 PM현황',NULL,'/gui/wm_pm_status_by_category','N',1301,NULL,'2025-01-09 14:12:44.288526+09',NULL,1,NULL,17),
	 ('wm_pm_wo_completion_rate','부서별 PM WO 완료율',NULL,'/gui/wm_pm_wo_completion_rate','N',1302,NULL,'2025-01-09 14:12:44.297038+09',NULL,1,NULL,17),
	 ('wm_facility_inspection_master','설비종류별 점검마스터',NULL,'/gui/wm_facility_inspection_master','N',1401,NULL,'2025-01-09 14:12:44.301445+09',NULL,1,NULL,18),
	 ('wm_inspection_issues','점검결과 이상 설비목록',NULL,'/gui/wm_inspection_issues','N',1402,NULL,'2025-01-09 14:12:44.30806+09',NULL,1,NULL,18),
	 ('wm_inspection_stats','점검 수행 통계',NULL,'/gui/wm_inspection_stats','N',1403,NULL,'2025-01-09 14:12:44.31242+09',NULL,1,NULL,18),
	 ('wm_ai_model','모델 관리',NULL,'/gui/wm_ai_model','N',10,NULL,'2025-01-21 15:02:29.146251+09','2025-01-21 16:54:21.318884+09',3,3,19),
	 ('wm_ai_tag_group','AI시스템 운영관리',NULL,'/gui/wm_ai_tag_group','N',10,NULL,'2025-01-21 15:02:29.146251+09','2025-01-21 16:54:21.318884+09',3,3,19),
	 ('wm_ai_tag','AI시스템 참조데이터 관리',NULL,'/gui/wm_ai_tag','N',20,NULL,'2025-01-21 15:02:33.592389+09','2025-01-21 16:54:21.327939+09',3,3,19),
	 ('wm_ai_tagdata_list','AI시스템 IF 확인',NULL,'/gui/wm_ai_tagdata_list','N',30,NULL,'2025-01-21 15:02:38.986308+09','2025-01-21 16:54:21.334786+09',3,3,19),
	 ('wm_predictive_conservation','예지보전 알람',NULL,'/gui/wm_predictive_conservation','N',40,NULL,'2025-01-21 15:02:45.262656+09','2025-01-21 16:54:21.342407+09',3,3,19),
	 ('wm_learning_data_info','학습데이터 정보',NULL,'/gui/wm_learning_data_info','N',50,NULL,'2025-01-21 16:54:07.515311+09','2025-01-21 16:54:21.349119+09',3,3,19),
	 ('wm_learning_data_from_tag','학습데이터 정보(태그)',NULL,'/gui/wm_learning_data_from_tag','N',60,NULL,'2025-01-21 15:02:57.467844+09','2025-01-21 16:54:21.356793+09',3,3,19),
	 ('wm_sample_test','샘플화면(test)',NULL,'/gui/wm_sample_test','N',10,NULL,'2025-04-02 14:01:08.53+09','2025-04-02 14:02:25.48+09',3,3,9999),
	 ('wm_sample_treelist','샘플1_트리그리드',NULL,'/gui/wm_sample_treelist','N',20,NULL,'2025-04-02 14:01:15.186+09','2025-04-02 14:02:25.487+09',3,3,9999),
	 ('wm_sample_form','샘플2_폼화면',NULL,'/gui/wm_sample_form','N',30,NULL,'2025-04-02 14:01:24.279+09','2025-04-02 14:02:25.491+09',3,3,9999),
	 ('wm_sample_chart','샘플3_차트',NULL,'/gui/wm_sample_chart','N',40,NULL,'2025-04-02 14:01:28.991+09','2025-04-02 14:02:25.495+09',3,3,9999),
	 ('wm_sample_popup','샘플4_팝업',NULL,'/gui/wm_sample_popup','N',50,NULL,'2025-04-02 14:01:32.741+09','2025-04-02 14:02:25.498+09',3,3,9999),
	 ('wm_sample_editor','샘플5_웹에디터',NULL,'/gui/wm_sample_editor','N',60,NULL,'2025-04-02 14:01:49.103+09','2025-04-02 14:02:25.502+09',3,3,9999),
	 ('wm_sample_spread_sheet','샘플6_스프레드시트',NULL,'/gui/wm_sample_spread_sheet','N',70,NULL,'2025-04-02 14:01:55.159+09','2025-04-02 14:02:25.507+09',3,3,9999),
	 ('wm_sample_upload','샘플7_파일업로드',NULL,'/gui/wm_sample_upload','N',80,NULL,'2025-04-02 14:02:02.343+09','2025-04-02 14:02:25.511+09',3,3,9999),
	 ('wm_sample_alert_noti','샘플8_알람_노티',NULL,'/gui/wm_sample_alert_noti','N',90,NULL,'2025-04-02 14:02:07.329+09','2025-04-02 14:02:25.515+09',3,3,9999),
	 ('wm_sample_export','샘플9_Export',NULL,'/gui/wm_sample_export','N',100,NULL,'2025-04-02 14:02:11.948+09','2025-04-02 14:02:25.519+09',3,3,9999),
	 ('wm_sample_design','샘플10_디자인',NULL,'/gui/wm_sample_design','N',110,NULL,'2025-04-02 14:02:20.316+09','2025-04-02 14:02:25.524+09',3,3,9999),
	 ('wm_cm_material_loc','자재보관위치',NULL,'/gui/wm_cm_material_loc','N',30,NULL,'2025-04-22 10:38:55.592719+09','2025-05-22 16:38:38.200868+09',1,1,11),
	 ('wm_cm_equip_group','설비분류',NULL,'/gui/wm_cm_equip_group','N',50,NULL,'2025-04-22 10:39:12.71875+09','2025-05-22 16:38:38.211641+09',1,1,11),
	 ('wm_cm_wo_project','프로젝트',NULL,'/gui/wm_cm_wo_project','N',60,NULL,'2025-04-22 10:39:20.139363+09','2025-05-22 16:38:38.218206+09',1,1,11),
	 ('wm_cm_code','기초코드',NULL,'/gui/wm_cm_code','N',10,NULL,'2025-04-23 18:21:06.794658+09','2025-05-22 16:38:38.183274+09',1,1,11),
	 ('wm_cm_material','자재마스터',NULL,'/gui/wm_cm_material','N',10,NULL,'2025-04-23 14:49:24.69621+09','2025-04-23 14:49:29.862765+09',1,1,24),
	 ('wm_wo_dept_performance','부서별 기간별 WO 발행 실적',NULL,'/gui/wm_wo_dept_performance','N',10,NULL,'2025-01-09 13:57:44.691621+09','2025-06-23 10:54:06.61626+09',1,1,16),
	 ('wm_if_qms','QMS',NULL,'/gui/wm_if_qms','N',10,NULL,'2025-04-29 11:35:49.825704+09','2025-07-08 18:32:30.72185+09',3,3,25),
	 ('wm_if_van','VAN',NULL,'/gui/wm_if_van','N',20,NULL,'2025-04-29 11:35:54.333431+09','2025-07-08 18:32:30.729512+09',3,3,25),
	 ('wm_cm_equip_loc','설비위치정보',NULL,'/gui/wm_cm_equip_loc','N',40,NULL,'2025-04-22 10:39:04.054258+09','2025-05-22 16:38:38.206393+09',1,1,11),
	 ('wm_dept_work_costs','부서별 기간별 작업비용',NULL,'/gui/wm_dept_work_costs','N',20,NULL,'2025-01-09 13:57:44.69963+09','2025-06-23 10:54:06.629497+09',1,1,16),
	 ('wm_top_working_hours_wo','작업시간 상위 WO',NULL,'/gui/wm_top_working_hours_wo','N',30,NULL,'2025-01-09 13:57:44.703792+09','2025-06-23 10:54:06.638382+09',1,1,16),
	 ('wm_conservation_cost_status','보전비용 현황',NULL,'/gui/wm_conservation_cost_status','N',40,NULL,'2025-01-09 13:57:44.708277+09','2025-06-23 10:54:06.649719+09',1,1,16),
	 ('wm_top_wo_in_work_cost','작업비용 상위 WO',NULL,'/gui/wm_top_wo_in_work_cost','N',50,NULL,'2025-01-09 13:57:44.712973+09','2025-06-23 10:54:06.660123+09',1,1,16),
	 ('wm_outsourced_tasks_count','아웃소싱 작업건수',NULL,'/gui/wm_outsourced_tasks_count','N',60,NULL,'2025-01-09 13:57:44.719247+09','2025-06-23 10:54:06.671038+09',1,1,16),
	 ('wm_dept_pm_rate','부서별 예방 정비율',NULL,'/gui/wm_dept_pm_rate','N',70,NULL,'2025-01-09 13:57:44.724097+09','2025-06-23 10:54:06.684928+09',1,1,16),
	 ('wm_team_breakdown_costs','팀별 고장비용 현황',NULL,'/gui/wm_team_breakdown_costs','N',80,NULL,'2025-01-09 13:57:44.730042+09','2025-06-23 10:54:06.694579+09',1,1,16),
	 ('wm_dept_overdue_tasks','부서별 기간별 지연작업 목록',NULL,'/gui/wm_dept_overdue_tasks','N',90,NULL,'2025-01-09 13:57:44.734652+09','2025-06-23 10:54:06.705074+09',1,1,16),
	 ('wm_dept_task_compliance_rate','부서별 기간별 작업 준수율',NULL,'/gui/wm_dept_task_compliance_rate','N',100,NULL,'2025-01-09 13:57:44.742667+09','2025-06-23 10:54:06.714895+09',1,1,16),
	 ('wm_causes_of_each_failure_part','고장부위별 원인',NULL,'/gui/wm_causes_of_each_failure_part','N',110,NULL,'2025-01-09 13:57:44.749717+09','2025-06-23 10:54:06.725362+09',1,1,16),
	 ('wm_dept_work_request_stats','부서별 작업 요청 통계',NULL,'/gui/wm_dept_work_request_stats','N',120,NULL,'2025-01-09 13:57:44.754036+09','2025-06-23 10:54:06.734662+09',1,1,16),
	 ('wm_facility_treatment_status','기간별 불용처리 설비 현황',NULL,'/gui/wm_facility_treatment_status','N',30,NULL,'2025-01-09 13:17:55.725443+09','2025-06-23 10:54:24.144827+09',1,1,15),
	 ('wm_facility_mttr_mtbf','설비별 MTTR/MTBF',NULL,'/gui/wm_facility_mttr_mtbf','N',40,NULL,'2025-01-09 13:17:55.733269+09','2025-06-23 10:54:24.153877+09',1,1,15),
	 ('wm_category_equipment_status','카테고리별 설비 현황',NULL,'/gui/wm_category_equipment_status','N',50,NULL,'2025-01-09 13:17:55.738518+09','2025-06-23 10:54:24.164429+09',1,1,15),
	 ('wm_critical_equipment_status','중요도별 설비 고장 현황',NULL,'/gui/wm_critical_equipment_status','N',60,NULL,'2025-01-09 13:17:55.742668+09','2025-06-23 10:54:24.205026+09',1,1,15),
	 ('wm_facility_maintenance_cost','설비별 정비비용',NULL,'/gui/wm_facility_maintenance_cost','N',70,NULL,'2025-01-09 13:17:55.748069+09','2025-06-23 10:54:24.237795+09',1,1,15),
	 ('wm_facility_downtime','설비별 고장시간',NULL,'/gui/wm_facility_downtime','N',80,NULL,'2025-01-09 13:17:55.75257+09','2025-06-23 10:54:24.294087+09',1,1,15),
	 ('wm_facility_specifications','설비별 사양 목록',NULL,'/gui/wm_facility_specifications','N',90,NULL,'2025-01-09 13:17:55.759948+09','2025-06-23 10:54:24.320578+09',1,1,15),
	 ('wm_pm_schedule_m','PM 일정생성(수동)',NULL,'/gui/wm_pm_schedule_m','N',40,NULL,'2025-05-19 16:36:59.969801+09','2025-05-19 16:43:54.678145+09',1,1,7),
	 ('wm_if_mes_oee','OEE',NULL,'/gui/wm_if_mes_oee','N',50,NULL,'2025-07-08 18:29:45.659391+09','2025-07-08 18:30:23.236457+09',3,3,29),
	 ('wm_cm_holiday','휴일 스케줄',NULL,'/gui/wm_cm_holiday','N',70,NULL,'2025-05-22 16:38:33.925766+09','2025-05-22 16:38:38.224596+09',1,1,11),
	 ('wm_wo_hist','WO 작업이력 조회',NULL,'/gui/wm_wo_hist','N',10,NULL,'2025-05-23 15:31:27.397192+09','2025-05-23 17:35:17.361694+09',3,3,6),
	 ('wm_wo_cancel','취소된 WO 목록',NULL,'/gui/wm_wo_cancel','N',20,NULL,'2025-05-23 17:32:25.256153+09','2025-05-23 17:35:17.374681+09',3,3,6),
	 ('wm_wo_pending','미처리 WO 목록',NULL,'/gui/wm_wo_pending','N',30,NULL,'2025-05-23 17:35:08.543719+09','2025-05-23 17:35:17.491582+09',3,3,6),
	 ('wm_proc_opts','프로세스',NULL,'/gui/wm_proc_opts','N',10,NULL,'2025-06-19 09:55:06.475874+09','2025-06-19 09:55:19.851549+09',1,1,27),
	 ('wm_sche_opts','스케줄링',NULL,'/gui/wm_sche_opts','N',20,NULL,'2025-06-19 09:55:15.584536+09','2025-06-19 09:55:19.862315+09',1,1,27),
	 ('wm_monthly_maintenance_cost','설비별 월간 정비비용',NULL,'/gui/wm_monthly_maintenance_cost','N',20,NULL,'2025-01-09 13:17:55.720707+09','2025-06-23 10:54:24.132344+09',1,1,15),
	 ('wm_dt_main','생산라인현황',NULL,'/gui/wm_dt_main','N',30,NULL,'2025-06-27 16:53:33.611898+09','2025-06-27 16:53:43.701123+09',3,3,1),
	 ('wm_if_reflow_profile','Reflow Profile',NULL,'/gui/wm_if_reflow_profile','N',10,NULL,'2025-07-08 18:31:18.367633+09','2025-07-08 18:31:39.784555+09',3,3,30),
	 ('wm_if_sap_mat','SAP Material',NULL,'/gui/wm_if_sap_mat','N',10,NULL,'2025-07-08 18:28:35.429485+09','2025-07-08 18:29:04.374451+09',3,3,28),
	 ('wm_if_sap_bom','SAP BOM',NULL,'/gui/wm_if_sap_bom','N',20,NULL,'2025-07-08 18:28:38.463414+09','2025-07-08 18:29:04.389407+09',3,3,28),
	 ('wm_if_sap_stock','SAP Stock',NULL,'/gui/wm_if_sap_stock','N',30,NULL,'2025-07-08 18:28:31.566768+09','2025-07-08 18:29:04.390482+09',3,3,28),
	 ('wm_if_sap_pcb_random','SAP PCB Rand.',NULL,'/gui/wm_if_sap_pcb_random','N',40,NULL,'2025-07-08 18:28:48.827073+09','2025-07-08 18:29:04.390482+09',3,3,28),
	 ('wm_if_mes_product_plan','생산계획',NULL,'/gui/wm_if_mes_product_plan','N',10,NULL,'2025-07-08 18:29:43.075516+09','2025-07-08 18:30:23.211457+09',3,3,29),
	 ('wm_if_mes_workorder','작업지시',NULL,'/gui/wm_if_mes_workorder','N',20,NULL,'2025-07-08 18:29:38.433791+09','2025-07-08 18:30:23.217969+09',3,3,29),
	 ('wm_if_mes_lot_history','LOT Hist.',NULL,'/gui/wm_if_mes_lot_history','N',30,NULL,'2025-07-08 18:29:31.320481+09','2025-07-08 18:30:23.225525+09',3,3,29),
	 ('wm_if_mes_fpy','FPY조회',NULL,'/gui/wm_if_mes_fpy','N',40,NULL,'2025-07-08 18:29:34.294351+09','2025-07-08 18:30:23.230592+09',3,3,29),
	 ('wm_if_viscosity_check','솔더점도측정',NULL,'/gui/wm_if_viscosity_check','N',20,NULL,'2025-07-08 18:31:12.967337+09','2025-07-08 18:31:39.792506+09',3,3,30),
	 ('wm_if_tension_check','스텐실텐션체크',NULL,'/gui/wm_if_tension_check','N',30,NULL,'2025-07-08 18:31:26.719379+09','2025-07-08 18:31:39.798913+09',3,3,30),
	 ('wm_if_mnt_pickup_rate','마운터 Pickup Rate',NULL,'/gui/wm_if_mnt_pickup_rate','N',40,NULL,'2025-07-08 18:30:30.144376+09','2025-07-08 18:31:39.805749+09',3,3,30),
	 ('wm_if_equ_result','설비실적(측정데이터)',NULL,'/gui/wm_if_equ_result','N',30,NULL,'2025-04-29 11:36:03.43116+09','2025-07-08 18:32:30.734633+09',3,3,25),
	 ('wm_if_topic_data','TOPIC데이터확인',NULL,'/gui/wm_if_topic_data','N',40,NULL,'2025-04-29 11:36:37.656223+09','2025-07-08 18:32:30.739363+09',3,3,25),
	 ('wm_check_result','점검 결과 조회',NULL,'/gui/wm_check_result','N',30,NULL,'2025-07-16 15:19:51.146965+09','2025-07-16 15:21:40.999601+09',3,3,8),
	 ('wm_check_wo_issued','점검이상 발행WO',NULL,'/gui/wm_check_wo_issued','N',40,NULL,'2025-07-16 15:20:54.266097+09','2025-07-16 15:21:41.019425+09',3,3,8);




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
, ('RANDOM_FOREST','랜덤포레스트 하이퍼파라미터','N','','Y','N',now())
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

	-- RANDOM_FOREST 파라미터
	, ('RANDOM_FOREST', 'N_ESTIMATORS',       '트리 개수',           '', NULL, 'Y', 'N', NOW())
	, ('RANDOM_FOREST', 'MAX_DEPTH',          '최대 깊이',           '', NULL, 'Y', 'N', NOW())
	, ('RANDOM_FOREST', 'MIN_SAMPLES_SPLIT',  '최소 분할 샘플 수',   '', NULL, 'Y', 'N', NOW())
	, ('RANDOM_FOREST', 'MIN_SAMPLES_LEAF',   '최소 리프 샘플 수',   '', NULL, 'Y', 'N', NOW())
	, ('RANDOM_FOREST', 'MAX_FEATURES',       '최대 특성 수',        '', NULL, 'Y', 'N', NOW())
	, ('RANDOM_FOREST', 'BOOTSTRAP',          '부트스트랩 사용여부', '', NULL, 'Y', 'N', NOW())
	, ('RANDOM_FOREST', 'RANDOM_STATE',       '랜덤 시드',           '', NULL, 'Y', 'N', NOW())	

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


--품목
--alter SEQUENCE material_id_seq restart WITH 1;

// 아래 품목그룸 코드를 mat_grp 테이블에 insert하는 구문을 작성
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
	('hpc1_매거진_Q', 'Q-factor', NULL, '2025-02-06 14:50:59.140', '2025-02-06 14:50:59.140', 3, 3, NULL, NULL);
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

