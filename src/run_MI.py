#@author: Diego Pedro, 13 January 2024
#@e-mail  diego.silva@ifam.edu.br
from MImodel import *
import os
import argparse
import numpy as np


def runExperiments(language,train_file_name,data_test_file_name,max_d_r,smoothing, max_l_train):

  MM = MImodel()

  MM.train(train_file_name,smoothing,max_l_train)
  return MM.testExp(data_test_file_name,language,max_d_r,max_l_train)



def init():
  parser = argparse.ArgumentParser(description='Indigenous languages')
  parser.add_argument('--PATH_cv',default='/home', type=str,help="cv folders")
  parser.add_argument('--max_d_r',default='2',type=str,help='permutation distance between two tokens. Use , to separated different values')
  parser.add_argument('--smoothing',default='null',type=str,help='laplace or edit')
  parser.add_argument('--max_l_train',default=10,type=int,help='The max len sentence allowed to train')
  args = parser.parse_args()

  return args


def getFiles_PATH(PATH_cv):

  language_data = {}
  for language in os.listdir(PATH_cv):

    if os.path.isdir(PATH_cv+'/'+language): #only folder
      folder = [{} for i in range(5)]

      for file_name in os.listdir(PATH_cv+'/'+language):
        local_PATH = PATH_cv+'/'+language+'/'+file_name

        folder_number = int(file_name.split('__')[1])
        folder[folder_number][file_name.split('__')[2].split('.')[0]] = local_PATH
      language_data[language] = folder

  return language_data


#(language,train_file_name,data_test_file_name,args):


def run_cv(args):

  previous_dir = '/'.join(args.PATH_cv.split('/')[0:-2])
  
  results_MI = open('%s/MI_results/results_MI_%d_%s.txt' % (previous_dir,args.max_l_train,args.smoothing),'w')
  
  language_data = getFiles_PATH(args.PATH_cv)
  max_d_r_list = [int(i) for i in args.max_d_r.split(',')]
  results_MI.write('max_d_r;max_l_train;language;UDA;DDA;syn_UDA;syn_DDA\n')
  for max_d_r in max_d_r_list:
      for language, data in language_data.items():
        uda_average, dda_average = [],[]
        for folder_number, dfolder in enumerate(data):
            UDA,DDA,syn_UDA,syn_DDA = runExperiments(language,
                                                      dfolder['train'],
                                                      dfolder['test'],
                                                      max_d_r,
                                                      args.smoothing,args.max_l_train)
            print(UDA)
            print(DDA)
            print(syn_UDA)
            print(syn_DDA)
            results_MI.write('%d;%d;%s;%.4f;%.4f;%s;%s\n' % (max_d_r,args.max_l_train,language,
                                                              UDA,DDA,str(syn_UDA),str(syn_DDA)))

args = init()
run_cv(args)