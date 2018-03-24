import os
import sys
import re
import subprocess

# Run scoring tests on output file
def run_stats(path_to_sclite, test_out, test_vie):
  # Run sclite
  ref_file = index_file(test_vie)
  hyp_file = index_file(test_out)

  sclite_exec = os.path.join(path_to_sclite, "sclite")    
  sclite_cmd = sclite_exec + \
  "  -r " + ref_file + \
  "  -h " + hyp_file + \
  "  -i wsj " + \
  "  -o dtl"

  print sclite_cmd
  run_shell_command(sclite_cmd)

  os.remove(ref_file)
  os.remove(hyp_file)

  return test_out + ".indexed.dtl"

# Helper function to run a shell command
def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()

# Scoop SER and TER stats from dtl
def scoop_dtl(fname):
  dtl_file = open(fname, "r")

  ser = ""
  ter = ""
  for line in dtl_file:
    if "with errors" in line:
      ser = re.findall(r'\d+.\d+\%', line)[0][:-1]
    elif "Percent Total Error" in line:
      ter = re.findall(r'\d+.\d+\%', line)[0][:-1]
  dtl_file.close()
  return [ter, ser]

# Index the lines of a file
def index_file(input):
  original_file = open(input, "r")

  indexed_name = input + ".indexed"
  indexed_file = open(indexed_name, "w")

  count = 1
  for line in original_file:
    indexed_file.write(line.strip() + "\t(" + str(count) + ")\n")
    count = count + 1

  original_file.close()
  indexed_file.close()

  return indexed_name

def run_sclite(path_to_sclite, output_file, vie_file):
  stats_file = run_stats(path_to_sclite, output_file, vie_file)
  return scoop_dtl(stats_file)