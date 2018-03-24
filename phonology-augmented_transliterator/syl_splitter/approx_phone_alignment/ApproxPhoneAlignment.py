import os

from shared_res.Syllable import Syllable
from shared_res.Word import Word

ONSET = "O"
NUCLEUS = "N"
CODA = "Cd"
GENERIC_VOWEL = "@"

EN_DIPTHONGS = ["EY", "AY", "OW", "AW", "OY", "ER", "AXR", "UW", "IY", "AX", "AO", "UH"]
COMPOUND_EN_CONSOS = ["CH", "TH", "DH", "SH", "K", "KD", "TS"]

def read_split_lex_file(lex_file_path):
  lex_file = open(lex_file_path, "r")

  all_words = []
  for line in lex_file:
    [en_syls_str, roles_str, vie_syls_str] = line.split("\t")[2:5]

    en_syls = [[unit.strip() for unit in en_syl.strip().split(" ")] for en_syl in en_syls_str[1:len(en_syls_str)].split("] [")]
    roles = [[unit.strip() for unit in roles_grp.split(" ")] for roles_grp in roles_str.split(" . ")]
    vie_syls = [[unit.strip() for unit in vie_syl.split(" ")[0:len(vie_syl.split(" "))]] for vie_syl in vie_syls_str.split(" . ")]

    new_word = Word()
    for idx in range(len(en_syls)):
      new_syl = Syllable()
      new_syl.create_new_syl(en_syls[idx], roles[idx], [], vie_syls[idx])
      new_word.add_new_syl(new_syl)

    all_words.append(new_word)

  return all_words
  lex_file.close()

def get_approx_phone_alignment(lex_file_path):
  all_words = read_split_lex_file(lex_file_path);
  phone_alignment_by_role = {ONSET: {}, NUCLEUS: {}, CODA: {}}
  vie_to_en_phone_alignment_prob = {ONSET: {}, NUCLEUS: {}, CODA: {}}

  for word in all_words:
    for syl in word.syls:
      for idx in range(len(syl.roles)):
        role = syl.roles[idx]
        en_grapheme = syl.en_graphemes[idx]
        vie_phoneme = syl.vie_phonemes[idx]
        if en_grapheme not in phone_alignment_by_role[role]:
          phone_alignment_by_role[role][en_grapheme] = [vie_phoneme]
        else:
          if vie_phoneme not in phone_alignment_by_role[role][en_grapheme]:
            phone_alignment_by_role[role][en_grapheme].append(vie_phoneme)

        if vie_phoneme not in vie_to_en_phone_alignment_prob[role]:
          vie_to_en_phone_alignment_prob[role][vie_phoneme] = {en_grapheme: 1}
        else:
          if en_grapheme not in vie_to_en_phone_alignment_prob[role][vie_phoneme]:
            vie_to_en_phone_alignment_prob[role][vie_phoneme][en_grapheme] = 1
          else:
            vie_to_en_phone_alignment_prob[role][vie_phoneme][en_grapheme] = vie_to_en_phone_alignment_prob[role][vie_phoneme][en_grapheme] + 1

  # normalize vie_to_en_phone_alignment_prob
  for role in vie_to_en_phone_alignment_prob:
    for vie_phoneme in vie_to_en_phone_alignment_prob[role]:
      sum_count = sum(vie_to_en_phone_alignment_prob[role][vie_phoneme].values())
      for en_grapheme in vie_to_en_phone_alignment_prob[role][vie_phoneme]:
        vie_to_en_phone_alignment_prob[role][vie_phoneme][en_grapheme] = 1.0 * vie_to_en_phone_alignment_prob[role][vie_phoneme][en_grapheme] / sum_count

  tmp = lex_file_path.split("_")
  phone_alignment_dict_file = open("/".join(lex_file_path.split("/")[0:len(lex_file_path.split("/"))-1]) + "/phone_alignment_dict_" + ("_").join(lex_file_path.split("_")[len(tmp)-2:len(tmp)]), "w")
  vie_to_en_phone_alignment_file = open("/".join(lex_file_path.split("/")[0:len(lex_file_path.split("/"))-1]) + "/vie_to_en_phone_alignment_" + ("_").join(lex_file_path.split("_")[len(tmp)-2:len(tmp)]), "w")

  phone_alignment_dict_file.write("ONSET\n")
  phone_alignment_dict_file.write(str(phone_alignment_by_role[ONSET]) + "\n\n")
  vie_to_en_phone_alignment_file.write("ONSET\n")
  vie_to_en_phone_alignment_file.write(str(vie_to_en_phone_alignment_prob[ONSET]) + "\n\n")

  phone_alignment_dict_file.write("NUCLEUS\n")
  phone_alignment_dict_file.write(str(phone_alignment_by_role[NUCLEUS]) + "\n\n")
  vie_to_en_phone_alignment_file.write("NUCLEUS\n")
  vie_to_en_phone_alignment_file.write(str(vie_to_en_phone_alignment_prob[NUCLEUS]) + "\n\n")

  phone_alignment_dict_file.write("CODA\n")
  phone_alignment_dict_file.write(str(phone_alignment_by_role[CODA]) + "\n\n")
  vie_to_en_phone_alignment_file.write("CODA\n")
  vie_to_en_phone_alignment_file.write(str(vie_to_en_phone_alignment_prob[CODA]) + "\n\n")

  phone_alignment_dict_file.close()
  vie_to_en_phone_alignment_file.close()


  return phone_alignment_by_role

def identify_compound_phones_in_hyp(hyp):
  correct_compound_phones_count = 0
  for idx in range(len(hyp.original_en_phonemes)):
    curr_phone = hyp.original_en_phonemes[idx]; curr_role = hyp.roles[idx]
    if curr_phone in EN_DIPTHONGS or curr_phone in COMPOUND_EN_CONSOS:
      prev_phone = "" ; prev_role = ""
      next_phone = "" ; next_role = ""
      if idx > 0:
        prev_phone = hyp.original_en_phonemes[idx-1]
        prev_role = hyp.roles[idx-1]
      if idx < len(hyp.original_en_phonemes) - 1:
        next_phone = hyp.original_en_phonemes[idx+1]
        next_role = hyp.roles[idx+1]
      if prev_phone == "_":
        if prev_role.split("_")[-1] == curr_role.split("_")[0]:
          correct_compound_phones_count = correct_compound_phones_count + 1
          print prev_phone + " " + curr_phone
      if next_phone == "_":
        if next_role.split("_")[0] == curr_role.split("_")[-1]:
          correct_compound_phones_count = correct_compound_phones_count + 1
          print curr_phone + " " + next_phone
  return correct_compound_phones_count


def score_hyp_with_phone_alignment(word_hyps, phone_alignment_dict):
  lowest_phone_alignment_pen = 1000
  best_hyps = []

  for hyp in word_hyps:
    vie_phones = [syl.strip().split() for syl in hyp.vie_ref_toneless]
    vie_roles = [syl.strip().split() for syl in hyp.vie_roles.split(" . ")]

    tmp_en_word = str(hyp.reconstructed_word)[1:-1]
    en_phones = [syl.strip().split(" ") for syl in tmp_en_word.split(" ] [")]

    phone_alignment_pen = 0
    for syl_idx in range(len(vie_roles)):
      for role_idx in range(len(vie_roles[syl_idx])):
        role = vie_roles[syl_idx][role_idx]
        vie_phone = vie_phones[syl_idx][role_idx]
        en_phone = en_phones[syl_idx][role_idx]

        if en_phone != GENERIC_VOWEL:
          if en_phone in phone_alignment_dict[role]:
            if vie_phone not in phone_alignment_dict[role][en_phone]:
              print("Wrong phone alignment: " + " - ".join([role, en_phone, vie_phone]))
              phone_alignment_pen = phone_alignment_pen + 1
    hyp.phone_alignment_pen = phone_alignment_pen
    # print hyp.get_str()
    if phone_alignment_pen < lowest_phone_alignment_pen:
      lowest_phone_alignment_pen = phone_alignment_pen
      best_hyps = [hyp]
    elif phone_alignment_pen == lowest_phone_alignment_pen:
      best_hyps.append(hyp)
  
  print("---------------- COMPLEX WORDS BEST HYPS ----------------------")
  for idx in range(len(best_hyps)):
    best_hyps[idx].compound_phones_count = identify_compound_phones_in_hyp(best_hyps[idx])
    print(best_hyps[idx].get_str())

  max_mod_pen = 0
  max_phone_alignment_pen = 0
  max_compound_phones_count = 0
  for idx in range(len(best_hyps)):
    if best_hyps[idx].mod_pen > max_mod_pen:
      max_mod_pen = best_hyps[idx].mod_pen
    if best_hyps[idx].phone_alignment_pen > max_phone_alignment_pen:
      max_phone_alignment_pen = best_hyps[idx].phone_alignment_pen
    if best_hyps[idx].compound_phones_count > max_compound_phones_count:
      max_compound_phones_count = best_hyps[idx].compound_phones_count

  for idx in range(len(best_hyps)):
    best_hyps[idx].compound_pen = best_hyps[idx].phone_alignment_pen * 1.0 / (max_phone_alignment_pen + 0.1) + \
      best_hyps[idx].phone_alignment_pen * 1.0 / (max_phone_alignment_pen + 0.1) - \
      best_hyps[idx].compound_phones_count * 1.0 / (max_compound_phones_count + 0.1)

  print("---------------- COMPLEX WORDBEST HYP ----------------------")
  best_hyps = sorted(best_hyps, key=lambda hyp: hyp.compound_pen)
  return best_hyps[0]
