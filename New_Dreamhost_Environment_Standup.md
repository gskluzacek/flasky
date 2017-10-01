# Overview
document the steps to create a new Dreamhost enviroment capable of serving a Flask web applicaiton

# Setup New User (optional)

1. log into the dreamhost web hosting control panel: https://panel.dreamhost.com
2. click Users / Manage Users
3. click the **Add A New User** button
4. choose the **Shell User** radio button
5. enter the unix userid: `flskusr`
6. check **Enhanced Security** checkbox: `yes`
7. enter the full name (or desc) of the userid: `<app-name> userid`
8. enter the desired password for the user (2x)

Click the **Add User** button

The users home directory will be: `/home/<userid>/`

# Create Sub-Domain

1. log into the dreamhost web hosting control panel: https://panel.dreamhost.com
2. click Domains / Manage Domains
3. click the **Add Hosting to a Domain / Sub-Domain** button
4. enter the sub-domain host: `komiclogr-dev.komicbox.com`
5. choose the **Remove WWW** radio button
6. From the drop down, select the user to run the domain under: either select the new user that was created above, 
select an existing user or selct _Create a New User (Recommended)_ : `flskusr`
7. enter the desired web directory: `/home/<user-name>/komiclogr-dev.komicbox.com/public`
8. PHP Mode `<leave default selection>`
9. check the **HTTPS:** checkbox: `yes`
10. leave the default **Automaticall upgrade PHP** checkbox selected: `yes`
11. check the **Extra Web Security** checkbox: `yes`
12. check the **Passenger** checkbox: `yes`

click the **Full host this domain** button 

# Setup Secure Hosting

1. log into the dreamhost web hosting control panel: https://panel.dreamhost.com
2. click Domains / Manage Domains
3. click the **Add** button for add a new SSL certificate with Let's Encrypt SSL
4. choose the domain / sub-domain: `komiclogr-dev.komicbox.com`
5. check the **I Agree** checkbox: `yes`

after verifying the _order total_ is $0.00, click the **Add Now** buton

# Setup Email Addresses

Set up 2 email address for the web application
* one email address to send emails from the application: `FLASKY_MAIL_SENDER`, `MAIL_USERNAME`
* and another email address for the default application admin: `FLASKY_ADMIN`

1. log into the dreamhost web hosting control panel: https://panel.dreamhost.com
2. click Mail / Manage Email
3. click the **Create New Email Address** button
4. enter the deisred email address (part before the `@`): `flask.app` / `flask.admin`
5. select the domain/sub-domain: `komiclogr-dev.komicbox.com`
6. enter a description for the mailbox name
7. enter a password for the mailbox (2x)
8. accecpt the defaults for the remaining fields

click the **Create Address** button


# Instal Custom Python 3.x
follow the instructions at: https://help.dreamhost.com/hc/en-us/articles/115000702772-Installing-a-custom-version-of-Python-3

_as of 28-SEP-2017, the above instructions are for python version 3.6.2, which worked very well._

example from `gstst` unix account
```
cd ~
mkdir tmp
cd tmp
wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tgz
tar zxvf Python-3.6.2.tgz
cd Python-3.6.2
./configure --prefix=$HOME/opt/python-3.6.2
make
make install
cd ~
opt/python-3.6.2/bin/python3 --version
nano .bash_profile
>>> add to following line to bottom of .bash_profile
>>>     export PATH=$HOME/opt/python-3.6.2/bin:$PATH
source .bash_profile
which python3
python3 --version
pip3 --version
```

_I'm thinking about not adding the python-3.6.2 directory to the `$PATH` in .bash_profie, but instead creating a separate
script in the applicaton home directroy and doing there._

# Setup a Virtual Environment
follow the instructions at: https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-Python-s-virtualenv-using-Python-3

## Install virtualenv
_see instructions above_ 

example from `gstst` unix account
```
pip3 install virtualenv
which virtualenv
which python3
```

## Create a New Virtual Environment
_refer to instrucations above_

example from `gstst` unix account
```
mkdir mywebsite.com
cd mywebsite.com/
virtualenv /home/gstst/mywebsite.com/venv-3.6 -p /home/gstst/opt/python-3.6.2/bin/python3

tree

./mywebsite.com/
|-- requirements.txt
`-- venv-3.6
    |-- bin
    |   |-- activate
    |   |-- activate.csh
    |   |-- activate.fish
    |   |-- activate_this.py
    |   |-- alembic
    |   |-- easy_install
    |   |-- easy_install-3.6
    |   |-- flask
    |   |-- mako-render
    |   |-- markdown_py
    |   |-- pip
    |   |-- pip3
    |   |-- pip3.6
    |   |-- python -> python3
    |   |-- python-config
    |   |-- python3
    |   |-- python3.6 -> python3
    |   `-- wheel
    |-- include
    |-- lib
    |   `-- python3.6
    `-- pip-selfcheck.json
```

_note: apparently, when you create a virtual environment, a symbolic link is create for `python` that points to 
`python3` and there are idential copies of pip named `pip` and `pip3`_

_also note: the above `tree` output was generated **after** the required packages weere installed to the virtual env._  

## Activating the new Virtual Environment

example from `gstst` unix account
```
cd mywebsite.com
source venv-3.6/bin/activate
```

not to deactive just enter `deactivate` from the command prompt.

## Install Required Packages

_make sure to active the Virtual Environment before starting_

example from `gstst` unix account
```
source venv-3.6/bin/activate
pip install -r requirements.txt
pip install ForgeryPy
pip list
```

# Create a MySQL database

## **IMPORTANT ISSUES**

### differences between local and hosted mysql behaviour was found

when creating a table with a column of the `TIMESTAMP` type with not-null set to true, _it appears that_ the 
local MySQL server automatically adds a default value of `CURRENT_TIMESTAMP` and `on update CURRENT_TIMESTAMP`

Howerver the hosted MySQL server does not _seem_ to have the same behavior. Short term fix is to alter the column:

`ALTER TABLE files CHANGE crt_dt TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;` 

**BUT,** there also appears to be a difference in the treatment of how the 2 instances handle columns that are
explicitly set to NULL

on the local MySQL server (version 5.7.15) this executes fine and will use the `CURRENT_TIMESTAMP` for the value
of the create date, despite it being explicitly set to `NULL`. The same insert statement on the DreamHost MySQL
server throws an error: `1048, "Column 'crt_dt' cannot be null"`

`insert into files (crt_dt, status, file_path, orig_file, default_discount) values(null, 'ok','blah','bogo',0.20);`  

apprently, there is a server setting called: `explicit_defaults_for_timestamp`. From the MySQL 5.6.x documentation
it defaults 0 (disabled). In the local MySQL instance it is disabled, but when I check the Dreamhost instance it
is set to 1 (enabled). The setting couldn't not be updated from the command line: 
`#1238 - Variable 'explicit_defaults_for_timestamp' is a read only variable`  

```
$ select @@explicit_defaults_for_timestamp;
>>> 1
$ insert into files (status, file_path, orig_file, default_discount) values('ok','blah','bogo',0.20);
>>> OK
$ insert into files (crt_dt, status, file_path, orig_file, default_discount) values(null, 'ok','blah','bogo',0.20);
>>> Error, crt_dt cannot be NULL
$ set explicit_defaults_for_timestamp 0;
$ insert into files (status, file_path, orig_file, default_discount) values('ok','blah','bogo',0.20);
>>> OK
$ insert into files (crt_dt, status, file_path, orig_file, default_discount) values(null, 'ok','blah','bogo',0.20);
>>> OK
```

the SQL emitted by SQL Alchemy does include the `crt_dt` column and it does set it to `NULL`

```
sqlalchemy.exc.IntegrityError: (pymysql.err.IntegrityError) (1048, "Column 'crt_dt' cannot be null")

[SQL: 'INSERT INTO files (crt_dt, status, file_path, orig_file, purch_dt, store, trans_num, default_discount, 
      tax_rate, pmt_meth, trans_total, sub_total, tax_total, discount_total, nei_trans_total, nei_sub_total, 
      nei_tax_total, nei_discount_total, notes) 
    VALUES (%(crt_dt)s, %(status)s, %(file_path)s, %(orig_file)s, %(purch_dt)s, %(store)s, %(trans_num)s, 
      %(default_discount)s, %(tax_rate)s, %(pmt_meth)s, %(trans_total)s, %(sub_total)s, %(tax_total)s, 
      %(discount_total)s, %(nei_trans_total)s, %(nei_sub_total)s, %(nei_tax_total)s, %(nei_discount_total)s, 
      %(notes)s)'
] [parameters: {'crt_dt': None, 'status': 'UPLOADED', 'file_path': 'input/invoice_mc_2017_05_21_A.txt', 
      'orig_file': 'test1.txt', 'purch_dt': datetime.date(2017, 5, 21), 'store': 'Modern Age Comics', 
      'trans_num': '0', 'default_discount': Decimal('0.20'), 'tax_rate': Decimal('0.07'), 
      'pmt_meth': 'Chase Visa Freedom', 'trans_total': None, 'sub_total': None, 'tax_total': None, 
      'discount_total': None, 'nei_trans_total': None, 'nei_sub_total': None, 'nei_tax_total': None, 
      'nei_discount_total': None, 'notes': None}
]

```

The long term work around may be to use `default=func.now()` on the column definition and possibly 
`onupdate=func.now()`

**UPDATE:**

Tested with the above work around and it has fixed the issue... 

Additonally the alter table statement mentioned above is not needed as default values are now specified for
both insert and update. 

the new SQL emitted:

```
2017-10-01 12:14:26,502 INFO sqlalchemy.engine.base.Engine 
  INSERT INTO files (
    crt_dt, status, file_path, orig_file, purch_dt, store, trans_num, default_discount, tax_rate, 
    pmt_meth, trans_total, sub_total, tax_total, discount_total, nei_trans_total, nei_sub_total, 
    nei_tax_total, nei_discount_total, notes
  ) VALUES (
    now(), %(status)s, %(file_path)s, %(orig_file)s, %(purch_dt)s, %(store)s, %(trans_num)s, 
    %(default_discount)s, %(tax_rate)s, %(pmt_meth)s, %(trans_total)s, %(sub_total)s, %(tax_total)s, 
    %(discount_total)s, %(nei_trans_total)s, %(nei_sub_total)s, %(nei_tax_total)s, %(nei_discount_total)s, 
    %(notes)s
  )
2017-10-01 12:14:26,502 INFO sqlalchemy.engine.base.Engine 
{
  'status': 'UPLOADED', 'file_path': 'input/invoice_mc_2017_05_21_A.txt', 'orig_file': 'fix_test.txt', 
  'purch_dt': datetime.date(2017, 5, 21), 'store': 'Modern Age Comics', 'trans_num': '0', 
  'default_discount': Decimal('0.20'), 'tax_rate': Decimal('0.0675'), 'pmt_meth': 'AmEx', 
  'trans_total': None, 'sub_total': None, 'tax_total': None, 'discount_total': None, 
  'nei_trans_total': None, 'nei_sub_total': None, 'nei_tax_total': None, 'nei_discount_total': None, 
  'notes': None
}
```


**SEE:**
* http://docs.sqlalchemy.org/en/rel_1_1/dialects/mysql.html#timestamp-columns-and-null
* http://docs.sqlalchemy.org/en/latest/core/defaults.html#sql-expressions
* https://dev.mysql.com/doc/refman/5.6/en/server-system-variables.html#sysvar_explicit_defaults_for_timestamp

## steps...

first create a hostname if one does not already exist

1. log into the dreamhost web hosting control panel: https://panel.dreamhost.com
2. click Goodies / MySQL Databases
3. click the **Add New Hostname** button
4. enter `mysql` into the hostname text field
5. select the domain/sub-domain from the dropdown

click the **Create this MySQL hostname now!** button

next, scroll down to the bottom of the page and enter the details for the new database

1. database name: `komiclogr-dev`
2. select the desired hostname from the dropdown: `mysql.komiclogr-dev.komicbox.com`
3. for the **First User** either select the desired db userid from the dropdown or select **create a new user now** option from the dropdown
4. enter the **New Username** for the database userid: `klogr_app_dev`
5. enter a password (2x)

click the **Add new database now!** button

## Command Line Access
`mysql -u klogr_app_dev -p -h mysql.komiclogr-dev.komicbox.com komiclogr_dev`

## Create test_tbl & Insert some data

```
mysql> create table test_tbl (id integer not null, usr_name varchar(30));
mysql> desc test_tbl;

+----------+-------------+------+-----+---------+-------+
| Field    | Type        | Null | Key | Default | Extra |
+----------+-------------+------+-----+---------+-------+
| id       | int(11)     | NO   |     | NULL    |       |
| usr_name | varchar(30) | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+

mysql> insert into test_tbl values(1, 'bob');
mysql> insert into test_tbl values(2, 'mike');
mysql> insert into test_tbl values(3, 'paul');
mysql> insert into test_tbl values(4, 'scott');

mysql> select * from test_tbl;

+----+----------+
| id | usr_name |
+----+----------+
|  1 | bob      |
|  2 | mike     |
|  3 | paul     |
|  4 | scott    |
+----+----------+
```




# Create the Necessary Files to Run the Flask Web Application

## .htaccess

mimimal `.htaccess` file
```
# tell passenger what python interpreter to use
PassengerPython "/home/flskusr/komiclogr-dev.komicbox.com/venv-3.6/bin/python"

# SET Environment variable RELATED CONFIG VALUES
SetEnv ENV_VAR_! 'some value'
```

## pasenger.py

minimal `pasenger.py` file

```
# instead of setting the python interpreter via os.execl(), use .htacces and the PassengerPython directive
# import sys, os
# INTERP = "/home/xxxx/xxxx/env/bin/python"
# if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

# uses Flask to implement the WSGI response
from manage import app as application
```

## manage.py

minimal `manage.py` file to test app server standup

```
from flask import Flask 
app = Flask(__name__)

@app.route('/') 
def index():
	return '<h1>Hello World!</h1>'

@app.route('/user/<name>') 
def user(name):
	return '<h1>Hello, %s!</h1>' % name

if __name__ == '__main__': 
	app.run(host='komiclogr-dev.komicbox.com', debug=True)
```

## $PATH settings

for testing the flask internal development web server, we need to modify the path to include the custom version
of python that was installed (3.6.2 above). we can create a short script that should be sourced before executing
the `manage.py` test script above.

the `set_path_for_python-3.6.sh` script file

```
#!/usr/bin/env bash

export PATH=$HOME/opt/python-3.6.2/bin:$PATH
``` 


# Testing the app server standup

## flask internal development web server

1. change direcrory to the applicaiton directory: `cd komiclogr-dev.komicbox.com`
2. first source the script file to set the path: `source set_path_for_python-3.6.sh`
3. start the development server: `python manage.py`
4. in your web browser go to: http://komiclogr-dev.komicbox.com:5000/ & http://komiclogr-dev.komicbox.com:5000/user/greg
5. once the test is complete, press `<CTRL-C>` to stop the development server

you should see output similar to the below:
```
 * Running on http://komiclogr-dev.komicbox.com:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 197-784-978
67.184.165.218 - - [28/Sep/2017 17:03:22] "GET / HTTP/1.1" 200 -
67.184.165.218 - - [28/Sep/2017 17:03:23] "GET /favicon.ico HTTP/1.1" 404 -
67.184.165.218 - - [28/Sep/2017 17:03:37] "GET /user/greg HTTP/1.1" 200 -
```

## production level Apache web server / Passenger

after you have successfully tested the development server and resolved any problems, you should be able to access the
web application vea the Apache / Passenger server. Go to the following URLS:

http://komiclogr-dev.komicbox.com/

http://komiclogr-dev.komicbox.com/user/Greg_my_main_man

# post deployment tasks

after deploying the code and bringing up the database, create the following scripts

to start the dev server, save the following as: `start_dev_server.sh`
```
./manage.py runserver -h komiclogr-dev.komicbox.com -p 5080
```

to restart the production server, save the following as: `restart_prod.sh` and recreate a tmp directory in the 
application directory: `mkdir tmp`

```
touch tmp/restart.txt
```