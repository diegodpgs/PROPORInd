import os
import shutil
import argparse

def getSentences(conllu_file):
  sentences = []
  sentence = ''

  for line in open(conllu_file).read().split('\n'):
    if len(line) < 2:
        sentences.append(sentence)
        sentence = ''
    else:
       sentence += line+'\n'
  

  return sentences

def CV(sentences):

  folders_split = ['' for i in range(5)]
  folders = [{'train':'','test':''} for i in range(5)]

  
  for index in range(len(sentences)):
    folders_split[index % 5] += sentences[index]+'\n'

  for index in range(5):
    folders[index]['test']  = folders_split[index]
    folders[index]['train'] = ''.join(folders_split[0:index])+''.join(folders_split[index+1:])

  return folders

def getCVFolders(PATH_CONLLU):
  languages_CV = {}

  for language in os.listdir(PATH_CONLLU):
    PATH = '%s/%s' % (PATH_CONLLU,language)

    
    for arquivo in os.listdir(PATH):
      if '.conllu' in arquivo:
        folders = CV(getSentences(PATH+'/'+arquivo))
        languages_CV[language] = {'test':[f['test'] for f in folders],'train':[f['train'] for f in folders]}
  
  return languages_CV


def createFolders(PATH,folders):

  try:
    os.mkdir(PATH)
  except:
    print(PATH,' Already exist. All files within will be deleted.')
    shutil.rmtree(PATH)
    os.mkdir(PATH)


  for language, data in folders.items():
    os.mkdir('%s/%s' % (PATH,language))
    for index,conllu in enumerate(data['train']):
        file_name_train = '%s__%s__train.conllu' % (language,index)
        writerTR = open('%s/%s/%s' % (PATH,language,file_name_train),'w')
        writerTR.write(conllu)

    for index,conllu in enumerate(data['test']):
        file_name_train = '%s__%s__test.conllu' % (language,index)
        writerTR = open('%s/%s/%s' % (PATH,language,file_name_train),'w')
        writerTR.write(conllu)
  

parser = argparse.ArgumentParser(description='cross validation config')
parser.add_argument('--PATH_data',type=str,help='Data provided to cross validation. The Conllu files must be included withing a folder for each language.')
parser.add_argument('--PATH_dest',type=str,help='Folder wich will be included the cross validation files')
args = parser.parse_args()

if "__main__":
  folders = getCVFolders(args.PATH_data)  
  createFolders(args.PATH_dest,folders)