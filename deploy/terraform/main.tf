terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}

resource "kubernetes_namespace" "sentinel" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_config_map" "sentinel_config" {
  metadata {
    name      = "sentinel-config"
    namespace = kubernetes_namespace.sentinel.metadata[0].name
  }

  data = {
    KAFKA_URL         = "kafka-service:9092"
    ELASTICSEARCH_URL = "http://elasticsearch-service:9200"
  }
}