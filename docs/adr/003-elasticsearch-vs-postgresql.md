# ADR-003 - Elasticsearch vs PostgreSQL

## Statut
Accepté

## Contexte
Le pipeline génère des millions d'events de sécurité à indexer et requêter.
Les cas d'usage principaux sont : recherche par utilisateur/IP/action,
agrégations temporelles, et visualisation dans un dashboard temps-réel.

## Décision
Elasticsearch a été retenu car les cas d'usage SecOps sont principalement
des recherches temporelles et des agrégations, exactement ce pour quoi
il est optimisé. Son intégration native avec Kibana évite également de
développer une couche de visualisation custom.

## Options considérées
- **PostgreSQL** : relationnel, ACID, mais requêtes full-text lentes
  sur de gros volumes et nécessite des outils tiers pour la visualisation
- **MongoDB** : document store flexible, mais pas optimisé pour
  l'analyse temporelle et les agrégations complexes
- **Elasticsearch** : optimisé pour la recherche full-text, les
  agrégations temporelles, intégration native avec Kibana

## Conséquences
- Requêtes temporelles très rapides sur des millions d'events  
- Dashboard Kibana intégré sans développement supplémentaire  
- Schéma flexible, pas besoin de migration si les fields évoluent  
- Pas de transactions ACID, pas adapté pour des données financières  
- Consommation mémoire élevée (minimum 512MB)  
- Pas de joins natifs entre index