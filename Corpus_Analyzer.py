from collections import Counter

class CorpusAnalyzer:
    def __init__(self, corpus1, corpus2):
        self.corpus1 = corpus1
        self.corpus2 = corpus2

    def compare_vocab(self):
        vocab1 = Counter(self.corpus1.nettoyer_texte(" ".join([doc.texte for doc in self.corpus1.id2doc.values()])).split())
        vocab2 = Counter(self.corpus2.nettoyer_texte(" ".join([doc.texte for doc in self.corpus2.id2doc.values()])).split())

        common_words = vocab1.keys() & vocab2.keys()
        specific_corpus1 = vocab1.keys() - vocab2.keys()
        specific_corpus2 = vocab2.keys() - vocab1.keys()

        return {
            "common": {word: (vocab1[word], vocab2[word]) for word in common_words},
            "specific_corpus1": {word: vocab1[word] for word in specific_corpus1},
            "specific_corpus2": {word: vocab2[word] for word in specific_corpus2}
        }