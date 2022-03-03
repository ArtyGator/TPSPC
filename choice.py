import os
import datetime as dt
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import filedialog as tkfd
from tkinter import simpledialog
from functools import partial
from logic import NoneSafe

WEEK_DAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
MONTHS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre',
          'Décembre']
CHOICES = NoneSafe(None, [True, False])


class ModernSimpleDialog(simpledialog.Dialog):
    def __init__(self, parent, title, text, buttons: list, default=0):
        self.text = text
        self.buttons = buttons
        self.btn_default = default
        self.pressed = None
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text=self.text).pack()
        return master

    def button_pressed(self, index, _=None):
        self.pressed = index
        self.destroy()

    def buttonbox(self):
        for i, btn_text in enumerate(self.buttons):
            ttk.Button(self, text=btn_text, command=partial(self.button_pressed, i)).pack(side='right')

        self.bind("<Return>", partial(self.button_pressed, self.btn_default))

    def go(self):
        return self.pressed
    # @classmethod
    # def go(cls, parent, title, text, buttons: list, default=0):
    #     d = cls(parent, title, text, buttons, default)
    #     d.mainloop()
    #     return d.pressed


def choice_load_previous(timestamp, invoker_window: tk.Toplevel):
    date = dt.datetime.fromisoformat(timestamp)
    d = ModernSimpleDialog(invoker_window, 'Plan de classe',
                           f"Un plan de classe datant de {WEEK_DAYS[date.weekday()]} {date.day} {MONTHS[date.month]} {date.year} à {date.strftime('%H:%M')} a été trouvé. Le charger ?",
                           [
                               "Charger",
                               "Générer un nouveau"
                           ], default=0)
    return CHOICES[d.go()]


def choice_file_open(starting_dir, invoker_window: tk.Toplevel):
    file_path = tkfd.askopenfilename(parent=invoker_window, filetypes=[("Classeur excel", '*.xlsx')],
                                     initialdir=starting_dir, title="Ouvrir une classe")
    return file_path


def choice_file_save(starting_dir, invoker_window: tk.Toplevel):
    file_path = tkfd.asksaveasfilename(parent=invoker_window, filetypes=[("Classeur excel", '*.xlsx')],
                                       initialdir=starting_dir, title="Sauvegarder les résultats",
                                       confirmoverwrite=False, defaultextension='.xlsx')
    return file_path


def choice_window(choices, wn_title=None, font_size=12):
    window = tk.Tk()
    window.title = wn_title

    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=font_size)  # modifie la taille de police par défaut
    window.option_add("*Font", default_font)

    if wn_title is not None:
        window.title = wn_title
    final_choice = None

    def quit_choiced(choiced):
        nonlocal final_choice
        final_choice = choiced
        window.destroy()

    for choice in choices:
        tk.Button(window, text=choice, command=partial(quit_choiced, choice)).pack(side='bottom', fill='x', ipadx=5,
                                                                                   ipady=5)

    window.mainloop()
    return final_choice
