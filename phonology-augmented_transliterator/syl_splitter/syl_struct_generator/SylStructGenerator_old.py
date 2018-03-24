# Generate all possible syllable structure hypothesis of the entries in an input file
import os
import sys
import copy
from lang_assets.EnVowels import EnVowels
from lang_assets.EnConsos import EnConsos
from Word import Word
from Syllable import Syllable
from WordHyp import WordHypothesis

import time

# Class of an alphabet in the syllable
VOWEL = "V"
CONSONANT = "C"

# Labels for the transformation of an alphabet
RIGHT = "R"        # The alphabet joins the preceding syllable
LEFT = "L"         # The alphabet joins the following syllable
SAME = "S"         # Stay at the same position, i.e. the alphabet becomes an individual syllable
LEFT_SAME = "LS"   # The alphabet is duplicated. One copy undergoes LEFT transformation and the other stays at the same position
LEFT_RIGHT = "LR"  # The alphabet is duplicated. One copy undergoes LEFT transformation and the other, RIGHT transformation.
REMOVED = "X"      # The alphabet is removed

# For a CONSONANT
CONSONANT_TRANS = [RIGHT, LEFT, SAME, LEFT_SAME, LEFT_RIGHT, REMOVED]
# For a VOWEL
VOWEL_TRANS = [RIGHT, LEFT, SAME, REMOVED]

# Symbol for generic vowel
GEN_VOWEL = "@"

# Class for syllable structure generation
class SylStructGenerator:
  # removal_thres: maximum proportion of alphabets that can be removed after the transformation
  def __init__(self, removal_thres):
    self.removal_thres = removal_thres

  # Label each letter of a word as VOWEL or CONSONANT
  def label_letter(self, word):
    # A position can be "skipped" if the maximum proportion of invalidated alphabets has not been reached
    # if invalid_count < len(word) * self.invalid_alpha_ratio:
    #   labels[pos] = REMOVED
    #   self.label_letter(all_labels, word, labels, pos+1, invalid_count+1)
    labels = [None] * len(word)

    for pos in range(len(word)):
      if word[pos] not in EnVowels.valid_graphemes and word[pos] not in EnConsos.valid_graphemes:
        print "ERROR: Unlabelled letter %s in word %s" % (word[pos], word)
        sys.exit(1)
      else:
        if word[pos] in EnVowels.valid_graphemes:
          labels[pos] = VOWEL
        elif word[pos] in EnConsos.valid_graphemes:
          labels[pos] = CONSONANT

    return labels
        

  # Generate transformation hypothesis for each position of the word
  def generate_transform_hyp(self, labels, trans, pos, all_hyps, removal_count):
    # If all the positions in the word have had their transformation generated
    if pos == len(labels):
      # Add a copy of trans to all_hyps
      trans_copy = copy.deepcopy(trans)
      all_hyps.append(trans_copy)
      #print "[ %s ]" % (" , ".join(trans_copy))
    else:
      # If the alphabet at position pos is a CONSONANT
      if labels[pos] == CONSONANT:
        # Iterate through transformation options for the alphabet at pos
        for option in CONSONANT_TRANS:
          # If the transformation option is "REMOVED",
          # check if the removal threshold has been reached
          # If the threshold is reached, skip
          if option == REMOVED:
            if removal_count >= self.removal_thres:
              continue
            else:
              trans[pos] = option
              self.generate_transform_hyp(labels, trans, pos+1, all_hyps, removal_count+1)

          trans[pos] = option
          self.generate_transform_hyp(labels, trans, pos+1, all_hyps, removal_count)

      # If the alphabet at position pos is a VOWEL
      elif labels[pos] == VOWEL:
        # All vowels has the option of staying at the same position
        trans[pos] = SAME
        self.generate_transform_hyp(labels, trans, pos+1, all_hyps, removal_count)

        # or each vowel can be combined with
        # a vowel on the left
        if pos-1 >= 0 and labels[pos-1] == VOWEL:
          trans[pos] = LEFT
          self.generate_transform_hyp(labels, trans, pos+1, all_hyps, removal_count)

        # a vowel on the right
        elif pos+1 < len(labels) and labels[pos+1] == VOWEL:
          trans[pos] = RIGHT
          self.generate_transform_hyp(labels, trans, pos+1, all_hyps, removal_count)

        # or removed if removal threshold has not been reached
        if removal_count < self.removal_thres:
          trans[pos] = REMOVED
          self.generate_transform_hyp(labels, trans, pos+1, all_hyps, removal_count+1)

  # Construct syllables from the labels and tranformation at each postion of the word
  def construct_syls(self, word, labels, trans):
    new_word = Word()
    for i in range(len(trans)):
      if trans[i] == "S" or trans[i] == "LS":
        # Generate a new syllable
        new_syl = Syllable()
        # If the current position is a "VOWEL"
        if labels[i] == VOWEL:
          new_syl.vowel = word[i]
        # If the current position is a "CONSONANT"
        elif labels[i] == CONSONANT:
          # Generate a vowel for the new syllable
          new_syl.vowel = GEN_VOWEL
          new_syl.ini_conso = word[i]

        # Search to the left for an alphabet that can be combined to the current syllable
        for j in reversed(range(0, i)):
          # An alphabet can be combined to the current syllable if its transformation is "R" or "LR"
          # stop the loop when reaching the first alphabet that is not of "R" or "LR" transformation
          if trans[j] == RIGHT or trans[j] == LEFT_RIGHT:
            # If the alphabet is a vowel, combine the alphabet with the current syllable's vowel
            if labels[j] == VOWEL:
              new_syl.vowel = word[j] + new_syl.vowel
            # If the alphabet is a consonant, add the alphabet to the current syllable's initial consonant
            elif labels[j] == CONSONANT:
              new_syl.ini_conso = word[j] + new_syl.ini_conso
          else:
            break

        # Search to the right for an alphabet that can be combined to the current syllable
        for j in range(i+1, len(word)):
          # An alphabet can be combined to the current syllable if its transformation is "L", "LS" or "LR"
          # stop the loop when reaching the first alphabet that is not of "L", "LR" or "LR" transformation
          if trans[j] == LEFT or trans[j] == LEFT_SAME or trans[j] == LEFT_RIGHT:
            # If the alphabet is a vowel, combine the alphabet with the current syllable's vowel
            if labels[j] == VOWEL:
              new_syl.vowel = new_syl.vowel + word[j]
            # If the alphabet is a consonant, add the alphabet to the current syllable's final consonant
            elif labels[j] == CONSONANT:
              new_syl.final_conso = new_syl.final_conso + word[j]
          else:
            break

        new_word.add_new_syl(new_syl)
    return new_word

  # Penalize transformations that don't actually affect the alphabet
  def penalize_invalid_transform(self, labels, trans):
    valid_trans = [True] * len(trans)
    # A RIGHT or LEFT_RIGHT transformation is invalid if there is a LEFT, LEFT_RIGHT, LEFT_SAME, or REMOVED transformation to its right prior to a SAME, or the word boundary is hit
    for pos in range(len(trans)):
      if trans[pos] == RIGHT:
        valid_trans[pos] = self.valid_RIGHT_transform(labels, trans, pos)
      elif trans[pos] == LEFT or trans[pos] == LEFT_SAME:
        valid_trans[pos] = self.valid_LEFT_transform(labels, trans, pos)
      elif trans[pos] == LEFT_RIGHT:
        valid_trans[pos] = self.valid_LEFT_RIGHT_transform(labels, trans, pos)
    # Penalty score is the number of invalid transformations
    penalty = 0
    for idx in range(len(valid_trans)):
      if valid_trans[idx] == False:
        penalty = penalty + 1
    return (penalty, valid_trans)

  # Check if a LEFT transformation is valid
  def valid_LEFT_transform(self, labels, trans, pos):
    # If the alphabet at index pos is a VOWEL
    if labels[pos] == VOWEL:
      # Iterate through the alphabets to the left of pos
      for idx in reversed(range(0,pos)):
        # Valid if a VOWEL of transformation SAME is found
        if labels[idx] == VOWEL and trans[idx] == SAME:
          return True
        # Continue checking the next alphabet to the left as long as the left alphabet is a VOWEL of transformation LEFT
        elif (labels[idx] == VOWEL and trans[idx] == LEFT):
          continue
        else:
          return False
      return False
    # If the alphabet at index pos is a CONSONANT
    elif labels[pos] == CONSONANT:
      # Iterate through the alphabets to the left of pos
      for idx in reversed(range(0,pos)):
        # Valid if a VOWEL of transformation SAME or LEFT_SAME is found
        if labels[idx] == VOWEL and (trans[idx] == SAME or trans[idx] == LEFT_SAME):
          return True
        # Continue checking the next alphabet to the left as long as the left alphabet is a CONSONANT of transformation LEFT
        elif labels[idx] == CONSONANT and trans[idx] == LEFT:
          continue
        else:
          return False
      return False

  # Check if a LEFT transformation is valid
  def valid_RIGHT_transform(self, labels, trans, pos):
    # If the alphabet at index pos is a VOWEL
    if labels[pos] == VOWEL:
      # Iterate through the alphabets to the right of pos
      for idx in range(pos+1,len(trans)):
        # Valid if a VOWEL of transformation SAME is found
        if labels[idx] == VOWEL and trans[idx] == SAME:
          return True
        # Continue checking the next alphabet to the right as long as the right alphabet is a VOWEL of transformation RIGHT
        elif (labels[idx] == VOWEL and trans[idx] == RIGHT):
          continue
        else:
          return False
      return False
    # If the alphabet at index pos is a CONSONANT
    elif labels[pos] == CONSONANT:
      # Iterate through the alphabets to the left of pos
      for idx in range(pos+1,len(trans)):
        # Valid if a VOWEL of transformation SAME is found
        if labels[idx] == VOWEL and trans[idx] == SAME:
          return True
        # Continue checking the next alphabet to the left as long as the right alphabet is a CONSONANT of transformation RIGHT
        elif labels[idx] == CONSONANT and trans[idx] == RIGHT:
          continue
        else:
          return False
      return False

  # Check if a LEFT_RIGHT transformation is valid
  def valid_LEFT_RIGHT_transform(self, labels, trans, pos):
    if self.valid_LEFT_transform(labels, trans, pos) and self.valid_RIGHT_transform(labels, trans, pos):
      return True
    else:
      return False

  # Get all the hypothesis with the lowest score
  def get_best_hyps(self, word, ref):
    labels = self.label_letter(word)

    trans = [None] * len(labels)
    all_trans_hyps = []
    all_word_hyps = []
    self.generate_transform_hyp(labels, trans, 0, all_trans_hyps, 0)

    for trans in all_trans_hyps:
      new_hyp = WordHypothesis()
      new_word = self.construct_syls(word, labels, trans)
      #print "Labels: [ %s ]" % " , ".join(labels)
      #print "Transformation: [ %s ]" % " , ".join(trans)
      #print "Word: %s\n" % str(new_word)

      new_hyp.original = word
      new_hyp.labels = labels
      new_hyp.transform = trans
      new_hyp.word = new_word
      new_hyp.encoded_struct = new_word.get_encoded_struct()

      (invalid_trans_pen, valid_trans_arr) = self.penalize_invalid_transform(new_hyp.labels, new_hyp.transform)
      new_hyp.invalid_trans_pen = invalid_trans_pen
      new_hyp.valid_trans_arr = valid_trans_arr

      new_hyp.acc_pen = self.levenshtein(new_hyp.encoded_struct, ref)
      new_hyp.mod_pen = self.levenshtein(new_hyp.word.to_plain_text(), new_hyp.original)

      all_word_hyps.append(new_hyp)

    #print "--------------------- BEST ACC SCORE HYPS -----------------------"
    # Score and retrieve all hypothesis with the best accuracy score
    word_hyps_sorted_by_acc = sorted(all_word_hyps, key=lambda hyp: hyp.acc_pen)
    min_pen = word_hyps_sorted_by_acc[0].acc_pen
    best_acc_score_hyps = []
    for hyp in word_hyps_sorted_by_acc:
      if hyp.acc_pen > min_pen:
        break
      else:
        best_acc_score_hyps.append(hyp)

    #for best_hyp in best_acc_score_hyps:
    #  best_hyp.print_str()

    print "--------------------- LOWEST INVALID TRANSFORMATION PENALTY -----------------------"
    # Score and retrieve hypothesis with the lowest invalid transformation penalty
    word_hyps_sorted_by_invalid_trans_pen = sorted(best_acc_score_hyps, key=lambda hyp: hyp.invalid_trans_pen)
    min_pen = word_hyps_sorted_by_invalid_trans_pen[0].invalid_trans_pen
    best_invalid_trans_score_hyps = []
    for hyp in word_hyps_sorted_by_invalid_trans_pen:
      if hyp.invalid_trans_pen > min_pen:
        break
      else:
        best_invalid_trans_score_hyps.append(hyp) 

    for best_hyp in best_invalid_trans_score_hyps:
      best_hyp.print_str()


    print "--------------------- LOWEST MODIFICATION PENALTY -----------------------"
    word_hyps_sorted_by_mod_pen = sorted(best_invalid_trans_score_hyps, key=lambda hyp: hyp.mod_pen)
    min_pen = word_hyps_sorted_by_mod_pen[0].mod_pen
    best_mod_pen_hyps = []
    for hyp in word_hyps_sorted_by_mod_pen:
      if hyp.mod_pen > min_pen:
        break
      else:
        best_mod_pen_hyps.append(hyp)

    for best_hyp in best_mod_pen_hyps:
      best_hyp.print_str()

    return best_mod_pen_hyps


  # Calculate Levenshtein (edit distance) between two string
  # This helper function is used to calculate the edit distance between a hypothesized syllable structure and
  # the reference syllabic structure
  # http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
  def levenshtein(self, s1, s2):
    if len(s1) < len(s2):
        return self.levenshtein(s2, s1)
 
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

#------------------------------------------ UNIT TESTS -------------------------------------

test_generator = SylStructGenerator(0.3)

# Unit test for letter labeling
def test_letters_labelling(word):
  print "Test letters labeling for: %s" % word
  test_generator.label_letter(word)
  for labels in all_labels:
    print labels

# Unit test for transformation generation of a word
def test_transform_generation(labels):
  print "Test transformation generation for: [ %s ]" % (" , ".join(labels))
  trans = [None] * len(labels)
  test_generator.generate_transform_hyp(labels, trans, 0)

# Unit test for constructing syllables
def test_syllable_construction(word, labels, trans):
  print "Test transformation generation for \n- Word: %s \n- With labels: [ %s ] \n- Transformation: [ %s ] " % (word, " , ".join(labels), " , ".join(moves))
  new_word = test_generator.construct_syls(word, labels, trans)
  print str(new_word)
  print new_word.get_encoded_struct()

# Unit test for invalid transformation
def test_invalid_transformation_penalty(labels, trans):
  (penalty, invalid_trans_arr) = test_generator.penalize_invalid_transform(labels, trans)
  print penalty
  print str(invalid_trans_arr)

# Unit test on getting the best hypothesis
def test_get_best_hyps(word, ref):
  best_word_hyps = test_generator.get_best_hyps(word, ref)
  for best_hyp in best_word_hyps:
    best_hyp.print_str()

#test_letters_labelling("palestine")
#test_transform_generation(["C", "V", "C", "V", "C", "C", "V", "C", "X"])
#test_syllable_construction("palestine", ["C", "V", "C", "V", "C", "C", "V", "C", "X"], ["R", "S", "R", "S", "LS", "R", "S", "L", "X"])
#test_syllable_construction("palestine", ["X", "X", "C", "V", "C", "C", "V", "C", "V"], [ "X" , "X" , "S" , "S" , "L" , "L" , "S" , "LR" , "S" ])
#generator = SylStructGenerator()
#test_all_steps("palestine")
#start_time = time.time()
#test_all_steps("palestine", "0 1 0 1 2 0 1 2")
#test_all_steps("palestine", "0 1 0 1 2 0 1 0 1 2")
#test_invalid_transformation_penalty(['C', 'V', 'C', 'V', 'C', 'C', 'V', 'C', 'V'], [ 'R' , 'S' , 'R' , 'S' , 'LS' , 'R' , 'S' , 'L' , 'X' ])
#test_get_best_hyps("palestine", "0 1 0 1 2 0 1 2")
#test_get_best_hyps("palestine", "0 1 0 1 2 0 1 0 1 2")
#test_get_best_hyps("fontainebleau", "0 1 2 0 1 2 0 1 0 1 0 1")
#print ("--- %s seconds ---" % str(time.time() - start_time))
#test_generator.get_best_hyps("lascaux", "0 1 2 0 1 0 1")
#test_generator.get_best_hyps("arguedas", "1 2 0 1 0 1 2")