USE ROLE SYSADMIN;

CREATE STREAM IF NOT EXISTS TEST_DB.TEST_SCHEMA.TEST_STREAM on table TEST_DB.TEST_SCHEMA.TEST_TABLE APPEND_ONLY=FALSE;