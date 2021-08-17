import pandas as pd
from io import StringIO

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive



"""Mise en place des identifications. 'client_secrets.json', contenant les
informations doit se trouver dans le dossier racine."""
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

"""Recherche du dossier contenant les données brutes"""
fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
tourisme_dossier = None
for file in fileList:
  # print('Title: %s, ID: %s' % (file['title'], file['id']))
  if(file['title'] == "tourisme_doc"):
      fileID = file['id']
      tourisme_dossier = file
      # print('Nom du dossier: %s, ID: %s' % (tourisme_dossier['title'],
      #                              tourisme_dossier['id']))
      
"""Une fois en possession du bon identifiant, c'est celui-ci qui sera inséré
dans la requête, pour obtenir, cette-fois, tous les fichiers."""
requete = "'" + tourisme_dossier['id'] + "' in parents and trashed=false"
donnees = drive.ListFile({'q': requete}).GetList()
consultables = {}

for donnee in donnees:
    """Une fois dans le bon dossier, les différents fichiers sont parcourus.
    S'il s'agit bien d'un csv, un tableau est créé de sa lecture puis ajouté
    à la liste consultable pour la lecture des données."""
    # print('Nom: %s, ID: %s' % (donnee['title'], donnee['id']))
    if donnee['title'][-4:] == ".csv":
        try:
            # print("C'est un csv!", donnee['title'])
            contenu = donnee.GetContentString()
            tableau = pd.read_csv(StringIO(contenu), sep=";")
            titre = tableau.columns[0]
            consultables[titre] = tableau
        except:
            pass
        
print(consultables)