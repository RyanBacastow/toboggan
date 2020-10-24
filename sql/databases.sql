

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
