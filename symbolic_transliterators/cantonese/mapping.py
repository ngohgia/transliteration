from __future__ import print_function
from syllable import ESyl
from syllable import TSyl
from syllable import syllable_split
import utility

map_onset = utility.load_dict('dict_onset_v01')
map_nucleus = utility.load_dict('dict_nucleus_v01')
map_coda = utility.load_dict('dict_coda_v01')
map_rules = []
vowel = 'aeuio'


def mapping(words):
    with open('rules') as fh:
        for line in fh.readlines():
            if len(line) == 0 or line[0] == '#':
                continue
            structs = line.split('\t')
            assert len(structs[0].split(',')) == 3
            on1, nu1, co1 = [part.strip() for part in structs[0].split(',')]
            if len(structs) == 2:
                assert len(structs[1].split(',')) == 3
                on2, nu2, co2 = [
                    part.strip() for part in structs[1].split(',')
                ]
                if on2 == '*':
                    assert on1 == '*'
                    for key, val in list(map_onset.items()):
                        map_rules.append(
                            [ESyl(key, nu1, co1), [TSyl(val, nu2, co2)]])
                    map_rules.append(
                        [ESyl('*', nu1, co1), [TSyl('', nu2, co2)]])
                elif co2 == '*':
                    assert co1 == '*'
                    for key, val in list(map_coda.items()):
                        map_rules.append(
                            [ESyl(on1, nu1, key), [TSyl(on2, nu2, val)]])
                    map_rules.append(
                        [ESyl(on1, nu1, '*'), [TSyl(on2, nu2, '')]])
                else:
                    map_rules.append(
                        [ESyl(on1, nu1, co1), [TSyl(on2, nu2, co2)]])
            elif len(structs) == 3:
                assert len(structs[1].split(',')) == 3
                assert len(structs[2].split(',')) == 3
                on2, nu2, co2 = [
                    part.strip() for part in structs[1].split(',')
                ]
                on3, nu3, co3 = [
                    part.strip() for part in structs[2].split(',')
                ]
                if on2 == '*':
                    assert on1 == '*'
                    for key, val in list(map_onset.items()):
                        map_rules.append([
                            ESyl(key, nu1, co1), [
                                TSyl(val, nu2, co2), TSyl(on3, nu3,
                                                                    co3)
                            ]
                        ])
                    map_rules.append([
                        ESyl('*', nu1, co1),
                        [TSyl('', nu2, co2), TSyl(on3, nu3, co3)]
                    ])
                else:
                    map_rules.append([
                        ESyl(on1, nu1, co1),
                        [TSyl(on2, nu2, co2), TSyl(on3, nu3, co3)]
                    ])

    # Split words into syllables
    syllables_sequences = []
    for i, word in enumerate(words):
        syllable_output = []
        for part in word.split('_'):
            fail, syllables = syllable_split(part)
            syllable_output.extend(syllables)
        syllables_sequences.append(syllable_output)

    entries = []
    for i, syllables_sequence in enumerate(syllables_sequences):
        sclite_out = []
        for j, syl in enumerate(syllables_sequence):
            if j == len(syllables_sequence) - 1 and syl == ESyl('bl', 'e', ''):
                sclite_out.append(TSyl('b', 'ou'))
                continue
            # Exceptions
            aux, syl = initial_consonant_clusters_mapping(syl)
            if aux is not None:
                sclite_out.append(aux)
            if syl == ESyl('h', 'u', 'n') and syl.suffix[0] == 't':
                sclite_out.append(TSyl('h', 'a', 'ng'))
            elif syl == ESyl('n', 'e', '') and syl.suffix[0] in ['g', 'v']:
                sclite_out.append(TSyl('n', 'oi', ''))
            elif syl == ESyl('c', 'e', '') and syl.suffix[0] in ['l']:
                sclite_out.append(TSyl('c', 'oi', ''))
            elif syl == ESyl('g', 'e', 'l'):
                sclite_out.append(TSyl('g', 'aa', 'k'))
            elif syl == ESyl('g', 'e', '') and j + 1 < len(
                    syllables_sequence) and syllables_sequence[j + 1] == ESyl(
                        'l', '', ''):
                sclite_out.append(TSyl('g', 'aa', 'k'))
            elif syl == ESyl('g', 'e', '') and syl.suffix[0] in ['l', 'n']:
                sclite_out.append(TSyl('g', 'ei', ''))
            elif syl == ESyl('g', 'er', ''):
                sclite_out.extend(
                    [TSyl('j', 'a', 't'), TSyl('j', 'i', '')])
            elif syl == ESyl('g', 'e', '') and syl.suffix[0] in ['r']:
                sclite_out.append(TSyl('j', 'a', 't'))
            elif syl == ESyl('v', 'e', '') and syl.prefix[-1] in ['i', 'e']:
                sclite_out.append(TSyl('f', 'u', ''))
            elif syl == ESyl('v', 'e', ''):
                sclite_out.append(TSyl('w', 'ai', ''))
            elif syl == ESyl('d', 'o',
                             '') and syl.prefix[-1] in ['n', 'l', 'r']:
                sclite_out.append(TSyl('d', 'ou', ''))
            elif syl == ESyl('g', 'or', ''):
                sclite_out.append(TSyl('gw', 'o', ''))
            elif syl == ESyl('g', 'o', '') and syl.suffix[0] in ['r', 'l']:
                sclite_out.append(TSyl('gw', 'o', ''))
            elif match(syl, ["t-o-m", "th-o-m"]):
                sclite_out.append(TSyl('t', 'o', 'ng'))
            elif syl == ESyl('*', 'i', 'p'):
                sclite_out.append(
                    TSyl(map_onset.get(syl.o, ''), 'i', 'p'))
            elif syl == ESyl('*', 'i', '') and syl.suffix[0] in ['p']:
                sclite_out.append(
                    TSyl(map_onset.get(syl.o, ''), 'i', 'p'))
            elif match(syl, ["p-ea-r", "b-ea-r"]):
                sclite_out.append(TSyl('b', 'e'))
            elif syl in [
                    ESyl('l', 'a', 'c'), ESyl('r', 'a', 'c'), ESyl(
                        'l', 'a', 'k'), ESyl('r', 'a', 'k')
            ]:
                sclite_out.append(TSyl('l', 'i', 'k'))
            elif match(syl, ["*-i-s", "*-i-t", "*-ea-t", "*-i-d"]):
                sclite_out.append(
                    TSyl(map_onset.get(syl.o, ''), 'i', 't'))
            else:
                found = False
                for key, val in map_rules:
                    if syl == key:
                        sclite_out.extend(val)
                        found = True
                        break
                if not found:
                    sclite_out.extend(default_mapping(syl))
        entries.append(sclite_out)

    return entries


# In ESyllabe, ["th-o-m", "t-o-m"]
def match(eng_syl, syl_list):
    for syl in syl_list:
        parts = syl.split('-')
        if eng_syl == ESyl(parts[0], parts[1], parts[2]):
            return True
        elif eng_syl == ESyl(parts[0],
                             parts[1]) and eng_syl.suffix.startswith(parts[2]):
            return True
    return False


# In : Grapheme form
# Out: Phoneme form
def default_mapping(syllable):
    return [
        TSyl(
            map_onset.get(syllable.o, ''),
            map_nucleus.get(syllable.n, '@'), map_coda.get(syllable.c, ''))
    ]


def initial_consonant_clusters_mapping(syl):
    if len(syl.o) > 1 and syl.o[
            -1] in ['l', 'r', 'n'] and syl.o[:-1] in ['ch', 'c', 'kh', 'k']:
        syl.o = 'l'
        return TSyl('h', 'a', 'k'), syl
    elif syl.o == 'pr':
        syl.o = 'r'
        return TSyl('p', 'ou'), syl
    elif syl.o == 'pl':
        syl.o = 'l'
        return TSyl('p', 'aa', 'k'), syl
    elif syl.o == 'br':
        syl.o = 'r'
        return TSyl('b', 'ou'), syl
    elif syl.o == 'bl':
        syl.o = 'l'
        return TSyl('b', 'ou'), syl
    elif syl.o == 'dr':
        syl.o = 'r'
        return TSyl('d', 'a', 'k'), syl
    elif syl.o in ['fl', 'fr']:
        syl.o = syl.o[1:]
        return TSyl('f', 'u'), syl
    elif syl.o == 'gl':
        syl.o = 'l'
        return TSyl('g', 'aa', 'k'), syl
    elif syl.o == 'gr':
        syl.o = 'r'
        return TSyl('g', 'aa', 'k'), syl
    elif syl.o in ['sm', 'sn', 'st', 'sp', 'str', 'sl']:
        syl.o = syl.o[1:]
        return TSyl('s', 'i'), syl
    elif syl.o == 'sw':
        syl.o = 'd'
        return TSyl('s', 'eoi', ''), syl
    elif syl.o == 'tr':
        syl.o = 'l'
        return TSyl('d', 'a', 'k'), syl
    else:
        return None, syl
