

import gc

def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    credit:http://djangosnippets.org/snippets/1949/
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


def run_calculation_on_object(calculation, object, verbose = False):
     
      
    new_value = calculation.calculate(object)
    
    if calculation.save_to_field != False:
        old_value = getattr(object, calculation.save_to_field)
        
        if old_value != new_value :
            setattr(object, calculation.save_to_field , new_value)
            object.save()
            
        if verbose:
            print 'OBJECT \'%s\' FIELD \'%s\' SET TO: %s' % (object, calculation.save_to_field, new_value)
        
        
def run_calculation(calculation, object = False, verbose = False):
                
    count = 0;
    
    if hasattr(calculation, 'init'):
        calculation.init()
    
    if object :
        run_calculation_on_object(calculation, object, verbose)
    else :
        queryset = queryset_iterator(calculation.model.objects.all(), calculation.query_set_chunk_size) 
        for obj in queryset: 
            run_calculation_on_object(calculation, obj, verbose)
            count += 1
         
    if verbose:            
        print 'Total model objects processed: %s' % count       
        
    if hasattr(calculation, 'close'):
        calculation.close()  
        
class Calculation():
    
    #The model related to this calculation, an object from this model will be passed to calculate
    #This is also the model which will have its objects iterated over
    model  = False
    
    #Which field to save the return value to.
    #For example, if you want to save the return of run_calculation to the field total to sum up
    #two other fields,
    #set field to the string "total" This field must exist in the model of this calculation
    save_to_field = False
    
    #How many rows to iterate over for the model (if called from the command line or run_calculation
    query_set_chunk_size = 1000
    
    #This gets called only once before all the calculations are run
    #If you want to open a log file, it may be opened here
    def init(self):
        pass

    #This gets called only once after all the calculations are run
    #If you want to close a log file, it may be closed here
    def close(self):
        pass
    
    #The actual calculation
    #object is an single object of the model specified in model
    #This function should return a value if field is not False. The 
    #returned value will be stored in field
    def calculate(self, object):
        pass