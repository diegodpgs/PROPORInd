from __future__ import print_function

import os
import argparse
import math
import time
import pickle

from collections import namedtuple
from modules import read_conll, get_tag_set
import modules.dmv_viterbi_model as dmv

def init_config(max_len=10):

    parser = argparse.ArgumentParser(description='train dmv with viterbi EM')

    # hyperparams
    parser.add_argument('--stop_adj', default=0.3, type=float,
        help='initial value for stop adjacent')
    parser.add_argument('--smth_const', default=1, type=int,
        help='laplace smooth parameter')

    # data input
    parser.add_argument('--train_file', type=str, help='train data path')
    parser.add_argument('--test_file', type=str, help='test data path')

    # others
    parser.add_argument('--train_from', type=str, default='',
        help='load a pre-trained checkpoint')
    parser.add_argument('--choice', choices=['random', 'minival', 'bias_middle',
        'soft_bias_middle', 'exclude_end', 'bias_left'], default='exclude_end',
        help='tie breaking policy at initial stage')
    parser.add_argument('--valid_nepoch', default=1, type=int,
        help='test every n iterations')
    parser.add_argument('--epochs', default=10, type=int,
        help='number of epochs')

    args = parser.parse_args()

    save_dir = "dump_models/dmv"

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, args.train_file.split('/')[-1].split('.')[0]+"_"+str(max_len)+"_viterbi_dmv.pickle")
    args.save_path = save_path

    print('Save',save_path)

    return args

def main(args,max_len_test=10,max_len_train=10):

    writerResults = open('Results_%d_E%d_%s_.txt' % (max_len_test,args.epochs,args.train_file.split('/')[-1]),'w')
    train_sents, codigo_sentence_train, _ = read_conll(args.train_file,max_len=max_len_train)
    test_sents, codigo_sentence_test, _ = read_conll(args.test_file, max_len=max_len_test)

    train_tags = [sent["tag"] for sent in train_sents]
    test_tags = [sent["tag"] for sent in test_sents]
    test_deps = [sent["head"] for sent in test_sents]

    tag_set = get_tag_set(train_tags)
    print('%d tags' % len(tag_set))
    writerResults.write('%d tags\n' % len(tag_set))
    print('------MARCADOR')
    model = dmv.DMV(args)
    model.init_params(train_tags, tag_set)
    #print('CONCLUIU init_params')
    model.set_harmonic(False)
    
    

    if args.train_from != '':
        model = pickle.load(open(args.train_from, 'rb'))
        directed, undirected,pdep = model.eval(test_deps, test_tags)
        writerResults.write('acc on length <= %d: #trees %d, undir %2.3f, dir %2.3f\n' % (max_len_test,len(test_deps), 100 * undirected, 100 * directed))

    epoch = 0
    stop = False

    directed, undirected,pdep = model.eval(test_deps, test_tags)
    writerResults.write('starting acc on length <= %d: #trees %d, undir %2.3f, dir %2.3f\n' % (max_len_test,len(test_deps), 100 * undirected, 100 * directed))

    num_train = len(train_tags)
    begin_time = time.time()
    print('--MARCADOR while')
    ultimo_DMV = []
    while epoch < args.epochs and (not stop):
        ultimo_DMV = []
        tita, count = dmv.DMVDict(), dmv.DMVDict()
        
        dmv.lplace_smooth(tita, count, tag_set, model.end_symbol, args.smth_const)
        log_likelihood = 0.0

        #s --> tag set for each sentence
        for i, s in enumerate(filter(lambda s: len(s) > 1,
                                    train_tags)):
            if i % 1000 == 0:
                print('epoch %d, sentence %d' % (epoch, i))
            
            parse_tree, prob = model.dep_parse(s)
            

            log_likelihood += prob
            model.MStep_s(parse_tree, tita, count)

        model.MStep(tita, count)
        print('\n\navg_log_likelihood:%.5f time elapsed: %.2f sec\n\n' % \
               (log_likelihood / num_train, time.time() - begin_time))

        if epoch % args.valid_nepoch == 0:
            directed, undirected,pdep = model.eval(test_deps, test_tags)
            ultimo_DMV = pdep
            writerResults.write('acc on length <= %d: #trees %d, undir %2.3f, dir %2.3f\n'% (max_len_test,len(test_deps), 100 * undirected, 100 * directed))

        epoch += 1

    pickle.dump(model, open(args.save_path, 'wb'))

    for index,s in enumerate(ultimo_DMV):
        writerResults.write('%s|%s\n' % ('<#>'.join([str(i) for i in s]),codigo_sentence_test[index]))


if __name__ == '__main__':
    parse_args = init_config(40)
    main(parse_args,40,40)
