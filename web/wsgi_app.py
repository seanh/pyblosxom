"""
WSGI application launcher for Pyblosxom.


Dependencies:
    - Pyblosxom 1.2+
    - wsgiref library from http://cvs.eby-sarna.com/wsgiref/
    - for mod_python: mp_wsgi_handler.py (mod_python wsgi wrapper)
        from http://www.c-area.ch/code/
    - for twisted: twisted_wsgi.py (twisted wsgi wrapper)
        from http://svn.webwareforpython.org/WSGIKit/trunk/wsgikit/


Configuration:
    - put this file in your weblog folder (where pyblosxom.cgi is)
    - mod_python:
        Note: If you have a folder in your document root that has the same name as the 
          Location used below, the SCRIPT_NAME and PATH_INFO variables will be broken.
          You should keep your blog's files outside your document root.
        <Location /weblog>
            PythonDebug Off
            SetHandler python-program
            # set PythonPath to the folders containing the files.
            PythonPath "['/path/to/mp_wsgi_handler', '/path/to/wsgi_app']+sys.path"
            PythonHandler mp_wsgi_handler::wsgi_handler
            # This should be the same as the Location above
            PythonOption ApplicationPath /weblog
            PythonOption application wsgi_app::application
        </Location>
        

Todo:
    - example configuration for twisted
    - more documentation

$Id$
"""
__author__ = "Steven Armstrong <kaidon at users dot sourceforge dot net>"
__version__ = "$Revision$ $Date$"
__url__ = "http://pyblosxom.sourceforge.net/"
__description__ = "WSGI application launcher for Pyblosxom"
__license__ = "Pyblosxom"


# Python imports
import sys

# Pyblosxom imports
from config import py as cfg
if cfg.has_key("codebase"):
    sys.path.insert(0, cfg["codebase"])

from Pyblosxom.pyblosxom import PyBlosxom
from Pyblosxom import tools

_debug = False

def _getExcInfo():
    try: from cStringIO import StringIO
    except ImportError: from StringIO import StringIO
    import traceback
    (exc_type, exc_value, tb) = sys.exc_info()
    exc_file = StringIO()
    traceback.print_exception(exc_type, exc_value, tb, file=exc_file)
    exc_string = exc_file.getvalue()
    return exc_string

def application(env, start_response):

    try: # regular application code here

        # ensure that PATH_INFO exists. a few plugins break if this is missing.
        if not 'PATH_INFO' in env:
            env['PATH_INFO'] = ""

        p = PyBlosxom(cfg, env)
        p.run()
    
        response = p.getResponse()
    
        if _debug:
            import os
            logFile = os.path.join(cfg.get('logdir', '/tmp'), 'pyblosxom.log')
            tools.make_logger(logFile)
            tools.log("status: %s" % response.status)
            tools.log("headers: %s" % response.headers)

        write = start_response(response.status, list(response.headers.items()))
        response.seek(0)
    
        # FIXME: somehow Firefox doesn't like this. using mod_python tables and CSS get messed up. why?
        #return response
        
        # so do it like this, which works nicely
        return [response.read()]

    except:
        # FIXME: it would be cool if we could catch a PyblosxomError or something here
        #  and let the server handle other exceptions.
        status = "500 Oops"
        response_headers = [("content-type", "text/plain")]
        start_response(status, response_headers)
        result = ["Pyblosxom WSGI application: A server error occurred.  Please contact the administrator."]
        if _debug:
            exc_string = _getExcInfo()
            tools.log(exc_string)
            result.append("\n")
            result.append(exc_string)
        return result


# vim: tabstop=4 shiftwidth=4