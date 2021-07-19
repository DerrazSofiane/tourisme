# -*- coding: utf-8 -*-

import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from calendar import monthrange
import os

from main import (traitements_informations, generique_variation, 
                  generique_volume, generique_potentiel, moyenne_donnees_brutes,
                  sommes_periode_choisie, evolutions_sum_annees, tops_pays,
                  valeurs_brutes_3annees, semaines_evolution_volume)

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
    my_expander = st.sidebar.beta_expander("Ouvrir", expanded=True)
    with my_expander:
        st.write("2- DONNÉES : chargez le fichier à analyser :open_file_folder:")
        # Permet de rentrer un fichier pour pouvoir l'utiliser
        uploaded_file = st.file_uploader("")

    try:
        # Appel de la fonction de traitement du fichier main
        fichier = traitements_informations(uploaded_file)
        # Récupération du nom de la 1ere colonne (cela permet l'identification)
        # du pays concerné du CSV
        nom_objet = list(fichier.columns)[0]
    
        st.sidebar.write(f"Vous analysez: **{nom_objet}** :heavy_check_mark:")
        # Ressort un tableau contenant les variations sur 4 semaines
        variation = generique_variation(fichier)
        # Ressort un tableau contenant le volume des valeurs brutes sur
        # 2 semaines
        volumes_brutes = generique_volume(fichier)
        # Ressort le top 3 des pays
        top3_generique = generique_potentiel(variation, volumes_brutes)

    # CALCUL GENERIQUE
        if st.sidebar.checkbox("Les tops") and uploaded_file != "None":
            """ Checkbox de la partie "Les tops pays"
            """
            st.title("1- Les Tops")
            st.write(top3_generique)
        
        if st.sidebar.checkbox("Volumes brutes") and uploaded_file != "None":
            """ Checkbox de la partie Volume brutes des 2 dernières semaines
            """
            st.title("Volumes brutes des 2 dernières semaines")
            volume_brute = (volumes_brutes.set_index(list(fichier.columns)[0]))
            st.write(volume_brute.style.set_precision(precision=2))
            tableau = volumes_brutes
            # renommage de la 1ere colonne en "semaine"
            tableau = tableau.rename({list(fichier.columns)[0]: "semaine"}, 
                                     axis=1)
            # Transformation du tableau pour pouvoir le manipuler
            data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", 
                                  value_name="valeur")
            st.title("Volumes brutes de la semaine S et de la semaine (S-1)")
            fig, ax = plt.subplots(figsize=(10,10))
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                 data=data_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points')
            #Permet d'afficher le graphique
            st.pyplot()
            
        if st.sidebar.checkbox("Variation (%)") and uploaded_file != "None":
            """ Checkbox de la partie Variation, il retourne un tableau de
            variation des 4 semaines ainsi que 2 graphique, S sur S-1
            ainsi que S-1 sur S-2
            """
            st.title("Variations (%) des 4 dernières semaines")
            st.write(variation)
            # Récupération des 2 premieres semaines
            var_S_S1 = variation.head(2).reset_index()
            var_S_S1 = var_S_S1.rename({"index": "semaine"}, axis=1)
            # Transformation du tableau pour pouvoir le manipuler
            evolution_melted = pd.melt(var_S_S1.sort_index(ascending=False), 
                                       id_vars="semaine", var_name="pays", 
                                       value_name="valeur")
            st.title("Variations (%) de S/S-1")
            fig, ax = plt.subplots(figsize=(10,10))
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                 data=evolution_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'center', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
            st.pyplot()
            
            # Récupération des 2 dernières semaines
            var_S1_S2 = variation.tail(2).reset_index()
            var_S1_S2 = var_S1_S2.rename({"index": "semaine"}, axis=1)
            evolution_s1_melted = pd.melt(var_S1_S2.sort_index(ascending=False), 
                                          id_vars="semaine", var_name="pays", value_name="valeur")
            st.title("Variations (%) de S-1/S-2")
            fig, ax = plt.subplots(figsize=(10,10))
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                 data=evolution_s1_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points')

            st.pyplot()
        # Checkbox de commentaire, le str sera conserver dans la variable d'après 
        # Si c'est coché
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
        # Mise en place d'une date min commencant à 0
        my_time = datetime.datetime.min.time()
        # Transformation de la colonne "Semaine" du fichier en datetime
        fichier["Semaine"] = fichier["Semaine"].dt.date
        # Récupération de la dernière date pour avoir une date de référence
        derniere_date = pd.unique(fichier[colonnes[0]])[-1]
        # Convertion des dates en datetime
        conv_derniere_date = datetime.datetime.combine(derniere_date, my_time)
        # Ressort une date au format datetime.date
        date_calendar = st.sidebar.date_input("sélectionner la date d'analyse",
                                              value=conv_derniere_date)
        
        periode_choisi = sommes_periode_choisie(fichier, date_calendar)
        # Ressort 3 tableaux, 2 semaines, 4 semaines et 12 semaines
        recap_2s, recap_4s, recap_12s = moyenne_donnees_brutes(periode_choisi)
        
        if st.sidebar.checkbox("1- Les Tops") and uploaded_file != "None":
            st.title("Moyenne des données brutes sur les 2 dernières semaines, des 4 dernières semaines, des 12 dernières semaines")
            
            # Création de 3 colonnes sur l'application pour pouvoir "ranger"
            # nos tableaux pour pouvoir afficher de façon vertical
            cols = st.beta_columns(3)
            cols[0].table(recap_2s)
            cols[1].table(recap_4s)
            cols[2].table(recap_12s)

            st.title("TOP 6")

            cols = st.beta_columns(3)
            cols[0].table(recap_2s.head(6))
            cols[1].table(recap_4s.head(6))
            cols[2].table(recap_12s.head(6))
            if st.checkbox("Voulez vous mettre un commentaire ?"):
                commentaire_recapitualitf_desc = st.text_area("Emplacement du commentaire", "")
                st.write(commentaire_recapitualitf_desc)
       
        if st.sidebar.checkbox("2- Volumes brutes des 3 dernières années du top 6"):
            def top_last_annee(recap):
                annee = date_calendar.year
                evolution_annee = evolutions_sum_annees(fichier, annee)
                top_6 = recap.head(6)
                pays = list(top_6.index)
                annees = list(pd.unique(evolution_annee["annee"]))
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
                st.title("Les Tops hebdo")
                top_pays_2s = tops_pays(recap_2s,fichier, "TOP 2 SEMAINES")
                st.write(top_pays_2s)
                st.title("Volumes brutes des 3 dernières années du top 6 hebdo")
                top_last_annee(recap_2s.head(6))
                
                
            if st.checkbox("Volumes brutes des 3 dernières années du top 6 mensuel"):
                st.title("Les Tops mensuel")
                top_pays_4s = tops_pays(recap_4s, fichier, "TOP 4 SEMAINES")
                st.write(top_pays_4s)
                st.title("Volumes brutes des 3 dernières années du top 6 mensuel")
                top_last_annee(recap_4s.head(6))
               
                
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
                
                derniere_3annees = list(pd.unique(fichier["Semaine"].map(lambda x: x.year)))
                derniere_3annees.sort(reverse=True)
                mode_annee = st.selectbox(
                        "Quelle annee?",
                        (derniere_3annees)
                        )
                brute_3ans = valeurs_brutes_3annees(fichier, 
                                                    int(mois[mode_mois]),
                                                    int(mode_annee))
                st.write(brute_3ans)
                st.title(f"Volumes brutes du mois {mode_mois} l’année {mode_annee} et du mois {mode_mois} de l’année {int(mode_annee - 1)}")
                brute_3ans = brute_3ans.T
                str_annee = [str(i) for i in brute_3ans]
                derniere_annee_annee1 = brute_3ans[str_annee[0:2]]
                top_6_mensuel = list(recap_4s.head(6).index)
                
                derniere_annee_annee1 = derniere_annee_annee1.loc[top_6_mensuel,:]
                derniere_annee_melt = pd.melt(derniere_annee_annee1.reset_index(), id_vars="index", var_name="annee", value_name="valeur")
                fig1 = plt.figure()

                ax = (sns.barplot(x="index", y="valeur", hue="annee", data=derniere_annee_melt.sort_values(by=["annee"])))
                plt.xticks(rotation=90)
                st.pyplot(fig1)
                
                st.title(f"Valeurs brutes du mois {mode_mois} l’année {str(int(mode_annee))} et du mois {mode_mois} de l’année {str(int(mode_annee-2))}")
                top_6_mensuel = list(recap_4s.head(6).index)
                derniere_annee_annee2 = brute_3ans[[str_annee[0], str_annee[-1]]]
                derniere_annee_annee2 = derniere_annee_annee2.loc[top_6_mensuel,:]
                derniere_annee_melt2 = pd.melt(derniere_annee_annee2.reset_index(), id_vars="index", var_name="annee", value_name="valeur")
                fig2 = plt.figure()

                ax2 = (sns.barplot(x="index", y="valeur", hue="annee", data=derniere_annee_melt2.sort_values(by=["annee"])))
                plt.xticks(rotation=90)
                st.pyplot(fig2)
            
            if st.checkbox("Volumes brutes des 3 dernières années du top 6 trimestriel"):
                st.title("Les Tops mensuel")
        if st.sidebar.checkbox("2- Variation (%) des 3 dernières années du top 6"):
            if st.checkbox("Volumes brutes des 3 dernières années du top 6 trimestriel"):
                st.title("Les Tops mensuel")
    except:
        pass
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        