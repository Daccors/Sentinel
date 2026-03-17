variable "namespace" {
  description = "Kubernetes namespace for Sentinel"
  type        = string
  default     = "sentinel-tf"
}

variable "elasticsearch_image" {
  description = "Elasticsearch Docker image"
  type        = string
  default     = "elasticsearch:9.3.0"
}

variable "kafka_image" {
  description = "Kafka Docker image"
  type        = string
  default     = "confluentinc/cp-kafka:7.6.0"
}