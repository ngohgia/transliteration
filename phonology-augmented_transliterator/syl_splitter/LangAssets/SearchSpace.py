import sys
import os
import copy
import math

# Search Space of a given corpus
# Each coordinate in the Search Space is defined by a tuples of (prev, curr, next)
# The value at each coordinate is a dictinary in which each key is a role
# and the corresponding value is the frequency of that role being assigned to
# the current letter, given the preceding and following letter

from LangAssets import LangAssets
from Rule import Rule
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from syl_struct_generator.SylStructGenerator_improved import label_letters

SEARCH_LVL_WEIGHT = 2
N_GRAM_WEIGHT = 3
GRAM_BAL_WEIGHT = 2

# Labels
CONSONANT = LangAssets.CONSONANT
VOWEL = LangAssets.VOWEL
DELIMITER = LangAssets.DELIMITER
ANY  = LangAssets.ANY
N_GRAM_LEN = LangAssets.N_GRAM_LEN

lang_assets = LangAssets()
ValidEnConsos = lang_assets.valid_en_consos
ValidEnVowels = lang_assets.valid_en_vowels

class SearchCoord:
  def __init__(self):
    self.coord = Rule()
    self.search_lvl = 1

  def extrapolate_rule_with_labels(self):
    extrapolated_rules = []
    rule = self.coord

    for prev_conv_range in range(0,len(rule.prev)+1):
      for next_conv_range in range(0,len(rule.next)+1):
        rule_tmp = copy.deepcopy(rule)
        new_search_coord = SearchCoord()
        if prev_conv_range > 0:
          for i in range(prev_conv_range):
            if rule_tmp.prev[i] != DELIMITER:
              rule_tmp.prev[i] = map_letter_to_label(rule_tmp.prev[i])

        if next_conv_range > 0:
          for j in reversed(range(len(rule_tmp.next)-next_conv_range, len(rule_tmp.next))):
            if rule_tmp.next[j] != DELIMITER:
              rule_tmp.next[j] = map_letter_to_label(rule_tmp.next[j])
        new_search_coord.coord = rule_tmp
        extrapolated_rules.append(new_search_coord)
    return extrapolated_rules

  def further_extrapolate_rule(self):
    extrapolated_rules = []
    rule = self.coord
    
    for prev_conv_range in range(0, len(rule.prev)+1):
      for next_conv_range in range(0, len(rule.next)+1):
        new_search_coord = SearchCoord()

        rule_tmp = copy.deepcopy(rule)
        if prev_conv_range < len(rule.prev):
          rule_tmp.prev = rule_tmp.prev[prev_conv_range:len(rule_tmp.prev)]
        else:
          rule_tmp.prev = []

        if next_conv_range < len(rule.next):
          rule_tmp.next = rule_tmp.next[0:len(rule_tmp.next) - next_conv_range]
        else:
          rule_tmp.next = []

        new_search_coord.coord = rule_tmp
        extrapolated_rules.append(new_search_coord)
    return extrapolated_rules

  def further_further_extrapolate_rule(self):
    rule_tmp = copy.deepcopy(self.coord)
    rule_tmp.curr = [map_letter_to_label(rule_tmp.curr[0])]
    new_search_coord = SearchCoord()
    new_search_coord.coord = rule_tmp
    new_search_coord.search_lvl = self.search_lvl + 2
    return new_search_coord

  def get_gram_len(self):
    coord = self.coord
    tok_list = coord.prev + coord.curr + coord.next
    gram_len = 0
    for tok in tok_list:
      if tok != CONSONANT and tok != VOWEL:
        gram_len = gram_len + 1
    if coord.curr[0] == CONSONANT or coord.curr[0] == VOWEL:
      gram_len = 0
    return gram_len

  def get_gram_balance(self):
    coord = self.coord
    left_gram = 0
    right_gram = 0
    for tok in reversed(coord.prev):
      if tok == CONSONANT or tok == VOWEL:
        break
      left_gram = left_gram + 1
    for tok in coord.next:
      if tok == CONSONANT or tok == VOWEL:
        break
      right_gram = right_gram + 1
    return math.fabs(left_gram - right_gram)

  def compute_search_lvl(self):
    gram_len = self.get_gram_len()
    gram_balance = self.get_gram_balance()
    if gram_len > 0:
      # self.search_lvl = math.factorial(N_GRAM_LEN) / math.factorial(gram_len) / math.factorial(N_GRAM_LEN - gram_len) * int(math.pow(2, N_GRAM_LEN-gram_len))
      self.search_lvl = (N_GRAM_LEN-gram_len) * int(math.pow(N_GRAM_WEIGHT, N_GRAM_LEN-gram_len)) + int(math.pow(GRAM_BAL_WEIGHT, gram_balance))

      coord = self.coord
      for tok in coord.prev:
        if tok == CONSONANT or tok == VOWEL:
          self.search_lvl = self.search_lvl - 1
      for tok in coord.next:
        if tok == CONSONANT or tok == VOWEL:
          self.search_lvl = self.search_lvl - 1
    else:
      #self.search_lvl = math.factorial(N_GRAM_LEN-1) * int(math.pow(2, N_GRAM_LEN-1))
      self.search_lvl = (N_GRAM_LEN-gram_len) * int(math.pow(N_GRAM_WEIGHT, N_GRAM_LEN)) + int(math.pow(GRAM_BAL_WEIGHT, gram_balance))

      coord = self.coord
      for tok in coord.prev:
        if tok != CONSONANT and tok != VOWEL:
          self.search_lvl = self.search_lvl - 1
      for tok in coord.next:
        if tok != CONSONANT and tok != VOWEL:
          self.search_lvl = self.search_lvl - 1

    

  def __eq__(self, other):
    if isinstance(other, SearchCoord):
      if self.coord == other.coord:
        return True
      else:
        return False
    return NotImplemented

  def __ne__(self, other):
    result = self.__eq__(other)
    if result is NotImplemented:
        return result
    return not result

  def to_str(self):
    return self.coord.to_str() + " | " + str(self.search_lvl)

# Map a letter to its label
def map_letter_to_label(letter):
  if letter in ValidEnVowels:
    return VOWEL
  elif letter in ValidEnConsos:
    return CONSONANT
  else:
    print "Letter %s cannot be mapped to a label" % letter
    sys.exit(1)

  

class SearchSpace:
  def __init__(self):
    self.space = {}

  def add_rule(self, rule):
    # tuple defining the coordinates in the search space
    coord = (",".join(rule.prev), rule.curr[0], ",".join(rule.next))
    role = rule.role[0]

    # If there is no coordinate matching the tuple, add a new one
    if coord not in self.space:
      self.space[coord] = {}
      # Initialize value of a role assigned to the coord
      self.space[coord][role] = 1
    # If there is a coordinate maching the tuple, 
    # update the frequency of the corresponding role
    else:
      if role not in self.space[coord]:
        self.space[coord][role] = 1
      else:
        self.space[coord][role] = self.space[coord][role] + 1

  def to_str(self):
    text = ""
    text = text + "\nSeach Space:\n"

    for coord in self.space:
      text = text + "|".join(coord) + " => " + str(self.space[coord]) + "\n"

    return text

  def normalized(self):
    for coord in self.space:
      roles = self.space[coord]

      total = 0
      for role in roles:
        total = total + self.space[coord][role]

      for role in roles:
        self.space[coord][role] = self.space[coord][role] * 1.0 / total
        #print self.space[coord][role]

  # Given a set of tokens [prev, curr, next] and the role of interest in the form
  # of a rule object,
  # return the probabilty for that role, assigned to the coordinate
  # in the search space that matches most closely to the given set of tokens
  def get_best_matched_coord_prob(self, coord):
    all_coords = []

    # Generate all possible tokens
    all_coords = self.create_all_possible_toks(coord)

    combined_prob = 0.0

    # all_toks = self.score_toks_lvl(all_toks)

    # if coord.coord.curr[0] == "e":
    #   print "Search coord: " + str(coord.coord.curr[0])
    #   print "Role" + coord.coord.role[0]

    search_lvl_sum = 0.0;
    for coord in all_coords:
      search_coord = coord.coord
      search_tuple = (",".join(search_coord.prev), search_coord.curr[0], ",".join(search_coord.next))
      # print "search_coord: " + str(search_tuple)
      
      if search_tuple in self.space:
        role = search_coord.role[0]
        # print "search_coord: " + search_coord.to_str()
        # print "roles: " + str(self.space[search_tuple])
        
        if role in self.space[search_tuple]:
          # print coord.to_str()
          # if coord.coord.curr[0] == "e":
          #   print coord.to_str()
          #   print "Role: " + role
          #   print "prob: " + str(self.space[search_tuple][role])
          #print str(combined_prob)
          combined_prob = combined_prob + 1.0/(SEARCH_LVL_WEIGHT * coord.search_lvl) * self.space[search_tuple][role]
          search_lvl_sum = search_lvl_sum + 1.0/(SEARCH_LVL_WEIGHT * coord.search_lvl)

    # print "role: " + str(role)
    # print str(best_matched_coord)
    # print str(highest_prob)
    if search_lvl_sum > 0:
      combined_prob = combined_prob / search_lvl_sum
    else:
      combined_prob = 0.0
    # print "COMBINED PROB: " + str(combined_prob)

    return combined_prob


  # For the given coordinate, return the list of roles with 
  # with the highest frequency
  def get_best_roles(self, coord):
    max_freq = 0
    best_roles = []
    for role in self.space[coord]:
      if self.space[coord][role] > max_freq:
        max_freq = self.space[coord][role]
        best_roles = [role]
      elif self.space[coord][role] == max_freq:
        best_roles.append(role)
        
    return best_roles

  def score_toks_lvl(self, all_toks):
    valid_toks = []
    for idx in range(len(all_toks)):
      if all_toks[idx][1] != ANY:
        if all_toks[idx][0] == ANY:
          all_toks[idx][-1] = all_toks[idx][-1] + 10
        if all_toks[idx][2] == ANY:
          all_toks[idx][-1] = all_toks[idx][-1] + 10
        if all_toks[idx][1] == CONSONANT or all_toks[idx][1] == VOWEL:
          all_toks[idx][-1] = all_toks[idx][-1] + 50

        valid_toks.append(all_toks[idx])
    return valid_toks

  # Given the tokens of a coordinate [prev, curr, next]
  # generate all possible sets of tokens
  def create_all_possible_toks(self, coord):
    all_coords = []
    all_coords.append(coord)

    all_coords_tmp = []
    all_coords_tmp.append(coord)

    extrapolated_coords = coord.extrapolate_rule_with_labels()
    for new_coord in extrapolated_coords:
      if new_coord not in all_coords:
        all_coords_tmp.append(new_coord)
        all_coords.append(new_coord)

    for coord in all_coords_tmp:
      further_extrapolated_rules = coord.further_extrapolate_rule()
      for new_coord in further_extrapolated_rules:
        if new_coord not in all_coords:
          all_coords.append(new_coord)

    all_coords_tmp = copy.deepcopy(all_coords)
    for coord in all_coords_tmp:
      new_coord = coord.further_further_extrapolate_rule()
      if new_coord not in all_coords:
        all_coords.append(new_coord)

    tmp = []
    for coord in all_coords:
      if coord not in tmp:
        coord.compute_search_lvl()
        tmp.append(coord)
      
    return tmp

# new_search_space = SearchSpace()
# new_coord = SearchCoord()
# new_coord.coord.prev = ['a', 's']
# new_coord.coord.curr = ['t']
# new_coord.coord.next = ['a', 'u']
# new_coord.coord.role = ['O']

# all_coords = new_search_space.create_all_possible_toks(new_coord)
# for i in range(len(all_coords)-1):
#   for j in range(i+1, len(all_coords)):
#     if all_coords[i].search_lvl > all_coords[j].search_lvl:
#       tmp = all_coords[i]
#       all_coords[i] = all_coords[j]
#       all_coords[j] = tmp

# for coord in all_coords:
#   print coord.to_str()
#   gram_len = coord.get_gram_len()
#   gram_balance = coord.get_gram_balance()
  
  # print gram_len
  # print gram_balance
  # if gram_len > 0:
  #   print math.factorial(N_GRAM_LEN) / math.factorial(gram_len) / math.factorial(N_GRAM_LEN - gram_len)
  #   print int(math.pow(3, N_GRAM_LEN-gram_len))
  #   print int(math.pow(3, gram_balance))
  # else:
  #   print math.factorial(N_GRAM_LEN-1)
  #   print int(math.pow(3, N_GRAM_LEN-1))
  #   print int(math.pow(3, gram_balance))