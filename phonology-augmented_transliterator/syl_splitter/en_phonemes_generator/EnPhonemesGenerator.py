import os
import sys
import subprocess

def create_input_for_t2p(all_words, t2p_input_path):
  t2p_input_file = open(t2p_input_path, "w")

  for word_hyp in all_words:
    t2p_input_file.write(word_hyp.original.upper() + "\n")

  t2p_input_file.close()

def get_phonemes_with_g2p(t2p_decoder_path, t2p_input_path, t2p_output_path):
  t2p_output_path_tmp = t2p_output_path + ".tmp"

  curr_dir = os.path.dirname(os.path.realpath(__file__))
  t2p_dir = os.path.dirname(os.path.realpath(t2p_decoder_path))

  # cd to the t2p folder
  os.chdir(t2p_dir)
  # run t2p
  command = "perl " + t2p_decoder_path + " < " + t2p_input_path + " > " + t2p_output_path_tmp
  run_shell_command(command)
  # cd back
  os.chdir(curr_dir)

  t2p_output_file_tmp = open(t2p_output_path_tmp, "r")
  t2p_output_file = open(t2p_output_path, "w")

  count = 0
  for line in t2p_output_file_tmp:
    if count > 2:
      t2p_output_file.write(line[2:len(line)])
    count = count + 1

  t2p_output_file_tmp.close()
  t2p_output_file.close()

def get_en_phonemes(t2p_output_path):
  count = 0;
  all_phonemes = []

  t2p_output_file = open(t2p_output_path, "r")

  for line in t2p_output_file:
    all_phonemes.append([phoneme.strip() for phoneme in line.split(" ")])

  t2p_output_file.close()
  return all_phonemes

def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()