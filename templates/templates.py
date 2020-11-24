import jinja2

# WAREHOUSES

warehouse_template_sql = jinja2.Template(
"""

CREATE WAREHOUSE IF NOT EXISTS {{name}}
WITH
  WAREHOUSE_SIZE = '{{warehouse_size}}'
  AUTO_SUSPEND = {{auto_suspend}}
  AUTO_RESUME = {{auto_resume}}
  COMMENT = '{{comment}}';

""")

# DATABASES

database_template_sql = jinja2.Template(
"""

CREATE DATABASE IF NOT EXISTS {{name}}
 COMMENT = '{{comment}}';

""")

# ROLES

role_insert_template_tf = jinja2.Template("""

"{{role}}" = {
  comment = "{{comment}}"
  users = {{users}}
}

""")

role_template_sql = jinja2.Template(
"""

CREATE ROLE IF NOT EXISTS {{name}}
COMMENT = '{{comment}}';

GRANT ROLE {{name}} TO ROLE SYSADMIN;

""")

# SCHEMAS

schema_template_sql = jinja2.Template(
"""

CREATE SCHEMA IF NOT EXISTS {{database}}.{{name}}
COMMENT = '{{comment}}';

""")

user_template_sql = jinja2.Template("""

CREATE USER IF NOT EXISTS {{name}}
  PASSWORD = '{{name}}'
  DISPLAY_NAME = '{{name}}'
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_WAREHOUSE = {{warehouse}}
  DEFAULT_NAMESPACE = {{namespace}}
  DEFAULT_ROLE = {{default_role}};

""")

table_template_sql = jinja2.Template(
"""

CREATE TABLE IF NOT EXISTS {{namespace}}.{{name}} ({{table_blob}});

"""
)

table_insert_template_sql = jinja2.Template(
"""
{{column_name}} {{column_type}},
"""
)

teardown_template_sql = jinja2.Template(
"""
DROP {{object_type}} IF EXISTS {{name}};
"""
)

aws_storage_integration_template = jinja2.Template(
"""
CREATE STORAGE INTEGRATION IF NOT EXISTS {{name}}
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = {{enabled}}
  STORAGE_AWS_ROLE_ARN = '{{integration_str}}'
  STORAGE_ALLOWED_LOCATIONS = {{storage_allowed_locations_str}}
  {%- if comment %}
  COMMENT = '{{comment}}'
  {%- endif -%}
  {% if storage_blocked_locations_str %}
  STORAGE_BLOCKED_LOCATIONS = {{storage_blocked_locations_str}}
  {%- endif -%}

"""
)

external_stage_template = jinja2.Template(
"""
CREATE stage IF NOT EXISTS {{namespace}}.{{name}}
 storage_integration = {{integration}}
 url='{{url}}'
 file_format = (TYPE = {{file_format}});

""")

pipe_template_sql = jinja2.Template(
"""
create pipe IF NOT EXISTS {{namespace}}.{{name}} auto_ingest={{auto_ingest}} as
 copy into {{full_namespace}} {{column_str}}
 from (
   {{query}} FROM @{{namespace}}.{{stage}})
 file_format = (type = '{{file_format}}');
""")

external_table_template_sql = jinja2.Template(
"""
create or replace external table {{namespace}}.{{name}}
  with location = @{{namespace}}.{{stage}}/
  auto_refresh = {{auto_refresh}}
  file_format = (type = '{{file_format}}');
"""
)

stream_template_sql = jinja2.Template(
"""
CREATE STREAM IF NOT EXISTS {{namespace}}.{{name}} on table {{full_namespace}} APPEND_ONLY={{append_only}};
"""
)

task_template_sql = jinja2.Template(
"""
CREATE TASK {{namespace}}.{{name}}
    WAREHOUSE  = {{warehouse_name}}
    COMMENT = '{{comment}}'
    SCHEDULE = '{{schedule}}'
  WHEN
    SYSTEM$STREAM_HAS_DATA('{{namespace}}.{{stream}}')
  AS INSERT INTO {{full_namespace}}
    {{select_statement}};

ALTER TASK IF EXISTS {{namespace}}.{{name}} RESUME;

"""
)