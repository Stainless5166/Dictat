# Dictat Infrastructure on Digital Ocean
# TODO Phase 5: Configure for production deployment

terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }

  # TODO: Configure remote state storage
  # backend "s3" {
  #   endpoint                    = "lon1.digitaloceanspaces.com"
  #   region                      = "us-east-1"  # Required but not used
  #   bucket                      = "dictat-terraform-state"
  #   key                         = "production/terraform.tfstate"
  #   skip_credentials_validation = true
  #   skip_metadata_api_check     = true
  # }
}

provider "digitalocean" {
  token = var.do_token
}

# SSH Key for Droplet Access
resource "digitalocean_ssh_key" "dictat" {
  name       = "dictat-deployment-key"
  public_key = file(var.ssh_public_key_path)
}

# VPC for network isolation
resource "digitalocean_vpc" "dictat" {
  name     = "${var.project_name}-vpc"
  region   = var.region
  ip_range = "10.10.0.0/16"
}

# Main Droplet
resource "digitalocean_droplet" "dictat_app" {
  name   = "${var.project_name}-app-${var.environment}"
  region = var.region
  size   = var.droplet_size
  image  = var.droplet_image

  ssh_keys = [digitalocean_ssh_key.dictat.id]
  vpc_uuid = digitalocean_vpc.dictat.id

  tags = [
    "dictat",
    var.environment,
    "backend",
  ]

  # User data for initial setup
  user_data = file("${path.module}/scripts/cloud-init.yml")

  # TODO Phase 5: Add more configuration
  # - Enable monitoring
  # - Configure backups
  # - Set up firewall rules
}

# Block Storage Volume for persistent data
resource "digitalocean_volume" "dictat_storage" {
  name                    = "${var.project_name}-storage-${var.environment}"
  region                  = var.region
  size                    = var.volume_size
  initial_filesystem_type = "ext4"
  description             = "Persistent storage for audio files and database"

  tags = ["dictat", var.environment]
}

# Attach volume to droplet
resource "digitalocean_volume_attachment" "dictat_storage_attachment" {
  droplet_id = digitalocean_droplet.dictat_app.id
  volume_id  = digitalocean_volume.dictat_storage.id
}

# Firewall
resource "digitalocean_firewall" "dictat" {
  name = "${var.project_name}-firewall-${var.environment}"

  droplet_ids = [digitalocean_droplet.dictat_app.id]

  # SSH (restricted to specific IPs in production)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.allowed_ssh_ips
  }

  # HTTP
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # HTTPS
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow all outbound
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# TODO Phase 5: Add DNS records
# resource "digitalocean_domain" "dictat" {
#   name = var.domain_name
# }
#
# resource "digitalocean_record" "dictat_a" {
#   domain = digitalocean_domain.dictat.name
#   type   = "A"
#   name   = "@"
#   value  = digitalocean_droplet.dictat_app.ipv4_address
# }

# TODO Phase 5: Add database (managed PostgreSQL)
# resource "digitalocean_database_cluster" "dictat_postgres" {
#   name       = "${var.project_name}-db-${var.environment}"
#   engine     = "pg"
#   version    = "15"
#   size       = var.database_size
#   region     = var.region
#   node_count = 1
# }

# TODO Phase 5: Add load balancer for HA
# resource "digitalocean_loadbalancer" "dictat" {
#   name   = "${var.project_name}-lb-${var.environment}"
#   region = var.region
#
#   forwarding_rule {
#     entry_port     = 443
#     entry_protocol = "https"
#
#     target_port     = 8000
#     target_protocol = "http"
#
#     certificate_name = digitalocean_certificate.dictat.name
#   }
#
#   healthcheck {
#     port     = 8000
#     protocol = "http"
#     path     = "/health"
#   }
#
#   droplet_ids = [digitalocean_droplet.dictat_app.id]
# }

# Outputs
output "droplet_ip" {
  value       = digitalocean_droplet.dictat_app.ipv4_address
  description = "Public IP address of the droplet"
}

output "droplet_id" {
  value       = digitalocean_droplet.dictat_app.id
  description = "ID of the droplet"
}

output "volume_id" {
  value       = digitalocean_volume.dictat_storage.id
  description = "ID of the storage volume"
}

output "vpc_id" {
  value       = digitalocean_vpc.dictat.id
  description = "ID of the VPC"
}
