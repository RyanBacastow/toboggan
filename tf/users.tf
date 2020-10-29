

locals {
  users = {
    

"TEST_USER" = {
  login_name = "TEST_USER"
  role       = "TEST_ROLE"
  namespace  = "TEST_DB.TEST_SCHEMA"
  warehouse  = "TEST_WH"
}


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
