from iter_1 import *
from pprint import pprint

# All transliterations
trans_dict = []

######################################################## FILE NAMES #########################################################################
# Phons
vowels_phon_file = "vowels.phon"
ini_consos_phon_file = "ini_consos.phon"
final_consos_phon_file = "final_consos.phon"

# Valid Vietnamese consonants
valid_consos_vie_file = "valid_consos.vie"
# Valid Vietnamese ending vowels
valid_ending_vowels_vie_file = "valid_ending_vowels.vie"
# Valid Vietnamese initial consonant clusters
ini_conso_clusters_vie_file = "ini_conso_clusters.vie"

# Valid stops in Vietnamese
t_stops_vie_file = "t_stops.vie"
p_stops_vie_file = "p_stops.vie"
k_stops_vie_file = "k_stops.vie"

# Valid English graphemes
vowels_en_file = "vowels.en"
consos_en_file = "consos.en"

# Mapping files
vowel_mapping_file = "vowel.map"
conso_mapping_file = "conso.map"

######################################################## SYLLABLE OBJECT #########################################################################
class Syllable:
  def __init__(self):
    self.pos = 0

    self.en_ini_conso = []
    self.en_vowel = []
    self.en_final_conso = []

    self.phon_ini_conso = []
    self.phon_vowel = []
    self.phon_final_conso = []

    self.vie_ini_conso = []
    self.vie_vowel = []
    self.vie_tone = 1
    self.vie_final_conso = []

  def to_string(self):
    return "Pos:" + str(self.pos) + "\n" + \
    "English: " + " ".join(self.en_ini_conso) + " | " + " ".join(self.en_vowel) + " | " + " ".join(self.en_final_conso) + "\n" + \
    "Phons: " + " ".join(self.phon_ini_conso) + " | " + " ".join(self.phon_vowel) + " | " + " ".join(self.phon_final_conso) + "\n" + \
    "Vietnamese: " + " ".join(self.vie_ini_conso) + " | " + " ".join(self.vie_vowel) + " | " + " ".join(self.vie_final_conso) + " _" + str(self.vie_tone) + "\n"
  
  def get_pretty(self):
    pretty = " ".join(self.vie_vowel)
    if len(self.vie_ini_conso) > 0:
      pretty = " ".join(self.vie_ini_conso) + " " + pretty
    if len(self.vie_final_conso) > 0:
      pretty = pretty + " " + " ".join(self.vie_final_conso)
    pretty = pretty + " _" + str(self.vie_tone)

    return  pretty

######################################################## TRANSLITERATION OBJECT #########################################################################
class Transliteration:
  original_phon_seq = []
  original_en_seq = []
  flag = []

  # Intermediate sequences for processing in each iteration
  inter_phon_seq = []
  inter_en_seq = []

  syl_seq =  []

  def __init__(self):
    self.original_phon_seq = []
    self.original_en_seq = []
    self.flag = []
    self.inter_phon_seq = []
    self.inter_en_seq = []
    self.syl_seq =  []

  def to_string(self):
    return "-------------- TRANSLITERATION -------------------\n" + \
    "Original English: " + " ".join(self.original_en_seq) + "\n" + \
    "Original Phons: " + " ".join(self.original_phon_seq) + "\n" + \
    "Intermediate English: " + " ".join(self.inter_en_seq) + "\n" + \
    "Intermediate Phons: " + " ".join(self.inter_phon_seq) + "\n" + \
    "Flag: " + " ".join([str(val) for val in self.flag]) + "\n" + \
    "Syllables Seq: \n" + "\t\n".join([syl.to_string() for syl in self.syl_seq if syl != None and syl != "IGNORE"]) + \
    "\n ---> Result: " + self.get_pretty()

  def get_pretty(self):
    tmp = " . ".join([syl.get_pretty() for syl in self.syl_seq if syl != None and syl != "IGNORE"])
    tmp = " ".join(tmp.split())

    return tmp

######################################################## RULE OBJECT #########################################################################
class Rule:
  def __init__(self):
    # Collection of all allowed phons
    self.vowel_set = []
    self.ini_conso_set = []
    self.final_conso_set = []

    # Collection of consonants allowed in Vietnamese
    self.valid_vie_consos_set = []
    # Collection of ending vowels in Vietnamese
    self.valid_ending_vie_vowels_set = []
    # Collections of Vietnamese consonant clusters
    self.vie_ini_conso_clusters_set = []

    # Different stops in Vietnamese
    self.t_stops_set = []
    self.p_stops_set = []
    self.k_stops_set = []

    # Collection of English vowels and consonants graphemes
    self.en_vowels_set = []
    self.en_consos_set = []

    # Default mapping
    self.default_conso_mapping = {}
    self.default_vowel_mapping = {}

  def read_rule_from_files(self, dir_path):
    # Initialize phons collections
    read_list_from_file(dir_path + vowels_phon_file, self.vowel_set)
    read_list_from_file(dir_path + ini_consos_phon_file, self.ini_conso_set)
    read_list_from_file(dir_path + final_consos_phon_file, self.final_conso_set)

    # Initialize the collection of valid consonants in Vietnamese
    read_list_from_file(dir_path + valid_consos_vie_file, self.valid_vie_consos_set)
    read_list_from_file(dir_path + valid_ending_vowels_vie_file, self.valid_ending_vie_vowels_set)
    # Initlaize the collection of consonant clusters in Vietnamese
    read_clusters_from_file(dir_path + ini_conso_clusters_vie_file, self.vie_ini_conso_clusters_set)

    # Initialize the collections of English vowels and consonants
    read_list_from_file(dir_path + consos_en_file, self.en_consos_set)
    read_list_from_file(dir_path + vowels_en_file, self.en_vowels_set)

    # Initlaize the collection of stops in Vietnamese
    read_list_from_file(dir_path + t_stops_vie_file, self.t_stops_set)
    read_list_from_file(dir_path + p_stops_vie_file, self.p_stops_set)
    read_list_from_file(dir_path + k_stops_vie_file, self.k_stops_set)

  def read_map_from_files(self, dir_path):
    # Initialize the default consonant mapping
    read_map_from_file(dir_path + conso_mapping_file, self.default_conso_mapping)
    # Initialize the default vowel mapping
    read_map_from_file(dir_path + vowel_mapping_file, self.default_vowel_mapping)

  def to_string(self):
    return "----------------- RULE ---------------------\n" + \
    "Vowels: " + " ".join(self.vowel_set) + "\n" + \
    "Initial Consonants: " + " ".join(self.ini_conso_set) + "\n" + \
    "Final Consonants: " + " ".join(self.final_conso_set) + "\n\n" + \
    "Valid Viet consonants: " + " ".join(self.valid_vie_consos_set) + "\n" + \
    "Valid ending Viet vowels: " + " ".join(self.valid_ending_vie_vowels_set) + "\n\n" + \
    "Viet initial cosonants clusters: " + " ".join([" ".join(cluster) for cluster in self.vie_ini_conso_clusters_set]) + "\n\n" + \
    "T-stops: " + " ".join(self.t_stops_set) + "\n" + \
    "P-stops: " + " ".join(self.p_stops_set) + "\n" + \
    "K-stops: " + " ".join(self.k_stops_set) + "\n"


######################################################## SUPPORT FUNCTIONS #########################################################################
def read_list_from_file(fname, list):
  tmp = open(fname, "r")
  for line in tmp:
  	list.append(line.strip())
  tmp.close()

#TODO Standardize all the list reading functions
def read_clusters_from_file(fname, list):
  tmp = open(fname, "r")
  for line in tmp:
    list.append(line.strip().split(" "))
  tmp.close()

def write_list_to_file(fname, trans_list):
  tmp = open(fname, "w")
  for trans in trans_list:
    tmp.write(trans.get_pretty() + "\n")
  tmp.close()

def read_map_from_file(fname, phon_map):
  tmp = open(fname, "r")
  key = ""
  val = ""
  for line in tmp:
    [key, val] = line.strip().split(" ")
    phon_map[key] = val
  tmp.close()

def pick_items_backwards_from_seq(seq, idx, n):
  if idx > n-1:
    return seq[idx-n+1:idx+1]
  else:
    return seq[:idx+1]

def pick_items_forwards_from_seq(seq, idx, n):
  if idx + n <= len(seq):
    return seq[idx:idx+n]
  else:
    return seq[idx:]
