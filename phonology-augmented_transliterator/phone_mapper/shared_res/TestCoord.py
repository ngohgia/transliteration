import copy
from LangAssets import LangAssets

ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
GRAPHEME = "G"
PHONEME = "P"
GENERIC_VOWEL = "@"

CLOSER_UNKNOWN_PHONEME_PEN = LangAssets.CLOSER_UNKNOWN_PHONEME_PEN
CLOSER_UNKNOWN_GRAPHEME_PEN = LangAssets.CLOSER_UNKNOWN_GRAPHEME_PEN

FARTHER_UNKNOWN_PHONEME_PEN = LangAssets.FARTHER_UNKNOWN_PHONEME_PEN
FARTHER_UNKNOWN_GRAPHEME_PEN = LangAssets.FARTHER_UNKNOWN_GRAPHEME_PEN

MAIN_UNKNOWN_PHONEME_PEN = LangAssets.MAIN_UNKNOWN_PHONEME_PEN
MAIN_UNKNOWN_GRAPHEME_PEN = LangAssets.MAIN_UNKNOWN_GRAPHEME_PEN

class TestCoord:
  def __init__(self):
    self.units = { ONSET: {GRAPHEME: "#", PHONEME: "#"} ,
                  NUCLEUS: {GRAPHEME: "#", PHONEME: "#"},
                  CODA: {GRAPHEME: "#", PHONEME: "#"} }
    self.tags = { ONSET: 0, NUCLEUS: 0, CODA: 0}

  def create_from_syl(self, syl):
    for idx in range(len(syl.roles)):
      role = syl.roles[idx]
      self.units[role][GRAPHEME] = syl.en_graphemes[idx]
      if syl.en_phonemes[idx] != "":
        self.units[role][PHONEME] = syl.en_phonemes[idx]
      else:self.units[role][PHONEME] = "_"


  def print_str(self):
    print "<" + self.units[ONSET][GRAPHEME] + "> /" + self.units[ONSET][PHONEME] + "/ |" \
          + "<" + self.units[NUCLEUS][GRAPHEME] + "> /" + self.units[NUCLEUS][PHONEME] + "/ |" \
          + "<" + self.units[CODA][GRAPHEME] + "> /" + self.units[CODA][PHONEME] + "/ |" \
          + ": " + str(self.tags[ONSET]) + ", " + str(self.tags[NUCLEUS]) + ", " + str(self.tags[CODA])

  def to_list(self):
    units = self.units
    tags = self.tags

    result = [units[ONSET][GRAPHEME], units[ONSET][PHONEME], \
      units[NUCLEUS][GRAPHEME], units[NUCLEUS][PHONEME], \
      units[CODA][GRAPHEME], units[CODA][PHONEME], \
      tags[ONSET], tags[NUCLEUS], tags[CODA]]
    return result

  def get_tagged_coords(self):
    all_tagged_coords = []
    for unit in self.tags:
      new_coord = copy.deepcopy(self)
      if new_coord.units[unit][GRAPHEME] != "#":
        new_coord.tags[unit] = 1
        all_tagged_coords.append(new_coord)
    return all_tagged_coords

  def extrapolate_and_rank(self):
    unit_list = self.to_list()
    all_unranked_coords = []
    self.extrapolate(unit_list, all_unranked_coords, 0)
    
    all_ranked_coords = []
    for coord in all_unranked_coords:
      all_ranked_coords.append([coord, coord.rank_coord()])
    return all_ranked_coords

  def rank_coord(self):
    rank = 1.0
    targ = ""

    for unit in self.tags:
      if self.tags[unit] == 1:
        targ = unit
        break

    if unit == NUCLEUS:
      if self.units[NUCLEUS][PHONEME] == "_":
        rank = rank + MAIN_UNKNOWN_PHONEME_PEN
      if self.units[NUCLEUS][GRAPHEME] == "_":
        rank = rank + MAIN_UNKNOWN_GRAPHEME_PEN

      if self.units[ONSET][GRAPHEME] == "_":
        rank = rank + CLOSER_UNKNOWN_GRAPHEME_PEN
      if self.units[ONSET][PHONEME] == "_":
        rank = rank + CLOSER_UNKNOWN_PHONEME_PEN

      if self.units[CODA][GRAPHEME] == "_":
        rank = rank + CLOSER_UNKNOWN_GRAPHEME_PEN
      if self.units[CODA][PHONEME] == "_":
        rank = rank + CLOSER_UNKNOWN_PHONEME_PEN
    elif unit == ONSET:
      if self.units[ONSET][PHONEME] == "_":
        rank = rank + MAIN_UNKNOWN_PHONEME_PEN
      if self.units[ONSET][GRAPHEME] == "_":
        rank = rank + MAIN_UNKNOWN_GRAPHEME_PEN

      if self.units[NUCLEUS][GRAPHEME] == "_":
        rank = rank + CLOSER_UNKNOWN_GRAPHEME_PEN
      if self.units[NUCLEUS][PHONEME] == "_":
        rank = rank + CLOSER_UNKNOWN_PHONEME_PEN

      if self.units[CODA][GRAPHEME] == "_":
        rank = rank + FARTHER_UNKNOWN_GRAPHEME_PEN
      if self.units[CODA][PHONEME] == "_":
        rank = rank + FARTHER_UNKNOWN_PHONEME_PEN
    elif unit == CODA:
      if self.units[CODA][PHONEME] == "_":
        rank = rank + MAIN_UNKNOWN_PHONEME_PEN
      if self.units[CODA][GRAPHEME] == "_":
        rank = rank + MAIN_UNKNOWN_GRAPHEME_PEN\

      if self.units[NUCLEUS][GRAPHEME] == "_":
        rank = rank + CLOSER_UNKNOWN_GRAPHEME_PEN
      if self.units[NUCLEUS][PHONEME] == "_":
        rank = rank + CLOSER_UNKNOWN_PHONEME_PEN

      if self.units[ONSET][GRAPHEME] == "_":
        rank = rank + FARTHER_UNKNOWN_GRAPHEME_PEN
      if self.units[ONSET][PHONEME] == "_":
        rank = rank + FARTHER_UNKNOWN_PHONEME_PEN

    return rank



  def extrapolate(self, unit_list, all_coords, pos):
    if pos > 6:
      return
    else:
      new_coord = self.list_to_coord(unit_list)
      all_coords.append(new_coord)

      for i in range(pos, len(unit_list)):
        if unit_list[i] == "#" and unit_list[i-1] != "#": 
          self.extrapolate(unit_list[0:i] + ["_", "_"] + unit_list[i+2:len(unit_list)], all_coords, i+1)
        elif unit_list[i] != "_": 
          self.extrapolate(unit_list[0:i] + ["_"] + unit_list[i+1:len(unit_list)], all_coords, i+1)

  def list_to_coord(self, unit_list):
    new_coord = TestCoord()
    new_coord.units[ONSET][GRAPHEME] = unit_list[0]
    new_coord.units[ONSET][PHONEME] = unit_list[1]

    new_coord.units[NUCLEUS][GRAPHEME] = unit_list[2]
    new_coord.units[NUCLEUS][PHONEME] = unit_list[3]

    new_coord.units[CODA][GRAPHEME] = unit_list[4]
    new_coord.units[CODA][PHONEME] = unit_list[5]

    new_coord.tags[ONSET] = unit_list[6]
    new_coord.tags[NUCLEUS] = unit_list[7]
    new_coord.tags[CODA] = unit_list[8]

    return new_coord

  def form_search_pt(self):
    search_pt = ""
    for unit in self.tags:
      if self.tags[unit] == 1:
        units = self.units
        if units[unit][GRAPHEME] != "_" or units[unit][PHONEME] != "_":
          if unit == ONSET:
            search_pt = "<" + units[ONSET][GRAPHEME] + ">/" + units[ONSET][PHONEME] + "/" \
            + "|" + "<" + units[NUCLEUS][GRAPHEME] + ">/" + units[NUCLEUS][PHONEME] + "/" \
            + "," + "<" + units[CODA][GRAPHEME] + ">/" + units[CODA][PHONEME] + "/"

          elif unit == NUCLEUS:
            search_pt = "<" + units[ONSET][GRAPHEME] + ">/" + units[ONSET][PHONEME] + "/" \
            + "|" + "<" + units[NUCLEUS][GRAPHEME] + ">/" + units[NUCLEUS][PHONEME] + "/" \
            + "|" + "<" + units[CODA][GRAPHEME] + ">/" + units[CODA][PHONEME] + "/"

          elif unit == CODA:
            search_pt = "<" + units[ONSET][GRAPHEME] + ">/" + units[ONSET][PHONEME] + "/" \
            + "," + "<" + units[NUCLEUS][GRAPHEME] + ">/" + units[NUCLEUS][PHONEME] + "/" \
            + "|" + "<" + units[CODA][GRAPHEME] + ">/" + units[CODA][PHONEME] + "/"
        break
    return search_pt

# test_coord = TestCoord()
# test_coord.units = { ONSET: {GRAPHEME: "c", PHONEME: "K"} ,
#                   NUCLEUS: {GRAPHEME: "o", PHONEME: "AA"},
#                   CODA: {GRAPHEME: "p", PHONEME: "PD"} }
# test_coord.tags = { ONSET: 0, NUCLEUS: 0, CODA: 1}
# all_ranked_coords = test_coord.extrapolate_and_rank()
# for i in range(len(all_ranked_coords)-1):
#   for j in range(i+1, len(all_ranked_coords)):
#     if all_ranked_coords[i][1] > all_ranked_coords[j][1]:
#       tmp = all_ranked_coords[i]
#       all_ranked_coords[i] = all_ranked_coords[j]
#       all_ranked_coords[j] = tmp

# for tmp in all_ranked_coords:
#   [coord, rank] = tmp
#   coord.print_str()
#   print str(rank) + "\n"
