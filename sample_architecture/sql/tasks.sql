USE ROLE SYSADMIN;

CREATE TASK TEST_DB.TEST_SCHEMA.TEST_TASK
    WAREHOUSE  = TEST_WH
    COMMENT = 'testing'
    SCHEDULE = '5 MINUTES'
  WHEN
    SYSTEM$STREAM_HAS_DATA('TEST_DB.TEST_SCHEMA.TEST_STREAM')
  AS INSERT INTO TEST_DB.TEST_SCHEMA.TEST_TABLE
    SELECT *;

ALTER TASK IF EXISTS TEST_DB.TEST_SCHEMA.TEST_TASK RESUME;
