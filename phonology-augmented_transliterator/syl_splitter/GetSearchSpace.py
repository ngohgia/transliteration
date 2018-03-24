import sys
import random
import copy

from LangAssets.Rule import Rule
from LangAssets.SearchSpace import SearchSpace
from LangAssets.LangAssets import LangAssets
from syl_struct_generator.SylStructGenerator_improved import *

# For each lexicon's hypothesis file, produce ITER_NUMBER of search spaces
ITER_NUMBER = 1

N_GRAM_LEN = LangAssets.N_GRAM_LEN

VOWEL = LangAssets.VOWEL
CONSONANT = LangAssets.CONSONANT
GENERIC_VOWEL = LangAssets.GENERIC_VOWEL
DELIMITER = LangAssets.DELIMITER
ANY = LangAssets.ANY

ONSET = LangAssets.ONSET
NUCLEUS = LangAssets.NUCLEUS
CODA = LangAssets.CODA

ValidEnConsos = lang_assets.valid_en_consos
ValidEnVowels = lang_assets.valid_en_vowels

ValidEnOnsets = lang_assets.valid_en_onsets
ValidEnNuclei = lang_assets.valid_en_nuclei
ValidEnCodas = lang_assets.valid_en_codas

def read_lex_hyps_from_file(fname):
  fi = open(fname, "r")
  lex_hyps = {}
  for line in fi:
    [word, roles, reconstructed_word, reconstructed_roles, vie_word] = line.strip().split("\t")
    roles = roles.split(" ")
    reconstruected_roles = reconstructed_roles.split(" ")

    if word not in lex_hyps:
      lex_hyps[word] = [[roles, reconstructed_word, reconstructed_roles, vie_word]]
    else:
      lex_hyps[word].append([roles, reconstructed_word, reconstructed_roles, vie_word])

  fi.close()
  return lex_hyps

def get_search_space_from_lex_hyps(lex_hyps, run_dir):
  valid_units = {ONSET: [], NUCLEUS: [], CODA: []}

  # For each word in the lexicon, randomly pick out
  # a hypothesis
  search_space = SearchSpace()
  training_dev_split_file = open(run_dir + "/training_dev_split.split.lex", "w")
  trained_valid_units_file = open(run_dir + "/trained_valid_units.split.lex", "w")
  
  for word in lex_hyps:
    # print word
    rand_idx = random.randrange(len(lex_hyps[word]))
    roles = lex_hyps[word][rand_idx][0]
    reconstructed_word = lex_hyps[word][rand_idx][1]
    reconstructed_roles = []
    for syl in lex_hyps[word][rand_idx][2].split("."):
      for role in syl.strip().split(" "):
        reconstructed_roles.append(role.strip())
    vie_word = lex_hyps[word][rand_idx][3]
    #print reconstructed_roles

    # Reformat the reconstructed_word
    reconstructed_word = reconstructed_word[1:-1]
    reconstructed_word = [part.strip().split(" ") for part in reconstructed_word.split(" ] [ ")]
    reconstructed_syls = reconstructed_word
    reconstructed_word = " . ".join(["".join(syl) for syl in reconstructed_word])

    # Extract valid subsyllabic units
    idx = 0
    for syl in reconstructed_syls:
      for unit in syl:
        if unit != GENERIC_VOWEL and unit not in valid_units[reconstructed_roles[idx]]:
          valid_units[reconstructed_roles[idx]].append(unit)
        idx = idx + 1


    # Save the reconstructed words as training_dev for phone mapping
    training_dev_split_file.write(reconstructed_word + "\t" + vie_word + "\n")


    # Convert the word and the letters to a rule and add
    # the rule to the search space
    convert_word_labels_to_rule(word, roles, search_space)

  for role in valid_units:
    trained_valid_units_file.write(role + "\t" + (", ").join(valid_units[role]) + "\n")
  
  trained_valid_units_file.close()
  training_dev_split_file.close()
  search_space.normalized()
  return [search_space, valid_units]

# From the word and the roles assigned to the letters of the word,
# generate a rule
def convert_word_labels_to_rule(word, roles, search_space):
  labels = label_letters(word)

  for idx in range(len(word)):
    rule = Rule()
    rule.curr = [word[idx]]
    all_rules = []

    start = idx - N_GRAM_LEN/2
    end = idx + N_GRAM_LEN/2 + 1

    if start < 0:
      start = 0
    if end > len(word):
      end = len(word)

    for j in range(start, idx):
      rule.prev.append(word[j])
    for j in range(idx+1, end):
      rule.next.append(word[j])

    if len(rule.prev) < (N_GRAM_LEN/2):
      rule.prev = [DELIMITER] + rule.prev
    if len(rule.next) < (N_GRAM_LEN/2):
      rule.next.append(DELIMITER)

    rule.role = [roles[idx]]

    tmp_all_rules = []
    all_rules.append(rule)
    tmp_all_rules.append(rule)

    extrapolated_rules = extrapolate_rule_with_labels(rule)
    for new_rule in extrapolated_rules:
      if new_rule not in all_rules:
        all_rules.append(new_rule)
        tmp_all_rules.append(new_rule)

    for rule in tmp_all_rules:
      further_extrapolated_rules = further_extrapolate_rule(rule)
      for new_rule in further_extrapolated_rules:
        if new_rule not in all_rules:
          all_rules.append(new_rule)

    tmp_all_rules = copy.deepcopy(all_rules)
    for rule in tmp_all_rules:
      new_rule = further_further_extrapolate_rule(rule)
      if new_rule not in all_rules:
        all_rules.append(new_rule)

    for rule in all_rules:
      #print rule.to_str()
      search_space.add_rule(rule)

def extrapolate_rule_with_labels(rule):
  extrapolated_rules = []
  for prev_conv_range in range(0,len(rule.prev)+1):
    for next_conv_range in range(0,len(rule.next)+1):
      rule_tmp = copy.deepcopy(rule)
      if prev_conv_range > 0:
        for i in range(0, prev_conv_range):
          if rule_tmp.prev[i] != DELIMITER:
            rule_tmp.prev[i] = map_letter_to_label(rule_tmp.prev[i])
      if next_conv_range > 0:
        for j in reversed(range(len(rule_tmp.next)-next_conv_range, len(rule_tmp.next))):
            if rule_tmp.next[j] != DELIMITER:
              rule_tmp.next[j] = map_letter_to_label(rule_tmp.next[j])
      extrapolated_rules.append(rule_tmp)
  return extrapolated_rules


def further_extrapolate_rule(rule):
  extrapolated_rules = []
  
  for prev_conv_range in range(0, len(rule.prev)+1):
    for next_conv_range in range(0, len(rule.next)+1):
      rule_tmp = copy.deepcopy(rule)

      if prev_conv_range < len(rule.prev):
        rule_tmp.prev = rule_tmp.prev[prev_conv_range:len(rule_tmp.prev)]
      else:
        rule_tmp.prev = []

      if next_conv_range < len(rule.next):
        rule_tmp.next = rule_tmp.next[0:len(rule_tmp.next) - next_conv_range]
      else:
        rule_tmp.next = []
      extrapolated_rules.append(rule_tmp)
  return extrapolated_rules

def further_further_extrapolate_rule(rule):
  rule_tmp = copy.deepcopy(rule)
  rule_tmp.curr = [map_letter_to_label(rule.curr[0])]
  return rule_tmp


# Map a letter to its label
def map_letter_to_label(letter):
  if letter in ValidEnVowels:
    return VOWEL
  elif letter in ValidEnConsos:
    return CONSONANT
  else:
    print "Letter %s cannot be mapped to a label" % letter
    sys.exit(1)

# ---------  UNIT TEST FOR RULE EXTRAPOLATION ------- #
# rule = ["h", "o", "n", "O"]
# extrapolated_rules = []
# extrapolate_rule_with_labels(rule, 0, extrapolated_rules)
# print "Rule: " + str(rule)
# print "Extrapolated rules: "
# for rule in extrapolated_rules:
#   print str(rule)

# --------- UNIT TEST FOR FURTHER RULE EXTRAPOLATION ------- #
# tmp_rule = ["h", "o", "n", "O"]
# tmp_extrapolated_rules = []
# extrapolate_rule_with_labels(tmp_rule, 0, tmp_extrapolated_rules)

# extrapolated_rules = []
# for tmp_rule in tmp_extrapolated_rules:
#   rule = Rule()
#   rule.prev = tmp_rule[0]
#   rule.curr = tmp_rule[1]
#   rule.next = tmp_rule[2]
#   rule.role = tmp_rule[3]
#   extrapolated_rules.append(rule)

# # Replace labels with "ANY"
# further_extrapolated_rules = further_extrapolate_rule(extrapolated_rules);
# all_rules = extrapolated_rules + further_extrapolated_rules

# print "All rules:"
# for rule in all_rules:
#   print rule.to_str()

# ---------  UNIT TEST FOR SEARCH SPACE GENERATION ------- #
# lex_hyp = {}
# lex_hyp['bush'] = [['O', 'N', 'O', 'N']]
# search_space = get_search_space_from_lex_hyps(lex_hyp)
# print search_space.to_str()

#lex_hyps = read_lex_hyps_from_file("results/best_lex_hyp_2014-12-09_23-20-40")
#search_space = get_search_space_from_lex_hyps(lex_hyps)
#print search_space.to_str()

# --------- UNIT TEST FOR CONVERT WORD LABELS TO RULES ------ #
# search_space = []
# roles = ["O", "N_Cd", "O", "N_Cd", "O", "O", "N_Cd", "O", "N_Cd", "O", "N_Cd", "O", "N", "N_Cd"]
# word = "nabuchodonosor"
# word = "montreal"
# roles = ["O", "N", "Cd", "O", "O", "N_Cd", "N", "Cd"]
# word = "courcy"
# roles = ["O", "N", "N", "Cd", "O", "N_Cd"]
# convert_word_labels_to_rule(word, roles, search_space)
