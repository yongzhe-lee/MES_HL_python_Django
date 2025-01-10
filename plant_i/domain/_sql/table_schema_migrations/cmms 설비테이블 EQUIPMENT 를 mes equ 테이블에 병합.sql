
/*
--1. 컬럼 매핑
--두 테이블의 구조를 비교하여 EQUIPMENT의 데이터를 equ로 매핑합니다. 
EQUIPMENT 컬럼	EQU 컬럼		설명
equip_pk		id	Primary Key 매핑
equip_cd		Code			고유 코드 매핑
equip_nm		Name			장비 이름
equip_dsc		Description		장비 설명
maker_pk		Maker			제조사 매핑
model_number	Model			모델 번호
serial_number	SerialNumber	시리얼 번호
make_dt			ProductionYear	제작 연도
install_dt		InstallDate	설치 날짜
disposed_date	DisposalDate	폐기 날짜
disposed_type	DisposalReason	폐기 사유
Status			equip_status	상태
 * */

-- EQUIPMENT 테이블의 칼럼을 EQU 테이블에 추가
ALTER TABLE public.equ
    ADD COLUMN equip_category_id varchar(2) NULL,
    ADD COLUMN up_equip_pk int4 NULL,
    ADD COLUMN loc_pk int4 NULL,
--    ADD COLUMN equip_status varchar(20) DEFAULT 'ES_OPER' NOT NULL, 
    ADD COLUMN site_id varchar(20) NULL,
    ADD COLUMN equip_class_path varchar(20) NULL,
    ADD COLUMN equip_class_desc varchar(120) NULL,
    ADD COLUMN asset_nos varchar(500) NULL,
    ADD COLUMN warranty_dt date NULL,
    ADD COLUMN buy_cost int8 NULL,
    ADD COLUMN photo_file_grp_cd varchar(50) NULL,
    ADD COLUMN doc_file_grp_cd varchar(50) NULL,
    ADD COLUMN import_rank_pk int2 NULL,
    ADD COLUMN environ_equip_yn bpchar(1) DEFAULT 'N' NOT NULL,
    ADD COLUMN ccenter_cd varchar(30) NULL,
    ADD COLUMN breakdown_dt date NULL,
    ADD COLUMN del_yn bpchar(1) DEFAULT 'N' NOT NULL,
    ADD COLUMN process_cd varchar(50) DEFAULT 'TEMP' NULL,
    ADD COLUMN system_cd varchar(50) DEFAULT 'temp' NULL,
    ADD COLUMN first_asset_status varchar(20) NULL;

COMMENT ON COLUMN public.equ.equip_category_id IS '설비 카테고리ID';
COMMENT ON COLUMN public.equ.up_equip_pk IS '상위설비PK';
COMMENT ON COLUMN public.equ.loc_pk IS '위치PK';
--COMMENT ON COLUMN public.equ.equip_status IS '상태(O 가동중, B 고장, I 유휴, D 불용, default O)';
COMMENT ON COLUMN public.equ.site_id IS '사이트(사업장)';
COMMENT ON COLUMN public.equ.equip_class_path IS '설비분류 경로';
COMMENT ON COLUMN public.equ.equip_class_desc IS '설비분류 설명';
COMMENT ON COLUMN public.equ.asset_nos IS '자산번호(n개, 콤마구분)';
COMMENT ON COLUMN public.equ.warranty_dt IS '보증만료일';
COMMENT ON COLUMN public.equ.buy_cost IS '구매비용';
COMMENT ON COLUMN public.equ.photo_file_grp_cd IS '사진파일그룹코드';
COMMENT ON COLUMN public.equ.doc_file_grp_cd IS '기술문서파일그룹코드';
COMMENT ON COLUMN public.equ.import_rank_pk IS '중요도등급PK';
COMMENT ON COLUMN public.equ.environ_equip_yn IS '환경설비 여부';
COMMENT ON COLUMN public.equ.ccenter_cd IS '코스트센터 코드';
COMMENT ON COLUMN public.equ.breakdown_dt IS '고장일시';
COMMENT ON COLUMN public.equ.del_yn IS '삭제여부';
COMMENT ON COLUMN public.equ.process_cd IS '프로세스 코드';
COMMENT ON COLUMN public.equ.system_cd IS '시스템 코드';

