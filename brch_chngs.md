# File Overview
this file documents the changes made to the flasky application to adapt the code for
the comic logger application. Additionally, it provides details on deployment & 
configuration of the app.

## Initial flasky_clone Repository Creation
this repo was created by forking the following repo:
https://github.com/miguelgrinberg/flasky

## Inital Branch Creation
the `comic_logger_mstr` branch was crated from the tag: `13b`

`Chapter 13: Comment moderation (13b)`



# Deployment Notes

## .htaccess file settings

For servers using passenger, you must set the `PassengerPython` setting and any Environment Variables in the 
`.htaccess` file in the applicaiton root directory. See the following example:

```
PassengerPython "/home/<user>/<app_dir>/env/bin/python"

SetEnv ENV_VAR_1 'some value'
```

## Create the Database!!

### from the feature progressed misgration scripts

You will need to make sure the alembic migrations versions exist in the appropriate directory, else you will need 
to create them from the data model. (see next section)

_see: page 85 in Flask Web Development_

to create the database and tables... 

from the shell with the appropriate virtual environment activated, execute:

`./manage.py db upgrade`

```
(via_PyCharm/) :flasky_clone $ ./manage.py db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 38c4e85512a9, initial migration
INFO  [alembic.runtime.migration] Running upgrade 38c4e85512a9 -> 456a945560f6, login support
INFO  [alembic.runtime.migration] Running upgrade 456a945560f6 -> 190163627111, account confirmation
/.../envs/<env>/lib/python3.5/site-packages/alembic/util/messaging.py:69: UserWarning: Skipping unsupported ALTER for creation of implicit constraint warnings.warn(msg)
INFO  [alembic.runtime.migration] Running upgrade 190163627111 -> 56ed7d33de8d, user roles
INFO  [alembic.runtime.migration] Running upgrade 56ed7d33de8d -> d66f086b258, user information
INFO  [alembic.runtime.migration] Running upgrade d66f086b258 -> 198b0eebcf9, caching of avatar hashes
INFO  [alembic.runtime.migration] Running upgrade 198b0eebcf9 -> 1b966e7f4b9e, post model
INFO  [alembic.runtime.migration] Running upgrade 1b966e7f4b9e -> 288cd3dc5a8, rich text posts
INFO  [alembic.runtime.migration] Running upgrade 288cd3dc5a8 -> 2356a38169ea, followers
INFO  [alembic.runtime.migration] Running upgrade 2356a38169ea -> 51f5ccfba190, comments
(via_PyCharm/) :flasky_clone $ 
```

### from clean migration scripts

1. create a migration repository with: `python migrate.py db init` This command creates a migrations folder, where all 
the migration scripts will be stored
2. create the migration script that will create the initial database: `python manage.py db migrate -m "initial migration"`
3. apply the migration script to create the database with empty tables: `python manage.py db upgrade`
 
_see: pages 65 - 66, 85 in Flask Web Development_

```
(via_PyCharm/) :flasky_clone $ ./manage.py db init
  Creating directory .../flasky_clone/migrations ... done
  Creating directory .../flasky_clone/migrations/versions ... done
  Generating .../flasky_clone/migrations/alembic.ini ... done
  Generating .../flasky_clone/migrations/env.py ... done
  Generating .../flasky_clone/migrations/README ... done
  Generating .../flasky_clone/migrations/script.py.mako ... done
  Please edit configuration/connection/logging settings in '.../flasky_clone/migrations/alembic.ini' before proceeding.

(via_PyCharm/) :flasky_clone $ ./manage.py db migrate -m "initial migration (finapp)"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'roles'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_roles_default' on '['default']'
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_users_email' on '['email']'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_users_username' on '['username']'
INFO  [alembic.autogenerate.compare] Detected added table 'follows'
INFO  [alembic.autogenerate.compare] Detected added table 'posts'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_posts_timestamp' on '['timestamp']'
INFO  [alembic.autogenerate.compare] Detected added table 'comments'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_comments_timestamp' on '['timestamp']'
  Generating .../flasky_clone/migrations/versions/518bd0aeaa26_initial_migration_finapp.py ... done

(via_PyCharm/) :flasky_clone $ ./manage.py db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 518bd0aeaa26, initial migration (finapp)
```

### Populating the Roles table

There is a method called `inser_roles()`` defined on the `Role` class in the `app/modles.py` file.
To populate the Roles table with the required role records we must execute this this method by 
executing the following:
 
_see: page 113 in Flask Web Development_

```
python manage.py shell
Role.insert_roles()
Role.query.all()
[<Role u'Administrator'>, <Role u'User'>, <Role u'Moderator'>]
```  

### Register the Initial System Admin Account

after configuring the FLASKY_ADMIN congig setting and creating the database, start the application up and
register with the email address configured in the FLASKY_ADMIN environment variable. Record the password 
someplace secure.

_see: pages 113 - 114 in Flask Web Development_

### Manufacturing data

_see: pages 135 - 137 in Flask Web Development_

uses ForgeryPy: http://tomekwojcik.github.com/ForgeryPy/

install with: `pip install forgerypy`

to create the fake data, start the python shell via: `python manage.py shell`

then execute:
```
User.generate_fake(100)
Post.generate_fake(100)
```

## Create the application Admin Account

_see the section: **Register the Initial System Admin Account** under the **Create the Database section**._





# Changing Database Backends

This section details what was done to migrate from the Base App's SQLite database backend to a MySQL database
backend.

## Prepwork
Before we can switch the application to use MySQL, we first have to
* Install MySQL _(if an installation does not already exist)_
* Create the MySQL userid that the application will use to access the database _(different than unix or application
userid)
* Creeat a new MySQL database _(if not using an existing database on the MySQL server)_

## Code Changes
_see the code changes made for the Pending commit_

## Configuration Changes
The following configuration changes are required
* modified the properties.sh and .htaccess files to set the data base userid and passwords

## Database Setup
after the database was created on the MySQL server and the necessary config changes were made, executed the usual database setup steps
* `./manage.py db upgrade`
* `./manage.py shell` --> `Role.insert_roles()`
* create admin user via web GUI
* `./manage.py shell` --> `User.generate_fake(50)`; `Post.generate_fake(1000)`





# Configuration Details

## Environment Variables

### Notes on SECRET_KEY

To ensure the secret key is _cryptographically_ random enough, pythong's `os.urandom()` function can be used to
generate the secret key value. However, since this function returns a binary value (i.e., not printable utf-8),
it is difficult to store the resulting value in an environment variable. As such, we us Base64 to encode the 
binary value into ASCII and then set our environment variable, in our `propterties.sh` file, to the ASCII base64 
encoded value.

#### Generating the Value

```
>>> import os
>>> import base64
>>> print("export SECRET_KEY='{0}'".format(base64.b64encode(os.urandom(24)).decode("utf-8")))
export SECRET_KEY=''e9lxkIu67Hazyx4817rxtJnwNTaQVRau'
```

copy and paste the last line from the above and place it into your properties.sh, take additonal steps, as appropriate, 
dependent on the envrionment
 
```
export FOO_BASE64='e9lxkIu67Hazyx4817rxtJnwNTaQVRau'
```

_see:_ https://stackoverflow.com/questions/44479826/how-do-you-set-a-string-of-bytes-from-an-environment-variable-in-python/46458421#46458421

#### Runtime reading of the value

The `base64_decode()` function in `config.py` is used to Base64 decode the value retrieved from the `SECRET_KEY`
environment variable. It takes 2 parameters, the base64 encoded value to be decoded and a default value to be returned
if the base64 encoded value is not set (i.e., `None` or the `Empty String`). The returned value can then be used 
to populate the `SECRET_KEY` flask app config setting.

### How To Correctly set environment variables in different environments

depending on the OS, tools used, server platform, etc., there may be different ways to set the environment varialbes
so the the Flask Application can access then.

#### DEV Environment
In PyCharm, to set environment variables, go into the _Run-->Edit configurations..._ window, select the 
configuration that you want to edit, and click the _'...'_ button next to the 
_Envriontment Variables_ input field in the _Environment_ section.

#### Production Environments
In environments running Passenger use the `SetEnv` directive in the `.htaccess` file to set environment variables

#### Other
The user executing the applicaiton or script from the command line, should source the `properties.sh` file 
before running any scripts.


### Variables
| ..........page.......... | .................variable................ | desc / notes |
|:------------------------:|:-----------------------------------------:|--------------|
| 81 | FLASK_CONFIG | specifies the configuration class to use. Valid values: `development`, `testing`, `production`. If the envrionment variable is not set, then the named `default` config class of ` DevelopmentConfig` will be used |
| 38, 45, 104 | SECRET_KEY   | used as a general-purpose encryption key by Flask and several third-party extensions. from the python shell `import os` and then call `os.urandom(24)`, cut and paste the generated value. Used to sign client-side session cookies. Used by Itsdangerous `TimedJSONWebSignatureSerializer()` token generator for JSON Web Signatures| 
| 69, 77 | MAIL_USERNAME | SMTP (outbound) Mail account userid for sending system emails|
| 69, 77 | MAIL_PASSWORD | SMTP (outbound) Mail account password for sending system emails |
| 76, 114, 216, 217 | FLASKY_ADMIN | The application's primary admin's email addres. When a user with this registers, it will autmatically be given the `ADMIN` role. System emails will be sent to this email address.|
| 69, 77, 217 | MAIL_PORT (*) | Port of the email server (25 for TLS disabled, 587 for TLS enabled) |
| 69, 77, 217 | MAIL_USE_TLS (*) | Enable Transport Layer Security (TLS) security (default flase?) |
| 77, 217 | MAIL_SERVER (*) | The hostname for the SMTP (outbound) mail server  |
| 73, 76, 2117 | FLASKY_MAIL_SENDER (*) | the sender of application emails which will appear in the sent email as the reply-to, though there should be a note in all emails that this email account is not monitored. |
| 77 | DEV_DATABASE_URL | **DEPRECATED** _see APP_DB_USER and APP_DB_PASSORD_ - dev database - uses default value or configure |
| 77 | TEST_DATABASE_URL | **DEPRECATED** _see APP_DB_USER and APP_DB_PASSORD_ - test database - uses default value or configure |
| 77 | DATABASE_URL | **DEPRECATED** _see APP_DB_USER and APP_DB_PASSORD_ - prodcution database - uses default value or configure |
| _new_ | APP_DB_USER | the userid used to connect to the database server |
| _new_ | APP_DB_PASSWORD | the userid used to connect to the database server |




# steps to deploy code to dreamhost

1. change directory to the application directory: `cd ~/komiclogr-dev.komicbox.com`
2. after initial standup testing the following files should be present in the applicaiton directory
   1. .htaccess
   2. prperties.sh
   3. passenger_wsi.py
   4. manage.py
   5. set_path_for_python-3.6.sh
3. edit the  `.htaccess` file adding/changin the necessary environment variables
4. edit the `prperties.sh` file adding/changin the necessary environment variables
5. clone the github repo: `git clone https://github.com/gskluzacek/flasky.git`
6. the above clone command will create a folder called `flasky`, cd into that folder
7. execute the following copy commands
   1. `cp config.py manage.py ..`
   2. `cp -r app migrations tests ..`
8. cd back to the applicaton directory: `cd ..`
9. source the modified `properties.sh` file
10. execute: `./manage.py shell`
    1. `for ck, cv in app.config.items():`
    2. `print(ck, "\t", cv)`
    3. review the config settings
11. execute: `./manage.py db upgrade`
12. execute: `./manage.py shell`
    1. `Role.insert_roles()`
    2. `Role.query.all()`
13. create admin user
    1. launch dev server: `./manage.py runserver -h komiclogr-dev.komicbox.com`
    2. in a web browser go to: http://komiclogr-dev.komicbox.com:5000
    3. click `login`
    4. click `Click here to register`
    5. enter the application admin email address as configured in th env var: `FLASKY_ADMIN`
    6. enter username of `AdminUser`
    7. enter password (2x)
    8. get link from confirmation email & confirm account
    9. login and post test message
    10. logout
14. enter `<CTRL-C>` to exit the dev server
15. add some dummy data
    1. `./manage.py shell`
    2. `User.generate_fake(50)`
    3. `Post.generate_fake(1000)`
16. execute: `touch tmp/restart.txt`
17. and continue to test, go to: http://komiclogr-dev.komicbox.com
    
   
   
   
   
   
    

# Themes
themes are listed with the current/active theme listed first followed by the most recently completed themes

# Create Db Models for the Komic-Logr Functionality
The focus for this theme is to begin adding functionality required for the Komic-Logr application, starting with
the data model. There should be some screen which displays some mocked up data from the new data models along with
basic navigation to get to the screen. 

## details

## commits
* f1a1c0876545e276ac463045218473bac9b56f37
* 8d7cd47a2bfa8a6b2500de4b08f18c6abfd1a41a



# Migrate Base App to MySQL Database

The focus for this theame is to migrate the current SQLite database to a MySQL database and documenting what is 
required to do so. The migration required changes to the code and configuration.

## details

* refactored the code for that sets the `SQLALCHEMY_DATABASE_URI` config setting.
* the setting was broken into components: 
  * `APP_DB_USER` and `APP_DB_PASSWORD` which are set from environment variables within the confing base class
  * `APP_DB_HOST` abd `APP_DB_DATABASE` which are set within the derived config sub-classes
  * additionally changed the db-dialect from `sqlite:///` to `mysql+pymysql://`
* refactored the `DevelopmentConfig` derived sub-class into 2 different sub-classes 1) local development 
and 2) hosted development
* added the new environment variables to the properties.sh and .htaccess files  

## commits

* c623fc0a45fbfba91bc640fb0e6fc8e2d38f3ab1


# Get Base App up & running in the Hosted environment

The focus for this theam was create a new Hosted Environment, perform and document the necessary tasks to stand it up
and to take the branch created in the first theme (and changes made to it) and deploy it to the newly created hosted
environment, making any additional changes necessary to get the base applicaiton up and running.

One concern that came out of this theme is how to safely store and track changes to sensitive configuration data, 
regardless if it is different across environments.

## details
* moved some configuration setting from being stored in config.py to being stored in environment variables
* created files that are specific to the Dreamhost hosted environment: .htacess and passenger_wsgi.py. These files 
are not under the version control system as they contain sensitive config information. 

## notes
* deplending on the platform used to serve the web applicatoin, different mechanism may be needed in each environment
* for the Dreamhost hosted environment, Passenger, a Apache module, is used to serve WSGI applications. As such some
additional components were reqired to be introduced which include:
  * .htaccess file  - for: setting the python executable that Pasenger should use and for the setting of environmental 
  variables used by used by config.py
  * passenger_wsgi.py - a simple wrapper script that exports the Flash app object created in manage.py as `application`
* Revisit how we are handling some of the configuration settings that are currently stored in environment variables. 
should we create additional sub-classes and place the config setting there instead of storing them in environment 
variables. Currently the setting are in the base class.

## commits
* 7ee6dc1b432d78bef4409a44663b583dc00f4aac
* b2c678984a6a8a8e0673d39011db6b048343ed65


# Get Base App up & running in DEV environment

For this theme we cloned the Flasky github repo and created a new branch called: `comic_logger_mstr` from the tag: 
`13b` - `Chapter 13: Comment moderation (13b)`.

The focus was to make any needed configuration changes and create the database and populate the tables. Additionally,
documentation was created detailing the process.

## details
* changes made to config.py
* created properties.sh file to set environment variables read by config.py
* introduced logic to read the SECRET_KEY config setting from a Base64 encoded value stored as an environment variable. 
The variable was set using os.urandom() which returns a binary value that was saved as an ASCII string using Base64 
encoding.

## commits
* fc38e6841178588dc6f555cf4366c265089fe65b
* e2cbe7b0bb2fcc5e4245015f6c49633ad85a14c2







# changes
most recent changes are listed first...

## pending


## 8d7cd47a2bfa8a6b2500de4b08f18c6abfd1a41a

**2017-10-01: Fix for `explicit_defaults_for_timestamp` MySQL Server Config setting**

### Issue Description
An issue was found on the Dreamhost MySQL server where 
1) `TIMESTAMP NOT NULL` columns were not being created with the 
`DEFAULT CURRENT_TIMESTAMP` and `on update CURRENT_TIMESTAMP` DDL; and 
2) INSERT statments that were including
`TIMESTAMP NOT NULL` columns in the list of columns being inserted with an explicit value of `NULL` being set, were
failing. 

The root cause was that on the Dreamhost MySQL server, the `explicit_defaults_for_timestamp` was set to 1 but on
the local MySQL server, the `explicit_defaults_for_timestamp` was set to 0.

From the MySQL Documentation:

> If explicit_defaults_for_timestamp is disabled, the server enables the nonstandard behaviors...

The non-standard behavior being, if a `TIMESTAMP NOT NULL` column is explicitly set to `NULL` MySQL will default
the value to the `CURRENT_TIMESTAMP`.

see: https://dev.mysql.com/doc/refman/5.6/en/server-system-variables.html#sysvar_explicit_defaults_for_timestamp

### Issue Resolution
The fix was to explicitly set the `default` and `onupdate` parameters when defining the `TIMESTAMP` column 
on the data model.

```
crt_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.now(), onupdate=db.func.now())
``` 

_for addtional details see the: **New_Dreamhost_Environment_Standup.md** document, in the 'IMPORTANT ISSUES' section 
under the 'Create MySQL Database' section._

### other
Also added the `SQLALCHEMY_ECHO` config setting to the Development config sub-classes and Set the value to False.
Setting the falue to True will echo the SQL being generated. This is useful for debugging.


## f1a1c0876545e276ac463045218473bac9b56f37

**2017-10-01: Create new data models for Komic Logr app**

* added: `File` data model
  * `load_file()` static class method that reads the input file (passed as a parameter) loads the `files` and `lines`
  table and returns an instance of the `File` class. 
    * For each line in the file it creates an instance of the `Line` class and adds it to the `File` instance's 
    `lines` list.
    * Was able to simplified the call to the `Line` constructor. (a `__init__()` method was added to the `Line`
     class).
    * After the file is read, the purchase date, store and transaction number are taken from the first `Line` 
    and are set on `File`
  * `generate_invoice()` & `generate_html_invoice()` instance methods for generating invoice output.
* added `Line` data model
  * `__init__()` method implemented to simplify the creation of `Line` instances _from the caller's perspective_
    * This allowed the removal of `or None`, truncating vachar values that were too long and performing calculations 
    for various field values when reading of the input values from the file 
    * added a new parameter for `default_disc_rate` - used to calc `purch_price`
    * pulled in the calculation of `pruch_price`, `cvr_dt_year`, `cvr_dt_month` and `cvr_dt_day`. Previously, these 
    were set after the lines records were commit to db. 
    * calls the `__init__()` of the `Line` class's bases class, passing the values from the `**kwargs` parameter
    via the `get()` method. This allowed us to take in the additonal parameter for `default_disc_rate` as a
    required positional parameter
  * static methods for parsing date values, parsing price values and calculating the purchase price 
* created: `invoice_template.html` for the generation of the output html invoice FILE
* created: `style.css` to style the invoice html
* manage.py: added the 2 new models: `File` & `Line` to the make_shell_context() funciton

## c623fc0a45fbfba91bc640fb0e6fc8e2d38f3ab1

**2017-09-30: Migrate Base App to MySQL Database**

The following code changes were made to accomodate the database backend change
* config.py 
  * added `APP_DB_USER` & `APP_DB_PASSWORD` config settings to the base class, populated from environment variables
  * split the `DevelopmentConfig` class into 2 separate classes: `DevLocalConfig` and `DevHostedConfig`
  * added `APP_DB_HOST` & `APP_DB_DATABASE` config settings
  * modified how the `SQLALCHEMY_DATABASE_URI` config setting value is derived - generates it from: `APP_DB_USER`, 
  `APP_DB_PASSWORD`, `APP_DB_HOST` and `APP_DB_DATABASE`. Also changed the db-dialect to `mysql+pymysql`
  * modified the keys for the `config` dictionary to split the developmntConfig class into separate classes. old key
  was `deveopment` new keys are: `dev-local` and `dev-hosted`. Also set the value for the `default` config to the 
  `DevLocalConfig` class
* properties.sh / .htaccess
  * added the `APP_DB_USER` & `APP_DB_PASSWORD` environment variables
  * modified the value of the `FLASK_CONFIG` environment variable to account for the spliting of the development config
  class into 2 separate config classes.


## b2c678984a6a8a8e0673d39011db6b048343ed65

**28-SEP-2017: resolve open testing issue** 

in the previous commit `7ee6dc1b432d78bef4409a44663b583dc00f4aac` it was noted that the confirmaiton email had not 
been received. This is incorrect. The email was delivered but was sent to the SPAM folder.

## 7ee6dc1b432d78bef4409a44663b583dc00f4aac

**28-SEP-2017: deploy code to fresh dreamhost install** 

### changes
* created `New_Dreamhost_Environment_Standup.md` with details on standing up a new Dreamhost environment
* modified `config.py` changed logic to get additonal config values from environment variables
* modified `properties.sh` added additonal environmental variables

### open issues found during testing
* confirmation email was not reciveved, but appreas, per the log, to have been sent.


## e2cbe7b0bb2fcc5e4245015f6c49633ad85a14c2

**28-SEP-2017: Config and DB set up for base application in DEV Enviroment** 

### config & database
* started setting up the configuration
  * config value changes in `config.py`
    * updated `MAIL_SERVER` for gmail
    * updated `FLASKY_MAIL_SENDER`
  * create properties.sh for environment variables - this file should be sourced prior to the execution of the 
development web server.
  * properties added:
    * FLASK_CONFIG
    * SECRET_KEY
    * MAIL_USERNAME
    * MAIL_PASSWORD
    * FLASKY_ADMIN
  * did not add properties for the following, will use the defaults provided by the `Config` classes
    * DEV_DATABASE_URL
    * TEST_DATABASE_URL
    * DATABASE_URL
  * Notes on properties.sh
    * if executing the application via PyCharm, environment variables will have to be set in the 
    IDE. see the DEV environment in the Environment variable section under Configuration Details._
    * _Note for execution under passenger need to put environment variables into the `.htaccess` file_
* created the database & added first user (AdminUser / flask.amin@gmail.com)
  * applied intial database migration: `./manage.py db upgrade`
  * added roles via `./manage.py shell Role.insert_roles()`
  * added app Admin via UI registrations & confirmed via emailed link
  * added dummy data for Users (75) and Posts (500) via `./manage.py shell User.generate_fake(75) Post.generate_fake(500)`

### notable
* for passenger, need to set the python interpreter in the `.htaccess` file
* added the `base64_decode()` function to `config.py`. This funciton is called to populate the `SECRET_KEY` config
setting. The value for the `SECRET_KEY` is a base64 encoded string stored in the environment variable by the 
same name. The function takes the encode string and a default `SECRET_KEY` value as parameters. the default value
is used if the environment variable is not set. 
 
### minor
* updated common requirements file
  * _to install dependencies from the requiremnts file use:_ `pip install -r <requirements-file>.txt`
* backing up old common requirements to common.txt.old
* created script to get the `pip show` info for each package and saved it to show1.txt
* created _clean_ alembic migration script starting direct from the data _current_ data model in this 
branch instead of having multiple intermediate migrations scripts.
  * scripts reside in the `migration_clean` directory
* create shell script to export schema to a text file, see: `schema/export_schema.sh`


## fc38e6841178588dc6f555cf4366c265089fe65b

**27-SEP-2017: Initial creation of branch** 

* created new branch
* added this file
* added Notes.md -- the notes I've taken while reading _Flask Web Development_
* updated .gitignore






# Backlog

## Themes
* add new application functionality that uses new models including navigation 
* strip out base functionality and navigation 

## Features
* To Be Determined...