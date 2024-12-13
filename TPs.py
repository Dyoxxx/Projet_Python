# =============== PARTIE 1 =============
# =============== 1.1 : REDDIT ===============
# Library
import praw

# Fonction affichage hiérarchie dict
def showDictStruct(d):
    def recursivePrint(d, i):
        for k in d:
            if isinstance(d[k], dict):
                print("-"*i, k)
                recursivePrint(d[k], i+2)
            else:
                print("-"*i, k, ":", d[k])
    recursivePrint(d, 1)

# Identification
reddit = praw.Reddit(client_id='kfqrLNtwc9kmmcxahpjtew', client_secret='FpjTjHg5IwR1060lGdqcUVDzwGz8_w', user_agent='WebScrapping')

# Requête
limit = 100
hot_posts = reddit.subreddit('all').top(limit=limit)#.top("all", limit=limit)#

# Récupération du texte
docs = []
docs_bruts = []
afficher_cles = False
for i, post in enumerate(hot_posts):
    if i%10==0: print("Reddit:", i, "/", limit)
    if afficher_cles:  # Pour connaître les différentes variables et leur contenu
        for k, v in post.__dict__.items():
            pass
            print(k, ":", v)

    if post.selftext != "":  # Osef des posts sans texte
        pass
        #print(post.selftext)
    docs.append(post.selftext.replace("\n", " "))
    docs_bruts.append(("Reddit", post))

#print(docs)

# =============== 1.2 : ArXiv ===============
# Libraries
import urllib, urllib.request
import xmltodict

# Paramètres
query_terms = ["covid"]
max_results = 50

# Requête
url = f'http://export.arxiv.org/api/query?search_query=all:{"+".join(query_terms)}&start=0&max_results={max_results}'
data = urllib.request.urlopen(url)

# Format dict (OrderedDict)
data = xmltodict.parse(data.read().decode('utf-8'))

#showDictStruct(data)

# Ajout résumés à la liste
for i, entry in enumerate(data["feed"]["entry"]):
    if i%10==0: print("ArXiv:", i, "/", limit)
    docs.append(entry["summary"].replace("\n", ""))
    docs_bruts.append(("ArXiv", entry))
    #showDictStruct(entry)

# =============== 1.3 : Exploitation ===============
print(f"# docs avec doublons : {len(docs)}")
docs = list(set(docs))
print(f"# docs sans doublons : {len(docs)}")

for i, doc in enumerate(docs):
    print(f"Document {i}\t# caractères : {len(doc)}\t# mots : {len(doc.split(' '))}\t# phrases : {len(doc.split('.'))}")
    if len(doc)<100:
        docs.remove(doc)

longueChaineDeCaracteres = " ".join(docs)

# =============== PARTIE 2 =============
# =============== 2.1, 2.2 : CLASSE DOCUMENT ===============
from TD4_Classes import Document
from TD5_Classes import RedditDocument, ArxivDocument

# =============== 2.3 : MANIPS ===============
import datetime
collection_reddit = []
collection_arxiv = []
for nature, doc in docs_bruts:
    if nature == "ArXiv":  # Les fichiers de ArXiv ou de Reddit sont pas formatés de la même manière à ce stade.
        #showDictStruct(doc)

        titre = doc["title"].replace('\n', '')  # On enlève les retours à la ligne
        try:
            authors = ", ".join([a["name"] for a in doc["author"]])  # On fait une liste d'auteurs, séparés par une virgule
        except:
            authors = doc["author"]["name"]  # Si l'auteur est seul, pas besoin de liste
        summary = doc["summary"].replace("\n", "")  # On enlève les retours à la ligne
        date = datetime.datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")  # Formatage de la date en année/mois/jour avec librairie datetime
        type = "ArXiv"
        # Partie 3
        doc_classe = ArxivDocument(titre, authors, date, doc["id"], summary, type)  # Création du Document
        collection_arxiv.append(doc_classe)  # Ajout du Document à la liste.

    elif nature == "Reddit":
        #print("".join([f"{k}: {v}\n" for k, v in doc.__dict__.items()]))
        titre = doc.title.replace("\n", '')
        auteur = str(doc.author)
        date = datetime.datetime.fromtimestamp(doc.created).strftime("%Y/%m/%d")
        url = "https://www.reddit.com/"+doc.permalink
        texte = doc.selftext.replace("\n", "")
        #rajout des commentaire
        commentaire = 0
        commentaire = doc.num_comments
        type = "Reddit"
        # Partie 3
        doc_classe = RedditDocument(titre, auteur, date, url, texte, type, commentaire)

        collection_reddit.append(doc_classe)

# Création de l'index de documents
id2doc_arxiv = {}
for i, doc in enumerate(collection_arxiv):
    id2doc_arxiv[i] = doc.titre

id2doc_reddit = {}
for i, doc in enumerate(collection_reddit):
    id2doc_reddit[i] = doc.titre

# =============== 2.4, 2.5 : CLASSE AUTEURS ===============
from TD4_Classes import Author

# =============== 2.6 : DICT AUTEURS ===============
authors_arxiv = {}
aut2id_arxiv = {}
num_auteurs_vus_arxiv = 0

authors_reddit = {}
aut2id_reddit = {}
num_auteurs_vus_reddit = 0

# Création de la liste+index des Auteurs
for doc in collection_arxiv:
    if doc.auteur not in aut2id_arxiv:
        num_auteurs_vus_arxiv += 1
        authors_arxiv[num_auteurs_vus_arxiv] = Author(doc.auteur)
        aut2id_arxiv[doc.auteur] = num_auteurs_vus_arxiv

    authors_arxiv[aut2id_arxiv[doc.auteur]].add(doc.texte)
'''
for doc in collection_reddit:
    if doc.auteur not in aut2id_reddit:
        num_auteurs_vus_reddit += 1
        authors_reddit[num_auteurs_vus_reddit] = Author(doc.auteur)
        aut2id_reddit[doc.auteur] = num_auteurs_vus_reddit

    authors_arxiv[aut2id_arxiv[doc.auteur]].add(doc.texte)
'''
# =============== 2.7, 2.8 : CORPUS ===============
from Corpus import Corpus
corpus_arxiv = Corpus("Mon corpus arxiv")

corpus_reddit = Corpus("Mon corpus reddit")

# Construction du corpus à partir des documents
for doc in collection_arxiv:
    corpus_arxiv.add(doc)
#corpus.show(tri="abc")
#print(repr(corpus))

for doc in collection_reddit:
    corpus_reddit.add(doc)


# =============== PARTIE 6 =============

# Recherche d'un mot spécifique dans le corpus
mot_cle = "machine"  # Exemple : chercher le mot "machine"
resultats_search = corpus_arxiv.search(mot_cle)
resultats_concorde = corpus_arxiv.concorde(mot_cle, 50)

# Affichage des résultats
print(f"Occurrences du mot '{mot_cle}' trouvées dans le corpus :")
for doc_id, mot_trouve in resultats_search:
    print(f"Document ID: {doc_id}, Mot trouvé: {mot_trouve}")

print(f"Occurrences du mot '{mot_cle}' trouvées dans le corpus :")
print(resultats_concorde)


print(corpus_arxiv.vocabulaire())
print(corpus_arxiv.calculer_freq())

# =============== PARTIE 7 =============
from Search_Engine import SearchEngine

moteur = SearchEngine(corpus_arxiv)

# Effectuer une recherche
query = "machine learning"
top_k = 5
resultats = moteur.search(query, top_k)

print("Résultats de la recherche :")
print(resultats)

# cette partie est laisser à la fin car on supprime notre variable corpus déjà faite
# =============== 2.9 : SAUVEGARDE ===============
import csv

def sauvegarder_csv(collection, fichier_csv="corpus.csv"):
    # Ouverture du fichier en mode écriture
    with open(fichier_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Écriture de l'en-tête
        writer.writerow(["Titre", "Auteur", "Date", "URL/ID", "Texte", "Type"])
        
        # Écriture des données de chaque document
        for doc in collection:
            writer.writerow([doc.titre, doc.auteur, doc.date, doc.url, doc.texte, doc.type])

# Appel de la fonction pour sauvegarder la collection dans un fichier CSV
sauvegarder_csv(collection_arxiv, "corpus_arxiv.csv")
sauvegarder_csv(collection_reddit, "corpus_reddit.csv")

import pickle

# Sauvegarde au format pickle
with open("corpus_arxiv.pkl", "wb") as f:
    pickle.dump(corpus_arxiv, f)
    
with open("corpus_reddit.pkl", "wb") as f:
    pickle.dump(corpus_reddit, f)

# Supression de la variable "corpus"
del corpus_reddit


# test pour l'ajout d'une méthode permettant d'importer un corpus déjà fait

# Charger le corpus sauvegardé au format pickle meilleur méthode pour importer/créer la classe que csv
corpus_pickle = Corpus.from_pickle("corpus.pkl")

# Charger le corpus sauvegardé au format CSV de manière static un peu nul comme méthode
# corpus_csv = Corpus.from_csv("corpus.csv")





