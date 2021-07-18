
from main import (traitements_informations, generique_variation_valeur_brutes,
                    generique_potentiel, moyenne_donnees_brute_pays, evolutions_sum_annees,
                    tableau_top, tableau_top_pays_hebdo, tableau_top_pays_mensuel,
                    tableau_top_pays_trimestre, comparaison_brute_mois_n)

import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from calendar import monthrange
import os

st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("OBSERVATOIRE DU TOURISME SUR INTERNET")
st.image("https://nicolasbaudy.files.wordpress.com/2020/02/cropped-logo-new-2.png", use_column_width=False)


# Sélection du mode
st.sidebar.write("# Bienvenue :computer:")
mode = st.sidebar.selectbox(
    "1- ANALYSE : choisissez le mode => Générique // Par Pays ",
    ("Générique", "Par pays")
)

# MODE GENERIQUE
st.sidebar.success(f"Vous avez choisi le mode {mode}")
if mode == "Générique":

    try:
        os.mkdir("images_generique")
    except:
        pass
    
    my_expander = st.sidebar.beta_expander("Ouvrir", expanded=True)
    with my_expander:
        st.write("2- DONNÉES : chargez le fichier à analyser :open_file_folder:")
        uploaded_file = st.file_uploader("")

    try:
        fichier = traitements_informations(uploaded_file)
        # Affiche l'intituler de l'objet 
        nom_objet = list(fichier.columns)[0]
        st.sidebar.write(f"Vous analysez: **{nom_objet}** :heavy_check_mark:")
        variation, valeurs_brutes = generique_variation_valeur_brutes(fichier)
        recapitulatif = generique_potentiel(variation, valeurs_brutes)
        top_3 = tableau_top(recapitulatif)


# CALCUL GENERIQUE
        if st.sidebar.checkbox("Les tops") and uploaded_file != "None":
            st.title("1- Les Tops")
            st.write(top_3.style.set_precision(2))
        if st.sidebar.checkbox("Volumes brutes") and uploaded_file != "None":
            st.title("Volumes brutes des 2 dernières semaines")
            st.write(valeurs_brutes.set_index(list(fichier.columns)[0]).style.set_precision(2))
            
            tableau = valeurs_brutes
            tableau = tableau.rename({list(fichier.columns)[0]: "semaine"}, axis=1)
            data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", value_name="valeur")
            st.title("Volumes brutes de la semaine S et de la semaine (S-1)")
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
            
        if st.sidebar.checkbox("Variation (%)") and uploaded_file != "None":
            st.title("Variations (%) des 4 dernières semaines")
            st.write(variation.style.set_precision(2))
            evolution = variation.head(2).reset_index()
            evolution = evolution.rename({"index": "semaine"}, axis=1)
            evolution_melted = pd.melt(evolution.sort_index(ascending=False), id_vars="semaine", var_name="pays", value_name="valeur")
            st.title("Variations (%) de S/S-1")
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
            if st.checkbox("Voulez vous mettre un commentaire ?"):
                commentaire_graph_s2 = st.text_area("Emplacement du commentaire", "")
            evolution_s1 = variation.tail(2).reset_index()
            evolution_s1 = evolution_s1.rename({"index": "semaine"}, axis=1)
            evolution_s1_melted = pd.melt(evolution_s1.sort_index(ascending=False), id_vars="semaine", var_name="pays", value_name="valeur")
            st.title("Variations (%) de S-1/S-2")
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
       
    except:
        pass


# MODE PAR PAYS
elif mode == "Par pays":
    try:
        os.mkdir("images_par_pays")
    except:
        pass
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
        date_calendar = st.sidebar.date_input("sélectionner la date d'analyse", value=conv_derniere_date)
        recapitualitf_2s, recapitualitf_4s, recapitualitf_12s = moyenne_donnees_brute_pays(fichier, date_calendar)

        if st.sidebar.checkbox("1- Les Tops") and uploaded_file != "None":
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
            
            recapitualitf_2s, recapitualitf_4s, recapitualitf_12s = moyenne_donnees_brute_pays(fichier, date_calendar)
        
        if st.sidebar.checkbox("2- Volumes brutes des 3 dernières années du top 6"):
            def top_last_annee(recap):
                annee = date_calendar.year
                evolution_annee = evolutions_sum_annees(fichier, annee)
                top_6 = recap.head(6)
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
            cols = st.beta_columns(3)
            
            if st.checkbox("Volumes brutes des 3 dernières années du top 6 hebdo"):
                st.title("Volumes brutes des 3 dernières années du top 6 hebdo")
                top_last_annee(recapitualitf_2s)
                st.title("Les Tops hebdo")
                top_pays = tableau_top_pays_hebdo(recapitualitf_2s, fichier)
                st.write(top_pays)
            
            if st.checkbox("Volumes brutes des 3 dernières années du top 6 mensuel"):
                st.title("Volumes brutes des 3 dernières années du top 6 mensuel")
                top_last_annee(recapitualitf_4s)
                st.title("Les Tops mensuel")
            
                top_pays_mensuel = tableau_top_pays_mensuel(recapitualitf_4s, fichier)
                st.write(top_pays_mensuel)

                mois = {"janvier": 1, 
                        "février": 2, 
                        "mars": 3, 
                        "avril": 4, 
                        "mai": 5,
                        "juin": 6, 
                        "juillet": 7,
                        "août": 8, 
                        "septembre": 9, 
                        "octobre": 10,
                        "novembre": 11, 
                        "décembre": 12}
                
                mois_str = list(mois.keys())
                mode_mois = st.selectbox(
                        "Quel mois?",
                        (mois_str)
                        )
                derniere_3annee = list(pd.unique(fichier["Semaine"].map(lambda x: x.year)))
                derniere_3annee.sort(reverse=True)
                mode_annee = st.selectbox(
                        "Quelle annee?",
                        (derniere_3annee)
                        )
                
                tableau_brute_n = comparaison_brute_mois_n(fichier, int(mois[mode_mois]), int(mode_annee))
                st.title(f"Volumes brutes du mois {mode_mois} l’année {mode_annee} et du mois {mode_mois} de l’année {int(mode_annee - 1)}")
                tableau_brute_n = tableau_brute_n.T
                str_annee = [str(i) for i in derniere_3annee]
                derniere_annee_annee1 = tableau_brute_n[str_annee[0:2]]
                top_6_mensuel = list(recapitualitf_4s.head(6).index)

                derniere_annee_annee1 = derniere_annee_annee1.loc[top_6_mensuel,:]
                derniere_annee_melt = pd.melt(derniere_annee_annee1.reset_index(), id_vars="index", var_name="annee", value_name="valeur")
                fig1 = plt.figure()

                ax = (sns.barplot(x="index", y="valeur", hue="annee", data=derniere_annee_melt.sort_values(by=["annee"])))
                plt.xticks(rotation=90)
                st.pyplot(fig1)
                
                st.title(f"Valeurs brutes du mois {mode_mois} l’année {str(int(mode_annee))} et du mois {mode_mois} de l’année {str(int(mode_annee-2))}")
                top_6_mensuel = list(recapitualitf_4s.head(6).index)
                derniere_annee_annee2 = tableau_brute_n[[str_annee[0], str_annee[-1]]]
                derniere_annee_annee2 = derniere_annee_annee2.loc[top_6_mensuel,:]
                derniere_annee_melt2 = pd.melt(derniere_annee_annee2.reset_index(), id_vars="index", var_name="annee", value_name="valeur")
                fig2 = plt.figure()

                ax2 = (sns.barplot(x="index", y="valeur", hue="annee", data=derniere_annee_melt2.sort_values(by=["annee"])))
                plt.xticks(rotation=90)
                st.pyplot(fig2)
                
            if st.checkbox("Volumes brutes des 3 dernières années du top 6 trimestriel"):
                st.title("Volumes brutes des 3 dernières années du top 6 trimestriel")
                top_last_annee(recapitualitf_12s)
      
        
        if st.sidebar.checkbox("TRIMESTRE") and uploaded_file != "None":
            st.title("Top potentiel trimestre")
            top_pays = tableau_top_pays_trimestre(recapitualitf_12s, fichier)
            st.write(top_pays)
                
    except:
        pass