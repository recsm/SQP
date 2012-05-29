from django.conf import settings


import Pyro4
# MD5Sum of a now-famous password. Pyro uses this to sign the message
#   Need to make sure nameserver and client use this 
#   or more easily just export PYRO_HMAC_KEY='2d736347ff7487d559d7fb3cfc1e92dd'
Pyro4.config.HMAC_KEY = "2d736347ff7487d559d7fb3cfc1e92dd"

try:
    Pyro4.config.HOST = settings.PYRO_HOST
except:
    pass

API_BASE_URL = '/sqp/api'

class URL():
    @staticmethod
    def question(id):
        return '%s/question/?questionId=%s' % (API_BASE_URL, id)
    
    @staticmethod
    def study(id):
        return '%s/study/?studyId=%s' % (API_BASE_URL, id)
    
    @staticmethod
    def item(id):
        return '%s/item/?itemId=%s' % (API_BASE_URL, id)
    
    @staticmethod
    def coding(question_id, characteristic_id):
        return '%s/coding/?questionId=%s&characteristicId=%s' % \
        (API_BASE_URL, question_id, characteristic_id)
        
    @staticmethod
    def question_coding_history(question_id):
        return '%s/questionCodingHistory/?questionId=%s' % \
        (API_BASE_URL, question_id)
        

def get_branch(charset_id, label):
    
    """Retrieve the branch associated with the given CharacteristicSet
       and linked to the Label passed. If found return it, if not None."""
       
    from sqp.models import Branch
    try:
        return Branch.objects.get(label = label, 
                characteristicset__id = charset_id)
    except Branch.DoesNotExist: # no branch with that label in that cSet
        return None

def get_label(characteristic):
    
    """Given a POST request and a non-categorical characteristic, determine
       which label to apply, and return it."""
       
    from sqp.models import Label  
    labels = Label.objects.filter(characteristic = characteristic, compute = True)
    return labels[0] # TODO: evaluate rules (now just taking the first found)


def get_codes_list(codes):
    codes_list = []
    for code in codes:
        code_dict = {'code' : code['code'] ,
                     'characteristic_short_name' : code['characteristic'].short_name} 
        codes_list.append(code_dict)
    return codes_list



def get_predictor():
    """This does a round robin of predictors [predictor_0, predictor_1], or just returns 'predictor' 
       if there is only one as defined in settings.PREDICTOR_COUNT"""
 
    if settings.PREDICTOR_COUNT == 1:
        predictor_name = 'predictor'
    else:
        predictor_name =  'predictor_%s' % get_predictor.predictor_counter
        
        if get_predictor.predictor_counter == settings.PREDICTOR_COUNT - 1:
            get_predictor.predictor_counter = 0
        else:
            get_predictor.predictor_counter += 1 
    
       
    return Pyro4.Proxy("PYRONAME:%s" % predictor_name )     
    

get_predictor.predictor_counter = 0
    
    
