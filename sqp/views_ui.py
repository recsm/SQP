import json
import inspect
import traceback
import sys

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist

from sqp import views_ui_exceptions 
from sqp.views_ui_calls import calls
from sqp import models

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

# Load the new user interface for the coding page. 
@login_required
def load_ui(request):
    
    return render_to_response('ui/coder_ui.html', {'title' : 'SQP Coder',
                                                   'user'  : request.user})


def format_error_message(exception_inst):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return traceback.format_exception(exc_type, exc_value, exc_traceback)

def http_json_service(request, function_name):
    
    obj_return = None
     
    try:
        
        #First find which function to call from the calls tuple
        call = False
        for call in calls:
            #Check to see if this call matches the call_function
            if function_name == call['name'] \
            and call['method'] == request.method:
                break
        if not call:
            raise views_ui_exceptions.ServiceError(views_ui_exceptions.error_bad_request, \
                                                    'Invalid call to %s' % function_name)
         
        #Standardize our params from GET into kwargs for our function
        kwargs = {}
        
        #Get the expected args from a function
        argspec         = inspect.getargspec(call['function']) 
        expected_args   = argspec.args
        default_args    = []
        if argspec.defaults:
            args_w_defaults = expected_args[-len(argspec.defaults):]
            for arg in args_w_defaults:
                default_args.append(arg)
        
            #slice off the args that have defaults from the expected args
            expected_args = expected_args[:-len(default_args)]
        
        for k, v in request.GET.iteritems():
            #Don't allow a user or obj_request_body to be passed directly from a param ... even though it should be impossible anyway
            if str(k) not in ['user','obj_request_body'] and k in argspec.args:
                kwargs[str(k)] = str(v)
    
        #If there is a user param, try to set it from the request or raise a login required exception
        if call['user_required'] and request.user.is_authenticated():
            kwargs['user'] = request.user
        elif call['user_required']:
            raise views_ui_exceptions.ServiceError(views_ui_exceptions.login_required, \
                                                    'Login required for function %s' % function_name)   
        
        #If the method is POST or PUT we make pass along the request json serialized into python
        try:                                            
            if request.method in ['POST', 'PUT']:
                kwargs['obj_request_body'] = json.loads(request.raw_post_data)
        except:
            raise views_ui_exceptions.ServiceError(views_ui_exceptions.error_bad_request, \
                                                    'Error reading in json from request');
        
        #Validate we have all of the required arguments
        for arg in expected_args:
            if arg not in kwargs.keys() and arg not in default_args:
                raise views_ui_exceptions.ServiceError(views_ui_exceptions.error_bad_request, \
                                                    'Missing argument %s. This call requires the arguments (%s).' % (arg, ', '.join(expected_args)))
        
        function_return = call['function'](**kwargs)
        
       
        
        if call['return_type'] == 'direct':
            #Return the result directly
            string_return = function_return   
        elif call['return_type'] == 'payload_meta_success':
            #We expect the return type to be a list of either 3 or 5 items
            #5 items indicates there is error information in the last two items
            #3 items indicates this is a normal return
            #The items returned from the function are expected to be in the order payload, meta, success
            #success = 1 = ok
            #success = 0 = failed
            if len (function_return) == 5:
                #call our function     
                payload, meta, success, error_key, error_message = function_return
                #Create the proper json structure 
                obj_return = {'payload'       : payload, 
                              'meta'          : meta,
                              'success'       : success,
                              'error_key'     : error_key,
                              'error_message' : error_message}
            elif len (function_return) == 3:
                payload, meta, success = function_return
                #Create the proper json structure 
                obj_return = {'payload' : payload, 
                              'meta'    : meta,
                              'success' : success}
            
      
          
          
            
        
    
    except views_ui_exceptions.ServiceError as inst:
        #exc_type, exc_value, exc_traceback = sys.exc_info()
        obj_return = {'success' : 0, 
                      'payload' : [],
                      'meta' : {}, 
                      'error_key' : inst.error_key,
                      'error_message' :  format_error_message(inst)}
    except ObjectDoesNotExist as inst:
        #exc_type, exc_value, exc_traceback = sys.exc_info()
        obj_return = {'success' : 0, 
                      'payload' : [],
                      'meta' : {},
                      'error_key' : views_ui_exceptions.object_not_found,
                      'error_message' :  format_error_message(inst)}
    except Exception as inst:
        """See http://docs.python.org/library/traceback.html for info on traceback"""
        obj_return = {'success' : 0, 
                      'payload' : [],
                      'meta' : {}, 
                      'error_key' : views_ui_exceptions.server_error, 
                      'error_message' :  format_error_message(inst)}

   
    if obj_return is not None:
        string_return = json.dumps(obj_return)
        
    return HttpResponse(string_return)
                

def service_live_doc(request, function_name = False, method=False):
    #First find which function to call from the calls tuple
     
    for call in calls:
        #Auto select first function for ease
        if not function_name:
            break
        #Check to see if this call matches the call_function
        if function_name == call['name'] \
        and call['method'] == method:
            break
    
    #Get the expected args from a function
    argspec         = inspect.getargspec(call['function']) 
    expected_args   = argspec.args
    default_args    = []
    #Defualt values are listed corresponding to the last args in expected args, here we find them
    if argspec.defaults:
        args_w_defaults = expected_args[-len(argspec.defaults):]
        for arg, value in zip(args_w_defaults, argspec.defaults):
            default_args.append({'name' : arg, 'value' : value})
        
        #slice off the args that have defaults
        expected_args = expected_args[:-len(argspec.defaults)]
        
    return render_to_response('sqp/live_api_doc.html', 
           {'selected_call'   : call,
            'expected_args'   : expected_args,
            'default_args'    : default_args,
            'function_doc'    : call['function'].__doc__,
            'function_name'   : call['function'].__name__,
            'source_lines'    : inspect.getsource(call['function']),
            'function_file'   : inspect.getfile(call['function']),
            'function_line'   : inspect.getsourcelines(call['function'])[1],
            'calls'           : calls},
           context_instance=RequestContext(request))
