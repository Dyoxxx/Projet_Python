import pytest
from TD4_Classes import Document, Author
from TD5_Classes import RedditDocument, ArxivDocument
from Corpus import Corpus
from Corpus_Analyzer import CorpusAnalyzer
from Evolution_Temporelle import mots_evolution_temporelle
import pandas as pd

def test_document():
    doc = Document("Titre", "Auteur", "2024/12/13", "url", "texte", "type")
    assert doc.titre == "Titre"
    assert doc.auteur == "Auteur"
    assert doc.date == "2024/12/13"
    assert doc.url == "url"
    assert doc.texte == "texte"
    assert doc.type == "type"

def test_author():
    author = Author("John Doe")
    author.add("Production 1")
    assert author.name == "John Doe"
    assert author.ndoc == 1
    assert "Production 1" in author.production

def test_reddit_document():
    reddit_doc = RedditDocument("Titre", "Auteur", "2024/12/13", "url", "texte", "Reddit", 10)
    assert reddit_doc.commentaire == 10
    assert reddit_doc.getType() == "Reddit"

def test_arxiv_document():
    arxiv_doc = ArxivDocument("Titre", "Auteur", "2024/12/13", "url", "texte", "Arxiv")
    assert arxiv_doc.getType() == "Arxiv"

def test_corpus_add_and_search():
    corpus = Corpus("TestCorpus")
    doc1 = Document("Title1", "Author1", "2024/12/13", "url1", "text1 keyword", "type1")
    corpus.add(doc1)

    results = corpus.search("keyword")
    assert len(results) == 1
    assert results[0][1] == "keyword"

def test_corpus_vocab_and_frequency():
    corpus = Corpus("TestCorpus")
    doc1 = Document("Title1", "Author1", "2024/12/13", "url1", "text1 keyword", "type1")
    doc2 = Document("Title2", "Author2", "2024/12/13", "url2", "text2 keyword extra", "type2")
    corpus.add(doc1)
    corpus.add(doc2)

    vocab = corpus.vocabulaire()
    assert "keyword" in vocab

    freq_df = corpus.calculer_freq()
    assert freq_df.loc["keyword", "Term Frequency"] == 2
    assert freq_df.loc["keyword", "Document Frequency"] == 2

def test_mots_evolution_temporelle():
    corpus = Corpus("TestCorpus")
    doc1 = Document("Title1", "Author1", "2024/12/13", "url1", "keyword text", "type1")
    doc2 = Document("Title2", "Author2", "2023/12/13", "url2", "another keyword", "type2")
    corpus.add(doc1)
    corpus.add(doc2)

    df = mots_evolution_temporelle(corpus, ["keyword"], "yearly")
    assert df.loc["2024", "keyword"] == 1
    assert df.loc["2023", "keyword"] == 1

def test_corpus_analyzer():
    corpus1 = Corpus("Corpus1")
    corpus2 = Corpus("Corpus2")
    doc1 = Document("Title1", "Author1", "2024/12/13", "url1", "text keyword", "type1")
    doc2 = Document("Title2", "Author2", "2024/12/14", "url2", "another text", "type2")
    corpus1.add(doc1)
    corpus2.add(doc2)

    analyzer = CorpusAnalyzer(corpus1, corpus2)
    vocab_comparison = analyzer.compare_vocab()

    assert "keyword" in vocab_comparison["specific_corpus1"]
    assert "another" in vocab_comparison["specific_corpus2"]

if __name__ == "__main__":
    pytest.main()
