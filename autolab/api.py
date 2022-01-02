from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import database, crud
from .ansible import ConfigBackupExecutor, CreateVMExecutor
from .config import get_ansible_configuration
from .schema import AnsibleJob, CreateVmRequest, CreateVmResponse

database.Base.metadata.create_all(bind=database.engine)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

create_vm_executor = CreateVMExecutor(get_ansible_configuration())
config_backup_executor = ConfigBackupExecutor(get_ansible_configuration())

app = FastAPI()
app_api = FastAPI()

@app_api.post("/create-vm")
async def create_vm(request: CreateVmRequest, db: Session = Depends(get_db)) -> CreateVmResponse:
    return await create_vm_executor.execute(db, request)

@app_api.post("/config-backup")
async def backup_network_configs(db: Session = Depends(get_db)):
    return await config_backup_executor.execute(db)

@app_api.get("/jobs", response_model=List[AnsibleJob])
def get_jobs(db: Session = Depends(get_db)):
    return crud.get_ansible_jobs(db)

@app_api.get("/jobs/{job_uuid}", response_model=AnsibleJob)
def get_job_by_uuid(job_uuid: str, db: Session = Depends(get_db)):
    job = crud.get_ansible_job(db, job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")
app.mount("/api", app_api)
