import re
from operator import attrgetter
import mysql.connector

con = mysql.connector.connect(user='root', password='fake', database='sqp')
con2 = mysql.connector.connect(user='root', password='fake', database='sqp')
cursor = con.cursor()
cursor_update=con2.cursor()

query=( "select id, admin from sqp_item")
cursor.execute(query)

query_update=("update sqp_item set admin_number=%s, admin_letter=%s, admin_subletter=%s where id=%s")

for (id, admin) in cursor:
	if re.match(r'^[A-Za-z]*[0-9]+[A-Za-z]*$', admin):
		letters=re.split('\d+', admin)
		letter=letters[0]
		number=filter(None,re.split('[A-Za-z]+',admin))[0]
		subletter=letters[1]
	else:
		if re.match(r'^[A-Za-z]*$',admin): 
			letter=admin
			number=None
			subletter=None
		else: # numbers letters numbers or whatever
			letter=admin
			number=None
			subletter=None
	cursor_update.execute(query_update, (number,letter,subletter, id))
	con2.commit()


cursor_update.close()
cursor.close()
con.close()
con2.close()
