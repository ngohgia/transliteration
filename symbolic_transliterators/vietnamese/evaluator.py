from sys import argv

script, lex_file_name, output_file_name, vie_file_name = argv

lex_file = open(lex_file_name, "r")
vie_file = open(vie_file_name, "r")
output_file = open(output_file_name, "r")
eval_file = open("test.eval", "w")

lex_lines = []
vie_lines = []
output_lines = []

count = 0

for line in lex_file:
  lex_lines.append(line.strip())

for line in vie_file:
  vie_lines.append(line.strip())

for line in output_file:
  output_lines.append(line.strip())

for idx in range(len(vie_lines)):
  if vie_lines[idx] != output_lines[idx]:
  	eval_file.write(lex_lines[idx] + "\t|\t" + output_lines[idx] + "\t|\t" + vie_lines[idx] + "\n\n")
  	count = count + 1

print "Total number of errors: " + str(count)
vie_file.close()
output_file.close()