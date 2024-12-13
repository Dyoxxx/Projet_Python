import streamlit as st
import pandas as pd
from Corpus import Corpus
from Search_Engine import SearchEngine
from Corpus_Analyzer import CorpusAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import Evolution_Temporelle

# Configurer la page de l'application
st.set_page_config(page_title="Explorateur de Corpus", layout="wide")

# Titre de l'application
st.title("Explorateur de Corpus Documentaire")

# Barre latérale pour charger les corpus
st.sidebar.header("Chargement des Corpus")
corpus_files = st.sidebar.file_uploader("Téléchargez un ou plusieurs fichiers Pickle des corpus", type=["pkl"], accept_multiple_files=True, key="corpus_files")

# Charger les corpus si disponibles
corpus_list = []
if corpus_files:
    for i, file in enumerate(corpus_files):
        corpus = Corpus.from_pickle(file)
        corpus_name = file.name.split('.')[0]  # Utiliser le nom du fichier pour identifier le corpus
        corpus_list.append((corpus_name, corpus))

# Fonction générique pour explorer un corpus
def explorer_corpus(corpus_name, corpus):
    st.subheader(f"Exploration des Documents ({corpus_name})")
    tri = st.selectbox(f"Méthode de tri ({corpus_name})", ["abc", "123"], key=f"tri_{corpus_name}")
    n_docs = st.slider(f"Nombre de documents à afficher ({corpus_name})", 1, len(corpus.id2doc), 5, key=f"n_docs_{corpus_name}")

    if st.button(f"Afficher les documents ({corpus_name})", key=f"btn_docs_{corpus_name}"):
        documents = list(corpus.id2doc.values())
        documents.sort(key=lambda x: x.titre if tri == "abc" else x.date)

        data = [{
            "Titre": doc.titre,
            "Auteur": doc.auteur,
            "Date": doc.date,
            "Texte (extrait)": doc.texte[:200]
        } for doc in documents[:n_docs]]

        df_documents = pd.DataFrame(data)
        st.dataframe(df_documents)

# Fonction générique pour une recherche dans un corpus
def rechercher_corpus(corpus_name, corpus):
    st.subheader(f"Recherche dans le Corpus ({corpus_name})")
    query = st.text_input(f"Entrez votre requête ({corpus_name})", "machine learning", key=f"query_{corpus_name}")
    moteur = SearchEngine(corpus)
    moteur_choisi = st.radio(f"Choisissez un moteur de recherche ({corpus_name})", ["TF-IDF", "BM25"], index=0, key=f"moteur_{corpus_name}")
    top_k = st.slider(f"Nombre de résultats ({corpus_name})", 1, len(corpus.id2doc), 5, key=f"top_k_{corpus_name}")

    if st.button(f"Rechercher ({corpus_name})", key=f"btn_search_{corpus_name}"):
        resultats = moteur.search(query, top_k=top_k) if moteur_choisi == "TF-IDF" else moteur.search_bm25(query, top_k=top_k)
        st.write(resultats)

# Fonction générique pour afficher un nuage de mots
def nuage_de_mots_corpus(corpus_name, corpus):
    st.subheader(f"Nuage de mot du Corpus ({corpus_name})")
    nb_mots = st.slider(f"Nombre de mots à afficher ({corpus_name})", 1, 50, 5, key=f"nb_mots_{corpus_name}")
    display_button = st.button(f"Afficher le nuage de mot ({corpus_name})", key=f"nuage_btn_{corpus_name}")

    # Utiliser un conteneur pour maintenir l'affichage
    if display_button:
        texte_concatenated = " ".join([doc.texte for doc in corpus.id2doc.values()])
        wordcloud = WordCloud(background_color='white', max_words=nb_mots).generate(texte_concatenated)

        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

# Fonction pour afficher la concorde
def afficher_concorde(corpus_name, corpus):
    st.subheader(f"Concorde dans le Corpus ({corpus_name})")
    query = st.text_input(f"Expression à retrouver ({corpus_name})", "machine learning", key=f"concorde_query_{corpus_name}")
    context = st.slider(f"Nombre de mots dans le contexte ({corpus_name})", 0, 500, 50, step=5, key=f"concorde_context_{corpus_name}")
    if st.button(f"Afficher le résultat du concorde ({corpus_name})", key=f"btn_concorde_{corpus_name}"):
        resultats = corpus.concorde(query, context)
        st.write(resultats)

# Fonction pour analyser temporellement
def analyser_temporellement(corpus_name, corpus):
    st.subheader(f"Analyse Temporelle des Mots-Clés ({corpus_name})")
    mots_cles = st.text_input(f"Entrez les mots-clés séparés par une virgule ({corpus_name})", "machine, learning", key=f"temporel_mots_cles_{corpus_name}")
    periode = st.radio(f"Période ({corpus_name})", ["yearly", "monthly"], index=0, key=f"temporel_periode_{corpus_name}")

    if st.button(f"Analyser l'évolution temporelle ({corpus_name})", key=f"btn_temporel_{corpus_name}"):
        mots_cles = [mot.strip() for mot in mots_cles.split(",")]
        df_evolution = Evolution_Temporelle.mots_evolution_temporelle(corpus, mots_cles, periode)
        st.line_chart(df_evolution)

# Fonction pour trier le corpus
def trier_corpus(corpus_name, corpus):
    st.subheader(f"Tri du Corpus ({corpus_name})")
    query = st.text_input(f"Entrez votre requête (obligatoire) ({corpus_name})", "Machine", key=f"tri_query_{corpus_name}")
    auteur = st.text_input(f"Entrez un auteur (optionnel) ({corpus_name})", "", key=f"tri_auteur_{corpus_name}")
    type_source = st.text_input(f"Entrez un type de source (optionnel) ({corpus_name})", "", key=f"tri_type_{corpus_name}")
    date_debut = st.text_input(f"Date de début (YYYY-MM-DD, optionnel) ({corpus_name})", "", key=f"tri_date_debut_{corpus_name}")
    date_fin = st.text_input(f"Date de fin (YYYY-MM-DD, optionnel) ({corpus_name})", "", key=f"tri_date_fin_{corpus_name}")

    if st.button(f"Trier ({corpus_name})", key=f"btn_tri_{corpus_name}"):
        resultats = corpus.query_with_filters(query, auteur, type_source, date_debut, date_fin)
        st.write(resultats)

# Affichage des corpus dans des onglets
if not corpus_list:
    st.warning("Veuillez charger au moins un corpus pour commencer.")
else:
    tabs = st.tabs([corpus_name for corpus_name, _ in corpus_list])

    for tab, (corpus_name, corpus) in zip(tabs, corpus_list):
        with tab:
            st.header(f"Manipulations pour {corpus_name}")
            explorer_corpus(corpus_name, corpus)
            afficher_concorde(corpus_name, corpus)
            rechercher_corpus(corpus_name, corpus)
            trier_corpus(corpus_name, corpus)
            analyser_temporellement(corpus_name, corpus)
            nuage_de_mots_corpus(corpus_name, corpus)

# Comparaison entre deux corpus
if len(corpus_list) > 1:
    st.header("Analyse Comparative entre Deux Corpus")
    corpus_to_compare = st.selectbox(
        "Choisissez un corpus pour la comparaison",
        [corpus_name for corpus_name, _ in corpus_list],
        key="corpus_to_compare_1"
    )
    corpus_to_compare_with = st.selectbox(
        "Choisissez un corpus à comparer avec",
        [corpus_name for corpus_name, _ in corpus_list],
        key="corpus_to_compare_2"
    )

    if corpus_to_compare != corpus_to_compare_with:
        corpusA = next(corpus for name, corpus in corpus_list if name == corpus_to_compare)
        corpusB = next(corpus for name, corpus in corpus_list if name == corpus_to_compare_with)

        analyzer = CorpusAnalyzer(corpusA, corpusB)
        comparison = analyzer.compare_vocab()

        common_count = len(comparison["common"])
        specific1_count = len(comparison["specific_corpus1"])
        specific2_count = len(comparison["specific_corpus2"])

        labels = ["Mots Communs", corpus_to_compare, corpus_to_compare_with]
        counts = [common_count, specific1_count, specific2_count]

        st.subheader("Téléchargement des Vocabulaires et des Fréquences")
        col1, col2 = st.columns(2)
        
        with col1:
            vocab_corpus1 = pd.DataFrame(list(corpusA.vocabulaire()), columns=["Mots"])
            csv_voc_corpus1 = vocab_corpus1.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Télécharger le vocabulaire de {corpus_to_compare}",
                data=csv_voc_corpus1,
                file_name=f"vocabulaire_{corpus_to_compare}.csv",
                mime="text/csv"
            )
            vocab_corpus2 = pd.DataFrame(list(corpusB.vocabulaire()), columns=["Mots"])
            csv_voc_corpus2 = vocab_corpus2.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Télécharger le vocabulaire de {corpus_to_compare_with}",
                data=csv_voc_corpus2,
                file_name=f"vocabulaire_{corpus_to_compare_with}.csv",
                mime="text/csv"
            )
            # Graphique comparatif des vocabulaires
            
            st.subheader("Graphique de Comparaison des Vocabulaires")
            fig, ax = plt.subplots()
            ax.bar(labels, counts, color=["blue", "green", "orange"])
            ax.set_title("Comparaison de la taille des Vocabulaires")
            ax.set_ylabel("Nombre de Mots")
            st.pyplot(fig)
            
        with col2:
            frequence_corpus1 = corpusA.calculer_freq()
            csv_freq_corpus1 = frequence_corpus1.to_csv(index=True).encode('utf-8')
            st.download_button(
                label=f"Télécharger les fréquences de {corpus_to_compare}",
                data=csv_freq_corpus1,
                file_name=f"frequence_{corpus_to_compare}.csv",
                mime="text/csv"
            )
            frequence_corpus2 = corpusB.calculer_freq()
            csv_freq_corpus2 = frequence_corpus2.to_csv(index=True).encode('utf-8')
            st.download_button(
                label=f"Télécharger les fréquences de {corpus_to_compare_with}",
                data=csv_freq_corpus2,
                file_name=f"frequence_{corpus_to_compare_with}.csv",
                mime="text/csv"
            )
            
            # Graphique comparatif des fréquences des mots
            st.subheader("Graphique de Comparaison des Fréquences des Mots")

            # Calcul des fréquences des mots
            common_freq = sum(sum(pair) for pair in comparison["common"].values())
            specific1_freq = sum(comparison["specific_corpus1"].values())
            specific2_freq = sum(comparison["specific_corpus2"].values())

            # Préparer les données pour le graphique
            labels = ["Mots Communs", corpus_to_compare, corpus_to_compare_with]
            counts = [common_freq, specific1_count, specific2_count]

            # Création du graphique
            fig, ax = plt.subplots()
            ax.bar(labels, counts, color=["blue", "green", "orange"])
            ax.set_title("Comparaison des Fréquences des Mots")
            ax.set_ylabel("Fréquence Totale des Mots")

            # Afficher le graphique dans Streamlit
            st.pyplot(fig)
        
        st.subheader(f"Analyse Temporelle des Mots-Clés ({corpus_to_compare}, {corpus_to_compare_with})")
        mot_cle = st.text_input(f"Entrez un mot-clé ({corpus_to_compare}, {corpus_to_compare_with})", "machine", key=f"temporel_mots_cles_{corpus_to_compare},{corpus_to_compare_with}")
        periode = st.radio(f"Période ({corpus_to_compare}, {corpus_to_compare_with})", ["yearly", "monthly"], index=0, key=f"temporel_periode_{corpus_to_compare},{corpus_to_compare_with}")

        if st.button(f"Analyser l'évolution temporelle ({corpus_to_compare}, {corpus_to_compare_with})"):
            # Calculer les fréquences pour chaque corpus
            df_corpus1 = Evolution_Temporelle.mots_evolution_temporelle(corpusA, [mot_cle], periode)
            df_corpus2 = Evolution_Temporelle.mots_evolution_temporelle(corpusB, [mot_cle], periode)

            # Renommer les colonnes pour éviter les conflits
            df_corpus1 = df_corpus1.rename(columns={mot_cle: f"{mot_cle} ({corpus_to_compare})"})
            df_corpus2 = df_corpus2.rename(columns={mot_cle: f"{mot_cle} ({corpus_to_compare_with})"})

            # Fusionner les deux DataFrames sur l'index (Période)
            df_combined = pd.merge(df_corpus1, df_corpus2, left_index=True, right_index=True, how="outer").fillna(0)
            st.line_chart(df_combined)



