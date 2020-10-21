

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