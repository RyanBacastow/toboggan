import jinja2
import json
import re

class Toboggan:
    """
    inputs: users, roles, queries, syntax
    outputs: users.tf, roles.tf, queries.json, main.tf, variables.tf
    """

    def __init__(self, mode='create', main_tf=None, warehouses_file=None, databases_file=None, users_file=None,
                 roles_file=None, schemas_file=None, tables_file=None, queries_file=None, queries_syntax=None):
        self.mode = mode
        self.sep = ' ------------------------------ '
        self.main_tf = main_tf
        self.warehouses_file = warehouses_file
        self.users_file = users_file
        self.roles_file = roles_file
        self.schemas_file = schemas_file
        self.tables_file = tables_file
        self.queries_file = queries_file
        self.queries_syntax = queries_syntax
        self.databases_file = databases_file
        self.warehouses = []
        self.default_roles = [{"name": "PUBLIC",
                               "comment": "Pseudo-role that is automatically granted to every user and every role in your account. The PUBLIC role can own securable objects, just like any other role; however, the objects owned by the role are, by definition, available to every other user and role in your account.This role is typically used in cases where explicit access control is not needed and all users are viewed as equal with regard to their access rights."},
                              {"name": "ACCOUNTADMIN",
                               "comment": "Role that encapsulates the SYSADMIN and SECURITYADMIN system-defined roles. It is the top-level role in the system and should be granted only to a limited/controlled number of users in your account."},
                              {"name": "SECURITYADMIN",
                               "comment": "Role that can manage any object grant globally, as well as create, monitor, and manage users and roles. More specifically, this role is granted the MANAGE GRANTS security privilege to be able to modify any grant, including revoking it. Inherits the privileges of the USERADMIN role via the system role hierarchy (e.g. USERADMIN role is granted to SECURITYADMIN)."},
                              {"name": "USERADMIN",
                               "comment": "Role that is dedicated to user and role management only. More specifically, this role is granted the CREATE USER and CREATE ROLE security privileges. Can create and manage users and roles in the account (assuming that ownership of those roles or users has not been transferred to another role)."},
                              {"name": "SYSADMIN",
                               "comment": "Role that has privileges to create warehouses and databases (and other objects) in an account. If, as recommended, you create a role hierarchy that ultimately assigns all custom roles to the SYSADMIN role, this role also has the ability to grant privileges on warehouses, databases, and other objects to other roles."}
                              ]
        self.roles = self.default_roles.copy()
        self.databases = []
        self.schemas = []
        self.tables = []
        self.users = []
        self.queries = []

    #         if queries_file:
    #             self.users = self.read_file(users_file)
    #         else:
    #             self.users = self.intake_users()

    @staticmethod
    def clean_text(start_text, mode="lower"):
        """
        start_text: str : input text
        return: str : corrected text
        """
        if mode == 'lower':
            text = start_text.lower()
        else:
            text = start_text.upper()
        text = text.replace(" ", "_")
        text = text.replace("-", "_")
        text = re.sub(r'\W+', '', text)

        if start_text != text:
            print(f"\nStandardized naming from {start_text} to {text}.")
        return text

    @staticmethod
    def read_file(filename):
        if '.json' in filename:
            with open('filename') as json_file:
                data = json.load(json_file)
                print(data)
        else:
            with open('filename') as f:
                data = f.read().splitlines()

        return data

    @staticmethod
    def dedupe_dict_list(l):
        deduped = [dict(t) for t in {tuple(d.items()) for d in l}]
        return deduped

    def intake_warehouses(self, warehouses):
        """
        warehouses: list: list of warehouses or empty list
        return: list: list of warehouses populated with at least 1 warehouse
        """
        print(f"\n{self.sep}WAREHOUSES{self.sep}\n")
        """
        resource "snowflake_warehouse" "warehouse_terraform" {
              name              =   "dev_wh"
              warehouse_size    =   "SMALL"
              auto_resume       =   false
              auto_suspend      =   600
              comment           =   "terraform development warehouse"
        }
        """
        warehouse_sizes = ['XSMALL', 'SMALL', 'MEDIUM', 'LARGE', 'XLARGE', 'XXLARGE', 'XXXLARGE', 'X4LARGE']

        while True:
            ans = input("\nDo you want to add a warehouse? y/n\n")
            if ans.lower() in ['y', 'yes']:
                warehouse = self.clean_text(input("\nWhat is the warehouse name?\n"), mode='upper')

                if warehouse in [x['name'] for x in warehouses]:
                    print("\nWarehouse already added, please use unique names.\n")
                    continue

                while True:
                    warehouse_size = input(f"""\nWhat size should the warehouse be? (choose using 1-8)
1. XSMALL
2. SMALL
3. MEDIUM
4. LARGE
5. XLARGE
6. XXLARGE
7. XXXLARGE
8. X4LARGE\n""")

                    if warehouse_size not in ['1', '2', '3', '4', '5', '6', '7', '8']:
                        print('\nUse a number between 1 and 8.\n')
                        continue
                    else:
                        warehouse_size = warehouse_sizes[int(warehouse_size) - 1]
                        print(f"\n{warehouse_size} selected.\n")
                        break

                while True:
                    auto_resume = input(
                        f"\nShould this warehouse start when queuried automatically?\n1. true\n2. false\n")

                    if auto_resume not in ['1', '2']:
                        print("\nUse 1 or 2.\n")
                        continue
                    else:
                        if auto_resume == '1':
                            auto_resume = 'true'
                        else:
                            auto_resume = 'false'

                        print(f"\nauto_resume {auto_resume} selected.\n")
                        break

                while True:
                    auto_suspend = input(
                        f"\nHow long for the warehouse to suspend after inactivity? (60 - 3600 seconds)\n")
                    try:
                        if int(auto_suspend) > 3601 or int(auto_suspend) < 60:
                            print("\nUse a number between 60 and 3600\n")
                            continue
                        else:
                            print(f"\nauto_suspend {auto_suspend} selected.\n")
                            break

                    except:
                        print("\nUse a number between 60 and 3600\n")
                        continue

                comment = input(f"\nLeave a descriptive comment to describe {warehouse}:\n")

                wh = {'name': warehouse, 'warehouse_size': warehouse_size, 'auto_resume': auto_resume,
                      'auto_suspend': auto_suspend, 'comment': comment}
                warehouses.append(wh)
                print(f"\nCreated warehouse tf: {wh}")

            elif ans.lower() in ['n', 'no']:
                if len(warehouses) < 1:
                    print("\nYou have to add at least one warehouse.\n")
                else:
                    break
            else:
                print('\nPlease use yes, y, no, or n\n')

        return self.dedupe_dict_list(warehouses)

    def intake_roles(self, roles):
        """
        roles: list: list of roles or empty list
        return: list : list of roles populated with at least 1 role
        """
        print(f"\n{self.sep}ROLES{self.sep}\n")

        while True:
            ans = input("\nDo you want to add a role? y/n\n")
            if ans.lower() in ['y', 'yes']:
                role = self.clean_text(input("\nWhat is the role name?\n"), mode='upper')
                # TODO name logic

                if role in [x['name'] for x in roles]:
                    print("\nRole already added, please use unique names.\n")
                    continue

                comment = input(f"\nLeave a descriptive comment to describe {role}:\n")

                roles.append({'name': role, 'comment': comment})
            elif ans.lower() in ['n', 'no']:
                if len(roles) == 0:
                    print("\nUsing default roles only.\n")
                    break
                else:
                    break
            else:
                print('\nPlease use yes, y, no, or n\n')

        return self.dedupe_dict_list(roles)

    def intake_databases(self, databases):
        """
        databases: list :list of databases or empty list
        returns: list : list of databases populated with at least 1 database
        """
        print(f"\n{self.sep}DATABASES{self.sep}\n")
        databases = []

        while True:
            ans = input("\nDo you want to add a database? y/n\n")
            if ans.lower() in ['y', 'yes']:
                database = self.clean_text(input("What is the database name?"), mode='upper')

                if database in [x for x in databases]:
                    print("Database already added, please use unique names.\n")
                    continue

                databases.append({'name': database})

            elif ans.lower() in ['n', 'no']:
                if len(databases) < 1:
                    print("You have to add at least one database.")
                else:
                    break
            else:
                print('Please use yes, y, no, or n\n')

        return self.dedupe_dict_list(databases)

    def intake_schemas(self, schemas):
        """
        schemas: list of schemas or empty list
        returns: list : list of schemas populated with at least 1 schema
        """
        print(f"\n{self.sep}SCHEMAS{self.sep}\n")

        schema_tracker = []
        while True:
            ans = input("\nDo you want to add a schema? y/n\n")
            if ans.lower() in ['yes', 'y']:
                name = self.clean_text(input("\nWhat is the schema name?\n"), mode='upper')
                if name in schema_tracker:
                    print("\nSchema already added, please use unique names.\n")
                    continue
                else:
                    schema_tracker.append(name)

                comment = input(f"\nLeave a descriptive comment to describe {name}:\n")

                out_dict = {'name': name, 'comment': comment, 'database': None, 'usage_access': [], 'all_access': []}

                # DATABASE SELECTION
                databases = []
                while True:
                    print(f"\nWhich database should {name} be created in?\n")
                    i = 1
                    for option in self.database_names:
                        print(f"{i}. {option}")
                        i += 1
                    database = input(f"\nChoose an option between 1 and {i - 1}\n")

                    try:
                        database = self.database_names[int(database) - 1]
                        if database in databases:
                            print(f"\n{database} already associated with schema.\n")
                            continue
                        else:
                            out_dict['database'] = database
                            print(f"\nAdded {database} association.\n")
                            break
                    except:
                        print(f"\nChoose an option between 1 and {i - 1}\n")
                        continue

                        # ROLE SELECTION
                roles = []
                while True:
                    ans = input(f"\nDo you want to add a role to access objects in {database}.{name}? y/n\n")
                    if ans.lower() in ['yes', 'y']:
                        print(f"\nWhat role should have access to objects in {database}.{name}?\n")
                        i = 1
                        for option in self.role_names:
                            print(f"{i}. {option}")
                            i += 1
                        role = input(
                            f"\nChoose an option between 1 and {i - 1}. Else, type 'help' to see roles and descriptions.\n")

                        try:
                            role = self.role_names[int(role) - 1]
                            if role in roles:
                                print(f"\n{role} already associated with schema.\n")
                                continue
                            else:
                                roles.append(role)

                        except:
                            if role.lower() == 'help':
                                print(self.sep + "ROLES OVERVIEW" + self.sep)
                                for role in self.roles:
                                    print(f"\n{role['name']} : {role['comment']}")
                                continue
                            else:
                                print(
                                    f"\nChoose an option between 1 and {i - 1}. Else, type 'help' to see roles and descriptions.\n")
                                continue

                                # ROLE-TYPE SELECTION
                        while True:
                            access_type = input(
                                f"""\nWhat type of access would you like to grant to {role} on {database}.{name}?\n
1. USAGE: Enables using a virtual warehouse and executeing queries on the warehouse.
2. ALL: Grants all privileges, except OWNERSHIP, on the warehouse.
Enter 1 or 2:\n""")
                            if access_type not in ["1", "2"]:
                                print("\nEnter 1 or 2.\n")
                                continue
                            else:
                                if access_type == '1':
                                    access_level = 'USAGE'
                                    out_dict['usage_access'].extend(role)
                                else:
                                    access_level = 'ALL'
                                    out_dict['all_access'].extend(role)

                                print(f"\nAdded {role} role to {access_level} access for {database}.{name}\n")

                                break
                        schemas.append(out_dict)
                        continue

                    elif ans.lower() in ['n', 'no']:
                        # Default behavior?
                        break
                    else:
                        print('\nPlease use yes, y, no, or n\n')

            elif ans.lower() in ['n', 'no']:
                if len(schemas) < 1:
                    print("\nYou must define at least 1 schema.\n")
                    continue
                else:
                    break
            else:
                print('\nPlease use yes, y, no, or n\n')
                continue

        return schemas

    def intake_tables(self):
        pass

    def intake_users(self, users):
        """
        users: list of users or empty list
        returns: list : list of users populated with at least 1 user
        """
        print(f"\n{self.sep}USERS{self.sep}\n")

        while True:
            ans = input("\nDo you want to add a user? y/n\n")
            if ans.lower() in ['yes', 'y']:
                user = {}
                name = self.clean_text(input("\nWhat is the user's username?\n"))
                if name in [x['name'] for x in users]:
                    print(f"\nUser '{name}' already added, please use unique names.\n")
                    continue
                else:
                    user['name'] = name

                while True:
                    print(f"What role should {name} have?\n")
                    i = 1
                    for option in self.role_names:
                        print(f"{i}. {option}")
                        i += 1
                    role = input(f"\nChoose an option between 1 and {i - 1}\n")

                    try:
                        role = self.role_names[int(role) - 1]
                        user['role'] = role
                        break
                    except:
                        print(f"\nChoose an option between 1 and {i - 1}\n")
                        continue

                while True:
                    print(f"\nWhat warehouse should {name} have?\n")
                    i = 1
                    for option in self.warehouses:
                        print(f"{i}. {option}")
                        i += 1
                    warehouse = input(f"\nChoose an option between 1 and {i - 1}\n")

                    try:
                        warehouse = self.warehouses[int(warehouse) - 1]
                        user['warehouse'] = warehouse
                        break
                    except:
                        print(f"\nChoose an option between 1 and {i - 1}\n")
                        continue

                schemas = [f"{x['database']}.{x['schema']}" for x in self.schemas]

                while True:
                    i = 1
                    print(f"\nWhat default database and schema should {name} have?\n")
                    for option in schemas:
                        print(f"{i}. {option}")
                        i += 1
                    namespace = input(f"\nChoose an option between 1 and {i - 1}\n")

                    try:
                        namespace = schemas[int(namespace) - 1]
                        user['namespace'] = namespace
                        break
                    except:
                        print(f"\nChoose an option between 1 and {i - 1}\n")
                        continue

                users.append(user)

            elif ans.lower() in ['n', 'no']:
                if len(users) < 1:
                    print("\nYou have to add at least one user.\n")
                else:
                    break
            else:
                print('\nPlease use yes, y, no, or n\n\n')

        return self.dedupe_dict_list(users)

    def intake_queries(self):
        pass

    def init_doc(self):
        """
        provider "snowflake" {
          account = "your-snowflake-account"
          region  = "your-snowflake-region"
        }
        """
        pass

    def create_warehouses(self):
        """
        Add warehouses to main.tf
        self.warehouses : {'name':warehouse, 'warehouse_size':warehouse_size, 'auto_resume':auto_resume, 'auto_suspend':auto_suspend, 'comment':comment}
        """

        out_str = ""

        warehouse_template = jinja2.Template("""
        resource "snowflake_warehouse" "warehouse_terraform" {
              name              =   "{{name}}"
              warehouse_size    =   "{{warehouse_size}}"
              auto_resume       =   {{auto_resume}}
              auto_suspend      =   {{auto_suspend}}
              comment           =   "{{comment}}"
        }""")

        for warehouse in self.warehouses:
            out_str += warehouse_template.render(name=warehouse['name'],
                                                 warehouse_size=warehouse['warehouse_size'],
                                                 auto_resume=warehouse['auto_resume'],
                                                 auto_suspend=warehouse['auto_suspend'],
                                                 comment=warehouse['comment']) + "\n"

        return out_str

    def create_roles(self):
        """
        create roles.tf if not provided
        self.roles : [{'name': 'role_name', 'comment':'description'}]
        """
        role_template = jinja2.Template("""
            locals {
              roles = {
               {{role_blob}}
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
            """)

        role_insert_template = jinja2.Template("""
                                                "{{role}}" = {
                                                  comment = "{{comment}}"
                                                  users = {{users}}
                                                }
                                                """)

        role_blob = """"""

        for role in self.roles:
            out_dict = item.copy()
            out_dict['users'] = []
            for user in self.users:
                if role['name'] in user['roles']:
                    out_dict['users'] = out_dict['users'].appent(user['name'])
            role_blob += role_insert_template.render(role=item['name'], comment=item['comment']).replace("'", '"')

        out_str = role_template.render(roles_blob=roles_blob)

        with open('roles.tf', 'w+') as f:
            f.write(out_str)

    def create_schemas(self):
        """
        self.schemas : [{'name':name, 'comment':comment, 'database': database, 'usage_access':[roles], 'all_access':[roles]}]
        """
        schema_template = jinja2.Template(
            """
            locals {
              schemas = {
                {{schema_blob}}
              }
            }
            resource "snowflake_schema" "schema" {
              for_each = local.schemas
              name     = each.key
              database = each.value.database
              comment  = each.value.comment
            }

            resource "snowflake_schema_grant" "schema_grant_usage" {
              for_each      = local.schemas
              schema_name   = each.key
              database_name = each.value.database
              privilege     = "USAGE"
              roles         = each.value.usage_roles
              shares        = []
            }

            resource "snowflake_schema_grant" "schema_grant_all" {
              for_each      = local.schemas
              schema_name   = each.key
              database_name = each.value.database
              privilege     = "ALL"
              roles         = each.value.all_roles
              shares        = []
            }
            """)

        schema_insert_template = jinja2.Template(
            """
            "{{schema}}" = {
                  database = "{{database}}"
                  comment = "{{comment}}"
                  usage_roles = {{usage_roles}}
                  all_roles = {{all_roles}}
                }\n
            """
        )

        schema_blob = """"""

        for item in self.schemas:
            schemas_blob += schema_insert_template.render(schema=item['name'], database=item['database'],
                                                          usage_roles=item['usage_roles'],
                                                          all_roles=item['all_roles']).replace("'", '"')

        out_str = schema_template.render(schemas_blob=schema_blob)

        with open('roles.tf', 'w+') as f:
            f.write(out_str)

    def create_users(self):
        """
        self.users : [{'name': 'role'}]
        """
        user_template = jinja2.Template(
            """
            locals {
              users = {
                {{user_blob}}
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
            """)

        user_insert_template = jinja2.Template("""
                                                "{{name}}" = {
                                                          login_name = "{{name}}"
                                                          role       = "{{role}}"
                                                          namespace  = "{{namespace}}"
                                                          warehouse  = "{{warehouse}}"
                                                        }
                                              """)

        user_blob = """"""

        for user in self.users:
            user_blob += user_insert_template.render(name=user['name'], role=user['role'], namespace=user['namespace'],
                                                     warehouse=user['warehouse']) + "\n"

        out_str = user_template.render(user_blob=user_blob)

        with open('users.tf', 'w+') as f:
            f.write(out_str)

    def convert_sql(self, sql_syntax):
        """
        convert a query from another syntax to snow sql
        """
        pass

    def create_main_tf(self):
        """
        create terraform
        """
        acct = input("What is your snowflake account address?\n")
        region = input("What is your snowflake account address?\n")
        main_template = jinja2.Template("""provider "snowflake" {
                                                      account = "{{acct}}"
                                                      region  = "{{region}}"
                                                    }""")
        out_str = main_template.render(acct=acct, region=region) + "\n"

        out_str += self.create_warehouses()

        with open("main.tf", "w") as f:
            f.write(out_str)

    def main(self):
        """
        TODO
        """
        self.warehouses = self.intake_warehouses(self.warehouses)
        self.warehouse_names = [x['name'] for x in self.warehouses]

        if self.roles_file:
            self.roles = self.read_file(roles_file)

        self.roles = self.intake_roles(self.roles)
        self.role_names = [x['name'] for x in self.roles]

        if self.databases_file:
            self.databases = self.read_file(databases_file)

        self.databases = self.intake_databases(self.databases)
        self.database_names = [x['name'] for x in self.databases]

        if self.schemas_file:
            self.schemas = self.read_file(schemas_file)

        self.schemas = self.intake_schemas(self.schemas)
        self.schema_names = [x['name'] for x in self.schemas]

        if self.users_file:
            self.users = self.read_file(users_file)

        self.users = self.intake_users(self.users)
        self.user_names = [x['name'] for x in self.users]

        if self.main_tf:
            # TODO logic here
            pass
        else:
            self.create_main_tf()

if __name__ == '__main__':
    t = Toboggan(mode='create')
    t.main()
