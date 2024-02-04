import os
from udmodel import *
import argparse
import shutil

U = UDModel()


parser = argparse.ArgumentParser(description="statistical")
parser.add_argument('--PATH',type=str,default=0,help='CONLLU file paths')

args = parser.parse_args()


previous_dir = '/'.join(args.PATH.split('/')[0:-1])
if 'stats' not in os.listdir(previous_dir):
	os.mkdir(previous_dir+'/stats')
else:
	shutil.rmtree(previous_dir+'/stats')
	os.mkdir(previous_dir+'/stats')

print(previous_dir+'/stats')
for folder in os.listdir(args.PATH):

	if '.' not in folder:
		for file_name in os.listdir(args.PATH+'/'+folder):

			if '.conllu' in file_name:
				print('------------------------')
				if 'test' in file_name:
					U.statistical(open('%s/stats/%s_test.stat' % (previous_dir ,folder),'w'),args.PATH+'/'+folder+'/'+file_name)
				elif 'train' in file_name:
					U.statistical(open('%s/stats/%s_train.stat' % (previous_dir ,folder),'w'),args.PATH+'/'+folder+'/'+file_name)

