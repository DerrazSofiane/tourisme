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


def generique_variation_valeur_brutes(fichier):
    # TODO voir pour la concatenation et voir les répercutions
    # Attention, si je mets cette colonnes, je vais devoir retravailler
    # la fonction au dessus pour la calcul vu que c'est un string
    #fichier["Objet"] = list(fichier.columns)[0]
    objet = list(fichier.columns)
    variation = moyenne_variation(fichier, 4)
    variation = variation.round(1)
    valeurs_brutes = fichier.tail(2).reset_index().drop(["index"], axis=1)
    valeurs_brutes[objet[1:]] = valeurs_brutes[objet[1:]].round(1)
    valeurs_brutes[objet[0]] = valeurs_brutes[objet[0]].astype(str)
    
    return variation, valeurs_brutes


def generique_potentiel(variation, valeurs_brutes):
    """ Le principe étant d'avoir un tableau similaire à celui qui est dans
    le fichier cvs, d'avoir dans le tableau, une colonne des moyennes des 2
    semaines ainsi qu'une colonnes des moyennes sur la totalité des 4 semaines.
    """
    # TODO voir pour la concatenation et voir les répercutions
    # Attention, si je mets cette colonnes, je vais devoir retravailler
    # la fonction au dessus pour la calcul vu que c'est un string
    variation = variation.astype(float)
    recapitualitf = pd.DataFrame()
    # Récupération des 2 dernières semaines situées dans le tableau
    semaines_S_S_1 = variation.head(2)
    semaines_4S = variation
    recapitualitf["2 semaines"] = semaines_S_S_1.mean()
    recapitualitf["4 semaines"] = semaines_4S.mean()
    recapitualitf["taille"] = valeurs_brutes.mean()
    recapitualitf["Top POTENTIEL"] = (recapitualitf["2 semaines"] * recapitualitf["taille"]) / 100
    
    return recapitualitf


def tableau_top(recapitualitf):
    """ Fonction ressortant un tableau regroupant:
        - top volume : les 3 plus grosses valeurs brutes 
            (en moyenne sur la période)
        - top progression : les 3 variations les plus fortes 
            (en moyennes sur la période)
        - top potentiel : les 3 plus gros produit VOLUME X PROGRESSION 
            (en moyenne sur la période)
    """
    top = {"top Volume": [],
           "top Progression": [],
           "Top Potentiel": []}
    
    # Récupération du top 3 pour chaque top
    top_progression = recapitualitf.sort_values(by=["2 semaines"], 
                                                ascending=False).head(3)
    top_pays_progress = list(top_progression.index)
    top_volume = recapitualitf.sort_values(by=["taille"], 
                                                ascending=False).head(3)
    top_pays_volume = list(top_volume.index)
    top_potentiel = recapitualitf.sort_values(by=["Top POTENTIEL"], 
                                                ascending=False).head(3)
    top_pays_potentiel = list(top_potentiel.index)
    
    def nettoyage_str(x):
        """ Fonction qui permet de remplacer les "[" ainsi que les "]"
        pour avoir un tableau identique à celui du pdf du client
        """
        x = str(x)
        if "[" and "]" in x:
            x = x.replace("[", "").replace("]", "")
        return x


    top["top Volume"].append(top_pays_volume)
    top["top Progression"].append(top_pays_progress)
    top["Top Potentiel"].append(top_pays_potentiel)
    colonnes = list(top.keys())
    top_pays = pd.DataFrame(top, columns=colonnes)
    
    for nom in colonnes:
        top_pays[nom] = top_pays[nom].apply(nettoyage_str)    

    return top_pays

    
def moyenne_donnees_brute_pays(fichier, periode):
    """ Cette fonction permet selon une période donnée, de ressortir un
    récapitulatif de la moyenne des données brutes sur les 2 dernières 
    semaines, 4 dernières semaines et 12 dernières semaines.
    """
    colonnes = list(fichier.columns)
    fichier = fichier[fichier[colonnes[0]] <= periode]
    somme_donnees = pd.DataFrame()
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
        
        assemblage[nom_colonne] = reindex_filtre.iloc[1,1:]
        + reindex_filtre.iloc[0,1:]

        somme_donnees = pd.concat([somme_donnees, assemblage], axis=1)

    somme_donnees = somme_donnees.astype(float)
    somme_donnees = somme_donnees.T
    semaines_2S = somme_donnees.head(2).mean()
    semaines_4S = somme_donnees.head(4).mean()
    semaines_12S = somme_donnees.mean()
    recapitualitf_2s = pd.DataFrame()
    recapitualitf_4s = pd.DataFrame()
    recapitualitf_12s = pd.DataFrame()
    recapitualitf_2s["TOP 2 SEMAINES"] = semaines_2S
    recapitualitf_4s["TOP 4 SEMAINES"] = semaines_4S
    recapitualitf_12s["TOP 12 SEMAINES"] = semaines_12S

    recapitualitf_desc_2s = recapitualitf_2s.sort_values(
        by="TOP 2 SEMAINES", 
        ascending=False)
    
    recapitualitf_desc_4s = recapitualitf_4s.sort_values(
        by="TOP 4 SEMAINES", 
        ascending=False)
    
    recapitualitf_desc_12s = recapitualitf_12s.sort_values(
        by="TOP 12 SEMAINES", 
        ascending=False)

    return recapitualitf_desc_2s, recapitualitf_desc_4s, recapitualitf_desc_12s


def tableau_top_pays_hebdo(recapitualitf_desc_2s, fichier):
    """ Fonction ressortant un tableau regroupant:
        - top volume : les 3 plus grosses valeurs brutes 
            (en moyenne sur la période)
        - top progression : les 3 variations les plus fortes 
            (en moyennes sur la période)
        - top potentiel : les 3 plus gros produit VOLUME X PROGRESSION 
            (en moyenne sur la période)
        de façon HEBDOMADAIRE
    """
    top = {"top Volume": [],
           "top Progression": [],
           "Top Potentiel": []} 
    recapitualitf_desc_2s = recapitualitf_desc_2s.sort_index()
    recapitualitf_desc_2s.fillna(0, inplace=True)
    #TODO VOIR PARTIE PROGRESSION
    variation = (moyenne_variation(fichier, 1).T).sort_index()
    variation.fillna(0, inplace=True)
    concat_tableau = pd.concat([variation, recapitualitf_desc_2s], axis=1)
    top_volume = recapitualitf_desc_2s.head(3).index.to_list()
    top_progression = variation.sort_values(by=list(variation.columns), 
                                            ascending=False).head(3).index.to_list()
    
    concat_tableau["potentiel"] = concat_tableau[list(concat_tableau.columns)[0]]*concat_tableau["TOP 2 SEMAINES"]
    top_potentiel =  list(concat_tableau.sort_values(by=["potentiel"]).head(3).index)
    
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
    top_pays = pd.DataFrame(top, columns=colonnes)
    
    for nom in colonnes:
        top_pays[nom] = top_pays[nom].apply(nettoyage_str)    
    
    return top_pays

# TOP PAYS MENSUEL
def tableau_top_pays_mensuel(recapitualitf_desc_4s, fichier):
    """ Fonction ressortant un tableau regroupant:
        - top volume : les 3 plus grosses valeurs brutes 
            (en moyenne sur la période)
        - top progression : les 3 variations les plus fortes 
            (en moyennes sur la période)
        - top potentiel : les 3 plus gros produit VOLUME X PROGRESSION 
            (en moyenne sur la période)
        de façon HEBDOMADAIRE
    """
    top = {"top Volume": [],
           "top Progression": [],
           "Top Potentiel": []} 
    recapitualitf_desc_4s = recapitualitf_desc_4s.sort_index()
    recapitualitf_desc_4s.fillna(0, inplace=True)
    #TODO VOIR PARTIE PROGRESSION
    variation = (moyenne_variation(fichier, 1).T).sort_index()
    variation.fillna(0, inplace=True)
    concat_tableau = pd.concat([variation, recapitualitf_desc_4s], axis=1)
    top_volume = recapitualitf_desc_4s.head(3).index.to_list()
    top_progression = variation.sort_values(by=list(variation.columns), 
                                            ascending=False).head(3).index.to_list()
    
    concat_tableau["potentiel"] = concat_tableau[list(concat_tableau.columns)[0]]*concat_tableau["TOP 4 SEMAINES"]
    top_potentiel =  list(concat_tableau.sort_values(by=["potentiel"]).head(3).index)
    
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
    top_pays = pd.DataFrame(top, columns=colonnes)
    
    for nom in colonnes:
        top_pays[nom] = top_pays[nom].apply(nettoyage_str)    
    
    return top_pays

# TOP PAYS TRIMESTRE
def tableau_top_pays_trimestre(recapitualitf_desc_12s, fichier):
    """ Fonction ressortant un tableau regroupant:
        - top volume : les 3 plus grosses valeurs brutes 
            (en moyenne sur la période)
        - top progression : les 3 variations les plus fortes 
            (en moyennes sur la période)
        - top potentiel : les 3 plus gros produit VOLUME X PROGRESSION 
            (en moyenne sur la période)
        de façon HEBDOMADAIRE
    """
    top = {"top volume": [],
           "top Progression": [],
           "Top Potentiel": []} 
    recapitualitf_desc_12s = recapitualitf_desc_12s.sort_index()
    recapitualitf_desc_12s.fillna(0, inplace=True)
    #TODO VOIR PARTIE PROGRESSION
    variation = (moyenne_variation(fichier, 1).T).sort_index()
    variation.fillna(0, inplace=True)
    concat_tableau = pd.concat([variation, recapitualitf_desc_12s], axis=1)
    top_volume = recapitualitf_desc_12s.head(3).index.to_list()
    top_progression = variation.sort_values(by=list(variation.columns), 
                                            ascending=False).head(3).index.to_list()
    
    concat_tableau["potentiel"] = concat_tableau[list(concat_tableau.columns)[0]]*concat_tableau["TOP 12 SEMAINES"]
    top_potentiel =  list(concat_tableau.sort_values(by=["potentiel"]).head(3).index)
    
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
    top_pays = pd.DataFrame(top, columns=colonnes)
    
    for nom in colonnes:
        top_pays[nom] = top_pays[nom].apply(nettoyage_str)    
    
    return top_pays

# SUM ANNEE
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

def comparaison_brute_mois_n(fichier, mois, annee):
    """ Fonction de comparaison des valeurs brutes en fonction du mois sur 
    une période de N a N-1
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

if __name__ == "__main__":
    csv_generique = r"C:/Users/ristarz/Desktop/tourisme2/GÉNÉRIQUES/CSV/DE-IT-NL-GB-US-BE-CH-ES-FR_Generique-Paris-Hebdo_20210607_1049.csv"
    csv_pays = r"C:/Users/ristarz/Desktop/tourisme2/PAR PAYS/CSV/BE_ATF-OutreMer-Hebdo_hebdo_20210607_1048.csv"
    fichier = traitements_informations(csv_pays)
    variation, valeurs_brutes = generique_variation_valeur_brutes(fichier)
    recapitualitf_desc = moyenne_donnees_brute_pays(fichier, 
                                                    datetime(2021, 3, 1))
