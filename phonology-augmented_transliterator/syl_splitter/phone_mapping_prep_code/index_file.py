import sys

script, input_file = sys.argv

def index_file(input):
  original_file = open(input, "r")

  indexed_name = input + ".indexed"
  indexed_file = open(indexed_name, "w")

  count = 1
  for line in original_file:
    indexed_file.write(line.strip() + "\t(" + str(count) + ")\n")
    count = count + 1

  return indexed_name

index_file(input_file)