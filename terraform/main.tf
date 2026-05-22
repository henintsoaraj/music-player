terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

resource "local_file" "player_config" {
  filename = "${path.module}/player_config.json"
  content  = jsonencode({
    app_name    = "music-player-devops"
    environment = "staging"
    services = {
      player     = { port = 8000 }
      redis      = { port = 6379 }
      prometheus = { port = 9090 }
      grafana    = { port = 3000 }
    }
  })
}

resource "local_file" "docker_env" {
  filename = "${path.module}/.env.production"
  content  = <<-EOT
    APP_NAME=music-player-devops
    ENVIRONMENT=production
    REDIS_HOST=redis
    PROMETHEUS_PORT=9090
    GRAFANA_PORT=3000
  EOT
}
