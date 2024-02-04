#@author: Diego Pedro, 13 January 2024
#@e-mail  diego.silva@ifam.edu.br
from udmodel import *
import argparse
import os
from openai import OpenAI
import time
import random
from compute_results import *

class llm_UD:

    def __init__(self,args):
        self.test = UDModel().parseConllu(args.PATHtest)
        self.train = UDModel().parseConllu(args.PATHtrain)
        self.max_len_sent_train = args.max_len_sent_train
        self.gpt_client = OpenAI(api_key=args.openkey)
        self.matchs_DDA = {}
        self.matchs_UDA = {}
        self.syntatic_relations_testset = {}
        self.guide = []
        self.parseGuide()

    def parseGuide(self):
      for conllu_parsed in self.train:

        pairs = ['(%s -> %s)'% (const['DEP'].lower(),const['HEAD'].lower()) for const in conllu_parsed[0]]
        sentence = conllu_parsed[1]
        
        self.guide.append((pairs,sentence))


    def generateGuide(self,fixed=0,shot=None):
        pairs = []
        sentences = []
        message = ""

        if fixed:
          for i in range(shot):
            pair,sentence = self.guide[i]
            pairs.append(pair)
            sentences.append(sentence)
        else:
          for i in range(shot):
            pair,sentence = None, None

            while True:
              pair,sentence = self.guide[random.randint(0,len(self.guide)-1)]
              if len(sentence.split()) > max_len_sent_train:
                continue
              else:
                break
            pairs.append(pair)
            sentences.append(sentence)

        for s in range(shot):
          message += 'Na sentença "%s",  as relações de dependência sintática são mostradas abaixo no formato (token dependente -> token cabeça),\n' % sentences[s]
          message += '\n'.join(pairs[s])
        
        
        return message+'.'

    def process_chatgpt_message(self,message,model_chat='gpt-3.5-turbo'):
        messages = []

        if message:
          messages.append({'role':'user','content':message},
                          )
          chat = self.gpt_client.chat.completions.create(
              model =model_chat,messages=messages
          )

        reply = chat.choices[0].message.content

        if 'Obs: ' in reply:
          reply = reply.split('Obs: ')[0]


        if 'Note que ' in reply:
          reply = reply.split('Note que ')[0]

        return reply

    def normalizeOutput(self,message,left=False):

        if len(message.split()) > 1:
          if left:
            return message.split()[-1]
          else:
            return message.split()[0]

        return message

    def __refine__(self,word,left,writerOUT):
      if len(word) <= 1:
        return word

      word = word.strip()

      writerOUT.write('REFINE [%s]\n' % word)
      if left:
        if word[0] == '-' and len(word.split()) > 2:
          word = word.split()[1].strip()

        writerOUT.write('REFINE [%s]\n' % word)
        if len(word.split()) > 1:
          if word.split()[0][0].isdigit():
            word = word.split()[1]
          else:
            word = word.split()[-1]

        writerOUT.write('REFINE [%s]\n' % word)

      if not left:
        writerOUT.write('REFINE [%s]\n' % word)
        if len(word.split()) > 1:
          word = word.split()[0]


      writerOUT.write('REFINE [%s]\n' % word)
      if len(word)> 1 and word[0] in ['(',')',']','[']:
        word = word[1:]

      writerOUT.write('REFINE [%s]\n' % word)
      if len(word)> 1 and word[-1] in ['(',')',']','[']:
        word = word[0:-1]

      writerOUT.write('REFINE [%s]\n' % word)
      writerOUT.write('-----------END REFINE---------\n')
      return word




    def getDepRelationsChat(self,message,writerOUT):
        if len(message) < 2:
          return []
        relations_text = message.replace('"','').split('\n')[1:]
        dep_relations = []


        for line in relations_text:
          if '"' in line:
            line = line.replace('"','')
          line = line.replace('"','').replace('-->','->').replace('<--','<-')
          left = ''
          right = ''
          if '->' in line:
            left,right = line.split('->')[0],line.split('->')[1]
            
          elif len(line.split()) == 2:
            left,right = line.split()[0],line.split()[1]

          dep, head = self.__refine__(left,True,writerOUT).strip(),self.__refine__(right,False,writerOUT).strip()
          dep_relations.append((dep,head))

        return dep_relations


    def compare(self,chatResponse,UDresponse):
      
      DDA = [0,len(UDresponse)]
      UDA = [0,len(UDresponse)]

      relations_pairs = []

      for r in UDresponse:

          relations_pairs.append('%s<#>%s' % (r['DEP'].lower(),r['HEAD'].lower()))

          if r['DEPREL'] not in self.syntatic_relations_testset:
            self.syntatic_relations_testset[r['DEPREL']] = 0

          if r['DEPREL'] not in self.matchs_UDA:
            self.matchs_UDA[r['DEPREL']] = 0

          if r['DEPREL'] not in self.matchs_DDA:
            self.matchs_DDA[r['DEPREL']] = 0


          self.syntatic_relations_testset[r['DEPREL']] += 1
      relations_pairs_buffer = relations_pairs.copy()


      for index_pair,chatRelation in enumerate(chatResponse):

          chatR_dh  = '%s<#>%s' % (chatRelation[0].lower(),chatRelation[1].lower())
          chatR_hd  = '%s<#>%s' % (chatRelation[1].lower(),chatRelation[0].lower())
          


          if chatR_dh in relations_pairs_buffer:
            index_relation = relations_pairs.index(chatR_dh)
            #print('DH',chatR_dh,'in',relations_pairs_buffer)
            self.matchs_UDA[UDresponse[index_relation]['DEPREL']] += 1
            self.matchs_DDA[UDresponse[index_relation]['DEPREL']] += 1
            DDA[0] += 1
            UDA[0] += 1
            relations_pairs_buffer.remove(chatR_dh) #To avoid compare to the same relation

          elif chatR_hd in relations_pairs_buffer:
            #print('HD',chatR_hd,'in',relations_pairs_buffer)
            index_relation = relations_pairs.index(chatR_hd)

            self.matchs_UDA[UDresponse[index_relation]['DEPREL']] += 1
            UDA[0] += 1
            relations_pairs_buffer.remove(chatR_hd) #To avoid compare to the same relation
      #print('COMPARADO=>',chatResponse)
      #print('COM=======>',[('%s<#>%s') % (r['DEP'].lower(),r['HEAD'].lower()) for r in UDresponse])
      #print('RESULTANDO>',UDA,DDA)
      return UDA, DDA

    def computeResults(self,writerR):

              
          writerR.write('UDA %.3f\n' % (sum(self.matchs_UDA.values())/sum(self.syntatic_relations_testset.values())))
          writerR.write('DDA %.3f\n' % (sum(self.matchs_DDA.values())/sum(self.syntatic_relations_testset.values())))

          for sy_rel, value in self.syntatic_relations_testset.items():
           writerR.write('%s;%.3f;%.3f;%d\n' % (sy_rel,self.matchs_UDA[sy_rel]/self.syntatic_relations_testset[sy_rel],
                                            self.matchs_DDA[sy_rel]/self.syntatic_relations_testset[sy_rel],self.syntatic_relations_testset[sy_rel]))



    def testGPT(self,args):

      PATH = '/'.join(os.getcwd().split('/')[0:-1])
      if 'results' not in os.listdir(PATH):
          os.mkdir('%s/results' % PATH)

      language = args.PATHtest.split('/')[-1]
      save_PATH = '%s/results/%s_results_%s_%s_%s.txt' % (PATH,language,args.shot,str(args.fixed),time.asctime())
      save_PATH_output = '%s/results/%s_output_%s_%s_%s.txt' % (PATH,language,args.shot,str(args.fixed),time.asctime())

      

      writerR = open(save_PATH,'w')
      writerOUT = open(save_PATH_output,'w')
      out_pattern = 0
      for index,sample in enumerate(self.test):
        
        depRel = sample[0]
        sentence = sample[1]
        
        if index % 10 == 0:
          print('%.3f %% concluded ' % ((index/100)*100))
          print('%.3f %% out of pattern' % ((out_pattern/100)*100))
          print(index)

        if index == args.requests:
          break

        message = ''

        if args.shot > 0:
          message = self.generateGuide(args.fixed,args.shot)

        message += """.\nListe as relações de dependência sintática na sentença "%s", usando o formato (token dependente -> token cabeça).""" % (sentence)

        try:
          writerOUT.write(sentence+'\n')
          writerOUT.write('MESSAGE|:|'+message+'\n')
          replyGPT = self.process_chatgpt_message(message)
          writerOUT.write('REPLY|:|'+replyGPT+'\n')
          llm = self.getDepRelationsChat(replyGPT,writerOUT)
          r = self.compare(llm,depRel)
          sentence_chat = '<#>'.join(['%s<@>%s' % (r[0],r[1]) for r in llm])
          sentence_dep  = '<#>'.join(['%s<@>%s<@>%s' % (d['DEP'],d['HEAD'],d['DEPREL']) for d in depRel])
          writerR.write('chatGPT|:|%s|:|UDA:%.3f<#>DDA: %.3f\n' % (sentence_chat,r[0][0]/r[0][1],r[1][0]/r[1][1]))
          writerR.write('DepRel |:|%s\n' % sentence_dep)
          writerR.write('>--<\n')

          writerOUT.write('chatGPT|:|%s|:|UDA:%.3f<#>DDA: %.3f\n' % (sentence_chat,r[0][0]/r[0][1],r[1][0]/r[1][1]))
          writerOUT.write('GoldTree |:|%s\n' % sentence_dep)
          writerOUT.write('>--<\n')
        except:
          writerOUT.write('---------------ERROR--------------\n')
          out_pattern += 1

         

        
      self.computeResults(writerR)
      return save_PATH
        
def formatTime(time_):

  miliseconds = str(time_).split('.')[1]
  totalseconds = int(str(time_).split('.')[0])
  hours = totalseconds // 3600
  minutes = (totalseconds % 3600) // 60
  seconds = (totalseconds % 3600) % 60

  print('%02d:%02d:%02d,%s' % (hours,minutes,seconds,miliseconds))

def summarize_results(file_results):
    relations = []

    for message in open(file_results).read().split('>--<')[0:-1]:

      if len(message.split('\n')) == 4:
        
        chat = message.split('\n')[1].split('|:|')[1]
        dep  = message.split('\n')[2].split('|:|')[1]
        
        relations.append((dep,chat))
    
   
    compare(relations.copy(),10)
    compare(relations.copy(),40)
    compare(relations.copy(),100)

if "__main__":
    parser = argparse.ArgumentParser(description='UDmodel')
    parser.add_argument('--PATHtest',type=str,default=0,help='CONLLU test file')
    parser.add_argument('--openkey',type=str,default='',help='openkey from openAI API')
    parser.add_argument('--PATHtrain',type=str,default='',help='used to generate one and two shot guide')
    parser.add_argument('--shot',type=int,default=0,help='0 - Zero shot, 1 = one Shot, 2 = Two Shot')
    parser.add_argument('--fixed',type=int,default=0,help="""0 - False, 1 = True. For shot 1, is used the first sentence 
                                          from the train file.\n For shot 2, are used the first two sentences in the train file.""")
    parser.add_argument('--requests',type=int,default=100,help='Total of requests')
    parser.add_argument('--max_len_sent_train',type=int,default=10,help="Max sentence train len")
    args = parser.parse_args()
    
    start = time.time()


    if args.shot != 0 and args.PATHtrain == '':
      print('For one or two shot you must define the PATHtrain')

    else:
      model = llm_UD(args)
      results = model.testGPT(args)
      summarize_results(results)
      # end = time.time()-start
      # formatTime(end)

