# ADR-001 - Kafka vs Simple Queue

## Statut
Accepté

## Contexte
Le pipeline ingère des logs CloudTrail en temps réel. Il était nécessaire
d'intégrer un système pour transporter les events entre le producteur et
le consommateur de façon fiable et scalable.

## Décision
Apache Kafka a été choisi comme message broker pour sa replay capability, 
la possibilité de rejouer des events passés pour tester de nouveaux modèles
ML sans régénérer les données.

## Options considérées
- **RabbitMQ** : queue classique et simple, mais les messages sont supprimés
  après consommation, ce qui empêche le backtesting
- **AWS SQS** : service managé fiable, mais crée un couplage fort à AWS et
  ne supporte pas le replay natif
- **Apache Kafka** : rétention des messages configurable, replay possible,
  scalable horizontalement

## Conséquences
- Replay capability pour le backtesting des modèles ML  
- Découplage entre producteur et consommateur  
- Scalable horizontalement via les partitions  
- Complexité opérationnelle plus élevée que RabbitMQ  
- Overhead pour un usage single-node en développement