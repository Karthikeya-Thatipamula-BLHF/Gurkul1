# Gurukul Platform - Render.com Deployment Guide

## Quick Deployment Steps

### 1. Prepare Repository
```bash
git add .
git commit -m "Production deployment"
git push origin main
```

### 2. Deploy to Render.com

#### Backend Service:
1. Go to https://render.com
2. New Web Service
3. Connect GitHub repository
4. Configure:
   - Name: gurukul-backend
   - Environment: Python 3
   - Build Command: cd Backend && pip install -r requirements_production.txt
   - Start Command: cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT

#### Frontend Service:
1. New Static Site
2. Connect GitHub repository  
3. Configure:
   - Name: gurukul-frontend
   - Build Command: cd "new frontend" && npm ci && npm run build
   - Publish Directory: new frontend/dist

### 3. Environment Variables

Set these in Render dashboard:

#### Backend:
```
MONGODB_URI=your_mongodb_connection_string
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://gurukul-frontend.onrender.com
```

#### Frontend:
```
VITE_API_BASE_URL=https://gurukul-backend.onrender.com
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
NODE_ENV=production
```

### 4. Verify Deployment

- Backend Health: https://gurukul-backend.onrender.com/health
- Frontend: https://gurukul-frontend.onrender.com
- API Docs: https://gurukul-backend.onrender.com/docs

## Troubleshooting

1. Check Render logs for errors
2. Verify environment variables
3. Test API endpoints individually
4. Check database connectivity

Your Gurukul Platform is ready for production!
