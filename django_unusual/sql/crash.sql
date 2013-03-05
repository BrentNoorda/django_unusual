-- by default postgresql databases contain time-zones; I hate that --
ALTER TABLE django_unusual_crash ALTER COLUMN "first" TYPE timestamp without time zone;
ALTER TABLE django_unusual_crash ALTER COLUMN "last" TYPE timestamp without time zone;
