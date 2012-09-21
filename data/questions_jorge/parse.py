import re

item_regex = re.compile(r'[A-Z]{1}[0-9]{1,4}([A-Za-z]{1,2})?')
text_area_regex = re.compile(r'\{[A-Z]+\}')

files =  [
'ESS1_AT_deu.txt',
'ESS1_BE_fra.txt',
'ESS1_BE_nld.txt'
]
for file_name in files:

	file = open('/tdev/projects/sqp_project/data/questions_jorge/%s' % file_name)

	round_name, country_iso, language_iso = file_name.replace('.txt', '').split('_')

	key = None
	questions = {}
	text_areas = ['INTRO', 
	              'QUESTION', 
	              'ANSWERS']


	for line in file:
		if item_regex.match(line):
			key = line.strip()
			questions[key] = {'INTRO'   : '',
							  'QUESTION' : '',
							  'ANSWERS'  : ''}

			current_text_area = 'QUESTION'
			continue
		elif text_area_regex.match(line):
			current_text_area = line.strip().replace('{', '').replace('}', '')
			if current_text_area not in text_areas:
				raise Exception('Bad text area ""' % current_text_area)
			continue
		if key:
			questions[key][current_text_area] += line

	for key in questions:
		print round_name, country_iso, language_iso
		print 'ITEM: ' + key
		print 'INTRO: ' + questions[key]['INTRO']
		print 'QUESTION: ' + questions[key]['QUESTION']
		print 'ANSWERS: ' + questions[key]['ANSWERS']

	
		print '-----------------------'