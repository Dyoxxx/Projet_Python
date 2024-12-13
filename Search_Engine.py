import numpy as np
from scipy.sparse import csr_matrix
import pandas as pd
from Corpus import Corpus

class SearchEngine:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.corpus = corpus
        self.k1 = k1  # Paramètre de réglage BM25
        self.b = b    # Paramètre de longueur des documents BM25
        self.vocab = self.build_vocab()
        self.avg_doc_len = np.mean([len(self.corpus.nettoyer_texte(doc.texte).split()) for doc in self.corpus.id2doc.values()])
        self.mat_tf, self.mat_tfidf = self.build_matrices()

    def build_vocab(self):
        vocab = {}
        words = sorted(self.corpus.vocabulaire())
        for i, word in enumerate(words):
            vocab[word] = {
                "id": i,
                "TF": 0,
                "DF": 0,
            }

        for doc_id, doc in self.corpus.id2doc.items():
            texte_nettoye = self.corpus.nettoyer_texte(doc.texte)
            mots = texte_nettoye.split()
            mots_uniques = set(mots)

            for mot in mots:
                if mot in vocab:
                    vocab[mot]["TF"] += 1

            for mot in mots_uniques:
                if mot in vocab:
                    vocab[mot]["DF"] += 1

        return vocab

    def build_matrices(self):
        num_docs = len(self.corpus.id2doc)
        num_terms = len(self.vocab)

        # Matrice TF
        data, rows, cols = [], [], []
        for doc_id, doc in self.corpus.id2doc.items():
            texte_nettoye = self.corpus.nettoyer_texte(doc.texte)
            mots = texte_nettoye.split()
            term_counts = {mot: mots.count(mot) for mot in set(mots)}

            for mot, count in term_counts.items():
                if mot in self.vocab:
                    rows.append(doc_id - 1)
                    cols.append(self.vocab[mot]["id"])
                    data.append(count)

        mat_tf = csr_matrix((data, (rows, cols)), shape=(num_docs, num_terms))

        # Calcul de TF-IDF
        tfidf_data = []
        for i, j, v in zip(rows, cols, data):
            df = self.vocab[list(self.vocab.keys())[j]]['DF']
            idf = np.log((1 + num_docs) / (1 + df)) + 1
            tfidf_data.append(v * idf)

        mat_tfidf = csr_matrix((tfidf_data, (rows, cols)), shape=(num_docs, num_terms))

        return mat_tf, mat_tfidf

    def search(self, query, top_k=5, method="tfidf"):
        if method == "tfidf":
            return self.search_tfidf(query, top_k)
        elif method == "bm25":
            return self.search_bm25(query, top_k)
        else:
            raise ValueError("Méthode de recherche non reconnue. Utilisez 'tfidf' ou 'bm25'.")

    def search_tfidf(self, query, top_k=5):
        query = self.corpus.nettoyer_texte(query).split()
        query_vec = np.zeros(len(self.vocab))

        for word in query:
            if word in self.vocab:
                query_vec[self.vocab[word]["id"]] += 1

        query_tfidf = query_vec / (np.linalg.norm(query_vec) + 1e-9)
        doc_tfidf = self.mat_tfidf.toarray()
        doc_norms = np.linalg.norm(doc_tfidf, axis=1, keepdims=True) + 1e-9
        similarities = np.dot(doc_tfidf, query_tfidf) / doc_norms.flatten()

        top_docs = np.argsort(-similarities)[:top_k]
        results = []

        for doc_id in top_docs:
            if similarities[doc_id] > 0:
                doc = self.corpus.id2doc[doc_id + 1]
                results.append({
                    "Titre": doc.titre,
                    "Auteur": doc.auteur,
                    "Date": doc.date,
                    "Score": similarities[doc_id]
                })

        return pd.DataFrame(results)

    def compute_bm25(self, query):
        query = self.corpus.nettoyer_texte(query).split()
        scores = np.zeros(len(self.corpus.id2doc))

        for word in query:
            if word in self.vocab:
                word_id = self.vocab[word]["id"]
                df = self.vocab[word]["DF"]
                idf = np.log((len(self.corpus.id2doc) - df + 0.5) / (df + 0.5) + 1)
                for doc_id, tf in enumerate(self.mat_tf[:, word_id].toarray().flatten()):
                    doc_len = len(self.corpus.nettoyer_texte(self.corpus.id2doc[doc_id + 1].texte).split())
                    score = idf * ((tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))))
                    scores[doc_id] += score

        return scores

    def search_bm25(self, query, top_k=5):
        scores = self.compute_bm25(query)
        top_docs = np.argsort(-scores)[:top_k]
        results = []

        for doc_id in top_docs:
            if scores[doc_id] > 0:
                doc = self.corpus.id2doc[doc_id + 1]
                results.append({
                    "Titre": doc.titre,
                    "Auteur": doc.auteur,
                    "Date": doc.date,
                    "Score": scores[doc_id]
                })

        return pd.DataFrame(results)

# Exemple d'utilisation
# moteur = SearchEngine(corpus)
# resultats_tfidf = moteur.search("machine learning", top_k=5, method="tfidf")
# resultats_bm25 = moteur.search("machine learning", top_k=5, method="bm25")
# print(resultats_tfidf)
# print(resultats_bm25)
