import os
import sys
import time
import subprocess
import logging


if __name__ == '__main__':
  try:
    script, training_lex_file_path, test_en_file_path, output_name, run_dir, t2p_decoder_path, log_file = sys.argv
  except ValueError:
    print "Syntax: transliterator.py    training_lex_file_path     test_en_file_path     run_dir    t2p_decoder_path   log_file_path"
    sys.exit(1)

# Log file
logging.basicConfig(filename= log_file, level= logging.DEBUG, format='%(message)s')

test_en_file_path = os.path.abspath(test_en_file_path)
training_lex_file_path = os.path.abspath(training_lex_file_path)
t2p_decoder_path = os.path.abspath(t2p_decoder_path)


# Helper function to log and print a message
def report(msg):
  print "%s\n" % msg
  logging.info(msg)

# Helper function to run a shell command
def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()

best_lex_hyp_file_name = os.path.abspath(run_dir + "/best_lex_hyp.txt")

#Train syllable splitting
command = "python syl_splitter/GetBestRules_improved.py " + \
   training_lex_file_path + " " \
   + run_dir + " " + \
   t2p_decoder_path
report(command)   
run_shell_command(command)
 
# Syllable splitting
command = "python syl_splitter/SplitWordWithSearchSpace.py" + \
    " " + best_lex_hyp_file_name + \
    " " + test_en_file_path + \
    " " + run_dir + \
    " " + t2p_decoder_path
report(command)
run_shell_command(command)

# Phone mapping
test_units_roles_file = os.path.abspath(run_dir + "/units_roles.txt")
command = "python phone_mapper/phone_mapper.py" + \
    " " + best_lex_hyp_file_name + \
    " " + test_units_roles_file + \
    " " + t2p_decoder_path
report(command)
run_shell_command(command)

# Tone setting
toneless_vie_phones_with_roles_file = os.path.abspath(run_dir + "/test.toneless_with_roles.output")
command = "python tone_setter/tone_setter.py" +  \
    " " + best_lex_hyp_file_name + \
    " " + toneless_vie_phones_with_roles_file + \
    " " + output_name
report(command)
run_shell_command(command)
