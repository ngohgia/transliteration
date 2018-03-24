from Syllable import Syllable

class Word:
  def __init__(self):
    self.syls = []

  def add_new_syl(self, syl):
    self.syls.append(syl)

  def __str__(self):
    return " ".join([str(syl) for syl in self.syls])

  def get_encoded_units(self):
    # print "In get_encoded_units "
    # for syl in self.syls:
    #   print str(syl)
    struct = [syl.get_encoded_units() for syl in self.syls]
    return " . ".join(struct)

  def to_plain_text(self):
  	return "".join([syl.to_plain_text() for syl in self.syls])