variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["rabbitmq", "simple_server", "light", "cron", "s3", "chrome-vnc"]
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

target "uniscrap-builder" {
  context = "."
  dockerfile = "./dockerfiles/uniscrap/Dockerfile"
  target = "uniscrap-builder"
}

target "chrome-vnc" {
  contexts = {
    uniscrap-builder = "target:uniscrap-builder"
  }
  context = "./dockerfiles/uniscrap"
  target = "chrome-vnc"
  tags = ["danielgreen1806/amascrap-chrome-vnc:${TAG}"]
  platforms = ["linux/amd64"]
}
