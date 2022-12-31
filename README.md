# TPSPC

Logiciel de répartition et d'évaluation des élèves en TP de physique-chimie

## Description

Ce logiciel a été créé pour deux enseignants de physique-chimie afin de faciliter l'évaluation des compétences et l'organisation lors des TP. Il remplit essentiellement deux fonctions :
- La répartition aléatoire des élèves en binômes ou trinômes (en fonction du nombre de paillasses disponibles), créant un plan qui peut être projeté au début du cours
- La notation des élèves en fonction de compétences définies en amont, qui peut être exporté sous forme de tableur

## Installation

Bien que je n'ai pas prévu ce programme pour le grand public, il est tout à fait possible d'y apporter des modifications de le faire tourner si vous êtes vous-même enseignant ou tout simplement curieux.

Vous aurez besoin de Python 3.5+ avec Tcl/Tk et d'un environnement venv ou anaconda fonctionnel.

ensuite, il vous suffira de lancer

    $ pip install -r requirements.txt

pour installer les composants nécessaires.

Le programme lit la liste d'élèves et de compétences depuis un tableur excel dans le style de ceux que l'on trouve dans `classes` (qui peut ne pas être vierge). Au moment de l'exportation, l'évaluation des compétences effectuées sera simplement ajoutée à la fin de chaque cellule. Il n'est donc pas nécessaire de créer une feuille d'évaluation par scéance.

Il est une bonne pratique de mettre dans ce tableur _toutes_ les compétences que vous pourriez être amené à évaluer. Le modifier ne devrait normalement pas poser problème au moment de la lecture, c'est simplement qu'une interface est pérvue au lancement du programme pour sélectionner les compétences que vous évaluerez.

Vous pourriez vouloir garder la même répartition de paillasses d'une scéance à l'autre. C'est pourquoi le programme se souviendra de la dernière répartition et vous proposera de la rétablir. En revanche, l'évaluation des compétences ne sera pas conservée. Vos modifications seront perdues si vous n'enregistrez pas à la fermeture. Si vous souhaitez évaluer des compétences sur plusieurs scéances, enregistrez simplement le fichier à la fin de chaque scéance. Comme l'exportation conserve les compétences précédentes, rien ne sera perdu.

## Limites connues

Le programme n'affiche pas encore parfaitement les binômes de plusieurs élèves s'ils ont des noms très longs. Si vous remarquez ce problème, il peut être judicieux d'abréger ceux-ci dans le tableur pour des raisons de lisibilité.

Le processus d'importation puis d'exportation du tableur ne conserve pas le style de ce dernier : si vous modifiez la largeur des colonnes, ou que vous faites des modifications estéthiques, celles-ci ne seront probablement pas conservées.

Il n'y a pas la possiblité de choisir les binômes qu'on souhaite ne pas voir se former (bien que cet ajout m'ait été suggéré à l'époque). Par un souci d'éthique, la répartition est purement aléatoire. Si ceci pose problème, vous pouvez éditer la fonction de répartition afin d'éviter ces cas particuliers.
