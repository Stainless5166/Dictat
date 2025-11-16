# Dictat Deployment Guide

Comprehensive guide for deploying Dictat to Digital Ocean (Isle of Man/UK GDPR jurisdiction).

## Prerequisites

- Digital Ocean account
- Terraform installed (>= 1.0)
- Docker and Docker Compose installed locally
- SSH key generated
- Domain name (optional)

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/dictat.git
cd dictat
```

### 2. Create Environment File

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Local Services

```bash
docker-compose up -d
```

### 4. Run Database Migrations

```bash
# TODO Phase 1: Once Alembic is configured
# docker-compose exec backend alembic upgrade head
```

### 5. Access Application

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000 (TODO Phase 3)

## Production Deployment to Digital Ocean

### Phase 5: Infrastructure Setup

#### 1. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your Digital Ocean token and settings
```

#### 2. Initialize Terraform

```bash
terraform init
```

#### 3. Plan Infrastructure

```bash
terraform plan
```

#### 4. Apply Infrastructure

```bash
terraform apply
```

This creates:
- VPC for network isolation
- Droplet (4GB RAM minimum)
- Block storage volume (100GB)
- Firewall rules
- SSH access

#### 5. Note Outputs

```bash
terraform output
# Save the droplet IP address
```

### Phase 5: Application Deployment

#### 1. SSH to Droplet

```bash
ssh root@<droplet-ip>
```

#### 2. Clone Repository

```bash
cd /app
git clone https://github.com/yourusername/dictat.git
cd dictat
```

#### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with production values:
# - Strong SECRET_KEY
# - Database credentials
# - Domain name
# - Email configuration
# - DPO contact information
```

#### 4. Mount Block Storage

```bash
# Verify volume is mounted at /mnt/dictat-storage
df -h

# Create symlinks
ln -s /mnt/dictat-storage/audio /app/dictat/storage/audio
ln -s /mnt/dictat-storage/postgres /app/dictat/postgres-data
```

#### 5. Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 6. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

#### 7. Create Admin User

```bash
# TODO Phase 1: Create admin user script
# docker-compose exec backend python scripts/create_admin.py
```

### Phase 5: SSL/TLS Configuration

#### Using Let's Encrypt with Traefik (Recommended)

```bash
# TODO: Configure Traefik in docker-compose.prod.yml
# - Automatic SSL certificate generation
# - HTTP to HTTPS redirect
# - Certificate renewal
```

### Phase 5: Monitoring Setup

#### 1. Access Grafana

```
http://<droplet-ip>:3001
Default: admin/admin
```

#### 2. Configure Dashboards

- Import Dictat dashboards from `monitoring/dashboards/`
- Configure alerts for:
  - High API response times
  - Database connection errors
  - Storage capacity warnings
  - Failed login attempts

#### 3. Access Prometheus

```
http://<droplet-ip>:9090
```

## Post-Deployment Tasks

### Phase 5: Security Hardening

1. **Restrict SSH Access**
   ```bash
   # Update terraform/terraform.tfvars
   allowed_ssh_ips = ["your.ip.address/32"]
   terraform apply
   ```

2. **Enable Fail2Ban**
   ```bash
   systemctl enable fail2ban
   systemctl start fail2ban
   ```

3. **Configure Firewall**
   ```bash
   ufw status
   # Verify only ports 22, 80, 443 are open
   ```

4. **Review Security Headers**
   - Check CSP, HSTS, X-Frame-Options in responses

### Phase 5: Backup Configuration

1. **Enable Digital Ocean Backups**
   - Enable in Terraform: `enable_backups = true`
   - Weekly automated snapshots

2. **Database Backups**
   ```bash
   # TODO: Set up automated database backups to Digital Ocean Spaces
   # crontab -e
   # 0 2 * * * /app/dictat/scripts/backup-db.sh
   ```

3. **Storage Backups**
   - Configure block storage snapshots
   - Retention: 7 years for medical data (GDPR)

### Phase 5: GDPR Compliance Checklist

- [ ] Data encryption at rest enabled
- [ ] SSL/TLS for data in transit
- [ ] Audit logging enabled for all sensitive operations
- [ ] Data retention policies configured (7 years)
- [ ] Right to erasure implemented and tested
- [ ] Right to portability implemented and tested
- [ ] Consent management implemented
- [ ] DPO contact information configured
- [ ] Privacy policy created and accessible
- [ ] Data processing agreement with Digital Ocean

### Phase 5: Testing

1. **Smoke Tests**
   ```bash
   # Test health endpoint
   curl https://yourdomain.com/health

   # Test API docs
   curl https://yourdomain.com/docs
   ```

2. **Authentication Tests**
   - User registration
   - Login
   - Token refresh
   - Password reset

3. **File Upload Tests**
   - Upload audio file
   - Stream audio file
   - Verify range requests work

4. **GDPR Tests**
   - Request data export
   - Verify audit logging
   - Test data deletion

## Monitoring and Maintenance

### Daily Checks
- Review application logs
- Check disk usage
- Monitor error rates

### Weekly Checks
- Review audit logs
- Check backup completion
- Review security alerts

### Monthly Checks
- Update dependencies
- Review and rotate secrets
- Compliance audit
- Performance optimization

## Rollback Procedures

### Application Rollback

```bash
# Revert to previous Docker image
docker-compose down
docker-compose up -d --force-recreate backend:previous-tag
```

### Database Rollback

```bash
# Restore from backup
# TODO Phase 5: Document database restoration procedure
```

### Infrastructure Rollback

```bash
cd terraform
terraform destroy --target=digitalocean_droplet.dictat_app
terraform apply
```

## Scaling

### Vertical Scaling (Increase Droplet Size)

```bash
# Update terraform/terraform.tfvars
droplet_size = "s-4vcpu-8gb"
terraform apply
```

### Horizontal Scaling (Multiple Droplets)

```bash
# TODO Phase 6: Configure load balancer
# - Add multiple backend droplets
# - Configure session affinity
# - Set up shared storage (Spaces)
```

## Cost Optimization

Current estimated monthly costs:
- Droplet (4GB): $24/month
- Block Storage (100GB): $10/month
- Backups: ~$5/month
- Bandwidth: Included (1TB)
- **Total: ~$40/month**

Tips:
- Monitor actual usage and adjust droplet size
- Use reserved instances for 15% discount (annual)
- Archive old audio files to Spaces ($5/250GB)

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check backend container: `docker-compose logs backend`
   - Verify database connection
   - Check environment variables

2. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check credentials in .env
   - Review connection pool settings

3. **File Upload Failures**
   - Check storage volume mount
   - Verify permissions on /app/storage
   - Check MAX_UPLOAD_SIZE setting

4. **OPA Authorization Errors**
   - Verify OPA container is running
   - Check OPA_URL configuration
   - Review policy files in opa/policies/

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/dictat/issues
- Documentation: https://docs.dictat.example.com
- Email: support@dictat.example.com
