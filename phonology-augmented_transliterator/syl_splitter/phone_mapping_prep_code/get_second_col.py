import sys
import os

script, input_file = sys.argv

input_file = os.path.abspath(input_file)

def get_second_col(input):
  original_file = open(input, "r")

  output_name = ".".join(input.split(".")[0:-1]) + ".output"
  output_file = open(output_name, "w")
  print output_name

  for line in original_file:
    output_file.write(line.split("\t")[-1])

get_second_col(input_file)