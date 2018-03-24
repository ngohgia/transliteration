from Coord import Coord

ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
GRAPHEME = "G"
PHONEME = "P"

class SearchPoint:
  def __init__(self):
    self.coord = ""
    self.val = ""

  def import_from_search_pt(self, coord):
    coords = coord.coords
    vals = coord.vals

    if vals[ONSET] != "#":
      self.coord = "<" + coords[ONSET][GRAPHEME] + ">/" + coords[ONSET][PHONEME] + "/" \
      + "|" + "<" + coords[NUCLEUS][GRAPHEME] + ">/" + coords[NUCLEUS][PHONEME] + "/" \
      + "," + "<" + coords[CODA][GRAPHEME] + ">/" + coords[CODA][PHONEME] + "/"
      self.val = vals[ONSET]

    elif vals[NUCLEUS] != "#":
      self.coord = "<" + coords[ONSET][GRAPHEME] + ">/" + coords[ONSET][PHONEME] + "/" \
      + "|" + "<" + coords[NUCLEUS][GRAPHEME] + ">/" + coords[NUCLEUS][PHONEME] + "/" \
      + "|" + "<" + coords[CODA][GRAPHEME] + ">/" + coords[CODA][PHONEME] + "/"
      self.val = vals[NUCLEUS]

    elif vals[CODA] != "#":
      self.coord = "<" + coords[ONSET][GRAPHEME] + ">/" + coords[ONSET][PHONEME] + "/" \
      + "," + "<" + coords[NUCLEUS][GRAPHEME] + ">/" + coords[NUCLEUS][PHONEME] + "/" \
      + "|" + "<" + coords[CODA][GRAPHEME] + ">/" + coords[CODA][PHONEME] + "/"
      self.val = vals[CODA]

  def __str__(self):
    return self.coord + " => " + self.val


class SearchSpace:
  def __init__(self):
    self.space = {}

  def add_new_search_point(self, coord):
    new_search_point = SearchPoint()
    new_search_point.import_from_search_pt(coord)
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

      for phoneme in self.space[coord]:
        self.space[coord][phoneme] = 1.0 * self.space[coord][phoneme] / normalizer
    