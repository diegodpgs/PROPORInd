import numpy as np
from scipy import stats
import os
import argparse


def test(mean_MI, values_DMV,alpha=0.05):
		student_scores = np.array([72, 89, 65, 73, 79, 84, 63, 76, 85, 75])
		mu = 70

		
		t_stat, p_value = stats.ttest_1samp(values_DMV, mean_MI)

		
		if p_value < alpha:
		    return (t_stat,p_value,"Reject the null hypothesis; there is a significant difference between the sample mean and the hypothesized population mean.")
		else:
		    return (t_stat,p_value,"Fail to reject the null hypothesis; there is no significant difference between the sample mean and the hypothesized population mean.")



def readMIresults(PATH_FILE):
	MI_results = {}

	for line in open(PATH_FILE).read().split('\n'):
		s = line.split(';')
		size = int(s[0])
		distance = int(s[1])
		language = s[2]
		UDA = float(s[3])
		DDA = float(s[4])

		if language not in MI_results:
			MI_results[language] = {}

		if size not in MI_results[language]:
			MI_results[language][size] = {}

		if distance not in MI_results[language][size]:
			MI_results[language][size][distance] = {'DDA':0,'UDA':0}

		MI_results[language][size][distance]['DDA'] = DDA
		MI_results[language][size][distance]['UDA'] = UDA

	return MI_results

def readDMVresults(PATH_FILE):
	DMV_results = {}

	for file_name in os.listdir(PATH_FILE):

		language = file_name.split('.txt')[0]

		if language not in DMV_results:
			DMV_results[language] = {'DDA':[],'UDA':[]}

		data = open(PATH_FILE+'/'+file_name).read().split('\n')

		for line in data:
			DMV_results[language]['UDA'].append(float(line.split(';')[1]))
			DMV_results[language]['DDA'].append(float(line.split(';')[2]))

	return DMV_results
			



parser = argparse.ArgumentParser(description="T-test")
parser.add_argument('--PATH_MI',type=str,default=0,help="PATH with the MI result files")
parser.add_argument('--PATH_DMV',type=str,default=0,help="PATH with the DMV result files summarized")
parser.add_argument('--size_len',type=int,default=10,help='Size length limit')


args = parser.parse_args()

MI_results = readMIresults(args.PATH_MI)
DMV_results = readDMVresults(args.PATH_DMV)


print('language;size;distance_MI;metric;MI;DMV;T-stat;P-value;result')
for language, sizes in MI_results.items():
	for distance,data in sizes[args.size_len].items():
		
		T = test(data['UDA'],DMV_results[language]['UDA'])
		print('%s;%d;%d;UDA;%.5f;%.5f;%.7f;%.7f;%s' % (language,args.size_len,distance,
															   data['UDA'],
															   np.average(DMV_results[language]['UDA']),
															   T[0],T[1],T[2]))
		T = test(data['DDA'],DMV_results[language]['DDA'])
		print('%s;%d;%d;DDA;%.5f;%.5f;%.7f;%.7f;%s' % (language,args.size_len,distance,
															   data['DDA'],
															   np.average(DMV_results[language]['DDA']),
															   T[0],T[1],T[2]))