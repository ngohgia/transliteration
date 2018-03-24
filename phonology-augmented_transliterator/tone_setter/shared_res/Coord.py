import copy

from shared_res.LangAssets import LangAssets

ANY_UNIT  = LangAssets.ANY_UNIT
TERMINAL  = LangAssets.TERMINAL

ONSET     = LangAssets.ONSET
NUCLEUS   = LangAssets.NUCLEUS
CODA      = LangAssets.CODA

PREV_TONE = LangAssets.PREV_TONE
NEXT_TONE = LangAssets.NEXT_TONE


class Coord:
  def __init__(self):
    self.coord = {}
    self.coord[ONSET] = TERMINAL
    self.coord[NUCLEUS] = TERMINAL
    self.coord[CODA] = TERMINAL
    self.coord[PREV_TONE] = ANY_UNIT
    self.coord[NEXT_TONE] = ANY_UNIT
    self.val = 1

  def __eq__(self, other):
    if isinstance(other, Coord):
      self_coord = self.coord
      other_coord = other.coord
      if self_coords[ONSET] == other_coord[ONSET] and self_coords[NUCLEUS] == other_coord[NUCLEUS] and self_coords[CODA] == other_coord[CODA] and self_coords[PREV_TONE] == other_coord[PREV_TONE] and self_coords[NEXT_TONE] == other_coord[NEXT_TONE]:
        return True
      else:
        return False
    return NotImplemented

  def __ne__(self, other):
    result = self.__eq__(other)
    if result is NotImplemented:
        return result
    return not result

  def encode_syl_to_coord(self, syl, prev_tone, next_tone):
    for idx in range(len(syl.roles)):
      role = syl.roles[idx]
      vie_phoneme = syl.vie_phonemes[idx]
      
      self.coord[role] = vie_phoneme
      self.coord[PREV_TONE] = prev_tone
      self.coord[NEXT_TONE] = next_tone
      self.val = syl.tone

  def print_str(self):
    print self.coord[ONSET] + " | " + self.coord[NUCLEUS] + " |  " + self.coord[CODA] \
    + " => " + str(self.val)

  def extrapolate(self):
    extrapolated_coords = [[self, 1]]

    prev_tone_less = copy.deepcopy(self)
    prev_tone_less.coord[PREV_TONE] = ANY_UNIT
    extrapolated_coords.append([prev_tone_less, 2])

    next_tone_less = copy.deepcopy(self)
    next_tone_less.coord[NEXT_TONE] = ANY_UNIT
    extrapolated_coords.append([next_tone_less, 2])

    tone_less = copy.deepcopy(self)
    tone_less.coord[NEXT_TONE] = ANY_UNIT
    tone_less.coord[PREV_TONE] = ANY_UNIT
    extrapolated_coords.append([tone_less, 3])

    onset_less = copy.deepcopy(self)
    onset_less.coord[NEXT_TONE] = ANY_UNIT
    onset_less.coord[PREV_TONE] = ANY_UNIT
    onset_less.coord[ONSET] = ANY_UNIT
    extrapolated_coords.append([onset_less, 5])

    nucleus_less = copy.deepcopy(self)
    nucleus_less.coord[NEXT_TONE] = ANY_UNIT
    nucleus_less.coord[PREV_TONE] = ANY_UNIT
    nucleus_less.coord[NUCLEUS] = ANY_UNIT
    extrapolated_coords.append([onset_less, 10])
    
    coda_less = copy.deepcopy(self)
    coda_less.coord[NEXT_TONE] = ANY_UNIT
    coda_less.coord[PREV_TONE] = ANY_UNIT
    coda_less.coord[CODA] = ANY_UNIT
    extrapolated_coords.append([coda_less, 20])

    single_nucleus = copy.deepcopy(self)
    single_nucleus.coord[NEXT_TONE] = ANY_UNIT
    single_nucleus.coord[PREV_TONE] = ANY_UNIT
    single_nucleus.coord[ONSET] = ANY_UNIT
    single_nucleus.coord[CODA] = ANY_UNIT
    extrapolated_coords.append([single_nucleus, 50])

    only_coda = copy.deepcopy(self)
    only_coda.coord[NEXT_TONE] = ANY_UNIT
    only_coda.coord[PREV_TONE] = ANY_UNIT
    only_coda.coord[ONSET] = ANY_UNIT
    only_coda.coord[NUCLEUS] = ANY_UNIT
    extrapolated_coords.append([only_coda, 30])
    
    return extrapolated_coords