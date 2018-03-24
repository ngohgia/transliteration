import os.path
from transliteration_framework import *

######################################################## POST PROCESS THE VIE SYLLABLES #########################################################################

class postprocess():
  iter_folder = os.path.join(os.path.dirname(__file__), 'postprocess/')

  def __init__(self, trans_dict):
    self.trans_dict = trans_dict

    self.iter_rules = Rule()
    self.iter_rules.read_rule_from_files(self.iter_folder)

  def remove_extra_final_consonants(self, syl):
    # If the vowel is an ending vowel in Vietnamese, do not map the final consonant
    if syl.vie_vowel[0] in self.iter_rules.valid_ending_vie_vowels_set:
      syl.phon_final_conso = []
      syl.vie_final_conso = []
      syl.vie_tone = 1

  def remove_extra_consecutive_consonants(self, trans):
    prv_idx = None

    for idx in range(len(trans.syl_seq)):
      if trans.syl_seq[idx] != None:
        if prv_idx == None:
          prv_idx = idx
        else:
          if len(trans.syl_seq[idx].phon_ini_conso) > 0 and len(trans.syl_seq[prv_idx].phon_final_conso) > 0:
            tmp_len = len(trans.syl_seq[prv_idx].phon_final_conso)
            if trans.syl_seq[idx].phon_ini_conso[0].find(trans.syl_seq[prv_idx].phon_final_conso[tmp_len-1]) == 0:
              trans.syl_seq[prv_idx].phon_final_conso = []
              trans.syl_seq[prv_idx].vie_final_conso = []
              trans.syl_seq[prv_idx].vie_tone = 1
          prv_idx = idx

  def fix_E_vowel(self, syl):
    if syl.vie_vowel == ["E"]:
      # TODO: fit this into the syllable structure
      if len(syl.vie_final_conso) == 0:
        if len(syl.vie_ini_conso) > 0 and ("r\\" in syl.vie_ini_conso[0] or \
          syl.vie_ini_conso == ["d_<"] or \
          syl.vie_ini_conso == ["b_<"] or \
          syl.vie_ini_conso == ["n"] or \
          syl.vie_ini_conso == ["l"] or \
          syl.vie_ini_conso == ["t"]):
          syl.vie_vowel = ["e"]
    elif syl.vie_vowel == ["e"]:
      if syl.vie_final_conso == ["n"] and syl.vie_ini_conso == ["ts\\"]:
        syl.vie_vowel = ["E"]


  def fix_final_K(self, trans, syl):
    if syl.vie_final_conso == ["k"]:
      if syl.vie_vowel == ["e"] or syl.vie_vowel == ["@:"] or \
      (syl.vie_ini_conso == ["l"] and syl.vie_vowel == ["E"]) or \
      (syl.vie_vowel == ["a:"] and syl.vie_final_conso == ["t"] and self.is_last_syl(trans, syl.pos)):
        syl.vie_final_conso = ["t"]
      elif syl.vie_vowel == ["i"]:
        syl.vie_final_conso = ["c"]
      elif syl.vie_vowel == ["o"] and len(syl.vie_ini_conso) == 0:
        syl.vie_vowel = ["O"]

  def fix_ini_conso_G(self, syl):
    if syl.vie_ini_conso == ["G"] and len(syl.vie_final_conso) == 0:
      if syl.vie_vowel == ["E"] or syl.vie_vowel == ["e"] :
        syl.vie_ini_conso = ["z"]
        syl.vie_vowel = ["e"]

  def fix_LIN_ending(self, syl):
    if syl.vie_ini_conso == ["l"] and syl.vie_vowel == ["i"] and syl.vie_final_conso == ["n"]:
      syl.vie_final_conso = ["J"]

  def fix_iN_ending(self, syl):
    if syl.vie_vowel == ["i"] and syl.vie_final_conso == ["N"]:
      syl.vie_final_conso = ["J"]

  def fix_SON_ending(self, trans):
    last_syl = None
    for syl in trans.syl_seq:
      if syl != None:
        last_syl = syl 

    if last_syl != None:
      if last_syl.en_ini_conso == ["s"] and last_syl.en_vowel == ["o"] and last_syl.en_final_conso == ["n"]:
        last_syl.vie_ini_conso = ["s"]
        last_syl.vie_vowel = ["@:"]
        last_syl.vie_final_conso = ["n"]
        last_syl.vie_tone = 1

  def fix_conso_W(self, syl):
    if len(syl.vie_ini_conso) > 0 and syl.vie_ini_conso[len(syl.vie_ini_conso)-1] == "w":
      if (syl.vie_vowel == ["a:"]):
        syl.vie_ini_conso = []
        syl.vie_vowel = ["Oa:"]

  def fix_vowel_W(self, syl):
    if syl.phon_vowel == ["W"]:
      if (syl.en_vowel == ["o"]):
        syl.vie_vowel = ["o"]
      else:
        syl.vie_vowel = ["u"]

  def fix_UR(self, syl):
    if syl.phon_vowel == ["AX"] and syl.phon_final_conso == ["R"] and \
    syl.en_vowel == ["u"] and syl.en_final_conso == ["r"]:
      syl.vie_vowel = ["@:"]
      syl.vie_final_conso = []

  def fix_vowel_clustes(self, trans):
    for idx in range(0, len(trans.inter_phon_seq)-1):
      if trans.syl_seq[idx] != None and trans.syl_seq[idx+1] != None:
        if trans.syl_seq[idx+1].vie_ini_conso == [] and trans.syl_seq[idx+1].vie_final_conso == [] and \
        trans.syl_seq[idx].vie_final_conso == []:
          if trans.syl_seq[idx].vie_vowel == ["u"] and trans.syl_seq[idx+1].vie_vowel == ["a:"]:
            trans.syl_seq[idx].vie_vowel = ["u@"]
            trans.syl_seq[idx+1] = None
          elif trans.syl_seq[idx].vie_vowel == ["O"] and trans.syl_seq[idx+1].vie_vowel == ["a:"]:
            trans.syl_seq[idx].vie_vowel = ["Oa:"]
            trans.syl_seq[idx+1] = None
          elif trans.syl_seq[idx].vie_vowel == ["u"] and trans.syl_seq[idx+1].vie_vowel == ["O"]:
            trans.syl_seq[idx].vie_vowel = ["u"]
            trans.syl_seq[idx+1] = None
          elif trans.syl_seq[idx].vie_vowel == ["u"] and trans.syl_seq[idx+1].vie_vowel == ["i"]:
            trans.syl_seq[idx].vie_vowel = ["uI"]
            trans.syl_seq[idx+1] = None
          elif trans.syl_seq[idx].vie_vowel == ["o"] and trans.syl_seq[idx+1].vie_vowel == ["@:"]:
            trans.syl_seq[idx].vie_vowel = ["u@ "]
            trans.syl_seq[idx+1] = None
          elif trans.syl_seq[idx].vie_vowel == ["a:"] and trans.syl_seq[idx+1].vie_vowel == ["o"]:
            trans.syl_seq[idx].vie_vowel = ["a:U"]
            trans.syl_seq[idx+1] = None

    for idx in range(0, len(trans.inter_phon_seq)-1):
      if trans.syl_seq[idx] != None and trans.syl_seq[idx+1] != None:
        if trans.syl_seq[idx].vie_ini_conso == [] and trans.syl_seq[idx].vie_final_conso == [] and \
        trans.syl_seq[idx+1].vie_ini_conso == [] and \
        trans.syl_seq[idx].vie_vowel == trans.syl_seq[idx+1].vie_vowel:
          trans.syl_seq[idx] = None
        elif trans.syl_seq[idx+1].vie_ini_conso == [] and trans.syl_seq[idx+1].vie_final_conso == [] and \
        trans.syl_seq[idx].vie_final_conso == [] and \
        trans.syl_seq[idx].vie_vowel == trans.syl_seq[idx+1].vie_vowel:
          trans.syl_seq[idx+1] = None

  def fix_ending_consonants(self, trans):
    idx = len(trans.inter_phon_seq)-1
    while idx > 0:
      if trans.inter_phon_seq[idx] == "_":
        idx = idx - 1
      else:
        break

    if trans.flag[idx] == 0:
      if trans.inter_phon_seq[idx] == "S" or \
        trans.inter_phon_seq[idx] == "SH":
          new_syl = Syllable()

          new_syl.vie_ini_conso = ["s"]
          new_syl.vie_vowel = ["@:"]
          new_syl.vie_tone = 1

          trans.syl_seq[idx] = new_syl
      elif trans.inter_phon_seq[idx] == "DD":
          new_syl = Syllable()

          new_syl.vie_ini_conso = ["d_<"]
          new_syl.vie_vowel = ["@:"]
          new_syl.vie_tone = 1

          trans.syl_seq[len(trans.inter_phon_seq)-1] = new_syl
      # elif trans.inter_phon_seq[idx] == "K" or trans.inter_phon_seq[idx] == "KD":
      #     new_syl = Syllable()

      #     new_syl.vie_ini_conso = ["k"]
      #     new_syl.vie_vowel = ["@:"]
      #     new_syl.vie_tone = 1

      #     trans.syl_seq[len(trans.inter_phon_seq)-1] = new_syl


    if trans.flag[idx-1:idx+1] == [0, 0]:
      if trans.inter_phon_seq[idx-1:idx+1] == ["S", "K"] or \
      trans.inter_phon_seq[idx-1:idx+1] == ["S", "KD"]:
          new_syl = Syllable()

          new_syl.vie_ini_conso = ["s @: _3 . k"]
          new_syl.vie_vowel = ["@:"]
          new_syl.vie_tone = 1

          trans.syl_seq[idx] = new_syl
      if trans.inter_phon_seq[idx-1:idx+1] == ["Z", "HH"]:
          new_syl = Syllable()

          new_syl.vie_ini_conso = ["z"]
          new_syl.vie_vowel = ["@:"]
          new_syl.vie_tone = 1
          if trans.inter_en_seq[idx] == "s":
            new_syl.vie_ini_conso = ["s"]

          trans.syl_seq[idx] = new_syl

  # Helper function, determine if the syllable at position idx is the last syllable
  def is_last_syl(self, trans, idx):
    for i in range(idx+1, len(trans.syl_seq)):
      if trans.syl_seq[i] != None:
        return False
    return True
######################################################## MAIN LOOP #####################################################################   
  def run(self):
    print "---------------- POST PROCESS ----------------------"
    for trans in self.trans_dict:
      self.remove_extra_consecutive_consonants(trans)
      # self.fix_ending_consonants(trans)
      self.fix_SON_ending(trans)

      for syl in trans.syl_seq:
        if syl != None:
          self.remove_extra_final_consonants(syl)
          self.fix_E_vowel(syl)
          # self.fix_final_K(trans, syl)
          self.fix_conso_W(syl)
          self.fix_vowel_W(syl)
          #self.fix_OE_vowel(syl)
          self.fix_ini_conso_G(syl)
          self.fix_UR(syl)
          # self.fix_LIN_ending(syl)
          # self.fix_iN_ending(syl)

      self.fix_vowel_clustes(trans)

      print trans.to_string()
