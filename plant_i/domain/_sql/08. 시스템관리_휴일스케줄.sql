-- public.holiday_custom definition

-- Drop table

-- DROP TABLE public.holiday_custom;

CREATE TABLE public.holiday_custom (
	nation_cd varchar(10) NOT NULL,
	type_val varchar(1) DEFAULT 'C'::character varying NULL,
	name_val varchar(100) NOT NULL,
	repeat_yn bpchar(1) DEFAULT 'N'::bpchar NOT NULL,
	holidate varchar(10) NULL,
	id serial4 NOT NULL,
	CONSTRAINT holiday_custom_unique null
);

