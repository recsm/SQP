from automtmm import walk_and_run

walk_and_run.walk_and_run_sqp('/home/daob/work/sqp_project/automtmm/analysesround4-new',
'/home/daob/work/sqp_project/temp', run_original = False)

sys.stderr.flush()


from sqp_project.sqp.models  import *

itemname = ('TRSTPRL', 'TRSTLGL', 'TRSTPLC', 'LRSCALE')


for name in itemname:
    item =Item.objects.get(name = name, study__id = 4)
    newq, created = Question.objects.get_or_create(item = item, language=Language.objects.get(iso='deu'), country = Country.objects.get(iso = ''))
    if created:
        newq.save()
        print "CREATED: %s " % newq
    else: print "%s already existed" % newq


#Check:
#	SI: slv
#	CH: deu
#	DE: deu

