      
      
locals {
  roles = {
   

"TEST_ROLE" = {
  comment = "testing role"
  users = ["TEST_USER"]
}

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
