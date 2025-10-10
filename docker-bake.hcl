variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["rabbitmq", "simple_server", "light", "cron", "s3"]
}

target "rabbitmq" {
  context = "./dockerfiles/msgbroker"
  tags = ["danielgreen1806/amascrap-rabbitmq:${TAG}"]
}

target "simple_server" {
  context = "./dockerfiles/simple_server"
  tags = ["danielgreen1806/amascrap-simple_server:${TAG}"]
}

target "light" {
  context = "./dockerfiles/light"
  tags = ["danielgreen1806/amascrap-light:${TAG}"]
}

target "cron" {
  context = "./dockerfiles/cron"
  tags = ["danielgreen1806/amascrap-cron:${TAG}"]
}

target "s3" {
  context = "./dockerfiles/s3"
  tags = ["danielgreen1806/amascrap-s3:${TAG}"]
}
