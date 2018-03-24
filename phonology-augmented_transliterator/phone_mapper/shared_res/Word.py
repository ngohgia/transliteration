from Syllable import Syllable

class Word:
  def __init__(self):
    self.syls = []

  def add_new_syl(self, new_syl):
    self.syls.append(new_syl)

  def print_str(self):
    print "Graphemes: " + " . ".join([syl.get_en_graphemes_str() for syl in self.syls])
    print "Roles: " + " . ".join([syl.get_roles_str() for syl in self.syls])
    print "English phonemes: " + " . ".join([syl.get_en_phonemes_str() for syl in self.syls])
    print "Vietnamese phonemes: " + " . ".join([syl.get_vie_phonemes_str() for syl in self.syls])
    print "\n"