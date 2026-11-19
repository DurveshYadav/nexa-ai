# Deployment sequence
git push
   ↓
GitHub Actions
   ↓
Tests
   ↓
Docker build
   ↓
Deployment platform
   ↓
Container starts
   ↓
Environment loaded
   ↓
Database migration
   ↓
Health check
   ↓
API live
