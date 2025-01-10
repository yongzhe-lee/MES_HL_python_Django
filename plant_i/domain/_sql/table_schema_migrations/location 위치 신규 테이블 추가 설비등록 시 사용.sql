CREATE TABLE public."location" (
	loc_pk serial4 NOT NULL,
	loc_nm varchar(100) NOT NULL,
	loc_cd varchar(30) NOT NULL,
	up_loc_pk int4 NULL,
	loc_status varchar(10) NOT NULL,
	site_id varchar(20) NULL,
	plant_yn bpchar(1) DEFAULT 'N'::bpchar NULL,
	building_yn bpchar(1) DEFAULT 'N'::bpchar NULL,
	spshop_yn bpchar(1) DEFAULT 'N'::bpchar NULL,
	isa95_class varchar(10) NULL,
	map_draw_file_cd varchar(50) NULL,
	out_order int2 DEFAULT 99 NULL,
	use_yn bpchar(1) DEFAULT 'Y'::bpchar NULL,
	del_yn bpchar(1) DEFAULT 'N'::bpchar NULL,
	"_created" timestamptz NOT NULL,
	"_modified" timestamptz NULL,
	"_creater_id" int4 NULL,
	"_modifier_id" int4 NULL,
	CONSTRAINT location_pk PRIMARY KEY (loc_pk),
	CONSTRAINT location_uk1 UNIQUE (loc_cd, site_id),
	CONSTRAINT location_fk FOREIGN KEY (up_loc_pk) REFERENCES public."location"(loc_pk)
);  
    
COMMENT ON COLUMN public."location".loc_pk IS '위치PK';
COMMENT ON COLUMN public."location".loc_nm IS '위치명';
COMMENT ON COLUMN public."location".loc_cd IS '위치코드';
COMMENT ON COLUMN public."location".up_loc_pk IS '상위위치PK';
COMMENT ON COLUMN public."location".loc_status IS '상태';
COMMENT ON COLUMN public."location".site_id IS '사이트ID';
COMMENT ON COLUMN public."location".plant_yn IS '공장 여부';
COMMENT ON COLUMN public."location".building_yn IS '건물 여부';
COMMENT ON COLUMN public."location".spshop_yn IS '보전자재창고 여부';
COMMENT ON COLUMN public."location".isa95_class IS 'ISA95 분류';
COMMENT ON COLUMN public."location".map_draw_file_cd IS 'MAP 도면파일 코드';
COMMENT ON COLUMN public."location".out_order IS '순서';
COMMENT ON COLUMN public."location".use_yn IS '사용여부';
COMMENT ON COLUMN public."location".del_yn IS '삭제여부';

