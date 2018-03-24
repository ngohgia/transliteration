class Syllable:
  def __init__(self):
    self.roles = []
    self.vie_phonemes = []
    self.tone = 1

  def create_new_syl(self, vie_phonemes, roles, tone):
    self.roles = roles
    self.vie_phonemes = vie_phonemes
    self.tone = tone

  def get_roles_str(self):
    return (" ").join(self.roles)

  def get_vie_phonemes_str(self):
    return (" ").join(self.vie_phonemes)

  def __str__(self):
    return " ".join(self.vie_phonemes) + " _" + str(self.tone)

