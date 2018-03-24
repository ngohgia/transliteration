import copy

ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
GRAPHEME = "G"
PHONEME = "P"

class Coord:
  def __init__(self):
    self.coords = {}
    self.coords[ONSET] = {GRAPHEME: '#', PHONEME: '#'}
    self.coords[NUCLEUS] = {GRAPHEME: '#', PHONEME: '#'}
    self.coords[CODA] = {GRAPHEME: '#', PHONEME: '#'}
    self.vals = {ONSET: '#', NUCLEUS: '#', CODA: '#'}

  def encode_unit_to_coord(self, syl):
    for idx in range(len(syl.roles)):
      role = syl.roles[idx]
      grapheme = syl.en_graphemes[idx]
      phoneme = syl.en_phonemes[idx]
      if phoneme == "":
        phoneme = "_"

      self.coords[role][GRAPHEME] = grapheme
      self.coords[role][PHONEME] = phoneme

      self.vals[role] = syl.vie_phonemes[idx]

  def gp_str(self, gp):
    return "<" + gp[GRAPHEME] + ">/" + gp[PHONEME] + "/"

  def print_str(self):
    gp = self.coords
    print self.gp_str(gp[ONSET]) + " | " + self.gp_str(gp[NUCLEUS]) + " |  " + self.gp_str(gp[CODA]) \
    + " => " + self.vals[ONSET] + " | " + self.vals[NUCLEUS] + " | " + self.vals[CODA]

  def to_list(self):
    coords = self.coords
    vals = self.vals

    result = [coords[ONSET][GRAPHEME], coords[ONSET][PHONEME], \
      coords[NUCLEUS][GRAPHEME], coords[NUCLEUS][PHONEME], \
      coords[CODA][GRAPHEME], coords[CODA][PHONEME] , \
      vals[ONSET], vals[NUCLEUS], vals[CODA]]
    return result

  def list_to_coord(self, unit_list):
    new_coord = Coord()
    new_coord.coords[ONSET][GRAPHEME] = unit_list[0]
    new_coord.coords[ONSET][PHONEME] = unit_list[1]

    new_coord.coords[NUCLEUS][GRAPHEME] = unit_list[2]
    new_coord.coords[NUCLEUS][PHONEME] = unit_list[3]

    new_coord.coords[CODA][GRAPHEME] = unit_list[4]
    new_coord.coords[CODA][PHONEME] = unit_list[5]

    new_coord.vals[ONSET] = unit_list[6]
    new_coord.vals[NUCLEUS] = unit_list[7]
    new_coord.vals[CODA] = unit_list[8]

    return new_coord

  def extrapolate(self, unit_list, all_coords, pos):
    if pos > 5:
      return
    else:
      new_coord = self.list_to_coord(unit_list)
      completed_coords = self.assign_val_to_extrapolated_coord(new_coord)
      for coord in completed_coords:
        all_coords.append(coord)

      for i in range(pos, len(unit_list)):
        if unit_list[i] == "#": 
          self.extrapolate(unit_list[0:i] + ["_", "_"] + unit_list[i+2:len(unit_list)], all_coords, i+1)
        elif unit_list[i] != "_": 
          self.extrapolate(unit_list[0:i] + ["_"] + unit_list[i+1:len(unit_list)], all_coords, i+1)


  def assign_val_to_extrapolated_coord(self, coord):
    results = []
    vals = coord.vals
    coords = coord.coords

    for unit in vals:
      if vals[unit] != "#" and coords[unit][GRAPHEME] != "#" and coords[unit][PHONEME] != "#" \
      and (coords[unit][GRAPHEME] != "_" or coords[unit][PHONEME] != "_"):        
        new_vals = {ONSET: "#", NUCLEUS: "#", CODA: "#"}
        new_vals[unit] = vals[unit]

        new_coord = copy.deepcopy(coord)
        new_coord.vals = new_vals

        results.append(new_coord)

    return results

