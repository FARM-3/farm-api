# Docker Deployment Checklist

## Pre-Deployment (Local Testing)

- [ ] Test Docker build locally:
  ```bash
  docker-compose -f docker-compose.dev.yml build
  ```

- [ ] Test Docker Compose locally:
  ```bash
  docker-compose -f docker-compose.dev.yml up
  ```

- [ ] Verify local app works:
  - [ ] Backend API: http://localhost:8000/api/
  - [ ] Django admin: http://localhost:8000/admin/
  - [ ] API docs: http://localhost:8000/api/docs/

- [ ] Test migrations:
  ```bash
  docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
  ```

- [ ] Create test superuser:
  ```bash
  docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
  ```

- [ ] Verify static files collected:
  ```bash
  docker-compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput
  ```

## Digital Ocean Deployment

- [ ] SSH into your server:
  ```bash
  ssh root@142.93.94.236
  ```

- [ ] Install Docker if not already installed:
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
  ```

- [ ] Install Docker Compose:
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

- [ ] Navigate to project:
  ```bash
  cd /var/www/teamrugyeyo
  ```

- [ ] Create .env file:
  ```bash
  cp .env.example .env
  nano .env
  ```

- [ ] Update these in .env:
  - [ ] `DJANGO_SECRET_KEY` - Generate new secure key
  - [ ] `DB_PASSWORD` - Use strong password
  - [ ] `SERVER_NAME` - Set to your domain or IP

- [ ] Push latest code to Digital Ocean:
  ```bash
  git pull origin main
  ```

- [ ] Stop existing Gunicorn:
  ```bash
  sudo killall gunicorn
  ```

- [ ] Build Docker images:
  ```bash
  docker-compose build backend
  ```

- [ ] Start containers:
  ```bash
  docker-compose up -d
  ```

- [ ] Verify containers running:
  ```bash
  docker-compose ps
  ```

- [ ] Run migrations:
  ```bash
  docker-compose exec backend python manage.py migrate
  ```

- [ ] Create superuser:
  ```bash
  docker-compose exec backend python manage.py createsuperuser
  ```

- [ ] Check logs for errors:
  ```bash
  docker-compose logs backend
  docker-compose logs nginx
  ```

## Post-Deployment Testing

- [ ] Test API endpoints:
  - [ ] Staff list: curl http://142.93.94.236/api/staff/
  - [ ] API docs: http://142.93.94.236/api/docs/
  - [ ] Admin: http://142.93.94.236/admin/

- [ ] Verify static files loading:
  - [ ] Admin CSS loads correctly
  - [ ] API docs styling works

- [ ] Test CORS (from your frontend):
  - [ ] POST request to /api/staff/ works
  - [ ] No CORS errors in browser console

- [ ] Monitor container health:
  ```bash
  docker-compose ps
  docker-compose logs -f backend
  ```

- [ ] Check disk space:
  ```bash
  df -h
  ```

## Ongoing Maintenance

- [ ] Set up automated backups for PostgreSQL
  - [ ] Script to backup database daily
  - [ ] Store backups securely (S3 or offsite)

- [ ] Monitor container logs:
  ```bash
  docker-compose logs -f backend --tail 100
  ```

- [ ] Update dependencies regularly:
  ```bash
  # Update requirements.txt, then rebuild
  docker-compose build --no-cache backend
  docker-compose up -d backend
  ```

- [ ] Clean up old Docker images:
  ```bash
  docker image prune -a
  docker system prune -a
  ```

- [ ] Set up SSL/HTTPS:
  - [ ] Get SSL certificate (Let's Encrypt)
  - [ ] Update nginx.conf with SSL blocks
  - [ ] Restart nginx

## Rollback Procedure (if needed)

If something breaks and you need to go back to Gunicorn:

```bash
# Stop Docker containers
docker-compose down

# Restart Gunicorn (if you kept it)
cd /var/www/teamrugyeyo/backend
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 api.wsgi:application &

# Or reinstall and start fresh
sudo systemctl start gunicorn
```

## Common Issues & Solutions

### Issue: Static files still not loading
**Solution:**
```bash
docker-compose exec backend python manage.py collectstatic --clear --noinput
docker-compose restart nginx
```

### Issue: Database migration errors
**Solution:**
```bash
docker-compose logs postgres  # Check DB logs
docker-compose exec backend python manage.py migrate --verbosity 2
```

### Issue: Port 80 already in use
**Solution:**
```bash
sudo lsof -i :80
sudo kill -9 <PID>
# Or change port in docker-compose.yml
```

### Issue: Cannot connect to database
**Solution:**
```bash
# Verify .env file has correct DB_URL
# Rebuild containers to apply changes
docker-compose build backend
docker-compose up -d
```

## Success Criteria

✅ All Docker containers are running
✅ API endpoints respond correctly
✅ Django admin loads with CSS/styling
✅ No CORS errors from frontend
✅ Static files serve correctly
✅ Database migrations complete
✅ Logs show no errors

You're ready to scale to AWS!
