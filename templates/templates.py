import jinja2

# WAREHOUSE
warehouse_template_tf = jinja2.Template(
"""

resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "{{name}}"
  warehouse_size    =   "{{warehouse_size}}"
  auto_resume       =   {{auto_resume}}
  auto_suspend      =   {{auto_suspend}}
  comment           =   "{{comment}}"
}

""")

warehouse_template_sql = jinja2.Template(
"""

CREATE OR REPLACE WAREHOUSE IF NOT EXISTS {{name}}
WITH
  WAREHOUSE_SIZE = '{{warehouse_size}}'
  AUTO_SUSPEND = {{auto_suspend}}
  AUTO_RESUME = {{auto_resume}}
  COMMENT = '{{comment}}';

""")

# DATABASES

database_template_tf = jinja2.Template(
"""

resource "snowflake_database" "{{name}}" {
  name                        = "{{name}}"
  comment                     = "{{comment}}"
}

"""
)


database_template_sql = jinja2.Template(
"""

CREATE DATABASE IF NOT EXISTS {{name}}
 COMMENT = '{{comment}}';

""")

# ROLES

role_template_tf = jinja2.Template("""      
      
locals {
  roles = {
   {{role_blob}}
  }
}

resource "snowflake_role" "role" {
  for_each = local.roles
  name     = each.key
  comment  = each.value.comment
}

resource "snowflake_role_grants" "role_grant" {
  for_each  = local.roles
  role_name = each.key
  users     = each.value.users
  roles     = []
}

""")

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

""")

# SCHEMAS

schema_template_tf = jinja2.Template(
"""

locals {
  schemas = {
    {{schema_blob}}
  }
}
resource "snowflake_schema" "schema" {
  for_each = local.schemas
  name     = each.key
  database = each.value.database
  comment  = each.value.comment
}

resource "snowflake_schema_grant" "schema_grant_usage" {
  for_each      = local.schemas
  schema_name   = each.key
  database_name = each.value.database
  privilege     = "USAGE"
  roles         = each.value.usage_roles
  shares        = []
}

resource "snowflake_schema_grant" "schema_grant_all" {
  for_each      = local.schemas
  schema_name   = each.key
  database_name = each.value.database
  privilege     = "ALL"
  roles         = each.value.all_roles
  shares        = []
}

""")

schema_insert_template_tf = jinja2.Template(
"""

"{{schema}}" = {
      database = "{{database}}"
      comment = "{{comment}}"
      usage_roles = {{usage_roles}}
      all_roles = {{all_roles}}
    }

"""
)

schema_template_sql = jinja2.Template(
"""

CREATE SCHEMA IF NOT EXISTS {{database}}.{{name}}
COMMENT = '{{comment}}';

""")

user_template_tf = jinja2.Template(
"""

locals {
  users = {
    {{user_blob}}
  }
}

resource "snowflake_user" "user" {
  for_each             = local.users
  name                 = each.key
  login_name           = each.value.login_name
  default_role         = each.value.role
  default_namespace    = each.value.namespace
  default_warehouse    = each.value.warehouse
  must_change_password = true
  default_password     = each.value.login_name
}

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

main_template_tf = jinja2.Template(
"""

provider "snowflake" {
  account = "{{acct}}"
  region  = "{{region}}"
  role  = "ACCOUNTADMIN"
}

""")

user_insert_template_tf = jinja2.Template(
"""

"{{name}}" = {
  login_name = "{{name}}"
  role       = "{{role}}"
  namespace  = "{{namespace}}"
  warehouse  = "{{warehouse}}"
}

"""
)
