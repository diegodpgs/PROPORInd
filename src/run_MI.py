from MImodel import *
import os
import argparse
import numpy as np


def getFileName(language,arguments):

    saida = '%s__%d__%d__%s.txt' % (language,arguments['max_d_r'],arguments['max_s'],arguments['smoothing'])
    return saida

def runExperiments(language,data_train,data_test_file_name,smoothing,max_d_r,max_s):
  arguments = {'smoothing':smoothing,
               'max_d_r':max_d_r,
               'max_s':max_s}

  MM = MImodel(max_s)
  MM.train(data_train,smoothing)


  return MM.testExp(data_test_file_name,language,arguments['max_d_r'],arguments['max_s'])



parser = argparse.ArgumentParser(description='Indigenous languages')
parser.add_argument('--PATH',default='/home', type=str,help="CONLLU files PATH")
parser.add_argument('--max_d_r',default='2',type=str,help='permutation distance between two tokens. Use , to separated different values')
parser.add_argument('--max_s',default='40',type=str,help='The maximum sentence length. Use , to separated different values')
args = parser.parse_args()




language_data = {}


previous_dir = '/'.join(args.PATH.split('/')[0:-2])

for language in os.listdir(args.PATH):
  if '.' not in language:
    folder = [{} for i in range(5)]

    for file_name in os.listdir(args.PATH+'/'+language):


      PATH = args.PATH+language+'/'+file_name
      folder_number = int(file_name.split('__')[1])


      folder[folder_number][file_name.split('__')[2].split('.')[0]] = PATH

    language_data[language] = folder


results_MI = open('%s/MI_results/results_MI.txt' % previous_dir,'w')

for max_s in [int(i) for i in args.max_s.split(',')]:
  max_d_r_list = [int(i) for i in args.max_d_r.split(',')]
  max_d_r_list.append(max_s)

  for max_d_r in max_d_r_list:
    for language, data in language_data.items():
      uda_average, dda_average = [],[]
      for folder_number, dfolder in enumerate(data):
          UDA,DDA = runExperiments(language,
                                      open(dfolder['train']).read().split('\n'),
                                      dfolder['test'],
                                      'laplace',max_d_r,max_s)
          uda_average.append(UDA)
          dda_average.append(DDA)

      results_MI.write('%d;%d;%s;%.4f;%.4f\n' % (max_s,max_d_r,language,np.average(uda_average),np.average(dda_average)))
