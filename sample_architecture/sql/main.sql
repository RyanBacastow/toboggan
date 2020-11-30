USE ROLE ACCOUNTADMIN;


CREATE ROLE IF NOT EXISTS TEST_ROLE
COMMENT = 'test';

GRANT ROLE TEST_ROLE TO ROLE SYSADMIN;

USE ROLE SYSADMIN;


CREATE WAREHOUSE IF NOT EXISTS TEST_WH
WITH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'test';

USE ROLE SYSADMIN;


CREATE DATABASE IF NOT EXISTS TEST_DB
 COMMENT = 'test';

USE ROLE SYSADMIN;


CREATE SCHEMA IF NOT EXISTS TEST_DB.TEST_SCHEMA
COMMENT = 'test';

USE ROLE ACCOUNTADMIN;


CREATE USER IF NOT EXISTS TEST_USER
  PASSWORD = 'TEST_USER'
  DISPLAY_NAME = 'TEST_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = TEST_WH
  DEFAULT_NAMESPACE = TEST_DB.TEST_SCHEMA
  DEFAULT_ROLE = TEST_ROLE;

USE ROLE SYSADMIN;
GRANT USAGE ON DATABASE TEST_DB TO ROLE TEST_ROLE;

GRANT ALL ON SCHEMA TEST_DB.TEST_SCHEMA TO ROLE TEST_ROLE;

USE ROLE SECURITYADMIN;
GRANT ALL ON FUTURE TABLES IN SCHEMA TEST_DB.TEST_SCHEMA TO ROLE TEST_ROLE;

USE ROLE SYSADMIN;


CREATE TABLE IF NOT EXISTS TEST_DB.TEST_SCHEMA.TEST_TABLE (
TEST_COLUMN NUMBER);


USE ROLE ACCOUNTADMIN;

CREATE STORAGE INTEGRATION IF NOT EXISTS TEST_INT
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::1234567891:role/test'
  STORAGE_ALLOWED_LOCATIONS = ('*')
  COMMENT = 'test'
USE ROLE SYSADMIN;

CREATE stage IF NOT EXISTS TEST_DB.TEST_SCHEMA.TEST_STAGE
 storage_integration = TEST_INT
 url='s3://bucket/dir/subdir'
 file_format = (TYPE = PARQUET);

USE ROLE SYSADMIN;

create pipe IF NOT EXISTS TEST_DB.TEST_SCHEMA.TEST_PIPE auto_ingest=TRUE as
 copy into TEST_DB.TEST_SCHEMA.TEST_TABLE (TEST_COLUMN)
 from (
   SELECT * FROM @TEST_DB.TEST_SCHEMA.TEST_STAGE)
 file_format = (type = 'PARQUET');
USE ROLE SYSADMIN;

create or replace external table TEST_DB.TEST_SCHEMA.
  with location = @TEST_DB.TEST_SCHEMA.TEST_STAGE/
  auto_refresh = TRUE
  file_format = (type = 'PARQUET');
USE ROLE SYSADMIN;

CREATE STREAM IF NOT EXISTS TEST_DB.TEST_SCHEMA.TEST_STREAM on table TEST_DB.TEST_SCHEMA.TEST_TABLE APPEND_ONLY=FALSE;
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
