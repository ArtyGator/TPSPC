import pyexcel as p
import os
from math import ceil
from random import shuffle, randint
import time as t  # for profiling purpose


class NoneSafe(list):
    """
    Liste particulière à laquelle on peut demander l'élément "None"
    """
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
    """
    Applique une fonction op à plusieurs listes en les combinant rang par rang et en comblant la longueur de celles
    trop petites
    :param op: Fonction à appliquer aux p-uplets
    :param d: élément par défaut pour le remplissage des listes trop petites
    :param l: une ou plus listes qui seront combinées ensemble, rang par rang.
    """
    max_len = max(map(len, l))
    l = map(lambda e: e + [d] * (max_len - len(e)), l)
    return map(op, zip(*l))


def parse_tab_comp(xl_path):
    sheet = p.iget_array(file_name=xl_path)
    liste_comp = next(sheet)[1:]  # sauter la légende
    liste_eleves = [row[0] for row in sheet]
    return liste_comp, liste_eleves


def save_tab_comp(comps_par_eleve: dict, xl_path):
    combinator = lambda i: ', '.join(filter(lambda e: e != '', i))
    # la liste d'élèves fournie doit être dans le même ordre dans que le fichier à modifier
    # les hashmap sont ordonnées dans python3.6+

    def transformer(g):
        # attention : pour le parser, les cellules vides n'apparaissent pas, pas même sous forme de chaînes vides
        yield next(g)  # sauter la légende
        for row in g:
            yield [row[0]] + list(greedy_combine(combinator, '', row[1:],
                                                 list(map(LETTERS_BY_GRADE.__getitem__, comps_par_eleve[row[0]]))))

    itab = p.iget_array(file_name=xl_path)
    # print(*transformer(itab), sep='\n')
    p.isave_as(array=transformer(itab), dest_file_name=xl_path)


def calculate_distribution(nb_eleves, nb_paillasses, can_extend=True, extent_limit=10):
    """
    x et y sont respectivement le nombre de duos et de trios
    cette fonction résout le système :
      2x + 3y = nb_eleves
      x + y <= nb_paillasses
    :return: (nb_paillasses_de_2, nb_paillasses_de_3)
    """
    if nb_eleves > nb_paillasses * 3:
        if can_extend and nb_eleves <= extent_limit * 3:
            nb_paillasses = ceil(nb_eleves / 3)
        else:
            raise ValueError("nombre d'élèves trop élevé")
    if nb_eleves <= nb_paillasses * 2:
        impair = int(nb_eleves % 2 != 0)
        x = nb_eleves // 2 - impair
        y = impair
    else:
        x = 3 * nb_paillasses - nb_eleves
        y = nb_eleves - 2 * nb_paillasses

    return x, y


def generate_pairs(liste_eleves, x, y):
    eleves = liste_eleves[:]  # on fait une copie de liste_eleves de manière à ne pas l'impacter en mélangeant
    shuffle(eleves)
    paillasses = []  # liste qui contiendra des 2-uplet et des 3-uplets d'élèves
    paillasses += chunks(eleves[:2 * x], 2)  # on sépare la liste, puis on la regroupe
    paillasses += chunks(eleves[2 * x:], 3)

    shuffle(paillasses)  # mélange la distribution géographique des duos et des trios
    return paillasses

