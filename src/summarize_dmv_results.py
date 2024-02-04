import os
import argparse
import numpy as np
from udmodel import *

parser = argparse.ArgumentParser(description="results DMV")
parser.add_argument('--PATH_R',type=str,default=0,help='Path of DMV result files')
parser.add_argument('--PATH_CV',type=str,default=0,help='Data CV files')
args = parser.parse_args()


def map_sentence_code_to_relations_DMV(PATH):
	results_dmv_mapped = {}

	for file_name in os.listdir(PATH):

		if 'resultado_' not in file_name:
			continue
		language = file_name.split('_')[1]
		folder = file_name.split('_')[2]

		if language not in results_dmv_mapped:
			results_dmv_mapped[language] = {}

		for line in open(PATH+'/'+file_name).read().split('\n'):
			if '<#>' in line:
				sentence_code = line.split('|')[1].strip()
				relations = line.split('|')[0].replace(')<#>(','<#>')[1:-2].replace(' ','').strip().split('<#>')
				relations_DMV = []

				for i in relations:
					if int(i.split(',')[0]) == -1 or int(i.split(',')[1]) == -1:
						continue
					relations_DMV.append((int(i.split(',')[0]),int(i.split(',')[1])))

				results_dmv_mapped[language][sentence_code] = relations_DMV

	return results_dmv_mapped


def map_code_to_gold_relations(PATH):
	UDM = UDModel()

	gold_conllu_mapped = {}

	for language in os.listdir(PATH):
		gold_conllu_mapped[language] = {}

		for file_name in os.listdir(PATH+'/'+language):

			if 'test.conllu' in file_name:
				file_PATH = PATH+'/'+language+'/'+file_name
				conllu_parsed = UDM.parseConllu(file_PATH)

				for i in conllu_parsed:
					code = i[1][0]
					r = []

					for ri in i[1][1]:
						if int(ri['ID']) == 0 or int(ri['HEAD']) == 0:
							continue
						r.append((int(ri['ID'])-1,int(ri['HEAD'])-1))

					gold_conllu_mapped[language][code] = r

	return gold_conllu_mapped


def compare_relations(gold,estimated):

	if len(gold) == 0 or len(estimated) == 0:
		return 0,0

	DDA = len(set(gold).intersection(set(estimated)))/len(gold)	
	UDA = 0

	for e in estimated:
		dh = e
		hd = (e[1],e[0])

		if dh in gold:
			UDA += 1
		elif hd in gold:
			UDA += 1

	UDA = UDA/len(gold)

	return UDA,DDA





gold_relations = map_code_to_gold_relations(args.PATH_CV)
dmv_relations = map_sentence_code_to_relations_DMV(args.PATH_R)



if 'summarized' not in os.listdir(args.PATH_R):
	os.mkdir(args.PATH_R+'/summarized')


for language, codes in dmv_relations.items():
	summarized_language = open('%s/summarized/%s.txt' % (args.PATH_R,language),'w')

	results_UDA_DDA = []
	for code, relations in codes.items():
		
		if code in gold_relations[language]:
			results_UDA_DDA.append(compare_relations(gold_relations[language][code],relations))

	summarized_language.write('\n'.join(['UDA_DDA;%.5f;%.5f' % (r[0],r[1]) for r in results_UDA_DDA]))



# def summarize_results():
# 	languages = {}

# 	for file_name in os.listdir(args.PATH):
# 		name = file_name.split('_')[1]

# 		if name not in languages:
# 			languages[name] = {'UDA':[],'DDA':[]}

# 		result_data_file = open(args.PATH+'/'+file_name).read().split('\n')

# 		for index, line in enumerate(result_data_file):

# 			if 'epoch 9, ' in line:
# 				languages[name]['UDA'].append(float(result_data_file[index-1].split('undir ')[1].split(',')[0]))
# 				languages[name]['DDA'].append(float(result_data_file[index-1].split(' dir ')[1]))



# 	for language, data in languages.items():
# 		print('%s;%.3f;%.3f' % (language,np.average(data['UDA']),np.average(data['DDA'])))
# 		for index in range(len(data['UDA'])):
# 			print('%s;%s;%.5f;%.5f' % (language,data['UDA'][index],data['DDA'][index]))


# if "__main__":
# 	summarize_results()
	

