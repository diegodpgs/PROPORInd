import os
import argparse
import numpy as np



parser = argparse.ArgumentParser(description="results DMV")
parser.add_argument('--PATH',type=str,default=0,help='Path of DMV result files')
parser.add_argument('--cv',type=int,default=0,help='0:One folder results 1:Five folders results')
args = parser.parse_args()


def summarize_results():
	languages = {}

	for file_name in os.listdir(args.PATH):
		name = file_name.split('_')[1]

		if name not in languages:
			languages[name] = {'UDA':[],'DDA':[]}

		result_data_file = open(args.PATH+'/'+file_name).read().split('\n')

		for index, line in enumerate(result_data_file):

			if 'epoch 9, ' in line:
				languages[name]['UDA'].append(float(result_data_file[index-1].split('undir ')[1].split(',')[0]))
				languages[name]['DDA'].append(float(result_data_file[index-1].split(' dir ')[1]))



	for language, data in languages.items():
		print('%s;%.3f;%.3f' % (language,np.average(data['UDA']),np.average(data['DDA'])))
		for index in range(len(data['UDA'])):
			print('%s;%s;%.5f;%.5f' % (language,data['UDA'][index],data['DDA'][index]))


if "__main__":
	if args.cv == 0:
		summarize_results()
	else:


