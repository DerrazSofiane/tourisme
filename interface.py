from main import (traitements_informations, moyenne_variations_generique,
                donnee_par_pays, evolution_jours, evolution_mois)
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import datetime
from calendar import monthrange
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("Expression tourisme")
st.write("Cette interface permet de visualiser les calculs ainsi que les graphiques relatif en temps réel")
st.sidebar.title("Version Alpha")
st.sidebar.write("Instruction")
st.sidebar.write("Veuillez ne sélectionner qu'un seul mode à la fois")
st.sidebar.write("Par pays: si vous voulez afficher les graphiques 15 jours ou par mois, vous devez déselectionner 'Graphique Valeurs brutes les 3 dernières années'")

st.sidebar.markdown("# Sélection du mode")
if st.sidebar.checkbox("GENERIQUE"):
    uploaded_file = st.file_uploader("Choisir fichier")
    try:
        df = traitements_informations(uploaded_file)
        tableau_comparatif, comparatif_final, valeur_brut = moyenne_variations_generique(df)
    except:
        pass
    try:
        st.title(list(df.columns)[0])
    except:
        pass
    if st.sidebar.checkbox("Calcul Générique"):
        st.title("Tableau comparatif des 4 dernières semaines en %")
        tableau_comparatif.index = tableau_comparatif.index +1
        st.write(tableau_comparatif.round(2).astype("str"))
        st.title("Tableau récapitulatif en %")
        st.write(comparatif_final.round(2).astype("str"))
        st.title("Tableau comparatif des valeurs brutes sur 2 semaines")
        st.write(valeur_brut.round(2).astype("str"))

    if st.sidebar.checkbox("Graphique Générique"):
        if st.sidebar.checkbox("Les 2 dernières semaines"):
            tableau = tableau_comparatif.iloc[-2:,:]
            tableau = tableau.rename({"index": "semaine"}, axis=1)
            data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", value_name="valeur")
            fig, ax = plt.subplots(figsize=(10,10))
            st.title("Evolution en % de S/S-1")
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

        if st.sidebar.checkbox("les 4 dernières semaines"):
            tableau = tableau_comparatif.iloc[0:2,:]
            tableau = tableau.rename({"index": "semaine"}, axis=1)
            data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", value_name="valeur")
            st.title("Evolution en % de S-1/S-2")
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
        
        if st.sidebar.checkbox("valeurs brutes"):
            tableau = valeur_brut.reset_index()
            tableau = tableau.rename({"index": "semaine"}, axis=1)
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

        if st.sidebar.checkbox("Graphique composite"):
            tableau = valeur_brut
            comparatif = pd.concat([comparatif_final, tableau])
            rename = list(comparatif.index)
            comparatif = comparatif.reset_index()
            comparatif["index"] = comparatif["index"].replace(rename[2], "taille")
            comparatif_final = comparatif.iloc[:3,:]
            comparatif_final = comparatif_final.rename({"index": "semaine"}, axis=1)        
            comparatif_final = comparatif_final.set_index("semaine").astype(float)
            comparatif_final = comparatif_final.T
            st.title("évolution tendances de recherches hebdomadaires")
            fig, ax = plt.subplots(figsize=(10,10))
            ax.grid()
            st.write(sns.scatterplot(x="Moy 4 sem", y="Moy 2 sem", size="taille", sizes=(50,400),data=comparatif_final))
            st.pyplot()

if st.sidebar.checkbox("PAR PAYS"):
    uploaded_file = st.file_uploader("Choisir fichier")
    #par_pays = "PAR PAYS/CSV/BE_ATF-Campagne-Hebdo_hebdo_20210607_1049.csv"
    try:
        df = traitements_informations(uploaded_file)
        colonnes = list(df.columns)
        derniere_date = pd.unique(df[colonnes[0]])[-1]
        my_time = datetime.datetime.min.time()
        conv_derniere_date = datetime.datetime.combine(derniere_date, my_time)
        date_calendar = st.sidebar.date_input('start date', value=conv_derniere_date)
        date_convert = datetime.datetime.combine(date_calendar, my_time)
        valeur_brut, comparatif_final, sorted_final, top_6 = donnee_par_pays(df, date_convert)
        indexage_semaine = valeur_brut.T
        list_index = list(indexage_semaine.index)
        indexage_semaine["semaine"] = list_index
        reindexage = indexage_semaine["semaine"].reset_index()
        reindexage.index = reindexage.index + 1
        st.sidebar.write(reindexage["semaine"])

    except:
        pass
    try:
        st.title(list(df.columns)[0])
    except:
        pass

    if st.sidebar.checkbox("Calcul par pays"):
        st.title("Tableau de comparatif de valeurs brutes sur 2 semaines / 4 semaines / 12 semaines")
        st.write(comparatif_final.round(2).astype("str"))
        st.title("Tableau de comparatif de valeurs brutes sur 2 semaines / 4 semaines / 12 semaines du plus grand au plus petit")
        st.write(sorted_final.round(2).astype("str"))
        st.title("TOP 6")
        st.write(top_6.round(2).astype("str"))
    
    if st.sidebar.checkbox("Graphique Valeurs brutes les 3 dernières années"):
        tableau = df
        brut = pd.DataFrame()
        colonnes = list(tableau.columns)[1:]
        annee_brut = pd.DataFrame()
        def annee(x):
            x = str(x)
            return x[:4]

        tableau["Annee"] = tableau["Semaine"].apply(annee)
        dernieres_annees = list(pd.unique(tableau["Annee"]))[-3:]
        tableau = tableau.drop("Semaine", axis=1)
        # [2019,2020,2021]
        for i in dernieres_annees:
            ans = tableau[tableau["Annee"] == i]
            sum_annee = ans.groupby("Annee").sum()
            brut = pd.concat([brut, sum_annee])
        brut = brut.reset_index()
        data_melted = pd.melt(brut, id_vars="Annee", var_name="ville", value_name="valeur")
        plt.title("Valeurs brutes des 3 dernières années")
        fig = plt.figure(1, figsize=(100, 80))
        plt.gcf().subplots_adjust(bottom=0.40)
        st.write(sns.lineplot(x="ville", y="valeur", hue="Annee", data=data_melted))
        plt.xticks(rotation=90)
        st.pyplot()

    if st.sidebar.checkbox("Tous les 15 jours"):
        if st.sidebar.checkbox("Evolution en % de S/S-1"):
            tableau_evolution = evolution_jours(df)
            tableau_evolution.index = tableau_evolution.index + 1
            st.write(tableau_evolution.round(2).astype("str"))
            tableau = tableau_evolution.iloc[:2,:]
            tableau = tableau.rename({"index": "semaine"}, axis=1)
            data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", value_name="valeur")
            fig, ax = plt.subplots(figsize=(10,10))
            st.title("évolution tendances recherches Semaine S / S-1")
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", data=data_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points') 
            plt.gcf().subplots_adjust(bottom=0.40)
            plt.xticks(rotation=90)       
            st.pyplot()

        if st.sidebar.checkbox("Evolution en % de S-1/S-2"):
            tableau_evolution = evolution_jours(df)
            tableau = tableau_evolution.iloc[-2:,:]
            tableau = tableau.rename({"index": "semaine"}, axis=1)
            data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", value_name="valeur")
            fig, ax = plt.subplots(figsize=(10,10))
            st.title("évolution tendances recherches Semaine S / S-1")
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", data=data_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points') 
            plt.gcf().subplots_adjust(bottom=0.40)
            plt.xticks(rotation=90)       
            st.pyplot()
            tableau_evolution.index = tableau_evolution.index + 1
            st.write(tableau_evolution.round(2).astype("str"))

    if st.sidebar.checkbox("Par mois"):
        mois_input = st.sidebar.text_input("Mois", 1)
        annee_input = st.sidebar.text_input("Année", 2021)
        nb_jour = monthrange(int(annee_input), int(mois_input))[1]
        st.sidebar.write("Il y a " + str(nb_jour) + " jours pour le mois " + str(mois_input) + " et l'année " + str(annee_input))
        if st.sidebar.checkbox("Valeurs brutes du mois M de l’année N et du mois M de l’année N-1"):
            tableau_brut = evolution_mois(df, int(mois_input), int(annee_input))
            #tableau_brut["annee"] = tableau_brut["annee"].astype(int)
            tableau_brut = tableau_brut.sort_values("annee", ascending=False)
            tableau = tableau_brut.iloc[:2,:]
            tableau = tableau.rename({"index": "annee"}, axis=1)
            data_melted = pd.melt(tableau, id_vars="annee", var_name="pays", value_name="valeur")
            fig, ax = plt.subplots(figsize=(10,10))
            st.title("évolution Valeurs brutes du mois M de l’année N et du mois M de l’année N-1 recherches Semaine S / S-1")
            st.write(sns.barplot(x="pays", y="valeur", hue="annee", data=data_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points') 
            plt.gcf().subplots_adjust(bottom=0.40)
            plt.xticks(rotation=90)       
            st.pyplot()
            tableau_brut.index = tableau_brut.index + 1
            st.write(tableau_brut.round(2).astype("str"))
        
        if st.sidebar.checkbox("Valeurs brutes du mois M de l’année N et du mois M de l’année N-2"):
            tableau_brut = evolution_mois(df, int(mois_input), int(annee_input))
            tableau_brut.index = tableau_brut.index + 1
            st.write(tableau_brut.round(2).astype("str"))
            tableau = tableau_brut.iloc[[0,-1],:]
            tableau = tableau.rename({"index": "annee"}, axis=1)
            data_melted = pd.melt(tableau, id_vars="annee", var_name="pays", value_name="valeur")
            fig, ax = plt.subplots(figsize=(10,10))
            st.title("Valeurs brutes du mois M de l’année N et du mois M de l’année N-2")
            st.write(sns.barplot(x="pays", y="valeur", hue="annee", data=data_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points') 
            plt.gcf().subplots_adjust(bottom=0.40)
            plt.xticks(rotation=90)       
            st.pyplot()

