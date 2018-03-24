import os
import math
import sys
import shutil
import csv
import time
import logging

from LangAssets.LangAssets import LangAssets
from LangAssets.WordHyp import WordHyp
from LangAssets.SearchSpace import SearchCoord
from LangAssets.Rule import Rule
from GetSearchSpace import get_search_space_from_lex_hyps
from GetSearchSpace import read_lex_hyps_from_file

from syl_struct_generator.SylStructGenerator_improved import label_letters
from syl_struct_generator.SylStructGenerator_improved import set_thres_per_role
from syl_struct_generator.SylStructGenerator_improved import construct_syls
from syl_struct_generator.SylStructGenerator_improved import are_all_subsyl_units_valid
from syl_struct_generator.SylStructGenerator_improved import are_all_letters_used
from syl_struct_generator.SylStructGenerator_improved import checkValidSubsylUnit

from phone_mapping_prep_code.create_reformatted_data import create_reformatted_data
from phone_mapping_prep_code.create_syls_from_split_test_file import create_syls_from_split_test_file
from phone_mapping_prep_code.combine_lex_cols import combine_lex_cols
from phone_mapping_prep_code.run_g2p import *
from phone_mapping_prep_code.reconstruct_vie_from_syls import reconstruct_vie_from_syls
from phone_mapping_prep_code.run_sclite import run_sclite

from en_phonemes_generator.EnPhonemesGenerator import get_phonemes_with_g2p

if __name__ == '__main__':
  try:
    script, best_lex_hyp_file_name, targ_file_name, run_dir, t2p_decoder_path = sys.argv
  except ValueError:
    print "Syntax: SplitWordWithSearchSpace.py    best_lex_hyp_file_name       targ_file_name      run_dir     t2p_decoder_path"
    sys.exit(1)

t2p_decoder_path = os.path.abspath(t2p_decoder_path)

N_GRAM_LEN = LangAssets.N_GRAM_LEN

ANY = LangAssets.ANY
DELIMITER = LangAssets.DELIMITER

# Threshold to skip a coordinate match
MIN_COORD_EPSILON = 1e-12

# All possible roles of an alphabet
ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
ONSET_NUCLEUS = "O_N"
ONSET_CODA = "O_Cd"
NUCLEUS_ONSET = "N_O"
NUCLEUS_NUCLEUS = "N_N"
NUCLEUS_CODA = "N_Cd"
CODA_ONSET = "Cd_O"
CODA_NUCLEUS = "Cd_N"
CODA_CODA = "Cd_Cd"
ONSET_NUCLEUS_CODA = "O_N_Cd"
CODA_ONSET_NUCLEUS = "Cd_O_N"
REMOVE = "R"


lang_assets = LangAssets()
VOWEL = LangAssets.VOWEL
CONSONANT = LangAssets.CONSONANT
DELIMITER = LangAssets.DELIMITER

GENERIC_VOWEL = LangAssets.GENERIC_VOWEL

PossibleRoles = LangAssets.POSSIBLE_ROLES
ValidEnConsos = lang_assets.valid_en_consos
ValidEnVowels = lang_assets.valid_en_vowels

ValidVieConsos = lang_assets.valid_vie_consos
ValidVieVowels = lang_assets.valid_vie_vowels

# Strict role constraints
ValidConsoRoles = [ONSET, NUCLEUS, CODA, NUCLEUS_CODA, ONSET_NUCLEUS, CODA_ONSET_NUCLEUS, CODA_ONSET, REMOVE]
ValidVowelRoles = [NUCLEUS, NUCLEUS_CODA, ONSET_NUCLEUS_CODA, REMOVE]

ValidSubSylUnit = {
  ONSET: lang_assets.valid_en_onsets,
  NUCLEUS: lang_assets.valid_en_nuclei,
  CODA: lang_assets.valid_en_codas
}

# Each role can only be assigned to more than a specific ratio of all the letters
# TO-DO estimate the maximum ratio of each role from the Vietnamese entries in training data
MAX_ROLES_RATIOS = {
  ONSET: 0.3,
  NUCLEUS: 0.4,
  CODA: 0.3,
  ONSET_NUCLEUS: 0.0,
  CODA_ONSET_NUCLEUS: 0.2,
  NUCLEUS_ONSET: 0.0,
  NUCLEUS_NUCLEUS: 0.0,
  NUCLEUS_CODA: 0.4,
  CODA_ONSET: 0.0,
  CODA_NUCLEUS: 0.0,
  CODA_CODA: 0.0,
  ONSET_NUCLEUS_CODA: 0.0,
  REMOVE: 0.1,
}

run_dir = os.path.abspath(run_dir)

#---------------- GET BEST SEARCH SPACE ------------------#
# Retrieve the best search space from the training + dev
def get_best_search_space():
  lex_hyps = read_lex_hyps_from_file(best_lex_hyp_file_name)
  [search_space, valid_units] = get_search_space_from_lex_hyps(lex_hyps, run_dir)
  #print search_space.to_str()
  return [search_space, valid_units]

#---------------- GENERATE ALL POSSIBLE ROLES FOR ALPHABETS IN A WORD ------------------#
# Use a dictionary to keep count on the number times a role is assigned to a letter
role_count = {}
for role in PossibleRoles:
  role_count[role] = 0

def create_search_coord(word, roles, idx):
  coord = Rule()
  coord.curr = [word[idx]]

  # Create search coordinate based on the length of the n-grams
  start = idx - N_GRAM_LEN/2
  end = idx + N_GRAM_LEN/2 + 1

  if start < 0:
    start = 0
  if end > len(word):
    end = len(word)

  for j in range(start, idx):
    coord.prev.append(word[j])
  for j in range(idx+1, end):
    coord.next.append(word[j])

  if len(coord.prev) < (N_GRAM_LEN/2):
    coord.prev = [DELIMITER] + coord.prev
  if len(coord.next) < (N_GRAM_LEN/2):
    coord.next.append(DELIMITER)
  coord.role = [roles[idx]]

  new_search_coord = SearchCoord()
  new_search_coord.coord = coord

  return new_search_coord


# Generate roles for letter in a word
def try_generate_roles_no_ref(word, labels, prob_by_letter, roles, pos, best_word_hyps_list, search_space, MAX_ROLES_COUNT, COORD_EPSILON):
  if pos > len(labels):
    # print ("Word: %s" % word)
    # print ("Labels: %s" % str(labels))
    # print ("Roles: %s" % str(roles))
    checked = [False] * len(roles)
    hyp_word = construct_syls(word, labels, roles, checked)
    update_hyps_list(word, roles, hyp_word, checked, best_word_hyps_list)
    return

  # create all search coordinate for each letter
  if (pos > 0):
    idx = pos-1
    new_search_coord = create_search_coord(word, roles, idx)


    # If the role assigned to pos is too unlikely, stop
    if search_space.get_best_matched_coord_prob(new_search_coord) < COORD_EPSILON:
      return
    if pos == len(labels):
      try_generate_roles_no_ref(word, labels, prob_by_letter, roles, pos + 1, best_word_hyps_list, search_space, MAX_ROLES_COUNT, COORD_EPSILON)
      return

  if labels[pos] == CONSONANT:
    # Assign all possible roles to a consonant
    for idx in range(len(ValidConsoRoles)):
      role = ValidConsoRoles[idx]
      if role_count[role] >= (MAX_ROLES_COUNT[role]):
        continue
      else:
        role_count[role] = role_count[role] + 1
        if is_valid_subsyllabic_unit(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos):
          try_generate_roles_no_ref(word, labels, prob_by_letter, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos + 1, best_word_hyps_list, search_space, MAX_ROLES_COUNT, COORD_EPSILON)
        role_count[role] = role_count[role] - 1
  elif labels[pos] == VOWEL:
    # Assign all possible roles to a vowel
    tmp_ValidVowelRoles = ValidVowelRoles
    if word[pos] == "y" or word[pos] == "i" or word[pos] == "u" or word[pos] == "e":
      tmp_ValidVowelRoles = tmp_ValidVowelRoles + [ONSET]
    if word[pos] == "u" or word[pos] == "e":
      tmp_ValidVowelRoles = tmp_ValidVowelRoles + [CODA]
    for idx in range(len(tmp_ValidVowelRoles)):
      role = tmp_ValidVowelRoles[idx]
      if role_count[role] >= (MAX_ROLES_COUNT[role]):
        continue
      else:
        role_count[role] = role_count[role] + 1
        if is_valid_subsyllabic_unit(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos):
          try_generate_roles_no_ref(word, labels, prob_by_letter, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos + 1, best_word_hyps_list, search_space, MAX_ROLES_COUNT, COORD_EPSILON)
        role_count[role] = role_count[role] - 1

#---------------- CHECK IF A SUBSYLLABIC UNIT IS VALID ------------------#
# From position pos, look backwards along the string to check if the current
# subsyllabic unit is valid
def is_valid_subsyllabic_unit(word, labels, roles, pos):
  # if the letter under consideration is at the beginning of the string
  # check if the letter is assigned a valid role to be at the
  # beginning of the word
  word_beginning = 0
  for i in range(len(roles)):
    if roles[i] != REMOVE:
      word_beginning = i
      break
  # impossible assignment for a word beginning
  # print word_beginning
  if pos == word_beginning:
    if labels[pos] == CONSONANT and \
    (roles[pos] == CODA or roles[pos] == NUCLEUS or roles[pos] == CODA_ONSET \
      or roles[pos] == CODA_ONSET_NUCLEUS):
      return False

  # if pos == 6:
  #   print pos
  #   print roles
  #   print roles[pos]
  #   print labels
  #   print labels[pos]
  
  # if pos is at the end of the word
  # check if the final letter is a valid subsyllabic unit
  if pos == len(roles) - 1:
    word_ending = -1
    for i in reversed(range(0, len(roles))):
      if roles[i] != REMOVE:
        word_ending = i
        break

    #print "word_ending: " + str(word_ending)
    if word_ending >= 0:
      curr_role = roles[word_ending].split("_")[-1]
      if roles[word_ending] == ONSET or roles[word_ending] == CODA_ONSET or roles[word_ending] == NUCLEUS:
        return False

  last_non_R_pos = -1
  end_of_unit = -1
  curr_role = ""
  subsyl_unit = ""

  # Get the last position in the word that is not assgined the REMOVE role
  for i in reversed(range(0, pos)):
    if roles[i] != REMOVE:
      last_non_R_pos = i
      break

  # Check if pos is a subsyllabic unit's boundary
  if last_non_R_pos >= 0:
    # if a syllable can be formed by the letter alone
    # check the previous sub-syllabic unit
    if roles[pos] == ONSET_NUCLEUS_CODA:
      curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    # if the letter is assigned a role CODA_ONSET_NUCLEUS
    elif roles[pos] == CODA_ONSET_NUCLEUS:
      # the letter must be a CONSONANT
      # if the last_non_R is also assigned CODA, expand
      if roles[last_non_R_pos] == CODA:
        subsyl_unit = word[pos]
        curr_role = CODA
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    # if the letter is assigned a role ONSET_NUCLEUS
    elif roles[pos] == ONSET_NUCLEUS:
      # the letter must be a CONSONANT
      # if the last_non_R is also assigned ONSET, expand
      if roles[last_non_R_pos] == ONSET:
        subsyl_unit = word[pos]
        curr_role = ONSET
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    # if the letter is assigned a role NUCLEUS_CODA
    elif roles[pos] == NUCLEUS_CODA:
      # the letter must be a VOWEL
      # if the last_non_R is also assigned NUCLEUS, expand
      if roles[last_non_R_pos] == NUCLEUS:
        subsyl_unit = word[pos]
        curr_role = NUCLEUS
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]
      end_of_unit = last_non_R_pos

    elif roles[pos] == CODA_ONSET:
      # the letter must be the end of a coda and the beginning of an onset
      # if the last_non_R is also assigned CODA, expand
      if roles[last_non_R_pos] == CODA:
        subsyl_unit = word[pos]
        curr_role = CODA
      # check the previous sub-syllabic unit is valid
      else:
        curr_role = roles[last_non_R_pos]
      
      end_of_unit = last_non_R_pos   
    else:
      if roles[pos] != roles[last_non_R_pos]:
        curr_role = roles[last_non_R_pos].split("_")[-1]
        end_of_unit = last_non_R_pos

        # Ignore if the role assignment at last_non_R_pos
        # is ONSET_NUCLEUS or ONSET_NUCLEUS_CODA or CODA_ONSET_NUCLEUS
        if roles[last_non_R_pos] in [ONSET_NUCLEUS, ONSET_NUCLEUS_CODA, CODA_ONSET_NUCLEUS]:
          return True
      else:
        # not yet at a subsyllabic unit's boundary
        if pos < len(roles)-1:
          return True
        else:
          curr_role = roles[pos]
          end_of_unit = len(roles)-1
    
    # If an ONSET is immediately followed by a CODA, CODA_ONSET_NUCLEUS
    # or ONSET_NUCLEUS_CODA, return false
    if roles[last_non_R_pos].split("_")[-1] == ONSET and \
    (roles[pos].split("_")[0] == CODA or roles[pos] == ONSET_NUCLEUS_CODA):
      return False

    # If a ONSET_NUCLEUS_CODA or NUCLEUS_CODA is immediately followed by a CODA, return false
    if (roles[last_non_R_pos] == ONSET_NUCLEUS_CODA or roles[last_non_R_pos] == NUCLEUS_CODA)and \
    roles[pos].split("_")[0] == CODA:
      return False

    # # if a NUCLEUS or NUCLEUS CODA can form an single syllable, return False
    # # since an equivalent hypothesis with a ONSET_NUCLEUS_CODA can be used instead
    last_last_non_R_pos = -1
    for j in reversed(range(0, last_non_R_pos)):
      if roles[j] != REMOVE:
        last_last_non_R_pos = j
        break

    if last_last_non_R_pos >= 0:
      if roles[last_last_non_R_pos].split("_")[-1] == CODA and \
      (roles[last_non_R_pos] == NUCLEUS or roles[last_non_R_pos] == NUCLEUS_CODA) and \
      roles[pos].split("_")[0] == ONSET:
        return False

    ############## DISABLE THIS FOR TEST ##########################################
    # if roles[last_non_R_pos] == NUCLEUS
    # and roles[pos] == ONSET or ONSET_NUCLEUS_CODA, return False
    # since an equivalent hypothesis of which roles[last_non_R_pos] == NUCLEUS_CODA
    # if roles[last_non_R_pos] == NUCLEUS and \
    # roles[pos].split("_")[0] == ONSET:
    #   return False


  #print ("end_of_unit: %d" % end_of_unit)
  # create the sub-syllabic unit
  if end_of_unit >= 0:
    for i in reversed(range(0, end_of_unit+1)):
      # if the role assigned to the letter at position i is REMOVE, skip the letter
      #print "i: " + str(i)
      if roles[i] == REMOVE:
        continue
      
      # break if NUCLEUS_CODA or ONSET_NUCLEUS_CODA is hit
      elif roles[i] == NUCLEUS_CODA or roles[i] == ONSET_NUCLEUS_CODA:
        break

      # if the role assigned to the letter at position i is the same as
      # curr_role, prepend the letter to the subsyllabic unit of consideration
      elif roles[i].split("_")[-1] == curr_role:
        #print "roles[i][-1]: " + roles[i].split("_")[-1]
        subsyl_unit = word[i] + subsyl_unit

        # stop if CODA_ONSET is hit
        if roles[i] == CODA_ONSET:
          break

      # stop if a new subsyllabic unit is hit
      else:
        break

    # print ("Curr role: %s" % curr_role)
    # print ("Subsyllabic unit: %s" % subsyl_unit)

    # Check if the subsyl_unit is a valid subsyllabic unit of the role curr_role (onset, nucleus, coda)
    if subsyl_unit != "":
      if not checkValidSubsylUnit(subsyl_unit, curr_role):
        return False

  return True

#---------------- GENERATE ALL POSSIBLE ROLES FOR ALPHABETS IN A WORD ------------------#
# Use the same code employed in SylStructGenerator
# However, there is no reference Vietnamese syllabic structures.
# Therefore, all hypothesis that don't:
# - Generate invalid subsyllabic units
# - Leave letters unused
# would be accepted

# Use a dictionary to keep count on the number times a role is assigned to a letter
role_count = {}
for role in PossibleRoles:
  role_count[role] = 0

def generate_roles_no_ref(word, labels, en_phones, search_space, COORD_EPSILON):
  thres_lvl = 0

  MAX_ROLES_COUNT = {}

  while thres_lvl < 3:
    MAX_ROLES_COUNT = set_thres_per_role(thres_lvl, word, MAX_ROLES_COUNT)
    print MAX_ROLES_COUNT


    best_word_hyps_list = []
    roles = [None] * len(labels)
    prob_by_letter = [0.0] * len(labels)
    try_generate_roles_no_ref(word, labels, prob_by_letter, roles, 0, best_word_hyps_list, search_space, MAX_ROLES_COUNT, COORD_EPSILON)

    # best_word_hyps_list = sorted(best_word_hyps_list, key=lambda hyp: hyp.mod_pen)

    # Pick out the top 20 hyps
    if len(best_word_hyps_list) > 0:
      # print ("Roles generation time: %0.1f" % (time.time() - start_time))  

      for idx in range(len(best_word_hyps_list)):
        best_word_hyps_list[idx].original_en_phonemes = en_phones
      return best_word_hyps_list
    
    thres_lvl = thres_lvl + 1
    print "New threshold per role"
  
  return []

#---------------- GET MOST PROBABLE HYPOTHESIS -------------------------#
def get_most_prob_hyp(hyps_list, search_space):
  # create all search coordinate for each letter
  for hyp_id in range(len(hyps_list)):
    hyp = hyps_list[hyp_id]
    word = hyp.original
    roles = hyp.roles

    hyps_list[hyp_id].prob_by_letter =[0.0] * len(word)

    for idx in range(len(word)):
      coord = Rule()
      coord.curr = [word[idx]]

      start = idx - N_GRAM_LEN/2
      end = idx + N_GRAM_LEN/2 + 1

      if start < 0:
        start = 0
      if end > len(word):
        end = len(word)

      for j in range(start, idx):
        coord.prev.append(word[j])
      for j in range(idx+1, end):
        coord.next.append(word[j])

      if len(coord.prev) < (N_GRAM_LEN/2):
        coord.prev = [DELIMITER] + coord.prev
      if len(coord.next) < (N_GRAM_LEN/2):
        coord.next.append(DELIMITER)
      coord.role = [roles[idx]]

      new_search_coord = SearchCoord()
      new_search_coord.coord = coord

      hyps_list[hyp_id].prob_by_letter[idx] = search_space.get_best_matched_coord_prob(new_search_coord)
    
    # print str(hyp.roles)
    # print str(hyp.prob_by_letter)
    hyps_list[hyp_id].construction_prob = reduce(lambda x, y: x*y, hyps_list[hyp_id].prob_by_letter)


  highest_compound_score_hyps = []
  if len(hyps_list) > 0:
    highest_compound_score_hyps = evaluate_compound_score([hyp for hyp in hyps_list])
    highest_compound_score_hyps = sorted(highest_compound_score_hyps, key=lambda hyp: hyp.compound_mod_score, reverse = True)
    report("---------------------- TOP COMPOUND SCORE HYPS ------------------------------")
    for hyp in highest_compound_score_hyps[0:10]:
      report(hyp.get_str())

  return highest_compound_score_hyps[0]
  # return word_hyps_sorted_by_compound_mod_score[0]

#---------------- RECOMPUTE MOD PEN -------------------------#
def recompute_mod_pen(hyps_list):
  for i in range(len(hyps_list)):
    hyps_list[i][0].compute_mod_error()
  return hyps_list


#---------------- COMPUTE COMPOUND ERROR -------------------------#
def compute_compound_score(hyps_list):
  # Find the maximum modification penalty
  max_mod_pen = max([hyp[0].mod_pen for hyp in hyps_list])

  # Subtract all hypothesis' mod pens by max_mod_pen and inverse
  for i in range(len(hyps_list)):
    hyps_list[i][0].normalized_mod_score = -(hyps_list[i][0].mod_pen - max_mod_pen)
  
  max_mod_score = max([hyp[0].normalized_mod_score for hyp in hyps_list])
  # normalize mod pen
  for i in range(len(hyps_list)):
    hyps_list[i][0].normalized_mod_score = hyps_list[i][0].normalized_mod_score*1.0 / (max_mod_pen+0.1)

  # compute compound mod_pen
  for i in range(len(hyps_list)):
    hyps_list[i][0].compound_mod_score = hyps_list[i][0].normalized_mod_score * 0.5 + hyps_list[i][-1] * 0.5

  return hyps_list

def compare_compound_score(hyp_1, hyp_2):
  prob_1 = hyp_1[-1]
  prob_2 = hyp_2[-1]

  mod_pen_1 = hyp_1[0].mod_pen
  mod_pen_2 = hyp_2[0].mod_pen

#---------------- UPDATE HYPS LIST -------------------------#
def update_hyps_list(orig_word, roles, new_word, checked, best_word_hyps_list):
  #print "encoded_vie_units: " + encoded_vie_units
  #print "new_word.get_encoded_unit: " + new_word.get_encoded_units()

  # print "roles: " + str(roles)
  # print "new_word: " + str(new_word)
  # print "are_all_subsyl_units_valid(new_word): " + str(are_all_subsyl_units_valid(new_word))
  # print "are_all_letters_used(checked): " + str(are_all_letters_used(checked))
  # print "checked: " + str(checked)
  # print "encoded_vie_units: " + encoded_vie_units
  # print "new_word.encoded_units: " + str(new_word.get_encoded_units())
  # print "\n"

  if not are_all_subsyl_units_valid(new_word):
    return

  if not are_all_letters_used(checked):
    return

  new_word_hyp = WordHyp()
  new_word_hyp.original = orig_word
  new_word_hyp.labels = label_letters(orig_word)
  new_word_hyp.roles = roles
  new_word_hyp.reconstructed_word = new_word
  
  new_word_hyp.compute_mod_error()
  new_word_hyp.award_hyp()
  new_word_hyp.extra_letter_count = new_word.to_plain_text().count(GENERIC_VOWEL)
  new_word_hyp.count_removal()
  new_word_hyp.count_compound_role()
  evaluate_phones_score(new_word_hyp)

  best_word_hyps_list.append(new_word_hyp)

  return

def get_units_roles_from_word(word):
  units = ""
  roles = ""

  units = " . ".join([" ".join([syl.onset, syl.nucleus, syl.coda]) for syl in word.syls])
  roles = " . ".join([syl.get_encoded_units() for syl in word.syls])

  return [units, roles]

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


# HELPER TO SCORE PHONES SCORE - TO BE REFACTORED
def evaluate_phones_score(hyp):
  phones_score = 0

  for idx in range(len(hyp.original_en_phonemes)):
    #if is_correct_compound_phone(hyp, idx) or is_correct_phone_removal(hyp, idx):
    if is_correct_compound_phone(hyp, idx):
      phones_score = phones_score + 1
  hyp.phones_score = phones_score
  return hyp

def is_correct_compound_phone(hyp, idx):
  EN_DIPTHONGS = ["EY", "AY", "OW", "AW", "OY", "ER", "AXR", "UW", "IY", "AX", "AO", "UH"]
  COMPOUND_EN_CONSOS = ["CH", "TH", "DH", "SH", "K", "TS"]

  curr_phone = hyp.original_en_phonemes[idx]; curr_role = hyp.roles[idx]
  if curr_phone in EN_DIPTHONGS or curr_phone in COMPOUND_EN_CONSOS:
    prev_phone = "" ; prev_role = ""
    next_phone = "" ; next_role = ""
    if idx > 0:
      prev_phone = hyp.original_en_phonemes[idx-1]
      prev_role = hyp.roles[idx-1]
    if idx < len(hyp.original_en_phonemes) - 1:
      next_phone = hyp.original_en_phonemes[idx+1]
      next_role = hyp.roles[idx+1]
    if prev_phone == "_":
      if prev_role.split("_")[-1] == curr_role.split("_")[0]:
        return True
    if next_phone == "_":
      if next_role.split("_")[0] == curr_role.split("_")[-1]:
        return True
  return False

def is_correct_phone_removal(hyp, idx):
  curr_phone = hyp.original_en_phonemes[idx]; curr_role = hyp.roles[idx]
  if curr_phone == "_" and hyp.roles[idx] == "R":
    if idx > 0:
      if not is_correct_compound_phone(hyp, idx-1):
        return True
    if idx < len(hyp.original_en_phonemes) - 1:
      if not is_correct_compound_phone(hyp, idx+1):
        return True
  return False

def evaluate_compound_score(possible_hyps):
  max_probability = max([hyp.construction_prob for hyp in possible_hyps])
  max_phones_score = max([hyp.phones_score for hyp in possible_hyps])
  for idx in range(len(possible_hyps)):
    possible_hyps[idx].compound_mod_score = possible_hyps[idx].construction_prob / max_probability + \
      possible_hyps[idx].phones_score / (max_phones_score + 0.1)
  return possible_hyps

# Helper function to log and print a message
def report(msg):
  print "%s\n" % msg
  logging.info(msg)

# ####### DEBUG #########
# subsyl_unit = 'ch'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'qu'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'y'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'lw'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'an'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'ne'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'i'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'tt'
# role = ONSET
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# 
# subsyl_unit = 'en'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'ae'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'aer'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'aernn'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'aernen'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'n'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'a'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'i'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'ell'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'wor'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'io'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'orld'
# role = NUCLEUS
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# 
# subsyl_unit = 'ln'
# role = CODA
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'lnn'
# role = CODA
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'en'
# role = CODA
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'ne'
# role = CODA
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'n'
# role = CODA
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'u'
# role = CODA
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# subsyl_unit = 'nk'
# role = CODA
# print subsyl_unit + " " + role + ": " + str(checkValidSubsylUnit(subsyl_unit, role))
# 
# sys.exit(1)
# #########

## Timing
start_time = time.time()

# ter_stats_file = open(run_dir  + "/TER_stats_run_" + ts, "w")
# ser_stats_file = open(run_dir  + "/SER_stats_run_" + ts, "w")
# ter_csv_writer = csv.writer(ter_stats_file)
# ser_csv_writer = csv.writer(ser_stats_file)

# Try 10 iterations
targ_file_name = os.path.abspath(targ_file_name)
targ_file = open(targ_file_name, "r")

targ_file_t2p_input_name = targ_file_name + ".cap"
targ_file_t2p_input = open(targ_file_t2p_input_name, "w")

for line in targ_file:
  targ_file_t2p_input.write(line.upper())
targ_file_t2p_input.close()
targ_file.close()

targ_file_t2p_output_name = targ_file_name + ".phones"
get_phonemes_with_g2p(t2p_decoder_path, targ_file_t2p_input_name, targ_file_t2p_output_name)

test_phones = []
targ_file_t2p_output = open(targ_file_t2p_output_name, "r")
for line in targ_file_t2p_output:
  test_phones.append(line.strip().split(" "))
targ_file_t2p_output.close()

[search_space, valid_units] = get_best_search_space()

test_split_file = open(run_dir + "/test_split", "w")
units_and_roles_file = open(run_dir + "/units_roles.txt", "w")
log_file = os.path.join(run_dir, "test_split_log")
logging.basicConfig(filename= log_file, level= logging.DEBUG, format='%(message)s')
report("---------------------- DECODING TEST FILE ------------------------------")

search_space_file = open(run_dir + "/search_space", "w")

search_space_file.write(search_space.to_str())
search_space_file.close()

solution_found = True
count = 0

targ_file = open(targ_file_name, "r")
print targ_file_name

for line in targ_file:
  start_time = time.time()

  word = line.strip()
  report("Decoding word: " + word)

  labels = label_letters(word)
  roles = [None] * len(word)
  en_phones = test_phones[count]

  best_hyp = WordHyp()
  COORD_EPSILON = 1.0
  while COORD_EPSILON >= MIN_COORD_EPSILON:
    hyps_list = generate_roles_no_ref(word, labels, en_phones, search_space, COORD_EPSILON)

    if len(hyps_list) > 0:
      # for hyp in hyps_list:
      #   hyp.get_str()

      best_hyp = get_most_prob_hyp(hyps_list, search_space)
      
      reconstructed_word = str(best_hyp.reconstructed_word)
      reconstructed_word = reconstructed_word[1:-1]
      reconstructed_word = [part.strip().split(" ") for part in reconstructed_word.split(" ] [ ")]
      reconstructed_word = " . ".join(["".join(syl) for syl in reconstructed_word])

      test_split_file.write(reconstructed_word + "\n")
      units_and_roles_file.write("\t".join(get_units_roles_from_word(best_hyp.reconstructed_word)) + "\n")
      report("Generation time: " + str(time.time() - start_time))
      break
    else:
      report("No splitting could be found for " + word)
      report("Lowering threshold " + word)
      COORD_EPSILON = COORD_EPSILON / 10.0

  count = count + 1


test_split_file.close()
units_and_roles_file.close()
targ_file.close()

# word = 'granique'
# labels = label_letters(word)
# roles = ['O_N' , 'O' , 'N' , 'O' , 'N' , 'Cd' , 'Cd' , 'Cd']
# for pos in range(len(roles)):
#   printis_valid_subsyllabic_unit(word, labels, roles, pos)

  # if solution_found:
  #   prep_data(ts, i)
  #   train_g2p_models(ts, i)
  #   test_g2p_models(ts, i)
  #   [all_ter, all_ser] = reconstruct_vie_and_score(ts, i, ref_file)

  #   max_order = 6
  #   for order in range(max_order):
  #     output = ["Iter " + str(i+1)] + all_ter
  #     ter_csv_writer.writerow(output)

  #     output = ["Iter " + str(i+1)] + all_ser
  #     ser_csv_writer.writerow(output)

# ter_stats_file.close()
# ser_stats_file.close()
