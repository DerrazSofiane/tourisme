"""
OBSERVATOIRE DU TOURISME SUR INTERNET

CONTEXTE :
Un outil a été développé pour collecter de la donnée et pour nettoyer cette 
donnée
L’outil de restitution implique des tâches manuelles très chronophages

OBJECTIFS :
Automatiser la production des livrables décrits dans cette expression de besoins
Donner accès direct auX clientS, à leur espace, à leurs analyses, sur internet

DÉMARCHE :
••• GÉNÉRIQUE ••• : 
TOUS LES 15 JOURS (mais demain, à la demande, en 
sélectionnant la période)
Les données sont organisées par « objet » : Paris, Hôtels, Rés. Tourisme, 
Camping, Ch Hôte, Voyage, Tout inclus, Week-End, Croisière, Avion, Train, 
Disney, Ski, … (cette liste se complétera probablement)
Les données récoltées sont HEBDOMADAIRES.
Les mises à jour sont « annule et remplace » (pas de mise à jour incrémentale).
La mise à dispo des données se fait par fichier CSV (voir répertoire CSV). 
Dans le fichier CSV, les données sont les pays, en colonne et les semaines 
en ligne.

CALCULS :
Moyenne des variations des 2 dernières semaines
Moyenne des variations des 4 dernières semaines
Moyenne des valeurs brutes des 2 dernières semaines

Tracé des 3 graphiques du fichier HEBDO – GÉNÉRIQUE.xlsx
Valeurs brutes de la semaine S et de la semaine (S-1)
Evolution en % de S/S-1 et de S-1 / S-2
Graphe composite
Intégration des graphiques dans HEBDO 2021 06 07.pdf
Publication du rapport et consultation 

••• PAR PAYS ••• : 
tous les 15 jours pour certains pays, tous les mois pour 
d’autres pays, tous les trimestres enfin
Les données sont organisées par « PANEL » : Outre-Mer, Urbain, Littoral, 
Montagne, Campagne (cette liste se complétera probablement).
Chaque panel se constitue d’« objets » qui correspondent à des destinations
Les données récoltées sont HEBDOMADAIRES.
Les mises à jour sont « annule et remplace » (pas de mise à jour incrémentale).
La mise à dispo des données se fait par fichier CSV (voir répertoire CSV). 
Dans le fichier CSV, les données sont les pays, en colonne et les semaines 
en ligne.
Les données sont copiées / collées (valeurs – transposées) à la main dans un 
fichier par pays (ex : BE.xlsx). Donc en colonne les semaines et en ligne les 
destinations.

CALCULS :
Moyenne des données brutes sur les 2 dernières semaines, des 4 dernières 
semaines, des 12 dernières semaines => en fonction de la période qu’on veut 
observer
Tri sur la moyenne du plus grand au plus petit
Sélection du top 6.
Tracé des graphiques du fichier BE.xlsx
Valeurs brutes des années 2019, 2020, 2021 (les 3 dernières années)
TOUS LES 15 JOURS :
Valeurs brutes de la semaine S et de la semaine (S-1)
Evolution en % de S/S-1 et de S-1 / S-2
Graphe composite
TOUS LES MOIS :
Valeurs brutes du mois M de l’année N et du mois M de l’année N-1
Valeurs brutes du mois M de l’année N et du mois M de l’année N-2
Evolution en % du mois de N/N-1 et de N / N-2
Graphe composite
Intégration des graphiques dans HEBDO 2021 06 07.pdf
Publication du rapport et consultation 


Livrables attendus :
Un rapport tous les 15 j
Un rapport tous les mois
Un rapport tous les trimestres
Accès sur internet à une interface permettant de :
Sélectionner la période à analyser (sélection des semaines à prendre en compte)
Sélectionner « générique » ou « par pays »
Sélectionner des objets génériques dans « générique » // des panels dans 
« par pays »
Affichage des graphes
Possibilité de formuler des commentaires manuellement
"""
import pandas as pd
import datetime
from datetime import timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from pprint import pprint

############# TRAVAIL SUR LES DONNÉES #############
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
                                                    format="%Y-%m-%d").dt.date
    
    return lecture_fichier


def moyenne_variations_generique(tableau):
    """ Fonction permettant de calculer la moyenne des variations sur X semaines
    Pour la calculer, la formule est la suivante:
    ((Va - Vd) / Vd) * 100
    Va : Valeur d'arrivée (semaine actuelle)
    Vd : Valeur de départ (semaine -1)
    """
    tableau_comparatif = pd.DataFrame()
    colonnes = tableau.columns
    dates = list(tableau[colonnes[0]])
    i = 0
    for days in range(1,5):
        """ Le but étant de pouvoir récupérer la semaine S ainsi que la semaine 
        S -1
        Pour ce faire, l'algorithme prends en charge 2 valeurs incrementales
        
        days : Qui permet de récuperer la semaine d'avant stocker dans la
        variable "semaine"

        i : Qui permet d'incrementer l'index du tableau qui stock la semaine
        """
        df_temp = pd.DataFrame()
        # Obtention de la date S a comparer
        semaine_actuelle = dates[-days]
        semaine = semaine_actuelle - timedelta(7*days)
        comparaison_2semaines = tableau[(tableau[colonnes[0]] <= semaine_actuelle) &
                                        (tableau[colonnes[0]] >= semaine)]
        
        comparaison_2semaines = comparaison_2semaines.reset_index(drop=True)
        col_nom = str(comparaison_2semaines.iloc[i+1,0]) + "/" + str(comparaison_2semaines.iloc[i,0]) 
        
        df_temp[col_nom] = ((comparaison_2semaines.iloc[i+1,1:] - 
                                        comparaison_2semaines.iloc[i,1:]) /
                                        comparaison_2semaines.iloc[i,1:])*100
        
        tableau_comparatif = pd.concat([tableau_comparatif, df_temp], axis=1)
        i += 1

    tableau_comparatif = tableau_comparatif.T
    tableau_comparatif = tableau_comparatif.astype(float)
    tableau_comparatif = tableau_comparatif.round(2).reset_index()

    comparatif_final = pd.DataFrame()
    moyenne_1_2semaine = (tableau_comparatif.iloc[0,1:] + tableau_comparatif.iloc[1,1:]) / 2
    moyenne_3_4semaine = (tableau_comparatif.iloc[2,1:] + tableau_comparatif.iloc[3,1:])/2
    comparatif_final["Moy 2 sem"] = moyenne_1_2semaine
    comparatif_final["Moy 4 sem"] = (moyenne_1_2semaine + moyenne_3_4semaine)/2 
    comparatif_final = comparatif_final.T
    
    i = 0
    valeur_brut = pd.DataFrame()
    for days in range(1,3):
        """ Le but étant de pouvoir récupérer la semaine S ainsi que la semaine 
        S -1
        Pour ce faire, l'algorithme prends en charge 2 valeurs incrementales
        
        days : Qui permet de récuperer la semaine d'avant stocker dans la
        variable "semaine"

        i : Qui permet d'incrementer l'index du tableau qui stock la semaine
        """
        df_temp = pd.DataFrame()
        # Obtention de la date S a comparer
        semaine_actuelle = dates[-days]
        semaine = semaine_actuelle - timedelta(7*days)
        comparaison_2semaines = tableau[(tableau[colonnes[0]] <= semaine_actuelle) &
                                        (tableau[colonnes[0]] >= semaine)]
        comparaison_2semaines = comparaison_2semaines.reset_index(drop=True)
        col_nom = str(comparaison_2semaines.iloc[i+1,0]) + "/" + str(comparaison_2semaines.iloc[i,0]) 
        df_temp[col_nom] = (comparaison_2semaines.iloc[i+1,1:] +
                                        comparaison_2semaines.iloc[i,1:]) / 2
        valeur_brut = pd.concat([valeur_brut, df_temp], axis=1)
        i += 1

    valeur_brut = (valeur_brut.T).astype(float).round(2)

    return tableau_comparatif.round(2), comparatif_final.round(2), valeur_brut.round(2)


def donnee_par_pays(tableau, periode):
    colonnes = list(tableau.columns)
    tableau[colonnes[0]] = pd.to_datetime(tableau[colonnes[0]], format="%Y-%m-%d")

    tableau = tableau[tableau[colonnes[0]] <= periode]
    dates = list(tableau[colonnes[0]])
    i = 0
    valeur_brut = pd.DataFrame()

    # Récuperation des 12 semaines comparées
    for days in range(1,13):
        """ Le but étant de pouvoir récupérer la semaine S ainsi que la semaine 
        S -1 X fois
        Pour ce faire, l'algorithme prends en charge 2 valeurs incrementales
        
        days : Qui permet de récuperer la semaine d'avant stocker dans la
        variable "semaine"

        i : Qui permet d'incrementer l'index du tableau qui stock la semaine
        """
        df_temp = pd.DataFrame()
        # Obtention de la date S a comparer
        semaine_actuelle = dates[-days]
        semaine = semaine_actuelle - timedelta(7*days)
        comparaison_2semaines = tableau[(tableau[colonnes[0]] <= semaine_actuelle) &
                                        (tableau[colonnes[0]] >= semaine)]
        comparaison_2semaines = comparaison_2semaines.reset_index(drop=True)
        col_nom = str(comparaison_2semaines.iloc[i+1,0]) + "/" + str(comparaison_2semaines.iloc[i,0]) 
        df_temp[col_nom] = (comparaison_2semaines.iloc[i+1,1:] +
                                        comparaison_2semaines.iloc[i,1:]) / 2
        valeur_brut = pd.concat([valeur_brut, df_temp], axis=1)
        #valeur_brut.index = [str(i)+" semaine" for i in range(1,13)]
        i += 1
    
    comparatif_final = pd.DataFrame()
    moyenne_2 = (valeur_brut.iloc[:,0] + valeur_brut.iloc[:,1]) / 2
    moyenne_4 = (valeur_brut.iloc[:,0] + valeur_brut.iloc[:,1] + valeur_brut.iloc[:,2] + valeur_brut.iloc[:,3]) / 4
    
    moyenne_12 = (valeur_brut.iloc[:,0] + valeur_brut.iloc[:,1] + valeur_brut.iloc[:,2] + valeur_brut.iloc[:,3] +
                valeur_brut.iloc[:,4] + valeur_brut.iloc[:,5] + valeur_brut.iloc[:,6] + valeur_brut.iloc[:,7] +
                valeur_brut.iloc[:,8] + valeur_brut.iloc[:,9] + valeur_brut.iloc[:,10] + valeur_brut.iloc[:,11]) / 12
        
    comparatif_final["2 semaines"] = moyenne_2
    comparatif_final["4 semaines"] = moyenne_4
    comparatif_final["12 semaines"] = moyenne_12
    sorted_final = comparatif_final.sort_values(["2 semaines", "4 semaines", "12 semaines"], ascending=False)
    top_6 = sorted_final.head(6)
    print(valeur_brut)
    return valeur_brut, comparatif_final, sorted_final, top_6


def evolution_jours(tableau):
    tableau_comparatif = pd.DataFrame()
    colonnes = tableau.columns
    dates = list(tableau[colonnes[0]])
    i = 0
    for days in range(1,5):
        """ Le but étant de pouvoir récupérer la semaine S ainsi que la semaine 
        S -1
        Pour ce faire, l'algorithme prends en charge 2 valeurs incrementales
        
        days : Qui permet de récuperer la semaine d'avant stocker dans la
        variable "semaine"

        i : Qui permet d'incrementer l'index du tableau qui stock la semaine
        """
        df_temp = pd.DataFrame()
        # Obtention de la date S a comparer
        semaine_actuelle = dates[-days]
        semaine = semaine_actuelle - timedelta(7*days)
        comparaison_2semaines = tableau[(tableau[colonnes[0]] <= semaine_actuelle) &
                                        (tableau[colonnes[0]] >= semaine)]
        
        comparaison_2semaines = comparaison_2semaines.reset_index(drop=True)
        col_nom = str(comparaison_2semaines.iloc[i+1,0]) + "/" + str(comparaison_2semaines.iloc[i,0]) 
        
        df_temp[col_nom] = ((comparaison_2semaines.iloc[i+1,1:] - 
                                        comparaison_2semaines.iloc[i,1:]) /
                                        comparaison_2semaines.iloc[i,1:])*100
        
        tableau_comparatif = pd.concat([tableau_comparatif, df_temp], axis=1)
        i += 1

    tableau_comparatif = tableau_comparatif.T
    tableau_comparatif = tableau_comparatif.astype(float)
    tableau_comparatif = tableau_comparatif.reset_index()

    #TODO inf et Nan dans la dataframe
    print(tableau_comparatif.dtypes)
    return tableau_comparatif


def evolution_mois(tableau, mois, annee):
    tableau_date = pd.DataFrame()
    for i in range(0,4):
        mois_map = tableau["Semaine"].map(lambda x: x.month) == mois
        tableau_mois = tableau[mois_map]
        annee_map = tableau_mois["Semaine"].map(lambda x: x.year) == annee-i
        tableau_annee_mois = tableau_mois[annee_map]
        tableau_date = pd.concat([tableau_date, tableau_annee_mois])

    def index_annee(x):
        x = str(x)[:4]
        return x
    tableau_date["annee"] = tableau_date["Semaine"].apply(index_annee)
    tableau_brut = tableau_date.groupby("annee").sum()
    return tableau_brut.reset_index()


def evolution_annee(tableau, annee):
    evolution_annee = pd.DataFrame()
    for i in range(0,4):
        N = tableau["Semaine"].map(lambda x: x.year) == annee - i
        tableau_annee = tableau[N]
        evolution_annee = pd.concat([evolution_annee, tableau_annee])
    
    def index_annee(x):
        x = str(x)[:4]
        return x
    evolution_annee["annee"] = evolution_annee["Semaine"].apply(index_annee)
    tableau_variation = (evolution_annee.groupby("annee").sum()).reset_index()
    tableau_variation = tableau_variation.astype(float)
    tableau_final = pd.DataFrame()
    """((Va - Vd) / Vd) * 100
    Va : Valeur d'arrivée (semaine actuelle)
    Vd : Valeur de départ (semaine -1)"""
    tableau_final["N/N-1"] = ((tableau_variation.iloc[-1,:] - tableau_variation.iloc[-2,:]) / tableau_variation.iloc[-2,:]) * 100
    tableau_final["N/N-2"] = ((tableau_variation.iloc[-1,:] - tableau_variation.iloc[0,:]) / tableau_variation.iloc[0,:]) * 100
    print(tableau_final)

