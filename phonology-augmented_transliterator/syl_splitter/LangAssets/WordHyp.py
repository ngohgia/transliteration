# Class for a syllable structure hypothesis

from LangAssets import LangAssets

VALID_CONSO_PRECED_SCHWA = LangAssets.VALID_CONSO_PRECED_SCHWA
ONSET_NUCLEUS = LangAssets.ONSET_NUCLEUS
CODA_ONSET_NUCLEUS = LangAssets.CODA_ONSET_NUCLEUS
ONSET_NUCLEUS_CODA = LangAssets.ONSET_NUCLEUS_CODA
NUCLEUS_CODA = LangAssets.NUCLEUS_CODA
CODA_ONSET = LangAssets.CODA_ONSET

ONSET = LangAssets.ONSET
NUCLEUS = LangAssets.NUCLEUS
CODA = LangAssets.CODA
REMOVE = LangAssets.REMOVE

GENERIC_VOWEL = LangAssets.GENERIC_VOWEL

class WordHyp:
  def __init__(self):
    self.original = ''
    self.original_en_phonemes = []
    self.vie_ref = ''
    self.vie_ref_toneless = []
    self.vie_roles = ''
    self.labels = []
    self.roles = []
    self.reconstructed_word = []
    self.removal_count = 0
    self.compound_role_count = 0
    self.phones_score = 0
    
    self.mod_pen = 0
    self.normalized_mod_score = 0
    self.compound_mod_score = 0
    self.generic_vowel_count = 0
    self.phone_alignment_pen = 0
    self.compound_pen = 0
    self.mixed_letters_pos_count = 0
    self.search_lvl = 0

    self.prob_by_letter = []
    self.construction_prob = 0.0

  def get_str(self):
    text = "Original: " + self.original + "\n"
    text = text + "Original English phonemes: " + str(self.original_en_phonemes) + "\n"
    text = text + "Vie ref: " + str(self.vie_ref) + "\n"
    text = text + "Vie toneless syls: " + str(self.vie_ref_toneless) + "\n"
    text = text + "Vie roles: " + str(self.vie_roles) + "\n"
    text = text + "Labels: " + str(self.labels) + "\n"
    text = text + "Roles: " + (" , ").join(self.roles) + "\n"
    text = text + "Reconstructed word: " + self.reconstructed_word.to_plain_text() + "\n"

    text = text + "New word: " + str(self.reconstructed_word) + "\n"
    text = text + "Construction probability by letter: " + str(self.prob_by_letter) + "\n"
    text = text + "Construction Probability: " + str(self.construction_prob) + "\n"
    text = text + "Encoded subsyllabic units: " + self.reconstructed_word.get_encoded_units() + "\n"
    text = text + "Compound role count: " + str(self.compound_role_count) + "\n"
    text = text + "Removal count: " + str(self.removal_count) + "\n"
    text = text + "Extra letter count: " + str(self.generic_vowel_count) + "\n"
    text = text + "Modification penalty: " + str(self.mod_pen) + "\n"
    text = text + "Normalized mod score: " + str(self.normalized_mod_score) + "\n"
    text = text + "Compound score: " + str(self.compound_mod_score) + "\n"
    text = text + "Phone alignment penalty: " + str(self.phone_alignment_pen) + "\n"
    text = text + "Phones score: " + str(self.phones_score) + "\n"
    text = text + "Mixed letters pos count: " + str(self.mixed_letters_pos_count) + "\n"
    text = text + "Compound penalty: " + str(self.compound_pen) + "\n"
    text = text + "Search lvl: " + str(self.search_lvl) + "\n"
    text = text + "\n"
    return text
  
  def count_removal(self):
    for role in self.roles:
      if role == "R":
        self.removal_count = self.removal_count + 1

  def count_compound_role(self):
    for role in self.roles:
      if role == CODA_ONSET:
        self.compound_role_count = self.compound_role_count + 1

  def count_generic_vowel(self):
    self.generic_vowel_count = self.reconstructed_word.to_plain_text().count(GENERIC_VOWEL)

  def compute_mod_error(self):
    self.mod_pen = levenshtein(self.reconstructed_word.to_plain_text(), self.original)

    # Penalize hypothesis that assigned schwa to invalid letters
    # except the case of "sh" and "th"
    for i in range(len(self.roles)):
      if self.roles[i] == ONSET_NUCLEUS or self.roles[i] == CODA_ONSET_NUCLEUS:
        if self.original[i] not in VALID_CONSO_PRECED_SCHWA and \
        not (self.original[i] == "h" and (i > 0 and \
          ((self.original[i-1] == "s" or self.original[i-1] == "t" \
            or self.original[i-1] == "k" or self.original[i-1] == "g")
          and self.roles[i-1].split("_")[-1] == ONSET))):
          self.mod_pen = self.mod_pen + 5

    # Penalize hypothesis with a CODA followed a schwa
    for i in range(len(self.roles)-1):
      if (self.roles[i] == ONSET_NUCLEUS or self.roles[i] == CODA_ONSET_NUCLEUS):
        for j in range(i+1, len(self.roles)):
          if self.roles[j] != REMOVE:
            if self.roles[j].split("_")[0] == CODA:
              self.mod_pen = self.mod_pen + 5
            break

    # Penalize hypothesis with mixed letters in the reconstructed word's syllables
    for syl in self.reconstructed_word.syls:
      self.mixed_letters_pos_count = self.mixed_letters_pos_count + syl.count_pos_with_mixed_letters()
    self.mod_pen = self.mod_pen + self.mixed_letters_pos_count 

    # Penalize hypothesis with REMOVE
    self.count_removal()
    self.mod_pen = self.mod_pen + self.removal_count*2

    # Penalize hypothesis with COMPOUND role
    self.count_compound_role()
    self.mod_pen = self.mod_pen + self.compound_role_count

    # Penalize hypothesis with REMOVE breaking up syllables
    # or subsyllabic unit
    for i in range(len(self.roles)):
      if self.roles[i] == REMOVE:
        last_non_R = -1
        next_non_R = -1
        # Search for last non REMOVE role
        for j in reversed(range(0, i)):
          if self.roles[j] != REMOVE:
            last_non_R = j
            break
        # Search for next non REMOVE role
        for j in range(i+1, len(self.roles)):
          if self.roles[j] != REMOVE:
            next_non_R = j
            break

        if last_non_R != -1 and next_non_R != -1 and \
        ((self.roles[last_non_R].split("_")[-1] == ONSET \
          and self.roles[next_non_R].split("_")[0] == NUCLEUS) or
        (self.roles[last_non_R].split("_")[-1] == NUCLEUS \
          and self.roles[next_non_R].split("_")[0] == CODA)):
          self.mod_pen = self.mod_pen + 2

        if last_non_R != -1 and next_non_R != -1 and \
        ((self.roles[last_non_R].split("_")[-1] == ONSET \
          and self.roles[next_non_R].split("_")[0] == ONSET) or \
        (self.roles[last_non_R] == CODA \
          and self.roles[next_non_R].split("_")[0] == CODA) or \
        (self.roles[last_non_R].split("_")[-1] == NUCLEUS \
          and self.roles[next_non_R].split("_")[0] == NUCLEUS)):
          self.mod_pen = self.mod_pen + 2

  def award_hyp(self):
    # Award hypothesis that compacts the roles assignment
    for i in range(len(self.roles)):
      if self.roles[i] == NUCLEUS_CODA:
        self.mod_pen = self.mod_pen - 1
      elif self.roles[i] == ONSET_NUCLEUS_CODA:
        self.mod_pen = self.mod_pen - 2

  def to_simple_hyp_text(self):
    text = self.original + "\t" + " ".join(self.labels) + "\t" + " ".join(self.roles)
    return text

  #---------------- LEVENSHTEIN -------------------------#
# Calculate Levenshtein (edit distance) between two string
# This helper function is used to calculate the edit distance between a hypothesized syllable structure and
# the reference syllabic structure
# http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(s1, s2):
  if len(s1) < len(s2):
      return levenshtein(s2, s1)

  # len(s1) >= len(s2)
  if len(s2) == 0:
      return len(s1)

  previous_row = range(len(s2) + 1)
  for i, c1 in enumerate(s1):
      current_row = [i + 1]
      for j, c2 in enumerate(s2):
          insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
          deletions = current_row[j] + 1       # than s2
          substitutions = previous_row[j] + (c1 != c2)
          current_row.append(min(insertions, deletions, substitutions))
      previous_row = current_row

  return previous_row[-1]
