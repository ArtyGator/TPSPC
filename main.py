import choice
from logic import *
from view import TPSPCApp
import os, sys, appdirs
import json
import datetime as dt

"""
Attribution automatique des places en TP
les variables en majuscules sont modifiables
pour être valides, les tableurs doivent contenir une compétence par colonne et un élève par ligne
les compétences évaluées peuvent difficilement changer d'une itération à l'autre

chaque colonne de ce tableur correspondra à une classe, et la première ligne contiendra le nom des classes
"""

APP_VENDOR = "Dumont"
APP_NAME = "TPSPC"
NB_PAILLASSES = 9
FONT_SIZE = 24
DT = False

if __name__ == '__main__':
    # va chercher les fichiers locaux de configuration, en les créant si nécessaire
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
            last_tab_comp={},
            geometry=''
        )

    def save_callback(instance: TPSPCApp, event=None):
        saver_file = choice.choice_file_save(conf['choice_path'], instance.winfo_toplevel())  # demande où enregistrer
        if saver_file != '':
            try:
                save_tab_comp(instance.sceance_competences, saver_file)
            except Exception as e:
                print(e)
                return 2
            else:
                return 0
        else:
            return -1


    ins = TPSPCApp(9, 2, FONT_SIZE)

    fichier_classe = choice.choice_file_open(conf['choice_path'], ins.winfo_toplevel())
    if fichier_classe == '':
        sys.exit(0)
    # cette fonction est cpu-bloquante, ne pas essayer de la lancer dans un thread
    liste_comp, liste_eleves = parse_tab_comp(fichier_classe)
    pairs = []
    mpreset = None
    keep_org = False
    if fichier_classe in conf['last_org']:
        # demande s'il faut remettre le dernier plan de classe
        keep_org = choice.choice_load_previous(conf['last_org_date'][fichier_classe], ins.winfo_toplevel())
    if keep_org:
        pairs = conf['last_org'][fichier_classe]
        mpreset = map(conf['last_tab_comp'][fichier_classe].__contains__, liste_comp)
    else:
        x, y = calculate_distribution(len(liste_eleves), 9, False, None)
        pairs = generate_pairs(liste_eleves, x, y)
    conf['last_org_date'][fichier_classe] = choice.dt.datetime.now().isoformat()

    ins.load_eleves(pairs)

    ins.choose_competences(liste_comp, liste_eleves, save_callback, preset=mpreset)

    today = dt.date.today()
    if today.day == 1 and today.month == 4 and today.year == 2022:
        now = dt.datetime.now()
        if now.hour == 14 and (45 <= now.minute <= 55) and not DT:
            ins.labo.after(1000, ins.labo.do_a_little_trolling)  # HEHEHEHE

    ins.mainloop()

    # une fois sorti de l'app, on sauvegarde la config
    spl = os.path.split(fichier_classe)
    conf['choice_path'] = spl[len(spl) - 2]
    conf['last_org'][fichier_classe] = pairs
    conf['last_tab_comp'][fichier_classe] = ins.names_comps
    with open(conf_path, mode='w+', encoding='utf-8') as f:
        f.write(json.dumps(conf))

