
                locals {
                  users = {
                    
                                                "DEV_USER" = {
                                                          login_name = "DEV_USER"
                                                          role       = "DEV_ROLE"
                                                          namespace  = "DEV_DB.RAW_LAYER"
                                                          warehouse  = "DEV_WH"
                                                        }
                                              

                                                "QA_USER" = {
                                                          login_name = "QA_USER"
                                                          role       = "QA_ROLE"
                                                          namespace  = "QA_DB.REFINED_LAYER"
                                                          warehouse  = "QA_WH"
                                                        }
                                              

                                                "STG_USER" = {
                                                          login_name = "STG_USER"
                                                          role       = "STG_ROLE"
                                                          namespace  = "STG_DB.REFINED_LAYER"
                                                          warehouse  = "STG_WH"
                                                        }
                                              

                                                "PROD_USER" = {
                                                          login_name = "PROD_USER"
                                                          role       = "PROD_ROLE"
                                                          namespace  = "PROD_DB.REFINED_LAYER"
                                                          warehouse  = "PROD_WH"
                                                        }
                                              

                                                "ANALYTICS_USER" = {
                                                          login_name = "ANALYTICS_USER"
                                                          role       = "ANALYTICS_ROLE"
                                                          namespace  = "PROD_DB.ANALYTICS_LAYER"
                                                          warehouse  = "ANALYTICS_WH"
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
                  must_change_password = false
                }
                