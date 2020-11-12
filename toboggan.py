#!/usr/bin/env python
# coding: utf-8

# In[10]:


import jinja2
import json
import re
import os
import snowflake as sf
from sqlalchemy import create_engine
from templates.templates import *

# #### TODO:
# - Create more robust Edit Mode to add resources or change existing associations.
# - Create integrations, pipes, shares intake and creation.
# - Create streams, and tasks intake and creation.
# - Create import from query logic.
# - Remove Terraaform components.
# - Use decorators to print out_str.
# - Create query converter from athena, mysql, postgres and terradata.

# In[11]:


class Toboggan:
    """
    self contained reader + writer class for snowflake infra
    """
    def __init__(self):
        self.sep = '-' * 35
        self.warehouses = []
        self.default_roles = [{"name":"PUBLIC", "comment":"Pseudo-role that is automatically granted to every user and every role in your account. The PUBLIC role can own securable objects, just like any other role; however, the objects owned by the role are, by definition, available to every other user and role in your account.This role is typically used in cases where explicit access control is not needed and all users are viewed as equal with regard to their access rights."},
                              {"name":"ACCOUNTADMIN", "comment":"Role that encapsulates the SYSADMIN and SECURITYADMIN system-defined roles. It is the top-level role in the system and should be granted only to a limited/controlled number of users in your account. This role alone is responsible for configuring parameters at the account level. Users with the ACCOUNTADMIN role can view and operate on all objects in the account, can view and manage Snowflake billing and credit data, and can stop any running SQL statements."},
                              {"name":"SECURITYADMIN", "comment":"Role that can manage any object grant globally, as well as create, monitor, and manage users and roles. More specifically, this role is granted the MANAGE GRANTS security privilege to be able to modify any grant, including revoking it. Inherits the privileges of the USERADMIN role via the system role hierarchy (e.g. USERADMIN role is granted to SECURITYADMIN)."},
                              {"name":"USERADMIN", "comment":"Role that is dedicated to user and role management only. More specifically, this role is granted the CREATE USER and CREATE ROLE security privileges. Can create and manage users and roles in the account (assuming that ownership of those roles or users has not been transferred to another role)."},
                              {"name":"SYSADMIN", "comment":"Role that has privileges to create warehouses and databases (and other objects) in an account. If, as recommended, you create a role hierarchy that ultimately assigns all custom roles to the SYSADMIN role, this role also has the ability to grant privileges on warehouses, databases, and other objects to other roles."}
                             ]
        self.access_types = ["USAGE: Enables using a virtual warehouse and executeing queries on the schema.", 
                             "ALL: Grants all privileges, except OWNERSHIP, on the schema.",
                             "CANCEL: Return to roles."]
        
        self.data_types = [{"name":"NUMBER", "desc":"Used to store whole numbers. Has default precision and scale of 38 and 0 respectively."},
                           {"name":"FLOAT", "desc":"Snowflake employs double-precision IEEE 754 floating-point numbers. It also supports special values like NaN (Not a Number), inf (infinity) and -inf(negative infinity)."},
                           {"name":"VARCHAR", "desc":"It holds Unicode characters and has a maximum length of 16 MB. Some BI/ETL tools may initialize the maximum length of the VARCHAR data in storage or in memory."},
                           {"name":"BINARY", "desc":"The BINARY data type does not have the concept of Unicode characters, so its length is always measured in bytes. The maximum length is 8 MB."},
                           {"name":"BOOLEAN", "desc":"has 2 values TRUE or FALSE. It may also have an “unknown” value, which is displayed by NULL."},
                           {"name":"DATE", "desc":"Snowflake provides support for a DATE data type (with no time elements). It allows dates in the most common forms (YYYY-MM-DD, DD-MON-YYYY, etc.)."},
                           {"name":"TIME", "desc":"Snowflake provides support for a TIME data type in the form of HH:MM:SS. It also supports an optional precision parameter for fractional seconds. By default, the precision is 9. All TIME values should lie between 00:00:00 and 23:59:59.999999999."},
                           {"name":"TIMESTAMP", "desc":"TIMESTAMP is a user-specified alias for one of the TIMESTAMP_* variants. Every operation where TIMESTAMP is employed, the associated TIMESTAMP_* variation is used. This data type is never stored in tables."},
                           {"name":"VARIANT", "desc":"It is a universal data type, which can be used to store values of any other type, including OBJECT and ARRAY. It can store data up to a maximum size of 16 MB."},
                           {"name":"OBJECT", "desc":"It is used to store collections of key-value pairs, where the key will be a non-empty string and the value is of VARIANT type. Currently, Snowflake does not support explicitly-typed objects."},
                           {"name":"ARRAY", "desc":"It is used to display dense and sparse arrays of arbitrary size. An index is a non-negative integer (up to 2^31-1) and values are of VARIANT type. Currently, Snowflake does not provide support for fixed-size arrays or arrays with values of a specific non-VARIANT type."},
                           {"name":"GEOGRAPHY", "desc":"models Earth as if it were a perfect sphere. It follos the WGS 84 standard."}]
        
        self.roles = self.default_roles.copy()
        self.databases = []
        self.schemas = []
        self.tables = []
        self.users = []
        self.queries = []
        self.namespaces = []
        self.storage_integrations = []
        self.stages = []
        self.pipes = []
        self.streams = []
        self.tasks = []
        self.arns = []
        
        self.account_info = {}
        
    ########################################## UTILITIES ##########################################
    @staticmethod
    def section(func):
        def inner(*args, **kwargs):
            print("#" * 50)
            func(*args, **kwargs)
            print("\n")
        return inner
    
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
    def dedupe_dict_list(l):
        deduped = [dict(t) for t in {tuple(d.items()) for d in l}]
        return deduped
    
    @staticmethod
    def create_dirs(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            
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
    
    @staticmethod
    def yes_no(q):
        while True:
            ans = input(f"\n{q} y/n\n")
            if ans.lower() in ['yes', 'y']:
                return True
            elif ans.lower() in ['n', 'no']:
                return False
            else:
                print('\nPlease use yes, y, no, or n\n')
                continue
    
    def choose_owner(self):
        while True:
            owner = self.make_choices(self.role_names, f"What role should own this object?", mode='help')
            if owner == 'HELP':
                print("\nChoose a what role should be used when creating or accessing this object.")
            elif owner == 'CANCEL':
                print("\nObject must have an owner role associated with it.")
            else:
                return owner
    
    def set_out_dirs(self, mode=None):
        """
        Get input and create in_out_path.
        """
        while True:
            self.in_out_path = input("\nWhat directory would you like to read from and save files to? Use relative or full path. Default is working dir. Dir should have extra directories with import files if present or else they will be created in dir.\n")
            if self.in_out_path.lower() in ["default", ""]:
                self.in_out_path = "."

            self.tf_out_dir = input(f"\nWhere would you like your terraform files to read from and output to within {self.in_out_path}? Use relative path from master dir where toboggan is running. Default dir name if tf/\n")
            if self.tf_out_dir.lower() in ["default", ""]:
                self.tf_out_dir = "tf"

            self.sql_out_dir = input(f"\nWhere would you like your sql files to read from or output to within {self.in_out_path}? Use relative path from master dir where toboggan is running. Default dir name sql/\n")
            if self.sql_out_dir.lower() in ["default", ""]:
                self.sql_out_dir = "sql"

            self.json_out_dir = input(f"\nWhere would you like your json files to read from or output to within {self.in_out_path}? Use relative path from master dir where toboggan is running. Default dir name json_files/\n")
            if self.json_out_dir.lower() in ["default", ""]:
                self.json_out_dir  = "json_files"
            
            if mode:
                try:
                    f = []
                    for (dirpath, dirnames, filenames) in os.walk(f"{self.in_out_path}/{self.json_out_dir}"):
                        f.extend(filenames)
                    if f:
                        print(f"\nFound existing files to use for import in {self.in_out_path}/{self.json_out_dir}:")
                        for file in f:
                            print(file)
                        break
                    else:
                        ans = self.yes_no(f"No files in {self.in_out_path}/{self.json_out_dir} to import. Re enter paths?")
                        if ans:
                            continue
                        else:
                            break
                except Exception as e:
                    print(e)
                    ans = self.yes_no(f"{self.in_out_path}/{self.json_out_dir} does not exist. No import will be possible from this location. Should it be created?")
                    if ans:
                        continue
                    else:
                        break
            else:
                break
        
        for folder in [self.tf_out_dir, self.sql_out_dir, self.json_out_dir]:
            self.create_dirs(f"{self.in_out_path}/{folder}")
            
    def read_json(self, file_name):
        out = []
        if os.path.exists(f"{self.in_out_path}/{self.json_out_dir}/{file_name}.json"):
            with open(f"{self.in_out_path}/{self.json_out_dir}/{file_name}.json", "r") as f:
                out = json.load(f)
                
            if not out:
                print(f"No data in {file_name}.json.")
                out = []
                      
        else:
            print(f"\nNo file named {file_name}.json in {self.in_out_path}.")
        
        return out
    
    def read_snowflake(self, resource_name):
        query = f"SHOW {resource_name.upper()};"
        results = self.run_queries(query, results_mode=True)
    
        return results
    
    def write_tf(self, filename, out_str):
        with open(f'{self.in_out_path}/{self.tf_out_dir}/{filename}.tf', 'w+') as f:
            f.write(out_str)
    
    def write_json(self, file_name, data):
        with open(f"{self.in_out_path}/{self.json_out_dir}/{file_name}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    def write_sql(self, file_name, data):
        with open(f"{self.in_out_path}/{self.sql_out_dir}/{file_name}.sql", 'w') as f:
            f.write(data)
            
    ########################################## INTAKE ##########################################
    
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
            ans = self.yes_no("Do you want to add a warehouse?")
            if ans:
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
                
            else:
                if len(warehouses) < 1:
                    print("\nYou have to add at least one warehouse.\n")
                else:
                    break
            
            self.warehouse_names = [x['name'] for x in warehouses]
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
            ans = self.yes_no("Do you want to add a role?")
            
            if ans:
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
                    
            else:
                if len(roles) == 0:
                    print("\nUsing default roles only.\n")
                break
            
            self.role_names = [x['name'] for x in roles]

        return roles
    
    def intake_databases(self):
        """
        databases: list :list of databases or empty list
        returns: list : list of databases populated with at least 1 database
        """
        databases = self.databases.copy()
        print(f"\n{self.sep}DATABASES{self.sep}\n")
        print("A database is a logical grouping of schemas. Each database belongs to a single Snowflake account.\n")
        
        while True:
            ans = self.yes_no("Do you want to add a database?")
            if ans:
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
                
            else:
                if len(databases) < 1:
                    print("You have to add at least one database.")
                    continue
                else:    
                    break

        self.database_names = [x['name'] for x in databases]
        return databases

    def intake_schemas(self):
        """
        schemas: list of schemas or empty list
        returns: list : list of schemas populated with at least 1 schema
        """
        schemas = self.schemas.copy()
        print(f"\n{self.sep}SCHEMAS{self.sep}\n")
        print("""A schema is a logical grouping of database objects (tables, views, etc.). Each schema belongs to a single database.\n""")

        while True:
            ans = self.yes_no("Do you want to add a schema?")
            if ans:
                name = self.clean_text(input("\nWhat is the schema name?\n"), mode='upper')
                if name in [x['name'] for x in schemas]:
                    print("\nSchema already added, please use unique names.\n")
                    continue
                elif name == '':
                    print("\nPlease use valid characters.\n")
                    continue

                comment = input(f"\nLeave a descriptive comment to describe {name}:\n")
                
                # DATABASE SELECTION
                databases = []
                while True:
                    out_dict = {'name':name, 'comment':comment, 'database': None, 'namespace': '', 'usage_access':[], 'all_access':[]}
                    ans = self.yes_no(f"Do you want to add {name} to a database?")
                    if ans:
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
                        out_dict['namespace'] = f"{database}.{name}"

                    else:
                        if len(databases) < 1:
                            print(f"\nYou must add {name} to at least 1 database.\n")
                            continue
                        else:
                            break
                    
                    #ROLE SELECTION
                    roles = []
                    while True:
                        ans = self.yes_no(f"Do you want to add a role to access objects in {database}.{name}?")
                        
                        if ans:
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

                        else:
                            break

                    schemas.append(out_dict)
                    print(f"\nCreated schema:")
                    for k,v in out_dict.items():
                        print(f"{k}: {v}")

            else:
                break

        self.schema_names = [x['name'] for x in schemas]
        self.namespaces = [x['namespace'] for x in schemas]
        return schemas

    def intake_users(self):
        """
        users: list of users or empty list
        returns: list : list of users populated with at least 1 user
        """
        print(f"\n{self.sep}USERS{self.sep}\n")
        print("A user identity recognized by Snowflake, whether associated with a person or program.\n")
        users = self.users.copy()
        while True:
            ans = self.yes_no("Do you want to add a user?")
            if ans:
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
                    ans = self.yes_no(f"Do you want to add {name} to a role?")
                    if ans:
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
                    else:
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
                              
            else:
                break

        self.user_names = [x['name'] for x in users]
        return users
    
    def add_namespaces(self, name):
        namespaces = []
        while True:
            ans = self.yes_no(f"Do you want to add {name} to a namespace?")
            
            if ans:
                namespace = self.make_choices(self.namespaces, f"Which namespace should {name} be added to?", mode='help')
                if namespace == "HELP":
                    print("Choose a database and schemas (namespace) that the table should belong to.")
                elif namespace == "CANCEL":
                    continue
                else:
                    namespaces.append(namespace)
                    print(f"Added {name} to {namespace}.")
                    continue
            else:
                if len(namespaces) > 0:
                    break
                else:
                    print("\nTable must belong to at least 1 namespace.")
                    continue
            
        return namespaces

    def add_columns(self, name):
        columns = []
        while True:
            ans = self.yes_no(f"Do you want to add a column to {name}?")
            
            if ans:
                out_dict = {"column_name": None, "column_type": None}
                column_name = self.clean_text(input("\nWhat is the column name?\n"), mode='upper')
                if column_name in [x['column_name'] for x in columns]:
                    print("\nColumn already added, please use unique names.\n")
                    continue
                elif column_name == '':
                    print("\nPlease use valid characters.\n")
                    continue
                else:
                    column_type = self.make_choices([x['name'] for x in self.data_types], f"What type of column should {column_name} be?")
                    if column_type == 'HELP':
                        print(f"{self.set}DATA TYPES{self.sep}")
                        print("These represent the most basic data types (though there are others as you can access in the docs here: https://docs.snowflake.com/en/sql-reference/data-types.html)")
                        for x in self.data_types:
                            print(f"{x['name']}: {x['desc']}")
                        continue
                    elif column_type == 'CANCEL':
                        continue
                    else:
                        out_dict['column_name'] = column_name
                        out_dict['column_type'] = column_type
                
                        columns.append(out_dict)
                        print(f"Added {column_name} to {name}.")
                        print(f"Existing columns: {columns}")

            else:
                if len(columns) > 0:
                    break
                else:
                    print("\nTable must least 1 column.")
                    continue
            
        return columns
    
    def intake_tables(self):
        print(f"\n{self.sep}TABLES{self.sep}\n")
        print("Add table objects.\n")
        tables = self.tables.copy()
        while True:
            ans = self.yes_no(f"Do you want to add a table?")
            
            if ans:
                out_dict = {"name": "", "namespaces": [], "columns": [], "comment": ""}
                name = self.clean_text(input("\nWhat is the table name?\n"), mode='upper')
                if name in [x['name'] for x in tables]:
                    print("\nTable already added, please use unique names.\n")
                    continue
                elif name == '':
                    print("\nPlease use valid characters.\n")
                    continue
                else:
                    namespaces = self.add_namespaces(name)
                    columns = self.add_columns(name)
                    comment = input(f"\nLeave a descriptive comment to describe {name}:\n")

                    out_dict['name'] = name
                    out_dict['namespaces'] = namespaces
                    out_dict['columns'] = columns
                    out_dict['comment'] = comment

                    tables.append(out_dict)
                    
            else:
                break
                
        return tables
    
    def add_integration_locations(self, mode="allowed", cloud="s3"):
        """
        STORAGE_ALLOWED_LOCATIONS = ('<cloud>://<bucket>/<path>/', '<cloud>://<bucket>/<path>/')
        STORAGE_BLOCKED_LOCATIONS = ('<cloud>://<bucket>/<path>/', '<cloud>://<bucket>/<path>/')
        """
        out_list = []
        while True:
            ans = self.yes_no(f"Would you like to add a blob location to the {mode} storage locations? Default is '*' for allowed and None for blocked.")
            if ans:
                int_name = input("What is the storage bucket and path location? ex: bucket_or_container/dir/subdir/\n")
                int_str = f"'{cloud}://{int_name}/'"
                if int_str[-1] != '/': int_str += '/'
                if int_str in out_list:
                    print(f"\n{int_str} already present. Please use unique paths.\n")
                    continue
                out_list.append(int_name)
                print(f"Added {int_name} to integrations.")
                    
            else:
                return out_list
    
    def intake_storage_integrations(self):
        """
        CREATE [ OR REPLACE ] STORAGE INTEGRATION [IF NOT EXISTS]
          <name>
          TYPE = EXTERNAL_STAGE
          cloudProviderParams
          ENABLED = { TRUE | FALSE }
          STORAGE_ALLOWED_LOCATIONS = ('<cloud>://<bucket>/<path>/', '<cloud>://<bucket>/<path>/')
          [ STORAGE_BLOCKED_LOCATIONS = ('<cloud>://<bucket>/<path>/', '<cloud>://<bucket>/<path>/') ]
          [ COMMENT = '<string_literal>' ]
        """
        print(f"\n{self.sep}STORAGE INTEGRATION{self.sep}\n")
        print("Add storage integration objects.\n")
        storage_integrations = self.storage_integrations.copy()
        while True:
            ans = self.yes_no("Do you want to add a storage integration?")
            
            if ans:
                out_dict = {"name": "",
                            "cloud": "",
                            "integration_str": "",
                            "enabled": "TRUE",
                            "storage_allowed_locations": [],
                            "storage_blocked_locations": [],
                            "storage_allowed_locations_str": None,
                            "storage_blocked_locations_str": None,
                            "comment": None
                           }
                
                name = self.clean_text(input("\nWhat is the storage integration name?\n"), mode='upper')
                if name in [x['name'] for x in storage_integrations]:
                    print("\nIntegration already added, please use unique names.\n")
                    continue
                elif name == '':
                    print("\nPlease use valid characters.\n")
                    continue
                else:
                    out_dict['name'] = name
                    cloud = self.make_choices(['AWS', 'AZURE'], "What cloud should this integration use?")
                    if cloud == "AWS":
                        integration_str = input("What is the storage aws role arn from AWS? (ex: arn:aws:iam::{account_number}:role/{role_name})\n")
                        self.arns.append(integration_str)
                        print(f"Using arn: {integration_str}.")
                    else:
                        print("Azure not supported yet.")
                        continue
                        #cloud_account_number = input("What is your Azure Tenant ID? (ex: 123456789, AZURE: aZZZZZZZ-YYYY-HHHH-GGGG-abcdef569123)\n")

                    out_dict['cloud'] = cloud
                    out_dict['integration_str'] = integration_str

                    allowed_locations = self.add_integration_locations(mode="allowed")
                    if allowed_locations:
                        allowed_locations_str = "(" + ', '.join([f"'{z}'" for z in allowed_locations]) + ")"
                    else:
                        allowed_locations_str = "('*')"

                    blocked_locations = self.add_integration_locations(mode="blocked")
                    if blocked_locations:
                        blocked_locations_str = "(" + ', '.join([f"'{z}'" for z in blocked_locations]) + ")"
                    else:
                        blocked_locations_str = None

                    out_dict['storage_allowed_locations'] = allowed_locations
                    out_dict['storage_blocked_locations'] = blocked_locations
                    out_dict['storage_allowed_locations_str'] = allowed_locations_str
                    out_dict['storage_blocked_locations_str'] = blocked_locations_str

                    enabled = self.make_choices(['TRUE', 'FALSE'], "Should the integration be enabled?")
                    out_dict['enabled'] = enabled
                    comment = input(f"\nLeave a descriptive comment to describe {name}:\n")
                    out_dict['comment'] = comment if comment else None
                    storage_integrations.append(out_dict)
            else:
                return storage_integrations

    def intake_stages(self):
        """
        https://docs.snowflake.com/en/user-guide/data-load-s3-create-stage.html
        
        CREATE OR REPLACE stage {{name}}
         storage_integration = {{integration}}
         url='{{url}}'
         file_format = (TYPE = {{file_format}});
         
        """
        print(f"\n{self.sep}EXTERNAL STAGES{self.sep}\n")
        print("Add storage external stage objects.\n")
        stages = self.stages.copy()
        while True:
            ans = self.yes_no("Do you want to add a stage?")
            
            if ans:
                out_dict = {"name": "",
                            "integration": "",
                            "url": "",
                            "file_format": "",
                            "database_name": "",
                            "schema_name": ""
                           }
                
                name = self.clean_text(input("\nWhat is the external stage name?\n"), mode='upper')
                
                if name in [x['name'] for x in stages]:
                    print("\nIntegration already added, please use unique names.\n")
                    continue
                elif name == '':
                    print("\nPlease use valid characters.\n")
                    continue
                else:
                    out_dict['name'] = name
                    
                    integration = self.make_choices(self.storage_integration_names, "What is the storage integration name?", mode="help")
                    out_dict['integration'] = integration
                    
                    url = input(f"What is the url path to the directory (s3://bucket/dir/subdir; azure://bucket/dir/subdir)")
                    out_dict['url'] = url
                    
                    file_format = self.make_choices(['PARQUET', 'JSON', 'AVRO', 'CSV', 'ORC', 'XML'], f"What is the file type for {name}?")
                    out_dict['file_format'] = file_format
                    
                    namespace = self.make_choices(self.namespaces, "Which namespace should the stage be created under?")
                    database_name = namespace.split(".")[0]
                    schema_name = namespace.split(".")[1]
                    
                    out_dict['database_name'] = database_name
                    out_dict['schema_name'] = schema_name
                    
                    stages.append(out_dict)
            else:
                return stages
    
    def intake_pipes(self):
        """
         create or replace pipe {{name}} auto_ingest={{auto_ingest}} as
            copy into {{namespace}} {{columns}}
            from (
              {{query}} FROM @{{stage}})
            file_format = (type = '{{file_format}}');
        """
        print(f"\n{self.sep}PIPES{self.sep}\n")
        print("Add pipe objects.\n")
        pipes = self.pipes.copy()
        while True:
            ans = self.yes_no("Do you want to add a pipe?")
            
            if ans:
                out_dict = {
                            "name": "",
                            "auto_ingest": "",
                            "namespace": "",
                            "query": "",
                            "stage": "",
                            "file_format": "",
                            "columns": [],
                            "column_str": ""
                           }
                
                name = self.clean_text(input("\nWhat is the pipe name?\n"), mode='upper')
                
                if name in [x['name'] for x in pipes]:
                    print("\nPipe already added, please use unique names.\n")
                    continue
                elif name == '':
                    print("\nPlease use valid characters.\n")
                    continue
                else:
                    out_dict['name'] = name
                    
                    stage = self.make_choices(self.stage_names, "What is the stage name?", mode="help")
                    out_dict['stage'] = stage
                    
                    auto_ingest = self.make_choices(['TRUE', 'FALSE'], f"Should auto-ingest be enabled for this pipe?")
                    out_dict['auto_ingest'] = auto_ingest
                    
                    table_name = self.make_choices(self.table_names, f"Which table should this pipe attach to?")
                    
                    table = next((item for item in self.tables if item["name"] == table_name), None)
                    
                    if table == None:
                        continue
                    
                    namespace = self.make_choices(table['namespaces'], f"What database and schema does {name} belong to?")
                    
                    full_namespace = f"{namespace}.{table_name}"
                    out_dict['namespace'] = full_namespace
                    
                    out_dict['columns'] = table['columns']

                    out_dict['column_str'] = "(" + ', '.join([f"{x['column_name']}" for x in table['columns']]) + ")"
                    
                    query = input(f"What is the query you'd like to run in the pipe definition?")
                    out_dict['query'] = query
                    
                    file_format = self.make_choices(['PARQUET', 'JSON', 'AVRO', 'CSV', 'ORC', 'XML'], f"What is the file type for {name}?")
                    out_dict['file_format'] = file_format
                    
                    pipes.append(out_dict)
            else:
                return pipes
    
    def intake_streams(self):
        pass
    
    def intake_tasks(self):
        pass
    
    def choose_mode(self):
        while True:
            mode = self.make_choices(['CREATE', 'IMPORT'], "Which mode would you like to run in?", mode='help')
            if mode == 'HELP':
                print("CREATE: Create a brand new set of resources (warehouses, dtabases, roles, schemas, users) from scratch.")
                print("IMPORT: Use the the json files in the self.json_out_dir directory to import existing resources.")
                continue
            elif mode == 'CANCEL':
                print("Must choose to either import or create new resources.")
                continue
            else:
                return mode
    
    def select_resource_name(self, resource, edit_type, l):
        while True:
            resource = self.make_choices(l, f"Which {resource.lower()} would you like to {edit_type.lower()}?", mode='help')
            if resource == 'HELP':
                print(f"Select a resource to {edit_type.lower()}.")
                continue
            elif resource == 'CANCEL':
                return False
            else:
                return resource
            
    def delete_resource(self, resource_name, in_list, key_field, change_type='delete', match=False, nested=False, preserve=True):
        i = 0
        for item in in_list:
            if nested:
                for nested_item in item[key_field]:
                    if match:
                        if resource_name in nested_item:
                            item[key_field].remove(nested_item)
                            print(f"Deleted {resource_name} in {item}.\n")
                    else:
                        if nested_item == resource_name:
                            item[key_field].remove(nested_item)
                            print(f"Deleted {resource_name} in {item}.\n")
                            
            if not preserve:
                if len(item[key_field]) < 1:
                    del in_list[i]
                 
            else:
                if match:
                    if change_type.lower() == 'null':
                        if resource_name in item[key_field]:
                            print(f"Changed {resource_name} to null in {item}.")
                            in_list[i][key_field] = ''


                    else:
                        if resource_name in item[key_field]:
                            print(f"Deleted {resource_name} in {item}.\n")
                            del in_list[i]


                else:
                    if change_type.lower() == 'null':
                        if item[key_field] == resource_name:
                            print(f"Changed {resource_name} to null in {item}.")
                            in_list[i][key_field] = ''


                    else:
                        if item[key_field] == resource_name:
                            print(f"Deleted {resource_name} in {item}.\n")
                            del in_list[i]


            i+=1
        return in_list
    
    def intake_changes(self):
        print(f"\n{self.sep}EDIT RESOURCES{self.sep}\n")
        print("Add or Delete any existing resources from the templates.\n")
        while True:
            ans = self.yes_no(f"Would you like to add or delete any resources?")
            if ans:
                self.warehouse_names = [x['name'] for x in self.warehouses]
                self.database_names = [x['name'] for x in self.databases]
                self.schema_names = [x['name'] for x in self.schemas]
                self.namespaces = [x['namespace'] for x in self.schemas]
                self.role_names = [x['name'] for x in self.roles]
                self.user_names = [x['name'] for x in self.users]
                self.table_names = [x['name'] for x in self.tables]
                self.storage_integration_names = [x['name'] for x in self.storage_integrations]
                self.stage_names = [x['name'] for x in self.stages]

                choice = self.make_choices(['WAREHOUSES','DATABASES','ROLES','SCHEMAS','USERS', 'TABLES', 'INTEGRATIONS', 'STAGES', 'PIPES', 'SHARES'], "Which objects would you like to review?", mode="help")
                if choice == "HELP":
                    print("\nChoose the type of object you'd like to go back and add to or delete from.\n")
                    continue
                elif choice == "CANCEL":
                    continue
                else:
                    edit_type = self.make_choices(['ADD','DELETE'], "Which action do you want to take?", mode='help')
                    if edit_type == 'HELP':
                        print("You can add a resource, delete a resource, or edit the naming of an existing resource. Will not drop actual resources, only from the creation scripts.")
                        continue
                    elif edit_type == 'CANCEL':
                        continue

                    if choice == 'WAREHOUSES':
                        if edit_type == 'ADD':
                            self.warehouses = self.intake_warehouses()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.warehouse_names)
                            if not resource_name:
                                continue
                            self.warehouses = self.delete_resource(resource_name, self.warehouses, 'name')
                            self.users = self.delete_resource(resource_name, self.users, 'warehouse', change_type='null', match=True)

                    elif choice == 'DATABASES':
                        if edit_type == 'ADD':
                            self.databases = self.intake_databases()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.database_names)
                            if not resource_name:
                                continue
                            self.databases = self.delete_resource(resource_name, self.databases, 'name')
                            self.schemas = self.delete_resource(resource_name, self.schemas,'database', match=True)
                            self.users = self.delete_resource(resource_name, self.users, 'namespace', change_type='null', match=True)
                            self.tables = self.delete_resource(resource_name, self.tables, 'namespaces', match=True, nested=True, preserve=False)
                            
                    elif choice == 'ROLES':
                        if edit_type == 'ADD':
                            self.roles = self.intake_roles()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.role_names)
                            if not resource_name:
                                continue
                            self.roles = self.delete_resource(resource_name, self.roles, 'name')
                            self.schemas = self.delete_resource(resource_name, self.schemas, 'usage_access', nested=True)
                            self.schemas = self.delete_resource(resource_name, self.schemas, 'all_access', nested=True)
                            self.users = self.delete_resource(resource_name, self.users, 'roles', nested=True)
                            self.users = self.delete_resource(resource_name, self.users, 'default_role',  change_type='null')

                    elif choice == 'SCHEMAS':
                        if edit_type == 'ADD':
                            self.schemas = self.intake_schemas()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.namespaces)
                            if not resource_name:
                                continue
                            self.schemas = self.delete_resource(resource_name, self.schemas, 'namespace')
                            self.users = self.delete_resource(resource_name, self.users, 'namespace', change_type='null', match=True)
                            self.tables = self.delete_resource(resource_name, self.tables, 'namespaces', match=True, nested=True, preserve=False)
                            
                    elif choice == 'USERS':
                        if edit_type == 'ADD':
                            self.users = self.intake_users()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.user_names)
                            if not resource_name:
                                continue
                            self.users = self.delete_resource(resource_name, self.users, 'name')

                    elif choice == 'TABLES':
                        if edit_type == 'ADD': 
                            self.tables= self.intake_tables()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.table_names)
                            if not resource_name:
                                continue
                            self.tables = self.delete_resource(resource_name, self.tables, 'name')
                            
                    elif choice == 'INTEGRATIONS':
                        if edit_type == 'ADD': 
                            self.storage_integrations = self.intake_storage_integrations()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.storage_integration_names)
                            if not resource_name:
                                continue
                            self.storage_integrations = self.delete_resource(resource_name, self.storage_integrations, 'name')
                            
                    elif choice == 'STAGES':
                        if edit_type == 'ADD':
                            self.stages = self.intake_stages()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.storage_stage_names)
                            if not resource_name:
                                continue
                            self.stages = self.delete_resource(resource_name, self.stages, 'name')
                            
                    elif choice == 'PIPES':
                        if edit_type == 'ADD':
                            self.pipes = self.intake_pipes()
                        elif edit_type == 'DELETE':
                            resource_name = self.select_resource_name(choice, edit_type, self.pipe_names)
                            if not resource_name:
                                continue
                            self.pipes = self.delete_resource(resource_name, self.pipes, 'name')
            else:
                break
    
    def intake_queries(self):
        pass
    
    ########################################## CREATE ##########################################
    
    def create_sql(self, filename, template, objects):
        out_str = ""
        
        for item in objects:
            out_str += template.render(item)
            
        self.write_sql(filename, out_str)
            
        return out_str
    
    def create_warehouses_tf(self):
        """
        Add warehouses to main.tf
        self.warehouses : {'name':warehouse, 'warehouse_size':warehouse_size, 'auto_resume':auto_resume, 'auto_suspend':auto_suspend, 'comment':comment}
        """
        
        out_str = ""
        
        for item in self.warehouses:
            out_str += warehouse_template_tf.render(item) + "\n"
        
        return out_str
    
    def create_warehouses_sql(self):
        """
        Add warehouses to warehouse.sql
        self.warehouses : {'name':warehouse, 'warehouse_size':warehouse_size, 'auto_resume':auto_resume, 'auto_suspend':auto_suspend, 'comment':comment}
         filename, template, objects, fields
        """
        
        out_str = "USE ROLE SYSADMIN;\n"
        out_str += self.create_sql('warehouses', warehouse_template_sql, self.warehouses)
        
        return out_str

    def create_databases_tf(self):
        """
        create roles.tf if not provided
        self.roles : [{'name': 'role_name', 'comment':'description'}]
        """
        
        blob = """"""
        
        for db in self.databases:
            blob += database_template_tf.render(name=db['name'], 
                                                comment=db['comment']
                                               )
                                
        out_str = database_template_tf.render(blob=blob)
        
        self.write_tf('databases', out_str)
            
        return out_str
            
    def create_databases_sql(self):
        """
        Create database.sql
        """
        out_str = "USE ROLE SYSADMIN;\n"
        
        out_str += self.create_sql('databases', database_template_sql, self.databases)
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

                for user in self.users:
                    if role['name'] in user['roles']:
                        out_dict['users'].append(user['name'])
                role_blob += role_insert_template_tf.render(role=out_dict['name'], comment=out_dict['comment'], users=out_dict['users']).replace("'",'"')
                                
        out_str = role_template_tf.render(role_blob=role_blob)
        
        self.write_tf('roles', out_str)
        
        return out_str
    
    def create_roles_sql(self):
        """
        Add roles to roles.sql
        """
        
        out_str = """USE ROLE ACCOUNTADMIN;\n"""
                
        out_str += self.create_sql('roles', role_template_sql, [role for role in self.roles if role['name'] not in [x['name'] for x in self.default_roles]])
        
        return out_str
    
    def create_grants_sql(self, mode='schema'):
        """
        Handle associating roles with correct schemas or users.
        """
        out_str = """USE ROLE SYSADMIN;"""
        
        
        sec_admin_stmts = []
        if mode == 'schema':
            for role in self.role_names:
                for schema in self.schemas:
                    if role in schema['all_access']:

                        out_str += f"\nGRANT USAGE ON DATABASE {schema['database']} TO ROLE {role};\n"
                        
                        out_str += f"\nGRANT ALL ON SCHEMA {schema['namespace']} TO ROLE {role};\n"
                        
                        sec_admin_stmts.append(f"GRANT ALL ON FUTURE TABLES IN SCHEMA {schema['database']}.{schema['name']} TO ROLE {role};")
                        
                    elif role in schema['usage_access']:
                        out_str += f"\nGRANT USAGE ON DATABASE {schema['database']} TO ROLE {role};\n"
                        out_str += f"\nGRANT USAGE ON SCHEMA {schema['namespace']} TO ROLE {role};\n"
    
                        sec_admin_stmts.append(f"GRANT SELECT ON FUTURE TABLES IN SCHEMA {schema['namespace']} TO ROLE {role};")
            
            out_str += "\nUSE ROLE SECURITYADMIN;\n"
            for s in sec_admin_stmts:
                out_str += s + "\n"
                                               
        else:
            for user in self.users:
                for role in user['roles']:
                    out_str += f"GRANT ROLE {role} to USER {user['name']};\n"
                out_string += f"GRANT USAGE, OPERATE ON WAREHOUSE {user['warehouse']} TO {user['name']};\n"
        
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
        
        self.write_tf('schemas', out_str)
        
        return out_str

    def create_schemas_sql(self):
        """
        Add schemas to schemas.sql
        """
        
        out_str = "USE ROLE SYSADMIN;\n"
        
        out_str += self.create_sql('schemas', schema_template_sql, self.schemas)
        
        return out_str

    def create_users_tf(self):
        """
        self.users : [{name: None, warehouse: None, namespace: None}]
        """
        
        user_blob = """"""
    
        for user in self.users:
            user_blob += user_insert_template_tf.render(name=user['name'], role=user['default_role'], namespace=user['namespace'], warehouse=user['warehouse']) + "\n"
                                
        out_str = user_template_tf.render(user_blob=user_blob)
        
        self.write_tf('users', out_str)
        
        return out_str
    
    def create_users_sql(self):
        """
        Add users to users.sql
        user: {name: None, warehouse: None, namespace: None}
        """
        
        out_str = "USE ROLE ACCOUNTADMIN;\n"
        
        out_str += self.create_sql('users', user_template_sql, self.users)
        
        return out_str
    
    def create_tables_sql(self):
        """
        Add users to tables.sql
        """
        
        out_str = """USE ROLE SYSADMIN;\n"""
        
        for table in self.tables:
            table_blob = """"""
            for column in table['columns']:
                table_blob += table_insert_template_sql.render(column_name=column['column_name'], column_type=column['column_type'])
            table_blob = table_blob[:-1]
            for namespace in table['namespaces']:
                out_str += table_template_sql.render(name=table['name'], namespace=namespace, table_blob=table_blob)
            
        self.write_sql('tables', out_str)
        
        return out_str
    
    def create_stages_sql(self):
        out_str = "USE ROLE SYSADMIN;\n"
        
        out_str += self.create_sql('stages', external_stage_template, self.stages)
        
        return out_str
    
    def create_pipes_sql(self):
        """
         create or replace pipe dev_pl_extract_reg_pipe auto_ingest=true as
            copy into "DEV_DB"."RAW_LAYER"."EXTRACT_REGISTRATION" (raw_variant, filename)
            from (
              SELECT *, metadata$filename FROM @dev_pl_extract_reg_stage)
            file_format = (type = 'parquet');
            
        create or replace pipe {{name}} auto_ingest={{auto_ingest}} as
            copy into {{namespace}} {{columns}}
            from (
              {{query}} FROM @{{stage}})
            file_format = (type = '{{file_format}}');
        """
        out_str = "USE ROLE SYSADMIN;\n"
        for pipe in self.pipes:
            out_str += pipe_template_sql.render(pipe)

        self.write_sql('pipes', out_str)
        return out_str
    
    def create_storage_integration_sql(self):
        """
        https://docs.snowflake.com/en/sql-reference/sql/create-storage-integration.html
        """
        out_str = "\nUSE ROLE SYSADMIN;\n"
        for integration in self.storage_integrations:
            if integration['cloud'] == "AWS":
                out_str += aws_storage_integration_template.render(integration)
            else:
                pass
                #TODO: AZURE
        self.write_sql('integrations', out_str)
        return out_str
    
    def create_main_sql(self, *args, **kwargs):
#         out_str = f"""USE ROLE {self.account_info['role']};"""
        print(f"\n{self.sep}MAIN SQL{self.sep}\n")
        out_str = f""""""
        for arg in args:
            out_str += arg + "\n"

        self.write_sql('main', out_str)
        
        print(out_str)
        return out_str
    
    def create_grants_file(self):
        out_str = ""
        out_str += self.create_grants_sql(mode='schema')
        out_str += self.create_grants_sql(mode='users')
        
        self.write_sql('grants', out_str)
        return out_str

    def create_main_tf(self): 
        """
        create terraform main.tf
        """
        
        out_str = main_template_tf.render(acct="YOUR_ACCT_NAME_HERE", region="YOUR_REGION_HERE")
        
        out_str += self.create_warehouses_tf()
        
        self.write_tf('main', out_str)
        
        return out_str
    
    def create_teardown_sql(self):
        out_str = "\nUSE ROLE ACCOUNTADMIN;\n"
        for warehouse in self.warehouses:
            out_str += teardown_template_sql.render(object_type="WAREHOUSE", name=warehouse['name'])
        
        for database in self.databases:
            out_str += teardown_template_sql.render(object_type="DATABASE", name=database['name'])
        
        for role in self.roles:
            if role['name'] not in [x['name'] for x in self.default_roles]:
                out_str += teardown_template_sql.render(object_type="ROLE", name=role['name'])
        
        for user in self.users:
            out_str += teardown_template_sql.render(object_type="USER", name=user['name'])
            
        for stage in self.stages:
            out_str += teardown_template_sql.render(object_type="STAGE", name=stage['name'])
            
        for pipe in self.pipes:
            out_str += teardown_template_sql.render(object_type="PIPE", name=pipe['name'])
        
        self.write_sql('teardown', out_str)
        
        return out_str
                
    def convert_sql(self, sql_syntax):
        """
        convert a query from another syntax to snow sql
        """
        pass
    
    ########################################## RUN ##########################################
    
    def run_queries(self, query, results_mode=False):
        if not self.account_info:
            self.account_info = self.intake_account_info()
        sfAccount = f"{self.account_info['name']}.{self.account_info['region']}"
        sfUser = f"{self.account_info['login']}"
        sfPswd = f"{self.account_info['password']}"

        conn_string = f"snowflake://{sfUser}:{sfPswd}@{sfAccount}/"

        engine = create_engine(conn_string)

        queries = query.split(";")
        queries = [query.strip() + ";" for query in queries if query]

        connection = engine.connect()
        results = []
        for query in queries:
            print(f"Attempting to run query: {query}")
            try:
                result = connection.execute(query)
                if results_mode:
                    for row in result:
                        row_as_dict = dict(row)
                        results.append(row_as_dict)
                        print(f"results: {row_as_dict}")

            except Exception as e:
                print(e)

        connection.close()
        engine.dispose()
    
    def intake(self):
        """
        Main function combining intake and output
        """
        
        # --------------------- INTAKE --------------------- #
        self.mode = self.choose_mode()
        
        if self.mode == 'IMPORT':
            print(f"\n{self.sep}IMPORT MODE{self.sep}\n")
            self.set_out_dirs(mode='import')
            import_mode = self.make_choices(['Import from sql connection to existing account.',
                                            f'Import from json files in {self.in_out_path}/{self.json_out_dir}/'],
                                           "Would you like to import from a snowflake account connection or json files?"
                                           )
            
            if import_mode == 'Import from sql connection to existing account.':
                self.warehouses = self.read_snowflake('warehouses')
                self.databases = self.read_snowflake('databases')
                self.roles = self.read_snowflake('roles')
                self.schemas = self.read_snowflake('schemas')
                self.users = self.read_snowflake('users')
                self.tables = self.read_snowflake('tables')
                self.storage_integrations = self.read_snowflake('integrations')
                self.stages = self.read_snowflake('stages')
                self.pipes = self.read_snowflake('pipes')
            else:
                self.warehouses = self.read_json('warehouses')
                self.databases = self.read_json('databases')
                self.roles = self.read_json('roles')
                self.schemas = self.read_json('schemas')
                self.users = self.read_json('users')
                self.tables = self.read_json('tables')
                self.storage_integrations = self.read_json('integrations')
                self.stages = self.read_json('stages')
                self.pipes = self.read_json('pipes')
            
            print(f"{self.sep}Existing Warehouses{self.sep}\n")
            for x in self.warehouses:
                print(json.dumps(x, indent=4))
                
            print(f"{self.sep}Existing Database{self.sep}\n")
            for x in self.databases:
                print(json.dumps(x, indent=4))
                
            print(f"{self.sep}Existing Roles{self.sep}\n")
            for x in self.roles:
                print(json.dumps(x, indent=4))

            print(f"{self.sep}Existing Schemas{self.sep}\n")
            for x in self.schemas:
                print(json.dumps(x, indent=4))

            print(f"{self.sep}Existing Users{self.sep}\n")
            for x in self.users:
                print(json.dumps(x, indent=4))
                
            print(f"{self.sep}Existing Tables{self.sep}\n")
            for x in self.tables:
                print(json.dumps(x, indent=4))
                
            print(f"{self.sep}Existing Integrations{self.sep}\n")
            for x in self.storage_integrations:
                print(json.dumps(x, indent=4))
            
            print(f"{self.sep}Existing Stages{self.sep}\n")
            for x in self.stages:
                print(json.dumps(x, indent=4))
                
            print(f"{self.sep}Existing Pipes{self.sep}\n")
            for x in self.pipes:
                print(json.dumps(x, indent=4))

        else:
            print(f"\n{self.sep}CREATE MODE{self.sep}\n")
            self.set_out_dirs()
            self.warehouses = self.intake_warehouses()
            self.roles = self.intake_roles()
            self.databases = self.intake_databases()
            self.schemas = self.intake_schemas()
            self.users = self.intake_users()
            self.tables = self.intake_tables()
            self.storage_integrations = self.intake_storage_integrations()
            self.stages = self.intake_stages()
            self.pipes = self.intake_pipes()
        
        # name updates
        self.warehouse_names = [x['name'] for x in self.warehouses]
        self.database_names = [x['name'] for x in self.databases]
        self.schema_names = [x['name'] for x in self.schemas]
        self.namespaces = [f"{x['name']}.{x['database']}" for x in self.schemas]
        self.role_names = [x['name'] for x in self.roles]
        self.user_names = [x['name'] for x in self.users]
        self.table_names = [x['name'] for x in self.tables]
        self.storage_integration_names = [x['name'] for x in self.storage_integrations]
        self.stage_names = [x['name'] for x in self.stages]
        self.pipe_names = [x['name'] for x in self.pipes]

        # EDIT MODE
        self.intake_changes()

    def create(self):
        # --------------------- DOC CREATION --------------------- #
        ans = self.yes_no("Would you like to create the associated documents (sql, tf, json) for your infrastructure?")
        if ans:
            # Warehouses
            self.wh_tf = self.create_warehouses_tf()
            self.wh_sql = self.create_warehouses_sql()
            self.write_json('warehouses', self.warehouses)

            # DBs
            self.db_tf = self.create_databases_tf()
            self.db_sql = self.create_databases_sql()
            self.write_json('databases', self.databases)

            # Roles
            self.role_tf = self.create_roles_tf()
            self.role_sql = self.create_roles_sql()
            self.write_json('roles', self.roles)

            # Schemas
            self.schema_tf = self.create_schemas_tf()
            self.schema_sql = self.create_schemas_sql()
            self.write_json('schemas', self.schemas)

            # Users
            self.user_tf = self.create_users_tf()
            self.user_sql = self.create_users_sql()
            self.write_json('users', self.users)

            # Tables
            self.table_sql = self.create_tables_sql()
            self.write_json('tables', self.tables)
            
            # Integrations
            self.integration_sql = self.create_storage_integration_sql()
            self.write_json('integrations', self.storage_integrations)
            
            # Stages
            self.stage_sql = self.create_stages_sql()
            self.write_json('stages', self.stages)

            # Pipes
            self.pipe_sql = self.create_pipes_sql()
            self.write_json('pipes', self.pipes)
            
            # Main files
            self.grants_sql = self.create_grants_sql()
            self.main_tf = self.create_main_tf()
            self.main_sql = self.create_main_sql(self.role_sql,
                                                 self.wh_sql,
                                                 self.db_sql,
                                                 self.schema_sql,
                                                 self.user_sql,
                                                 self.grants_sql,
                                                 self.table_sql,
                                                 self.integration_sql,
                                                 self.stage_sql,
                                                 self.pipe_sql
                                                )
            
            self.teardown_sql = self.create_teardown_sql()
        else:
            print("Files not created.\n")
        
        ans = self.yes_no("Would you like to run your main.sql file?")
        if ans:
            self.account_info = self.intake_account_info()
            self.run_queries(self.main_sql)
        else:
            print("Queries not run.\n")

# In[ ]:


if __name__ == '__main__':
    print("\nTOBOGGAN: Automating Snowflake Setup.\n")
    import time
    time.sleep(.1)
    T = Toboggan()
    T.intake()
    T.main_create()
    print("\nComplete.\n")

# In[ ]:



