

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
