# -*- coding: utf-8 -*-
"""
OBSERVATOIRE DU TOURISME SUR INTERNET

CONTEXTE :
Un outil a été développé pour collecter de la donnée et pour nettoyer cette 
donnée
L’outil de restitution implique des tâches manuelles très chronophages

OBJECTIFS :
Automatiser la production des livrables décrits dans cette expression de
besoins
Donner accès direct aux clients, à leur espace, à leurs analyses, sur internet
"""

import pandas as pd
from datetime import timedelta, datetime

def traitements_informations(fichier):
    """ Fonction de retraitement des informations situées dans le fichier.
    Elle permet de modifier le format de la date, de remplacer les "," en "."
    pour permettre de le mettre dans le format attendu pour effectuer des 
    opérations.
    """
    lecture_fichier = pd.read_csv(fichier, sep=";", encoding="latin-1")

    def remplacement_virgule(valeur):
        n_valeur = str(valeur)
        n_valeur = n_valeur.replace(",", ".")

        return float(n_valeur)

    colonnes = lecture_fichier.columns

    for colonne in colonnes[1:]:
        lecture_fichier[colonne] = lecture_fichier[colonne].apply(
                                                        remplacement_virgule)

    lecture_fichier[colonnes[0]] = pd.to_datetime(lecture_fichier[colonnes[0]],
                                                    format="%Y-%m-%d")
    
    return lecture_fichier


def moyenne_variation(fichier, nb_semaine):
    """ Fonction permettant de calculer la moyenne des variations sur X 
    semaines
    Pour la calculer, la formule est la suivante:
    ((Va - Vd) / Vd) * 100
    Va : Valeur d'arrivée (semaine actuelle)
    Vd : Valeur de départ (semaine -1)
    
    Exemple: Si on veut la moyenne de variation sur 2 semaines
    semaine actuelle étant le 12/06/2021 de valeur 12 et la semaine d'avant, 
    le 11/06/2021 de valeur 9, le calcul sera :
        ((12 - 9)) / 9 ) * 100 => 33.3
    La moyenne de variation est donc de 33.3 %
    """
    variation = pd.DataFrame()
    colonnes = list(fichier.columns)
    semaines = list(fichier[colonnes[0]])
    for semaine in range(1, nb_semaine + 1):
        assemblage = pd.DataFrame()
        semaine_comparer = semaines[-semaine]
        semaine_avant = semaine_comparer - timedelta(7)
        filtre = fichier[(fichier[colonnes[0]] >= semaine_avant) &
                         (fichier[colonnes[0]] <= semaine_comparer)]
        reindex_filtre = filtre.reset_index(drop=True)
        nom_colonne = str(reindex_filtre.iloc[1,0])[:10] + "/" 
        nom_colonne += str(reindex_filtre.iloc[0,0])[:10]
        
        assemblage[nom_colonne] = ((reindex_filtre.iloc[1,1:] - 
                                    reindex_filtre.iloc[0,1:]) / 
                                   reindex_filtre.iloc[0,1:]) * 100

        variation = pd.concat([variation, assemblage], axis=1)
        
    return variation.T

####-###-###-###-###-###-###-###-###-GENERIQUE-###-###-###-###-###-###-###-###
def generique_variation(fichier):
    """ Fonction permettant de retourner le volume de variation (%) sur un 
    nombre de semaines données en paramètre de la fonction.
    
    Exemple:
        tableau variation pour 4 semaines:
                                        DE       BE       CH    ...
            2021-05-30/2021-05-23  22.2222 -25.9192  83.3333    ...
            2021-05-23/2021-05-16        0     37.5      -20    ...
            2021-05-16/2021-05-09  28.5714  71.4286  28.5714    ...
            2021-05-09/2021-05-02  16.6667      -30 -27.0833    ...
    """
    # Appel de la fonction de la moyenne de variation pour 4 semaines
    variation = moyenne_variation(fichier, 4)
    # Arrondie à 1 chiffre après la virgule
    variation = variation.round(1)
    
    return variation


def generique_volume(fichier):
    """ Fonction permettant de retourner un tableau
    contenant les moyennes des valeurs brutes des 2 dernières semaines.
    
    Exemple:
        tableau Volumes brutes:
                Paris    DE    BE    CH    ES     FR    IT    NL   GB    US
            2021-05-23   9.0  49.5  18.0  18.0  229.5  21.0  27.0  8.0   9.0
            2021-05-30  11.0  36.7  33.0  18.3  201.7  32.0  27.0  8.0  10.0  
    """
    objet = list(fichier.columns)
    # Remet l'index du tableau par défault et suppréssion de la nouvelle
    # colonne crée appelée "index"
    volume_brutes = fichier.tail(2).reset_index().drop(["index"], axis=1)
    # Le but étant via la variable "objet" (variable contenant toutes les 
    # colonnes) de pouvoir dire "Récupération de toute les colonnes sauf la 
    # premiere et arrondir à 1 chiifre après la virgule"
    volume_brutes[objet[1:]] = volume_brutes[objet[1:]].round(1)
    volume_brutes[objet[0]] = volume_brutes[objet[0]].astype(str)
    
    return volume_brutes


def generique_potentiel(variation, valeurs_brutes):
    """ Le principe étant d'avoir un tableau similaire à celui qui est dans
    le fichier cvs, d'avoir dans le tableau, une colonne des moyennes des 2
    semaines ainsi qu'une colonnes des moyennes sur la totalité des 4 semaines.
    """
    variation = variation.astype(float)
    recapitulatif = pd.DataFrame()
    # Récupération des 2 dernières semaines situées dans le tableau
    deux_semaines = variation.head(2)
    recapitulatif["2 semaines"] = deux_semaines.mean()
    recapitulatif["taille"] = valeurs_brutes.mean()
    recapitulatif["Top POTENTIEL"] = (recapitulatif["2 semaines"] * 
                                      recapitulatif["taille"]) / 100
    
    """ le principe étant de sortir un tableau regroupant:
        - top volume : les 3 plus grosses valeurs brutes 
            (en moyenne sur la période)
        - top progression : les 3 variations les plus fortes 
            (en moyennes sur la période)
        - top potentiel : les 3 plus gros produit VOLUME X PROGRESSION 
            (en moyenne sur la période)
    """
    tops = {"top Volume": [],
           "top Progression": [],
           "Top Potentiel": []}
    
    # Récupération des tops 3 pour chaque top
    top_progression = list(recapitulatif.sort_values(by=["2 semaines"], 
                                                ascending=False).head(3).index)
    top_volume = list(recapitulatif.sort_values(by=["taille"], 
                                                ascending=False).head(3).index)
    top_potentiel = list(recapitulatif.sort_values(by=["Top POTENTIEL"], 
                                                ascending=False).head(3).index)
    
    def nettoyage_str(x):
        """ Fonction qui permet de remplacer les "[" ainsi que les "]"
        pour avoir un tableau identique à celui du pdf du client
        """
        x = str(x)
        if "[" and "]" in x:
            x = x.replace("[", "").replace("]", "")
        return x

    tops["top Volume"].append(top_progression)
    tops["top Progression"].append(top_volume)
    tops["Top Potentiel"].append(top_potentiel)
    colonnes = list(tops.keys())
    tops_3_pays = pd.DataFrame(tops, columns=colonnes)
    
    for nom in colonnes:
        tops_3_pays[nom] = tops_3_pays[nom].apply(nettoyage_str)    

    return tops_3_pays


###-###-###-###-###-###-###-###-PAR-PAYS###-###-###-###-###-###-###-###-###-##
def sommes_periode_choisie(fichier, periode):
    """ Fonction permettant de ressortir un tableau de la somme des valeurs 
    sous 12 semaines en fonction d'une période donnée (en format datetime) et 
    du tableau du fichier excel.
    Exemple:
        période = datetime(2021, 3, 1)
        
        Résultat:
                                                   2021-02-21/2021-02-28  ...
        Tahiti (PF)                                                   38  ...                    
        Guadeloupe (GP)                                            49.69  ...    
        Martinique (LC)                                            64.31  ...    
        Réunion (RE)                                              140.31  ...      
        Guyane (GF)                                                    0  ...        
        St Barthélémy (BL)                                            13  ...        
        Mayotte (YT)                                                  38  ...      
        Saint Martin (ile d Amérique du nord) (MF)                     0  ...      
        Nouvelle Caledonie (NC)                                        0  ...      
    """

    colonnes = list(fichier.columns)
    fichier = fichier[fichier[colonnes[0]] <= periode]
    sommes_donnees = pd.DataFrame()
    semaines = list(fichier[colonnes[0]])
    
    for semaine in range(1, 12 + 1):
        assemblage = pd.DataFrame()
        semaine_comparer = semaines[-semaine]
        semaine_avant = semaine_comparer - timedelta(7)
        filtre = fichier[(fichier[colonnes[0]] >= semaine_avant) &
                         (fichier[colonnes[0]] <= semaine_comparer)]
        
        reindex_filtre = filtre.reset_index(drop=True)
        nom_colonne = str(reindex_filtre.iloc[0,0])[:10] + "/" 
        nom_colonne += str(reindex_filtre.iloc[1,0])[:10]
        
        assemblage[nom_colonne] = reindex_filtre.iloc[1,1:] + reindex_filtre.iloc[0,1:]

        sommes_donnees = pd.concat([sommes_donnees, assemblage], axis=1)

    sommes_donnees = sommes_donnees.astype(float).T

    return sommes_donnees    


def moyenne_donnees_brutes(sommes_donnees):
    """ Fonction ressortant 3 tableaux.
    Les tops pays sur les moyenne des données brutes sur 
    - les 2 dernières semaines, 
    - les 4 dernières semaines, 
    - les 12 dernières semaines 
    => en fonction de la période qu’on veut observer
    """
    semaines_2S = sommes_donnees.head(2).mean()
    semaines_4S = sommes_donnees.head(4).mean()
    semaines_12S = sommes_donnees.mean()
    recapitualitf_2s = pd.DataFrame()
    recapitualitf_4s = pd.DataFrame()
    recapitualitf_12s = pd.DataFrame()
    recapitualitf_2s["TOP 2 SEMAINES"] = semaines_2S
    recapitualitf_4s["TOP 4 SEMAINES"] = semaines_4S
    recapitualitf_12s["TOP 12 SEMAINES"] = semaines_12S

    recap_desc_2s = recapitualitf_2s.sort_values(
        by="TOP 2 SEMAINES", 
        ascending=False)
    
    recap_desc_4s = recapitualitf_4s.sort_values(
        by="TOP 4 SEMAINES", 
        ascending=False)
    
    recap_desc_12s = recapitualitf_12s.sort_values(
        by="TOP 12 SEMAINES", 
        ascending=False)

    return recap_desc_2s, recap_desc_4s, recap_desc_12s


def tops_pays(recapitualif_x_semaines, fichier, str_top_semaine):
    """ Fonction retournant un tableau du top 3 des pays ayant le plus gros
    Volume, d'un top 3 des pays ayant le plus haut top de progression ainsi
    qu'un top 3 des pays ayant le plus de potentiel
    Exemple:
        top Volume       top Progression        Top Potentiel
    0  'FR', 'BE', 'NL'  'CH', 'IT', 'NL'  'IT', 'CH', 'NL'
    
    recapitualif_x_semaines étant le récapitulatif du nombre de semaine
    exemple: recap_desc_2s 
    et le top_semaine étant le nom de la colonne 
    en string
    exemple: "TOP 2 SEMAINES"
    """
    top = {"top Volume": [],
           "top Progression": [],
           "Top Potentiel": []} 
    
    recapitualif_x_semaines = recapitualif_x_semaines.sort_index()
    recapitualif_x_semaines.fillna(0, inplace=True)
    variation = (moyenne_variation(fichier, 1).T).sort_index()
    variation.fillna(0, inplace=True)
    concat_tableau = pd.concat([variation, recapitualif_x_semaines], axis=1)
    top_volume = recapitualif_x_semaines.head(3).index.to_list()
    top_progression = variation.sort_values(by=list(variation.columns), 
                                            ascending=False).head(3).index.to_list()
    
    concat_tableau["potentiel"] = concat_tableau[list(concat_tableau.columns)[0]]*concat_tableau[str_top_semaine]
    top_potentiel = list(concat_tableau.sort_values(by=["potentiel"]).head(3).index)
    
    def nettoyage_str(x):
        """ Fonction qui permet de remplacer les "[" ainsi que les "]"
        pour avoir un tableau identique à celui du pdf du client
        """
        x = str(x)
        if "[" and "]" in x:
            x = x.replace("[", "").replace("]", "")
        return x

    top["top Volume"].append(top_volume)
    top["top Progression"].append(top_progression)
    top["Top Potentiel"].append(top_potentiel)
    colonnes = list(top.keys())
    top_3_pays = pd.DataFrame(top, columns=colonnes)
    
    for nom in colonnes:
        top_3_pays[nom] = top_3_pays[nom].apply(nettoyage_str)    
    
    return top_3_pays


def evolutions_sum_annees(fichier, annee):
    """ Fonction retournant un tableau les valeurs brutes
    des 3 dernieres année.
    """
    evolution_annee = pd.DataFrame()
    for i in range(0,4):
        N = fichier["Semaine"].map(lambda x: x.year) == annee - i
        tableau_annee = fichier[N]
        evolution_annee = pd.concat([evolution_annee, tableau_annee])
    
    def index_annee(x):
        x = str(x)[:4]
        return x
    
    evolution_annee["annee"] = evolution_annee["Semaine"].apply(index_annee)
    evolution_annee = evolution_annee.reset_index()
    evolution_annee.drop(["index", "Semaine"], axis=1, inplace=True)
    colonne_voulu = list(evolution_annee.columns)[::-1]
    evolution_annee = evolution_annee[colonne_voulu]
    
    return evolution_annee


def valeurs_brutes_3annees(fichier, mois, annee):
    """ Fonction retournant un tableau de la sommes des valeurs des pays 
    en fonction du mois et des 3 dernières années à partir de l'argument
    année de la fonction.
    Exemple pour le mois 2 et l'année 2021 :
               Tahiti (PF)  ...  Nouvelle Caledonie (NC)
        annee               ...                         
        2019         215.0  ...                      0.0
        2020         127.0  ...                     25.0
        2021          76.0  ...                      0.0
    """
    tableau_date = pd.DataFrame()
    
    for i in range(0,4):
        mois_map = fichier["Semaine"].map(lambda x: x.month) == mois
        tableau_mois = fichier[mois_map]
        annee_map = tableau_mois["Semaine"].map(lambda x: x.year) == annee-i
        tableau_annee_mois = tableau_mois[annee_map]
        tableau_date = pd.concat([tableau_date, tableau_annee_mois])

    def index_annee(x):
        x = str(x)[:4]
        return x
    
    tableau_date["annee"] = tableau_date["Semaine"].apply(index_annee)
    tableau_brut = tableau_date.groupby("annee").sum()
    
    return tableau_brut


def semaines_evolution_volume(fichier, periode):
    """ Fonction permettant de récupérer 4 semaines (S / S-1 et S-1 / S-2)
    et de calculer les variations sur une période donnée
    Exemple:
        les 4 semaines a partir du 2021-3-21
    retourne un tableau
    """
    colonnes = list(fichier.columns)
    fichier = fichier[fichier[colonnes[0]] <= periode]
    variation = moyenne_variation(fichier,4)
    variation.fillna(0, inplace=True)
    
    return variation


if __name__ == "__main__":
    csv_generique = r"C:/Users/ristarz/Desktop/tourisme2/GÉNÉRIQUES/CSV/DE-IT-NL-GB-US-BE-CH-ES-FR_Generique-Paris-Hebdo_20210607_1049.csv"
    csv_pays = r"C:/Users/ristarz/Desktop/tourisme2/PAR PAYS/CSV/BE_ATF-Montagne-Mensuel_mensuel_20210607_1048.csv"
    fichier = traitements_informations(csv_generique)
