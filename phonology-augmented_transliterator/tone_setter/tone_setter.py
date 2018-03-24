import os
import sys
import copy
import subprocess

from shared_res.Syllable import Syllable
from shared_res.Word import Word
from shared_res.Coord import Coord
from shared_res.SearchSpace import SearchSpace
from shared_res.SearchSpace import SearchPoint

from shared_res.LangAssets import LangAssets
ANY_UNIT  = LangAssets.ANY_UNIT
TERMINAL  = LangAssets.TERMINAL

ONSET     = LangAssets.ONSET
NUCLEUS   = LangAssets.NUCLEUS
CODA      = LangAssets.CODA

PREV_TONE = LangAssets.PREV_TONE
NEXT_TONE = LangAssets.NEXT_TONE

DEFAULT_TONE = LangAssets.DEFAULT_TONE


RANK_WEIGHT = 1.0

if __name__ == '__main__':
  try:
    script, train_dev_lex_name, toneless_vie_phones_with_roles_name, test_output_file_path = sys.argv
  except ValueError:
    print "Syntax: tone_setter.py      train_dev_lex_name      toneless_vie_phones_with_roles"
    sys.exit(1)

def read_train_dev_lex_file(train_dev_lex_path):
  train_dev_lex_file = open(train_dev_lex_path, "r")

  all_words = []
  for line in train_dev_lex_file:
    [en_syls_str, roles_str, vie_syls_str] = line.split("\t")[2:5]

    vie_syls = [[unit.strip() for unit in vie_syl.split(" ")[0:len(vie_syl.split(" "))]] for vie_syl in vie_syls_str.split(" . ")]
    roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
    tones = [(vie_syl.strip().split(" ")[-1])[-1] for vie_syl in vie_syls_str.split(" . ")]
    
    new_word = Word()
    for idx in range(len(vie_syls)):
      new_syl = Syllable()
      new_syl.create_new_syl(vie_syls[idx], roles[idx], tones[idx])
      new_word.add_new_syl(new_syl)

    all_words.append(new_word)

  return all_words
  train_dev_lex_file.close()


def read_toneless_vie_phones_with_roles_file(toneless_vie_phones_with_roles_path):
  toneless_vie_phones_with_roles_file = open(toneless_vie_phones_with_roles_path, "r")

  all_words = []
  for line in toneless_vie_phones_with_roles_file:
    [vie_syls_str, roles_str] = line.split("\t")

    vie_syls = [[unit.strip() for unit in vie_syl.split(" ")] for vie_syl in vie_syls_str.split(" . ")]
    roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
    
    new_word = Word()
    for idx in range(len(vie_syls)):
      new_syl = Syllable()
      new_syl.create_new_syl(vie_syls[idx], roles[idx], 1)
      new_word.add_new_syl(new_syl)

    all_words.append(new_word)

  return all_words
  toneless_vie_phones_with_roles_file.close()

def get_best_word(word, possible_tones, max_tone_score, syl_idx, best_word, searchspace):
  if syl_idx >= len(word.syls):
    tone_score = score_tone_assignment(word, searchspace)
    
    # word.print_str()
    # print tone_score
    
    if tone_score > max_tone_score[0]:
      best_word[0] = copy.deepcopy(word)
      max_tone_score[0] = tone_score
  else:
    for tone in possible_tones[syl_idx]:
      word.syls[syl_idx].tone = tone
      get_best_word(word, possible_tones, max_tone_score, syl_idx +1, best_word, searchspace)

def score_tone_assignment(word, searchspace):
  word_score = 1.0

  for idx in range(len(word.syls)):
    syl = word.syls[idx]

    rank_sum = 1.0
    syl_score = 0.0

    prev_tone = TERMINAL
    if idx > 0:
      prev_tone = word.syls[idx-1].tone

    next_tone = TERMINAL
    if idx < len(word.syls) - 1:
      next_tone = word.syls[idx+1].tone

    new_coord = Coord()
    new_coord.encode_syl_to_coord(syl, prev_tone, next_tone)
    extrapolated_coords_with_ranks = new_coord.extrapolate()
    
    for ranked_coord in extrapolated_coords_with_ranks:
      coord = ranked_coord[0]
      rank = ranked_coord[-1]

      search_point = SearchPoint()
      search_point.import_from_coord(coord)

      if search_point.coord in searchspace.space and search_point.val in searchspace.space[search_point.coord]:
        syl_score = syl_score + searchspace.space[search_point.coord][search_point.val]/(RANK_WEIGHT * rank)
        rank_sum = rank_sum + RANK_WEIGHT * rank

    syl_score = syl_score / rank_sum
    word_score = word_score * syl_score

  return word_score


# GET TRAINING DEV DATA
train_dev_lex_path = os.path.abspath(train_dev_lex_name)
train_dev_searchspace_path = train_dev_lex_path + ".tones.searchspace"

all_train_dev_words = read_train_dev_lex_file(train_dev_lex_name)

searchspace = SearchSpace()
for word in all_train_dev_words:
  for idx in range(len(word.syls)):
    syl = word.syls[idx]

    prev_tone = TERMINAL
    if idx > 0:
      prev_tone = word.syls[idx-1].tone

    next_tone = TERMINAL
    if idx < len(word.syls) - 1:
      next_tone = word.syls[idx+1].tone

    new_coord = Coord()
    new_coord.encode_syl_to_coord(syl, prev_tone, next_tone)
    extrapolated_coords_with_ranks = new_coord.extrapolate()
    extrapolated_coords = [coord_with_rank[0] for coord_with_rank in extrapolated_coords_with_ranks]
    
    for coord in extrapolated_coords:
      searchspace.add_new_search_point(coord)

# NORMALIZE THE SEARCH SPACE
searchspace.normalize()

# GET TEST DATA
toneless_vie_phones_with_roles_path = os.path.abspath(toneless_vie_phones_with_roles_name)
test_output_file_root = ".".join(toneless_vie_phones_with_roles_path.split(".")[0:-2])
local_output_path = test_output_file_root + ".output"

all_test_words = read_toneless_vie_phones_with_roles_file(toneless_vie_phones_with_roles_path)

result_words = []
for word in all_test_words:
  possible_tones = []

  for idx in range(len(word.syls)):
    syl = word.syls[idx]
    
    prev_tone = TERMINAL
    if idx > 0:
      prev_tone = word.syls[idx-1].tone

    next_tone = TERMINAL
    if idx < len(word.syls) - 1:
      next_tone = word.syls[idx+1].tone

    tmp_coord = Coord()
    tmp_coord.encode_syl_to_coord(syl, prev_tone, next_tone)

    tmp_coord.coord[ONSET] = ANY_UNIT
    tmp_coord.coord[CODA] = ANY_UNIT
    tmp_coord.coord[PREV_TONE] = ANY_UNIT
    tmp_coord.coord[NEXT_TONE] = ANY_UNIT

    search_point = SearchPoint()
    search_point.import_from_coord(tmp_coord)

    if search_point.coord in searchspace.space:
      possible_tones.append(searchspace.space[search_point.coord].keys())
    else:
      possible_tones.append([DEFAULT_TONE])

  best_word = [Word()]
  get_best_word(word, possible_tones, [0.0], 0, best_word, searchspace)

  best_word = best_word[0]
  result_words.append(best_word)


test_output_file = open(test_output_file_path, "w")
for word in result_words:
  test_output_file.write(" . ".join([str(syl) for syl in word.syls]) + "\n")
test_output_file.close()

local_test_output_file = open(local_output_path, "w")
for word in result_words:
  local_test_output_file.write(" . ".join([str(syl) for syl in word.syls]) + "\n")
test_output_file.close()


train_dev_searchspace_file = open(train_dev_searchspace_path, "w");
train_dev_searchspace_file.write(str(searchspace))
