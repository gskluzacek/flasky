# Virtual Environments

to check if you have it
> virtualenv --version

Install on Mac OS
> sudo easy_install virtualenv

create the Python virtual environment inside the flasky folder (make sure to CD into this folder). The command has a 
single required argument, the name of the virtual environment. A folder with the chosen name will be created in the 
current directory and all files associated with the virtual environment will be inside. A com‐ monly used naming 
convention for virtual environments is to call them **venv**
> virtualenv venv

to begin using the virtual environment:
> source venv/bin/activate

to stop using the virtual environment: 
> deactivate


# from pages xiii thru xv of the preface - How to work with the example code:

repo
> https://github.com/miguelgrinberg/flasky


The git clone command installs the source code from GitHub into a flasky folder that is 
created in the current directory
> git clone https://github.com/miguelgrinberg/flasky.git


to checkout the code for chapter 1
> git checkout 1a


If you modify the source files of the application then Git will not let you check out a 
different revision, as that would cause your local changes to be lost. Before you can check 
out a different revision, you will need to revert the files to their original state. 
The easiest way to do this is with the git reset command:
> git reset --hard


you may want to refresh your local repository from the one on GitHub, where bug fixes 
and improvements may have been applied. The commands that achieve this are:
> git fetch --all
> git fetch --tags
> git reset --hard origin/master


to view all the differences between two versions of the application
> git diff  2a 2b

or go to github
> https://github.com/miguelgrinberg/flasky/compare/2a...2b


# Contexts

Flask activates (or pushes) the application and request contexts before dispatching a request and then removes them 
when the request is handled. When the application context is pushed, the current_app and g variables become available 
to the thread; likewise, when the request context is pushed, request and session become available as well. If any of 
these variables are accessed without an active application or request context, an error is generated.

* current_app
* g
* request
* session

## creating and using an app context from the python shell

```
from flask import Flask
from flask import current_app
app = Flask("some pig")
app_ctx = app.app_context()
app_ctx.push()
print(current_app.name)
```

# requests and view functions and responses

A view function has 2 tasks
1. generate a response to a request (presentation logic)
2. trigger a change in the state of the application (business logic)

Mixing business logic and presentation logic in the view function creates code that is hard to understand and maintain. 
For example, generating and HTML table by concatenating the HTML tags (string litterals) with data from various SQL 
queries (key value paris in a dictionary object). Write code like this would be hard to modify later if the database 
structure changes or if the DIVs and CSS are used to present the data. The business logic and presentation logic need 
to be decoupled.

Instead templates shoudl be used to generate the HTML. Templates are passes the input data that they use (as determined 
by the business logic) and renders the final output.

# request hooks

Sometimes it is useful to execute code before or after each request is processed. For example, at the start of each 
request it may be necessary to create a database connection, or authenticate the user making the request. Instead of 
duplicating the code that does this in every view function, Flask gives you the option to register common functions to 
be invoked before or after a request is dispatched to a view function

Request hooks are implemented as decorators. These are the four hooks supported by Flask:
* **before_first_request:** Register a function to run before the first request is handled.
* **before_request:** Register a function to run before each request.
* **after_request:** Register a function to run after each request, if no unhandled ex‐
ceptions occurred.
* **teardown_request:** Register a function to run after each request, even if unhandled exceptions occurred.

A common pattern to share data between request hook functions and view functions is to use the g context global. For 
example, a before_request handler can load the logged- in user from the database and store it in g.user. Later, when 
the view function is invoked, it can access the user from there.

# response

## normal repsonse
view functions need to return a response. 3 parts:
* a string
* a status code (default is 200)
* a dictionary of headers

Instead of returning a 3 element tuple, can use make_response() function. Parrms are the same listed above

`from flask import make_response`

## redirect response

use Flask's helper funciton: redirect(<URL>)

sets the status code to 302

`from flask import redirect`

## Error Hanling

`from flask import abort`

Use the flask helper funciton: abort(404)

sets the status code to 404, and then returns control back to the web server (i.e., it exits funciton)

# Flask-Script

The Flask-Script extension provides support for writing external scripts in Flask. This includes 
running a development server, a customised Python shell, scripts to set up your database, cronjobs, 
and other command-line tasks that belong outside the web application itself.

_As of Flask 0.11, Flask includes a built-in CLI tool, and that may fit your needs better. see:_
http://flask.pocoo.org/docs/0.12/cli/

## installing

to instal flask-script
> pip install flask-script

## using...

```
from flask_script import Manager

manager = Manager(app)

if __name__ == '__main__': 
    manager.run()
```

The method of initialization of this extension is common to many extensions: an instance of the main class is 
initialized by passing the application instance as an argument to the constructor.

The server startup is routed through manager.run(), where the command line is parsed

`usage: hello.py [-h] {shell,runserver} ..`

### shell

Runs a Python shell inside Flask application context. The shell command is used to start a Python shell session in the 
context of the application. You can use this session to run maintenance tasks or tests, or to debug issues

You will need to import all modules, Classes, objects, etc. that are needed... unless you configure the
Flask-Script’s shell command to automatically import certain objects by regerstering them via a 
`make_context` callback function.

```
from flask.ext.script import Shell 

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
    
manager.add_command("shell", Shell(make_context=make_shell_context))
```

The `make_shell_context()` function above, registers the application and database instances and the models 
so that they are automatically imported into the shell

```
python hello.py shell
>>> app
<Flask 'app'>
>>> db
<SQLAlchemy engine='sqlite:////home/flask/flasky/data.sqlite'> >>> User
<class 'app.User'>
```

also alternatively:

```
@manager.shell
def make_shell_context():
    return dict(app=app, db=db, models=models)
```

### adding commands

in the above section `manager.add_command()` was used, there is also a decorator that can be uses

```
@manager.command
def hello():
    print("hello")
```

Alternatively, one can derive a subclass from the `Command` base class, defining a `run()` method.

```
from flask_script import Command
    
class Hello(Command):
    "prints hello world"
    
    def run(self):
        print("hello world")
```

Then: `manager.add_command('hello', Hello())`

and finaly `$ python manage.py hello`

there is also the `@manager.option` decorator...



### runserver

Runs the Flask development server [by calling `app.run()`]. The runserver command, as its name implies, starts the web server. 
Running `python xxxxxx.py runserver` starts the web server in debug mode, but there many more options available: 
`python xxxxxx.py runserver --help`

    optional arguments:
      -h, --help
      -t HOST, --host HOST
      -p PORT, --port PORT
      --threaded
      --processes PROCESSES
      --passthrough-errors
      -d, --no-debug
      -r, --no-reload

by default, Flask’s development web server listens for connections on localhost, so only connections originating from 
within the computer running the server are accepted. The following command makes the web server listen for connections 
on the public network interface, enabling other computers in the network to connect as well

    (venv) $ python hello.py runserver --host 0.0.0.0
     * Running on http://0.0.0.0:5000/
     * Restarting with reloader

# templating

Flask uses jinja2 templating, and by default looks for templates in a `templates` subfolder located inside the 
application folder.

`from flask import render_template`

## within view functions

Use `return render_template('index.html')` or `return render_template('user.html', name=name)` or `return 
render_template('user.html', {'name':name, 'age':age)` to render the template.

The function render_template provided by Flask integrates the Jinja2 template engine with the application. This function 
takes the filename of the template as its first argu‐ ment. Any additional arguments are key/value pairs that represent 
actual values for variables referenced in the template. In this example, the second template is receiving a name 
variable.

## within templates

Use `{{ var-name }}` in the template to render data.

Jinja2 recognizes variables of any type, even complex types such as lists, dictionaries and objects. The following are 
some more examples of variables used in templates:
```
<p>A value from a dictionary: {{ mydict['key'] }}.</p>
<p>A value from a list: {{ mylist[3] }}.</p>
<p>A value from a list, with a variable index: {{ mylist[myintvar] }}.</p>
<p>A value from an object's method: {{ myobj.somemethod() }}.</p>
```

The last one is very powerful... calling a method on an object!!

## fitlers

* capitalize
* lower
* upper
* title
* trim
* safe - renders the value without performing any escaping
* striptags - removes any html tags before rendering

jinja will escape special characters before outputting them, e.g.: `<h1>Hi there</h1>` the `<` and `>` get escaped as 
`&lt;` and `&gt;`

SEE: http://jinja.pocoo.org/docs/2.9/templates/

## control structures

* {% if `<cond>` %} / {% else %} / {% endif %}
* {% for `<x>` in `<xs>` %} / {% endfor %}
* {%  macros `<macro-name>`(`<marcor-args>`) %} / `<macro-cmds>` / {% endmacro %} / {{ `<macro-name>`(`<marcor-args>`) }}
* {% import '`<macro-file-name>`.html' as macros %}
* {% include '`<common-code-file-name>`.html' %}

To make macros more reusable, they can be stored in standalone files that are then imported from all the templates 
that need them.

Portions of template code that need to be repeated in several places can be stored in a separate file and included from 
all the templates to avoid repetition

## inheritance

in the base-class template `<base-file-name>`.html

```
<html>
<head>
    {% block head %}
    <title>{% block title %}{% endblock %} - My Application</title> 
    {% endblock %}
</head>
<body>
    {% block body %}
    {% endblock %}
</body>
</html>
```

defines 3 blocks the derived template can set values for / modify
* head - note has a nested block and other content...
* title
* body

in the sub-classing template `<sub-class-file-name>`.html

```
{% extends "base.html" %}
{% block title %}Index{% endblock %}
{% block head %}
    {{ super() }}
    <style>
        body {...}
    </style>
{% endblock %}
{% block body %} <h1>Hello, World!</h1> {% endblock %}
```

when setting the content for the `head` block, `{{ super() }}` is called to retain the original content defined in the 
base template. 

resuting rendered output

```
<head>
<html>
    <title>Index - My Application</title> 
    <style>
        body {...}
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>
```

## inheritance extended example for error handling

make use of the bootstrap library as the base template, then create a application base template that extends the 
Boostrap base template, then derive the application templates from the new app base template and derive the error
templates from the new app base template as well

### base application templates

The application base template, `base.html` extends the bootstrap base template and includes the application's title, nav bar and a 
block for the page's content.

```
{% extends "bootstrap/base.html" %}

{% block title %}...{% endblock %}

{% block navbar %}
...
{% endblock %}

{% block content %}
<div class="container">
    {% block page_content %}{% endblock %}
</div>
{% endblock %}
```

### derived User template based on aplication base template

The template for the index page is then derived from the applicaiton's base template, `base.html` and only the title 
and content block need to be populated. The Nav Bar is automatically included.

````
{% extends "base.html" %}

{% block title %}Flasky{% endblock %}

{% block page_content %}
  <div class="page-header">
    <h1>Hello, {{ name }}!</h1>
  </div>
{% endblock %}
````

### derived error template based on aplication base template

The template for the index page is then derived from the applicaiton's base template, `base.html` and only the title 
and content block need to be populated. The Nav Bar is automatically included.

````
{% extends "base.html" %}

{% block title %}Flasky - Page Not Found{% endblock %}

{% block page_content %}
  <div class="page-header">
    <h1>Not Found</h1>
  </div>
{% endblock %}
````

# Twitter Bootstrap Integration

Bootstrap is an open source framework from Twitter that provides user interface com‐ ponents to create clean and 
attractive web pages that are compatible with all modern web browsers.

Bootstrap is a client-side framework, so the server is not directly involved with it. All the server needs to do is 
provide HTML responses that reference Bootstrap’s cascading style sheets (CSS) and JavaScript files and instantiate the 
desired components through HTML, CSS, and JavaScript code. The ideal place to do all this is in templates.

## install

`pip install flask-bootstrap`

## import and initialization

```
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
```

## template usage

The Jinja2 extends directive implements the template inheritance by referencing `bootstrap/base.html` from 
Flask-Bootstrap. The base template from Flask-Bootstrap provides a skeleton web page that includes all the 
Bootstrap CSS and JavaScript files.

`{% extends "bootstrap/base.html" %}`

Base templates define blocks that can be overriden by derived templates. The block and endblock directives define blocks 
of content that are added to the base template.

```
{% block title %}Flasky{% endblock %}
{% block navbar %}
    ...
{% endblock %}
{% block content %}
    ...
{% endblock %}
```

The user.html template above defines three blocks called title, navbar, and content. These are all blocks that the base 
template exports for derived templates to define.

### bootstrap blocks

* doc -- The entire HTML document
* html_attribs -- Attributes inside the `<html>` tag 
* html -- The contents of the `<html>` tag 
* head -- The contents of the `<head>` tag 
* title -- The contents of the `<title>` tag 
* metas -- The list of `<meta>` tags 
* styles -- Cascading stylesheet definitions 
* body_attribs -- Attributes inside the `<body>` tag
* body -- The contents of the `<body>` tag
* navbar -- User-defined navigation bar 
* content -- User-defined page content 
* scripts -- JavaScript declarations at the bottom of the document 

# error pages

to the view add error handlers with

`@app.errorhandler(<err-num>)`

for example to handle 404, page not found

```
@app.errorhandler(404)
def page_not_found(e):
    return render_template('<customer_error_template>.html'), 404
```

# Links

use `url_for(<view-function-name>)` to generate the anchor link tag for a given route. 

pass named paramters for dynamic urls: `url_for(<view-function-name>, param1='<some value>')`

adding the `_external=True` to the url_for() call will generate an external URL, for example: `url_for(
user, name='mike', _external=True)` would generate a URL of:

http://localhost:5000/user/mike  --- versus ---   /user/mike

additional named parameters that are not part of the view's parameters are appended to the query string: `url_for(
user, name='mike', page=2, _external=True)`

http://localhost:5000/user/mike?page=2

# static files

Static files such as images or css files are stored in the `static` directory. URLs for these files can be generated
with `url_for('static', filename='<static-file-name>)`

# Localization of Dates and Times

see the moment.js javascript library and Flask-Moment flask extension.

download from: http://momentjs.com

install the flask extension with: `pip install flask-moment`

import and initialize with

```
from flask_moment import Moment 
moment = Moment(app)
```

in view route pass a date time object in UTC for example:

```
return render_template('index.html', current_time=datetime.utcnow())
```

then in the template:

```
{{ moment(current_time).format('LLL') }}
{{ moment(current_time).fromNow(refresh=True) }}
```

The format('LLL') format renders the date and time according to the time zone and locale settings in the client computer. 

The fromNow() render style shown in the second line renders a relative timestamp and automatically refreshes it as time 
passes. E.g., 

Also implmentes: format(), fromNow(), fromTime(), calendar(), valueOf(), and unix() methods from moment.js

See: http://momentjs.com/docs/#/displaying/

set the localization language in the template by: `{{ moment.lang('es') }}`

The Diplays something like the following in the web page:

```
The local date and time is September 25, 2017 6:28 PM.
That was a few minutes ago.
```

# configuration

the `app.config` is a dictionary used by Flask and its extensions to store configuraiton settings. The configu‐ ration 
object also has methods to import configuration values from files or the environment.

## using Classes & sub Classes for configuration

### the base class

The `Config` base class contains settings that are common to all configurations.  Some settings can 
be optionally imported from environment variables, or example, the value of the `SECRET_KEY`.

Configuration classes can define a `init_app()`, a class method that takes an **application instance** 
as an argument. Here configuration-specific initialization can performed.

### the sub classes 

The different subclasses define settings that are specific to a configuration. Additional 
configurations can be added as needed.

The `SQLALCHEMY_DATABASE_URI` variable is assigned different values under each of the three 
configurations. This enables the application to run under different configurations, each using a 
different database.

### registering environment values

At the bottom of the configuration script, the instances of the different configuration Classes 
are _registered_ in the config dictionary. Additionally, the development configuration is registered as 
the default config object.

### example ...

```
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string' 
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # ...
    
    @staticmethod
        def init_app(app): 
            pass
    
class DevelopmentConfig(Config): 
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    # ...
    
class TestingConfig(Config): 
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')    
    # ...
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    # ...

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

# Using an Application Factory

Creating the application object in a single-file application is convenient, however the app object is
in the global scope and there is no way to dynamically configure it.

Because the application is created in the global scope (within the single-file application file), 
there is no way to apply configuration changes dynamically. By the time the script is running, the application instance 
has already been created. 

Being able to dynamically configure the app object is particularly important for unit tests because sometimes 
it is necessary to run the application under different configuration settings for better test coverage.

To fix this issue, the creation of the app object will be defered, and moved into an Application
Factory that is then explicitly called by the script.

## implementing the application factory...

The application facory funciton is defined in the `app` package's `__init__.py`. We use `__init__.py`
to import the Flask Extensions used by our applicaiton. The last import statement reads in the 
application's configuration.

```
from flask import Flask, render_template 
from flask.ext.bootstrap import Bootstrap 
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy 
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
```
However since we have not created the app object yet, we create the extension objects passing no 
parameters, i.e., uninitialized.

```
def create_app(config_name):
    app = Flask(__name__)
     
    app.config.from_object(config[config_name])  # 1
    config[config_name].init_app(app)            # 2
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    
    # attach routes and custom error pages here
    from main import main as main_blueprint     # 7 
    app.register_blueprint(main_blueprint)      # 8
    
    return app
```

The configuration object to use is _selected_ by the value of the `config` dictionary key 
name passed in the `config_name` parameter.

Line #1 uses the `app.config.from_object()` to configure the app object

Line #2 calls the _selected_ config class's `init_app()` method.

Line #7 will execute th3 `main` `__init__.py` code which will define the blue print as well as
import the `vies` and `error` handlers.

Line #8 then registers the blue print with the application

The remaining lines initialize the Flask Extensions used by the application by calling the 
`init_app()` method.

## Blueprints - Routes & custom Error Handlers with the Application Factory

_I'm not sure I'm buyting the following explanation from Flask Web Development..._

> The conversion to an application factory introduces a complication for routes. In single-script 
applications, the application instance exists in the global scope, so routes can be easily defined 
using the app.route decorator. But now that the application is created at runtime, the app.route 
decorator begins to exist only after create_app() is invoked, which is too late. 

_I'd argue, even in the old single-script application, the app obj was created at run-time!! How else
could you create it?! And also, the app.route decorator also only existed after the app
object is created. I really see no difference._  

Though I will agree, that blueprints offer a better way to organize the application over the 
single-script application. 

_app/main/\_\_init\_\_.py_

```
from flask import Blueprint
main = Blueprint('main', __name__) 
from . import views, errors
```

The constructor for the Blueprint class takes two required arguments: the blueprint name and the module or 
package where the blueprint is located.

The routes of the application are stored in an app/main/views.py module inside the package, and 
the error handlers are in app/main/errors.py. Importing these modules causes the routes and error 
handlers to be associated with the blueprint. 

**It is important to note that the modules are imported at the bottom of the** `app/__init__.py` 
**script to avoid circular dependencies, because views.py and errors.py need to import the 
main blueprint.**

when registering the error handlers (which are now inside a blue print) the `app_errorhandler` 
decorator must now be used (instead of the regular `errorhandler` decorator) so that the error 
handlers are invoked for all web pages and not just those inside the blue print.

## url_for() changes with Blueprints

Flask applies a namespace to all the endpoints coming from a blueprint so that multiple blueprints 
can define **view functions with the same** [endpoint] **names** [without collisions]. The namespace is the 
name of the blueprint, so the index() view function is _registered_ with _endpoint_ name main.index 
and its URL can be obtained with `url_for('main.index')`.

There is also a shortened form that can be used internally within a Blueprint, `url_for('.index')`. 
But to refer to a route that is external to the current Blueprint, the long form must sill be used.

## updated launch script

A separate script, `manage.py` is now used to launch the application. To run the development server,
execute:

### the new script:

```
#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default') 
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__': 
    manager.run()
```

### executing
`python manage.py runserver` or just `./manage.py runserver` now that a shebang line has been added.

### db updates
db updates can be applied with: `python manage.py db upgrade`

# Requirements file

## creating a requiremnts file

generate one like this...

`pip freeze >requirements.txt`

## using a requirements file

Have pip read the packages to install with:

`pip install -r requirements.txt`

# unit tests

## defining unit test cases

The test directory is under the project directory, not in the app directory. Additonally, an empty 
`__init__.py` should exist inside the test directory to make it a propper python package. _This way
the `unittest` package can scan all the modules (within the package) and locate the tests._

_in tests/test_basics.py_

```
import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
```

The above uses the unittest package from the Python standard library. The `setUp()` and `tearDown()` 
methods run before and after each test, and any methods that have a name that begins with `test_` 
are executed as tests.

see: https://docs.python.org/2/library/unittest.html

The `setUp()` method tries to create an environment for the test that is close to that of a 
running application. It first creates an application configured for testing and activates its 
context. This step ensures that tests have access to `current_app`, like regular requests. 
Then it creates a brand-new database that the test can use when necessary. The database and 
the application context are removed in the `tearDown()` method.

## executing unit test cases

the unit test cases can be executed with the following:

`python manage.py test`


# Forms

## request object provides

the `request.form` dictionary provides access to all form data.

## form generation flask extension

use Flask-WTF and WTForms, install it and dependencies with:

`pip install flask-wtf`


https://flask-wtf.readthedocs.io/en/stable/

http://wtforms.readthedocs.io/en/latest/


## cross-seite request forgery - CSRF 

Flask-WTF implements CSRF protection and uses the encryption key configured into the Flask app object:

```
app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xaf\xd6\xbdv\x87\xad\x1e\xe6\x85\xb5J\xe8\x87]\x8d\x0f{-\xc4\xb7\xb0\xbc\xe9V'
```

To generate the SECRET KEY you can execute the following in a python shell:

```
>>> import os
>>> os.urandom(24)
>>> ^D
``` 

For added security, the secret key should be stored in an environment variable instead of being embedded in the code.

## form classes

Each web form is represented by a sub-class derived from `Form` class. The class defines the list of fields in the 
form, each represented by an object. Each field object can have one or more validators functions attached to check 
whether the input submitted by the user is valid.

```
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()]) 
    submit = SubmitField('Submit')
```

The above creates a form called `NameForm` with 2 `<input>` elements: 1 with a type of `text` called `name` and 1 
with a type of `submit` (a button) called `submit`. The first argument to the field constructors is the label that will 
be used when rendering the form to HTML

The list of standard HTML fields supported by WTForms
* StringField
* TextAreaField
* PasswordField
* HiddenField
* DateField  -- a datetime.date value
* DateTimeField -- a datetime.datetime value
* IntegerField
* DecimalField -- a decimal.Decimal value
* FloatField
* BooleanField -- a Checkbox with True and False values
* RadioField -- a List of radio buttons
* SelectField
* SelectMultipleField
* FileField -- a File upload field
* SubmitField -- a Form submission button
* FormField -- _Embed a form as a field in a container form_
* FieldList -- _a List of fields of a given type_

WTForms validators
* Email
* EqualTo -- Compares the values of two fields
* IPAddress
* Length
* NumberRange -- Validates that the value entered is within a numeric range
* Optional -- Allows empty input on the field, skipping additional validators
* Required
* Regexp -- Validates the input against a regular expression
* URL
* AnyOf -- Validates that the input is one of a list of possible values
* NoneOf -- Validates that the input is none of a list of possible values

## rendering forms

### minimal implementation

```html
<form method="POST">
    {{ form.name.label }} {{ form.name(id='my-text-field') }} 
    {{ form.submit() }}
</form>
```
any named parameters passed will become attributes on the form element.

### reneding with Bootstrap's Form Styles

Flask-Bootstrap provides a very high-level helper function that renders an entire Flask-WTF __form__ using Bootstrap’s 
predefined form styles, all with a single call.

```jinja2
    {% import "bootstrap/wtf.html" as wtf %}
    {{ wtf.quick_form(form) }}
```

The import directive works in the same way as regular Python scripts do and allows template elements to be imported 
and used in many templates. The imported bootstrap/ wtf.html file defines helper functions that render Flask-WTF forms 
using Bootstrap. The wtf.quick_form() function takes a Flask-WTF form object and renders it using default Bootstrap 
styles.

### full example using Bootstrap from a template

```jinja2
{% extends "base.html" %}

{% import "bootstrap/wtf.html" as wtf %}

{% block title %}Flasky{% endblock %}

{% block page_content %}
<div class="page-header">
    <h1>Hello, {% if name %}{{ name }}{% else %}Stranger{% endif %}!</h1>
</div>
{{ wtf.quick_form(form) }}
{% endblock %}
```

## forms in the view function

```
@app.route('/', methods=['GET', 'POST']) def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
    form.name.data = ''
    return render_template('index.html', form=form, name=name)
```

The view function creates an instance of the `NameForm` class shown previously to represent the form, which 
is passes to the `render_template()` call as a named parameter.

The `validate_on_submit()` method of the form returns True when the form was submitted and the data has 
been accepted by all the field validators. In all other cases, `validate_on_submit()` returns False. The 
return value of this method effectively serves to decide whether the form needs to be rendered or 
processed.

When the form is submitted by the user, the server receives a POST request with the data. The call to 
`validate_on_submit()` invokes the `Required()` validator attached to the `name` field. If the `name` 
is not empty, then the validator accepts it and `validate_on_submit()` returns True

The name entered by the user is accessible as the `data` attribute of the field. The form field can be cleared by 
setting that `data` attribute to an empty string.

# Post Form Submits, Redirects & user session

After a form is submitted via the POST method, if the user does a refresh of the web page in their 
browser, they will get a pop-up warning asking them to confirm resubmitting the form again. When the 
last request sent is a POST request with form data, a refresh would cause a duplicate form submission, 
which in almost all cases is not the desired action. As such, it is good practice for web applications 
to never leave a POST request as a last request sent by the web browser.

This can be achieved by responding to POST requests with a redirect to a new page (could be the same
page)instead of sending a normal HTML response. When the broswer receives a redirect request, it will
issue a new GET request to the specified web page. Now the last request is a GET, so the refresh command 
works as expected.

https://en.wikipedia.org/wiki/Post/Redirect/Get

However, becuase the resulting web page after the redirect will not have access to the web form data,
any data that we want to use must be stored in the user's session. The user `session` is one of the four
contextes that Flask activate before turning over control to the request handler (view) function. The
sesion variable is a standard python dictionary.

 By default, user sessions are stored in client-side cookies that are cryptographically signed using 
 the configured SECRET_KEY. Any tam‐ pering with the cookie content would render the signature invalid, 
 thus invalidating the session.

## saving a value

`session['name'] = <value>`

## getting a saved value

`session.get('name')`

using `get()` avoids throwing a `KeyError` exception if the key is not found in the session dictionary. 
Additionally, you can pass a 2nd parameter (a defualt value) to the `get()` method, which will be 
returned if the key is not found, else `None` will be returned.

## issuing a redirect

`return redirect(url_for('index'))`

The `redirect()` function is a  helper function that generates the HTTP redirect response.


# feedback to the USER via the Message Flash API

it is useful to give the user a status update after a request is completed, like a confirmation message
or a validation error, or some other warning.

## in the view function / route

```
from flask import flash
flash('Looks like you have changed your name!')
```

## in the template

In addtion to calling the `flash()` fuction, the templates needs to render these messages. The best 
place to render flashed messages is the base template, because that will enable these messages in 
all pages. Use the Flask `get_flashed_messages()` function in the template get the messages and render 
them.

In the base applicaiton template, messages can be rendered using Bootstrap’s alert CSS styles for 
warning messages...

```
{% block content %}
<div class="container">
    {% for message in get_flashed_messages() %}
    <div class="alert alert-warning">
        <button type="button" class="close" data-dismiss="alert">&times;</button>
        {{ message }}
    </div>
    {% endfor %}
    {% block page_content %}...{% endblock %}
</div>
{% endblock %}
```

A loop is used because there could be multiple messages in the queue, one for each time `flash()` was 
called. Onece a messages is retrieved using `get_flashed_messages()` it will be discared and will not 
be returned again if `get_flashed_messages()` is called a second time.

# SQL Alchemy

Integrate with Flask via Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/2.1/

the plugin provides:
* all the functions and classes from `sqlalchemy` and `sqlalchemy.orm`
* a preconfigured scoped session called `session` (accessible via `db.session`)
* the `metadata`
* the `engine`
* a `SQLAlchemy.create_all()` and `SQLAlchemy.drop_all()` methods to create and drop tables according to 
the models
* a `Model` baseclass that is a configured _declarative base_.

The `Model` declarative base class has a `query` attribute attached that is used to query the model (`Model` and 
`BaseQuery`).

see this web page for instructions on how to use the plugin from the python shell and initializing the
plugin when the app context is created dynamically in a function:

http://flask-sqlalchemy.pocoo.org/2.1/contexts/

## Installation

`pip install flask-sqlalchemy`

## Database Config & Specification

* MySql  -- `mysql://username:password@hostname/database`
* Postgres  -- `postgresql://username:password@hostname/database`
* SQLite  -- `sqlite:////absolute/path/to/database`
* SQLite windows -- `sqlite:///c:/absolute/path/to/database`

Can also specify db driver for example, MySql with PyMySQL:

`mysql+pymysql://root:root@localhost/test_temporal'`

The db url must be stored in the app config dictionary key: `SQLALCHEMY_DATABASE_URI`. Another config
setting is SQLALCHEMY_COMMIT_ON_TEARDOWN. When set to True to enable automatic commits of database 
changes at the end of each request

see: http://flask-sqlalchemy.pocoo.org/2.1/config/

```
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/test_temporal'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

The object instantiated from class SQLAlchemy represents the database and provides
access to all the functionality of Flask-SQLAlchemy.

## Model definitions

The model for a given database table is typically a Python class with attributes that match the 
columns of a corresponding database table.

http://flask-sqlalchemy.pocoo.org/2.1/models/

The base class for models is the `db.Model` class, with the `db.` being the object created when 
initializing the SQLAlchemy plugin (Model is a _declarative base_ which can be used to declare models). 

### example model class definitions

```
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref=db.backref('role', lazy='joined'), lazy='joined')
    
    def __init__(self, rolename):
        self.name = rolename
    
    def __repr__(self):
        return '<Role %r>' % self.name
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    def __repr__(self):
        return '<User %r>' % self.username
```

you should include a `__repr__()` method to give moels a string representation that can be used for 
debugging and testing

#### data models on multiple databases

You can specify mutliple databases (on different servers and platforms, i.e., MySql & SQLite) in 
your app's configuration that Flask-SQLAlchemy can use. You can then specify what database a `Model`
class should use with the `__bind_key__` attribute.

see: http://flask-sqlalchemy.pocoo.org/2.1/binds/

### column objects

To create the database column name that is different from the class attribute name, provide an 
optional string value, with the desired column name, as the first argument.

Otherwise the 1st parameter passed to the db.Column constructor is the database column type

| Type name | Python type | Description | 
| --------- | ----------- | ----------- |
| Integer | int | Regular integer, typically 32 bits |
| SmallInteger | int | Short-range integer, typically 16 bits |
| BigInteger | int or long | Unlimited precision integer |
| Float | float | Floating-point number |
| Numeric | decimal.Decimal | Fixed-point number |
| String | str | Variable-length string |
| Text | str | Variable-length string, optimized for large or unbound length |
| Unicode | unicode | Variable-length Unicode string |
| UnicodeText | unicode | Variable-length Unicode string, optimized for large or unbound length |
| Boolean | bool | Boolean value |
| Date | datetime.date | Date value |
| Time | datetime.time | Time value |
| DateTime | datetime.datetime | Date and time value |
| Interval | datetime.timedelta | Time interval |
| Enum | str | List of string values |
| PickleType | Any Python object | Automatic Pickle serialization |
| LargeBinary | str | Binary blob |

The remaining parameters to db.Column specify various configuration options

| option name | description |
| ----------- | ----------- |
| primary key | If set toTrue, the column is the table’s primary key |
| unique | If set toTrue, do not allow duplicate values for this column |
| index | If set to True, create an index for this column, so that queries are more efficient |
| nullable | If set toTrue, allow empty values for this column. If set toFalse, the column will not allow null values. |
| default | Define a default value for the column |

### relastionships

#### one to many

Relationships are defined with the relationship() function and the ForeignKey() Class.

If a relationship is being declared before the other table is created, strings lterals can be used to 
refer to classes that are not created yet.

in the Role class to define a one-to-many relationship...

`users = db.relationship('User', backref=db.backref('role', lazy='joined'), lazy='joined')`

_If you would want to have a one-to-one relationship you can pass `uselist=False` to `relationship()`._

in the User class...

`role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))`

* The actual FK is the `role_id` column on the `users` table. 
* The `users` attribtue on the `Role` class is a collection object that contains all of the `User` 
objects associated with the given roles tale record. 
* The `backref` named parameter creates a new attribute called `role` on the `User` class that 
can be used to access the one `Role` object associated with the `User` object. Use the `db.backref()`
funciton (as shown above) to specify how the data should be loaded on the `User` `role` attribute, else
`backref` can be set to a string litteral, e.g.: `role`
* The `lazy` named parameter defines when SQLAlchemy will load the data from the database

Posible values for the `lazy` named parameter are:
* `select` - the default, SQLAlchemy will load the data _as necessary_ in _one go_ using a standard select 
statement... _sounds like a second SQL statement is executed to get the child records, if and when they
are ever accessed_
* `immediate` - items are loaded when the source object is loaded _how are they loaded, we know its not
a joined query or a subquery, as thoses are separate settings below, so it it just a second SQL statment
that is exectued separately to get the child records, and if so, how is this different from `select`. 
maybe its that the 2nd query is executed right away, where `select` defers the execution until the 
data is needed? I'm not sure if this is a valid value as it is not mentioned on the plugin web site_
* `joined` - tells SQLAlchemy to load the relationship **in the same query** as the parent using a 
JOIN statement
* `subquery` - works like 'joined' but instead of a JOIN, a subquery is used
* `dynamic` - is special and useful if you have many items. Instead of loading the items SQLAlchemy 
will return another query object which you can further refine before loading the items. This is 
usually what you want if you expect more than a handful of items for this relationship.

#### many to many example

For a many-to-many relationships you will need to define a _helper_ table that is used for the 
relationship. For the _helper_ table, a class derived from the Table Class should be used instead of
a class derived from the Model class.

```
tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('page_id', db.Integer, db.ForeignKey('page.id'))
)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('pages', lazy='dynamic'))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
```

from the Flask-SQLAlchemy web page: http://flask-sqlalchemy.pocoo.org/2.1/models/
> Here we configured Page.tags to be a list of tags once loaded because we don’t expect too many 
> tags per page. The list of pages per tag (Tag.pages) however is a dynamic backref. As mentioned 
> above this means that you will get a query object back you can use to fire a select yourself.

## database access via the Python Shell

When using the Flask-Script plugin, call the python script passing an argument value of `shell`

`python <script-name>.py shell`

Then import the `db` object created as part of the applicaiton initialization (*)

`from <module> import db`

Import the `Model` classes

`from <module> import <Model class 1>, <Model class 2>, ...`

(*) see the Flask-Sript / Shell section above for information on how to automate the import of objects


### creating, dropping, inserting, updating & deleting
you can then issue database commands via the `db` object

* drop all tables from the database that are specified as `Model` clases with: `db.drop_all()`
* create all tables in the database that are specified as `Model` clases with: `db.create_all()`
* create `Model` objects and add them to the `db.session` via `db.session.add(<model-obj>)`
* delete `Model` objects from a table: `db.session.delete(<model-obj>)` _note requires having the
model object loaded before it can be deleted_
* to update a `Model` object that has been loaded from the database, just modify the objects attributes,
add it to the session and commit the changes. 
* commit `Model` objects added to the `db.session` with: `db.session.commit()`
* rollback with: `db.session.rollback()`

Inserting data into the database is a three step process:
1. Create the Python object
2. Add it to the session
3. Commit the session

you can create _child_ objects and add them to the _parent_ object's collection, this will
establish the FK relationship for the records.

```
>>> user_role = Role(name='User')
>>> user_role.users.append(user_john = User(username='john'))
>>> user_role.users.append(user_john = User(username='mary'))
```

Alternatively, you can set the _parent_ object directly on the _child_ object's parent attribute:

```
>>> admin_role = Role(name='Admin')
>>> user_dave = User(username='david', role=admin_role)
>>> user_hal = User(username='HAL 9000', role=admin_role)
```

### querying

Flask-SQLAlchemy provides a `query` attribute on your Model class to query the database.

#### filters
* filter()
* filter_by()
* limit()
* offset()
* order_by()
* group_by()

#### executors

* all()
* first()
* get()
* first_or_404()
* get_or_404()
* count()
* paginate()


When you access the `query` attribute you will get back a new `query object` over **all** records. 
You can then use methods like `filter_by()` to filter the records before you fire the _SQL select_ with 
`all()` or `first()`. If you want to access the records by primary key, you can also use `get()`. sort
records with `order_by()`. Addvanded filtering with `filter()`


```
User.query.all()                                              # get all records
User.query.filter_by(username='peter').first()                # simple filter_by
User.query.filter(User.email.endswith('@example.com')).all()  # advanced filter
User.query.order_by(User.username)                            # order_by, gets all recs, no all() needed
User.query.limit(10).all()                                    # get the first 10 records
User.query.get(1)
```

if you already have a `Model` object read in from the database, you can use it with `filter_by()`. To see 
the SQL being generated, convert the query object to a string

```
role_1 = Role.query.get(1)
qry_obj = User.qyery.filter_by(role=role_1)
result_set = qry_obj.all()
print(str(qry_obj))
```

### accessing the underlying query object for _relationships_

By changing the `lazy` parameter value of a relationship to `dynamic`, when you access the relationship
collection object, you will get back a query object that has not been executed yet, so you can modify it
before it is executed and results are returned.

```
# back in the User Model class...
#    users = db.relationship('User', backref='role', lazy='dynamic')

role_1 = Role.query.get(1)
users.order_by(User.username).all()
```

# Flask-Migrate (alembic)

Alembic is a database migration framework. In the same way source code version control tools keep 
track of changes to source code files, a database migration framework keeps track of changes to a 
database schema, and then incremental changes can be applied to the database.

http://alembic.zzzcomputing.com/en/latest/

http://flask-migrate.readthedocs.io/en/latest/

## install

To use Alembic with Flask, you install & use the Flask-Migrate plugin.

`pip install flask-migrate`

## use

Alembic can be invoked via Flask-Script, by adding a new command to the manager.

```
from flask.ext.migrate import Migrate, MigrateCommand
    
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
```
Before database migrations can be maintained, it is necessary to create a 
migration repository with the init subcommand:

`python <module-name>.py db init`

This command creates a migrations folder, where all the migration scripts will be stored. The 
files in a database migration repository must always be added to version control along with the 
rest of the application.

### migration scripts

### create migration script
python hello.py db migrate -m "initial migration"

### apply migration script
python hello.py db upgrade

Two functions: `upgrade()` - applies the database changes that are part of the migration. And 
`downgrade()` -  removes them.

Alembic migrations can be created manually or automatically using the `revision` and `migrate` 
sub-commands, respectively.

A manual migration creates a migration skeleton script with empty upgrade() and downgrade() 
functions that need to be implemented by the developer using directives exposed by Alembic’s 
Operations object. 

An auto‐matic migration, on the other hand, generates the code for the upgrade() and downgrade() 
functions by looking for differences between the model definitions and the current state of the 
database.

_Automatic migrations are not always accurate and can miss some details. Migration scripts generated 
automatically should always be reviewed. n particular, Alembic is currently unable to detect table name changes, 
column name changes, or anonymously named constraints_

see: http://alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect

sample **generation** of a migration script:

    (venv) $ python hello.py db migrate -m "initial migration"
    INFO  [alembic.migration] Context impl SQLiteImpl.
    INFO  [alembic.migration] Will assume non-transactional DDL.
    INFO  [alembic.autogenerate] Detected added table 'roles'
    INFO  [alembic.autogenerate] Detected added table 'users'
    INFO  [alembic.autogenerate.compare] Detected added index
    'ix_users_username' on '['username']'
      Generating /home/flask/flasky/migrations/versions/1bc
      594146bb5_initial_migration.py...done

sample **execution** of the generated migration script:

    (venv) $ python hello.py db upgrade
    INFO  [alembic.migration] Context impl SQLiteImpl.
    INFO  [alembic.migration] Will assume non-transactional DDL.
    INFO  [alembic.migration] Running upgrade None -> 1bc594146bb5, initial migration

For a first migration, this is effectively equivalent to calling db.create_all(), but in successive migrations the 
upgrade command applies updates to the tables without affecting their contents.

# Flask-Mail

## install

`pip install flask-mail`

## app config

* MAIL_HOSTNAME - default localhost
* MAIL_PORT - default 25
* MAIL_USE_TLS - default False: Enable Transport Layer Security (TLS) security
* MAIL_USE_SSL - default False: Enable Secure Sockets Layer (SSL) security
* MAIL_USERNAME
* MAIL_PASSWORD

_Note: usernames and passwords should not be directly included in the script, put them in 
`$ENVIRONMENT_VARIABLES` instead._

### example config

```
import os
# ...
app.config['MAIL_SERVER'] = 'smtp.googlemail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
```
## usage

### dummy email account created to test with

```
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'xxx@yyy.org'
app.config['MAIL_PASSWORD'] = 'blahblahblah'
```

see: https://www.lifewire.com/what-are-the-gmail-smtp-settings-1170854

### tesing from the python shell

```
>>> from flask_mail import Mail, Message
>>> from hello import mail
>>> msg = Message('test subject', sender='flask.framework@gmail.com', recipients=['gskluzacek@gmail.com'])
>>> msg.body = 'this is a test, this is only a test... if this had been a real emergency, kiss your sweet ars good-bye!'
>>> msg.html = '<b>this is a test, this is only a test... if this had been a real emergency, kiss your sweet ars good-bye!</b>'
>>> with app.app_context():
...     mail.send(msg)
```

### sending mail - sample code

```
from flask.ext.mail import Message 

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
```

## sending mail in a separate thread - sample code

```
from threading import Thread 

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
    
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs) 
    thr = Thread(target=send_async_email, args=[app, msg]) thr.start()
    
    return thr
```

### sending email with the Celery Task Queue

see:
* https://blog.miguelgrinberg.com/post/using-celery-with-flask
* http://www.celeryproject.org

# Large App Directory Structure

## first pass

```
└── flasky
    ├── config.py
    ├── manage.py
    ├── app
    │   ├── __init__.py
    │   ├── main
    │   │   ├── __init__.py
    │   │   ├── errors.py
    │   │   ├── forms.py
    │   │   └── views.py
    │   ├── email.py
    │   ├── models.py
    │   ├── templates
    │   │   ├── 404.html
    │   │   ├── 500.html
    │   │   ├── base.html
    │   │   ├── index.html
    │   │   └── mail
    │   │       ├── new_user.html
    │   │       └── new_user.txt
    │   └── static
    │       └── favicon.ico
    ├── data-<environment>.sqlite
    ├── migrations
    │   ├── README
    │   ├── alembic.ini
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions
    │       └── 38c4e85512a9_initial_migration.py
    ├── tests
    │   ├── __init__.py
    │   └── test_basics.py
    ├── venv
    │   ├── ...
    │   └── ...
    ├── requirements.txt
    ├── LICENSE
    └── README.md
```

## config.py

contains Class definitions for the conf base class and derived config classes for each environment.

The config class to use is stored in an environment variable and passed to the `create_app()` call 
in the `manage.py` script.

## manage.py

Implements the logic to instantiate the app object with the desired configuration by calling the
`create_app()` function located in the `app/__init__.py` file.

Also implements the code needed to do db updates via alembic, and the python shell command.

## app directory

This is the Application (python) package, so it includes an `__init__.py` file.

The application package is where all the application code (modules and other application sub 
packages), templates, static files and any other application resources live.

We have the main package (contains an `__init__.py` file), and the email.py & models.py modules.

# User Auth

## Password Hashing

## Auth Blueprint

## Using Flask-Login for user auth

### protecting routes

### the login form & signing users in/out

## New User Registration

## Account Confirmation

## Account Management

# User Roles

## Representing Roles

## Role Assignment

## Role Verification

# User Profiles

## Profile Info

## User Profile Page

## Profile Editor

### for the user

### for the Admin

## Avitars

# Application logic: Blog Post

# Application logic: Followers

# Application logic: User Comments

# Application logic: Blog Post

# RESTful API

# TLM: Testing

# TLM: Performance

# TLM: Deployment




