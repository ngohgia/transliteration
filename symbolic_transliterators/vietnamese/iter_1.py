import os.path
from transliteration_framework import *

######################################################## ITERATION 1 #########################################################################
# Treat Y as a consonant
# Add omitted consonants
# Not treat omitted vowels yet
iter_id = 1

class iter_1():

  def __init__(self, trans_dict):
    self.trans_dict = trans_dict

    self.iter_folder = os.path.join(os.path.dirname(__file__), 'iter_1/')

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
      if phon_seq[idx] in self.iter_rules.vowel_set or phon_seq[idx] == "_":
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
      if phon_seq[idx] in self.iter_rules.vowel_set and phon_seq[idx] != "W":
        break
      elif phon_seq[idx] in self.iter_rules.ini_conso_set:
        phon_conso = [phon_seq[idx]]
        en_conso = [en_seq[idx]]
        trans.flag[idx] = iter_id
        # Deal with compound initial consonants
        if phon_seq[idx] == "NG":
          if idx > 0 and phon_seq[idx-1] == "_":
            en_conso = pick_items_backwards_from_seq(en_seq, idx, 2)
          if idx < len(phon_seq)-1 and phon_seq[idx+1] == "_":
            en_conso = pick_items_forwards_from_seq(en_seq, idx, 2)
        elif phon_seq[idx] == "K":
          if idx > 0 and phon_seq[idx-1] == "_":
            en_conso = pick_items_backwards_from_seq(en_seq, idx, 2)
          if idx < len(phon_seq)-1 and (phon_seq[idx+1] == "_" or phon_seq[idx+1] == "HH"):
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

  # Fix the hack of vowel position
  def check_syllable(self, idx, trans, en_seq, phon_seq):
    if trans.syl_seq[idx] != None:
      return None
    if (idx > 0 and (phon_seq[idx-1] == "AXR" or phon_seq[idx-1] == "_" or phon_seq[idx-1] == "ER" or phon_seq[idx-1] == "AY")) or \
      (idx < len(phon_seq)-1 and phon_seq[idx+1] == "_"):
      return None
    if phon_seq[idx] in self.iter_rules.vowel_set:
      if phon_seq[idx] == "W" and not (idx > 0 and phon_seq[idx-1] in self.iter_rules.ini_conso_set):
        return None
      new_syl = Syllable()
      new_syl.pos = idx
      new_syl.phon_vowel.append(phon_seq[idx])
      new_syl.en_vowel.append(en_seq[idx])

      trans.flag[idx] = iter_id

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
      tmp = self.check_syllable(idx, trans, trans.inter_en_seq, trans.inter_phon_seq)
      if tmp != None:
        trans.syl_seq[idx] = tmp

    for syl in trans.syl_seq:
      if syl != None:
        # map initial consonants
        self.map_ini_conso(syl)

        # map vowel
        self.map_vowel(syl)

        # map final consonants
        self.map_final_conso(syl)

        # process tone
        self.process_tone(syl)

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

  def map_ini_conso_cluster_SGK(self, syl):
    if syl.phon_ini_conso == ["S","G", "K"] or syl.phon_ini_conso == ["SH","G", "K"]:
      syl.vie_ini_conso = ["s @: _3 . G"]
      return True
    return False 

  def map_ini_conso_cluster_ZR(self, syl):
    if syl.phon_ini_conso == ["Z","R"] and syl.en_ini_conso == ["s", "r"]:
      syl.vie_ini_conso = ["s @: _3 . r\\"]
      return True
    return False 

  def map_ini_conso_cluster_ZM(self, syl):
    if syl.phon_ini_conso == ["Z","M"] and syl.en_ini_conso == ["s", "m"]:
      syl.vie_ini_conso = ["s @: _3 . m"]
      return True
    return False 

  def map_ini_conso_cluster_TH(self, syl):
    if syl.phon_ini_conso == ["T","H"]:
      syl.vie_ini_conso = ["x"]
      return True
    return False

  def map_ini_conso_cluster_RH(self, syl):
    if syl.phon_ini_conso == ["R","HH"]:
      syl.vie_ini_conso = ["z"]
      return True
    return False

  def map_ini_conso_cluster_KH(self, syl):
    if syl.phon_ini_conso == ["K","HH"]:
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
    not self.map_ini_conso_cluster_SGK(syl) and \
    not self.map_ini_conso_cluster_SGK(syl) and \
    not self.map_ini_conso_cluster_TH(syl) and \
    not self.map_ini_conso_cluster_KH(syl) and \
    not self.map_ini_conso_cluster_RH(syl) and \
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

        if idx < len(trans.inter_phon_seq)-2:
          if trans.inter_phon_seq[idx+1] == "TS" and \
            trans.inter_en_seq[idx] == "t" and \
          trans.inter_en_seq[idx+1] == "s":
            trans.inter_phon_seq[idx] = "T"
            trans.inter_phon_seq[idx+1] = "S"

      elif trans.original_en_seq[idx] == "j" and \
      idx < len(trans.original_en_seq)-1 and trans.original_en_seq[idx+1] == "a":
        trans.inter_phon_seq[idx] = "IH"

      elif trans.inter_phon_seq[idx] == "M" and \
      idx < len(trans.inter_phon_seq)-1 and trans.inter_phon_seq[idx+1] == "W":
        trans.inter_phon_seq[idx] = "M"
        trans.inter_phon_seq[idx+1] = "UH"

    for idx in range(len(trans.inter_phon_seq)-1):
      if trans.inter_en_seq[idx] == trans.inter_en_seq[idx+1] and \
      trans.inter_phon_seq[idx] == trans.inter_phon_seq[idx+1]:
        if trans.inter_phon_seq[idx] == "G":
          trans.inter_phon_seq[idx] = "GD"
        elif trans.inter_phon_seq[idx] == "N":
          trans.inter_phon_seq[idx] = "NX"
        elif trans.inter_phon_seq[idx] == "T":
          trans.inter_phon_seq[idx] = "TD"
        elif trans.inter_phon_seq[idx] == "P" or trans.inter_phon_seq[idx] == "B":
          trans.inter_phon_seq[idx] = "PD"

######################################################## SINGLE INITIAL CONSONANTS MAPPING RULES #####################################################################
  def map_ini_conso_DX(self, syl):
    if syl.phon_ini_conso == ["DX"]:
      if syl.en_ini_conso == ["t"]:
        syl.vie_ini_conso.append("t")
      else:
        syl.vie_ini_conso = ["d_<"]
      return True
    return False

  def map_ini_conso_K(self, syl):
    if syl.phon_ini_conso == ["K"]:
      if syl.en_ini_conso == ["k", "h"]:
        syl.vie_ini_conso.append("x")
      elif syl.en_ini_conso == ["g"]:
        syl.vie_ini_conso.append("G")
      else:
        syl.vie_ini_conso.append("k ")
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
      elif syl.en_ini_conso == ["g"]:
        syl.vie_ini_conso.append("G")
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

  def map_ini_conso_G(self, syl):
    if syl.phon_ini_conso == ["G"]:
      if syl.en_ini_conso == ["s"] or syl.en_ini_conso == ["x"]:
        syl.vie_ini_conso.append("s")
      else:
        syl.vie_ini_conso.append("G")
      return True
    return False
  
  def map_ini_conso_Y(self, syl):
    if syl.phon_ini_conso == ["Y"]:
      # for KWS
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
  def map_vowel_AXR(self, syl):
    if syl.phon_vowel == ["AXR"]:
      if syl.en_vowel == ["o"]:
        syl.vie_vowel = ["o"]
      elif syl.en_vowel == "u":
        syl.vie_vowel = "u";
      else:
        syl.vie_vowel = "@:";
      return True
    return False
    
  def map_vowel_AX(self, syl):
    if syl.phon_vowel == ["AX"]:
      if syl.en_vowel == ["e"]:
        syl.vie_vowel = ["E"]
      elif syl.en_vowel == ["u"]:
        syl.vie_vowel = ["u"]
      elif syl.en_vowel == ["o"]:
        syl.vie_vowel = ["o"]
      elif syl.en_vowel == ["i"]:
        syl.vie_vowel = ["i"]
      elif syl.en_vowel == ["a", "y"]:
        syl.vie_vowel = ["aI"]
      elif syl.en_vowel == ["a", "i"]:
        syl.vie_vowel = ["a:I"]  
      else:
        syl.vie_vowel = ["a:"]
      return True
    return False

  def map_vowel_OW(self, syl):
    if syl.phon_vowel == ["OW"]:
      if syl.en_vowel == ["o", "w"]:
        syl.vie_vowel = ["@U"]
      else:
        syl.vie_vowel = ["O"]
      return True
    return False

  def map_vowel_AY(self, syl):
    if syl.phon_vowel == ["AY"]:
      if syl.en_vowel == ["i"] or syl.en_vowel == ["y"]:
        syl.vie_vowel = ["i"]
      else:
        syl.vie_vowel = ["a:I"]
      return True
    return False

  def map_vowel_IX_IY_IH(self, syl):
    if syl.phon_vowel == ["IX"] or syl.phon_vowel == ["IY"] or syl.phon_vowel == ["IH"]:
      if syl.en_vowel == ["e"]:
        syl.vie_vowel = ["E"]
      elif syl.en_vowel == ["a"]:
        syl.vie_vowel = ["a:"]
      else:
        syl.vie_vowel = ["i"]
      return True
    return False

  def map_vowel_AA(self, syl):
    if syl.phon_vowel == ["AA"]:
      if syl.en_vowel == ["o"]:
        syl.vie_vowel = ["O"]
      else:
        syl.vie_vowel = ["a:"]
      return True
    return False

  def map_vowel_AH(self, syl):
    if syl.phon_vowel == ["AH"]:
      if syl.en_vowel == ["o"]:
        syl.vie_vowel = ["o"]
      else:
        syl.vie_vowel = ["u"]
      return True
    return False       

  def map_vowel_EH(self, syl):
    if syl.phon_vowel == ["EH"]:
      if syl.en_vowel == ["o"]:
        syl.vie_vowel = ["O"]
      elif syl.en_vowel == ["e"]:
        syl.vie_vowel = ["E"]
      else:
        syl.vie_vowel = ["a:"]
      return True
    return False

  def map_vowel_AO(self, syl):
    if syl.phon_vowel == ["AO"]:
      if syl.en_vowel == ["a", "u"] or syl.en_vowel == ["a", "w"]:
        syl.vie_vowel = ["aU"]
      elif syl.en_vowel == ["a"]:
        syl.vie_vowel = ["a:"]
      else:
        syl.vie_vowel = ["O"]
      return True
    return False

  def map_vowel_EY(self, syl):
    if syl.phon_vowel == ["EY"]:
      if syl.en_vowel == ["a", "y"]:
        syl.vie_vowel = ["aI"]
      elif syl.en_vowel == ["a", "i"]:
        syl.vie_vowel = ["EU"]
      elif syl.en_vowel == ["u"] or syl.en_vowel == ["e"]:
        syl.vie_vowel = ["e"]
      else:
        syl.vie_vowel = ["a:"]
      return True
    return False

  def map_default_single_vowel(self, syl):
    if len(syl.phon_vowel) == 1:
      if syl.phon_vowel[0] in self.iter_rules.vowel_set:
        syl.vie_vowel.append(self.iter_rules.default_vowel_mapping[syl.phon_vowel[0]])

  def map_vowel(self, syl):
    if not self.map_vowel_AXR(syl) and \
    not self.map_vowel_AX(syl) and \
    not self.map_vowel_AY(syl) and \
    not self.map_vowel_IX_IY_IH(syl) and \
    not self.map_vowel_AA(syl) and \
    not self.map_vowel_AH(syl) and \
    not self.map_vowel_EH(syl) and \
    not self.map_vowel_AO(syl) and \
    not self.map_vowel_EY(syl):
      self.map_default_single_vowel(syl)    

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
      syl.vie_final_conso.append("c")
      return True
    return False

  def map_final_conso_L(self, syl):
    if syl.phon_final_conso == ["L"]:
      if syl.phon_vowel == ["IH"] or \
      syl.phon_vowel == ["EY"] or \
      syl.phon_vowel == ["EH"] or \
      syl.phon_vowel == ["AO"] or \
      syl.phon_vowel == ["AE"] or \
      syl.phon_vowel == ["IX"] or \
      syl.phon_vowel == ["OW"] or \
      syl.phon_vowel == ["AX"] or \
      syl.phon_vowel == ["AH"] or \
      syl.phon_vowel == ["AA"]:
        syl.vie_final_conso = ["n"]
      else:
        syl.phon_final_conso = []
        syl.vie_final_conso = []
      return True
    return False

  def map_final_conso_NG(self, syl):
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
      not self.map_final_conso_NG(syl) and \
      not self.map_final_conso_L(syl):
        self.map_default_final_conso(syl)

######################################################## PROCESS TONES #####################################################################  
  def process_tone(self, syl):
    if len(syl.vie_final_conso) > 0:
      if syl.vie_final_conso[0] in ["k", "p", "t", "c"]:
        syl.vie_tone = 2

######################################################## MAIN LOOP #####################################################################   
  def run(self):
    print "---------------- ITER 1 ----------------------"
    for trans in self.trans_dict:
      self.transliterate(trans)
      print trans.to_string()
