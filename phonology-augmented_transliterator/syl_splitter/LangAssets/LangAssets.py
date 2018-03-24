import os

class LangAssets:
  N_GRAM_LEN = 5

  # Possible labels of an alphabet
  VOWEL = "V"
  CONSONANT = "C"
  ANY = "ANY"

  DELIMITER = "#"

  GENERIC_VOWEL = "@"

  # All possible roles of an alphabet
  ONSET = "O"
  NUCLEUS = "N"
  CODA = "Cd"
  ONSET_NUCLEUS = "O_N"
  NUCLEUS_ONSET = "N_O"
  NUCLEUS_NUCLEUS = "N_N"
  NUCLEUS_CODA = "N_Cd"
  CODA_ONSET = "Cd_O"
  CODA_NUCLEUS = "Cd_N"
  CODA_CODA = "Cd_Cd"
  ONSET_NUCLEUS_CODA = "O_N_Cd"
  CODA_ONSET_NUCLEUS = "Cd_O_N"
  REMOVE = "R"

  # All possible roles
  POSSIBLE_ROLES = [ONSET, NUCLEUS, CODA, 
    ONSET_NUCLEUS, NUCLEUS_ONSET, NUCLEUS_NUCLEUS,
    NUCLEUS_CODA, CODA_ONSET, CODA_NUCLEUS, CODA_CODA, ONSET_NUCLEUS_CODA, CODA_ONSET_NUCLEUS, REMOVE]

  # All valid roles for a vowel
  VALID_VOWEL_ROLES = [ONSET, NUCLEUS, CODA,
      ONSET_NUCLEUS, NUCLEUS_NUCLEUS, NUCLEUS_CODA, REMOVE]

  # All valid roles for a consonant
  # A consonant assigned the ONSET_NUCLEUS role can only form
  # an independent syllable
  VALID_CONSO_ROLES = [ONSET, NUCLEUS, CODA, CODA_NUCLEUS, NUCLEUS_ONSET,
      ONSET_NUCLEUS, NUCLEUS_NUCLEUS, NUCLEUS_CODA, CODA_ONSET, REMOVE]

  # SET OF CONSONANTS ALLOWED TO PRECEDE SCHWA
  VALID_CONSO_PRECED_SCHWA = ['p', 'r', 'b', 't', 'd', 'k', 'g', 's', 'f', 'z']

  def __init__(self):
    cur_dir = os.path.dirname(__file__) + "/"

    self.valid_en_vowels = self.get_valid_letters(cur_dir + "/valid_english_vowels.txt")
    self.valid_en_consos = self.get_valid_letters(cur_dir + "valid_english_consos.txt")

    self.valid_vie_vowels = self.get_valid_letters(cur_dir + "valid_vie_vowels.txt")
    self.valid_vie_consos = self.get_valid_letters(cur_dir + "valid_vie_consos.txt")

    self.valid_en_codas = self.get_valid_syl_units(cur_dir + "valid_english_codas.txt")
    self.valid_en_nuclei = self.get_valid_syl_units(cur_dir + "valid_english_nuclei.txt")
    # !!!! Added "tr" to list of valid onsets
    # !!!! Added "c", "l", "h", "j", "z" to list of valid codas
    self.valid_en_onsets = self.get_valid_syl_units(cur_dir + "valid_english_onsets.txt")

  def get_valid_letters(self, input_fname):
    input_file = open(input_fname, "r")
    result = []

    for line in input_file:
      if line.strip() not in result:
        result.append(line.strip())
    return result

  def get_valid_syl_units(self, input_fname):
    input_file = open(input_fname, "r")
    result = []

    for line in input_file:
      units = [unit.strip() for unit in line.split("\t\t")[-1].split(" ")]
      for unit in units:
        if unit not in result:
          result.append(unit)
    return result