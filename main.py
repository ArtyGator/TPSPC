import choice
from logic import *
from view import TPSPCApp
import os, appdirs
import json

"""
Attribution automatique des places en TP
les variables en majuscules sont modifiables
pour être valides, les tableurs doivent contenir une compétence par colonne et un élève par ligne
les compétences évaluées peuvent difficilement changer d'une itération à l'autre

chaque colonne de ce tableur correspondra à une classe, et la première ligne contiendra le nom des classes
"""

# TODO: implementer la sélection de certaines compétences qui apparaîtront dans l'évaluateur
APP_VENDOR = "Dumont"
APP_NAME = "TPSPC"
NB_PAILLASSES = 9
FONT_SIZE = 17

if __name__ == '__main__':  # threaded failsafe
    config_dir = appdirs.user_config_dir(APP_NAME, APP_VENDOR, roaming=True)
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    conf_path = os.path.join(config_dir, 'config.json')
    conf = {}
    if os.path.isfile(conf_path):
        with open(conf_path, mode='r', encoding='utf-8') as f:
            conf = json.loads(f.read())
    else:
        conf.update(
            choice_path=None,
            last_org={},
            last_org_date={},
            last_tab_comp={}
        )

    def save_callback(instance: TPSPCApp, event=None):
        saver_file = choice.choice_file_save(conf['choice_path'], instance.winfo_toplevel())
        if saver_file != '':
            try:
                save_tab_comp(instance.sceance_competences, saver_file)
            except:
                return 2
            else:
                return 0
        else:
            return -1


    ins = TPSPCApp(9, 2, 15)

    fichier_classe = choice.choice_file_open(conf['choice_path'], ins.winfo_toplevel())
    # this is a cpu-blocking function that will crash your computer if you try to use threading on it
    liste_comp, liste_eleves = parse_tab_comp(fichier_classe)
    pairs = []
    mpreset = None
    c = False  # if the statement below doesn't change the state of the choice it will default to false
    if fichier_classe in conf['last_org']:
        c = choice.choice_load_previous(conf['last_org_date'][fichier_classe], ins.winfo_toplevel())
    if c:
        pairs = conf['last_org'][fichier_classe]
        mpreset = map(conf['last_tab_comp'][fichier_classe].__contains__, liste_comp)
    else:
        x, y = calculate_distribution(len(liste_eleves), 9, False, None)
        pairs = generate_pairs(liste_eleves, x, y)
    conf['last_org_date'][fichier_classe] = choice.dt.datetime.now().isoformat()

    ins.load_eleves(pairs)
    # ins.load_competences(liste_comp, liste_eleves, save_callback)
    ins.choose_competences(liste_comp, liste_eleves, save_callback, preset=mpreset)

    ins.mainloop()

    spl = os.path.split(fichier_classe)
    conf['choice_path'] = spl[len(spl) - 2]
    conf['last_org'][fichier_classe] = pairs
    conf['last_tab_comp'][fichier_classe] = ins.names_comps
    with open(conf_path, mode='w+', encoding='utf-8') as f:
        f.write(json.dumps(conf))

