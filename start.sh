#!/bin/bash
set -e


echo "🛡️  Sentinel — Deployment Script"
echo "======================================"
echo "1) Local development (Docker Compose)"
echo "2) Kubernetes (minikube)"
echo "3) Kubernetes + Terraform"
echo ""
read -p "Choose environment [1/2/3]: " choice

case $choice in
  1)
    echo "🚀 Starting local environment..."
    docker compose up -d
    sleep 10
    poetry install
    echo "✅ Done — Kibana: http://localhost:5601"
    ;;
  2)
    echo "🚀 Deploying to Kubernetes..."
    minikube start
    kubectl apply -f deploy/k8s/namespace.yml
    kubectl apply -f deploy/k8s/configmap.yml
    kubectl apply -f deploy/k8s/elasticsearch.yml
    kubectl apply -f deploy/k8s/kafka.yml
    kubectl apply -f deploy/k8s/sentinel.yml
    kubectl wait --for=condition=ready pod -l app=elasticsearch -n sentinel --timeout=120s
    kubectl wait --for=condition=ready pod -l app=kafka -n sentinel --timeout=120s
    echo "✅ Done"
    kubectl get pods -n sentinel
    ;;
  3)
    echo "🚀 Deploying with Terraform..."
    minikube start
    cd deploy/terraform
    terraform init
    terraform apply -auto-approve
    echo "✅ Done"
    ;;
  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac