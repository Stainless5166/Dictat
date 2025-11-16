# Terraform Variables for Digital Ocean Deployment

variable "do_token" {
  description = "Digital Ocean API token"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "dictat"
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "region" {
  description = "Digital Ocean region (lon1 for London, closest to Isle of Man)"
  type        = string
  default     = "lon1"
}

variable "droplet_size" {
  description = "Droplet size (s-2vcpu-4gb recommended minimum)"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "droplet_image" {
  description = "Droplet image (Ubuntu 22.04 LTS)"
  type        = string
  default     = "ubuntu-22-04-x64"
}

variable "volume_size" {
  description = "Storage volume size in GB"
  type        = number
  default     = 100

  validation {
    condition     = var.volume_size >= 10 && var.volume_size <= 1000
    error_message = "Volume size must be between 10 and 1000 GB."
  }
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key for droplet access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "allowed_ssh_ips" {
  description = "List of IP addresses allowed to SSH (restrict in production)"
  type        = list(string)
  default     = ["0.0.0.0/0", "::/0"]  # TODO: Restrict in production
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "enable_monitoring" {
  description = "Enable Digital Ocean monitoring"
  type        = bool
  default     = true
}

variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

# Database variables (if using managed database)
variable "database_size" {
  description = "Database cluster size"
  type        = string
  default     = "db-s-1vcpu-1gb"
}

# Tags
variable "tags" {
  description = "Additional tags for resources"
  type        = list(string)
  default     = ["dictat", "medical", "gdpr-compliant"]
}
