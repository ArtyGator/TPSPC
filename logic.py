import pyexcel as p
import os
from math import ceil
from random import shuffle, randint
import time as t  # for profiling purpose


class NoneSafe(list):
    def __init__(self, nn_value, liste):
        self.nn = nn_value
        super().__init__(liste)

    def __getitem__(self, item):
        return self.nn if item is None else super().__getitem__(item)


LETTER_SEPARATOR = ', '
LETTERS_BY_GRADE = NoneSafe('', ['?', 'D', 'C', 'B', 'A'])


def chunks(lst, n):
    """
    Yields successive n-sized chunks from lst
    :param lst: input list
    :param n: size of chunks
    :return: chunks of data iterator
    """
    for i in range(0, len(lst), n):
        yield tuple(lst[i:i + n])


def greedy_combine(op, d, *l):
    max_len = max(map(len, l))
    l = map(lambda e: e + [d] * (max_len - len(e)), l)
    return map(op, zip(*l))


def parse_tab_comp(xl_path):
    sheet = p.iget_array(file_name=xl_path)
    liste_comp = next(sheet)[1:]
    liste_eleves = [row[0] for row in sheet]
    return liste_comp, liste_eleves


def save_tab_comp(comps_par_eleve: dict, xl_path):
    combinator = lambda i: ', '.join(filter(lambda e: e != '', i))
    # la liste d'élèves fournie doit être dans le même ordre dans que le fichier à modifier
    # les hashmap sont ordonnées dans python3.6+

    def transformer(g):
        # IMPORTANT here this does not work because the empty cells don't appear as empty strings, but shrink the row
        yield next(g)  # trust the already existing file ?
        for row in g:
            yield [row[0]] + list(greedy_combine(combinator, '', row[1:],
                                                 list(map(LETTERS_BY_GRADE.__getitem__, comps_par_eleve[row[0]]))))

    itab = p.iget_array(file_name=xl_path)
    # print(*transformer(itab), sep='\n')
    p.isave_as(array=transformer(itab), dest_file_name=xl_path)


def calculate_distribution(nb_eleves, nb_paillasses, can_extend=True, extent_limit=10):
    """
    | 2x + 3y = nb_eleves
    | x + y <= nb_paillasses
    :return: (nb_paillasses_de_2, nb_paillasses_de_3)
    """
    if nb_eleves > nb_paillasses * 3:
        if can_extend and nb_eleves <= extent_limit * 3:
            nb_paillasses = ceil(nb_eleves / 3)
        else:
            raise ValueError("nombre d'élèves trop élevé.")
    if nb_eleves <= nb_paillasses * 2:
        impair = int(nb_eleves % 2 != 0)
        x = nb_eleves // 2 - impair
        y = impair
    else:
        x = 3 * nb_paillasses - nb_eleves
        y = nb_eleves - 2 * nb_paillasses

    return x, y


def generate_pairs(liste_eleves, x, y):
    eleves = liste_eleves[:]  # slice pour copier liste_eleves
    shuffle(eleves)  # agit de manière à ce que liste_eleves ne soit pas impacté par la procédure
    paillasses = []  # liste qui contiendra des 2-uplet et des 3-uplets d'élèves
    paillasses += chunks(eleves[:2 * x], 2)  # slice pour séparer la liste, puis on la groupe
    paillasses += chunks(eleves[2 * x:], 3)

    shuffle(paillasses)  # mélange la distribution géographique des duos et des trios
    return paillasses

# print(parse_classes('classes/example.xlsx'))
