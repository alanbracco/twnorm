# from string import ascii_lowercase as lcase
import re
from oov_classifier import OOVclassifier


class PrimaryCandidates(object):

    def __init__(self, n):
        self.cf = OOVclassifier()
        self.n_errors = n

    def upper_lower(self, word):
        """
            return a set that contains
            lowercase word,
            uppercase word,
            titlecase word.
        """
        return {word.lower(), word.upper(), word.title()}

    def accent_mark(self, word):
        """
            return set of words
            related to accent marks confusion
        """
        n = len(word)
        restored = ''
        vowels = 'aeiou'
        m_vowels = 'áéíóú'
        # eliminate all accent marks
        for i in range(n):
            cl = word[i]  # current letter
            if cl in m_vowels:
                restored += vowels[m_vowels.index(cl)]
            else:
                restored += cl
        cands = {restored}  # word without accent marks, potential candidate
        # try with one accent mark for each vowel at a time
        for i in range(n):
            cl = restored[i]
            if cl in vowels:
                new = m_vowels[vowels.index(cl)]
                cands.add(restored[:i] + new + restored[i+1:])
        return cands

    def change_letters(self, word):
        """
            return set of words with
            one frequent letter confusion
            changed at a time
            contemplating if
            preserves pronunciation (except j/g sound)
        """
        candidates = set()
        # 1 for a o u next letter cases, 2 for e i next letter cases
        # 3 for c or s previous to h
        change = {'v': ['b'], 'b': ['v'], 'c1': ['k'], 'c2': ['s', 'z'],
                  's1': ['z'], 's2': ['c', 'z'], 'z1': ['s'], 'z2': ['c', 's'],
                  'll': ['y', 'sh'], 'y': ['ll', 'sh'], 'sh': ['ll', 'y'],
                  'x': ['ch'], 'h3': [''], 'k1': ['c'], 'k2': ['qu'],
                  'qu': ['k'], 'j': ['g'], 'g': ['j']}
        for i in range(len(word)-1):
            pair = word[i:i+2]  # pair of letters
            # get values of pair's first letter in "change dict"
            if not pair[1].isdigit():  # avoid if word contains c1, z2, etc
                key = pair[0]
                if key == 'h' and i > 0 and word[i-1] not in 'cs':
                    key += '3'
                elif key not in change.keys() and pair[1] in 'aou':
                    key += '1'
                elif key not in change.keys() and pair[1] in 'ei':
                    key += '2'
                for new in change.get(key, {}):
                    cand1 = word[:i] + new + word[i+1:]
                    candidates.add(cand1)
                # get values of pair in "change dict" (for 'll' and 'sh' cases)
                for new in change.get(pair, {}):
                    cand2 = word[:i] + new + word[i+2:]
                    candidates.add(cand2)
        return candidates

    def spelling_error(self, word, n):
        """
            execute change_letters n times
            on modified words
            and return all modified words
            (each execution of change_letters)
            n: number of errors to correct
        """
        all_cand = set()  # to store all candidates
        last_cand = {word}  # candidates of last change_letters loop
        for _ in range(n):
            last_tmp = set()  # collect cand generated with last_cand
            # for each "w" generated in last change_letters calls
            for w in last_cand:
                cand = self.change_letters(w)
                last_tmp = last_tmp.union(cand)
            all_cand = all_cand.union(last_tmp)
            last_cand = last_tmp
        return all_cand

    def char_rep(self, word):
        """
            return a list that contains (in given order)
            original word,
            word with no repetitions,
            word with two occurrences together max. (e.g. caassaa, caasaa)
        """
        no_rep = re.sub(r'(.)\1+', r'\1', word)  # no repetitions
        rep2 = re.sub(r'(.)\1+', r'\1\1', word)  # two occurrences max
        return [word, no_rep, rep2]

    def look_for_pattern(self, word):
        """
            return repetition pattern found if exists
            else return ''
        """
        result = ''
        regex = r"(\b([a-z]{2,}?)\2+\b)"
        pattern = re.findall(regex, word, re.X | re.I)
        if pattern != []:
            result = pattern[0][1]
        return result

    def onetwo_repetition(self, word):
        """
            return a set of variants of word
            with at most one (adjacent) letter repeated (e.g. holaa, hoola) and
            with at most two (adjacent) letter repeated (e.g. hoolaa, hholaa)
            Constraint: input word muts have two occurrences together max.
        """
        candidates = set()
        rep2_tmp = list(word)
        n = len(word)
        # replace adjacent repeated letters (second) for '-'
        for i in range(len(rep2_tmp) - 1):
            if rep2_tmp[i] == rep2_tmp[i+1]:
                rep2_tmp[i+1] = '-'
        # replace '-' for original (one and two at a time)
        for i in range(n - 1):
            if word[i] == word[i+1]:
                cand_list = rep2_tmp[:i] + [word[i]] + rep2_tmp[i:]
                # with adjacent letter repeated
                cand = ''.join(cand_list).replace('-', '')
                candidates.add(cand)
                # with two pairs repeated
                hyphens = [j for j in range(i, n - 1) if cand_list[j] == '-']
                for j in hyphens:
                    cand_list2 = cand_list[:j] + [word[j]] + cand_list[j:]
                    cand = ''.join(cand_list2).replace('-', '')
                    candidates.add(cand)
        return candidates

    def all_reps(self, word):
        """
            return a set of words that contains
            word, word with no rep., wor with two occurrences together max,
            patterns found and all combinations of one or two occurrences
            of adjacent letters.
        """
        reps = self.char_rep(word)
        result = {w for w in reps}
        # look for patterns in each word in reps
        for w in reps:
            patt = self.look_for_pattern(w)
            if patt != '':
                result.add(patt)
        # reps[2] is word with two occurrences together max.
        onetwo = self.onetwo_repetition(reps[2])
        for w in onetwo:
            result.add(w)
        return result

    def filter_candidates(self, cands):
        """
            return set of IV candidates
        """
        candidates = set()
        cf = self.cf
        for w in cands:
            if w in cf.ND.keys():
                candidates.add(cf.ND[w])
            if cf.check(w):
                candidates.add(w)
        return candidates

    def generate(self, word):
        """
            return a set of primary candidates
        """
        b, cands, candidates = set(), set(), set()
        if word != '':
            reps = self.all_reps(word)
            for wd in reps:
                cands.add(wd)
                accent_mark = self.accent_mark(wd)
                b = b.union(accent_mark)
                cands = cands.union(accent_mark)
                for ww in b:
                    spelling_error = self.spelling_error(ww, self.n_errors)
                    cands = cands.union(spelling_error)
            # filter cands_tmp (only leaves correct words)
            cands = self.filter_candidates(cands)
            for c in cands:
                candidates = candidates.union(self.upper_lower(c))
            candidates = self.filter_candidates(candidates)

        return candidates


class SecondaryCandidates(object):
    def __init__(self):
        self.helper = PrimaryCandidates(2)
        self.cf = self.helper.cf

    def edit_distance(self, word):
        candidates = set()
        cf = self.cf
        n = len(word)
        abc = 'abcdefghijklmnñopqrstuvwxyzáéíóú'
        # abc = lcase[:14] + 'ñ' + lcase[14:] + 'áéíóú'
        if n > 1:
            for i in range(n):
                # delete i-th letter
                cand = word[:i] + word[i+1:]
                if cf.check(cand):
                    candidates.add(cand)
                # swap i-th letter for i+1-th letter
                if i > 0:
                    swap = word[i] + word[i-1]
                    cand = word[:i-1] + swap + word[i+1:]
                    if cf.check(cand):
                        candidates.add(cand)
                for x in abc:
                    # replace i-th letter for x
                    cand = word[:i] + x + word[i+1:]
                    if cf.check(cand):
                        candidates.add(cand)
                    # insert x in i-th position
                    cand = word[:i] + x + word[i:]
                    if cf.check(cand):
                        candidates.add(cand)
        for x in abc:
            # insert x at the end of word
            cand1, cand2 = word + x, x + word
            for cand in [cand1, cand2]:
                if cf.check(cand):
                    candidates.add(cand)
        return candidates

    def generate(self, word):
        """
            return a set of secondary candidates
        """
        candidates = set()
        if word != '':
            helper = self.helper
            cands = set()
            # edit distance over result of all_reps
            # to catch cases like e.g. "corrriend" -> "corriendo"
            for w in helper.all_reps(word):
                cands = cands.union(self.edit_distance(w))
            candidates = helper.filter_candidates(cands)
        return candidates


if __name__ == '__main__':
    a = PrimaryCandidates(2)
    inp = input("Enter a word: ")
    p = a.generate(inp)
    if p == set():
        b = SecondaryCandidates()
        s = b.generate(inp)
        print("Second:", s)
    else:
        print("Primary:", p)
