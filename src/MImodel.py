#@author: Diego Pedro, 13 January 2024
#@e-mail  diego.silva@ifam.edu.br
from collections import defaultdict
from collections import Counter
from udmodel import *
from edit import *
import numpy as np
import os
import time
import random

class MImodel:

  def __init__(self,case_sensitive=False):
    self.ud_model = UDModel()
    self.mult_dists_x = {}
    self.mult_dists_yx = {}
    self.output = {}
    self.smoothing = 'null'
    self.deprel = ['nsubj','obj','iobj','csubj','ccomp','xcomp','obl','vocative','expl','dislocated','advcl','advmod','discourse','aux','cop','mark','nmod','appos','nummod','acl','amod','det','clf','case','conj','cc','fixed','flat','compound','list','parataxis','orphan','goeswith','reparandum','punct','root','dep']
    self.__content__ = 'FORM'
    self.__initVariables()
    self.case_sensitive = case_sensitive

  def __initVariables(self):
      self.output = {'DDA':dict([(dp,[0,0]) for dp in self.deprel]),
                     'UDA':dict([(dp,[0,0]) for dp in self.deprel])}

  def editSearch(self,a):

    minor_string = ''
    minor_value = 100
    equals_strings = 1
    prob = 0
    tokens = list(self.mult_dists_x.copy().keys())
    average_distance = [[] for i in range(100)]

    for token in tokens:
      v = edit_distance(a,token)
      average_distance[v].append(self.mult_dists_x.copy()[token])

      if v < minor_value:
        minor_value = v
        minor_string = token 
        equals_strings = 1
        prob = self.mult_dists_x.copy()[token]

    return np.average(average_distance[minor_value])


  def __smoothing(self,token_frequency,total_tokens_frequency,token=None):

    if token_frequency != 0:
        return token_frequency

    if self.smoothing == 'null':
      return token_frequency

    if self.smoothing == 'laplace':
      return 1/total_tokens_frequency

    if self.smoothing == 'edit':

      if token == None:
        return 1/total_tokens_frequency

      prob = self.editSearch(token)

      if prob == 0:
        return 1/total_tokens_frequency

      return prob


  def computeMI(self,language,x,y):
    """For reference: https://people.cs.umass.edu/~elm/Teaching/Docs/mutInf.pdf
       Example: white house
       y = freq(white)
       x = freq(house)
       yx = white<#>house
    """

    IM = 0
    totalfreq = float(np.sum(list(self.mult_dists_yx.copy().values())))
    distx = self.__smoothing(self.mult_dists_x.copy()[x],totalfreq,x)
    disty = self.__smoothing(self.mult_dists_x.copy()[y],totalfreq,y)
    distyx = self.__smoothing(self.mult_dists_yx.copy()['%s<#>%s' % (y,x)],totalfreq)

    if distyx == 0:
        return 0
    join = distyx/totalfreq

    return join*(np.log2(distyx)+np.log2(totalfreq)-np.log2(distx)-np.log2(disty))

  def computeDist(self,CONLLU_file_name,max_train_len):

      dist_x = defaultdict(int)
      dist_yx = defaultdict(int)
      previous_token = ''
      #print('DIST',CONLLU_file_name)
      sentences = [self.ud_model.get_sentence_form(s['sentence']) for s in self.ud_model.parseConllu(CONLLU_file_name)]

      for sentence in sentences:
        tokens = sentence.split() if self.case_sensitive else sentence.lower().split()

        if len(tokens) > max_train_len:
          continue

        for token in tokens: 
          dist_x[token] += 1


          if previous_token != '':
            dist_yx['%s<#>%s' % (previous_token,token)] += 1

          previous_token = token

      return dist_x, dist_yx

  def combination(self,language, sentence,distance_limit):
    """ Root == 0"""
    
    list_combinations = []
    for index_c1, const1 in enumerate(sentence):

      for index_c2 in range(index_c1,len(sentence)):
        if index_c1 == index_c2:
          continue
        
        if index_c2 - index_c1 <= distance_limit:

          const1_form = const1[self.__content__].replace('--','-')
          const2_form = sentence[index_c2][self.__content__].replace('--','-')

          if not self.case_sensitive:
            const1_form = const1_form.lower()
            const2_form = const2_form.lower()

          list_combinations.append((self.computeMI(language,const1[self.__content__],\
                              sentence[index_c2][self.__content__]),const1_form,const2_form,index_c1+1,index_c2+1))
          
    list_combinations.sort()

    return list_combinations[::-1]

 

  def __processPairs(self,relations_target,permutation_pairs,language,max_distance_relations,log=False):

    if len(relations_target) == 0:
        return
    relations_target_pairs = {}


    for r in relations_target:
      relations_target_pairs[r['PAIR']] = r['DEPREL']

      self.output['UDA'][r['DEPREL']][1] += 1
      self.output['DDA'][r['DEPREL']][1] += 1

    for index_pair,perm_pair in enumerate(permutation_pairs):
        A = len(perm_pair[1])
        B = len(perm_pair[2])

        
        perm_pair_dh  = '%d<#>%d' % (perm_pair[-2],perm_pair[-1])
        perm_pair_hd  = '%d<#>%d' % (perm_pair[-1],perm_pair[-2])

        if perm_pair_dh in relations_target_pairs.keys():

          self.output['UDA'][relations_target_pairs[perm_pair_dh]][0] += 1
          self.output['DDA'][relations_target_pairs[perm_pair_dh]][0] += 1

        elif perm_pair_hd in relations_target_pairs.keys():
          self.output['UDA'][relations_target_pairs[perm_pair_hd]][0] += 1

  def train(self,data_train,smoothing='null',max_train_len=10):
    self.smoothing = smoothing
    

    dists = self.computeDist(data_train,max_train_len)
    self.mult_dists_x = dists[0]
    self.mult_dists_yx = dists[1]

  def summary_results(self):


    UDA_output = [values[0] for key, values in self.output['UDA'].items()]
    UDA_target = [values[1] for key, values in self.output['UDA'].items()]
    DDA_output = [values[0] for key, values in self.output['DDA'].items()]
    DDA_target = [values[1] for key, values in self.output['DDA'].items()]
    tdp = sum([i[1] for k,i in self.output['UDA'].items()])/10
    
    UDA_syn_output, DDA_syn_output = [],[]

    for dep_rel in self.deprel:

      if self.output['DDA'][dep_rel][1] > tdp and self.output['DDA'][dep_rel][0] > 0:
        DDA_syn_output.append((self.output['DDA'][dep_rel][0]/self.output['DDA'][dep_rel][1],dep_rel))

      if self.output['UDA'][dep_rel][1] > tdp and self.output['UDA'][dep_rel][0] > 0:
        UDA_syn_output.append((self.output['UDA'][dep_rel][0]/self.output['UDA'][dep_rel][1],dep_rel))

    UDA_syn_output.sort()
    DDA_syn_output.sort()

    UDA = sum(UDA_output)/sum(UDA_target)
    DDA = sum(DDA_output)/sum(DDA_target)
    return UDA,DDA,UDA_syn_output[::-1],DDA_syn_output[::-1]


  def testExp(self,data_test,language,max_distance_relations,max_length_sentence):
    

    parsed = self.ud_model.parseConllu(data_test) 
    parsed = {'depRel':[lp['depRel'] for lp in parsed],'sentence':[lp['sentence'] for lp in parsed]} 


    total_sentences = len(parsed['sentence'])
    permutation_count = 0
    previous_precision = 0
    sentences_processed = 0

    for index_sentence, sentence in enumerate(parsed['sentence']):
      
      if len(sentence) > max_length_sentence:
        continue


      startp = time.time()

      p = self.combination(language,sentence,max_distance_relations)


      if len(p) > 0:

        relations = parsed['depRel'][index_sentence]

        relations_pair_function = [r['DEPREL'] for r in relations]

        self.__processPairs(relations,p[0:len(relations)],language,max_distance_relations)

    return self.summary_results()


           