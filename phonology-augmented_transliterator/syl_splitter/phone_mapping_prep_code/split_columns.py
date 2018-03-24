import sys

if __name__ == '__main__':
  try:
    script, source_file_name, dest_files_name = sys.argv
  except ValueError:
    print "Split two columns of a lex file into two separate dest files with extension .syl_en and .syl_vie"
    print "Syntax: python split_columns.py source_file_name"
    sys.exit(1)

def split(source_file_name):
  syl_lex_file = open(source_file_name, "r")
  syl_en_file = open(dest_files_name + ".syl_seq", "w")
  syl_vie_file = open(dest_files_name + ".vie", "w")

  syls_en = []
  syls_vie = []
  for line in syl_lex_file:
    [en, vie] = line.strip().split("\t")
    syls_en.append(en.strip())
    syls_vie.append(vie.strip())

  for i in range(len(syls_en)):
    syl_en_file.write(syls_en[i] + "\n")
    syl_vie_file.write(syls_vie[i] + "\n")


  syl_en_file.close()
  syl_vie_file.close()
  syl_lex_file.close()

split(source_file_name)

