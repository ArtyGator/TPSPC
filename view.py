import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter import ttk
from tkinter.font import nametofont
from math import ceil
from functools import partial
import re

DOT_RELSIZE = .6
CROSS_RELSIZE = DOT_RELSIZE / 2
COLORS_BY_GRADE = ('none', 'red', 'yellow', 'green', 'royalblue')
ALTERNANCE_COULEUR = lambda i: 'white' if i % 2 == 0 else 'azure'


class Labo(tk.Frame):
    def __init__(self, parent, liste_paillasses, callback, nb_rangees, padding):
        super().__init__(parent, bd=0, bg='powderblue')

        [self.columnconfigure(i, weight=1) for i in range(nb_rangees)]  # counting from 0
        [self.rowconfigure(i, weight=1) for i in range(ceil(len(liste_paillasses) / nb_rangees))]

        for pair_i, pair in enumerate(liste_paillasses):
            pail_frame = tk.Frame(self, relief='solid', bd=2)
            pail_frame.rowconfigure(0, weight=1)
            for eleve_i, nom_eleve in enumerate(pair):
                pail_frame.columnconfigure(eleve_i, weight=1)
                tk.Button(pail_frame, text=nom_eleve, command=partial(callback, nom_eleve),
                          anchor='center').grid(row=0, column=eleve_i, sticky=tk.NSEW, padx=0, ipadx=4,
                                                pady=0)
            pail_frame.grid(
                row=pair_i // nb_rangees, column=pair_i % nb_rangees, padx=padding, pady=padding,
                sticky=tk.NSEW)


class CompChooser(tk.Frame):
    def __init__(self, parent, liste_comp, close_cb, font_top, font_bottom, preset=None):
        super().__init__(parent, bd=3, relief='solid', bg='blue')
        self.comps = liste_comp
        if preset is not None:  # preset can be an iterator
            self.var_list = list(map(lambda b: tk.BooleanVar(self, b), preset))
        else:
            self.var_list = [tk.BooleanVar(self, True) for _ in liste_comp]
        self.close_callback = close_cb

        self.columnconfigure(0, weight=1)
        [self.rowconfigure(i) for i in range(len(liste_comp))]

        tk.Label(self, text='Choisir compétences à évaluer', font=font_top, bg='gainsboro', anchor='center',
                 ).grid(row=0,
                        column=0,
                        columnspan=2,
                        sticky=tk.NSEW)

        for i, nom_comp in enumerate(liste_comp):
            tk.Checkbutton(self, onvalue=True, offvalue=False, text=nom_comp, anchor=tk.W,
                           variable=self.var_list[i]).grid(column=0, row=i, sticky=tk.NSEW)

        tk.Button(self, text='Fermer', font=font_bottom, bg='gainsboro', command=self.on_close, anchor='e', padx=16,
                  pady=0, relief='groove').grid(row=len(liste_comp) + 1, column=0,
                                                sticky=tk.NSEW)

    def on_close(self):
        fl = self.get_filter()
        self.close_callback(list(filter(fl.__contains__, self.comps)))
        self.destroy()

    def get_filter(self):
        return set(
            map(self.comps.__getitem__, [i for i, e in enumerate(self.var_list) if e.get()])
        )


class Evaluator(tk.Frame):
    def __init__(self, parent, liste_comp_evaluees, comp_callback, font_top, font_bottom):
        super().__init__(parent, bd=3, relief='solid', bg='black')
        self.comp_canvas_list = []
        self.callback = comp_callback

        self.grid(row=0, column=0)  # this is a terrible practise normally but here we need measurements
        self.lower()

        [self.columnconfigure(i, weight=1) for i in range(2)]
        dot_half = DOT_RELSIZE / 2
        tk.Label(self, text='Nom élève', font=font_top, bg='gainsboro', anchor='center',
                 relief='flat').grid(row=0,
                                     column=0,
                                     columnspan=2,
                                     sticky=tk.NSEW)
        for i, nom_comp in enumerate(liste_comp_evaluees):
            self.rowconfigure(i + 1, weight=1)

            lbl = tk.Label(self, text=nom_comp, bg=ALTERNANCE_COULEUR(i), anchor='w', padx=8, pady=2)
            lbl.grid(row=i + 1, column=0, columnspan=1, sticky=tk.NSEW)
            lbl.update()
            line_height = lbl.winfo_height()

            can = tk.Canvas(self, bg=ALTERNANCE_COULEUR(i), borderwidth=0, relief="flat",
                            highlightthickness=0,
                            height=line_height, width=line_height * 4)
            can.grid(row=i + 1, column=1, sticky=tk.NS + tk.W)  # this sticky doesnt do anything
            can.update()
            b_y = can.winfo_y() - 4

            self.comp_canvas_list.append(can)
            self.line_height = line_height
            can.delete()
            for i_c, c in enumerate(COLORS_BY_GRADE[1:]):
                center_i = 0.5 + i_c
                eid = self.comp_canvas_list[i].create_oval((center_i - dot_half) * self.line_height,
                                                           (0.5 - dot_half) * self.line_height,
                                                           (center_i + dot_half) * self.line_height,
                                                           (0.5 + dot_half) * self.line_height,
                                                           fill=c, activeoutline='white',
                                                           outline=c, width=0)

                self.comp_canvas_list[i].tag_bind(eid, "<Button-1>", partial(comp_callback, i, i_c + 1))
            ttk.Separator(self, orient='horizontal').place(in_=self, relwidth=1., height=1,
                                                           y=b_y, x=0)

        n_competences = len(liste_comp_evaluees)
        self.rowconfigure(n_competences + 1, weight=1)
        tk.Button(self, text='Fermer', font=font_bottom, bg='gainsboro',
                  command=self.lower, anchor='e', padx=16, pady=0, relief='groove',
                  activebackground='white').grid(
            row=n_competences + 1, column=0, columnspan=2,
            sticky=tk.NSEW)
        self.cross_ids = [None] * n_competences

    def refresh_eval_crosses(self, current_eleve_competences):
        dot_half = CROSS_RELSIZE / 2

        for i, grade in enumerate(current_eleve_competences):
            self.comp_canvas_list[i].delete(self.cross_ids[i])
            if grade is None:
                continue
            center_i = 0.5 + grade - 1  # WARN: grade can be none
            eid = self.comp_canvas_list[i].create_oval((center_i - dot_half) * self.line_height,
                                                       (0.5 - dot_half) * self.line_height,
                                                       (center_i + dot_half) * self.line_height,
                                                       (0.5 + dot_half) * self.line_height,
                                                       fill='black', width=0)

            self.comp_canvas_list[i].tag_bind(eid, "<Button-1>", partial(self.callback, i, grade))
            self.cross_ids[i] = eid


class TPSPCApp(tk.Tk):
    def __init__(self, nb_paillasses, nb_rangees=2, font_size=13, padding=25, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nb_paillasses = nb_paillasses
        self.nb_rangees = nb_rangees
        self.padding = padding
        self.saved = None
        self.save_cb = None
        self.nom_current_eleve_eval = ""
        self.eval = None
        self.labo = None
        # self.liste_competences = []
        self.sceance_competences = {}  # dict (string hash) maps to lists, relation with the list of comp
        self.names_comps = []

        self.title("Attribution des places")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        default_font_options = nametofont("TkDefaultFont").actual()

        button_font = (default_font_options['family'], font_size)
        label_font = (default_font_options['family'], 15)
        self.other_fonts = ((default_font_options['family'], 14, "underline"),
                            (default_font_options['family'], 13, ""))

        self.option_add("*Button*font", button_font)
        self.option_add("*Label*font", label_font)
        self.option_add("*Checkbutton*font", label_font)
        self.option_add("*Checkbutton*borderwidth", 0)

        self.option_add("*Button*relief", "flat")
        self.option_add("*Label*relief", "flat")
        self.option_add("*Button*borderwidth", 0)
        self.option_add("*Takefocus", False)
        # self.bind('<Configure>', self.on_resize)
        self.bind('<Escape>', self.hide_evaluation_table)

    def load_eleves(self, liste_paillasses):
        self.labo = Labo(self, liste_paillasses, self.on_click_eleve, self.nb_rangees, self.padding)
        self.labo.grid(row=0, column=0, sticky=tk.NSEW)

    def choose_competences(self, toutes_comp, *load_opts, preset=None):

        def partial_f(liste_comps):
            self.load_competences(liste_comps, *load_opts)

        comp_chooser = CompChooser(self, toutes_comp, partial_f, *self.other_fonts, preset=preset)
        comp_chooser.grid(row=0, column=0)

    def load_competences(self, list_comp_evaluees, liste_eleves, save_callback):
        self.save_cb = save_callback
        self.names_comps = list_comp_evaluees  # need this to keep the name of comps for saving with main.py
        self.eval = Evaluator(self, list_comp_evaluees, self.on_click_competence, *self.other_fonts)

        for e in liste_eleves:
            self.sceance_competences[e] = [None for _ in list_comp_evaluees]

        self.protocol('WM_DELETE_WINDOW', self.close_callback)
        self.bind('<Control-s>', partial(self.save_callback, self))
        self.saved = True

    def evaluate_eleve(self, nom_eleve: str):
        self.nom_current_eleve_eval = nom_eleve
        self.eval.winfo_children()[0].configure(text=nom_eleve)
        self.refresh_eval_cross()
        self.eval.lift()

    def on_click_eleve(self, nom):
        self.evaluate_eleve(nom)

    def refresh_eval_cross(self):
        self.eval.refresh_eval_crosses(self.sceance_competences[self.nom_current_eleve_eval])

    def on_click_competence(self, i_competence, grade, event):
        if self.sceance_competences[self.nom_current_eleve_eval][i_competence] == grade:
            # we re-submitted the same grade
            self.sceance_competences[self.nom_current_eleve_eval][i_competence] = None  # reset the grade
        else:
            self.sceance_competences[self.nom_current_eleve_eval][i_competence] = grade
        self.saved = False
        self.refresh_eval_cross()

    def hide_evaluation_table(self, _=None):
        self.eval.lower()

    def save_callback(self):
        self.save_cb(self)
        self.saved = True

    def close_callback(self):
        if not self.saved:
            save = msgbox.askyesno('Sauvegarde', "Des données d'évaluation ont été saisies. Les sauvegarder ?")
            if save:
                code = self.save_cb(self)
                if code == 0:
                    pass
                if code == -1:
                    return
                else:
                    msgbox.showerror("Erreur", "Le fichier n'a pas pu être sauvegardé")
            elif save is None:
                return
        self.destroy()
