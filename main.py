from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, RedirectResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import yaml
import git
import os
import shutil
from datetime import datetime
import tempfile
from contextlib import asynccontextmanager
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")

CONFIG_FILE = "config.yaml"
REPOS_DIR = "repos"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)

def update_mirrors():
    config = load_config()
    repos = config.get('repositories', [])
    for repo_url in repos:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(REPOS_DIR, repo_name)
        try:
            if not os.path.exists(repo_path):
                git.Repo.clone_from(repo_url, repo_path, mirror=True)
            else:
                repo = git.Repo(repo_path)
                repo.remotes.origin.fetch(prune=True)
        except Exception as e:
            print(f"Error updating {repo_url}: {str(e)}")
        time.sleep(40)  # 40 seconds delay between each repo

# Initialize scheduler
scheduler = BackgroundScheduler()
def schedule_job(cron_expr):
    scheduler.remove_all_jobs()
    if cron_expr:
        scheduler.add_job(update_mirrors, CronTrigger.from_crontab(cron_expr))
    else:
        scheduler.add_job(update_mirrors, 'interval', hours=12)
scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(REPOS_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        save_config({'repositories': [], 'cron': ''})
    config = load_config()
    cron_expr = config.get('cron', '')
    schedule_job(cron_expr)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/set_cron")
async def set_cron(cron: str = Form(...)):
    config = load_config()
    config['cron'] = cron
    save_config(config)
    schedule_job(cron)
    return RedirectResponse(url="/", status_code=303)

@app.get("/")
async def home(request: Request):
    config = load_config()
    repos = config.get('repositories', [])
    cron = config.get('cron', '')
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "repos": repos, "cron": cron}
    )

@app.post("/add")
async def add_repo(repo_url: str = Form(...)):
    config = load_config()
    if 'repositories' not in config:
        config['repositories'] = []
    
    if repo_url not in config['repositories']:
        config['repositories'].append(repo_url)
        save_config(config)
        # Trigger immediate mirror
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(REPOS_DIR, repo_name)
        if not os.path.exists(repo_path):
            git.Repo.clone_from(repo_url, repo_path, mirror=True)
    
    return {"status": "success"}

@app.post("/remove")
async def remove_repo(repo_url: str = Form(...)):
    config = load_config()
    if repo_url in config.get('repositories', []):
        config['repositories'].remove(repo_url)
        save_config(config)
        
        # Remove the mirrored repository
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(REPOS_DIR, repo_name)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
    
    return {"status": "success"}

@app.get("/download/{repo_name}")
async def download_repo(repo_name: str):
    repo_path = os.path.abspath(os.path.join(REPOS_DIR, repo_name))
    if not os.path.exists(repo_path):
        return {"error": "Repository not found"}
    
    clones_dir = os.path.abspath("clones")
    os.makedirs(clones_dir, exist_ok=True)
    clone_target = os.path.join(clones_dir, repo_name)
    # Remove previous clone if exists
    if os.path.exists(clone_target):
        shutil.rmtree(clone_target)
    # Clone from mirror to clones directory
    git.Repo.clone_from(f"file://{repo_path}", clone_target)
    # Create zip file
    zip_path = os.path.join(clones_dir, f"{repo_name}.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    shutil.make_archive(os.path.join(clones_dir, repo_name), 'zip', clone_target)
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
