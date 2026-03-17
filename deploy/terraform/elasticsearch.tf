resource "kubernetes_deployment" "elasticsearch" {
  metadata {
    name      = "elasticsearch"
    namespace = kubernetes_namespace.sentinel.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "elasticsearch"
      }
    }

    template {
      metadata {
        labels = {
          app = "elasticsearch"
        }
      }

      spec {
        container {
          name  = "elasticsearch"
          image = var.elasticsearch_image

          env {
            name  = "discovery.type"
            value = "single-node"
          }
          env {
            name  = "xpack.security.enabled"
            value = "false"
          }
          env {
            name  = "ES_JAVA_OPTS"
            value = "-Xms512m -Xmx512m"
          }

          port {
            container_port = 9200
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "elasticsearch" {
  metadata {
    name      = "elasticsearch-service"
    namespace = kubernetes_namespace.sentinel.metadata[0].name
  }

  spec {
    selector = {
      app = "elasticsearch"
    }

    port {
      port        = 9200
      target_port = 9200
    }
  }
}