
from TD4_Classes import Author, Document
from TD5_Classes import RedditDocument, ArxivDocument
import re
import pandas as pd
import string
import pickle

class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.aut2id = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0

    def add(self, doc):
        if doc.auteur not in self.aut2id:
            self.naut += 1
            self.authors[self.naut] = Author(doc.auteur)
            self.aut2id[doc.auteur] = self.naut
        self.authors[self.aut2id[doc.auteur]].add(doc.texte)

        self.ndoc += 1
        self.id2doc[self.ndoc] = doc

    def show(self, n_docs=-1, tri="abc"):
        docs = list(self.id2doc.values())
        if tri == "abc":  # Tri alphabétique
            docs = list(sorted(docs, key=lambda x: x.titre.lower()))[:n_docs]
        elif tri == "123":  # Tri temporel
            docs = list(sorted(docs, key=lambda x: x.date))[:n_docs]

        print("\n".join(list(map(repr, docs))))

    def __repr__(self):
        docs = list(self.id2doc.values())
        docs = list(sorted(docs, key=lambda x: x.titre.lower()))

        return "\n".join(list(map(str, docs)))

    def search(self, keyword):
        results = []
        pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
        
        for doc_id, doc in self.id2doc.items():
            matches = pattern.findall(doc.texte)
            for match in matches:
                results.append((doc_id, match))
        
        return results
    
    def concorde(self, expression, context=30):
        pattern = re.compile(expression, re.IGNORECASE)
        rows = []

        for doc_id, doc in self.id2doc.items():
            matches = pattern.finditer(doc.texte)
            for match in matches:
                start_context = max(0, match.start() - context)
                end_context = min(len(doc.texte), match.end() + context)

                contexte_gauche = doc.texte[start_context:match.start()]
                motif_trouve = doc.texte[match.start():match.end()]
                contexte_droit = doc.texte[match.end():end_context]

                rows.append({
                    "contexte gauche": contexte_gauche.strip(),
                    "motif trouvé": motif_trouve.strip(),
                    "contexte droit": contexte_droit.strip(),
                })

        return pd.DataFrame(rows)
    
    def nettoyer_texte(self, chaine):
        chaine = chaine.lower()
        chaine = chaine.replace('\n', ' ')
        chaine = re.sub(r'[^\w\s]', ' ', chaine)
        chaine = re.sub(r'\d+', '', chaine)
        chaine = re.sub(r'\s+', ' ', chaine).strip()
        
        return chaine
    
    def vocabulaire(self):
        vocabulaire = set()
        for doc_id, doc in self.id2doc.items():
            texte_nettoye = self.nettoyer_texte(doc.texte)
            mots = texte_nettoye.split()
            vocabulaire.update(mots)
        return vocabulaire
    
    def calculer_freq(self):
        vocabulaire = self.vocabulaire()
        freq = {mot: {"Term Frequency": 0, "Document Frequency": 0} for mot in vocabulaire}

        for doc_id, doc in self.id2doc.items():
            texte_nettoye = self.nettoyer_texte(doc.texte)
            mots = texte_nettoye.split()
            mots_uniques = set(mots)
            
            for mot in mots:
                if mot in freq:
                    freq[mot]["Term Frequency"] += 1
            
            for mot in mots_uniques:
                if mot in freq:
                    freq[mot]["Document Frequency"] += 1

        freq_df = pd.DataFrame.from_dict(freq, orient='index')
        freq_df.index.name = "Mot"
        return freq_df
    
    def sauvegarder_vocabulaire(self, fichier_vocabulaire="vocabulaire.txt"):
        vocabulaire = self.vocabulaire()
        with open(fichier_vocabulaire, "w", encoding="utf-8") as f:
            for mot in sorted(vocabulaire):
                f.write(f"{mot}\n")
        print(f"Vocabulaire sauvegardé dans {fichier_vocabulaire}")

    def sauvegarder_frequences(self, fichier_frequences="frequences.csv"):
        freq_df = self.calculer_freq()
        freq_df.to_csv(fichier_frequences, index=True, encoding="utf-8")
        print(f"Fréquences sauvegardées dans {fichier_frequences}")
        
    # Méthode pour charger un corpus depuis un fichier pickle
    @staticmethod
    def from_pickle(fichier_pickle):
        with open(fichier_pickle, "rb") as f:
            corpus = pickle.load(f)
        print(f"Corpus chargé depuis {fichier_pickle}")
        return corpus

    @staticmethod # méthode moins quali a voir si on garde
    def from_csv(fichier_csv):
        df = pd.read_csv(fichier_csv)
        corpus = Corpus("Corpus chargé depuis CSV")
        for _, row in df.iterrows():
            # Forcer les valeurs NaN à être des chaînes vides
            titre = str(row["Titre"]) if not pd.isna(row["Titre"]) else ""
            auteur = str(row["Auteur"]) if not pd.isna(row["Auteur"]) else ""
            date = str(row["Date"]) if not pd.isna(row["Date"]) else ""
            url = str(row["URL/ID"]) if not pd.isna(row["URL/ID"]) else ""
            texte = str(row["Texte"]) if not pd.isna(row["Texte"]) else ""
            type_doc = str(row["Type"]) if not pd.isna(row["Type"]) else ""
            
            # Création des documents en fonction du type
            if type_doc == "Reddit":
                commentaire = int(row["Commentaire"]) if "Commentaire" in row and not pd.isna(row["Commentaire"]) else 0
                doc = RedditDocument(
                    titre=titre, auteur=auteur, date=date, url=url, texte=texte, type=type_doc, commentaire=commentaire
                )
            elif type_doc == "Arxiv":
                doc = ArxivDocument(
                    titre=titre, auteur=auteur, date=date, url=url, texte=texte, type=type_doc
                )
            else:
                doc = Document(
                    titre=titre, auteur=auteur, date=date, url=url, texte=texte, type=type_doc
                )
            corpus.add(doc)
        print(f"Corpus chargé depuis {fichier_csv}")
        return corpus
