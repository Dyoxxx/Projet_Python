# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 16:04:10 2024

@author: Thibaud
"""

from TD4_Classes import Document 

# Partie 1
class RedditDocument(Document):
    
    def __init__(self, titre="", auteur="", date="", url="", texte="", type="Reddit", commentaire = 0):
        super().__init__(titre=titre, auteur=auteur, date=date, url=url, texte=texte, type=type)
        self.commentaire = commentaire
    
    def __repr__(self):
        return f"Titre : {self.titre}\tAuteur : {self.auteur}\tDate : {self.date}\tURL : {self.url}\tTexte : {self.texte}\tCommentaire : {self.commentaire}"

    def __str__(self):
        super().__str__()
    
    def getType(self):
        return(self.type)
    
# Partie 2
class ArxivDocument(Document):
    
    def __init__(self, titre="", auteur="[]", date="", url="", texte="", type="Arxiv"):
        super().__init__(titre=titre, auteur=auteur, date=date, url=url, texte=texte, type=type)

    def __str__(self):
        super().__str__()
        
    def getType(self):
        return(self.type)
    
# Partie 4.2
class DocumentGenerator:
    
    @staticmethod
    def factory(type, titre):
        if type == 'Reddit': return RedditDocument(titre)
        if type == 'Arxiv': return ArxivDocument(titre)
        
        assert 0, 'Erreur : ' + type #si le type entré est inconnu