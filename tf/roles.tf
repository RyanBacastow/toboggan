      
      
locals {
  roles = {
   

"DEV_ROLE" = {
  comment = "Accessible to PUBLIC, default to devs and all users. Access to DEV_WH and DEV_DB objects."
  users = ["DEV_USER"]
}


"QA_ROLE" = {
  comment = "For QA access, QA_WH warehouse and QA_DB object access."
  users = ["QA_USER"]
}


"STG_ROLE" = {
  comment = "For STG access, can be given and revoked as needed to devs or qas. Medium instance wh, access to STG_DB objects."
  users = ["STG_USER"]
}


"PROD_ROLE" = {
  comment = "Production role is for prod ETL flows only. Granted to streams and tasks, PROD_DB, and using PROD_WH Large Instance."
  users = ["PROD_USER", "TABLEAU_USER"]
}


"ANALYTICS_ROLE" = {
  comment = "This is a role for tableau and/or analysts, large instance type, access to various layers."
  users = ["ANALYTICS_USER", "TABLEAU_USER"]
}


"TMO_ROLE" = {
  comment = "This role is for sharing and interfacing with the TMO External Snowflake acct."
  users = ["TMO_USER"]
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
