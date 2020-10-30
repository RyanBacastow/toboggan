

provider "snowflake" {
  account = "YOUR_ACCT_NAME_HERE"
  region  = "YOUR_REGION_HERE"
  role  = "ACCOUNTADMIN"
}


resource "snowflake_warehouse" "warehouse_terraform" {
  name              =   "TEST_WH"
  warehouse_size    =   "XSMALL"
  auto_resume       =   true
  auto_suspend      =   300
  comment           =   "Test warehouse deployment"
}

