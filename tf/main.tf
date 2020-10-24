

provider "snowflake" {
  account = "test"
  region  = "test"
  role  = "ACCOUNTADMIN"
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "DEV_WH"
  warehouse_size    =   "SMALL"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "This database is for developers and public role access. General scheduled and adhoc work, not for large workloads or views."
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "QA_WH"
  warehouse_size    =   "SMALL"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "This database is for QA workflows and QA resources to query. Can be used in a variety of ways, but may not be good for largest analytical workflows."
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "STG_WH"
  warehouse_size    =   "MEDIUM"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "This warehouse is for use with the staging database. Medium instance, various workflows allowed."
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "PROD_WH"
  warehouse_size    =   "LARGE"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "Production warehouse for ETL workflows and large query workloads."
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "ANALYTICS_WH"
  warehouse_size    =   "LARGE"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "Analytics Warehouse for ad-hoc and tableau query needs"
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "TMO_WH"
  warehouse_size    =   "MEDIUM"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "This is a warehouse for TMO read, write, and share workflows into TMO external snowflake acct."
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "TEST_WH"
  warehouse_size    =   "XSMALL"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "Delete me"
}

