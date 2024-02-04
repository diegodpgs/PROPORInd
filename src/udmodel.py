#@author: Diego Pedro, 13 January 2024
#@e-mail  diego.silva@ifam.edu.br
import collections as cl
import numpy as np 

class UDModel:


  def parseLine(self,const):
      """We used the same terms described in https://universaldependencies.org/format.html at 26 September 2023"""

      field = const.split('\t')
      distance = abs(int(field[0])-int(field[6]))


      return {'distance_dep_relation':distance,
              'ID':field[0],
              'FORM':field[1],
              'lema_pos':'%s_%s' % (field[2],field[3]),
              'LEMMA':field[2],
              'UPOS':field[3],
              'XPOS':field[4],
              'FEATS':field[5],
              'HEAD':field[6],
              'DEPREL':field[7],
              'PAIR':'%s<#>%s' % (field[0],field[6])}

  def end_sentence__(self,line):
      return True if len(line) <= 1 else False

  def is_validconst__(self,line):
      try:
        idtoken = line.split()[0]

        return True if idtoken[0].isdigit() and ('.' not in idtoken and '-' not in idtoken) else False

      except:
        print(f'[{line}]')
        print(len(line),type(line),ord(line[0]))
        raise Exception()

  def getSentenceDepRelations(self,sentence,content='FORM',root=False):
      deprel = []
      ids = dict([(const['ID'],const['FORM']) for const in sentence])
      idspos = dict([(const['ID'],const['UPOS']) for const in sentence])


      for line in sentence:
        if ':' in line['DEPREL']:
          line['DEPREL'] = line['DEPREL'].split(':')[0]

        if line['HEAD'] == '0':
          if not root:
            continue
          deprel.append({'HEAD':'root',
                        'DEP':line[content],
                        'DEPREL':line['DEPREL'],
                        'UPOSD':line['UPOS'],
                        'UPOSH':line['UPOS'],
                        'distance_dep_relation':line['distance_dep_relation'],
                        'PAIR':line['PAIR']})
        else:
          deprel.append({'HEAD':ids[line['HEAD']],
                        'DEP':line[content],
                        'UPOSD':line['UPOS'],
                        'UPOSH':idspos[line['HEAD']],
                        'DEPREL':line['DEPREL'],
                        'distance_dep_relation':line['distance_dep_relation'],
                        'PAIR':line['PAIR']})


      return deprel


  def get_sentence_form(self,sentence):

      return ' '.join([const['FORM'] for const in sentence])


  def parseConllu(self,file_name_CONLLU):
      conllu_parsed = []
      es = 0

      sentence = []
      sent_id = ''
      
      for line in open(file_name_CONLLU).read().lower().split('\n'):

          if '# sent_id = ' in line:
            sent_id = line.split('# sent_id = ')[1]

          if self.end_sentence__(line):
            conllu_parsed.append({'depRel':self.getSentenceDepRelations(sentence),'sent_id':sent_id,'sentence':sentence})
            sentence = []
            es += 1

          elif self.is_validconst__(line):
            sentence.append(self.parseLine(line))

      

      print('%s\n%d Sentences\n%d dependency relations' % (file_name_CONLLU,len(conllu_parsed[1:-1]),sum([len(i['depRel']) for i in conllu_parsed[1:-1]])))
      return conllu_parsed[0:-1]

  def statistical(self,writer_statistical,file_name_CONLLU):
    
      conllu_parsed = self.parseConllu(file_name_CONLLU)

      data = {'distance_dep_relation':[], 'UPOS_dep':[],'token':[],'sentence_len':[],'DEPREL':[]}

      for sentence in conllu_parsed:
        depSen = sentence['depRel']
        data['sentence_len'].append(len(sentence['sentence']))

        for const in depSen:
          data['distance_dep_relation'].append(const['distance_dep_relation'])
          data['UPOS_dep'].append(const['UPOSD'])
          data['token'].append(const['DEP'])
          data['DEPREL'].append(const['DEPREL'])



      
      writer_statistical.write('Distance|Average:%.3f|Min:%d|Max:%d\n' % (np.average(data['distance_dep_relation']),
                                                     min(data['distance_dep_relation']),
                                                     max(data['distance_dep_relation'])))
      writer_statistical.write('Tokens length|Total:%d|Average:%.3f|Min:%d|Max:%d\n' % (len([td for td in data['token']]),
                                                    np.average([len(td) for td in data['token']]),
                                                     min([len(td) for td in data['token']]),
                                                     max([len(td) for td in data['token']])))

      writer_statistical.write('Types:%d\n' % (len(set(data['token']))))
      writer_statistical.write('Complexity:%.3f\n' % (len(data['token'])/len(set(data['token'])))) 
      writer_statistical.write('Sentence length|Total:%d|Average:%.3f|Min:%d|Max:%d|STD:%.3f\n' % (len(data['sentence_len']),
                                                     np.average(data['sentence_len']),
                                                     min(data['sentence_len']),
                                                     max(data['sentence_len']),
                                                     np.std(data['sentence_len'])))

      writer_statistical.write('Sentence length|10:%.3f|40:%.3f\n' % ([s<= 10 for s in data['sentence_len']].count(True)/len(data['sentence_len']),
                                                     [s<= 40 for s in data['sentence_len']].count(True)/len(data['sentence_len'])))

      writer_statistical.write('Token Frequency\n')
      for token in cl.Counter(data['token']).most_common():
        writer_statistical.write(str(token)+'\n')

      writer_statistical.write('Pos Frequency\n')
      for token in cl.Counter(data['UPOS_dep']).most_common():
        writer_statistical.write(str(token)+'\n')

      writer_statistical.write('DPREL Frequency\n')
      for token in cl.Counter(data['DEPREL']).most_common():
        writer_statistical.write(str(token)+'\n')







