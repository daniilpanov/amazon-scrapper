variable "UNISCRAP_STOMP_HOST" {
  default = "msgbroker"
}

variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["rabbitmq", "light", "cron", "chrome-vnc"]
}

target "rabbitmq" {
  context = "./dockerfiles/msgbroker"
  tags = ["danielgreen1806/amascrap-rabbitmq:${TAG}"]
}

target "light" {
  context = "./dockerfiles/light"
  tags = ["danielgreen1806/amascrap-light:${TAG}"]
}

target "cron" {
  context = "./dockerfiles/cron"
  tags = ["danielgreen1806/amascrap-cron:${TAG}"]
}

target "uniscrap-builder" {
  context = "."
  dockerfile = "./dockerfiles/uniscrap/Dockerfile"
  target = "uniscrap-builder"
  args = {
    VITE_STOMP_HOST = "${UNISCRAP_STOMP_HOST}"
  }
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
