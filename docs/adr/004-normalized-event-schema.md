# ADR-004 - Normalisation ECS vs Format Custom

## Statut
Accepté

## Contexte
Les logs CloudTrail ont un format spécifique AWS avec des champs comme
"eventName", "userIdentity", "awsRegion". Il fallait décider comment
représenter les events en interne pour que le reste du pipeline soit
indépendant de la source des logs.

## Décision
Un format interne normalisé ("NormalizedEvent") a été créé, indépendant
du format AWS. Seul le parseur connaît le format CloudTrail, le reste
du pipeline travaille uniquement avec "NormalizedEvent".

## Options considérées
- **Format brut CloudTrail** : simple à implémenter, mais couplage fort
  à AWS, tout le pipeline dépendrait du format AWS
- **Elastic Common Schema (ECS)** : standard industrie, mais complexe
  à implémenter complètement et sur-dimensionné pour ce projet
- **Format interne normalisé** : plus simple, indépendant d'AWS,
  extensible à d'autres sources de logs

## Conséquences
- Découplage total entre la source des logs et le pipeline  
- Ajout d'une nouvelle source (GCP, Azure) sans modifier le pipeline  
- Modèle Pydantic typé — validation automatique des données  
- Couche de transformation supplémentaire à maintenir  
- Perte de certains champs spécifiques AWS non inclus dans le modèle