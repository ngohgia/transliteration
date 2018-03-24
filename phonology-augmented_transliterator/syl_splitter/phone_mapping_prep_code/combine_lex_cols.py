import sys

def combine_lex_cols(source_files_name):
  syl_en_file = open(source_files_name + ".syl_en", "r")
  syl_vie_file = open(source_files_name + ".syl_vie", "r")
  syl_lex_file = open(source_files_name + ".lex", "w")

  syls_en = []
  syls_vie = []
  for line in syl_en_file:
    syls_en.append(line.strip())

  for line in syl_vie_file:
    syls_vie.append(line.strip())

  for i in range(len(syls_en)):
    syl_lex_file.write(syls_en[i] + "\t" + syls_vie[i] + "\n")


  syl_en_file.close()
  syl_vie_file.close()
  syl_lex_file.close()
