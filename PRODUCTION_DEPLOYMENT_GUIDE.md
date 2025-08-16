# Gurukul Platform - Production Deployment Guide

## 🚀 Complete Production Deployment Instructions

This guide will walk you through deploying the Gurukul Learning Platform to production with all necessary security, performance, and reliability configurations.

## 📋 Prerequisites

### System Requirements
- **Server**: Linux (Ubuntu 20.04+ recommended) or Windows Server
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Python 3.9+
- Node.js 18+ (for local builds)

## 🔧 Step 1: Initial Setup

### 1.1 Clone and Prepare Repository
```bash
# Clone the repository
git clone <your-repository-url>
cd Gurukul_new-main

# Make scripts executable
chmod +x deploy_production.sh
chmod +x setup_production.py
chmod +x production_readiness_check.py
chmod +x health_check_production.py
```

### 1.2 Run Production Setup
```bash
# Run automated production setup
python3 setup_production.py
```

This script will:
- Create production environment files
- Generate secure keys and passwords
- Set up directory structure
- Configure security settings

## 🔐 Step 2: Configure Environment Variables

### 2.1 Backend Configuration
Edit `Backend/.env` with your production values:

```bash
# Required API Keys (Get from respective providers)
GROQ_API_KEY=your_actual_groq_api_key
OPENAI_API_KEY=your_actual_openai_api_key
GEMINI_API_KEY=your_actual_gemini_api_key

# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/gurukul
# OR for local MongoDB:
# MONGODB_URI=mongodb://admin:password@mongodb:27017/gurukul?authSource=admin

# Domain Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 2.2 Frontend Configuration
Edit `new frontend/.env.production`:

```bash
# API URLs (Update with your domain)
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 🗄️ Step 3: Database Setup

### 3.1 MongoDB Atlas (Recommended)
1. Create MongoDB Atlas account
2. Create a new cluster
3. Create database user
4. Whitelist your server IP
5. Get connection string and update `MONGODB_URI`

### 3.2 Local MongoDB (Alternative)
The docker-compose will set up MongoDB automatically with the credentials in your `.env` file.

## 🔒 Step 4: SSL/TLS Configuration

### 4.1 Obtain SSL Certificates

#### Option A: Let's Encrypt (Free)
```bash
# Install certbot
sudo apt install certbot

# Get certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

#### Option B: Commercial Certificate
Place your certificates in `nginx/ssl/`:
- `certificate.crt`
- `private.key`
- `ca_bundle.crt` (if required)

### 4.2 Update Nginx Configuration
Edit `nginx/nginx.conf` to include SSL configuration.

## ✅ Step 5: Validation

### 5.1 Run Production Readiness Check
```bash
python3 production_readiness_check.py
```

Fix any issues reported before proceeding.

### 5.2 Validate Configuration
```bash
# Check Docker configuration
docker-compose -f docker-compose.production.yml config

# Validate environment files
grep -v "^#" Backend/.env | grep "your_.*_here" || echo "Environment validation passed"
```

## 🚀 Step 6: Deployment

### 6.1 Deploy Services
```bash
# Run production deployment
./deploy_production.sh
```

### 6.2 Verify Deployment
```bash
# Check service health
python3 health_check_production.py

# Check container status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

## 🔍 Step 7: Post-Deployment Verification

### 7.1 Test Application
1. **Frontend**: Visit `https://yourdomain.com`
2. **API**: Visit `https://api.yourdomain.com/health`
3. **Documentation**: Visit `https://api.yourdomain.com/docs` (if enabled)

### 7.2 Performance Testing
```bash
# Test API response times
curl -w "@curl-format.txt" -o /dev/null -s "https://api.yourdomain.com/health"

# Test frontend loading
curl -w "@curl-format.txt" -o /dev/null -s "https://yourdomain.com"
```

## 📊 Step 8: Monitoring Setup

### 8.1 Log Monitoring
```bash
# Set up log rotation
sudo cp logs/logrotate.conf /etc/logrotate.d/gurukul

# Monitor logs in real-time
docker-compose -f docker-compose.production.yml logs -f --tail=100
```

### 8.2 Health Monitoring
Set up a cron job for regular health checks:
```bash
# Add to crontab
*/5 * * * * /path/to/gurukul/health_check_production.py >> /var/log/gurukul-health.log 2>&1
```

## 🔄 Step 9: Backup Strategy

### 9.1 Database Backup
```bash
# MongoDB backup script
docker exec gurukul-mongodb-prod mongodump --out /backup/$(date +%Y%m%d_%H%M%S)
```

### 9.2 Application Backup
```bash
# Backup configuration and data
tar -czf gurukul-backup-$(date +%Y%m%d).tar.gz \
  Backend/.env \
  nginx/ssl/ \
  logs/ \
  docker-compose.production.yml
```

## 🛠️ Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs [service-name]

# Restart specific service
docker-compose -f docker-compose.production.yml restart [service-name]
```

#### Database Connection Issues
```bash
# Test MongoDB connection
docker exec gurukul-mongodb-prod mongosh --eval "db.adminCommand('ping')"

# Check Redis connection
docker exec gurukul-redis-prod redis-cli ping
```

#### SSL Certificate Issues
```bash
# Test SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check certificate expiry
openssl x509 -in nginx/ssl/certificate.crt -text -noout | grep "Not After"
```

## 📞 Support

For issues and support:
1. Check logs: `docker-compose -f docker-compose.production.yml logs`
2. Run health check: `python3 health_check_production.py`
3. Validate configuration: `python3 production_readiness_check.py`

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d
```

### Security Updates
```bash
# Update base images
docker-compose -f docker-compose.production.yml pull

# Rebuild with security updates
docker-compose -f docker-compose.production.yml build --pull
```

---

## 🎉 Congratulations!

Your Gurukul Learning Platform is now deployed and ready for production use!

**Important URLs:**
- Frontend: `https://yourdomain.com`
- API: `https://api.yourdomain.com`
- Health Check: `https://api.yourdomain.com/health`
