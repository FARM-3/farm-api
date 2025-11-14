# Docker Deployment Guide

This guide explains how to deploy your Rugyeyo app using Docker and Docker Compose.

## Project Structure

```
/var/www/teamrugyeyo/
├── backend/              # Django API
│   ├── api/             # Django project
│   ├── Dockerfile       # Already updated with collectstatic
│   └── requirements.txt
├── frontend-web/        # React web app
├── frontend-mobile/     # React Native app
├── docker-compose.yml   # Orchestrates all services
├── nginx.conf          # Reverse proxy configuration
├── .env                # Environment variables (NEVER commit this)
└── .env.example        # Template for .env file
```

## Step 1: Set Up Environment Variables

On your Digital Ocean server:

```bash
cd /var/www/teamrugyeyo
cp .env.example .env
nano .env
```

Update these critical values:
- `DJANGO_SECRET_KEY` - Generate a new one (use Django's get_random_secret_key())
- `DB_PASSWORD` - Use a strong password
- `DB_URL` - Should be: `postgresql://rugyeyo_user:your-password@postgres:5432/rugyeyo_db`

Save and exit (Ctrl+X, Y, Enter).

## Step 2: Stop Current Gunicorn Process

```bash
sudo killall gunicorn
# or if using systemd
sudo systemctl stop gunicorn
```

## Step 3: Build and Start Docker Containers

```bash
cd /var/www/teamrugyeyo

# Build the backend image (this will run collectstatic automatically)
docker-compose build backend

# Start all services
docker-compose up -d

# Check if everything is running
docker-compose ps
```

You should see:
- rugyeyo-backend (running)
- rugyeyo-postgres (running)
- rugyeyo-nginx (running)

## Step 4: Verify It's Working

```bash
# Check backend logs
docker-compose logs backend

# Check nginx logs
docker-compose logs nginx

# Test the API
curl http://localhost/api/staff/

# Test Django admin
curl http://localhost/admin/
```

## Step 5: Access Your Application

- **API**: http://142.93.94.236/api/
- **Django Admin**: http://142.93.94.236/admin/
- **API Docs**: http://142.93.94.236/api/docs/

The CSS should now load correctly!

## Useful Docker Commands

### View logs
```bash
docker-compose logs -f backend      # Follow backend logs
docker-compose logs -f nginx        # Follow nginx logs
docker-compose logs -f postgres     # Follow database logs
```

### Stop all services
```bash
docker-compose down
```

### Restart services
```bash
docker-compose restart backend
docker-compose restart nginx
```

### Run migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Create superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Access backend shell
```bash
docker-compose exec backend python manage.py shell
```

## Deploying Code Changes

When you push new code:

```bash
cd /var/www/teamrugyeyo

# Pull latest code
git pull origin main

# Rebuild backend (collectstatic runs automatically)
docker-compose build backend

# Restart backend service
docker-compose up -d backend

# Check if running
docker-compose ps
```

## Scaling to AWS

When you move to AWS, you can use:

1. **AWS ECR** - Store your Docker images
2. **AWS ECS** - Run your containers
3. **AWS RDS** - Managed PostgreSQL database
4. **AWS ALB** - Load balancing
5. **AWS CloudFront** - CDN for static files

The beauty of Docker: your `Dockerfile` and `docker-compose.yml` make this transition seamless. Same images, different infrastructure.

## Troubleshooting

### Django admin CSS still not loading?
```bash
# Manually collect static files in the container
docker-compose exec backend python manage.py collectstatic --clear --noinput

# Restart nginx
docker-compose restart nginx
```

### Database connection issues?
```bash
# Check database logs
docker-compose logs postgres

# Make sure DB_URL in .env matches postgres service credentials
```

### Port 80 already in use?
```bash
# Find what's using port 80
sudo lsof -i :80

# Kill it (or change nginx port in docker-compose.yml)
sudo kill -9 <PID>
```

### Out of disk space?
```bash
# Clean up Docker
docker system prune -a

# Check disk usage
du -sh /var/lib/docker
```

## Next Steps

1. Set up SSL/HTTPS (uncomment the HTTPS block in nginx.conf)
2. Set up automated backups of your PostgreSQL database
3. Monitor your containers with Portainer or similar tool
4. Consider setting up CI/CD to automatically build and deploy on git push
