CREATE TABLE public.dummy_date (
	data_date date NOT NULL,
	data_ymd varchar(10) NULL,
	data_year int4,
	data_month int2,
	data_day int2,
	yw_year int4,	-- 연주차 기준 연도
	yw_week int2,	-- 연 기준 주차
	mw_month int2,		-- 월주차 기준 월
	month_week int2,	-- 월 기준 주차
	week_day int2,	-- 요일. (월1...토6,일0)
	holiday_yn varchar(1),
	CONSTRAINT dummy_date_pkey PRIMARY KEY (data_date),
	CONSTRAINT dummy_date_uniq01 unique  (data_ymd),
	CONSTRAINT dummy_date_uniq02 UNIQUE (data_year, data_month, data_day)
);

CREATE INDEX dummy_date_index01 ON public.dummy_date USING btree (yw_year, yw_week);
CREATE INDEX dummy_date_index02 ON public.dummy_date USING btree (yw_year, mw_month, month_week);

insert into dummy_date(data_date)
select generate_series( '2000-01-01'::date , '2100-12-31'::date, '1 day'::interval)::date as data_date
;

update dummy_date
set data_ymd = to_char(data_date, 'yyyy-mm-dd')
, data_year =  to_char(data_date, 'yyyy')::integer
, data_month = to_char(data_date, 'mm')::integer
, data_day = to_char(data_date, 'dd')::integer
, week_day = extract (dow from data_date)
, yw_week = extract (week from data_date)
;

update dummy_date 
set yw_year = data_year;

-- 12월 데이터 중 주 기준으로 다음해 데이터 처리
update dummy_date 
set yw_year = data_year + 1
where data_month = 12
and yw_week = 1
;

-- 1월 데이터 중 주 기준으로 이전해 데이터 처리
update dummy_date 
set yw_year = data_year - 1
where data_month = 1
and yw_week >= 50
;

update dummy_date 
set mw_month = data_month
;

-- 목요일에 대해서 월 기준 주차수 지정 
with A as 
(
select data_year, data_month, data_date, row_number() over (partition by data_year, data_month order by data_date) as month_week
from dummy_date 
where 1 = 1
--and data_year = 2021 
--and data_month = 1
and week_day = 4
group by data_year, data_month, data_date
)
update dummy_date dd
set month_week = A.month_week
from A 
where A.data_date = dd.data_date
;

-- 목요일 기준으로 월요일부터 일요일까지 동일 주로 설정 
with A as (
select week_day, month_week, data_date, data_date - interval '3 days' as monday, data_date + interval '3 days' as sunday
from dummy_date
where month_week > 0
order by data_date
)
update dummy_date dd
set month_week = A.month_week
from A 
where dd.data_date between A.monday and A.sunday
and dd.month_week is null
;

-- 다음 달로 처리할 데이터 
update dummy_date
set mw_month = case when data_month = 12 then 1 else data_month + 1 end
where month_week = 1
and data_day >  20
;

-- 이전 달로 처리할 데이터 
update dummy_date
set mw_month = case when data_month = 1 then 12 else data_month - 1 end 
where month_week >= 4
and data_day <  15
;

-- 토요일, 일요일을 휴일로 
update dummy_date 
set holiday_yn = 'Y'
where week_day in (6, 0)
;

-- 공휴일을 휴일로 
update dummy_date 
set holiday_yn = 'Y'
where data_month = 1 
and data_day = 1
;

update dummy_date 
set holiday_yn = 'Y'
where data_month = 3
and data_day = 1
;

update dummy_date 
set holiday_yn = 'Y'
where data_month = 5
and data_day = 5
;
update dummy_date 
set holiday_yn = 'Y'
where data_month = 6
and data_day = 6
;

update dummy_date 
set holiday_yn = 'Y'
where data_month = 8
and data_day = 15
;

update dummy_date 
set holiday_yn = 'Y'
where data_month = 10
and data_day = 3
;

update dummy_date 
set holiday_yn = 'Y'
where data_month = 10
and data_day = 9
;

update dummy_date 
set holiday_yn = 'Y'
where data_month = 12
and data_day = 25
;