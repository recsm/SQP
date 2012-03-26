from sqp_project.sqp.models import *
import re

items = Item.objects.all()

findletter = re.compile(r'([A-Z]{1})([0-9]+)')
findtestnum = re.compile(r'TEST[A]*([0-9]+)', re.IGNORECASE)

for item in items:
	if item.admin:
		found = findletter.findall(item.admin)
		if found: found = found[0]
		item.admin_letter = found[0]
		item.admin_number = int(found[1])
	else:
		item.admin_letter = 'T'
		found = findtestnum.findall(item.name)
		if found: item.admin_number = int(found[0])

	item.save()


