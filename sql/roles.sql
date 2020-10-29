

CREATE ROLE IF NOT EXISTS TEST_ROLE
COMMENT = 'this is a test role to show json structure';

GRANT ROLE TEST_ROLE TO ROLE SYSADMIN;
