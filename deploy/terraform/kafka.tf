resource "kubernetes_deployment" "kafka" {
  metadata {
    name      = "kafka"
    namespace = kubernetes_namespace.sentinel.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "kafka"
      }
    }

    template {
      metadata {
        labels = {
          app = "kafka"
        }
      }

      spec {
        container {
          name  = "kafka"
          image = var.kafka_image

          security_context {
            run_as_user = 0
          }

          env {
            name  = "KAFKA_NODE_ID"
            value = "1"
          }
          env {
            name  = "KAFKA_PROCESS_ROLES"
            value = "broker,controller"
          }
          env {
            name  = "KAFKA_LISTENERS"
            value = "PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093"
          }
          env {
            name  = "KAFKA_ADVERTISED_LISTENERS"
            value = "PLAINTEXT://kafka-service:9092"
          }
          env {
            name  = "KAFKA_CONTROLLER_LISTENER_NAMES"
            value = "CONTROLLER"
          }
          env {
            name  = "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR"
            value = "1"
          }
          env {
            name  = "KAFKA_LOG_DIRS"
            value = "/tmp/kafka-logs"
          }
          env {
            name  = "CLUSTER_ID"
            value = "MkU3OEVBNTcwNTJENDM2Qk"
          }
          env {
            name  = "KAFKA_CONTROLLER_QUORUM_VOTERS"
            value = "1@localhost:9093"
          }

          port {
            container_port = 9092
          }

          volume_mount {
            name       = "kafka-logs"
            mount_path = "/tmp/kafka-logs"
          }
        }

        volume {
          name = "kafka-logs"
          empty_dir {}
        }
      }
    }
  }
}

resource "kubernetes_service" "kafka" {
  metadata {
    name      = "kafka-service"
    namespace = kubernetes_namespace.sentinel.metadata[0].name
  }

  spec {
    selector = {
      app = "kafka"
    }

    port {
      port        = 9092
      target_port = 9092
    }
  }
}