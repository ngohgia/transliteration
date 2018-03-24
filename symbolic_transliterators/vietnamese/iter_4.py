import os.path
from transliteration_framework import *

######################################################## ITERATION 1 #########################################################################
# Correct vowels by overriding syllable created from the previous iteration
iter_id = 4

class iter_4():
  def __init__(self, trans_dict):
    self.trans_dict = trans_dict

    self.iter_folder = os.path.join(os.path.dirname(__file__), 'iter_4/')

    self.iter_rules = Rule()
    self.iter_rules.read_rule_from_files(self.iter_folder)
    self.iter_rules.read_map_from_files(self.iter_folder)
    print self.iter_rules.to_string()

  def find_ini_conso_cluster(self, trans, en_seq, phon_seq, vowel_idx):
    phon_conso = None
    en_conso = None

    phon_tmp = []
    en_tmp = []

    start = vowel_idx-1 if vowel_idx >= 1 else 0
    end = vowel_idx-4 if vowel_idx >= 4 else -1
    for idx in range(start, end, -1):
      if phon_seq[idx] in self.iter_rules.vowel_set:
        break
      elif phon_seq[idx] != "_":
        phon_tmp = [phon_seq[idx]] + phon_tmp
        en_tmp = [en_seq[idx]] + en_tmp
        if phon_tmp in self.iter_rules.vie_ini_conso_clusters_set:
          phon_conso = phon_tmp
          en_conso = en_tmp

          for j in range(idx, start+1):
            trans.flag[j] = iter_id

    if phon_conso != None and en_conso != None:
      return [phon_conso, en_conso]
    return None

  def find_ini_conso(self, trans, en_seq, phon_seq, vowel_idx):
    tmp = self.find_ini_conso_cluster(trans, en_seq, phon_seq, vowel_idx)
    if tmp != None:
      [phon_conso, en_conso] = tmp
      return [phon_conso, en_conso]
    
    for idx in range(vowel_idx-1, -1, -1):
      if phon_seq[idx] in self.iter_rules.vowel_set:
        break
      elif phon_seq[idx] in self.iter_rules.ini_conso_set:
        phon_conso = [phon_seq[idx]]
        en_conso = [en_seq[idx]]
        trans.flag[idx] = iter_id
        # Deal with compound initial consonants
        if phon_seq[idx] == "K" or phon_seq[idx] == "NG":
          if idx > 0 and phon_seq[idx-1] == "_":
            en_conso = pick_items_backwards_from_seq(en_seq, idx, 2)
          if idx < len(phon_seq)-1 and phon_seq[idx+1] == "_":
            en_conso = pick_items_forwards_from_seq(en_seq, idx, 2)

        return[phon_conso, en_conso]

    return None

  def find_final_conso(self, trans, en_seq, phon_seq, vowel_idx):
    for idx in range(vowel_idx+1, len(phon_seq)):
      if phon_seq[idx] in self.iter_rules.vowel_set:
        break
      elif phon_seq[idx] in self.iter_rules.final_conso_set:
        phon_conso = [phon_seq[idx]]
        en_conso = [en_seq[idx]]
        trans.flag[idx] = iter_id

        if phon_seq[idx] == "NG":
          if idx > 0 and phon_seq[idx-1] == "_":
            en_conso = pick_items_backwards_from_seq(en_seq, idx, 2)
          if idx < len(phon_seq)-1 and phon_seq[idx+1] == "_":
            en_conso = pick_items_forwards_from_seq(en_seq, idx, 2)
        
        return [phon_conso, en_conso]
    return None

  # Removed the check if the syllable exists
  def check_syllable(self, idx, trans, en_seq, phon_seq):
    if phon_seq[idx] in self.iter_rules.vowel_set:
      new_syl = Syllable()
      new_syl.pos = idx
      new_syl.phon_vowel.append(phon_seq[idx])
      new_syl.en_vowel.append(en_seq[idx])

      trans.flag[idx] = iter_id
      if phon_seq[idx] == "AH" and \
      idx > 0 and phon_seq[idx-1] == "_":
        new_syl.en_vowel = pick_items_backwards_from_seq(en_seq, idx, 2)
      
      tmp = self.find_ini_conso(trans, en_seq, phon_seq, idx)
      if tmp != None:
        [new_syl.phon_ini_conso, new_syl.en_ini_conso] = tmp

      tmp = self.find_final_conso(trans, en_seq, phon_seq, idx)
      if tmp != None:
        [new_syl.phon_final_conso, new_syl.en_final_conso] = tmp

      return new_syl
    return None

  def transliterate(self, trans):
    self.preprocess(trans)

    for idx in range(len(trans.inter_phon_seq)):
      syl = self.check_syllable(idx, trans, trans.inter_en_seq, trans.inter_phon_seq)
      if syl != None:
        trans.syl_seq[idx] = syl

        # map initial consonants
        self.map_ini_conso(trans.syl_seq[idx])

        # map vowel
        self.map_vowel(trans.syl_seq[idx])

        # map final consonants
        self.map_final_conso(trans.syl_seq[idx])

        # process tone
        self.process_tone(trans.syl_seq[idx])       

######################################################## INITIAL CONSONANT CLUSTERS MAPPING RULES #####################################################################
## TODO: Manage the additional syllables
  def map_ini_conso_cluster_SKW(self, syl):
    if syl.phon_ini_conso == ["S","K","W"] or syl.phon_ini_conso == ["SH","K","W"]:
      syl.vie_ini_conso = ["s @: _3 . k"]
      return True
    return False

  def map_ini_conso_cluster_THR(self, syl):
    if syl.phon_ini_conso == ["TH", "R"]:
      syl.vie_ini_conso = ["t_h @: _3 . r\\"]
      return True
    return False    

  def map_ini_conso_cluster_STR(self, syl):
    if syl.phon_ini_conso == ["S","T", "R"] or syl.phon_ini_conso == ["SH","T", "R"]:
      syl.vie_ini_conso = ["s @: _3 . ts\\"]
      return True
    return False

  def map_ini_conso_cluster_SKR(self, syl):
    if syl.phon_ini_conso == ["S","K", "R"] or syl.phon_ini_conso == ["SH","K", "R"]:
      syl.vie_ini_conso = ["s @: _3 . k @: _3 . z\\"]
      return True
    return False   

  def map_ini_conso_cluster_TH(self, syl):
    if syl.phon_ini_conso == ["T","H"]:
      syl.vie_ini_conso = ["x"]
      return True
    return False

  def map_ini_conso_cluster_TR(self, syl):
    if syl.phon_ini_conso == ["T","R"]:
      syl.vie_ini_conso = ["ts\\"]
      return True
    return False

  def map_ini_conso_cluster_SH(self, syl):
    if syl.phon_ini_conso == ["S","H"]:
      syl.vie_ini_conso = ["s"]
      return True
    return False

  def map_ini_conso_cluster_ZM(self, syl):
    if syl.phon_ini_conso == ["Z","M"] and syl.en_ini_conso == ["s", "m"]:
      syl.vie_ini_conso = ["s @: _3 . m"]
      return True
    return False 

  def map_ini_conso_cluster_RH(self, syl):
    if syl.phon_ini_conso == ["R","HH"]:
      syl.vie_ini_conso = ["r\\"]
      return True
    return False

  def map_ini_conso_cluster_KH(self, syl):
    if syl.phon_ini_conso == ["K","HH"]:
      syl.vie_ini_conso = ["x"]
      return True
    return False

  def map_default_ini_conso_cluster(self, cur_syl):
    if len(cur_syl.phon_ini_conso) == 2 and len(cur_syl.en_ini_conso) == 2:
      vie_cluster = ""

      tmp_syl = Syllable()
      tmp_syl.en_ini_conso = [cur_syl.en_ini_conso[0]]
      tmp_syl.phon_ini_conso = [cur_syl.phon_ini_conso[0]]
      self.map_single_ini_conso(tmp_syl)
      vie_cluster = tmp_syl.vie_ini_conso[0] + " @: _3 . "

      tmp_syl.en_ini_conso = [cur_syl.en_ini_conso[1]]
      tmp_syl.phon_ini_conso = [cur_syl.phon_ini_conso[1]]
      self.map_single_ini_conso(tmp_syl)
      vie_cluster = vie_cluster + tmp_syl.vie_ini_conso[1]

      cur_syl.vie_ini_conso = [vie_cluster]

  def map_ini_conso_cluster(self, syl):
    if not self.map_ini_conso_cluster_SKW(syl) and \
    not self.map_ini_conso_cluster_THR(syl) and \
    not self.map_ini_conso_cluster_STR(syl) and \
    not self.map_ini_conso_cluster_SKR(syl) and \
    not self.map_ini_conso_cluster_TH(syl) and \
    not self.map_ini_conso_cluster_RH(syl) and \
    not self.map_ini_conso_cluster_KH(syl) and \
    not self.map_ini_conso_cluster_TR(syl) and \
    not self.map_ini_conso_cluster_ZM(syl) and \
    not self.map_ini_conso_cluster_SH(syl):
      self.map_default_ini_conso_cluster(syl)

######################################################## PREPROCESS #####################################################################
  def preprocess(self, trans):
    for idx in range(len(trans.inter_phon_seq)):
      if trans.inter_phon_seq[idx] == "_" and \
      not (idx > 0 and trans.inter_phon_seq[idx-1] == "CH") and not (idx < len(trans.inter_phon_seq)-1 and trans.inter_phon_seq[idx+1] == "CH") and \
      not (idx > 0 and trans.inter_phon_seq[idx-1] == "K") and not (idx < len(trans.inter_phon_seq)-1 and trans.inter_phon_seq[idx+1] == "K") and \
      not (idx > 0 and trans.inter_phon_seq[idx-1] == "NG") and not (idx < len(trans.inter_phon_seq)-1 and trans.inter_phon_seq[idx+1] == "NG") and \
      not (idx > 0 and trans.inter_phon_seq[idx-1] == "F"):
        if trans.inter_en_seq[idx] in self.iter_rules.en_consos_set:
          if trans.inter_en_seq[idx] == "c" or trans.inter_en_seq[idx] == "q":
            trans.inter_phon_seq[idx] = "K"
          elif trans.inter_en_seq[idx] == "h":
            trans.inter_phon_seq[idx] = "HH"
          elif trans.inter_en_seq[idx] == "j":
            trans.inter_phon_seq[idx] = "JH"
          else:
            trans.inter_phon_seq[idx] = trans.inter_en_seq[idx].upper()

      if idx > 0 and trans.inter_phon_seq[idx-1] == "JH" and trans.inter_phon_seq[idx] == "AH":
        trans.inter_phon_seq[idx-1] = "_"
        trans.inter_phon_seq[idx] = "AH"

######################################################## SINGLE INITIAL CONSONANTS MAPPING RULES #####################################################################
  def map_ini_conso_DX(self, syl):
    if syl.phon_ini_conso == ["DX"]:
      if syl.en_ini_conso == ["t"]:
        syl.vie_ini_conso.append("t")
        return True
      else:
        syl.vie_ini_conso = ["d_< "]
        return True
    return False

  def map_ini_conso_K(self, syl):
    if syl.phon_ini_conso == ["K"]:
      if syl.en_ini_conso == ["k", "h"]:
        syl.vie_ini_conso.append("x")
        return True
      else:
        syl.vie_ini_conso.append("k ")
        return True
    return False

  def map_ini_conso_G(self, syl):
    if syl.phon_ini_conso == ["G"]:
      if syl.en_ini_conso == ["s"] or syl.en_ini_conso == ["x"]:
        syl.vie_ini_conso.append("s")
      else:
        syl.vie_ini_conso.append("G")
      return True
    return False    

  def map_ini_conso_Z(self, syl):
    if syl.phon_ini_conso == ["Z"]:
      if syl.en_ini_conso == ["s"]:
        syl.vie_ini_conso.append("s")
      else:
        syl.vie_ini_conso.append("z")
      return True
    return False      

  def map_ini_conso_JH(self, syl):
    if syl.phon_ini_conso == ["JH"]:
      if syl.en_ini_conso == ["j"]:
        syl.vie_ini_conso.append("z")
        return True
      elif syl.en_ini_conso == ["g"]:
        syl.vie_ini_conso.append("G ")
        return True
      else:
        syl.vie_ini_conso.append("ts\\")
        return True
    return False

  def map_ini_conso_CH(self, syl):
    if syl.phon_ini_conso == ["CH"]:
      if syl.en_ini_conso == ["t"]:
        syl.vie_ini_conso.append("t")
      else:
        syl.vie_ini_conso.append("ts\\")
      return True
    return False
  
  def map_ini_conso_Y(self, syl):
    # for KWS
    if syl.phon_ini_conso == ["Y"]:
      syl.vie_ini_conso.append("z")
      return True
    return False

  def map_default_single_ini_conso(self, syl):
    if syl.phon_ini_conso[0] in self.iter_rules.ini_conso_set:
      syl.vie_ini_conso.append(self.iter_rules.default_conso_mapping[syl.phon_ini_conso[0]])

  def map_single_ini_conso(self, syl):
    if not self.map_ini_conso_DX(syl) and \
    not self.map_ini_conso_Y(syl) and \
    not self.map_ini_conso_Z(syl) and \
    not self.map_ini_conso_G(syl) and \
    not self.map_ini_conso_JH(syl) and \
    not self.map_ini_conso_CH(syl) and \
    not self.map_ini_conso_K(syl):
      self.map_default_single_ini_conso(syl)

  def map_ini_conso(self, syl):
    if len(syl.phon_ini_conso) > 0:
      if len(syl.phon_ini_conso) == 1:
        self.map_single_ini_conso(syl)
      else:
        self.map_ini_conso_cluster(syl)      

######################################################## VOWEL MAPPING RULES #####################################################################
  def map_vowel_AH(self, syl):
    if syl.phon_vowel == ["AH"]:
      if syl.en_vowel == ["j", "u"]:
        syl.vie_vowel = ["iU"]
      elif syl.en_vowel == ["o"]:
        syl.vie_vowel = ["o"]
      else:
        syl.vie_vowel = ["u"]
      return True
    return False

  def map_vowel(self, syl):
    self.map_vowel_AH(syl)

######################################################## FINAL CONSONANTS MAPPING RULES #####################################################################   
  def map_final_conso_t_stop(self, syl):
    if syl.phon_final_conso[0] in self.iter_rules.t_stops_set:
      syl.vie_final_conso.append("t")
      return True
    return False

  def map_final_conso_p_stop(self, syl):
    if syl.phon_final_conso[0] in self.iter_rules.p_stops_set:
      syl.vie_final_conso.append("p")
      return True
    return False

  def map_final_conso_k_stop(self, syl):
    if syl.phon_final_conso[0] in self.iter_rules.k_stops_set:
      syl.vie_final_conso.append("k")
      return True
    return False

  def map_final_conso_CH(self, syl):
    if syl.phon_final_conso == ["CH"]:
      syl.vie_final_conso.append("ts\\")
      return True
    return False

  def map_final_conso_L(self, syl):
    if syl.phon_final_conso == ["L"]:
      if syl.phon_vowel == ["IH"] or \
      syl.phon_vowel == ["EY"] or \
      syl.phon_vowel == ["EH"] or \
      syl.phon_vowel == ["AO"] or \
      syl.phon_vowel == ["AE"] or \
      syl.phon_vowel == ["OW"] or \
      syl.phon_vowel == ["IX"] or \
      syl.phon_vowel == ["AX"] or \
      syl.phon_vowel == ["AH"] or \
      syl.phon_vowel == ["AA"]:
        syl.vie_final_conso = ["n"]
      else:
        syl.phon_final_conso = []
        syl.vie_final_conso = []
      return True
    return False

  def map_final_conso_N(self, syl):
    if syl.phon_final_conso == ["NG"]:
      if syl.en_final_conso == ["n", "g"]:
        syl.vie_final_conso = ["N"]
      else:
        syl.vie_final_conso = ["n"];
      return True
    return False

  def map_default_final_conso(self, syl):
    if syl.phon_final_conso[0] in self.iter_rules.final_conso_set:
      syl.vie_final_conso.append(self.iter_rules.default_conso_mapping[syl.phon_final_conso[0]])

  def map_final_conso(self, syl):
    if len(syl.phon_final_conso) > 0:
      if not self.map_final_conso_t_stop(syl) and \
      not self.map_final_conso_p_stop(syl) and \
      not self.map_final_conso_k_stop(syl) and \
      not self.map_final_conso_CH(syl) and \
      not self.map_final_conso_N(syl) and \
      not self.map_final_conso_L(syl):
        self.map_default_final_conso(syl)

######################################################## PROCESS TONES #####################################################################  
  def process_tone(self, syl):
    if len(syl.vie_final_conso) > 0:
      if syl.vie_final_conso[0] in ["k", "p", "t", "c"]:
        syl.vie_tone = 2

######################################################## MAIN LOOP #####################################################################   
  def run(self):
    print "---------------- ITER 4 ----------------------"
    for trans in self.trans_dict:
      self.transliterate(trans)
      print trans.to_string()
