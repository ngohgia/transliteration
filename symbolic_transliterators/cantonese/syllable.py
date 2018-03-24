#!/usr/bin/python
import sys

vowels = ['a', 'i', 'u', 'e', 'o']
init_digraph = [
    'bl', 'br', 'ch', 'cl', 'cr', 'dr', 'fl', 'fr', 'gr', 'pl', 'pr', 'sh',
    'st', 'th', 'tr', 'tw', 'wh', 'wr', 'ph', 'kr', 'kh'
]
init_trigraph = ['sch', 'scr', 'shr', 'sph', 'spl', 'spr', 'squ', 'str', 'thr']
init_consonant_clusters = init_digraph + init_trigraph

fin_digraph = [
    'ft', 'kt', 'lt', 'ld', 'lk', 'lp', 'lb', 'lf', 'lm', 'nt', 'nd', 'ns',
    'nz', 'nk', 'ng', 'ps', 'pt', 'sk', 'sp', 'st', 'rt', 'sh', 'th', 'ck',
    'gh', 'kh', 'ph', 'ch'
]
fin_trigraph = [
    'lph',
    'lch',
    'lge',
    'mph',
    'nch',
    'nj',
    'nct',
]
fin_consonant_clusters = fin_digraph + fin_trigraph

replace_list = {'oo': 'u', 'ee': 'i', 'ck': 'k'}


class ESyl:
    """Syllable class for toneless language"""

    def __init__(self, onset="", nucleus="", coda=""):
        self.o, self.n, self.c = onset, nucleus, coda
        self.prefix, self.suffix = "", ""

    def toString(self):
        return "".join([self.o, self.n, self.c])

    def size(self):
        return len(self.o) + len(self.n) + len(self.c)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               (True if other.o == '*' else self.o == other.o) and \
               (True if other.n == '*' else self.n == other.n) and \
               (True if other.c == '*' else self.c == other.c)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(repr(self))


class TSyl:
    """Syllable class for tonal language"""

    def __init__(self, onset="", nucleus="", coda="", tone=""):
        self.o, self.n, self.c, self.t = onset, nucleus, coda, tone

    def placeTone(self):
        if self.c == '':
            if self.n in [
                    'aai', 'aau', 'oi', 'oe', 'ai', 'au', 'iu', 'eu', 'e'
            ]:
                self.t = '1'
            elif self.n in ['yu', 'eoi']:
                self.t = '4'
            elif self.n == 'aa':
                if self.o in ['t', 'd']:
                    self.t = '2'
                else:
                    self.t = '1'
            elif self.n == 'ei':
                if self.o in ['d']:
                    self.t = '3'
                else:
                    self.t = '1'
            elif self.n == 'ou':
                if self.o in ['g', 's']:
                    self.t = '1'
                else:
                    self.t = '2'
            elif self.n == 'o':
                if self.o in ['h', 'l']:
                    self.t = '4'
                else:
                    self.t = '1'
            elif self.n == 'u':
                if self.o in ['f']:
                    self.t = '2'
                elif self.o in ['g']:
                    self.t = '4'
                else:
                    self.t = '1'
            elif self.n == 'i':
                if self.o in ['s', 'j']:
                    self.t = '6'
                else:
                    self.t = '1'
        elif self.c == 'n':
            if self.n in ['aa', 'eo', 'i']:
                if self.o in ['l']:
                    self.t = '4'
            elif self.n in ['a']:
                if self.o in ['m']:
                    self.t = '4'
            else:
                self.t = '1'
        elif self.c == 't':
            if self.n == 'a':
                if self.o in ['f']:
                    self.t = '6'
            else:
                self.t = '1'
        elif self.c == 'p':
            if self.n == 'i':
                if self.o in ['t']:
                    self.t = '3'
            else:
                self.t = '1'
        elif self.c == 'k':
            if self.n == 'i':
                if self.o in ['l']:
                    self.t = '6'
            else:
                self.t = '1'
        elif self.c == 'ng':
            if self.n == 'u':
                if self.o in ['l']:
                    self.t = '3'
            elif self.n == 'i':
                if self.o in ['l']:
                    self.t = '6'
            else:
                self.t = '1'
        elif self.c == 'm':
            self.t = '1'

        if len(self.t) == 0:
            self.t = '1'
        return self

    def toString(self):
        if self.t == '':
            self.placeTone()
        return " ".join([
            part for part in [self.o, self.n, self.c, self.t] if len(part) > 0
        ])

    def toStringToneless(self):
        return " ".join(
            [part for part in [self.o, self.n, self.c] if len(part) > 0])

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               (True if other.o == '*' else self.o == other.o) and \
               (True if other.n == '*' else self.n == other.n) and \
               (True if other.c == '*' else self.c == other.c) and \
               (True if other.t == '*' else self.t == other.t)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(repr(self))


def segmentation(word):
    """ Input: Word, Output: Sequence of vowel clusters and consonance clusters
    eg: Input = arsenal, Output = ['a', 'rs', 'e', 'n', 'a', 'l'] """
    vowel_cluster = ""
    consonant_cluster = ""
    clusters = []
    for c in word:
        if c == 'y':
            if len(consonant_cluster) > 0:
                clusters.append(consonant_cluster)
                consonant_cluster = ""
                clusters.append(c)
            else:
                clusters.append(vowel_cluster + c)
                vowel_cluster = ""
        elif c in vowels:
            if len(consonant_cluster) > 0:
                clusters.append(consonant_cluster)
                consonant_cluster = ""
            vowel_cluster += c
        else:
            if len(vowel_cluster) > 0:
                clusters.append(vowel_cluster)
                vowel_cluster = ""
            consonant_cluster += c
    if len(vowel_cluster) > 0:
        clusters.append(vowel_cluster)
        vowel_cluster = ""
    if len(consonant_cluster) > 0:
        clusters.append(consonant_cluster)
        consonant_cluster = ""
    return clusters


def syllable_split(word):
    clusters = segmentation(word)
    syl_seq = []
    fail_clusters = []
    if len(clusters) == 1:
        if clusters[0][0] == 'y' and len(clusters[0] > 1):
            syl_seq.append(ESyl(clusters[0][0], clusters[0][1:]))
        elif clusters[0][0] in vowels + ['y']:
            syl_seq.append(ESyl("", clusters[0]))
        else:
            syl_seq.append(ESyl(clusters[0]))
        return fail_clusters, syl_seq

    # Remove redundant character in doublet
    for i in range(len(clusters)):
        for doublet in ['ll', 'ff', 'dd', 'gg', 'ss', 'zz', 'rr', 'tt']:
            if doublet in clusters[i]:
                clusters[i] = clusters[i].replace(doublet, doublet[0])

    for i in range(len(clusters)):
        for k, v in list(replace_list.items()):
            if k in clusters[i]:
                clusters[i] = clusters[i].replace(k, v)

    for i in range(len(clusters)):
        # The first condition seems redundant.
        # The only time it is true is when the clusters is assigned as coda
        if len(clusters[i]) > 0 and (clusters[i][0] in vowels or (
                clusters[i] == 'y' and i > 0 and len(clusters[i - 1]) > 0)):
            syllable, clusters[i] = ESyl('', clusters[i], ''), ''
            """Pick out onset"""
            if 1 == i:
                syllable.o, clusters[i - 1] = clusters[i - 1], ''
            elif i > 0:  # Prevent out-of-bound error
                if len(clusters[i - 1]) == 1 or clusters[
                        i - 1] in init_consonant_clusters or clusters[
                            i - 1] == 'y':
                    syllable.o, clusters[i - 1] = clusters[i - 1], ''
                elif len(clusters[i - 1]) > 0:
                    # Couldn't pick up the preceeding consonants
                    # probably unresolved consonant clusters
                    syl_seq.append(ESyl(clusters[i - 1], "", ""))
                    fail_clusters.append(clusters[i - 1])
            """Pick out coda"""
            # If the vowel is at the penultimate position
            # just append the last consonant cluster to it.
            if i == len(clusters) - 2 and len(clusters[
                    i + 1]) > 0 and clusters[i + 1] not in vowels:
                syllable.c, clusters[i + 1] = clusters[i + 1], ''
            elif i < len(clusters) - 2:
                # Otherwise, if the following consonant cluster has 2 characters,
                # split it up unless it is an digraph
                if (2 == len(clusters[i + 1])) and (
                        clusters[i + 1] not in init_digraph):
                    syllable.c, clusters[i + 1] = clusters[i + 1][0], clusters[
                        i + 1][1]
                # Split the following consonant clusters if it has more than 2 characters
                elif len(clusters[i + 1]) > 2:
                    # and ends in one of the following clusters.
                    if clusters[i + 1].endswith(tuple(init_trigraph)):
                        syllable.c, clusters[i + 1] = clusters[
                            i + 1][:-3], clusters[i + 1][-3:]
                    elif clusters[i + 1].endswith(tuple(init_digraph)):
                        syllable.c, clusters[i + 1] = clusters[
                            i + 1][:-2], clusters[i + 1][-2:]
                    # or starts with one of the following clusters.
                    elif clusters[i + 1].startswith(tuple(fin_digraph)):
                        syllable.c, clusters[i + 1] = clusters[
                            i + 1][:2], clusters[i + 1][2:]
                    # desperation
                    else:
                        syllable.c, clusters[i + 1] = clusters[
                            i + 1][:-1], clusters[i + 1][-1]

            syl_seq.append(syllable)

    if len(syl_seq) > 1 and syl_seq[-1] in [ESyl('l', 'e', '')]:
        syl_seq[-1] = ESyl(syl_seq[-1].o, '', '')

    if (len(syl_seq) > 1 and len(syl_seq[-2].c) == 0 and
            len(syl_seq[-2].n) == 1 and syl_seq[-1] in [
                ESyl('n', 'e'), ESyl('k', 'e'), ESyl('d', 'e'), ESyl('b', 'e'),
                ESyl('z', 'e')
            ]):
        syl_seq[-2].n += syl_seq[-1].toString()
        del syl_seq[-1]

    for syl in syl_seq:
        if len(syl.c) > 0 and syl.c[0] in ['r', 'w']:
            syl.n += syl.c[0]
            syl.c = syl.c[1:]

    temp = []
    for i, s in enumerate(syl_seq):
        if len(s.c) > 1 and s.c[-2:] in ['st']:
            temp.extend([ESyl(s.o, s.n, s.c[:-2]), ESyl(s.c[-2:])])
        elif len(s.c) > 0 and s.c[-1] in ['z', 'v', 's']:
            temp.extend([ESyl(s.o, s.n, s.c[:-1]), ESyl(s.c[-1])])
        elif s.c in ['hn']:
            temp.extend([ESyl(s.o, s.n), ESyl(s.c)])
        elif s.c in ['h']:
            temp.extend([ESyl(s.o, s.n)])
        elif len(s.c) == 0 and s.n in ['io']:
            temp.extend([ESyl(s.o, s.n[0]), ESyl('', s.n[1])])
        elif s in [ESyl('m', 'e')] and i > 0 and temp[-1].c == '':
            temp[-1].c = s.o
        else:
            temp.append(s)
    syl_seq = temp

    word_copy = ''.join([syl.toString() for syl in syl_seq])
    pos = 0
    for syl in syl_seq:
        syl.prefix, syl.suffix = word_copy[0:pos], word_copy[pos + syl.size():]
        pos += syl.size()
    syl_seq[0].prefix, syl_seq[-1].suffix = "^", "$"
    return fail_clusters, syl_seq


def main(words):
    for word in words:
        fail, syl_seq = syllable_split(word)
        output = ' '.join([','.join([s.o, s.n, s.c]) for s in syl_seq])
        print(output)
        print("Failure:", len(fail), fail)
        for s in syl_seq:
            print('--', s.prefix, '[', ''.join([s.o, s.n, s.c]), ']', s.suffix)


if __name__ == '__main__':
    main(sys.argv[1:])
