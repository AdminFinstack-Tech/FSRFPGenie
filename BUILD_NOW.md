# 🚀 Ready to Build and Push - Quick Start

## ⚠️ Docker Not Running

I detected that Docker Desktop is not currently running. Let's fix that!

---

## 🔧 Step 1: Start Docker Desktop

### On macOS:
```bash
# Open Docker Desktop
open -a Docker

# Or from Applications folder
# Applications → Docker → Double-click Docker.app
```

### Verify Docker is Running:
```bash
# Wait 20-30 seconds for Docker to start, then check:
docker info

# Should show Docker version and system info
# If you see "Cannot connect to Docker daemon", wait a bit longer
```

---

## 🚀 Step 2: Run Build and Push

Once Docker is running:

```bash
cd /Users/ilyasashu/RFPAINew

# Build and push everything
./build-and-push.sh
```

---

## 📋 What Will Happen

The script will:

1. **Login to Azure Container Registry** ✅
   - Uses credentials from `.env.azure`
   - Server: `rfpragreg.azurecr.io`

2. **Build Backend Image** 🔨
   - Platform: `linux/amd64` (required for Azure)
   - Base: Python 3.11 slim
   - Includes: All dependencies from `requirements.txt`
   - Time: ~5-10 minutes

3. **Build Frontend Image** 🔨
   - Platform: `linux/amd64`
   - Multi-stage build (Node → Nginx)
   - Time: ~3-5 minutes

4. **Push to Azure** 📤
   - Backend: `rfpragreg.azurecr.io/rfprag-backend:latest`
   - Frontend: `rfpragreg.azurecr.io/rfprag-frontend:latest`
   - Time: ~3-5 minutes (depends on internet speed)

5. **Verify** ✅
   - Lists images in ACR
   - Confirms successful upload

**Total Time: ~15-20 minutes** ⏱️

---

## 🎯 Quick Command Reference

```bash
# 1. Start Docker (if not running)
open -a Docker

# 2. Wait for Docker to start (check with)
docker ps

# 3. Run build and push
./build-and-push.sh

# 4. Watch progress
# The script shows real-time progress
```

---

## 🐛 If Something Goes Wrong

### Docker Won't Start
```bash
# Kill any stuck Docker processes
killall Docker

# Restart Docker
open -a Docker
```

### Build Fails
```bash
# Check Docker has enough memory (4GB recommended)
# Docker Desktop → Settings → Resources → Memory

# Try building individually
cd backend
docker build --platform linux/amd64 -t test-backend .

cd ../frontend
docker build --platform linux/amd64 -t test-frontend .
```

### Login Fails
```bash
# Verify .env.azure has correct credentials
cat .env.azure | grep ACR

# Re-login manually
source .env.azure
echo $ACR_PASSWORD | docker login $ACR_LOGIN_SERVER \
    --username $ACR_USERNAME \
    --password-stdin
```

### Push is Slow
```bash
# This is normal! Pushing to Azure can take 5-10 minutes
# especially for the backend image (~500MB)

# You can check progress:
docker push rfpragreg.azurecr.io/rfprag-backend:latest
# Shows layer upload progress
```

---

## ✅ Success Indicators

You'll know it's successful when you see:

```
════════════════════════════════════════════════════════════
✅ SUCCESS! All images built and pushed
════════════════════════════════════════════════════════════

📋 Summary:
   ✅ Backend:  rfpragreg.azurecr.io/rfprag-backend:latest
   ✅ Frontend: rfpragreg.azurecr.io/rfprag-frontend:latest

🚀 Next Steps:
   1. Deploy to Azure Container Apps:
      ./scripts/5-deploy-to-azure.sh
```

---

## 🎬 After Build Completes

### Option 1: Deploy for First Time
```bash
cd scripts
./5-deploy-to-azure.sh
```

### Option 2: Update Existing Deployment
```bash
cd scripts
./7-update-deployment.sh
```

### Option 3: Verify Images
```bash
# Check images are in ACR
az acr repository list --name rfpragreg --output table
```

---

## 📊 Resource Usage

During build, expect:
- **CPU**: High usage (~80-100%)
- **Memory**: 4-6 GB
- **Disk**: ~2 GB for images
- **Network**: ~500 MB upload

---

## 🎯 TL;DR - Just Do This

```bash
# 1. Start Docker
open -a Docker

# 2. Wait 30 seconds, then
cd /Users/ilyasashu/RFPAINew
./build-and-push.sh

# 3. Get coffee ☕ (takes ~15 minutes)

# 4. Deploy
cd scripts
./5-deploy-to-azure.sh
```

---

## 💡 Pro Tips

1. **First build is slowest** - subsequent builds use cache and are much faster

2. **Build during off-peak hours** - Azure uploads faster when network is less congested

3. **Use specific tags for production**:
   ```bash
   ./build-and-push.sh v1.0.0
   ```

4. **Monitor build in real-time** - the script shows all output, don't worry about the length!

5. **Keep Docker Desktop updated** - newer versions have better performance

---

## 📞 Need Help?

If the build fails:
1. Check Docker is running: `docker ps`
2. Check internet connection
3. Verify Azure credentials in `.env.azure`
4. Check Docker has enough resources (Settings → Resources)
5. Try building one image at a time (backend, then frontend)

**Common Issue**: First build might fail due to Docker pulling base images. Just run again!

---

## ✨ Ready?

**Start Docker Desktop now, wait 30 seconds, then run:**

```bash
./build-and-push.sh
```

🚀 Let's go!
