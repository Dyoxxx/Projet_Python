import numpy as np
from scipy.sparse import csr_matrix
import pandas as pd
from Corpus import Corpus

class SearchEngine:
    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        self.vocab = self.build_vocab()
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

        # On calcule TF-IDF
        tfidf_data = []
        for i, j, v in zip(rows, cols, data):
            df = self.vocab[list(self.vocab.keys())[j]]["DF"]
            idf = np.log((1 + num_docs) / (1 + df)) + 1
            tfidf_data.append(v * idf)

        mat_tfidf = csr_matrix((tfidf_data, (rows, cols)), shape=(num_docs, num_terms))

        return mat_tf, mat_tfidf

    def search(self, query, top_k=5):
        # On 'vectorize' 
        query = self.corpus.nettoyer_texte(query).split()
        query_vec = np.zeros(len(self.vocab))

        for word in query:
            if word in self.vocab:
                query_vec[self.vocab[word]["id"]] += 1

        # On calcule les cosinus
        query_tfidf = query_vec / (np.linalg.norm(query_vec) + 1e-9)
        doc_tfidf = self.mat_tfidf.toarray()
        doc_norms = np.linalg.norm(doc_tfidf, axis=1, keepdims=True) + 1e-9
        similarities = np.dot(doc_tfidf, query_tfidf) / doc_norms.flatten()

        # On prend les poids les plus importants
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