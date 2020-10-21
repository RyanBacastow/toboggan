#!/usr/bin/env python
# coding: utf-8

# In[10]:


import jinja2
import json
import re
import os
from templates.templates import *

# In[11]:


class Intake(object):
    """
    inputs: users, roles, queries, syntax
    outputs: users.tf, roles.tf, queries.json, main.tf, variables.tf
    """
    def __init__(self):
        self.sep = ' ------------------------------ '
        self.warehouses = []
        self.default_roles = [{"name":"PUBLIC", "comment":"Pseudo-role that is automatically granted to every user and every role in your account. The PUBLIC role can own securable objects, just like any other role; however, the objects owned by the role are, by definition, available to every other user and role in your account.This role is typically used in cases where explicit access control is not needed and all users are viewed as equal with regard to their access rights."},
                              {"name":"ACCOUNTADMIN", "comment":"Role that encapsulates the SYSADMIN and SECURITYADMIN system-defined roles. It is the top-level role in the system and should be granted only to a limited/controlled number of users in your account."},
                              {"name":"SECURITYADMIN", "comment":"Role that can manage any object grant globally, as well as create, monitor, and manage users and roles. More specifically, this role is granted the MANAGE GRANTS security privilege to be able to modify any grant, including revoking it. Inherits the privileges of the USERADMIN role via the system role hierarchy (e.g. USERADMIN role is granted to SECURITYADMIN)."},
                              {"name":"USERADMIN", "comment":"Role that is dedicated to user and role management only. More specifically, this role is granted the CREATE USER and CREATE ROLE security privileges. Can create and manage users and roles in the account (assuming that ownership of those roles or users has not been transferred to another role)."},
                              {"name":"SYSADMIN", "comment":"Role that has privileges to create warehouses and databases (and other objects) in an account. If, as recommended, you create a role hierarchy that ultimately assigns all custom roles to the SYSADMIN role, this role also has the ability to grant privileges on warehouses, databases, and other objects to other roles."}
                             ]
        self.access_types = ["USAGE: Enables using a virtual warehouse and executeing queries on the schema.", 
                             "ALL: Grants all privileges, except OWNERSHIP, on the schema.",
                             "CANCEL: Return to roles."]
        self.roles = self.default_roles.copy()
        self.databases = []
        self.schemas = []
        self.tables = []
        self.users = []
        self.queries = []
        
        self.account_info = {}
        
        self.tf_out_dir = 'tf'
        self.sql_out_dir = 'sql'
        
#         if queries_file:
#             self.users = self.read_file(users_file)
#         else:
#             self.users = self.intake_users()

    @staticmethod
    def create_dirs(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    
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
        text = text.strip()
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
    
    @staticmethod
    def make_choices(l, t, mode=None):
        l = l.copy()
        if mode:
            l.extend(["HELP", "CANCEL"])
        len_l = len(l)
        while True:
            print (f"\n{t}")
            for i in (range(1, len(l) + 1)):
                print(f"{i}. {l[i - 1]}")

            ans =  input(f"""(Choose using 1-{len_l})\n""")

            try:
                if int(ans) not in [x for x in range(1,len_l + 1)]:
                    print(f'\nUse a number between 1 and {len_l}.\n')
                    continue
                else:
                    out = l[int(ans) - 1]
                    print(f"\n{out} selected.")
                    return(out)
            except:
                print(f'\nUse a number between 1 and {len_l}.\n')
                continue
    
    def intake_account_info(self):
        """
        Takes the account name, region, login, and password. Sets the login and password for tf connection.
        """
        name = input("What is your snowflake account address?\n")
        region = input("What is your snowflake account region?\n")
        login = input("What is your snowflake account login name?\n")
        password = input("What is your snowflake account password\n")
        
        out_dict = {'name': name, 'region': region, 'login': login, 'password': password}
        
        #SET ENV VARS
        os.environ['SNOWFLAKE_USER'] = out_dict['login']
        os.environ['SNOWFLAKE_PASSWORD'] = out_dict['password']
        
        return out_dict
        
    def intake_warehouses(self):
        """
        warehouses: list: list of warehouses or empty list
        return: list: list of warehouses populated with at least 1 warehouse
        """
        warehouses = self.warehouses.copy()

        print(f"\n{self.sep}WAREHOUSES{self.sep}\n")
        print("A virtual warehouse, often referred to simply as a “warehouse”, is a cluster of compute resources in Snowflake. A warehouse provides the required resources, such as CPU, memory, and temporary storage\n")

        warehouse_sizes = ['XSMALL', 'SMALL', 'MEDIUM', 'LARGE', 'XLARGE', 'XXLARGE', 'XXXLARGE', 'X4LARGE']
        
        while True:
            ans = input("\nDo you want to add a warehouse? y/n\n")
            if ans.lower() in ['y', 'yes']:
                warehouse = self.clean_text(input("\nWhat is the warehouse name?\n"), mode='upper')
                
                if warehouse in [x['name'] for x in warehouses]:
                    print("\nWarehouse already added, please use unique names.\n")
                    continue      
                
                elif warehouse == '':
                    print("\nPlease use valid characters.\n")
                    continue
                
                warehouse_size = self.make_choices(warehouse_sizes, "What size should the warehouse be?")
                
                auto_resume = self.make_choices(['true', 'false'], "Should this warehouse start when queuried automatically?")
                
                while True:
                    auto_suspend = input(f"\nHow long for the warehouse to suspend after inactivity? (60 - 3600 seconds)\n")
                    try:
                        if int(auto_suspend) > 3601 or int(auto_suspend) < 60:
                            print("\nUse a number between 60 and 3600\n")
                            continue
                        else:
                            print(f"\nauto_suspend {auto_suspend} selected.")
                            break
                            
                    except:
                        print("\nUse a number between 60 and 3600\n")
                        continue
                
                comment = input(f"\nLeave a descriptive comment to describe {warehouse}:\n")
                
                wh = {'name':warehouse, 'warehouse_size':warehouse_size, 'auto_resume':auto_resume, 'auto_suspend':auto_suspend, 'comment':comment}
                warehouses.append(wh)
                print(f"\nCreated warehouse:")
                for k, v in wh.items():
                    print(f"{k}: {v}")
                
            elif ans.lower() in ['n', 'no']:
                if len(warehouses) < 1:
                    print("\nYou have to add at least one warehouse.\n")
                else:
                    break
            else:
                print('\nPlease use yes, y, no, or n\n')
        
        return warehouses
        
        
    def intake_roles(self):
        """
        roles: list: list of roles or empty list
        return: list : list of roles populated with at least 1 role
        """
        roles = self.roles.copy()

        print(f"\n{self.sep}ROLES{self.sep}\n")
        print("An entity to which privileges can be granted. Roles are in turn assigned to users. Note that roles can also be assigned to other roles, creating a role hierarchy.\n")

        while True:
            ans = input("\nDo you want to add a role? y/n\n")
            if ans.lower() in ['y', 'yes']:
                role = self.clean_text(input("\nWhat is the role name?\n"), mode = 'upper')
                #TODO name logic
                
                if role in [x['name'] for x in roles]:
                    print("\nRole already added, please use unique names.\n")
                    continue
                
                elif role == '':
                    print("\nPlease use valid characters.\n")
                    continue
                
                comment = input(f"\nLeave a descriptive comment to describe {role}:\n")
                
                r = {'name':role,'comment':comment}
                roles.append(r)
                
                print(f"\nCreated role:")
                for k, v in r.items():
                    print(f"{k}: {v}")
                    
            elif ans.lower() in ['n', 'no']:
                if len(roles) == 0:
                    print("\nUsing default roles only.\n")
                    break
                else:
                    break
            else:
                print('\nPlease use yes, y, no, or n\n')
        
        return roles
    
    def intake_databases(self):
        """
        databases: list :list of databases or empty list
        returns: list : list of databases populated with at least 1 database
        """
        databases = self.databases.copy()
        print(f"\n{self.sep}DATABASES{self.sep}\n")
        print("A database is a logical grouping of schemas. Each database belongs to a single Snowflake account.\n")
        databases = []
        
        while True:
            ans = input("\nDo you want to add a database? y/n\n")
            if ans.lower() in ['y', 'yes']:
                database = self.clean_text(input("\nWhat is the database name?\n"), mode='upper')
                
                if database in [x['name'] for x in databases]:
                    print("\nDatabase already added, please use unique names.\n")
                    continue
                
                elif database == '':
                    print("\nPlease use valid characters.\n")
                    continue
                comment = input(f"\nLeave a descriptive comment to describe {database}:\n")
                d = {'name': database, 'comment': comment}
                databases.append(d)
                print(f"\nAdded Database:")
                for k, v in d.items():
                    print(f"{k}: {v}")
                
            elif ans.lower() in ['n', 'no']:
                if len(databases) < 1:
                    print("You have to add at least one database.")
                else:    
                    break
            else:
                print('Please use yes, y, no, or n\n')
        
        return databases

    def intake_schemas(self):
        """
        schemas: list of schemas or empty list
        returns: list : list of schemas populated with at least 1 schema
        """
        schemas = self.schemas.copy()
        print(f"\n{self.sep}SCHEMAS{self.sep}\n")
        print("""A schema is a logical grouping of database objects (tables, views, etc.). Each schema belongs to a single database.\n""")

        schema_tracker = []
        while True:
            ans = input("\nDo you want to add a schema? y/n\n")
            if ans.lower() in ['yes', 'y']:
                name = self.clean_text(input("\nWhat is the schema name?\n"), mode='upper')
                if name in schema_tracker:
                    print("\nSchema already added, please use unique names.\n")
                    continue
                elif name == '':
                    print("\nPlease use valid characters.\n")
                    continue
                else:
                    schema_tracker.append(name)

                comment = input(f"\nLeave a descriptive comment to describe {name}:\n")
                
                # DATABASE SELECTION
                databases = []
                while True:
                    out_dict = {'name':name, 'comment':comment, 'database': None, 'usage_access':[], 'all_access':[]}
                    ans = input(f"\nDo you want to add {name} to a database? y/n\n")
                    if ans.lower() in ['yes', 'y']:
                        database = self.make_choices(self.database_names, f"Which database should {name} be created in?", mode='help')
                        if database in databases:
                            print(f"\n{name} already added to schema {database}.\n")
                            continue
                        elif database == 'HELP':
                            print("\nPlease select the database that this schema should belong to, each schema must belong to a database.\n")
                            continue
                        elif database == 'CANCEL':
                            continue
                        
                        databases.append(database)
                        out_dict['database'] = database

                    elif ans.lower() in ['n', 'no']:
                        if len(databases) < 1:
                            print(f"\nYou must add {name} to at least 1 database.\n")
                            continue
                        else:
                            break
                    else:
                        print('\nPlease use yes, y, no, or n\n')
                        continue
                    
                    #ADD TABLES
                    # TODO
                    
                    #ROLE SELECTION
                    roles = []
                    while True:
                        ans = input(f"\nDo you want to add a role to access objects in {database}.{name}? y/n\n")
                        
                        if ans.lower() in ['yes', 'y']:
                            
                            role = self.make_choices(self.role_names, f"What role should have access to objects in {database}.{name}?", mode='help')
                            
                            if role == 'HELP':
                                print(self.sep + "ROLES OVERVIEW" + self.sep)
                                for role in self.roles:
                                    print(f"\n{role['name']} : {role['comment']}")
                                continue
                                
                            elif role == 'CANCEL':
                                print("\nCanceled.\n")
                                continue
                            
                            if role in roles:
                                print(f"\nRole {role} already associated with {database}.{name}.\n")
                                continue

                            #ROLE-TYPE SELECTION
                            access_type = self.make_choices(['ALL', 'USAGE'], f"What type of access would you like to grant to {role} on {database}.{name}?", mode='help')
    
                            if access_type == 'ALL':
                                roles.append(role)
                                out_dict['all_access'].append(role)
                            
                            elif access_type == 'USAGE':
                                roles.append(role)
                                out_dict['usage_access'].append(role)
                            
                            elif access_type == 'HELP':
                                print(f"{self.sep}ACCESS TYPE{self.sep}")
                                print("\nALL: Granting ALL access means the role will have permission to execute all commands on the schema and objects therein. eg CREATE TABLE, MODIFY, etc")
                                print("USAGE: Granting USAGE access enables using a schema, including executing SHOW SCHEMAS commands to list the schema details in a database.")
                                continue
                                
                            else:
                                print("\nReturning to role selection.\n")
                                continue

                            print(f"\nAdded {role} role to {access_type} access for {database}.{name}\n")
                            continue

                        elif ans.lower() in ['n', 'no']:
                            #Default behavior?
                            break
                        else:
                            print('\nPlease use yes, y, no, or n\n')
                    
                    schemas.append(out_dict)
                    print(f"\nCreated schema:")
                    for k,v in out_dict.items():
                        print(f"{k}: {v}")

            elif ans.lower() in ['n', 'no']:
                break
            else:
                print('\nPlease use yes, y, no, or n\n')
                continue
            
        return schemas

    def intake_tables(self):
        pass

    def intake_users(self):
        """
        users: list of users or empty list
        returns: list : list of users populated with at least 1 user
        """
        print(f"\n{self.sep}USERS{self.sep}\n")
        print("A user identity recognized by Snowflake, whether associated with a person or program.\n")
        users = self.users.copy()
        while True:
            ans = input("\nDo you want to add a user? y/n\n")
            if ans.lower() in ['yes', 'y']:
                user = {"name": None, "warehouse": None, "namespace": None, "roles":[], "default_role": None}
                name = self.clean_text(input("\nWhat is the user's username?\n"), mode='upper')
                if name in [x['name'] for x in users]:
                    print(f"\nUser '{name}' already added, please use unique names.\n")
                    continue
                elif name == '':
                    print("\nPlease use valid characters.\n")
                    continue
                else:
                    user['name'] = name
                
                #ROLE SELECTION
                roles = ['PUBLIC']
                while True:
                    ans = input(f"\nDo you want to add {name} to a role? y/n\n")
                    if ans.lower() in ['yes', 'y']:
                        role = self.make_choices(self.role_names, f"What role should {name} have?", mode='help')
                        if role == 'HELP':
                            print("Each user can belong to as many roles as required.")
                            print(self.sep + "ROLES OVERVIEW" + self.sep)
                            for role in self.roles:
                                print(f"\n{role['name']} : {role['comment']}")
                            continue
                        elif role == 'CANCEL':
                            print("\nCanceled.\n")
                            continue
                        elif role in roles:
                            if role == 'PUBLIC':
                                print("\nEvery user automatically has access to the PUBLIC role.\n")
                            else:
                                print(f"\nUser '{name}' already associated with role {role}, please use unique names.\n")
                            continue
                        elif role == '':
                            print("\nPlease use valid characters.\n")
                            continue
                        else:
                            roles.append(role)
                    elif ans.lower() in ['no', 'n']:
                        if len(roles) <= 1:
                            print("Default PUBLIC role selected.")
                        user['roles'].extend(roles)
                        break
                
                default_role = self.make_choices(roles, f"Which role should be the default role for {name}?")
                user['default_role'] = default_role
                
                warehouse = self.make_choices(self.warehouse_names, f"What warehouse should {name} use as a default?")
                user['warehouse'] = warehouse
                
                schemas = [f"{x['database']}.{x['name']}" for x in self.schemas]
            
                namespace = self.make_choices(schemas, f"What default database and schema should {name} have?")
                
                user['namespace'] = namespace
                users.append(user)
                print("\nCreated User:")
                for k, v in user.items():
                    print(f"{k}: {v}")
                              
            elif ans.lower() in ['n', 'no']:
                if len(users) < 1:
                    print("\nYou have to add at least one user.\n")
                else:
                    break
            else:
                print('\nPlease use yes, y, no, or n\n\n')
        
        return users
    
    def choose_mode(self):
        while True:
            mode = self.make_choices(['CREATE', 'IMPORT'], "Which mode would you like to run in?", mode='help')
            if mode == 'HELP':
                print("\ncreate: Create a brand new set of resources (warehouses, dtabases, roles, schemas, users) from scratch.")
                print("import: Use the snowglobe module to import existing resources into the .tfstate and tf resource files.")
                continue
            elif mode == 'CANCEL':
                print("Must choose to either import or create new resources.")
                continue
            else:
                return mode
                
    def import_resources(self):
        pass
                
    def main(self):
        """
        TODO
        """
        self.account_info = self.intake_account_info()
        
        self.mode = self.choose_mode()
        if self.mode == 'CREATE':
        # ----------------------- INTAKE ----------------------- #
            self.warehouses = self.intake_warehouses()
            self.warehouse_names = [x['name'] for x in self.warehouses]

            self.roles = self.intake_roles()
            self.role_names = [x['name'] for x in self.roles]

            self.databases = self.intake_databases()
            self.database_names = [x['name'] for x in self.databases]

            self.schemas = self.intake_schemas()
            self.schema_names = [x['name'] for x in self.schemas]

            self.users = self.intake_users()
            self.user_names = [x['name'] for x in self.users]
                   
        # --------------------- DOC CREATION --------------------- #
        
        elif self.mode == 'import':
            self.import_resources()
            


# In[12]:


class create_output:
    def __init__(self, intake):
        self.mode = intake.mode
        self.sep = intake.sep
        self.warehouses = intake.warehouses
        self.default_roles = intake.default_roles
        self.access_types = intake.access_types
        self.roles = intake.roles
        self.databases = intake.databases
        self.schemas = intake.schemas
        self.tables = intake.tables
        self.users = intake.users
        self.queries = intake.queries
        self.account_info = intake.account_info

        self.tf_out_dir = intake.tf_out_dir 
        self.sql_out_dir = intake.sql_out_dir
    
    @staticmethod
    def create_dirs(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def intake_queries(self):
        pass
    
    def create_sql(self, filename, template, objects, fields):
        out_str = ""
        
        for item in objects:
            d = {}
            for field in fields:
                d[field] = item[field]
            out_str += template.render(d)
        
        with open(f'{self.sql_out_dir}/{filename}', 'w+') as f:
            f.write(out_str)
            
        return out_str
    
    def create_warehouses_tf(self):
        """
        Add warehouses to main.tf
        self.warehouses : {'name':warehouse, 'warehouse_size':warehouse_size, 'auto_resume':auto_resume, 'auto_suspend':auto_suspend, 'comment':comment}
        """
        
        out_str = ""
        
        for item in self.warehouses:
            out_str += warehouse_template_tf.render(name=item['name'],
                                                 warehouse_size=item['warehouse_size'], 
                                                 auto_resume=item['auto_resume'], 
                                                 auto_suspend=item['auto_suspend'],
                                                 comment=item['comment']) + "\n"
        
        return out_str
    
    def create_warehouses_sql(self):
        """
        Add warehouses to warehouse.sql
        self.warehouses : {'name':warehouse, 'warehouse_size':warehouse_size, 'auto_resume':auto_resume, 'auto_suspend':auto_suspend, 'comment':comment}
         filename, template, objects, fields
        """
        
        out_str = self.create_sql('warehouses.sql', warehouse_template_sql, self.warehouses, ['name', 'warehouse_size', 'auto_suspend', 'auto_resume', 'comment'])
        
        return out_str

    def create_databases_tf(self):
        """
        create roles.tf if not provided
        self.roles : [{'name': 'role_name', 'comment':'description'}]
        """
        
        blob = """"""
        
        for db in self.databases:
            blob += database_template_tf.render(name=db['name'], 
                                                #comment=db['comment']
                                               )
                                
        out_str = database_template_tf.render(blob=blob)
        
        with open(f'{self.tf_out_dir}/db.tf', 'w+') as f:
            f.write(out_str)
            
        return out_str
            
    def create_databases_sql(self):
        """
        Create database.sql
        """
        out_str = ""
        
        out_str = self.create_sql('databases.sql', database_template_sql, self.databases, ['name', 
#                                                                                            'comment'
                                                                                          ])
        
        return out_str
        
    def create_roles_tf(self):
        """
        create roles.tf if not provided
        self.roles : [{'name': 'role_name', 'comment':'description'}]
        """
        
        role_blob = """"""
        
        for role in self.roles:
            if role['name'] not in [x['name'] for x in self.default_roles]:
                out_dict = role.copy()
                out_dict['users'] = []
                print(out_dict)
                for user in self.users:
                    if role['name'] in user['roles']:
                        out_dict['users'].append(user['name'])
                role_blob += role_insert_template_tf.render(role=out_dict['name'], comment=out_dict['comment'], users=out_dict['users']).replace("'",'"')
                                
        out_str = role_template_tf.render(role_blob=role_blob)
        
        with open(f'{self.tf_out_dir}/roles.tf', 'w+') as f:
            f.write(out_str)
        
        return out_str
            
    def create_grants_sql(self, mode='schema'):
        """
        Handle associating roles with correct schemas or users.
        #schema: {'name':name, 'comment':comment, 'database': database, 'usage_access':[ROLES], 'all_access':[ROLES]}
        #user: {"name": name, "warehouse": warehouse, "namespace": namespace}
        """
        out_str = ""
        
        if mode == 'schema':
            for role in self.role_names:
                for schema in self.schemas:
                    if role in schema['all_roles']:
                        out_str += f"GRANT ALL ON SCHEMA {schema['database']}.{schema['schema']} TO ROLE {role};\n"
                    elif role in schema['usage_roles']:
                        out_str += f"GRANT USAGE ON SCHEMA {schema['database']}.{schema['schema']} TO ROLE {role};\n"
        
        else:
            for user in self.users:
                for role in user['roles']:
                    out_str += f"GRANT ROLE {role} to USER {user['name']};\n"
                out_string += f"GRANT OPERATE ON WAREHOUSE {user['warehouse']} TO {user['name']};"
                
        return out_str

    def create_roles_sql(self):
        """
        Add roles to roles.sql
        """
        
        out_str = ""

        out_str = self.create_sql('roles.sql', role_template_sql, [role for role in self.roles if role['name'] not in [x['name'] for x in self.default_roles]], ['name', 'comment'])
                    
        return out_str
    
    def create_schemas_tf(self):
        """
        self.schemas : [{'name':name, 'comment':comment, 'database': database, 'usage_access':[roles], 'all_access':[roles]}]
        """
            
        schema_blob = """"""
            
        for item in self.schemas:
            schema_blob += schema_insert_template_tf.render(schema=item['name'], 
                                                         database=item['database'], 
                                                         usage_roles=item['usage_access'], 
                                                         all_roles=item['all_access']).replace("'",'"')
                                
        out_str = schema_template_tf.render(schemas_blob=schema_blob)
        
        with open(f'{self.tf_out_dir}/schemas.tf', 'w+') as f:
            f.write(out_str)
        
        return out_str

    def create_schemas_sql(self):
        """
        Add schemas to schemas.sql
        """
        
        out_str = ""
        
        out_str = self.create_sql('schemas.sql', schema_template_sql, self.schemas, ['name', 'comment', 'database'])
        print(out_str)
        
        return out_str

    def create_users_tf(self):
        """
        self.users : [{name: None, warehouse: None, namespace: None}]
        """
        
        user_blob = """"""
    
        for user in self.users:
            user_blob += user_insert_template_tf.render(name=user['name'], role=user['default_role'], namespace=user['namespace'], warehouse=user['warehouse']) + "\n"
                                
        out_str = user_template_tf.render(user_blob=user_blob)
        
        with open(f'{self.tf_out_dir}/users.tf', 'w+') as f:
            f.write(out_str)
        
        return out_str
    
    def create_users_sql(self):
        """
        Add users to users.sql
        user: {name: None, warehouse: None, namespace: None}
        """
        
        out_str = ""
        
        out_str = self.create_sql('users.sql', user_template_sql, self.users, ['name', 'warehouse', 'namespace', 'default_role'])
        print(out_str)
        
        return out_str
    
    def create_grants_file(self):
        out_str = ""
        out_str += self.create_grants_sql(mode='schema')
        out_str += self.create_grants_sql(mode='users')
        
        with open(f'{self.sql_out_dir}/grants.sql', 'w+') as f:
            f.write(out_str)
        
        return out_str

    def create_main_tf(self): 
        """
        create terraform main.tf
        """
        
        out_str = main_template_tf.render(acct=self.account_info['name'], region=self.account_info['region']) + "\n"
        
        out_str += self.create_warehouses_tf()
        
        with open(f'{self.tf_out_dir}/main.tf', "w") as f:
            f.write(out_str)
        
        return out_str
    
    def create_main_sql(self, *args, **kwargs):
        out_str = """"""
        for arg in args:
            out_str += arg + "\n"
        with open(f'{self.sql_out_dir}/main.sql', "w") as f:
            f.write(out_str)
        
        return out_str
            
        
    def convert_sql(self, sql_syntax):
        """
        convert a query from another syntax to snow sql
        """
        pass
    
    @staticmethod
    def create_dirs(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def main(self):
        """
        All functionality triggered from here.
        """
        # --------------------- DOC CREATION --------------------- #
        for path in [self.tf_out_dir, self.sql_out_dir]:
            if not os.path.exists(path):
                self.create_dirs(path)
        
        # Warehouses
        wh_tf = self.create_warehouses_tf()
        wh_sql = self.create_warehouses_sql()
        
        # DBs
        db_tf = self.create_databases_tf()
        db_sql = self.create_databases_sql()
        
        # Roles
        role_tf = self.create_roles_tf()
        role_sql = self.create_roles_sql()

        # Schemas
        schema_tf = self.create_schemas_tf()
        schema_sql = self.create_schemas_sql()
        
        # Users
        user_tf = self.create_users_tf()
        user_sql = self.create_users_sql()
        
        # Main files
        main_tf = self.create_main_tf()
        main_sql = self.create_main_sql(wh_sql, db_sql, role_sql, schema_sql, user_sql)
        
        # Queries
        # TODO
        
        # DDLs
        # TODO
      

# In[13]:


def toboggan():
    print("\nTOBOGGAN: Automating your Snowflake Migration.\n")
    intake = Intake()
    intake.main()
    output = create_output(intake).main()
    print("Complete.")

# In[14]:


# doc_test = doc_creation(holder)
# doc_test.main()

# In[ ]:


if __name__ == '__main__':
    toboggan()
