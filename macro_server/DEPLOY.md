# Deployment Guide for Railway

## Option 1: Using Railway CLI (Recommended)

1.  **Install CLI:** `npm i -g @railway/cli`
2.  **Login:** `railway login`
3.  **Initialize Project:**
    ```bash
    cd macro_server
    railway init
    ```
4.  **Add Database:**
    ```bash
    railway add postgresql
    ```
5.  **Deploy:**
    ```bash
    railway up
    ```
    (Select the `macro_server` folder if asked, or just run it from root if you want to deploy the whole thing, but dragging the folder into the dashboard is easier if not using CLI for everything).
    
    *Better CLI Flow:*
    ```bash
    cd macro_server
    railway init
    railway up
    ```
6.  **Public Domain:**
    Go to Railway Dashboard -> Select Service -> Settings -> Generate Domain.

## Option 2: Using GitHub (Easiest)

1.  Push this code to your GitHub repository.
2.  Go to [Railway Dashboard](https://railway.app/new).
3.  Select "Deploy from GitHub repo".
4.  Select your repository.
5.  **Root Directory:** Set this to `/macro_server` in the settings if asked, or Railway might auto-detect.
6.  **Add Database:** Right click on the canvas -> Add -> Database -> PostgreSQL.
7.  **Connect:** Railway usually auto-injects `DATABASE_URL` into your service.

## Option 3: Manual Upload (Not recommended for updates)
(Not supported well by Railway anymore, use CLI or GitHub).

## After Deployment
Test your URL: `https://your-project.up.railway.app/health`
