
error_bad_request = 'bad_request'
login_required    = 'login_required'           
server_error      = 'server_error'
object_not_found  = 'object_not_found'
no_permission     = 'no_permission'

class ServiceError(Exception):
    def __init__(self, error_key, error_message):
        self.error_key = error_key
        self.error_message = error_message
    def __str__(self):
        return repr(self.error_message)
    
    
    
