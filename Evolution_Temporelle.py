import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import pandas as pd
from Corpus import Corpus

def mots_evolution_temporelle(corpus, mots_cles, periode='monthly'):
    """
    Analyse l'évolution temporelle des fréquences d'un ou plusieurs mots-clés dans un corpus.

    :param corpus: Instance de la classe Corpus.
    :param mots_cles: Liste de mots-clés à analyser.
    :param periode: Période d'agrégation ('monthly', 'yearly').
    """
    mots_cles = [mot.lower() for mot in mots_cles]  # Uniformiser les mots clés
    freq_temporelles = {mot: Counter() for mot in mots_cles}

    for doc_id, doc in corpus.id2doc.items():
        # Nettoyer le texte du document
        texte = corpus.nettoyer_texte(doc.texte)
        mots = texte.split()

        # Extraire la date
        if not doc.date:
            continue
        
        try:
            date = datetime.strptime(doc.date, "%Y/%m/%d")
        except ValueError:
            continue

        if periode == 'monthly':
            periode_key = f"{date.year}-{date.month:02d}"
        elif periode == 'yearly':
            periode_key = str(date.year)
        else:
            raise ValueError("Période non supportée : choisissez 'monthly' ou 'yearly'.")

        
    
        # Compter les mots clés dans ce document
        for mot in mots_cles:
            count = texte.count(mot)
            freq_temporelles[mot][periode_key] += mots.count(mot)

    # Créer un DataFrame pour visualisation
    data = []
    for mot, freqs in freq_temporelles.items():
        for periode_key, freq in freqs.items():
            data.append((mot, periode_key, freq))
    df = pd.DataFrame(data, columns=['Mot', 'Période', 'Fréquence'])
    df = df.pivot(index='Période', columns='Mot', values='Fréquence').fillna(0)
    
    return df

'''
# Exemple d'utilisation
mots_cles = ["machine", "learning"]
periode = 'yearly'
corpus = Corpus.from_pickle("corpus1.pkl")
df_temporelle = mots_evolution_temporelle(corpus, mots_cles, periode)
print(df_temporelle)
'''