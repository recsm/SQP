import re
from sqp_project.sqp.models import *

white = re.compile(r'[\n\r\t \s]')

countries = open('round5/countries', 'rb').readlines()

cnt_lans = ([white.sub('', cstr) for cstr in cnt_lan_str.split('*')] \
        for cnt_lan_str in countries)

round5_items = Item.objects.filter(study__id__exact = 5)

for cnt_lan in cnt_lans:
    print cnt_lan
    language = Language.objects.get(iso__exact = cnt_lan[2])
    country  = Country.objects.get(iso__exact = cnt_lan[0])

    for item in round5_items:
        print "Adding question for %s with country %s and language %s..."% \
                (item.admin, cnt_lan[0], cnt_lan[2])
        try:
            newq, new = Question.objects.get_or_create(item = item, 
                    language = language, country = country)
        except Exception, err:
            print "Error: could not because %s" % str(err)
            continue
        if not new: 
            print "Warning: already existed. Doing nothing." 
        newq.save()
