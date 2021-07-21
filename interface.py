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
                  valeurs_brutes_3annees, variation_hebdo, evolutions_mois_annee,
                  variation_mensuel, moyenne_trimestrielle, valeur_trimestrielle,
                  variation_trimestrielle)

st.set_option('deprecation.showPyplotGlobalUse', False)



st.title("OBSERVATOIRE DU TOURISME")
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
        if st.sidebar.checkbox("1 - Les tops") and uploaded_file != "None":
            # Checkbox de la partie "Les tops pays"
            st.title("1- Les meilleures pays pour le tourisme durant les 4 dernières semaines")
            colonnes = list(top3_generique.columns)
            top3_generique2 = pd.concat([top3_generique[colonnes[0]], top3_generique[colonnes[1]], top3_generique[colonnes[2]]])
            index = [1,2,3]
            colonne = "Top 3"
            top3_generique2.columns = colonne
            top3_generique2.index = index
            st.table(top3_generique2)
        
        if st.sidebar.checkbox("2 - Les volumes") and uploaded_file != "None":
            # Checkbox de la partie Volume brutes des 2 dernières semaines
            st.title("Volumes des 2 dernières semaines")
            volume_brute = volumes_brutes.set_index(list(fichier.columns)[0])
            
            tmp = volume_brute.copy()
            colonnes = tmp.columns
         
            def arrondie_str(x):
                x = str(x)
                x_str = x[:5]
                print(x_str)
                return x_str
            
            for colonne in colonnes:
                tmp[colonne] = tmp[colonne].apply(arrondie_str)

            st.write(tmp)
            tableau = volumes_brutes
            # renommage de la 1ere colonne en "semaine"
            tableau = tableau.rename({list(fichier.columns)[0]: "semaine"}, 
                                     axis=1)
            # Transformation du tableau pour pouvoir le manipuler
            data_melted = pd.melt(tableau, id_vars="semaine", var_name="pays", 
                                  value_name="valeur")
            st.write(tableau)
            st.write(data_melted)
            st.title("Volumes de la semaine S et de la semaine (S-1)")
            fig, ax = plt.subplots(figsize=(10,10))
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                 data=data_melted))
            ax.grid(axis="x")
            for p in ax.patches:
                ax.annotate(format(p.get_height(), '.1f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'bottom', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points',
                    rotation=90)
            #Permet d'afficher le graphique
            st.pyplot()
            
        if st.sidebar.checkbox("3 - Les variation (%)") and uploaded_file != "None":

            st.title("Variations (%) des 4 dernières semaines")
            variation_copy = variation.copy()
            variation_colonnes = variation.columns
            
            def arrondie_str(x):
                x = str(x)
                x_str = x[:5]
                print(x_str)
                return x_str
            
            for colonne in colonnes:
                variation_copy[colonne] = variation_copy[colonne].apply(arrondie_str)
                
            st.write(variation_copy)
            # Récupération des 2 premieres semaines
            var_S_S1 = variation.head(2).reset_index()
            var_S_S1 = var_S_S1.rename({"index": "semaine"}, axis=1)
            # Transformation du tableau pour pouvoir le manipuler
            evolution_melted = pd.melt(var_S_S1.sort_index(ascending=False), 
                                       id_vars="semaine", var_name="pays", 
                                       value_name="valeur")
            st.title("Variations hebdomadaires des volumes")
            fig, ax = plt.subplots(figsize=(10,10))
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                 data=evolution_melted))
            ax.grid(axis="x")
            ax.set(xlabel="Pays", ylabel='Variation (%)')
            for p in ax.patches:
                ax.annotate(" "+str(format(p.get_height(), '.1f'))+"%", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'bottom', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points',
                    rotation=90)
            st.pyplot()
            
            # Récupération des 2 dernières semaines
            var_S1_S2 = variation.tail(2).reset_index()
            var_S1_S2 = var_S1_S2.rename({"index": "semaine"}, axis=1)
            evolution_s1_melted = pd.melt(var_S1_S2.sort_index(ascending=False), 
                                          id_vars="semaine", var_name="pays", value_name="valeur")
            st.title("Variations hebdomadaires des volumes de la semaine passée")
            fig, ax = plt.subplots(figsize=(10,10))
            st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                 data=evolution_s1_melted))
            ax.grid(axis="x")
            ax.set(xlabel="Pays", ylabel='Variation (%)')
            for p in ax.patches:
                ax.annotate(" "+str(format(p.get_height(), '.1f'))+"%", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'bottom', 
                    size=9,
                    xytext = (0, 1), 
                    textcoords = 'offset points',
                    rotation=90)

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
        
        if st.sidebar.checkbox("1- Les tops") and uploaded_file != "None":
            st.title("Les volumes hebdomadaires moyens des 2, 4, 12 dernières semaines")
            
            def arrondie_str(x):
                x = str(x)
                x_str = x[:5]
                print(x_str)
                return x_str
            
            recap_2s_copy = recap_2s.copy()
            recap_4s_copy = recap_4s.copy()
            recap_12s_copy = recap_12s.copy()
            
            for colonne in list(recap_2s_copy.columns):
                recap_2s_copy[colonne] = recap_2s_copy[colonne].apply(arrondie_str)
            
            for colonne in list(recap_4s_copy.columns):
                recap_4s_copy[colonne] = recap_4s_copy[colonne].apply(arrondie_str)
            
            for colonne in list(recap_12s_copy.columns):
                recap_12s_copy[colonne] = recap_12s_copy[colonne].apply(arrondie_str)
            # Création de 3 colonnes sur l'application pour pouvoir "ranger"
            # nos tableaux pour pouvoir afficher de façon vertical
            
            st.title("TOP 6")

            cols = st.beta_columns(3)
            cols[0].table(recap_2s_copy.head(6))
            cols[1].table(recap_4s_copy.head(6))
            cols[2].table(recap_12s_copy.head(6))
            st.title("Les valeurs suivantes")
            cols = st.beta_columns(3)
            cols[0].table(recap_2s_copy.iloc[7:])
            cols[1].table(recap_4s_copy.iloc[7:])
            cols[2].table(recap_12s_copy.iloc[7:])

            
            if st.checkbox("Voulez vous mettre un commentaire ?"):
                commentaire_recapitualitf_desc = st.text_area("Emplacement du commentaire", "")
                st.write(commentaire_recapitualitf_desc)
       
        if st.sidebar.checkbox("2- Les volumes des 3 dernières années du top 6"):
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
           
            if st.sidebar.checkbox("Volumes des 3 dernières années du top 6 hebdo"):
                st.title("Les tops hebdomadaires")
                top_pays_2s = tops_pays(recap_2s,fichier, "TOP 2 SEMAINES")
                colonnes = list(top_pays_2s.columns)
                top_pays_concat = pd.concat([top_pays_2s[colonnes[0]], top_pays_2s[colonnes[1]], top_pays_2s[colonnes[2]]])
                index = [1,2,3]
                colonne = "Top 3"
                
                top_pays_concat.columns = colonne
                top_pays_concat.index = index
                st.table(top_pays_concat)
                st.title("Volumes des 3 dernières années du top 6 hebdo")
                top_last_annee(recap_2s.head(6))
                
                if st.checkbox("Voulez vous mettre un commentaire ?"):
                    commentaire_graph_s2 = st.text_area("Emplacement du commentaire", "")
            elif st.sidebar.checkbox("Volumes des 3 dernières années du top 6 mensuel"):
                def top_last_mois_annee(recap, mois, annee):
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
                        
                st.title("Les tops mensuels")
                top_pays_4s = tops_pays(recap_4s, fichier, "TOP 4 SEMAINES")
                colonnes = list(top_pays_4s.columns)
                top_pays_concat_mensuel = pd.concat([top_pays_4s[colonnes[0]], top_pays_4s[colonnes[1]], top_pays_4s[colonnes[2]]])
                index = [1,2,3]
                colonne = "Top 3"
                
                top_pays_concat_mensuel.columns = colonne
                top_pays_concat_mensuel.index = index
                st.table(top_pays_concat_mensuel)
                st.title("Volumes mensuels des 3 dernières années")
               
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
                        "Quelle année?",
                        (derniere_3annees)
                        )
                top_last_mois_annee(recap_4s.head(6), int(mois[mode_mois]), int(mode_annee))
                brute_3ans = valeurs_brutes_3annees(fichier, 
                                                    int(mois[mode_mois]),
                                                    int(mode_annee))
                st.title(f"Volumes mensuels de {mode_mois} {mode_annee} comparé à {mode_annee-1}")
               
                brute_3ans = brute_3ans.T
                str_annee = [str(i) for i in brute_3ans]
                derniere_annee_annee1 = brute_3ans[[str_annee[1], str_annee[-1]]]
                top_6_mensuel = list(recap_4s.head(6).index)
                
                derniere_annee_annee1 = derniere_annee_annee1.loc[top_6_mensuel,:]
                derniere_annee_melt = pd.melt(derniere_annee_annee1.reset_index(),
                                              id_vars="index", var_name="annee",
                                              value_name="valeur")
                fig_mensuel1, ax_mensuel = plt.subplots(figsize=(10,10))
                ax_mensuel = (sns.barplot(x="index", y="valeur", hue="annee", 
                                  data=derniere_annee_melt.sort_values(by=["annee"])))
                plt.xticks(rotation=90)
                ax_mensuel.set(xlabel="Région", ylabel='Volume')
                ax_mensuel.grid()
                for p in ax_mensuel.patches:
                    ax_mensuel.annotate(" "+str(format(p.get_height(), '.1f')), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'bottom', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points',
                        rotation=90)
                st.pyplot()
                
                st.title(f"Volumes mensuels de {mode_mois} {mode_annee} comparé à {mode_annee-2}")
                top_6_mensuel = list(recap_4s.head(6).index)
                derniere_annee_annee2 = brute_3ans[[str_annee[0], str_annee[-1]]]
                derniere_annee_annee2 = derniere_annee_annee2.loc[top_6_mensuel,:]
                derniere_annee_melt2 = pd.melt(derniere_annee_annee2.reset_index(), 
                                               id_vars="index", var_name="annee",
                                               value_name="valeur")
                fig_mensuel2, ax_mensuel2 = plt.subplots(figsize=(10,10))

                ax_mensuel2 = (sns.barplot(x="index", y="valeur", hue="annee", 
                                   data=derniere_annee_melt2.sort_values(by=["annee"])))
                ax_mensuel2.set(xlabel="Région", ylabel='Volume')
                plt.xticks(rotation=90)
                ax_mensuel2.grid()
                for p in ax_mensuel2.patches:
                    ax_mensuel2.annotate(" "+str(format(p.get_height(), '.1f')), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'bottom', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points',
                        rotation=90)
                st.pyplot()
                
                if st.checkbox("Voulez vous mettre un commentaire ?"):
                    commentaire_graph_s2 = st.text_area("Emplacement du commentaire", "")
            elif st.sidebar.checkbox("Volumes des 3 dernières années du top 6 trimestriel"):
                st.title("Les Tops trimestriel")
                top_pays_12s = tops_pays(recap_12s, fichier, "TOP 12 SEMAINES")
                colonnes = list(top_pays_12s.columns)
                top_pays_concat_trim = pd.concat([top_pays_12s[colonnes[0]],
                                                  top_pays_12s[colonnes[1]], 
                                                  top_pays_12s[colonnes[2]]])
                index = [1,2,3]
                colonne = "Top 3"
                
                top_pays_concat_trim.columns = colonne
                top_pays_concat_trim.index = index
                st.table(top_pays_concat_trim)
                
                derniere_3annees_trim = list(pd.unique(fichier["Semaine"].map(lambda x: x.year)))
                derniere_3annees_trim.sort(reverse=True)
                mode_annee = st.selectbox(
                        "Quelle annee?",
                        (derniere_3annees_trim)
                        )
                
                
                ############################### voir courbes
                
                
                
                
                
                
                moyenne_trimestre = moyenne_trimestrielle(fichier, mode_annee,
                                                          recap_12s)
                moyenne_trimestre_t = moyenne_trimestre.T.reset_index()
                moyenne_trimestre_t = moyenne_trimestre_t.rename({"index": "annee"}, axis=1)
                moyenne_trimestre_melted = pd.melt(moyenne_trimestre_t.sort_index(ascending=False), 
                                          id_vars="annee", var_name="pays", value_name="valeur")
                colonnes = list(moyenne_trimestre.columns)
                pays = list(pd.unique(moyenne_trimestre_melted["pays"]))
                moyenne_trimestre_melted_filtreN = moyenne_trimestre_melted[(moyenne_trimestre_melted["annee"] == 2021)]
                moyenne_trimestre_melted_filtreN2 = moyenne_trimestre_melted[(moyenne_trimestre_melted["annee"] == 2020)]
                concat_N = pd.concat([moyenne_trimestre_melted_filtreN,moyenne_trimestre_melted_filtreN2])
                
                st.title(f"Volume du 1er Trimestre de l'année {colonnes[0]} et {colonnes[1]}")
                fig3, ax3 = plt.subplots(figsize=(10,10))
                st.write(sns.barplot(x="pays", y="valeur", hue="annee", 
                                     data=concat_N))
                ax3.grid()
                for p in ax3.patches:
                    ax3.annotate(" "+str(format(p.get_height(), '.1f')), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'bottom', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points',
                        rotation=90)
                plt.xticks(rotation=90)
                ax3.set(xlabel="Région", ylabel='Volume')

                st.pyplot()
                
                moyenne_trimestre_melted_filtreN3 = moyenne_trimestre_melted[(moyenne_trimestre_melted["annee"] == 2019)]
                concat_N2 = pd.concat([moyenne_trimestre_melted_filtreN,moyenne_trimestre_melted_filtreN3])
                st.title(f"Volume du 1er Trimestre de l'année {colonnes[0]} et {colonnes[2]}")
                fig4, ax4 = plt.subplots(figsize=(10,10))

                st.write(sns.barplot(x="pays", y="valeur", hue="annee", 
                                     data=concat_N2))
                ax4.grid()
                for p in ax4.patches:
                    ax4.annotate(" "+str(format(p.get_height(), '.1f')), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'bottom', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points',
                        rotation=90)
                plt.xticks(rotation=90)
                ax4.set(xlabel="Région", ylabel='Volume')

                st.pyplot()
                if st.checkbox("Voulez vous mettre un commentaire ?"):
                    commentaire_graph_s2 = st.text_area("Emplacement du commentaire", "")
                
        if st.sidebar.checkbox("3- Les variation (%) des 3 dernières années du top 6"):
            if st.sidebar.checkbox("Les variation (%) hebdomadaire"):
                st.title("Les variations (%) hebdomadaire")
                variation_hebdo = variation_hebdo(fichier, date_calendar, recap_2s)
                variation_hebdo_s_s1 = variation_hebdo.head(2)
                variation_hebdo_s1_s2 = variation_hebdo.tail(2)
                variation_hebdo_s_s1 = variation_hebdo_s_s1.reset_index()
                variation_hebdo_s_s1 = variation_hebdo_s_s1.rename({list(variation_hebdo_s_s1.columns)[0]: "semaine"}, 
                                     axis=1)
                variation_hebdo_s1_s2 = variation_hebdo_s1_s2.reset_index()
                variation_hebdo_s1_s2 = variation_hebdo_s1_s2.rename({list(variation_hebdo_s1_s2.columns)[0]: "semaine"}, 
                                     axis=1)
                # Transformation du tableau pour pouvoir le manipuler
                data_melted_s = pd.melt(variation_hebdo_s_s1, id_vars="semaine", var_name="pays", 
                                      value_name="valeur")
  
                data_melted_s1 = pd.melt(variation_hebdo_s1_s2, id_vars="semaine", var_name="pays", 
                                      value_name="valeur")
                st.title("Variation en % de S/S-1")
                fig, ax = plt.subplots(figsize=(10,10))
                st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                     data=data_melted_s))
                ax.grid(axis="x")
                for p in ax.patches:
                    ax.annotate(" "+str(format(p.get_height(), '.1f')+"%"), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'bottom', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                #Permet d'afficher le graphique
                ax.set(xlabel="Région", ylabel='Variation (%)')
                st.pyplot()
                
                st.title("Variations en % de S-1 / S-2")
                fig, ax = plt.subplots(figsize=(10,10))
                st.write(sns.barplot(x="pays", y="valeur", hue="semaine", 
                                     data=data_melted_s1))
                ax.grid(axis="x")
                for p in ax.patches:
                    ax.annotate(" "+str(format(p.get_height(), '.1f')+"%"), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'bottom', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                #Permet d'afficher le graphique
                ax.set(xlabel="Région", ylabel='Variation (%)')

                st.pyplot()
                if st.checkbox("Voulez vous mettre un commentaire ?"):
                    commentaire_graph_s2 = st.text_area("Emplacement du commentaire", "")
            elif st.sidebar.checkbox("Les variations (%) mensuelle"):
                st.title("Les variations (%) mensuelle")
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
                        "Quelle année?",
                        (derniere_3annees)
                        )
                variation_mensuelle = variation_mensuel(fichier, mode_annee, 
                                                        mois[mode_mois],recap_4s)
                variation_mensuelle = variation_mensuelle.reset_index()

                colonnes_annee_mois = list(variation_mensuelle.columns)
                st.title(f"Evolution en % du mois {mode_mois} de l'année {mode_annee} et {mode_annee-1}")               
                
                fig, ax = plt.subplots(figsize=(10,10))
                st.write(plt.bar(variation_mensuelle[colonnes_annee_mois[0]],variation_mensuelle[colonnes_annee_mois[1]]))
                ax.grid()
                for p in ax.patches:
                    ax.annotate(" "+str(format(p.get_height(), '.1f')+"%"), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'top', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                plt.xticks(rotation=90)
                ax.set(xlabel="Région", ylabel='Variation (%)')

                legend = str(mode_mois)+" "+str(mode_annee)+"/"+str(mode_annee-1)
                plt.title(legend)
                #Permet d'afficher le graphique
                st.pyplot()
                
                st.title(f"Evolution en % du mois {mode_mois} de l'année {mode_annee} et {mode_annee-2}")
                
                fig, ax = plt.subplots(figsize=(10,10))
                st.write(plt.bar(variation_mensuelle[colonnes_annee_mois[0]],variation_mensuelle[colonnes_annee_mois[2]]))
                ax.grid()
                for p in ax.patches:
                    ax.annotate(" "+str(format(p.get_height(), '.1f')+"%"), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'top', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                plt.xticks(rotation=90)
                legend2 = str(mode_mois)+" "+str(mode_annee)+"/"+str(mode_annee-2)
                plt.title(legend2)
                ax.set(xlabel="Région", ylabel='Variation (%)')

                #Permet d'afficher le graphique
                st.pyplot()
                if st.checkbox("Voulez vous mettre un commentaire ?"):
                    commentaire_graph_s2 = st.text_area("Emplacement du commentaire", "")
            elif st.sidebar.checkbox("Les variation (%) trimestrielle"):
                st.title("les variation (%) trimestrielle")
                derniere_3annees = list(pd.unique(fichier["Semaine"].map(lambda x: x.year)))
                derniere_3annees.sort(reverse=True)
                mode_annee = st.selectbox(
                        "Quelle annee?",
                        (derniere_3annees)
                        )
                moyenne_trimestre = moyenne_trimestrielle(fichier, mode_annee,
                                                          recap_12s)
                variation_trimestrielle = variation_trimestrielle(moyenne_trimestre)
                colonnes = list(variation_trimestrielle.columns)
                fig, ax = plt.subplots(figsize=(10,10))
                t1 = variation_trimestrielle[colonnes[0]].reset_index()
                st.title(f"Les variations du 1er Trimestre de l'année {mode_annee} et {mode_annee-2}")
                st.write(sns.barplot(x="index",y = colonnes[0], data=t1))
                ax.grid()
                ax.set(xlabel="Région", ylabel='Variation (%)')

                for p in ax.patches:
                    ax.annotate(" "+str(format(p.get_height(), '.1f')+"%"), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'top', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points',
                        rotation=90)
                plt.xticks(rotation=90)
                st.pyplot()
                st.title(f"les variations du 1er Trimestre de l'année {mode_annee} et {mode_annee-1}")

                t2 = variation_trimestrielle[colonnes[1]].reset_index()
                fig2, ax2 = plt.subplots(figsize=(10,10))

                st.write(sns.barplot(x="index",y = colonnes[1], data=t2))
                ax2.grid()
                for p in ax2.patches:
                    ax2.annotate(" "+str(format(p.get_height(), '.1f')+"%"), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'top', 
                        size=9,
                        xytext = (0, 1), 
                        textcoords = 'offset points')
                plt.xticks(rotation=90)
                ax2.set(xlabel="Région", ylabel='Variation (%)')

                st.pyplot()
                if st.checkbox("Voulez vous mettre un commentaire ?"):
                    commentaire_graph_s3 = st.text_area("Emplacement du commentaire", "")
                
    except:
        pass
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        