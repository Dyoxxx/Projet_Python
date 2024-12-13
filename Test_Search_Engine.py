import unittest
from Corpus import Corpus
from Search_Engine import SearchEngine
from TD4_Classes import Document
from Corpus_Analyzer import CorpusAnalyzer
from Evolution_Temporelle import mots_evolution_temporelle

class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        # Préparer un premier corpus fictif pour les tests
        self.corpus1 = Corpus("Test Corpus 1")
        self.corpus1.add(Document(titre="Doc1", auteur="Author1", date="2022/01/01", texte="machine learning is amazing"))
        self.corpus1.add(Document(titre="Doc2", auteur="Author2", date="2023/01/01", texte="deep learning and machine learning"))
        self.corpus1.add(Document(titre="Doc3", auteur="Author3", date="2024/01/01", texte="artificial intelligence powers machine learning"))

        # Préparer un second corpus fictif pour les comparaisons
        self.corpus2 = Corpus("Test Corpus 2")
        self.corpus2.add(Document(titre="Doc4", auteur="Author4", date="2025/01/01", texte="machine vision is different"))
        
        # Initialiser le moteur de recherche
        self.engine = SearchEngine(self.corpus1)

        # Initialiser CorpusAnalyzer avec deux corpus
        self.analyzer = CorpusAnalyzer(self.corpus1, self.corpus2)

    def test_build_vocab(self):
        # Vérifie que le vocabulaire est construit correctement
        vocab = self.engine.vocab
        self.assertIn("machine", vocab)
        self.assertIn("learning", vocab)
        self.assertEqual(vocab["machine"]["TF"], 3)
        self.assertEqual(vocab["learning"]["DF"], 3)

    def test_tfidf_matrix(self):
        # Vérifie que la matrice TF-IDF est construite
        self.assertEqual(self.engine.mat_tfidf.shape, (3, len(self.engine.vocab)))

    def test_search_tfidf(self):
        # Test de la recherche avec TF-IDF
        results = self.engine.search("machine learning", top_k=2)
        self.assertEqual(len(results), 2)
        self.assertIn("Doc1", results["Titre"].values)

    def test_search_bm25(self):
        # Test de la recherche avec BM25
        results = self.engine.search_bm25("machine learning", top_k=2)
        self.assertEqual(len(results), 2)
        self.assertIn("Doc1", results["Titre"].values)

    def test_temporal_analysis(self):
        # Appel à la fonction mots_evolution_temporelle
        temporal_data = mots_evolution_temporelle(self.corpus1, ["machine", "learning"], periode="yearly")

        # Vérification que le DataFrame n'est pas vide
        self.assertGreaterEqual(len(temporal_data), 1)
        
        # Vérification que les colonnes incluent les mots-clés attendus
        self.assertIn("machine", temporal_data.columns)
        self.assertIn("learning", temporal_data.columns)
        
        # Vérification que l'index contient la période attendue
        self.assertIn("2023", temporal_data.index.astype(str))


    def test_comparative_analysis(self):
        # Test de la comparaison de deux corpus
        comparison = self.analyzer.compare_vocab()
        common = comparison["common"]
        specific1 = comparison["specific_corpus1"]
        specific2 = comparison["specific_corpus2"]
        

        self.assertIn("machine", common)
        self.assertIn("learning", specific1)
        self.assertIn("vision", specific2)

if __name__ == "__main__":
    unittest.main()
