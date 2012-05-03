

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