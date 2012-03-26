from django.core.management.base import BaseCommand, CommandError
from sqp.models import Question, CharacteristicSet
from django.contrib.auth.models import User


class Command(BaseCommand):
    '''
        manage.py sqp update_complete userId questionId
    '''
    
    args = '<user_id question_id >'
    help = 'Updates a questions completeness after a coding choice is made'

    def handle(self, *args, **options):
        
        if len(args) != 2:
            raise CommandError('2 arguments were expected and %s were given. Please specify user_id question_id as arguments' % len(args))
         
        user      = User.objects.get(id=args[0])
        profile   = user.get_profile()
        
        question  = Question.objects.get(id=args[1])
        
        #update the completeness for the coding   
        for_charset = CharacteristicSet.objects.get(id=profile.default_characteristic_set_id)
        
        #lock
        question.update_completion(user=user, for_charset=for_charset) 
        #unlock