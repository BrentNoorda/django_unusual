-- because we want the colortemp id field to rollover, these commands will make sure
-- it rolls over after 2 billion, which isn't a problem because the field is purged frequently
-- by demos/ColorTemp_GC.py anyway. we also initialize very close to the rollover point just to make sure
-- it works
ALTER SEQUENCE django_unusual_colortemp_id_seq MINVALUE 1 MAXVALUE 2000000000 START 1999999990 RESTART 1 CYCLE;
SELECT setval('django_unusual_colortemp_id_seq',1999999990);

-- by default postgresql databases contain time-zones; I hate that --
ALTER TABLE django_unusual_colortemp ALTER COLUMN "created" TYPE timestamp without time zone;
