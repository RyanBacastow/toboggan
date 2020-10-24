

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



CREATE DATABASE IF NOT EXISTS DEV_DB
 COMMENT = 'This database is for dev schemas and uses dev wh workflow.';


CREATE DATABASE IF NOT EXISTS QA_DB
 COMMENT = 'This database is for qa schemas and uses qa wh workflow.';


CREATE DATABASE IF NOT EXISTS STG_DB
 COMMENT = 'This database is for stg schemas and uses stg wh workflow.';


CREATE DATABASE IF NOT EXISTS PROD_DB
 COMMENT = 'This database is for prod schemas and uses prod wh workflow.';


CREATE DATABASE IF NOT EXISTS ANALYTICS_DB
 COMMENT = 'This database is for analytics, sandbox, view, and other schemas and uses analytical wh workflow.';



CREATE ROLE IF NOT EXISTS DEV_ROLE
COMMENT = 'Accessible to PUBLIC, default to devs and all users. Access to DEV_WH and DEV_DB objects.';


CREATE ROLE IF NOT EXISTS QA_ROLE
COMMENT = 'For QA access, QA_WH warehouse and QA_DB object access.';


CREATE ROLE IF NOT EXISTS STG_ROLE
COMMENT = 'For STG access, can be given and revoked as needed to devs or qas. Medium instance wh, access to STG_DB objects.';


CREATE ROLE IF NOT EXISTS PROD_ROLE
COMMENT = 'Production role is for prod ETL flows only. Granted to streams and tasks, PROD_DB, and using PROD_WH Large Instance.';


CREATE ROLE IF NOT EXISTS ANALYTICS_ROLE
COMMENT = 'This is a role for tableau and/or analysts, large instance type, access to various layers.';


CREATE ROLE IF NOT EXISTS TMO_ROLE
COMMENT = 'This role is for sharing and interfacing with the TMO External Snowflake acct.';



CREATE SCHEMA IF NOT EXISTS DEV_DB.RAW_LAYER
COMMENT = 'The raw layer represents data populated directly from the datalake either from snowpipe or external tables. Columns include a variant type and a metadata filename column.';


CREATE SCHEMA IF NOT EXISTS QA_DB.RAW_LAYER
COMMENT = 'The raw layer represents data populated directly from the datalake either from snowpipe or external tables. Columns include a variant type and a metadata filename column.';


CREATE SCHEMA IF NOT EXISTS STG_DB.RAW_LAYER
COMMENT = 'The raw layer represents data populated directly from the datalake either from snowpipe or external tables. Columns include a variant type and a metadata filename column.';


CREATE SCHEMA IF NOT EXISTS PROD_DB.RAW_LAYER
COMMENT = 'The raw layer represents data populated directly from the datalake either from snowpipe or external tables. Columns include a variant type and a metadata filename column.';


CREATE SCHEMA IF NOT EXISTS DEV_DB.REFINED_LAYER
COMMENT = 'The refined layer holds defined schemas (defined by ddls made by devs) and is populated from transformations done on raw data from RAW_LAYER. Feeds downstream analytics, views, and other objects accessible to users.';


CREATE SCHEMA IF NOT EXISTS QA_DB.REFINED_LAYER
COMMENT = 'The refined layer holds defined schemas (defined by ddls made by devs) and is populated from transformations done on raw data from RAW_LAYER. Feeds downstream analytics, views, and other objects accessible to users.';


CREATE SCHEMA IF NOT EXISTS STG_DB.REFINED_LAYER
COMMENT = 'The refined layer holds defined schemas (defined by ddls made by devs) and is populated from transformations done on raw data from RAW_LAYER. Feeds downstream analytics, views, and other objects accessible to users.';


CREATE SCHEMA IF NOT EXISTS PROD_DB.REFINED_LAYER
COMMENT = 'The refined layer holds defined schemas (defined by ddls made by devs) and is populated from transformations done on raw data from RAW_LAYER. Feeds downstream analytics, views, and other objects accessible to users.';


CREATE SCHEMA IF NOT EXISTS DEV_DB.ANALYTICS_LAYER
COMMENT = 'This layer can be used to create views and a variety of tables needed for downstream processes such as tableau or ad hoc reporting.';


CREATE SCHEMA IF NOT EXISTS QA_DB.ANALYTICS_LAYER
COMMENT = 'This layer can be used to create views and a variety of tables needed for downstream processes such as tableau or ad hoc reporting.';


CREATE SCHEMA IF NOT EXISTS STG_DB.ANALYTICS_LAYER
COMMENT = 'This layer can be used to create views and a variety of tables needed for downstream processes such as tableau or ad hoc reporting.';


CREATE SCHEMA IF NOT EXISTS PROD_DB.ANALYTICS_LAYER
COMMENT = 'This layer can be used to create views and a variety of tables needed for downstream processes such as tableau or ad hoc reporting.';



CREATE USER IF NOT EXISTS DEV_USER
  PASSWORD = 'DEV_USER'
  DISPLAY_NAME = 'DEV_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = DEV_WH
  DEFAULT_NAMESPACE = DEV_DB.RAW_LAYER
  DEFAULT_ROLE = DEV_ROLE;


CREATE USER IF NOT EXISTS QA_USER
  PASSWORD = 'QA_USER'
  DISPLAY_NAME = 'QA_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = QA_WH
  DEFAULT_NAMESPACE = QA_DB.RAW_LAYER
  DEFAULT_ROLE = QA_ROLE;


CREATE USER IF NOT EXISTS STG_USER
  PASSWORD = 'STG_USER'
  DISPLAY_NAME = 'STG_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = STG_WH
  DEFAULT_NAMESPACE = STG_DB.RAW_LAYER
  DEFAULT_ROLE = STG_ROLE;


CREATE USER IF NOT EXISTS PROD_USER
  PASSWORD = 'PROD_USER'
  DISPLAY_NAME = 'PROD_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = PROD_WH
  DEFAULT_NAMESPACE = PROD_DB.RAW_LAYER
  DEFAULT_ROLE = PROD_ROLE;


CREATE USER IF NOT EXISTS ANALYTICS_USER
  PASSWORD = 'ANALYTICS_USER'
  DISPLAY_NAME = 'ANALYTICS_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = ANALYTICS_WH
  DEFAULT_NAMESPACE = PROD_DB.REFINED_LAYER
  DEFAULT_ROLE = ANALYTICS_ROLE;


CREATE USER IF NOT EXISTS TABLEAU_USER
  PASSWORD = 'TABLEAU_USER'
  DISPLAY_NAME = 'TABLEAU_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = ANALYTICS_WH
  DEFAULT_NAMESPACE = PROD_DB.REFINED_LAYER
  DEFAULT_ROLE = ANALYTICS_ROLE;


CREATE USER IF NOT EXISTS TMO_USER
  PASSWORD = 'TMO_USER'
  DISPLAY_NAME = 'TMO_USER'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = TMO_WH
  DEFAULT_NAMESPACE = PROD_DB.REFINED_LAYER
  DEFAULT_ROLE = TMO_ROLE;

