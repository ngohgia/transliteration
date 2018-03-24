from LangAssets import LangAssets

lang_assets = LangAssets()
ValidEnConsos = lang_assets.valid_en_consos
ValidEnVowels = lang_assets.valid_en_vowels

SPECIAL_NUCLEUS_CONSOS = ['r']
SPEICAL_ONSET_VOWELS = ['u', 'i', 'y']

class Syllable:
  onset = ""
  nucleus = ""
  coda = ""

  def __str__(self):
    return "[ %s ]" % " ".join([self.onset, self.nucleus, self.coda])

  def get_encoded_units(self):
    struct = []
    if self.onset != "":
      struct.append("O")
    if self.nucleus != "":
      struct.append("N") 
    if self.coda != "":
      struct.append("Cd") 
    return " ".join(struct)

  def to_plain_text(self):
    return "".join([self.onset, self.nucleus, self.coda])

  def get_unit_count(self):
    return len(self.get_encoded_units().split(" "))

  def count_pos_with_mixed_letters(self):
    count = 0;

    if len(self.onset) > 0 and self.onset[0] in ValidEnConsos:
      for i in range(len(self.onset)):
        if self.onset[i] in ValidEnVowels and self.onset[i] not in SPEICAL_ONSET_VOWELS:
          count = count + 1
          break  

    for i in range(len(self.nucleus)):
      if self.nucleus[i] in ValidEnConsos and self.nucleus[i] not in SPECIAL_NUCLEUS_CONSOS:
        count = count + 1
        break

    for i in range(len(self.coda)):
      if self.coda[i] in ValidEnVowels:
        count = count + 1
        break
    return count
