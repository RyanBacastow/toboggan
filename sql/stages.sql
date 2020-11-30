
CREATE stage IF NOT EXISTS TEST_DB.TEST_SCHEMA.TEST_STAGE
 storage_integration = TEST_INT
 url='s3://bucket/dir/subdir'
 file_format = (TYPE = PARQUET);
