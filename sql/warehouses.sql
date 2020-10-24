CREATE OR REPLACE WAREHOUSE IF NOT EXISTS DEV_WH
WITH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'This database is for developers and public role access. General scheduled and adhoc work, not for large workloads or views.';


CREATE OR REPLACE WAREHOUSE IF NOT EXISTS QA_WH
WITH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'This database is for QA workflows and QA resources to query. Can be used in a variety of ways, but may not be good for largest analytical workflows.';


CREATE OR REPLACE WAREHOUSE IF NOT EXISTS STG_WH
WITH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'This warehouse is for use with the staging database. Medium instance, various workflows allowed.';


CREATE OR REPLACE WAREHOUSE IF NOT EXISTS PROD_WH
WITH
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'Production warehouse for ETL workflows and large query workloads.';


CREATE OR REPLACE WAREHOUSE IF NOT EXISTS ANALYTICS_WH
WITH
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'Analytics Warehouse for ad-hoc and tableau query needs';


CREATE OR REPLACE WAREHOUSE IF NOT EXISTS TMO_WH
WITH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'This is a warehouse for TMO read, write, and share workflows into TMO external snowflake acct.';


CREATE OR REPLACE WAREHOUSE IF NOT EXISTS TEST_WH
WITH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = true
  COMMENT = 'Delete me';
