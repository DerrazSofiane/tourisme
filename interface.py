"""
Interface graphique pour observer les resultats obtenu du programme main.py
"""

from main import (traitements_informations, generique_variation_valeur_brutes,
                    generique_potentiel, moyenne_donnees_brute_pays, evolutions_sum_annees,
                    tableau_top, tableau_top_pays_hebdo)

import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from calendar import monthrange
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("OBSERVATOIRE DU TOURISME SUR INTERNET :chart:")
st.write("Cette interface permet de visualiser les calculs ainsi que les graphiques relatif en temps réel")

# Sélection du mode
st.sidebar.write("# Bienvenue dans la sélection du mode :computer:")
mode = st.sidebar.selectbox(
    "Quel mode voulez vous?",
    ("Générique", "Par pays")
)

# MODE GENERIQUE
st.sidebar.success(f"Vous avez choisi le mode {mode}")
if mode == "Générique":
    my_expander = st.sidebar.beta_expander("Ouvrir", expanded=True)
    with my_expander:
        st.write("Choisir un fichier :open_file_folder:")
        uploaded_file = st.file_uploader("")

    try:
        fichier = traitements_informations(uploaded_file)
        # Affiche l'intituler de l'objet 
        nom_objet = list(fichier.columns)[0]
        st.sidebar.write(f"Vous êtes sur : **{nom_objet}** :heavy_check_mark:")
        variation, valeurs_brutes = generique_variation_valeur_brutes(fichier)
        recapitulatif = generique_potentiel(variation, valeurs_brutes)
        top_3 = tableau_top(recapitulatif)


# CALCUL GENERIQUE
        if st.sidebar.checkbox("Calcul Générique") and uploaded_file != "None":
            st.title("Moyenne des variations des 2 dernières semaines")
            st.write(variation.head(2).style.set_precision(2))
            st.title("Moyenne des variations des 4 dernières semaines")
            st.write(variation.style.set_precision(2))
            st.title("Moyenne des valeurs brutes des 2 dernières semaines")
            st.write(valeurs_brutes.set_index(list(fichier.columns)[0]).style.set_precision(2))
            st.title("Récapitulatif :white_check_mark:")
            st.write(recapitulatif.T.style.set_precision(2))
            st.title("Top Potentiel")
            st.write(top_3.style.set_precision(2))
            if st.checkbox("Voulez vous mettre un commentaire ?"):
                commentaire_calculs = st.text_area("Emplacement du commentaire", "")


# GRAPHIQUE GENERIQUE
        if st.sidebar.checkbox("Graphique Générique") and uploaded_file != "None":
            if st.sidebar.checkbox("Valeurs brutes"):
                tableau = valeurs_brutes
                tableau = tableau.rename({list(fichier.columns)[0]: "semaine"}, axis=1)
                data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", value_name="valeur")
                st.title("Valeurs brutes de la semaine S et de la semaine (S-1)")
                fig, ax = plt.subplots(figsize=(10,10))
                st.write(sns.barplot(x="pays", y="valeur", hue="semaine", data=data_melted))
                ax.grid(axis="x")
                for p in ax.patches:
                    ax.annotate(format(p.get_height(), '.1f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'center', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                st.pyplot()


            if st.sidebar.checkbox("Evolution en % de S/S-1"):
                evolution = variation.head(2).reset_index()
                evolution = evolution.rename({"index": "semaine"}, axis=1)
                evolution_melted = pd.melt(evolution.sort_index(ascending=False), id_vars="semaine", var_name="pays", value_name="valeur")
                st.title("Evolution en % de S/S-1")
                fig, ax = plt.subplots(figsize=(10,10))
                st.write(sns.barplot(x="pays", y="valeur", hue="semaine", data=evolution_melted))
                ax.grid(axis="x")
                for p in ax.patches:
                    ax.annotate(format(p.get_height(), '.1f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'center', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                st.pyplot()


            if st.sidebar.checkbox("Evolution en % de S-1/S-2"):
                evolution_s1 = variation.tail(2).reset_index()
                evolution_s1 = evolution_s1.rename({"index": "semaine"}, axis=1)
                evolution_s1_melted = pd.melt(evolution_s1.sort_index(ascending=False), id_vars="semaine", var_name="pays", value_name="valeur")
                st.title("Evolution en % de S-1/S-2")
                fig, ax = plt.subplots(figsize=(10,10))
                st.write(sns.barplot(x="pays", y="valeur", hue="semaine", data=evolution_s1_melted))
                ax.grid(axis="x")
                for p in ax.patches:
                    ax.annotate(format(p.get_height(), '.1f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'center', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                st.pyplot()

                if st.checkbox("Voulez vous mettre un commentaire ?"):
                    commentaire_graph_s2 = st.text_area("Emplacement du commentaire", "")
    except:
        pass


# MODE PAR PAYS
elif mode == "Par pays":
    my_expander = st.sidebar.beta_expander("Ouvrir", expanded=True)
    with my_expander:
        st.write("Choisir un fichier :open_file_folder:")
        uploaded_file = st.file_uploader("")

    try:
        fichier = traitements_informations(uploaded_file)
        colonnes = list(fichier.columns)
        my_time = datetime.datetime.min.time()
        fichier["Semaine"] = fichier["Semaine"].dt.date
        derniere_date = pd.unique(fichier[colonnes[0]])[-1]
        conv_derniere_date = datetime.datetime.combine(derniere_date, my_time)
        # Ressort une date au format datetime.date
        date_calendar = st.sidebar.date_input('start date', value=conv_derniere_date)

        if st.sidebar.checkbox("Moyenne des données brutes") and uploaded_file != "None":
            recapitualitf_2s, recapitualitf_4s, recapitualitf_12s = moyenne_donnees_brute_pays(fichier, date_calendar)
            st.title("Moyenne des données brutes sur les 2 dernières semaines, des 4 dernières semaines, des 12 dernières semaines")

            cols = st.beta_columns(3)
            cols[0].table(recapitualitf_2s.style.set_precision(2))
            cols[1].table(recapitualitf_4s.style.set_precision(2))
            cols[2].table(recapitualitf_12s.style.set_precision(2))

            st.title("TOP 6")

            cols = st.beta_columns(3)
            cols[0].table(recapitualitf_2s.head(6).style.set_precision(2))
            cols[1].table(recapitualitf_4s.head(6).style.set_precision(2))
            cols[2].table(recapitualitf_12s.head(6).style.set_precision(2))
            if st.checkbox("Voulez vous mettre un commentaire ?"):
                commentaire_recapitualitf_desc = st.text_area("Emplacement du commentaire", "")
                st.write(commentaire_recapitualitf_desc.style.set_precision(2))
            
            if st.sidebar.checkbox("HEBDOMADAIRES") and uploaded_file != "None":
                recapitualitf_2s, recapitualitf_4s, recapitualitf_12s = moyenne_donnees_brute_pays(fichier, date_calendar)
                st.title("Top potentiel")
                top_pays = tableau_top_pays_hebdo(recapitualitf_2s, fichier)
                st.write(top_pays)
                
                #if st.checkbox("Voulez vous mettre un commentaire ?"):
                    #commentaire_top_hebdo = st.text_area("Emplacement du commentaire", "")


                if st.sidebar.checkbox("Valeurs brutes des 3 dernères années du top 6 hebdo"):
                    annee = date_calendar.year
                    evolution_annee = evolutions_sum_annees(fichier, annee)
                    top_6 = recapitualitf_2s.head(6)
                    pays = list(top_6.index)
                    annees = pd.unique(evolution_annee["annee"])
                    #f, ax = plt.subplots(2,3,figsize=(10,4))
                    for p in pays:
                        st.write(p)
                        annee1 = evolution_annee[p][(evolution_annee["annee"] == "2019")].reset_index().drop("index", axis=1)
                        annee2 = evolution_annee[p][(evolution_annee["annee"] == "2020")].reset_index().drop("index", axis=1)
                        annee3 = evolution_annee[p][(evolution_annee["annee"] == "2021")].reset_index().drop("index", axis=1)
                        last = pd.concat([annee1, annee2, annee3], axis=1)
                        last.columns = [p+" 2019", p+" 2020", p+" 2021"]
                        last.fillna(0, inplace=True)
                        plt.plot(last)
                        plt.legend(last.columns)
                        
                        st.pyplot()
                                

    except:
        pass

st.sidebar.write("")
st.sidebar.write("Âdhavan Algorithmics")


