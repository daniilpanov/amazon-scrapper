variable "UNISCRAP_STOMP_HOST" {
  default = "msgbroker"
}

variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["rabbitmq", "app", "cron", "chrome-vnc"]
}

target "rabbitmq" {
  context = "./dockerfiles/msgbroker"
  tags = ["danielgreen1806/amascrap-rabbitmq:${TAG}"]
}

target "app" {
  context = "./app_main"
  tags = ["danielgreen1806/amascrap-app:${TAG}"]
}

target "cron" {
  context = "./cron"
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
