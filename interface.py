# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import random
#import pycountry
#import gettext
from datetime import datetime, timedelta
from scipy.signal import savgol_filter
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from io import StringIO

# POUR LANCER L'INTERFACE EN LOCAL:
#   streamlit run interface.py

# POUR LANCER L'INTERFACE SUR LE WEB, après avoir mis le code sur le dépot 
# https://github.com/Lee-RoyMannier/tourisme
# https://share.streamlit.io/lee-roymannier/tourisme/main/interface.py

st.set_option('deprecation.showPyplotGlobalUse', False)

#français = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['fr'])
#français.install()

# Code iso des pays traduits en noms français courts 
pays = pd.read_csv("Dictionnaire_Pays.csv")
noms_pays = pays["Country"]
noms_pays.index = pays["2CODE"]

# TODO: 
# Se référer à 2019 pour faire les prévisions. 

### I - LECTURE DES DONNEES 
def lecture_donnees(nom_tableau, DATA_DRIVE):
    # A partir des identifiants Google, le tableau choisi par l'utilisateur
    # est lu, transformé en tableau, reformaté et renvoyé
    id_drive = DATA_DRIVE[nom_tableau]
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)
    fichier_source = drive.CreateFile({'id': id_drive})
    donnee_brut = fichier_source.GetContentString()
    data = pd.read_csv(StringIO(donnee_brut), sep=";")
    
    # Formatage de l'index en date
    data = data.set_index(data.columns[0])
    data.index = data.index.map(lambda x: datetime.strptime(x, "%Y-%m-%d").date())

    # Formatage des nombres à vigule en flottant
    data = data.applymap(lambda x: float(x.replace(",", ".")))
    print("Tableau final:",data)

    return data


def donnees_aleatoires(t0=datetime(2017, 6, 1).date(), nb_semaines=4*53):
    data = pd.DataFrame()
 
    data.index = [t0+timedelta(days=i*7) for i in range(nb_semaines)]
    for pays in ['FR', 'SU', 'EN', 'IT', 'ES']:
        data[pays] = [random.gauss(10, 4) for i in range(nb_semaines)]

    data.index.name = "Paris"

    return data


### II - MISE EN FORME
month_str = {
    1: "janvier" , 2: "février"  , 3: "mars", 
    4: "avril"   , 5: "mai"      , 6: "juin", 
    7: "juillet" , 8: "août"     , 9: "septembre",
    10:"octobre" , 11:"novembre" , 12:"décembre"}


def duree_str(date1, date2):
    """Ecrit l'interval entre deux dates d'une manière intuitive et sans 
    redondances. Les dates en entrée sont au format de la librairie datetime.
    
    Par exemple, si on en en entrée:
    >>> date1 = datetime(2020, 10, 3)
    >>> date2 = datetime(2020, 10, 10)
    
    Alors l'interval entre les deux date s'écrira: 'du 3 au 10 octobre 2020' à
    la place par exemple de l'écriture redondante: 'du 3 octobre 2020 au 10 
    octobre 2020'.
    
    Si cela est nécessaire, les années et les mois sont précisés pour chaque
    date. Par exemple, on écrira: 'du 3 octobre 2020 au 10 septembre 2021'."""
    
    d1 = min(date1, date2)
    d2 = max(date1, date2)
    
    def day_str(j):
        if j==1:
            return "1er"
        else:
            return str(j)
    
    a1, m1, j1 = str(d1.year), month_str[d1.month], day_str(d1.day)
    a2, m2, j2 = str(d2.year), month_str[d2.month], day_str(d2.day)
    
    if a1==a2 and m1==m2:
        return  j1+" au "+j2+" "+m2+" "+a2
    elif a1==a2 and m1!=m2:    
        return  j1+" "+m1+" au "+j2+" "+m2+" "+a2 
    else:
        return  j1+" "+m1+" "+a1+" au "+j2+" "+m2+" "+a2


def nom_pays(code_iso):
    """ Nom court en Français d'un pays à partir de son code iso en 2 lettres.
    Retourne par exemple "France" pour "FR" """
    try:
        #return _(noms_pays[code_iso].split(" (")[0]).split(" ")[0]
        return (noms_pays[code_iso].split(" (")[0]).split(" ")[0]
    except:
        return code_iso


def arrondie_str(x):
    corps, decimales = str(x).split('.')
    return corps+','+decimales[:2]


### III - CALCULS
def variation(x, delta=timedelta(days=7)):
    t2 = max(x.index)
    t1 = t2-delta
    return (x[t2]-x[t1])/x[t1]


def variations(data, date1, date2, delta=4*timedelta(7)):
    # Variations en pourcentage
    dt = data.index[-1] - data.index[-2]
    var = 100*(data-data.shift(round(delta/dt)))/data.shift(round(delta/dt))

    # Variations pendant delta, pour toutes les dates entre date1 et date2 
    date_min = max(min(data.index), date1-delta)
    date_max = min(max(data.index), date2)
    var = var[(var.index>=date_min) & (var.index<=date_max)]
    
    # double index avec la date de début et de fin 
    #dates_1, dates_2 = var.index-delta, var.index
    #dates_1.name, dates_2.name = "début", "fin"
    #var.index = [dates_1, dates_2]

    return var


def tops3(data, date1, date2):

    def tops(data, date1, date2):
        data = data[(data.index>=date1) & (data.index<=date2)]
        tops = data.mean().sort_values(ascending=False)
        return tops
    
    var = variations(data, date1, date2, delta=4*timedelta(7))

    tops_volume    = tops(data, date1, date2)
    tops_variation = tops(var , date1, date2)
    tops_potentiel = (tops_variation*tops_volume).sort_values(ascending=False)

    tops3 = pd.DataFrame({
        "top volume"      : list(tops_volume.head(3).index),
        "top progression" : list(tops_variation.head(3).index),
        "top potentiel"   : list(tops_potentiel.head(3).index)}).T

    tops3 = tops3.applymap(lambda x: nom_pays(x)+"("+x+")")
    tops3.columns = ["1er", "2ème", "3ème"]
    
    return tops3


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
    top = {"top Volume": [], "top Progression": [], "Top Potentiel": []} 
    
    recapitualif_x_semaines = recapitualif_x_semaines.sort_index()
    recapitualif_x_semaines.fillna(0, inplace=True)
    variation = (variations(fichier, 1).T).sort_index()
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
    """ Tableau les valeurs brutes des 3 dernieres année."""
    evolution_annee = pd.DataFrame()
    
    for i in range(0,4):
        N = fichier["Semaine"].map(lambda x: x.year) == annee - i
        tableau_annee = fichier[N]
        evolution_annee = pd.concat([evolution_annee, tableau_annee])

    evolution_annee["annee"] = evolution_annee["Semaine"].apply(lambda x: str(x)[:4])
    evolution_annee = evolution_annee.reset_index()
    evolution_annee.drop(["index", "Semaine"], axis=1, inplace=True)
    colonne_voulu = list(evolution_annee.columns)[::-1]
    evolution_annee = evolution_annee[colonne_voulu]
    
    return evolution_annee


def evolutions_mois_annee(fichier, mois, annee):
    """ Tableau les valeurs brutes des 3 dernieres année."""
    tableau_date = pd.DataFrame()
    
    for i in range(0,4):
        mois_map = fichier["Semaine"].map(lambda x: x.month) == mois
        tableau_mois = fichier[mois_map]
        annee_map = tableau_mois["Semaine"].map(lambda x: x.year) == annee-i
        tableau_annee_mois = tableau_mois[annee_map]
        tableau_date = pd.concat([tableau_date, tableau_annee_mois])

    tableau_date["annee"] = tableau_date["Semaine"].apply(lambda x: str(x)[:4])
    tableau_date = tableau_date.reset_index()
    tableau_date.drop(["index", "Semaine"], axis=1, inplace=True)
    colonne_voulu = list(tableau_date.columns)[::-1]
    tableau_date = tableau_date[colonne_voulu]
    
    return tableau_date


def valeurs_brutes_3annees(fichier, mois, annee):
    """ Tableau de la sommes des valeurs des pays en fonction du mois et des 
    3 dernières années à partir de l'argument année de la fonction.
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
    
    tableau_date["annee"] = tableau_date["Semaine"].apply(lambda x: str(x)[:4])
    tableau_brut = tableau_date.groupby("annee").sum()
    
    return tableau_brut


def valeur_trimestrielle(data, annee):
    annee_map = data["Semaine"].map(lambda x: x.year) == annee
    tableau_annee_mois = data[annee_map]
    tableau_annee_mois[str(annee)] = list(tableau_annee_mois.reset_index().index)
    
    return tableau_annee_mois


def moyenne_trimestrielle(data, annee, top6_trimestre):
    """ Moyennes du trimestre T1 de l'année X par rapport a l'année X-1

    Argument:
        data => dataframe
        annee => dernière année 
        trimestre => le numéro du trimestre (T1 est le trimestre correspondant
                                             au 3 premier mois)
        top6_trimestre => tableau regroupant le top 6 trimestriel
    """
    tableau_moyenne = pd.DataFrame()
    def boucle_mois(annee):
        colonnes = list(top6_trimestre.head(6).index)
        tableau_date = pd.DataFrame()
        
        for i in range(0,3):
            mois_map = data["Semaine"].map(lambda x: x.month) == 1+i
            tableau_mois = data[mois_map]
            annee_map = tableau_mois["Semaine"].map(lambda x: x.year) == annee
            tableau_annee_mois = tableau_mois[annee_map]
            tableau_date = pd.concat([tableau_date, tableau_annee_mois])
        return tableau_date.loc[:,colonnes]
    
    tableau_date = boucle_mois(annee)
    moyenne_last_annee = tableau_date.mean()
    tableau_moyenne[annee] = moyenne_last_annee
    tableau_date2 = boucle_mois(annee-1)
    moyenne_annee2 = tableau_date2.mean()
    tableau_moyenne[annee-1] = moyenne_annee2
    tableau_date3 = boucle_mois(annee-2)
    moyenne_annee3 = tableau_date3.mean()
    tableau_moyenne[annee-2] = moyenne_annee3
    
    return tableau_moyenne


def variation_hebdo(data, periode, top_6_hebdo):
    """ Fonction permettant de récupérer 4 semaines (S / S-1 et S-1 / S-2)
    et de calculer les variations sur une période donnée
    Exemple:
        les 2 semaines a partir du 2021-3-21
    retourne un tableau
    """
    colonnes = list(data.columns)
    data = data[data[colonnes[0]] <= periode]
    variation = variations(data,4)
    variation.fillna(0, inplace=True)
    top_6 = list(top_6_hebdo.head(6).index)
    top_variation_hebdo = variation.loc[:,top_6]
    
    return top_variation_hebdo


def variation_trimestrielle(tableau_moyenne):
    def variation_mois_annee(x,y):
        try:
            var = ((x - y) / y) * 100
        except ZeroDivisionError:
            var = 0
        return var
    
    tableau_variation = pd.DataFrame()
    colonnes = list(tableau_moyenne.columns)
    tableau_variation["T1 "+str(colonnes[0])+"/"+str(colonnes[1])] = tableau_moyenne.apply(lambda x: variation_mois_annee(x[colonnes[0]], x[colonnes[1]]), axis=1)
    tableau_variation["T1 "+str(colonnes[0])+"/"+str(colonnes[2])] = tableau_moyenne.apply(lambda x: variation_mois_annee(x[colonnes[0]], x[colonnes[2]]), axis=1)
    
    return tableau_variation

def variation_mensuel(data, annee, mois, top_6_mensuel):
    """ Fonction permettant de récupérer 4 semaines et de calculer les 
    variations sur une période donnée. Nous allons chercher à construire un 
    tableau de moyenne d'un moix X et d'année Y sous la forme:
        
                         Moy Mai 2020    	Moy Mai 2021	
        RÈunion (RE)	               65    	 113    	
        Guadeloupe (GP)	           44    	 69    	
        Martinique (LC)	           28    	 60    	
    """
    moyenne_region = pd.DataFrame()
    top_region = list(top_6_mensuel.head(6).index)
    top_region.append("Semaine")
    data = data.loc[:,top_region]
    for i in range(0,3):
        tmp = pd.DataFrame()
        # Construction du tableau pour l'année N actuel (2021 pour exemple)
        annee_map = data["Semaine"].map(lambda x: x.year) == annee - i
        tableau_mois = data[annee_map]
        # Construction pour le mois M
        mois_map = tableau_mois["Semaine"].map(lambda x: x.month) == mois
        tableau = tableau_mois[mois_map]
        tmp[str(mois)+" "+str(annee-i)] = tableau.head(4).mean(axis=0)
        moyenne_region = pd.concat([moyenne_region, tmp], axis=1)
        
    annees = list(moyenne_region.columns)
    variation = pd.DataFrame()
   
    def variation(x,y):
        if y!=0:
            return ((x - y) / y) * 100
        else:
            return 0
    
    variation[annees[0]+" / "+annees[1]] = moyenne_region.apply(lambda x: variation(x[annees[0]], x[annees[1]]), axis=1)
    variation[annees[0]+" / "+annees[2]] = moyenne_region.apply(lambda x: variation(x[annees[0]], x[annees[2]]), axis=1)
   
    return variation

### IV - GRAPHQUES

def graph_volumes(data, nom_x, nom_y, nom_z):
    # Mise en forme des données (data) pour pouvoir utiliser seaborne, dans un 
    # tableau à trois colonnes (data_graph). La première est le temps, sous 
    # forme de date, la deuxième est les valeurs (volumes, variations, etc...),
    # la troixième les catégories (pays, région, etc..).
    # Les légendes des axes du dessin sont:
    # légende des catégories -> nom_x
    # légende des valeurs    -> nom_y
    # légende du temps       -> nom_z
    data_graph = pd.DataFrame()
    for pays in list(data.columns):
        df = pd.DataFrame({nom_z: data[pays].index, nom_y: data[pays], nom_x: pays})
        data_graph = data_graph.append(df, ignore_index=True)

    # Lorsque les valeurs sont des volumes, les dates représentent des 
    # semaines. Elles sont mises sous un format plus lisible.
    # Lorsque les valeurs sont des variations, les dates représentent le début
    # de la première semaine de variation 
    dt = timedelta(days=6) # temps entre le début et la fin de la semaine 
    data_graph[nom_z] = data_graph[nom_z].apply(lambda t: duree_str(t, t+dt))

    # Les volumes sont ensuite représentés à l'aide de barres.
    # Différentes palettes de couleurs ont été testées:
    # YlGnBu RdBu OrRd PRGn Spectral YlOrBr
    fig, ax = plt.subplots(figsize=(10,6), dpi=300)
    sns.barplot(x=nom_x, y=nom_y, hue=nom_z, data=data_graph,
                palette=sns.color_palette("YlGnBu")[-min(len(data),6):])

    # Les différentes semaines sont données en légende
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.01),
              fancybox=True, shadow=False, ncol=3)

    # Les volumes sont écrits en bleu en haut d'une barre, lorsque la valeur
    # est positive et en bas d'une barre lorsque la valeur est négative.
    for p in ax.patches:
        text = " "+format(p.get_height(), '.1f')+" "
        if "%" in nom_y: text+="% "
        x = p.get_x() + p.get_width() / 2.
        y = p.get_height()
        if y >= 0:
            ax.annotate(text, (x,y), ha='center', va='bottom', size=8, 
                        color='blue', xytext=(0,1), textcoords='offset points',
                        rotation=90)
        else:
            ax.annotate(text, (x,y), ha='center', va='top', size=8, 
                        color='red', xytext=(0,1), textcoords='offset points',
                        rotation=90)

    # Des limites un peu plus larges sont fixées en ordonnées afin d'être 
    # certain que les écritures précédentes ne dépassent du cadre
    ymin, ymax = min(data_graph[nom_y]), max(data_graph[nom_y])
    ax.set_ylim([(ymin-0.2*(ymax-ymin) if ymin < 0 else 0),
                 (ymax+0.2*(ymax-ymin) if ymax > 0 else 0)])

    return fig

def graph_3_ans(data, pays, lissage=False):
    """Lissage avec le filtre de Savitzky-Golay . Il utilise les moindres 
    carrés pour régresser une petite fenêtre de vos données sur un polynôme, 
    puis utilise le polynôme pour estimer le point situé au centre de la 
    fenêtre. Enfin, la fenêtre est décalée d’un point de données et le 
    processus se répète. Cela continue jusqu'à ce que chaque point ait été 
    ajusté de manière optimale par rapport à ses voisins. Cela fonctionne très 
    bien même avec des échantillons bruyants provenant de sources non 
    périodiques et non linéaires."""

    a = max(data.index).year
    j1 = data[data.index >= datetime(a, 1, 1).date()].index[0]
    fig, ax = plt.subplots(figsize=(10,6), dpi=300)
    for i in range(3):
        date1, date2 = datetime(a-i, 1, 1).date(), datetime(a-i, 12, 31).date()
        data_ = data[(data.index>date1) & (data.index<=date2)]
        dates = [j1+int((date-date1).days/7.)*timedelta(days=7) for date in data_.index]
        ligne  = ('o--' if i==0 else '.-')
        ligne2 = ('o:'  if i==0 else '.:')
        c = sns.color_palette("YlGnBu")[-i*2-1]
        y = data_[pays].values
        if lissage:
            ylis = savgol_filter(y, 15, 3)
            ax.plot(dates, ylis, ligne, color=c, label=str(a-i)+u" lissé")
            ax.plot(dates, y, ligne2, color=c, label=str(a-i), alpha=0.3)
        else:
            ax.plot(dates, y, ligne, color=c, label=str(a-i))
    
    # Les différentes semaines sont données en légende
    ax.legend(fancybox=True, shadow=False, ncol=1)
    
    # Des limites pour que l'échelle ne change pas entre le lissage et 
    # l'abscence de lissage 
    ax.set_ylim(0, 1.1*data[pays].max())
    
    ax.set_ylabel("Indice Google Trends – Base 100")
    ax.set_title(pays)
    
    plt.xticks([datetime(a, m+1, 1).date() for m in range(12)], 
           ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
           rotation=45) 

    return fig


### V - GENERATION D'UN RAPPORT
def rapport_pdf():
    pass


### VI - INTERFACES WEB

def entete():
    txt = u"""Bienvenue à l’observatoire digital des destinations françaises de Atout, powered by
Baudy et Compagnie ©"""
    cols = st.beta_columns(2) # number of columns in each row! = 2
    cols[0].image("logo_Atout_France.png", use_column_width=True)
    cols[1].image("logo_Baudy_Co.png", use_column_width=True) 
    #cols[1].image("https://nicolasbaudy.files.wordpress.com/2020/02/cropped-logo-new-2.png")
    st.title("Observatoire digital des destinations")
    st.text(txt)


def introduction():
    txt = """
Les termes de recherches touristiques utilisés dans Google par les internautes
sont comptés. Les "termes" sont des groupes de mots correspondant à un même
concept, non nécessairement accolés aux destinations. IL s'agit de mesurer si 
l’intérêt pour le terme analysé redémarre, indépendamment d’un lieu.

Par exemple l'analyse portera sur "hôtel" et non "hôtel à Lyon" de la 
rubrique « travel » de Google Trends.

  - Périodicité d’analyse: 2 fois par mois
  
  - Marchés analysés: Allemagne (DE), Belgique (BE), Espagne (ES),
Etats-Unis (US), France (FR), Italie (IT), Pays-Bas (NL) Royaume-Uni (UK)
et Suisse (CH)

  - Termes analysés: hôtel, résidence de tourisme, camping, chambre d’hôte,
voyage, tout inclus, week-end, croisière, billet d’avion, billet de train,
Paris et Disneyland Paris (toutes catégories)."""

    st.title("Introduction")
    st.header("1- Analyse des mots clés génériques par pays")
    st.text(txt)


def choix_fichier_donnees(DATA_DRIVE):
    #my_expander = st.sidebar.beta_expander("Ouvrir", expanded=True)
    #with my_expander:
    #    st.write(u"Fichier à analyser")
    #    uploaded_file = st.file_uploader("")

    # uploaded_file = st.sidebar.file_uploader("Données de Google Trends:")
    if DATA_DRIVE != None:
        uploaded_file = st.sidebar.selectbox("Quelle requête effectuer?",
                                             DATA_DRIVE.keys())
        return uploaded_file


def selection_mode_analyse():
    global mode
    txt = "Type d'analyse: " 
    mode = st.sidebar.selectbox(txt, ("Générique", "Par pays"))
    #st.sidebar.success(f"Vous avez choisi le mode {mode}")


def visualisation_tops(data):
    date_1, date_2 = max(data.index) - 4*timedelta(7), max(data.index)
    txt = f"""
Synthèse des classements des 3 meilleurs pays sur une période d'analyse, par défaut 
les 4 dernières semaines disponibles du {duree_str(date_1,date_2)}, respectivement 
pour le 'top volume', la 'top progession' et le 'top potentiel'. 
 
  - L'indicateur de 'volume' est la moyenne des volumes hebdomadaires constatés sur 
les 4 dernières semaines. Il rend compte du niveau d'activité général, tout en 
minimisant les fluctuations pouvant survenir à l'échelle hebdomadaire.
 
  - L'indicateur de 'progression' est la moyenne sur la période des variations
hebdomadaires en pourcentages. Plus il y a eu de variations hebdomadaires à la
hausse pendant 4 semaines, plus l'indicateur de progression est élévé. 

  - L'indicateur de 'potentiel' est le produit de l'indicateur de volume par 
l'indicateur de progression. Il indique les gains potentiels futurs si la tendance 
à la progression observée est conservée.
"""
    st.title("1 - Tops pays")
    st.text(txt)

    date_1, date_2 = max(data.index) - 4*timedelta(7), max(data.index)
    date1 = st.date_input("début:",value=date_1)
    date2 = st.date_input("fin:",  value=date_2)

    top3 = tops3(data, date1, date2)
    st.table(top3)


def visualisation_volumes(data):
    txt = """
Google Trends permet de mesurer, de manière relative, l’évolution des recherches 
des internautes, à partir de mots-clés (sujets ou destinations), avec un indice 100
pour la valeur la plus haute au cours de la période analysée. Le champ d’application 
est restreint au domaine du « travel » (ou catégorie « voyage »). Les résultats ne 
sont pas des valeurs absolues mais se lisent en indices.

La visualisation de cet indice au cours des dernières semaines permet de constater 
les fluctuations et les éventuelles tendances de manière empirique. L'attention est 
mise sur les 2 denières semaines puis sur les 4 dernières semaines. """
    st.title("2 - Indice des tendances de recherches des 2 dernières semaines ")
    st.text(txt)

    st.header("a - Tendances de recherche des 2 dernières semaines")
    table = data.tail(2).applymap(lambda x: "{:.1f}".format(x))
    table.index = table.index.map(lambda t: duree_str(t, t+timedelta(days=6)))
    st.write(table)

    nom_x, nom_y, nom_z = "Pays", "Indice Google Trends – Base 100", "Semaine"
    st.pyplot(graph_volumes(data.tail(2), nom_x, nom_y, nom_z))

    st.header("b - Tendances de recherche des 4 dernières semaines")
    table = data.tail(4).applymap(lambda x: "{:.1f}".format(x))
    table.index = table.index.map(lambda t: duree_str(t, t+timedelta(days=6)))
    st.write(table)
    st.pyplot(graph_volumes(data.tail(4), nom_x, nom_y, nom_z))


def visualisation_variations(data):
    date = lambda i: max(data.index) + i*timedelta(7)
    semaine =lambda i: duree_str(data.index[-i], data.index[-i]+timedelta(6))
    periode = lambda i, j: "semaine du "+semaine(i)+" à la semaine du "+semaine(j)
    txt = """
D'une semaine à l'autre les tendances de recherche des indices de Google Trends peuvent
fluctuer."""

    st.title("3 - Variations de l'indice")
    st.text(txt)

    st.header("a - Variations S/S-1 comparées à S-1/S-2")
    #st.text(f"{periode(-1,0)}")
    var = variations(data, date(-1), date(0), delta=timedelta(7)).tail(2)
    table = var.applymap(lambda x: "{:.1f}".format(x))
    #table.index = table.index.map(lambda t: duree_str(t, t+timedelta(days=6)))
    table.index = ["S-1/S-2", "S/S-1"]
    st.write(table)

    nom_x, nom_y, nom_z = "Pays", "Variation de l'indice Google Trends – %", "Semaine"
    st.pyplot(graph_volumes(var, nom_x, nom_y, nom_z))

    st.header("b - Variations S-1/S-2 comparées à S-2/S-3")
    #st.text(f"{periode(-2,-1)}")
    var = variations(data, date(-2), date(-1), delta=timedelta(7)).tail(2)
    table = var.applymap(lambda x: "{:.1f}".format(x))
    #table.index = table.index.map(lambda t: duree_str(t, t+timedelta(days=6)))
    table.index = ["S-2/S-3", "S-1/S-2"]
    st.write(table)

    nom_x, nom_y, nom_z = "Pays", "Variation de l'indice Google Trends – %", "Semaine"
    st.pyplot(graph_volumes(var, nom_x, nom_y, nom_z))
    
def connexion_drive(id_dossier):
    # Les données sont contenues dans un dossier sur le Drive de Google.
    # Le fichier 'client_secrets.json', contenant les informations de connexion
    # doit se trouver dans le dossier racine du projet.
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    # gauth.LoadCredentialsFile("mycreds.txt")
    # if gauth.credentials is None:
    #     # Authenticate if they're not there
    #     gauth.LocalWebserverAuth()
    # elif gauth.access_token_expired:
    #     # Refresh them if expired
    #     gauth.Refresh()
    # else:
    #     # Initialize the saved creds
    #     gauth.Authorize()
    # # Save the current credentials to a file
    # gauth.SaveCredentialsFile("mycreds.txt")
    
    # gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    # Une fois en possession du bon identifiant, c'est celui-ci qui sera inséré
    # dans la requête, pour obtenir, cette-fois, tous les fichiers.
    requete = "'" + id_dossier + "' in parents and trashed=false"
    donnees = drive.ListFile({'q': requete}).GetList()
    consultables = {}
    # Une fois dans le bon dossier, les différents fichiers sont parcourus.
    # S'il s'agit bien d'un csv, un tableau est créé de sa lecture puis ajouté
    # à la liste consultable pour la lecture des données.
    for donnee in donnees:
        if donnee['title'][-4:] == ".csv":
            print("Tentative de réception des données", donnee['title'])
            try:
                titre_brut = donnee['title'][:-4].split("-")
                titre = titre_brut[-2]
                consultables[titre] = donnee['id']
            except:
                pass 
    # Finalement, les données globales sont définies
    return consultables

def interface():
    # Connexion au dossier Drive lors du chargement des données
    # L'identifiant pour y accéder directement doit être spécifié
    # DATA_DRIVE = connexion_drive('1SoNgSF05srF1mDt_eBmWGa-rlEnhC02Y')
    DATA_DRIVE = "TEST"
    print("DATA:", DATA_DRIVE)
    
    entete()
    if st.sidebar.checkbox("Introduction", value=True):
        introduction()

    selection_mode_analyse()

    ### ANALYSE GLOBALE
    if mode == "Générique":
        fichier = choix_fichier_donnees(DATA_DRIVE)
        try:
            # Données brutes
            data = lecture_donnees(fichier, DATA_DRIVE)

            ### 1 - LES TOPS
            if st.sidebar.checkbox("1 - Les tops") and fichier != "None":
                visualisation_tops(data)
            
            ### 2 - LES VOLUMES
            if st.sidebar.checkbox("2 - Les volumes") and fichier != "None":
                visualisation_volumes(data)
    
            ### 3 - LES VARIATIONS
            if st.sidebar.checkbox("3 - Les variations") and fichier != "None":
                visualisation_variations(data)
    
            # COMMENTAIRE à inclure dans le rapport
            #if st.checkbox("Voulez-vous mettre un commentaire?"):
            #    commentaire_1 = st.text_area("Commentaire", "")
    
        except:
            pass

    ### ANALYSE PAR PAYS
    if mode == "Par pays":
        fichier = choix_fichier_donnees(DATA_DRIVE)
        try:
            # données brutes
            data = lecture_donnees(fichier, DATA_DRIVE)
    
            # Date d'analyse
            txt = "Date d'analyse"
            date2 = st.sidebar.date_input(txt,value=max(data.index))

            # Moyennes des volumes sur 2, 4 et 12 semaines, triés par ordre 
            # décroissant
            moyennes = {}
            for i in [2, 4, 12]:
                date1 = date2-i*timedelta(7)
                moyennes[i] = data[(data.index>date1) & (data.index<=date2)].mean()
                moyennes[i] = moyennes[i].sort_values(ascending=False)
                moyennes[i].name = "TOP "+str(i)+" SEMAINES"

            ### 1 - LES TOPS
            if st.sidebar.checkbox("1- Les tops") and fichier != "None":
                st.title("1 - Les tops tendances de recherche")
                txt = f"""
Les valeurs moyennes des tendances de recherche de Google Trends sont classées,
sur des périodes, de respectivement:
    - 2 semaines, du {duree_str(date2- 2*timedelta(7), date2)}
    - 4 semaines, du {duree_str(date2- 4*timedelta(7), date2)}
    - 12 semaines, du {duree_str(date2-12*timedelta(7), date2)}"""
                st.text(txt)

                st.header("a - Le top 6")
                cols, k = st.beta_columns(3), 0
                for i, k in zip([2, 4, 12],[0,1,2]):
                    cols[k].table(moyennes[i].apply(arrondie_str).head(6))

                if st.checkbox("afficher les valeurs suivantes..."):
                    st.header("b - Les valeurs suivantes")
                    cols, k = st.beta_columns(3), 0
                    for i, k in zip([2, 4, 12],[0,1,2]):
                        cols[k].table(moyennes[i].apply(arrondie_str).iloc[7:])

                # # COMMENTAIRE à inclure dans le rapport
                # if st.checkbox("Voulez vous mettre un commentaire ?"):
                #     commentaire_2 = st.text_area("Commentaire", "")
           
            ### 2 - LES VOLUMES
            if st.sidebar.checkbox("2 - Les volumes des 3 dernières années du top 6"):
                st.title("2 - Comparaisons annuelles des tops 6")
                classements = ('Top 2 semaines', 'Top 4 semaines','Top 12 semaines')
                lissage    = st.sidebar.checkbox("Lissage") 
                classement = st.sidebar.radio("Classement: ", classements)

                if classement == 'Top 2 semaines':
                    for zone in moyennes[2].head(6).index:
                        st.pyplot(graph_3_ans(data, zone, lissage))
                if classement == 'Top 4 semaines':
                    for zone in moyennes[4].head(6).index:
                        st.pyplot(graph_3_ans(data, zone, lissage))
                if classement == 'Top 12 semaines':
                    for zone in moyennes[12].head(6).index:
                        st.pyplot(graph_3_ans(data, zone, lissage))


            ### 3 - LES VARIATIONS
            if st.sidebar.checkbox("3- Les variation des 3 dernières années du top 6"):
                st.text("En cours de refonte")

        except:
            pass

### VI - TESTS UNITAIRES
test = False

if test:
    print("lecture des données:")
    try:
        fichier = "../DE-IT-NL-GB-US-BE-CH-ES-FR_Generique-Paris-Hebdo_20210607_1049.csv"
        data = lecture_donnees(fichier)
    except:
        data = donnees_aleatoires(t0=datetime(2017, 6, 1), nb_semaines=4*53)
    print(data)
    
    print("\ntest d'écriture des noms de pays à patir des codes iso:")
    for x in ['FR', 'BE', 'IT', 'CH', 'NL', 'US', 'GB']:
        print("\tcode iso:", x, "=> nom du pays:", nom_pays(x))

    print("\ntest d'écriture d'une durée:")
    date1 = datetime(2021, 5,  9).date()
    date2 = datetime(2021, 5, 30).date()
    print("\tdu", date1, " au ", date2, ": ", duree_str(date1, date2))


### VII - PROGRAMME PRINCIPAL
interface()