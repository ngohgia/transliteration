from Syllable import Syllable

class Word:
  def __init__(self):
    self.syls = []

  def add_new_syl(self, new_syl):
    self.syls.append(new_syl)

  def print_str(self):
    print "Roles: " + " . ".join([syl.get_roles_str() for syl in self.syls])
    print "Vietnamese phonemes: " + " . ".join([str(syl) for syl in self.syls])
    print "\n"