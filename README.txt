Guide d’Utilisation
Installation
1.	Clonez le dépôt :
git clone <url-du-depot>
cd <nom-du-projet>
2.	Installez les dépendances Python :
pip install -r requirements.txt
Exécution de l'Application
1.	Lancez l'application :
streamlit run Interface_Streamlit.py
2.	Accédez à l'application via :
l'URL local ou l'URL Network affiché dans la console au moment de l'execution
Normalement l'application devrait se lancer toute seule
Exécution des Tests
•	Tests Python :
pytest test_scripts.py test_search_engine.py