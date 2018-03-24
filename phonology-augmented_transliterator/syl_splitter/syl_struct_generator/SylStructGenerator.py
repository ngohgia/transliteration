# Generate all possible syllable structure hypothesis of the entries in an input file
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LangAssets.LangAssets import LangAssets
from LangAssets.Syllable import Syllable
from LangAssets.Word import Word
from LangAssets.WordHyp import WordHyp

#---------------- IMPORT ALL VALID ENGLISH CONSONANTS/ VOWELS ---------------

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
REMOVE = "R"


lang_assets = LangAssets()
VOWEL = LangAssets.VOWEL
CONSONANT = LangAssets.CONSONANT
GENERIC_VOWEL = LangAssets.GENERIC_VOWEL

PossibleRoles = LangAssets.POSSIBLE_ROLES
ValidEnConsos = lang_assets.valid_en_consos
ValidEnVowels = lang_assets.valid_en_vowels

ValidVieConsos = lang_assets.valid_vie_consos
ValidVieVowels = lang_assets.valid_vie_vowels

ValidConsoRoles = LangAssets.VALID_CONSO_ROLES
ValidVowelRoles = LangAssets.VALID_VOWEL_ROLES

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
  ONSET_NUCLEUS: 0.2,
  NUCLEUS_ONSET: 0.2,
  NUCLEUS_NUCLEUS: 0.2,
  NUCLEUS_CODA: 0.2,
  CODA_ONSET: 0.2,
  CODA_NUCLEUS: 0.2,
  CODA_CODA: 0.2,
  REMOVE: 0.2,
}

#print ValidEnConsos
#print ValidEnVowels
#print ValidSubSylUnit[ONSET]
#print ValidSubSylUnit[NUCLEUS]
#print ValidSubSylUnit[CODA]

#---------------- LABEL ALL LETTERS IN A WORD ------------------#
def label_letters(word):
  labels = [None] * len(word)

  for pos in range(len(word)):
    if word[pos] not in ValidEnVowels and word[pos] not in ValidEnConsos:
      print "ERROR: Unlabeled letter %s in word %s" % (word[pos], word)
      sys.exit(1)
    else:
      if word[pos] in ValidEnVowels:
        labels[pos] = VOWEL
      elif word[pos] in ValidEnConsos:
        labels[pos] = CONSONANT

  return labels

#---------------- ENCODE A VIETNAMESE ENTRY IN SUBSYLLABIC UNITS ------------------#
def encode_vie_word(word):
  syls = word.split(".")
  toneless_syls = [(" ").join(syl.strip().split(" ")[:-1]) for syl in syls]

  encoded_units = []
  for syl in toneless_syls:
    vie_phons = syl.split(" ")
    syl_struct = [None] * len(vie_phons)

    # Encode the nucleus of the syllable
    for i in range(len(vie_phons)):
      phon = vie_phons[i]
      if phon in ValidVieVowels:
        syl_struct[i] = NUCLEUS
        break

    for i in range(len(vie_phons)):
      phon = vie_phons[i]
      # Check if a phone is either a valid Vietnamese vowels or consonants
      if phon not in ValidVieVowels and phon not in ValidVieConsos:
        print ("Error: unaccounted phon %s" % vie_phons[i])
        sys.exit(1)

      if phon in ValidVieConsos:
        # Encode the syllable's onset
        if i+1 < len(syl_struct) and syl_struct[i+1] == NUCLEUS:
          syl_struct[i] = ONSET
        # Encode the syllable's coda
        elif i-1 >= 0 and syl_struct[i-1] == NUCLEUS:
          syl_struct[i] = CODA
    encoded_units.append(" ".join(syl_struct))

  return " . ".join(encoded_units)

#---------------- GENERATE ALL POSSIBLE ROLES FOR ALPHABETS IN A WORD ------------------#

# Use a dictionary to keep count on the number times a role is assigned to a letter
role_count = {}
for role in PossibleRoles:
  role_count[role] = 0

def generate_roles(word, labels, roles, pos, encoded_vie_units, best_word_hyps_list):
  # roles[pos] is not yet assigned
  if pos-1 >= 0 and (roles[pos-1] != REMOVE or pos == len(roles)):
    #print ("Word: %s" % word)
    #print ("Labels: %s" % str(labels))
    #print ("Roles: %s" % str(roles))
    if not is_valid_subsyllabic_unit(word, labels, roles, pos-1):
      #print " Invalid at: " + str(pos-1)
      #print ("Word: %s" % word)
      #print ("Labels: %s" % str(labels))
      #print ("Roles: %s" % str(roles))
      return

  if pos >= len(labels):
    #print ("Word: %s" % word)
    #print ("Labels: %s" % str(labels))
    #print ("Roles: %s" % str(roles))
    hyp_word = construct_syls(word, labels, roles)
    #print ("hyp_word: %s" % str(hyp_word))
    update_best_hyp_words_list(word, encoded_vie_units, roles, hyp_word, best_word_hyps_list)
    return
  # if the boundary of a subsyllabic unit is hit, check for the validity of the unit
  # ignore the checkingwhen the role assigned to the letter is REMOVE
  # if the subsyllabic unit is invalid, return

  if labels[pos] == CONSONANT:
    for idx in range(len(ValidConsoRoles)):
      role = ValidConsoRoles[idx]
      if role_count[role] >= (len(labels) * MAX_ROLES_RATIOS[role] + 1):
        continue
      else:
        role_count[role] = role_count[role] + 1
        generate_roles(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos + 1, encoded_vie_units, best_word_hyps_list)
        role_count[role] = role_count[role] - 1
  elif labels[pos] == VOWEL:
    for idx in range(len(ValidVowelRoles)):
      role = ValidVowelRoles[idx]
      if role_count[role] >= (len(labels) * MAX_ROLES_RATIOS[role] + 1):
        continue
      else:
        role_count[role] = role_count[role] + 1
        generate_roles(word, labels, roles[0:pos] + [role] + roles[pos+1:len(labels)], pos + 1, encoded_vie_units, best_word_hyps_list)
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
  if pos == word_beginning:
    # roles[pos] can only possibly be ONSET or NUCLEUS
    if roles[pos] != ONSET and roles[pos] != NUCLEUS:
      return False
  
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
      if roles[word_ending].split("_")[-1] == ONSET:
        return False

  last_non_R_pos = -1
  end_of_unit = -1
  curr_role = ""
  subsyl_unit = ""

  # Get the last position in the word that is not assgined the REMOVE role
  # if the position of consideration is at the end of the word and is not
  # assigned a REMOVE role, it is the last_non_R_pos
  for i in reversed(range(0, pos)):
    if roles[i] != REMOVE:
      last_non_R_pos = i
      break
  #if pos == len(roles)-1 and roles[pos] != REMOVE:
  #  last_non_R_pos = pos

  # if end of the word is reached
  if pos == len(roles)-1 and roles[pos] != REMOVE:
    if roles[pos] == NUCLEUS_CODA and labels[pos] == VOWEL:
      # the syllabel is one single vowel
      return True

  #print ("last_non_R_pos: %d" % last_non_R_pos)
  if last_non_R_pos >= 0: 
    if roles[last_non_R_pos] == NUCLEUS_CODA and labels[last_non_R_pos] == VOWEL:
      # the syllabel is one single vowel
      return True

    # if role is either ONSET, CODA or NUCLEUS
    if len(roles[pos].split("_")) == 1:
      if last_non_R_pos >= 0:
        if roles[pos].split("_")[0] == CODA:
          if roles[last_non_R_pos].split("_")[-1] == ONSET or \
          (roles[last_non_R_pos].split("_")[-1] == NUCLEUS and labels[last_non_R_pos] == CONSONANT):
            return False        
        if roles[pos] != roles[last_non_R_pos]:
          end_of_unit = last_non_R_pos
          #print ("roles[last_non_R_pos]: %s" % roles[last_non_R_pos])
          curr_role = roles[last_non_R_pos].split("_")[-1]
    else:
      if last_non_R_pos >= 0:
        if roles[pos].split("_")[0] == CODA and \
        not (roles[pos] == NUCLEUS_CODA and labels[pos] == VOWEL):
          if roles[last_non_R_pos].split("_")[-1] == ONSET or \
          (roles[last_non_R_pos].split("_")[-1] == NUCLEUS and labels[last_non_R_pos] == CONSONANT):
            return False
        #print "CODA follows ONSET"

        if roles[pos].split("_")[0] == NUCLEUS and \
        roles[last_non_R_pos] == ONSET_NUCLEUS and labels[last_non_R_pos] == CONSONANT:
          return False
        #print "NUCLEUS follows GENERIC_VOWEL"
        
        if roles[pos].split("_")[0] == roles[last_non_R_pos].split("_")[-1]:
          end_of_unit = last_non_R_pos
          curr_role = roles[pos].split("_")[0]
          subsyl_unit = word[pos]
        else:
          if word[pos] not in ValidSubSylUnit[roles[pos].split("_")[0]]:
            return False
          else:
            end_of_unit = last_non_R_pos
            curr_role = roles[last_non_R_pos].split("_")[-1]

  #print ("end_of_unit: %d" % end_of_unit)
  # create the subsyllabic unit
  if end_of_unit >= 0:
    for i in reversed(range(0, end_of_unit+1)):
      # if the role assigned to the letter at position i is REMOVE, skip the letter
      #print "i: " + str(i)
      if roles[i] == REMOVE:
        continue
      # Exception: if the current role of consideration is nucleus
      # if the letter at position i is a consonant and is assigned role
      # "NN", the letter is not prepened to subsyl_unit
      elif curr_role == NUCLEUS and labels[i] == CONSONANT \
        and (roles[i] == NUCLEUS_NUCLEUS or roles[i] == CODA_NUCLEUS or roles[i] == ONSET_NUCLEUS):
          break
      # if the role assigned to the letter at position i is the same as
      # curr_role, prepend the letter to the subsyllabic unit of consideration
      elif roles[i].split("_")[-1] == curr_role:
        #print "roles[i][-1]: " + roles[i].split("_")[-1]
        subsyl_unit = word[i] + subsyl_unit
      # otherwise, a subsyllabic boundary is hit
      # check if the letter can still be prepended to the subsyllabic unit of consideration
      else:
        break

    #print ("Curr role: %s" % curr_role)
    #print ("Subsyllabic unit: %s" % subsyl_unit)

    if subsyl_unit in ValidEnConsos and curr_role == NUCLEUS:
      return True

    # Check if the subsyl_unit is a valid subsyllabic unit of the role curr_role (onset, nucleus, coda)
    if subsyl_unit != "" and \
    subsyl_unit not in ValidSubSylUnit[curr_role]:
      return False

  return True

#---------------- CONSTRUCT SYLLABLES ------------------#
def construct_syls(word, labels, roles):
  reconstructed_word = Word()
  # Search for the first letter that is assigned the NUCLEUS role
  idx = 0
  while idx < len(roles):
    #print "idx: " + str(idx)
    if roles[idx] == NUCLEUS:
      new_syl = Syllable()
      #print ("idx: %d" % idx)
      if labels[idx] == CONSONANT:
        #print ("NUCLEUS at %d is %s" % (idx, word[idx]))
        # if the letter is labeled CONSONANT
        # generate a new syllable with the letter at the ONSET position
        # and a generic vowel as the NUCLEUS
        new_syl.onset = word[idx]
        new_syl.nucleus = GENERIC_VOWEL
        # the syllable is complete, move idx to the next letter
        idx = idx + 1
        reconstructed_word.add_new_syl(new_syl)
      else:
      	#print ("Vowel at %d is %s" % (idx, word[idx]))
        new_syl = add_onset(word, labels, roles, new_syl, idx-1)
        #print ("new_syl after adding onset: %s" % new_syl.to_plain_text())
        new_syl.nucleus = word[idx]
        if idx == len(roles)-1:
          idx = len(roles)
        for j in range(idx+1, len(roles)):
          if roles[j] == REMOVE:
            # skip the letter
            if j >= len(roles)-1:
              idx = len(roles)
            continue
          elif roles[j] == NUCLEUS:
            # append the letter to the nucleus of the syllable
            new_syl.nucleus = new_syl.nucleus + word[j]
            # If the nucleus reaches the end of the word, set idx == len(roles) and terminate the loop
            if j >= len(roles)-1:
              idx = len(roles)
          elif roles[j] == NUCLEUS_NUCLEUS:
            new_syl.nucleus = new_syl.nucleus + word[j]
            # the syllable is complete, nucleus of the next syllable
            # starts from the current letter
            idx = j
            break
          elif roles[j] == NUCLEUS_ONSET:
            new_syl.nucleus = new_syl.nucleus + word[j]
            # the syllable is complete, move idx to the next letter
            idx = j + 1
            break
          # only merge the letter assigned NUCLEUS_CODA to the current syllable if 
          # the letter is a consonant. A vowel assiedn NUCLEUS_CODA forms a single
          # syllable
          elif roles[j] == NUCLEUS_CODA and labels[j] == CONSONANT:
            new_syl.nucleus = new_syl.nucleus + word[j]
            new_syl.coda = word[j]
            # construct the coda to complete the word
            # move idx
            [new_syl, idx] = add_coda(word, labels, roles, new_syl, j+1)
            break
          else:
            # look for coda of the syllable
            #print "start looking for coda from: " + str(j)
            [new_syl, idx] = add_coda(word, labels, roles, new_syl, j)
            break
        reconstructed_word.add_new_syl(new_syl)
        #print ("Complete new_syl: %s" % new_syl.to_plain_text())
    elif roles[idx] == NUCLEUS_NUCLEUS:
      new_syl = Syllable()
      if labels[idx] == CONSONANT:
        # if the letter is labelled CONSONANT
        # generate a new syllable with the letter at the ONSET position
        # and a generic vowel as the NUCLEUS
        new_syl.onset = word[idx]
        new_syl.nucleus = GENERIC_VOWEL
        # the syllable is comlete, move idx to the next letter
        idx = idx + 1
        reconstructed_word.add_new_syl(new_syl)
      else:
        # if there is no other NUCLEUS immediately preceding this letter        
        for j in reversed(range(0, idx)):
          if roles[j] != REMOVE:
            if roles[j].split("_")[-1] != NUCLEUS:
              new_syl = Syllable()
              new_syl = add_onset(word, labels, roles, new_syl, idx-1)
              new_syl.nucleus = word[idx]
              reconstructed_word.add_new_syl(new_syl)
            break

        # there is no onset in the syllable
        new_syl = Syllable()
        new_syl.nucleus = word[idx]
        if idx == len(roles)-1:
          idx = len(roles)
        for j in range(idx+1, len(roles)):
          if roles[j] == REMOVE:
            if j >= len(roles)-1:
              idx = len(roles)
            # skip the letter
            continue
          elif roles[j] == NUCLEUS:
            # append the letter to the nucleus of the syllable
            new_syl.nucleus = new_syl.nucleus + word[j]
            # If the nucleus reaches the end of the word, set idx == len(roles) and terminate the loop
            if j >= len(roles)-1:
              idx = len(roles)
          elif roles[j] == NUCLEUS_NUCLEUS:
            new_syl.nucleus = new_syl.nucleus + word[j]
            # the syllable is complete, nucleus of the next syllable
            # starts from the current letter
            idx = j
            break
          elif roles[j] == NUCLEUS_ONSET:
            new_syl.nucleus = new_syl.nucleus + word[j]
            # the syllable is complete, move idx to the next letter
            idx = j + 1
            break
          # only merge the letter assigned NUCLEUS_CODA to the current syllable if 
          # the letter is a consonant. A vowel assiedn NUCLEUS_CODA forms a single
          # syllable
          elif roles[j] == NUCLEUS_CODA and labels[j] == CONSONANT:
            new_syl.nucleus = new_syl.nucleus + word[j]
            new_syl.coda = word[j]
            # construct the coda to complete the word
            # move idx
            [new_syl, idx] = add_coda(word, labels, roles, new_syl, idx+1)
            break
          else:
            # look for coda of the syllable
            [new_syl, idx] = add_coda(word, labels, roles, new_syl, j)
            break
        reconstructed_word.add_new_syl(new_syl)
    elif roles[idx] == ONSET_NUCLEUS:
      new_syl = Syllable()

      if labels[idx] == CONSONANT:
        new_syl.onset = word[idx]
        new_syl.nucleus = GENERIC_VOWEL
        idx = idx + 1
        reconstructed_word.add_new_syl(new_syl)
      else:
        new_syl.onset = word[idx]
        new_syl = add_onset(word, labels, roles, new_syl, idx-1)
        new_syl.nucleus = word[idx]

        if idx == len(roles)-1:
          idx = len(roles)
        for j in range(idx+1, len(roles)):
          if roles[j] == REMOVE:
            if j >= len(roles)-1:
              idx = len(roles)
            # skip the letter
            continue
          elif roles[j] == NUCLEUS:
            # append the letter to the nucleus of the syllable
            new_syl.nucleus = new_syl.nucleus + word[j]
            # If the nucleus reaches the end of the word, set idx == len(roles) and terminate the loop
            if j >= len(roles)-1:
              idx = len(roles)
          elif roles[j] == NUCLEUS_NUCLEUS:
            new_syl.nucleus = new_syl.nucleus + word[j]
            # the syllable is complete, nucleus of the next syllable
            # starts from the current letter
            idx = j
            break
          elif roles[j] == NUCLEUS_ONSET:
            new_syl.nucleus = new_syl.nucleus + word[j]
            # the syllable is complete, move idx to the next letter
            idx = j + 1
            break
          # only merge the letter assigned NUCLEUS_CODA to the current syllable if 
          # the letter is a consonant. A vowel assiedn NUCLEUS_CODA forms a single
          # syllable
          elif roles[j] == NUCLEUS_CODA and labels[j] == CONSONANT:
            new_syl.nucleus = new_syl.nucleus + word[j]
            new_syl.coda = word[j]
            # construct the coda to complete the word
            # move idx
            [new_syl, idx] = add_coda(word, labels, roles, new_syl, idx+1)
            break
          else:
            # look for coda of the syllable
            [new_syl, idx] = add_coda(word, labels, roles, new_syl, j)
            break
          reconstructed_word.add_new_syl(new_syl)
    elif roles[idx] == CODA_NUCLEUS:
      new_syl = Syllable()
      if labels[idx] == CONSONANT:
        new_syl.onset = word[idx]
        new_syl.nucleus = GENERIC_VOWEL
        # the syllable is comlete, move idx to the next letter
        reconstructed_word.add_new_syl(new_syl)
      idx = idx + 1
    elif roles[idx] == NUCLEUS_CODA and labels[idx] == VOWEL:
      new_syl = Syllable()
      new_syl.nucleus = word[idx]
      # the syllable is comlete, move idx to the next letter
      reconstructed_word.add_new_syl(new_syl)
      idx = idx + 1
    else:
      # skip the letter
      idx = idx + 1
  return reconstructed_word

#---------------- ADD ONSET -------------------------#
def add_onset(word, labels, roles, new_syl, end_idx):
  # Search backwards from the end_idx to 0 to find all letters
  # that can be prepended to the new_syl's onset
  for idx in reversed(range(0, end_idx+1)):
    if roles[idx] == REMOVE:
      continue
    elif roles[idx].split("_")[-1] == ONSET:
      new_syl.onset = word[idx] + new_syl.onset
      if len(roles[idx].split("_")) > 1:
        return new_syl
    else:
      return new_syl
  return new_syl

#---------------- ADD CODA -------------------------#
def add_coda(word, labels, roles, new_syl, start_idx):
  # Search forwards from the start_idx to the end to find all letters
  # that can be appended to the new_syl's coda
  #print "add_coda start_idx: " + str(start_idx)
  idx = start_idx
  while idx < len(roles):
    if roles[idx] == REMOVE:
      idx = idx + 1
    elif roles[idx].split("_")[0] == CODA:
      new_syl.coda = new_syl.coda + word[idx]
      if len(roles[idx].split("_")) > 1:
        return [new_syl, idx]
    else:
      return [new_syl, idx]
    idx = idx + 1
  return [new_syl, idx]

#---------------- UPDATE BEST HYP WORD LIST -------------------------#
def update_best_hyp_words_list(orig_word, encoded_vie_units, roles, new_word, best_word_hyps_list):
  #print "encoded_vie_units: " + encoded_vie_units
  #print "new_word.get_encoded_unit: " + new_word.get_encoded_units()
  if new_word.get_encoded_units() == encoded_vie_units:
    new_word_hyp = WordHyp()
    new_word_hyp.original = orig_word
    new_word_hyp.labels = label_letters(orig_word)
    new_word_hyp.roles = roles
    new_word_hyp.reconstructed_word = new_word
    new_word_hyp.mod_pen = levenshtein(new_word.to_plain_text(), orig_word)

    #print new_word_hyp.get_str()

    if len(best_word_hyps_list) == 0:
      best_word_hyps_list.append(new_word_hyp)
      return
    # If the new hypothesized word has the same edit distance to the original word
    # as it is of the first word in the list of current best hypothesized words list,
    # add the new hypothesized word to the list
    if new_word_hyp.mod_pen == best_word_hyps_list[0].mod_pen:
      best_word_hyps_list.append(new_word_hyp)
    # If the new hypothesized word has a LOWER edit distance to the original word
    # as it is of the first word in the list of current best hypothesized words list,
    # CLEAR the list and add the new hypothesized word into the list
    elif new_word_hyp.mod_pen < best_word_hyps_list[0].mod_pen:
      best_word_hyps_list.append(new_word_hyp)
  return


#---------------- LEVENSHTEIN -------------------------#
# Calculate Levenshtein (edit distance) between two string
# This helper function is used to calculate the edit distance between a hypothesized syllable structure and
# the reference syllabic structure
# http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(s1, s2):
  if len(s1) < len(s2):
      return levenshtein(s2, s1)

  # len(s1) >= len(s2)
  if len(s2) == 0:
      return len(s1)

  previous_row = range(len(s2) + 1)
  for i, c1 in enumerate(s1):
      current_row = [i + 1]
      for j, c2 in enumerate(s2):
          insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
          deletions = current_row[j] + 1       # than s2
          substitutions = previous_row[j] + (c1 != c2)
          current_row.append(min(insertions, deletions, substitutions))
      previous_row = current_row

  return previous_row[-1]



# Timing
start_time = time.time()

#word = "bloembergen"
#"palestine"
#"bloembergen"
#estenssoro  E t _2 . s @: _3 . t E n _1 . s o _1 . r\ o _1

# -------- Unit test for Vietnamese word encoding ------------
#vie_word = "E t _2 . s @: _3 . t E n _1 . s o _1 . r\ o _1"
#encoded_vie_units = encode_vie_word(vie_word)
#print ("Vietnamese word: %s" % vie_word)
#print ("Encoded Vietnamese units: %s" % encoded_vie_units)

# -------- Unit test for labelling a word ------------
#labels = label_letters(word)
#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))

# -------- Unit test for checking if a subsyllabic unit is valid ------------
#word = "asterisk"
#print ("Word: %s" % word)
#labels = label_letters(word)
#roles = [NUCLEUS, ONSET, ONSET, NUCLEUS, NUCLEUS_ONSET, NUCLEUS, CODA, CODA]
#print "Valid onset at position 2: " + str(is_valid_subsyllabic_unit(word, labels, roles, 2))
#print "Valid nucleus at position 4: " + str(is_valid_subsyllabic_unit(word, labels, roles, 4))

#roles = [ONSET, ONSET, ONSET, NUCLEUS, NUCLEUS_ONSET, NUCLEUS, CODA, CODA]
#print "Valid nucleus at position 2: " + str(is_valid_subsyllabic_unit(word, labels, roles, 2))

#roles = [NUCLEUS, NUCLEUS_NUCLEUS, ONSET, NUCLEUS, NUCLEUS_ONSET, NUCLEUS, CODA, CODA]
#print "Valid nucleus at position 1: " + str(is_valid_subsyllabic_unit(word, labels, roles, 1))
#print "Valid onset at position 2: " + str(is_valid_subsyllabic_unit(word, labels, roles, 2))

#word = "asterisk"
#print ("Word: %s" % word)
#labels = label_letters(word)
#roles = [NUCLEUS, ONSET, ONSET, NUCLEUS, NUCLEUS_ONSET, NUCLEUS, CODA, CODA]
#print "Valid onset at position 2: " + str(is_valid_subsyllabic_unit(word, labels, roles, 2))
#print "Valid nucleus at position 4: " + str(is_valid_subsyllabic_unit(word, labels, roles, 4))

#word = "estenssoro"
#labels = label_letters(word)

#roles = ['O', 'Cd_O', 'O', 'O', 'Cd_O', 'N', 'Cd_O', 'N', 'N', 'N']
#roles = [ 'N', 'Cd_N', 'O', 'N', 'N', 'N' ,'Cd_N', 'R', 'Cd_N', 'R' ]
#roles =['N', 'O', 'O', 'O', 'O', 'Cd', 'Cd', 'N', 'N', 'R']
#roles = ['O', 'O', 'O', 'O', 'Cd_N', 'Cd_N', 'Cd_N', 'R', 'Cd_O', 'N']
# Correct
#roles = ['N', 'Cd_N', 'O', 'N', 'Cd', 'R', 'O', 'N', 'O', 'N']

#print ("Word: %s" % word)
#print ("Labels: %s" % labels)
#print ("Roles: %s" % roles)
#i = 2
#print ("Valid onset at position %d: %s" % (i, str(is_valid_subsyllabic_unit(word, labels, roles, i))))
#for i in range(len(roles)):
#  print ("\nPosition %d" % (i))
#  print ("Valid onset at position %d: %s" % (i, str(is_valid_subsyllabic_unit(word, labels, roles, i))))

#word = "almadies"
#roles = [ 'R' , 'O' , 'O' , 'N_N' , 'Cd_N' , 'R' , 'R' , 'N' ]
#roles = [ 'R' , 'O' , 'O' , 'N_N' , 'Cd_N' , 'R' , 'R' , 'N' ]
#labels = label_letters(word)

#constructed_syls = construct_syls(word, labels, roles)
#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))
#print ("Roles: %s" % str(roles))
#for i in range(len(roles)):
#  print ("\nPosition %d" % (i))
#  print ("Valid onset at position %d: %s" % (i, str(is_valid_subsyllabic_unit(word, labels, roles, i))))


#word = "bishkek"
#vie_word = "b_< i t _2 . s @: _3 . k e c _2"
#labels = label_letters(word)
#roles = ['O', 'N', 'Cd_N', 'R', 'O', 'N', 'Cd']
#roles = ['O', 'O', 'R', 'R', 'O', 'O', 'R']

#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))
#print ("Roles: %s" % str(roles))
#for i in range(len(roles)):
#  print ("\nPosition %d" % (i))
#  print ("Valid onset at position %d: %s" % (i, str(is_valid_subsyllabic_unit(word, labels, roles, i))))


#word = "klapheck"
#vie_word = "k @: _3 . l a: p _2 . h e c _2"
#roles = ['N', 'O', 'N', 'Cd', 'O', 'N', 'Cd', 'Cd']

# word = "abailard"
# # roles = ['N' , 'O' , 'N' , 'N' , 'O' , 'N' , 'O' , 'R']
# # roles = ['N' , 'N' , 'R' , 'N' , 'O' , 'N' , 'O_N' , 'R']
# #roles = ['N', 'O' , 'R' , 'N' , 'O' , 'N' , 'N_O' , 'R']

# word = 'adriatique'
# # vie_word = 'a: _1 . d_< @: _3 . r\ i _1 . a: _1 . t i c _2'
# # roles = ['N', 'O_N', 'O', 'N', 'N_N', 'O', 'N', 'Cd', 'Cd', 'Cd']
# # roles = ['N' , 'O' , 'R' , 'O_N' , 'N' , 'O_N' , 'N' , 'O' , 'N' , 'Cd']
# roles = ['N', 'O_N', 'O', 'N', 'N_Cd', 'O', 'N', 'Cd', 'Cd', 'Cd']

# word = 'addis'
# # vie_word = 'E t _2 . d_< i t _2 . s @: _3'
# roles = ['N', 'Cd', 'O', 'N', 'Cd_N']

# word = 'alexandrie'
# # # vie_word = 'a: _1 . l a: c _2 . s a N _1 . d_< @: _3 . r\ i _1'
# # roles = ['N', 'O', 'N', 'Cd_O', 'N', 'Cd', 'O_N', 'O', 'N', 'R']
# roles = ['N', 'O', 'N', 'Cd_O', 'N', 'Cd', 'O_N', 'O', 'N', 'N']


# word = 'florida'
# # vie_word = 'f @: _3 . l O _1 . r\ i _1 . d_< a: _1'
# roles = ['N', 'O', 'N', 'O', 'N', 'O', 'N']


# labels = label_letters(word)
# print ("Word: %s" % word)
# print ("Labels: %s" % str(labels))
# print ("Roles: %s" % str(roles))
# for i in range(len(roles)):
#   print ("\nPosition %d" % (i))
#   print ("Valid at position %d: %s" % (i, str(is_valid_subsyllabic_unit(word, labels, roles, i))))

# -------- Unit test for syllables construction ------------
#word = "palestine"
#labels = label_letters(word)
#roles = [ONSET, NUCLEUS, ONSET, NUCLEUS, CODA_NUCLEUS, ONSET, NUCLEUS, CODA, REMOVE]
#roles = ['O', 'N', 'O', 'O', 'Cd_O', 'Cd', 'N', 'N', 'N']
#roles = ['O', 'N', 'O', 'O', 'Cd_O', 'Cd', 'N', 'N', 'N_N']
#roles = ['O', 'N', 'O', 'O', 'Cd_O', 'Cd', 'N', 'Cd', 'N']

#word = "estenssoro"
#roles = [NUCLEUS, CODA_NUCLEUS, ONSET, NUCLEUS, CODA, REMOVE, ONSET, NUCLEUS, ONSET, NUCLEUS]
#roles = [ 'N' , 'Cd_N' , 'O' , 'N' , 'Cd' , 'O' , 'O' , 'N' , 'N_N' , 'Cd' ]
#labels = label_letters(word)

#constructed_syls = construct_syls(word, labels, roles)
#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))
#print ("Roles: %s" % str(roles))
#print ("Constructed syllables: %s" % str(constructed_syls))

#word = 'bishkek'
#roles = ['O', 'N', 'Cd_N', 'R', 'O', 'N', 'Cd']
#roles = ['O' , 'N' , 'Cd_N' , 'O' , 'R' , 'N' , 'Cd_N']
#roles = ['O', 'N', 'O', 'O', 'N', 'N', 'N']
#roles = ['O', 'N', 'N', 'Cd', 'Cd', 'Cd', 'R']

#labels = label_letters(word)
#constructed_syls = construct_syls(word, labels, roles)
#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))
#print ("Roles: %s" % str(roles))
#print ("Constructed syllables: %s" % str(constructed_syls))

#word = 'mornay'
#roles = ['O', 'N', 'O', 'N', 'R', 'N']
#labels = label_letters(word)
#constructed_syls = construct_syls(word, labels, roles)
#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))
#print ("Roles: %s" % str(roles))
#print ("Constructed syllables: %s" % str(constructed_syls))

#word = 'lastman'
#roles = ['O', 'N', 'O_N', 'N', 'O', 'N', 'Cd']
#labels = label_letters(word)
#constructed_syls = construct_syls(word, labels, roles)
#print ("Word: %s" % word)
#print ("Labels: %s" % str(labels))
#print ("Roles: %s" % str(roles))
#print ("Constructed syllables: %s" % str(constructed_syls))

#word = 'klapheck'
#roles = ['N', 'O', 'N', 'Cd', 'O', 'N', 'Cd', 'Cd']

# word = 'adriatique'
# vie_word = 'a: _1 . d_< @: _3 . r\ i _1 . a: _1 . t i c _2'
# roles = ['N', 'O_N', 'O', 'N', 'N_N', 'O', 'N', 'Cd', 'Cd', 'Cd']

# word = 'adriatique'
# #roles = ['N' , 'O' , 'R' , 'O_N' , 'N' , 'O_N' , 'N' , 'O' , 'N' , 'Cd']
# #roles = ['N', 'O_N', 'O', 'N', 'N', 'O', 'N_N', 'O', 'N', 'Cd']
# roles = ['N', 'O_N', 'O', 'N', 'N_Cd', 'O', 'N', 'Cd', 'Cd', 'Cd']

#word = 'addis'
# vie_word = 'E t _2 . d_< i t _2 . s @: _3'
#roles = ['N', 'Cd', 'O', 'N', 'Cd_N']

# word = 'alexandrie'
# vie_word = 'a: _1 . l a: c _2 . s a N _1 . d_< @: _3 . r\ i _1'
# # roles = ['N', 'O', 'N', 'Cd_O', 'N', 'Cd', 'O_N', 'O', 'N', 'R']
# roles = ['N', 'O', 'N', 'Cd_O', 'N', 'Cd', 'O_N', 'O', 'N', 'N']

# word = 'florida'
# # vie_word = 'f @: _3 . l O _1 . r\ i _1 . d_< a: _1'
# roles = ['N', 'O', 'N', 'O', 'N', 'O', 'N']

word = 'bishkek'
roles = ['O' , 'N' , 'Cd_O' , 'O_N' , 'O' , 'N' , 'Cd']

labels = label_letters(word)
constructed_syls = construct_syls(word, labels, roles)
print ("Word: %s" % word)
print ("Labels: %s" % str(labels))
print ("Roles: %s" % str(roles))
print ("Constructed syllables: %s" % str(constructed_syls))

# -------- Unit test for role generation ------------
#word = "palestine"
#word = "bloembergen"

#word = "estenssoro"
#vie_word = "E t _2 . s @: _3 . t E n _1 . s o _1 . r\ o _1"
#encoded_vie_units = encode_vie_word(vie_word)
#labels = label_letters(word)

#best_word_hyps_list = []
#roles = [None] * len(labels)
#generate_roles(word, labels, roles, 0, encoded_vie_units, best_word_hyps_list)
#for word_hyp in best_word_hyps_list:
#  print word_hyp.get_str()
# bucket = []
# for hyp_word in best_hyp_words_list:
#   bucket.append(str(hyp_word))
# bucket = set(bucket)
# hyp_counts = {}
# for item in bucket:
#   hyp_counts[item] = 0
# for hyp_word in best_hyp_words_list:
#   hyp_counts[str(hyp_word)] = hyp_counts[str(hyp_word)] + 1
# for hyp_word in hyp_counts:
#   print ("%s - %d" % (hyp_word, hyp_counts[hyp_word]))

# word = "bishkek"
# vie_word = "b_< i t _2 . s @: _3 . k e c _2"
# encoded_vie_units = encode_vie_word(vie_word)
# labels = label_letters(word)

# best_word_hyps_list = []
# roles = [None] * len(labels)
# generate_roles(word, labels, roles, 0, encoded_vie_units, best_word_hyps_list)
# for word_hyp in best_word_hyps_list:
#   print word_hyp.get_str()

# word = 'mornay'
# vie_word = 'm O k _2 . n aI _1'
# encoded_vie_units = encode_vie_word(vie_word)
# labels = label_letters(word)

# best_word_hyps_list = []
# roles = [None] * len(labels)
# generate_roles(word, labels, roles, 0, encoded_vie_units, best_word_hyps_list)
# for word_hyp in best_word_hyps_list:
#   print word_hyp.get_str()

#word = 'klapheck'
#vie_word = 'k @: _3 . l a: p _2 . h e c _2'

#word = 'uelen'
#vie_word = 'u _1 . e _1 . l E n _1'

#word = 'abailard'
#vie_word = 'a: _1 . b_< e _1 . l a: _1'

#word = 'alexandrie'
#vie_word = 'a: _1 . l a: c _2 . s a N _1 . d_< @: _3 . r\ i _1'

# # # word = 'adriatique'
# # # vie_word = 'a: _1 . d_< @: _3 . r\ i _1 . a: _1 . t i c _2'

# word = 'addis'
# vie_word = 'E t _2 . d_< i t _2 . s @: _3'

# word = 'aleksandrovich'
# vie_word = 'a: _1 . l E c _2 . s a N _1 . d_< @: _3 . r\ o _1 . v i c _2'

# word = 'florida'
# vie_word = 'f @: _3 . l O _1 . r\ i _1 . d_< a: _1'

# encoded_vie_units = encode_vie_word(vie_word)
# labels = label_letters(word)
# best_word_hyps_list = []
# roles = [None] * len(labels)
# generate_roles(word, labels, roles, 0, encoded_vie_units, best_word_hyps_list)
# for word_hyp in best_word_hyps_list:
#   print word_hyp.get_str()

# print ("Roles generation time: %0.1f" % (time.time() - start_time))
