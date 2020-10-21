            
            locals {
              roles = {
               
                                                "PUBLIC" = {
                                                  comment = "Pseudo-role that is automatically granted to every user and every role in your account. The PUBLIC role can own securable objects, just like any other role; however, the objects owned by the role are, by definition, available to every other user and role in your account.This role is typically used in cases where explicit access control is not needed and all users are viewed as equal with regard to their access rights."
                                                  users = 
                                                }
                                                
                                                "ACCOUNTADMIN" = {
                                                  comment = "Role that encapsulates the SYSADMIN and SECURITYADMIN system-defined roles. It is the top-level role in the system and should be granted only to a limited/controlled number of users in your account."
                                                  users = 
                                                }
                                                
                                                "SECURITYADMIN" = {
                                                  comment = "Role that can manage any object grant globally, as well as create, monitor, and manage users and roles. More specifically, this role is granted the MANAGE GRANTS security privilege to be able to modify any grant, including revoking it. Inherits the privileges of the USERADMIN role via the system role hierarchy (e.g. USERADMIN role is granted to SECURITYADMIN)."
                                                  users = 
                                                }
                                                
                                                "USERADMIN" = {
                                                  comment = "Role that is dedicated to user and role management only. More specifically, this role is granted the CREATE USER and CREATE ROLE security privileges. Can create and manage users and roles in the account (assuming that ownership of those roles or users has not been transferred to another role)."
                                                  users = 
                                                }
                                                
                                                "SYSADMIN" = {
                                                  comment = "Role that has privileges to create warehouses and databases (and other objects) in an account. If, as recommended, you create a role hierarchy that ultimately assigns all custom roles to the SYSADMIN role, this role also has the ability to grant privileges on warehouses, databases, and other objects to other roles."
                                                  users = 
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
            