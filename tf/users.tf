
                locals {
                  users = {
                    
                  }
                }

                resource "snowflake_user" "user" {
                  for_each             = local.users
                  name                 = each.key
                  login_name           = each.value.login_name
                  default_role         = each.value.role
                  default_namespace    = each.value.namespace
                  default_warehouse    = each.value.warehouse
                  must_change_password = false
                }
                