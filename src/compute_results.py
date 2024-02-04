#@author: Diego Pedro, 13 January 2024
#@e-mail  diego.silva@ifam.edu.br
import os
import argparse
from udmodel import *



def compare(sentence_relation,sentence_length=10):
	print('----- Summarized results on sentence length <= %d-------' % sentence_length)
	results = [{'DDA':{},'UDA':{}} for i in range(sentence_length+2)]


	for r in sentence_relation:

		dep = ['<@>'.join(rd.lower().split('<@>')[0:-1]) for rd in r[0].split("<#>")]
		if len(dep) > sentence_length:
			continue
		map_DPREL = dict([(dep[index].lower(),rd.lower().split('<@>')[-1]) for index,rd in enumerate(r[0].split("<#>"))])
		number_of_relations = len(dep)
		
		if len(r[1]) < 4:
			continue

		for dprel in map_DPREL.values():
			
			if dprel not in results[number_of_relations]['DDA']:
				results[number_of_relations]['DDA'][dprel] = [0,0]
			results[number_of_relations]['DDA'][dprel][1] += 1
				
			if dprel not in results[number_of_relations]['UDA']:
				results[number_of_relations]['UDA'][dprel] = [0,0]
			results[number_of_relations]['UDA'][dprel][1] += 1

		

		for llm_r in r[1].lower().split("<#>"):
			dh = llm_r
			
			hd = '%s<@>%s' % (llm_r.lower().split('<@>')[1],llm_r.lower().split('<@>')[0])

			if dh in dep:
				dep.remove(dh)
				results[number_of_relations]['DDA'][map_DPREL[dh]][0] += 1
				results[number_of_relations]['UDA'][map_DPREL[dh]][0] += 1
			elif hd in dep:
				dep.remove(hd)
				results[number_of_relations]['UDA'][map_DPREL[hd]][0] += 1


	total_R = 0
	matchs_DDA = 0
	matchs_UDA = 0
	matchs_DDA_deprel = {}
	matchs_UDA_deprel = {}
	
	if [i['DDA']=={} for i in results].count(True) == len(results):
		print('Every sentence has length > than %d' % sentence_length)
		return 
	for index,r in enumerate(results):
		if r['DDA'] == {}:
			continue

		total_R += sum([values[1]  for dprel, values in r['DDA'].items()])

		for dprel, values in r['DDA'].items():
			matchs_DDA += values[0]

			if dprel not in matchs_DDA_deprel:
				matchs_DDA_deprel[dprel] = [0,0]
			matchs_DDA_deprel[dprel][0] += values[0]
			matchs_DDA_deprel[dprel][1] += values[1]

		for dprel, values in r['UDA'].items():
			matchs_UDA += values[0]

			if dprel not in matchs_UDA_deprel:
				matchs_UDA_deprel[dprel] = [0,0]
			matchs_UDA_deprel[dprel][0] += values[0]
			matchs_UDA_deprel[dprel][1] += values[1]


	print('UDA:%.4f DDA:%.4f [%d]' % (matchs_UDA/total_R,matchs_DDA/total_R,total_R))
	
	print('---UDA----')
	UDA = [(values[0]/values[1],dprel,values) for dprel, values in matchs_UDA_deprel.items()]
	UDA.sort()
	for i in UDA[::-1]:
		print('%.4f;%s;%s' % (i[0],i[1],str(i[2])))

	print('---DDA----')
	DDA = [(values[0]/values[1],dprel,values) for dprel, values in matchs_DDA_deprel.items()]
	DDA.sort()
	for i in DDA[::-1]:
		print('%.4f;%s;%s' % (i[0],i[1],str(i[2])))





def run():

	parser = argparse.ArgumentParser(description='Results')
	parser.add_argument('--PATHfile',type=str,help="file path of results")
	parser.add_argument('--sentLength',type=int,help="max length sentence")

	args = parser.parse_args()


	relations = []

	for message in open(args.PATHfile).read().split('>--<')[0:-1]:

		if len(message.split('\n')) == 4:
			
			chat = message.split('\n')[1].split('|:|')[1]
			dep  = message.split('\n')[2].split('|:|')[1]
			
			relations.append((dep,chat))

	compare(relations,args.sentLength)


