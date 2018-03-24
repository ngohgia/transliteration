import sys

def retrieve_syls_mapping(syls_mapping_file_name):
  syls_mapping_file = open(syls_mapping_file_name, "r")
  mapping_dict = {}

  for line in syls_mapping_file:
    [en_syl, vie_syl] = line.strip().split("\t")
    mapping_dict[en_syl] = vie_syl

  syls_mapping_file.close()
  return mapping_dict

def reconstruct(syls_seq_file_name, syls_output_file_name, mapping_dict):
  syls_seq_file = open(syls_seq_file_name, "r")  
  syls_output_file = open(syls_output_file_name, "w")

  for line in syls_seq_file:
    en_syls = [syl.strip() for syl in line.strip().split(" . ")]

    for en_syl in en_syls:
      if en_syl not in mapping_dict:
        return False
      else:
        vie_syls = [mapping_dict[en_syl] for en_syl in en_syls]
    
    syls_output_file.write(" . ".join(vie_syls) + "\n")

  syls_seq_file.close()
  syls_output_file.close()
  return True

def reconstruct_vie_from_syls(syls_seq_file, syls_mapping_file, syls_output_file):
  mapping_dict = retrieve_syls_mapping(syls_mapping_file)
  return reconstruct(syls_seq_file, syls_output_file, mapping_dict)