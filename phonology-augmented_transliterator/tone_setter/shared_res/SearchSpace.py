from Coord import Coord
from shared_res.LangAssets import LangAssets

ANY_UNIT  = LangAssets.ANY_UNIT
TERMINAL  = LangAssets.TERMINAL

ONSET     = LangAssets.ONSET
NUCLEUS   = LangAssets.NUCLEUS
CODA      = LangAssets.CODA

PREV_TONE = LangAssets.PREV_TONE
NEXT_TONE = LangAssets.NEXT_TONE

class SearchPoint:
  def __init__(self):
    self.coord = ""
    self.val = ""

  def import_from_coord(self, search_coord):
    coord = search_coord.coord

    self.coord = str(coord[PREV_TONE]) + "," + coord[ONSET] + "|" + coord[NUCLEUS] + "|" + coord[CODA] + "," + str(coord[NEXT_TONE])
    self.val = search_coord.val

  def __str__(self):
    return self.coord + " => " + self.val


class SearchSpace:
  def __init__(self):
    self.space = {}

  def add_new_search_point(self, coord):
    new_search_point = SearchPoint()
    new_search_point.import_from_coord(coord)
    # print str(new_search_point)

    if new_search_point.coord not in self.space:
      self.space[new_search_point.coord] = {new_search_point.val: 1}
    else:
      if new_search_point.val not in self.space[new_search_point.coord]:
        self.space[new_search_point.coord][new_search_point.val] = 1
      else:
        self.space[new_search_point.coord][new_search_point.val] = self.space[new_search_point.coord][new_search_point.val] + 1

  def __str__(self):
    text = ""
    for coord in self.space:
      result = coord + " => "
      for phoneme in self.space[coord]:
        result = result + phoneme
        result = result + " " + str(self.space[coord][phoneme]) + ", "
      result = result[0:-2]
      text = text + result + "\n"
    
    return text

  def normalize(self):
    for coord in self.space:
      normalizer = sum(self.space[coord].values())

      for tone in self.space[coord]:
        self.space[coord][tone] = 1.0 * self.space[coord][tone] / normalizer
