import sys

def read_original_data(input_file):
    input = open(input_file, "r")

    en_words = []
    vie_words = []
    for line in input:
        [en, vie] = line.strip().split("\t")
        en_word = [syl.strip() for syl in en.split(" . ")]
        vie_word = [syl.strip() for syl in vie.split(" . ")]
        if len(en_word) != len(vie_word):
            print ("ERROR! Mismatched numeber of syllables in entry %s" % line.strip())
            sys.exit(1)
        en_words.append(en_word)
        vie_words.append(vie_word)

    input.close()
    return [en_words, vie_words]

def create_new_data(en_words, vie_words):
    entries = []
    for i in range(len(en_words)):
        en_syls = en_words[i]
        vie_syls = vie_words[i]
        for j in range(len(en_syls)):
            entry = en_syls[j] + "\t" + vie_syls[j]
            if entry not in entries:
                entries.append(entry)

    return entries

def write_to_files(entries, output_files_name):
    syl_en = open(output_files_name + ".syl_en", "w")
    syl_vie = open(output_files_name + ".syl_vie", "w")
    
    for entry in entries:
        [en, vie] = entry.split("\t")
        syl_en.write(en + "\n")
        syl_vie.write(vie + "\n")

    syl_en.close()
    syl_vie.close()

def create_reformatted_data(input_file, output_files_name):
    [en_words, vie_words] = read_original_data(input_file)
    entries = create_new_data(en_words, vie_words)
    write_to_files(entries, output_files_name)