class Syllable:
  def __init__(self):
    self.en_graphemes = []
    self.roles = []
    self.en_phonemes = []
    self.vie_phonemes = []

  def create_new_syl(self, en_graphemes, roles, en_phonemes, vie_phonemes):
    self.en_graphemes = en_graphemes
    self.en_phonemes = en_phonemes
    self.roles = roles
    self.vie_phonemes = vie_phonemes

  def get_en_graphemes_str(self):
    return (" ").join(self.en_graphemes)

  def get_roles_str(self):
    return (" ").join(self.roles)

  def get_en_phonemes_str(self):
    print str(self.en_phonemes)
    return (" - ").join(self.en_phonemes)

  def get_vie_phonemes_str(self):
    return (" ").join(self.vie_phonemes)

