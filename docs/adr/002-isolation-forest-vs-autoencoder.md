# ADR-002 - Isolation Forest vs Autoencoder

## Statut
Accepté

## Contexte
Le projet nécessitait un algorithme de détection d'anomalies non-supervisé
sur des données comportementales IAM, sans labels d'entraînement disponibles.

## Décision
L'Isolation Forest a été retenu en raison du faible nombre de features
comportementales (5 features) et de son interprétabilité, en SecOps,
pouvoir expliquer pourquoi un event est suspect est aussi important que
de le détecter.

## Options considérées
- **Autoencoder** : puissant sur des données complexes, mais nécessite
  beaucoup de données d'entraînement et de puissance de calcul
- **One-Class SVM** : bon pour les petits datasets mais lent à grande
  échelle et sensible au choix du kernel
- **Isolation Forest** : entraînement rapide, interprétable, efficace
  sur des données tabulaires peu dimensionnelles

## Conséquences
- Entraînement et scoring rapides (< 1s)  
- Interprétable, score d'anomalie explicable à un analyste SOC  
- Pas besoin de labels, apprentissage non-supervisé  
- Moins performant sur des données très haute dimension  
- Sensible à la qualité des données d'entraînement