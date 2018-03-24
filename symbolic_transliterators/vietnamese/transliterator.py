from sys import argv
from iter_1 import iter_1
from iter_2 import iter_2
from iter_3 import iter_3
from iter_4 import iter_4
from postprocess import postprocess
from transliteration_framework import *
from pprint import pprint

script, lex_file_name, output_file_name = argv

# All transliterations
trans_dict = []

######################################################## INITIALIZE INPUT #########################################################################
def initialize_input(lex_file_name, vie_file_name):
  lex_file = open(lex_file_name, "r")
  vie_file = open(vie_file_name, "w")

  phon_input = []
  en_input = []

  # Read input
  for line in lex_file:
    [en_input, phon_input] = line.strip().split("\t\t")
    
    new_trans = Transliteration()
    new_trans.original_phon_seq = phon_input.split(" ")
    new_trans.original_en_seq = list(en_input)

    new_trans.flag = [0 for i in range(len(new_trans.original_phon_seq))]

    for phon in new_trans.original_phon_seq:
      new_trans.inter_phon_seq.append(phon)
    for en in new_trans.original_en_seq:
      new_trans.inter_en_seq.append(en)

    new_trans.syl_seq = [None for i in range(len(new_trans.original_phon_seq))]
    print new_trans.to_string()

    # Add the input to the transliteration dictionary
    trans_dict.append(new_trans)

######################################################## MAIN LOOP #########################################################################
initialize_input(lex_file_name, output_file_name)
new_iter = iter_1(trans_dict)
new_iter.run()
new_iter = iter_2(trans_dict)
new_iter.run()
new_iter = iter_3(trans_dict)
new_iter.run()
new_iter = iter_4(trans_dict)
new_iter.run()
postprocess = postprocess(trans_dict)
postprocess.run()

write_list_to_file(output_file_name, trans_dict)
