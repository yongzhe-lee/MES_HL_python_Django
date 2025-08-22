
truncate table equ cascade;
alter SEQUENCE equ_id_seq restart WITH 1;

--truncate table tag cascade;
--ALTER TABLE equ ALTER COLUMN del_yn SET DEFAULT 'N';


-- HPC#1
alter SEQUENCE equ_id_seq restart WITH 1;
INSERT INTO equ
(id, "Code", "Name", "Maker", "_created", "_modified", "_creater_id", "_modifier_id",  "MESCode", "SAPCode", line_id) 
values
(1, 'hpc1.load', 'HPC#1 매거진로더', '은일', now(), now(), 1, 1, '', '', 1),
(2, 'hpc1.flash' , 'HPC#1플래쉬프로그램입력', '코어솔루션', now(), now(), 1, 1, 'PCU111001', '', 1),
(3, 'hpc1.ict' , 'HPC#1 ICT', '코어솔루션', now(), now(), 1, 1, '', 'PCU112001', 1),
(4, 'hpc1.coatload', 'HPC#1 PCB코팅로더', 'CJT', now(), now(), 1, 1, '', '', 1),
(5, 'hpc1.coating1', 'HPC#1 Conformal코팅1', '', now(), now(), 1, 1, '', '', 1),
(6, 'hpc1.coating2', 'HPC#1 Conformal코팅2', '', now(), now(), 1, 1, '', '', 1),
(7, 'hpc1.coatvision', 'HPC#1 PCB코팅비젼', '', now(), now(), 1, 1, '', '', 1),
(8, 'hpc1.pcbrev', 'HPC#1 PCB반전', 'CJT', now(), now(), 1, 1, '', '', 1),
(9, 'hpc1.curing', 'HPC#1 코팅경화Curing', 'YJE', now(), now(), 1, 1, '', '', 1),
(10, 'hpc1.frobackload', 'HPC#1 프론트백로더', 'CJT', now(), now(), 1, 1, '', '', 1),
(11, 'hpc1.uh.load', 'HPC#1 Upper 하우징 로딩', 'CJT', now(), now(), 1, 1, '', '', 1),
(12, 'hpc1.tim', 'HPC#1 TIM도포', 'CJT', now(), now(), 1, 1, '', '', 1),
(13, 'hpc1.lh.load', 'HPC#1 Lower하우징로딩', 'CJT', now(), now(), 1, 1, '', '',1),
(14, 'hpc1.scrwt', 'HPC#1 스크류체결', 'CJT', now(), now(), 1, 1, '', '',1),
(15, 'hpc1.scrwt.height', 'HPC#1 스크류높이체크', 'CJT', now(), now(), 1, 1, '', '',1),
(16, 'hpc1.fclip', 'HPC#1 Fan&Clip Fan조립', 'CJT', now(), now(), 1, 1, '', '', 1),
(17, 'hpc1.fclip.height', 'HPC#1 Fan&Clip 높이체크', 'CJT', now(), now(), 1, 1, '', '', 1),
(18, 'hpc1.fclip.clip', 'HPC#1 Fan&Clip 클립', 'CJT', now(), now(), 1, 1, '', '', 1),
(19, 'hpc1.eol1', 'HPC#1 EOL1', '일신', now(), now(), 1, 1, '', '', 1),
(20, 'hpc1.eol2', 'HPC#1 EOL2', '일신', now(), now(), 1, 1, '', '', 1),
(21, 'hpc1.pinchk', 'HPC#1 Pin검사', 'CJT', now(), now(), 1, 1, '', '', 1),
(22, 'hpc1.labeling', 'HPC#1 Pin검사 라벨링', 'CJT', now(), now(), 1, 1, '', '', 1),
(23, 'hpc1.brackassm', 'HPC#1 브라켓조립', 'CJT', now(), now(), 1, 1, '', '', 1),
(24, 'hpc1.brackassm.height', 'HPC#1 브라켓높이', 'CJT', now(), now(), 1, 1, '', '', 1)

--추가
;


-- SMT#4설비
INSERT INTO equ (id, "Code", "Name", "Maker", "_created", "_modified", "_creater_id", "_modifier_id",  "MESCode", "SAPCode", line_id) 
values
(25, 'smt4.loader', 'SMT#4 매거진로더', '', now(), now(), 1, 1, '', '', 2),
(26, 'smt4.laserrmarking', 'SMT#4 PCB Laser Marking', '', now(), now(), 1, 1, '', '', 2),
(27, 'smt4.sp1', 'SMT#4 SP1', '', now(), now(), 1, 1, '', '', 2),
(28, 'smt4.sp2', 'SMT#4 SP2', '', now(), now(), 1, 1, '', '', 2),
(29, 'smt4.spi', 'SMT#4 SPI', '', now(), now(), 1, 1, '', '', 2),
(30, 'smt4.mnt', 'SMT#4 마운터', '', now(), now(), 1, 1, '', '', 2),
(31, 'smt4.pre-aoi', 'SMT#4 PRE-AOI', '', now(), now(), 1, 1, '', '', 2),
(32, 'smt4.reflow', 'SMT#4 Reflow Soldering', '', now(), now(), 1, 1, '', '', 2),
(33, 'smt4.aoi', 'SMT#4 AOI', '', now(), now(), 1, 1, '', '', 2),
(34, 'smt4.aoireview', 'SMT#4 AOI REVIRE', '', now(), now(), 1, 1, '', '', 2),
(35, 'smt4.unloader', 'SMT#4 매거진언로더', '', now(), now(), 1, 1, '', '', 2),
(36, 'hpc1.packing', 'HPC#1 Packing', '', now(), now(), 1, 1, '', '', 1)
;

INSERT INTO equ (id, "Code", "Name", "Maker", "_created", "_modified", "_creater_id", "_modifier_id",  "MESCode", "SAPCode", line_id) 
values
(37, 'smt4.mnt1', 'SMT#4 마운터모듈1', '', now(), now(), 1, 1, '', '', 2),
(38, 'smt4.mnt2', 'SMT#4 마운터모듈2', '', now(), now(), 1, 1, '', '', 2),
(39, 'smt4.mnt3', 'SMT#4 마운터모듈3', '', now(), now(), 1, 1, '', '', 2),
(40, 'smt4.mnt4', 'SMT#4 마운터모듈4', '', now(), now(), 1, 1, '', '', 2),
(41, 'smt4.mnt5', 'SMT#4 마운터모듈5', '', now(), now(), 1, 1, '', '', 2),
(42, 'smt4.mnt6', 'SMT#4 마운터모듈6', '', now(), now(), 1, 1, '', '', 2),
(43, 'smt4.mnt7', 'SMT#4 마운터모듈7', '', now(), now(), 1, 1, '', '', 2),
(44, 'smt4.mnt8', 'SMT#4 마운터모듈8', '', now(), now(), 1, 1, '', '', 2),
(45, 'smt4.mnt9', 'SMT#4 마운터모듈9', '', now(), now(), 1, 1, '', '', 2),
(46, 'smt4.mnt10', 'SMT#4 마운터모듈10', '', now(), now(), 1, 1, '', '', 2),
(47, 'smt4.mnt11', 'SMT#4 마운터모듈11', '', now(), now(), 1, 1, '', '', 2),
(48, 'smt4.mnt12', 'SMT#4 마운터모듈12', '', now(), now(), 1, 1, '', '', 2),
(49, 'smt4.mnt13', 'SMT#4 마운터모듈13', '', now(), now(), 1, 1, '', '', 2),
(50, 'smt4.mnt14', 'SMT#4 마운터모듈14', '', now(), now(), 1, 1, '', '', 2),
(51, 'smt4.mnt15', 'SMT#4 마운터모듈15', '', now(), now(), 1, 1, '', '', 2),
(52, 'hpc1.tim.assy', 'HPC#1 Housing & PCB Assembly', '', now(), now(), 1, 1, '', '', 1),
(53, 'hpc1.fclip.screw', 'HPC#1 Fan&Clip Screw 체결', '', now(), now(), 1, 1, '', '', 1);



--select currval('equ_id_seq');
alter SEQUENCE equ_id_seq restart WITH 53;

/*
알람		ALARM
온도		TEMP
전압		VOLT
전류		CURRENT
가동비가동		RUN
카운터		COUNTER
*/

truncate table tag_grp cascade;
alter SEQUENCE tag_grp_id_seq restart WITH 1;
insert into tag_grp ("Code", "Name", "_created") values('PLC', 'PLC', now());
insert into tag_grp ("Code", "Name", "_created") values('EM', '전력량계', now());
alter SEQUENCE tag_grp_id_seq restart WITH 2;

truncate table data_src cascade;
alter SEQUENCE data_src_id_seq restart WITH 1;

/*전력량계*/
insert into data_src (id, "Name", "SourceType", _created) values (1, '플래쉬 전력량계1', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (2, 'ICT 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (3, '컨포멀코팅1 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (4, '컨포멀코팅2 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (5, '코팅비전 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (6, 'Curring 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (7, '프론트백로더 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (8, '업하우징 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (9, 'TIM도포 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (10, 'LOW하우징 전력량계0', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (11, '스크류체결 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (12, '스크류팬클립 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (13, 'EOL1 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (14, 'EOL2 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (15, '핀체크 전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (16, '브라켓 조립전력량계', 'EM', now());
insert into data_src (id, "Name", "SourceType", _created) values (17,'패킹 전력량계', 'EM', now());


/*PLC*/
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (31, '매거진로더PLC', 'PLC', now(), 1);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (32, '플래쉬프로그램입력PLC', 'PLC', now(), 2);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (33, 'ICTPLC', 'PLC', now(), 3);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (34, 'PCB코팅로더PLC', 'PLC', now(), 4);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (35, 'PCB반전PLC', 'PLC', now(), 5);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (36, '코팅경화CuringPLC', 'PLC', now(), 6);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (37, '프론트백PCB로딩PLC', 'PLC', now(), 7);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (38, 'Upper 하우징 로딩PLC', 'PLC', now(), 8);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (39, 'TIM도포PLC', 'PLC', now(), 9);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (40, 'Lower하우징로딩PLC', 'PLC', now(), 10);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (41, '스크류체결PLC', 'PLC', now(), 11);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (42, 'Fan&Clip조립PLC', 'PLC', now(), 12);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (43, 'EOL1PLC', 'PLC', now(), 13);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (44, 'EOL2PLC', 'PLC', now(), 14);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (45, 'Pin검사&라벨PLC', 'PLC', now(), 15);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (46, '브라켓조립PLC', 'PLC', now(), 16);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (47, 'SMT#3로더PLC', 'PLC', now(), 17);
insert into data_src (id, "Name", "SourceType", _created, "Equipment_id") values (48, 'SMT#3언로더PLC', 'PLC', now(), 18);
alter SEQUENCE data_src_id_seq restart WITH 49;

/*매거진로더*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created") 
values 
('hpc1.load.au.op','hpc1매거진로더 자동운전', 1, now()),
('hpc1.load.au.stop','hpc1매거진로더 자동정지', 1, now()),
('hpc1.load.lamp.g','hpc1매거진로더 경광등(GREEN)', 1, now()),
('hpc1.load.lamp.y','hpc1매거진로더 경광등(YELLOW)', 1, now()),
('hpc1.load.lamp.r','hpc1매거진로더 경광등(RED)', 1, now()),
('hpc1.load.air.press','hpc1매거진로더 공압상태', 1, now()),
('hpc1.load.door','hpc1매거진로더 도어상태', 1, now()),
('hpc1.load.prod.detect1','hpc1매거진로더 제품감지1', 1, now()),
('hpc1.load.prod.detect2','hpc1매거진로더 제품감지2', 1, now()),
('hpc1.load.prod.detect3','hpc1매거진로더 제품감지3', 1, now()),
('hpc1.load.prod.info','hpc1매거진로더 기종정보', 1, now()),
('hpc1.load.out.sens','hpc1매거진로더 아웃센서 ', 1, now()),
('hpc1.load.accu.cnt','hpc1매거진로더 아웃카운터 누적', 1, now()),
('hpc1.load.work.cnt','hpc1매거진로더 워크카운터', 1, now()),
('hpc1.load.chg.reset','hpc1매거진로더 카운터리셋', 1, now()),
('hpc1.load.pitch','hpc1매거진로더 PITCH', 1, now()),
('hpc1.load.alm.cnt','hpc1매거진로더 LOADER알람갯수', 1, now())
;

/*플래쉬프로그램입력*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.flash.au.md','hpc1 flash자동모드', 2, now()),
('hpc1.flash.ma.md','hpc1 flash수동모드', 2, now()),
('hpc1.flash.au.op','hpc1 flash자동운전', 2, now()),
('hpc1.flash.au.stop','hpc1 flash자동정지', 2, now()),
('hpc1.flash.emer.stop','hpc1 flash비상정지', 2, now()),
('hpc1.flash.1f.conv.op.step','hpc1 flash1f컨베이어자동운전STEP', 2, now()),
('hpc1.flash.1f.tcyli.op.step','hpc1 flash1f실린더자동운전STEP', 2, now()),
('hpc1.flash.2f.conv.op.step','hpc1 flash2f컨베이어자동운전STEP', 2, now()),
('hpc1.flash.2f.tcyli.op.step','hpc1Flash2f실린더자동운전STEP', 2, now()),
('hpc1.flash.lamp.r','hpc1 flash경광등(RED)', 2, now()),
('hpc1.flash.lamp.y','hpc1 flash경광등(YELLOW)', 2, now()),
('hpc1.flash.lamp.g','hpc1 flash경광등(GREEN)', 2, now()),
('hpc1.flash.buzz','hpc1 flashBUZZER', 2, now()),
('hpc1.flash.1f.door1','hpc1 flash도어1f-1상태', 2, now()),
('hpc1.flash.1f.door2','hpc1 flash도어1f-2상태', 2, now()),
('hpc1.flash.2f.door1','hpc1 flash도어2f-1상태', 2, now()),
('hpc1.flash.1f.prod.detect1','hpc1 flash제품감지 1F-1', 2, now()),
('hpc1.flash.1f.prod.detect2','hpc1 flash제품감지 1F-2', 2, now()),
('hpc1.flash.1f.prod.detect3','hpc1 flash제품감지 1F-3', 2, now()),
('hpc1.flash.1f.prod.detect4','hpc1 flash제품감지 1F-4', 2, now()),
('hpc1.flash.1f.prod.detect5','hpc1 flash제품감지 1F-5', 2, now()),
('hpc1.flash.1f.prod.detect6','hpc1 flash제품감지 1F-6', 2, now()),
('hpc1.flash.2f.prod.detect1','hpc1 flash제품감지 2F-1', 2, now()),
('hpc1.flash.2f.prod.detect2','hpc1 flash제품감지 2F-2', 2, now()),
('hpc1.flash.2f.prod.detect3','hpc1 flash제품감지 2F-3', 2, now()),
('hpc1.flash.2f.prod.detect4','hpc1 flash제품감지 2F-4', 2, now()),
('hpc1.flash.2f.prod.detect5','hpc1 flash제품감지 2F-5', 2, now()),
('hpc1.flash.2f.prod.detect6','hpc1 flash제품감지 2F-6', 2, now()),
('hpc1.flash.prod.info','hpc1 flash 기종정보', 2, now()),
('hpc1.flash.elev.op1','hpc#1 flash 엘리베이터운전1', 2, now()),
('hpc1.flash.elev.op2','hpc#1 flash 엘리베이터운전2', 2, now()),

('hpc1.flash.alm.cnt','hpc1 flash 알람여부', 2, now()), /*M10000*/
('hpc1.flash.air.press','hpc1 flash 공압상태', 2, now()),
;

insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.flash.1f.cyl.up','hpc1 flash 1층실린더업',2, now()),
('hpc1.flash.1f.cyl.down','hpc1 flash 1츨실린더다운',2, now()),
('hpc1.flash.1f.conv.up','hpc1 flash 1층 컨베이어업',2, now()),
('hpc1.flash.1f.conv.down','hpc1 flash 1층 컨베이어다운',2, now()),
('hpc1.flash.2f.cyl.up','hpc1 flash 2층실린더업',2, now()),
('hpc1.flash.2f.cyl.down','hpc1 flash 2층실린더다운',2, now()),
('hpc1.flash.2f.conv.up','hpc1 flash 2층 컨베이어업',2, now()),
('hpc1.flash.2f.conv.down','hpc1 flash 2층 컨베이어다운',2, now())
;

insert into tag(tag_code, tag_name,"Equipment_id", "_created", tag_group_id)
values
('hpc1.flash.tp.use.cnt','hpc1 flash Test Proobe 사용COUNT',2, now(), 8), 
('hpc1.flash.tp.near.end.cnt','hpc1 flash Test Proobe 사용 임박 COUNT',2, now(), 8), 
('hpc1.flash.tp.replace.cycle','hpc1 flash Test Proobe 교체 주기',2, now(), 8), 
('hpc1.flash.mst.smp.op.mode','hpc1 flash 제품 투입 수량',2, now(), 8)
;




/*ICT*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.ict.au.op','hpc1 ict자동운전', 3, now()),
('hpc1.ict.au.stop','hpc1 ict자동정지', 3, now()),
('hpc1.ict.au.md','hpc1 ict자동운전모드', 3, now()),
('hpc1.ict.ma.md','hpc1 ict수동운전모드', 3, now()),
('hpc1.ict.emer.stop','hpc1 ict비상정지', 3, now()),
('hpc1.ict.conv.op.step','hpc1 ict컨베이버자동운전STEP', 3, now()),
('hpc1.ict.tcyli.op.step','hpc1 ict실린더자동운전STEP', 3, now()),
('hpc1.ict.lamp.r','hpc1 ict경광등(RED)', 3, now()),
('hpc1.ict.lamp.y','hpc1 ict경광등(YELLOW)', 3, now()),
('hpc1.ict.lamp.g','hpc1 ict경광등(GREEN)', 3, now()),
('hpc1.ict.buzz','hpc1 ict BUZZER', 3, now()),
('hpc1.ict.door','hpc1 ict 도어상태', 3, now()),
('hpc1.ict.cyl.up','hpc1 ict 실린더작동업', 3, now()),
('hpc1.ict.cyl.down','hpc1 ict 실린더작동다운', 3, now()),
('hpc1.ict.prod.detect1','hpc1 ict 제품감지1', 3, now()),
('hpc1.ict.prod.detect2','hpc1 ict 제품감지2', 3, now()),
('hpc1.ict.prod.detect3','hpc1 ict 제품감지3', 3, now()),
('hpc1.ict.prod.detect4','hpc1 ict 제품감지4', 3, now()),
('hpc1.ict.prod.detect5','hpc1 ict 제품감지5', 3, now()),
('hpc1.ict.prod.detect6','hpc1 ict 제품감지6', 3, now()),
('hpc1.ict.prod.info','hpc1 ict 기종정보', 3, now()),
('hpc1.ict.air.press','hpc1 ict 공압상태', 3, now()),
('hpc1.ict.alm.cnt','hpc1 ict 알람여부', 3,now());

insert into tag(tag_code, tag_name,"Equipment_id", "_created", tag_group_id)
values
('hpc1.ict.tp.use.cnt','hpc1 ICT 1단 설비Test Proobe 사용COUNT',2, now(), 8), 
('hpc1.ict.tp.near.end.cnt','hpc1 1단 ICT 설비Test Proobe 사용 임박 COUNT',2, now(), 8), 
('hpc1.ict.tp.replace.cycle','hpc1 1단 ICT 설비Test Proobe 교체 주기',2, now(), 8), 
('hpc1.ict.mst.smp.op.mode','hpc1 1단 ICT 설비마스터샘플 모드',2, now(), 8)
;



insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values 
  ('hpc1.ict.conv.up','hpc1 ICT 컨베이어 작동업', 3,now()),
  ('hpc1.ict.conv.down','hpc1 ICT 컨베이어다운', 3,now()) ,
('hpc1.ict.inconv.prod.detect','Link Conveyor(input)컨베이어제품 진입 감지 센서',2, now(), 8), 
('hpc1.ict.inconv.sec1.detect','Link Conveyor(input)컨베이어 1구간 제품 감지 센서',2, now(), 8), 
('hpc1.ict.inconv.sec2.detect','Link Conveyor(input)컨베이어 2구간 제품 감지 센서',2, now(), 8), 
('hpc1.ict.inconv.sec3.detect','Link Conveyor(input)컨베이어 3구간 제품 감지 센서',2, now(), 8), 
('hpc1.ict.inconv.sec4.detect','Link Conveyor(input)컨베이어 4구간 제품 감지 센서',2, now(), 8), 
('hpc1.ict.inconv.prod.out.detect','Link Conveyor(input)컨베이어 제품 배출 감지 센서',2, now(), 8), 
('hpc1.ict.outconv.prod.detect','Link Conveyor(out)컨베이어 제품 진입 감지 센서',2, now(), 8), 
('hpc1.ict.outconv.sec1.detect','Link Conveyor(out)컨베이어 1구간 제품 감지 센서',2, now(), 8), 
('hpc1.ict.outconv.sec2.detect','Link Conveyor(out)컨베이어 2구간 제품 감지 센서',2, now(), 8), 
('hpc1.ict.outconv.prod.out.detect','Link Conveyor(out)컨베이어 제품 배출 감지 센서',2, now(), 8), 
('hpc1.ict.ng.buff.good.cnt','NG Buffer제품OK카운터 ',2, now(), 8), 
('hpc1.ict.ng.buff.defect.cnt','NG Buffer제품NG카운터',2, now(), 8), 
('hpc1.ict.ng.buff.prod.detect','NG Buffer제품감지',2, now(), 8)
;


  ;



/*PCB코팅로더*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.coatload.op.mode','PCB코팅로더자동/수동모드', 4, now()),
('hpc1.coatload.au.op','PCB코팅로더자동운전', 4, now()),
('hpc1.coatload.au.stop','PCB코팅로더자동정지', 4, now()),
('hpc1.coatload.emer.stop','PCB코팅로더비상정지', 4, now()),
('hpc1.coatload.au.op.step','PCB코팅로더자동운전_STEP', 4, now()),
('hpc1.coatload.lamp.g','PCB코팅로더경광등(GREEN)', 4, now()),
('hpc1.coatload.lamp.y','PCB코팅로더경광등(YELLOW)', 4, now()),
('hpc1.coatload.lamp.r','PCB코팅로더경광등(RED)', 4, now()),
('hpc1.coatload.air.press','PCB코팅로더공압상태', 4, now()),
('hpc1.coatload.door1','PCB코팅로더 도어상태1', 4, now()),
('hpc1.coatload.door2','PCB코팅로더 도어상태2', 4, now()),
('hpc1.coatload.door3','PCB코팅로더 도어상태3', 4, now()),
('hpc1.coatload.door4','PCB코팅로더 도어상태4', 4, now()),
('hpc1.coatload.door5','PCB코팅로더 도어상태5', 4, now()),
('hpc1.coatload.prod.detect1','PCB코팅로더제품감지1', 4, now()),
('hpc1.coatload.prod.detect2','PCB코팅로더제품감지2', 4, now()),
('hpc1.coatload.prod.info','PCB코팅로더기종정보', 4, now()),
('hpc1.coatload.ct','PCB코팅로더C/T', 4, now()),
('hpc1.coatload.alm.cnt','PCB코팅로더알람갯수', 4, now())
;


/*PCB반전*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.pcbrev.op.mode','hpc1 PCB반전자동/수동모드', 5, now()),
('hpc1.pcbrev.au.op','hpc1 PCB반전자동운전', 5, now()),
('hpc1.pcbrev.au.stop','hpc1 PCB반전자동정지', 5, now()),
('hpc1.pcbrev.emer.stop','hpc1 PCB반전비상정지', 5, now()),
('hpc1.pcbrev.au.op.step','hpc1 PCB반전자동운전_STEP', 5, now()),
('hpc1.pcbrev.lamp.g','hpc1 PCB반전경광등(GREEN)', 5, now()),
('hpc1.pcbrev.lamp.y','hpc1 PCB반전경광등(YELLOW)', 5, now()),
('hpc1.pcbrev.lamp.r','hpc1 PCB반전경광등(RED)', 5, now()),
('hpc1.pcbrev.door','hpc1 PCB반전도어상태', 5, now()),
('hpc1.pcbrev.prod.detect','hpc1 PCB반전제품감지', 5, now()),
('hpc1.pcbrev.prod.info','hpc1 PCB반전기종정보', 5, now()),
('hpc1.pcbrev.ct','hpc1 PCB반전C/T', 5, now()),
('hpc1.pcbrev.air.press','hpc1 PCB반전공압상태', 5, now()),
('hpc1.pcbrev.alm','hpc1 PCB반전알람', 5, now()),
('hpc1.pcbrev.alm.cnt','hpc1 PCB반전알람갯수', 5, now())
;

/*CURING*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.curing.au.md','hpc1 CURING자동모드', 6, now()),
('hpc1.curing.ma.md','hpc1 CURING수동모드', 6, now()),
('hpc1.curing.au.op','hpc1 CURING자동운전', 6, now()),
('hpc1.curing.au.stop','hpc1 CURING자동정지', 6, now()),
('hpc1.curing.emer.stop','hpc1 CURING비상정지', 6, now()),
('hpc1.curing.au.op.step','hpc1 CURING자동운전_ STEP', 6, now()),
('hpc1.curing.prod.detect.in','hpc1 CURING제품감지(in)', 6, now()),
('hpc1.curing.prod.detect.out','hpc1 CURING제품감지(out)', 6, now()),
('hpc1.curing.prod.info','hpc1 CURING기종정보', 6, now()),
('hpc1.curing.alm.cnt','CURING알람', 6, now()),
('hpc1.curing.top.cur.temp','hpc1 CURING상부현재온도', 6, now()),
('hpc1.curing.top.set.temp','hpc1 CURING상부설정온도', 6, now()),
('hpc1.curing.botm.cur.temp','hpc1 CURING하부현재온도', 6, now()),
('hpc1.curing.botm.set.temp','hpc1 CURING하부설정온도', 6, now())
;





/*FRONT BACK LOAD*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.frobackload.op.mode','hpc1 프론트백PCB로딩자동/수동모드', 7, now()),
('hpc1.frobackload.au.op','hpc1 프론트백PCB로딩자동운전', 7, now()),
('hpc1.frobackload.au.stop','hpc1 프론트백PCB로딩자동정지', 7, now()),
('hpc1.frobackload.emer.stop','hpc1 프론트백PCB로딩비상정지', 7, now()),
('hpc1.frobackload.au.op.step','hpc1 프론트백PCB로딩자동운전_STEP', 7, now()),
('hpc1.frobackload.lamp.g','hpc1 프론트백PCB로딩경광등(GREEN)', 7, now()),
('hpc1.frobackload.lamp.y','hpc1 프론트백PCB로딩경광등(YELLOW)', 7, now()),
('hpc1.frobackload.lamp.r','hpc1 프론트백PCB로딩경광등(RED)', 7, now()),
('hpc1.frobackload.alm','hpc1 프론트백PCB로딩알람', 7, now()),
('hpc1.frobackload.alm.cnt','hpc1 프론트백PCB로딩알람갯수', 7, now()),
('hpc1.frobackload.ct','hpc1 프론트백PCB로딩C/T', 7, now()),
('hpc1.frobackload.air.press','hpc1 프론트백PCB로딩공압상태', 7, now()),
('hpc1.frobackload.door1','hpc1 프론트백PCB로딩도어상태1', 7, now()),
('hpc1.frobackload.door2','hpc1 프론트백PCB로딩도어상태2', 7, now()),
('hpc1.frobackload.door3','hpc1 프론트백PCB로딩도어상태3', 7, now()),
('hpc1.frobackload.door4','hpc1 프론트백PCB로딩도어상태4', 7, now()),
('hpc1.frobackload.prod.info','hpc1 프론트백PCB로딩기종정보', 7, now())
;

/*Upper하우징로딩*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.uh.load.op.mode','U하우징로딩자동/수동모드', 8, now()),
('hpc1.uh.load.au.op','U하우징로딩자동운전', 8, now()),
('hpc1.uh.load.au.stop','U하우징로딩자동정지', 8, now()),
('hpc1.uh.load.emer.stop','U하우징로딩비상정지', 8, now()),
('hpc1.uh.load.au.op.step','U하우징로딩자동운전_STEP', 8, now()),
('hpc1.uh.load.lamp.g','U하우징로딩경광등(GREEN)', 8, now()),
('hpc1.uh.load.lamp.y','U하우징로딩경광등(YELLOW)', 8, now()),
('hpc1.uh.load.lamp.r','U하우징로딩경광등(RED)', 8, now()),
('hpc1.uh.load.door1','U하우징로딩도어상태1', 8, now()),
('hpc1.uh.load.door2','U하우징로딩도어상태2', 8, now()),
('hpc1.uh.load.door3','U하우징로딩도어상태3', 8, now()),
('hpc1.uh.load.door4','U하우징로딩도어상태4', 8, now()),
('hpc1.uh.load.door5','U하우징로딩도어상태5', 8, now()),
('hpc1.uh.load.door6','U하우징로딩도어상태6', 8, now()),
('hpc1.uh.load.prod.detect','U하우징로딩제품감지', 8, now()),
('hpc1.uh.load.prod.info','U하우징로딩기종정보', 8, now()),
('hpc1.uh.load.alm','U하우징로딩알람', 8, now()),
('hpc1.uh.load.alm.cnt','U하우징로딩알람갯수', 8, now()),
('hpc1.uh.load.ct','U하우징로딩C/T', 8, now()),
('hpc1.uh.load.air.press','U하우징로딩공압상태', 8, now())
;

/*TIM 도포*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.tim.op.mode','TIM도포자동/수동모드', 9, now()),
('hpc1.tim.au.op','TIM도포자동운전', 9, now()),
('hpc1.tim.au.stop','TIM도포자동정지', 9, now()),
('hpc1.tim.emer.stop','TIM도포비상정지', 9, now()),
('hpc1.tim.au.op.step','TIM도포자동운전STEP', 9, now()),
('hpc1.tim.vis.au.op.step','TIM비전자동운전STEP', 9, now()),
('hpc1.tim.scrw.au.op.step','TIM하우징결합자동운전STEP', 9, now()),
('hpc1.tim.alm.cnt','TIM도포알람갯수', 9, now()),
('hpc1.tim.lamp.g','TIM도포경광등(GREEN)', 9, now()),
('hpc1.tim.lamp.y','TIM도포경광등(YELLOW)', 9, now()),
('hpc1.tim.lamp.r','TIM도포경광등(RED)', 9, now()),
('hpc1.tim.door1','TIM도포도어상태1', 9, now()),
('hpc1.tim.door2','TIM도포도어상태2', 9, now()),
('hpc1.tim.door3','TIM도포도어상태3', 9, now()),
('hpc1.tim.door4','TIM도포도어상태4', 9, now()),
('hpc1.tim.door5','TIM도포도어상태5', 9, now()),
('hpc1.tim.door6','TIM도포도어상태6', 9, now()),
('hpc1.tim.tim.prod.detect','TIM도포제품감지', 9, now()),
('hpc1.tim.vis.prod.detect','TIM비전제품감지', 9, now()),
('hpc1.tim.scrw.prod.detect1','TIM하우징결합제품감지1', 9, now()),
('hpc1.tim.scrw.prod.detect2','TIM하우징결합제품감지2', 9, now()),
('hpc1.tim.prod.info','TIM도포기종정보', 9, now()),
('hpc1.tim.tim.alm','TIM도포알람', 9, now()),
('hpc1.tim.vis.alm','TIM비전알람', 9, now()),
('hpc1.tim.scrw.alm','TIM하우징결합알람', 9, now()),
('hpc1.tim.ct','TIM도포C/T', 9, now()),
('hpc1.tim.vis.ct','TIM비전C/T', 9, now()),
('hpc1.tim.scrw.ct','TIM하우징결합C/T', 9, now()),
('hpc1.tim.air.press','TIM도포공압상태', 9, now())
;


/*Lower하우징로딩*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.lh.load.op.mode','L하우징로딩자동/수동모드', 10, now()),
('hpc1.lh.load.au.op','L하우징로딩자동운전', 10, now()),
('hpc1.lh.load.au.stop','L하우징로딩자동정지', 10, now()),
('hpc1.lh.load.emer.stop','L하우징로딩비상정지', 10, now()),
('hpc1.lh.load.au.op.step','L하우징로딩자동운전_STEP', 10, now()),
('hpc1.lh.load.lamp.g','L하우징로딩경광등(GREEN)', 10, now()),
('hpc1.lh.load.lamp.y','L하우징로딩경광등(YELLOW)', 10, now()),
('hpc1.lh.load.lamp.r','L하우징로딩경광등(RED)', 10, now()),
('hpc1.lh.load.door1','L하우징로딩도어상태1', 10, now()),
('hpc1.lh.load.door2','L하우징로딩도어상태2', 10, now()),
('hpc1.lh.load.door3','L하우징로딩도어상태3', 10, now()),
('hpc1.lh.load.door4','L하우징로딩도어상태4', 10, now()),
('hpc1.lh.load.door5','L하우징로딩도어상태5', 10, now()),
('hpc1.lh.load.door6','L하우징로딩도어상태6', 10, now()),
('hpc1.lh.load.prod.detect','L하우징로딩제품감지', 10, now()),
('hpc1.lh.load.prod.info','L하우징로딩기종정보', 10, now()),
('hpc1.lh.load.alm','L하우징로딩알람', 10, now()),
('hpc1.lh.load.alm.cnt','L하우징로딩알람갯수', 10, now()),
('hpc1.lh.load.ct','L하우징로딩C/T', 10, now()),
('hpc1.lh.load.air.press','L하우징로딩공압상태', 10, now())
;


/*스크류체결*/
insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('hpc1.scrwt.op.mode','스크류체결자동/수동모드', 11, now()),
('hpc1.scrwt.au.op','스크류체결자동운전', 11, now()),
('hpc1.scrwt.au.stop','스크류체결자동정지', 11, now()),
('hpc1.scrwt.emer.stop','스크류체결비상정지', 11, now()),
('hpc1.scrwt.au.op.step','스크류체결자동운전STEP', 11, now()),
('hpc1.scrwt.hc.au.op.step','스크류체결높이체크자동운전STEP', 11, now()),
('hpc1.scrwt.lamp.g','스크류체결경광등(GREEN)', 11, now()),
('hpc1.scrwt.lamp.y','스크류체결경광등(YELLOW)', 11, now()),
('hpc1.scrwt.lamp.r','스크류체결경광등(RED)', 11, now()),
('hpc1.scrwt.door1','스크류체결도어상태1', 11, now()),
('hpc1.scrwt.door2','스크류체결도어상태2', 11, now()),
('hpc1.scrwt.door3','스크류체결도어상태3', 11, now()),
('hpc1.scrwt.door4','스크류체결도어상태4', 11, now()),
('hpc1.scrwt.door5','스크류체결도어상태5', 11, now()),
('hpc1.scrwt.prod.detect','스크류체결제품감지', 11, now()),
('hpc1.scrwt.prod.info','스크류체결기종정보', 11, now()),
('hpc1.scrwt.alm.cnt','스크류체결알람갯수', 11, now()),
('hpc1.scrwt.hc.alm.cnt','스크류체결높이체크알람갯수', 11, now()),
('hpc1.scrwt.ct','스크류체결C/T', 11, now()),
('hpc1.scrwt.hc.ct','스크류체결높이체크C/T', 11, now()),
('hpc1.scrwt.air.press','스크류체결공압상태', 11, now()),
('hpc1.scrwt.use.cnt','스크류체결사용COUNT', 11, now()),
('hpc1.scrwt.remain.cnt','스크류체결사용임박COUNT', 11, now()),
('hpc1.scrwt.usg.lim.cnt','스크류체결교체COUNT', 11, now())
;

/*팬클립조립*/
insert into tag (tag_code, tag_name, "Equipment_id", "_created")
values
('hpc1.fclip.op.mode','팬클립조립공통자동/수동모드', 12, now()),
('hpc1.fclip.au.op','팬클립조립공통자동운전', 12, now()),
('hpc1.fclip.au.stop','팬클립조립공통자동정지', 12, now()),
('hpc1.fclip.emer.stop','팬클립조립공통비상정지', 12, now()),
('hpc1.fclip.hfan.au.op.step','fc하우징팬결합자동운전STEP', 12, now()),
('hpc1.fclip.scrw.au.op.step','fc스크류체결자동운전STEP', 12, now()),
('hpc1.fclip.htck.au.op.step','fc높이체크자동운전STEP', 12, now()),
('hpc1.fclip.fwir.au.op.step','fc팬와이어자동운전STEP', 12, now()),
('hpc1.fclip.lamp.g','팬클립조립공통경광등(GREEN)', 12, now()),
('hpc1.fclip.lamp.y','팬클립조립공통경광등(YELLOW)', 12, now()),
('hpc1.fclip.lamp.r','팬클립조립공통경광등(RED)', 12, now()),
('hpc1.fclip.door1','팬클립조립공통도어상태1', 12, now()),
('hpc1.fclip.door2','팬클립조립공통도어상태2', 12, now()),
('hpc1.fclip.door3','팬클립조립공통도어상태3', 12, now()),
('hpc1.fclip.door4','팬클립조립공통도어상태4', 12, now()),
('hpc1.fclip.hfan.prod.detect','fc하우징팬결합제품감지', 12, now()),
('hpc1.fclip.scrw.prod.detect','fc스크류체결제품감지', 12, now()),
('hpc1.fclip.htck.prod.detect','fc높이체크제품감지', 12, now()),
('hpc1.fclip.fwir.prod.detect','fc팬와이어제품감지', 12, now()),
('hpc1.fclip.prod.info','팬클립조립공통기종정보', 12, now()),
('hpc1.fclip.hfan.alm','fc하우징팬결합알람', 12, now()),
('hpc1.fclip.scrw.alm','fc스크류체결알람', 12, now()),
('hpc1.fclip.hc.alm','fc높이체크알람', 12, now()),
('hpc1.fclip.fw.alm','fc팬와이어알람', 12, now()),
('hpc1.fclip.alm.cnt','fc팬클립조립공통알람갯수', 12, now()),
('hpc1.fclip.hfan.ct','하우징팬결합C/T', 12, now()),
('hpc1.fclip.scrw.ct','fc스크류체결C/T', 12, now()),
('hpc1.fclip.htck.ct','높이체크C/T', 12, now()),
('hpc1.fclip.fwir.ct','팬와이어C/T', 12, now()),
('hpc1.fclip.use.cnt','fc스크류체결사용COUNT', 12, now()),
('hpc1.fclip.remain.cnt','fc스크류체결사용임박COUNT', 12, now()),
('hpc1.fclip.usg.lim.cnt','fc스크류체결교체 COUNT', 12, now())
;


/*EOL*/ 
insert into tag (tag_code, tag_name, "Equipment_id", "_created")
values
('hpc1.eol.op.au','EOL자동모드', 13, now()),
('hpc1.eol.op.ma','EOL수동모드', 13, now()),
('hpc1.eol.op.mode','EOL자동/수동 모드', 13, now()),
('hpc1.eol.au.op','EOL자동운전', 13, now()),
('hpc1.eol.au.stop','EOL자동정지', 13, now()),
('hpc1.eol.emer.stop','EOL비상정지', 13, now()),
('hpc1.eol.au.op.step','EOL자동운전_STEP', 13, now()),
('hpc1.eol.lamp.g','EOL경광등(GREEN)', 13, now()),
('hpc1.eol.lamp.y','EOL경광등(YELLOW)', 13, now()),
('hpc1.eol.lamp.r','EOL경광등(RED)', 13, now()),
('hpc1.eol.door1','EOL도어상태1', 13, now()),
('hpc1.eol.door2','EOL도어상태2', 13, now()),
('hpc1.eol.door3','EOL도어상태3', 13, now()),
('hpc1.eol.door4','EOL도어상태4', 13, now()),
('hpc1.eol1.prod.detect','EOL1제품감지', 14, now()),
('hpc1.eol2.prod.detect','EOL2제품감지', 14, now()),
('hpc1.eol.prod.info','EOL기종정보', 13, now()),
('hpc1.eol1.jig.clamp','EOL#1 검사지그 클램프', 13, now()),
('hpc1.eol1.prob.md.fward','EOL#1 프로브 모델전진', 13, now()),
('hpc1.eol1.prob.fward','EOL#1 프로브 전진', 13, now()),
('hpc1.eol1.test.exec','EOL#1 테스트 실행', 13, now()),
('hpc1.eol1.prob.bward','EOL#1 프로브 후진', 13, now()),
('hpc1.eol1.prob.md.bward','EOL#1 프로브 모델후진', 13, now()),
('hpc1.eol1.unclamp','EOL#1 언클램프', 13, now()),
('hpc1.eol1.wk.finish','EOL#1 작업완료', 13, now()),
('hpc1.eol2.jig.clamp','EOL#2 검사지그 클램프', 14, now()),
('hpc1.eol2.prob.md.fward','EOL#2 프로브 모델전진', 14, now()),
('hpc1.eol2.prob.fward','EOL#2 프로브 전진', 14, now()),
('hpc1.eol2.test.exec','EOL#2 테스트 실행', 14, now()),
('hpc1.eol2.prob.bward','EOL#2 프로브 후진', 14, now()),
('hpc1.eol2.prob.md.bward','EOL#2 프로브 모델후진', 14, now()),
('hpc1.eol2.unclamp','EOL#2 언클램프', 14, now()),
('hpc1.eol2.wk.finish','EOL#2 작업완료', 14, now()),
('hpc1.eol.ct','EOL C/T', 13, now()),
('hpc1.eol.air.press','EOL공압상태', 13, now()),
('hpc1.eol1.perf.test','EOL성능검사(마스터샘플', 13, now()),
('hpc1.eol1.test.proo.cnt1','EOL테스트프루프개수1', 13, now()),
('hpc1.eol1.test.proo.cnt2','EOL테스트프루프개수2', 13, now()),
('hpc1.eol1.test.proo.cnt3','EOL테스트프루프개수3', 13, now()),
('hpc1.eol1.test.proo.cnt4','EOL테스트프루프개수4', 13, now()),
('hpc1.eol1.test.proo.cnt5','EOL테스트프루프개수5', 13, now()),
('hpc1.eol.alm.cnt','EOL알람여부', 13, now())
;

/*PINCHK*/
insert into tag (tag_code, tag_name, "Equipment_id", "_created")
values
('hpc1.pinchk.op.mode','핀체크라벨 자동/수동모드', 15, now()),
('hpc1.pinchk.au.op','핀체크라벨 자동운전', 15, now()),
('hpc1.pinchk.au.stop','핀체크라벨 자동정지', 15, now()),
('hpc1.pinchk.emer.stop','핀체크라벨 비상정지', 15, now()),
('hpc1.pinchk.op.auto','핀체크라벨 [라벨] 자동중', 15, now()),
('hpc1.pinchk.op.manual','핀체크라벨 [라벨] 수동중', 15, now()),
('hpc1.pinchk.au.op.step','핀체크라벨 자동운전_STEP', 15, now()),
('hpc1.pinchk.lamp.g','핀체크라벨 경광등(GREEN)', 15, now()),
('hpc1.pinchk.lamp.y','핀체크라벨 경광등(YELLOW)', 15, now()),
('hpc1.pinchk.lamp.r','핀체크라벨 경광등(RED)', 15, now()),
('hpc1.pinchk.air.press','핀체크라벨 공압상태', 15, now()),
('hpc1.pinchk.door1','핀체크라벨 도어상태1', 15, now()),
('hpc1.pinchk.door2','핀체크라벨 도어상태2', 15, now()),
('hpc1.pinchk.door3','핀체크라벨 도어상태3', 15, now()),
('hpc1.pinchk.door4','핀체크라벨 도어상태4', 15, now()),
('hpc1.pinchk.prod.detect','핀체크라벨 제품감지', 15, now()),
('hpc1.pinchk.prod.info','핀체크라벨 기종정보', 15, now()),
('hpc1.pinchk.ct','핀체크라벨 C/T', 15, now()),
('hpc1.pinchk.alm.cnt','핀체크라벨알람여부', 15, now())
;

/*brackassm*/
insert into tag (tag_code, tag_name, "Equipment_id", "_created")
values
('hpc1.brackassm.op.mode','브라켓조립자동/수동모드', 16, now()),
('hpc1.brackassm.au.op','브라켓조립자동운전', 16, now()),
('hpc1.brackassm.au.stop','브라켓조립자동정지', 16, now()),
('hpc1.brackassm.emer.stop','브라켓조립비상정지', 16, now()),
('hpc1.brackassm.scrw.au.op.step','브라켓스크류자동운전_STEP', 16, now()),
('hpc1.brackassm.hck.au.op.step','브라켓높이체크자동운전_STEP', 16, now()),
('hpc1.brackassm.lamp.g','브라켓조립경광등(GREEN)', 16, now()),
('hpc1.brackassm.lamp.y','브라켓조립경광등(YELLOW)', 16, now()),
('hpc1.brackassm.lamp.r','브라켓조립경광등(RED)', 16, now()),
('hpc1.brackassm.air.press','브라켓조립공압상태', 16, now()),
('hpc1.brackassm.door1','브라켓스크류도어상태1', 16, now()),
('hpc1.brackassm.door2','브라켓스크류도어상태2', 16, now()),
('hpc1.brackassm.scrw.prod.detect','브라켓스크류제품감지', 16, now()),
('hpc1.brackassm.hck.prod.detect','브라켓높이체크제품감지', 16, now()),
('hpc1.brackassm.prod.info','브라켓조립기종정보', 16, now()),
('hpc1.brackassm.scrw.alm','브라켓스크류알람', 16, now()),
('hpc1.brackassm.hc.alm','브라켓높이체크알람', 16, now()),
('hpc1.brackassm.alm.cnt','브라켓조립알람갯수', 16, now()),
('hpc1.brackassm.scrw.ct','브라켓스크류 C/T', 16, now()),
('hpc1.brackassm.hc.ct','브라켓높이체크 C/T', 16, now())
;


/**********************************************************************/

insert into tag(tag_code, tag_name,"Equipment_id", "_created") 
values 
('smt4.load.au.md','smt4로더자동모드', 17, now()),
('smt4.load.ma.md','smt4로더수동모드', 17, now()),
('smt4.load.au.op.step','smt4로더자동운전_STEP', 17, now()),
('smt4.load.lamp.g','smt4로더경광등(GREEN)', 17, now()),
('smt4.load.lamp.y','smt4로더경광등(YELLOW)', 17, now()),
('smt4.load.lamp.r','smt4로더경광등(RED)', 17, now()),
('smt4.load.pitch','smt4워크피치', 17, now()),
('smt4.load.pitch.first','smt4 first pitch', 17, now()),
('smt4.load.pcb.pan.cnt','smt4로더PCB패널개수', 17, now()),
('smt4.load.alm.cnt','smt4로더알람여부', 17, now())
;

insert into tag(tag_code, tag_name,"Equipment_id", "_created")
values
('smt4.unload.au.md','smt4언로더자동모드', 18, now()),
('smt4.unload.ma.md','smt4언로더수동모드', 18, now()),
('smt4.unload.lamp.g','smt4언로더경광등(GREEN)', 18, now()),
('smt4.unload.lamp.y','smt4언로더경광등(YELLOW)', 18, now()),
('smt4.unload.lamp.r','smt4언로더경광등(RED)', 18, now()),
('smt4.unload.door','smt4언로더도어상태', 18, now()),
('smt4.unload.prod.detect','smt4언로더제품감지', 18, now()),
('smt4.unload.pitch.first','smt4언로더 FIRST PITCH', 18, now()),
('smt4.unload.pitch','smt4언로더PITCH', 18, now()),
('smt4.unload.pcb.pan.cnt','smt4언로더PCB패널개수', 18, now()),
('smt4.unload.alm.cnt','sm43언로더 알람여부', 18, now())
;
