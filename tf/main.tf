

provider "snowflake" {
  account = "test"
  region  = "test"
  role  = "ACCOUNTADMIN"
}



resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "TEST_WH"
  warehouse_size    =   "LARGE"
  auto_resume       =   true
  auto_suspend      =   60
  comment           =   "this is a test wh"
}

