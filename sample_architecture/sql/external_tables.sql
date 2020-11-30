USE ROLE SYSADMIN;

create or replace external table TEST_DB.TEST_SCHEMA.
  with location = @TEST_DB.TEST_SCHEMA.TEST_STAGE/
  auto_refresh = TRUE
  file_format = (type = 'PARQUET');