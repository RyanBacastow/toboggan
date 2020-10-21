
            locals {
              schemas = {
                
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
            