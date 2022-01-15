from concurrent.futures import ThreadPoolExecutor
from typing import List
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from . import database, crud, config
from .ansible import PlaybookConfig, AnsibleJobExecutorService, get_ip_addrs, status_handler
from .schema import AnsibleJob, BaseResponse, CreateVmRequest

database.Base.metadata.create_all(bind=database.engine)

settings = config.get_app_settings()

# ===== create a register the playbook configs =====
create_vm_config = PlaybookConfig(
    private_data_dir=settings.create_vm_private_data_dir,
    playbook="create-vm.yml",
    quiet=settings.ansible_quiet,
    finished_callback=get_ip_addrs,
)

config_backup_config = PlaybookConfig(
    private_data_dir=settings.config_backup_private_data_dir,
    playbook="config-backup.yml",
    quiet=settings.ansible_quiet,
)


executor = ThreadPoolExecutor(max_workers=1)
executor_service = AnsibleJobExecutorService(executor, status_handler)


app = FastAPI()
app_api = FastAPI()

@app_api.post("/create-vm", response_model=BaseResponse)
async def create_vm(request: CreateVmRequest) -> BaseResponse:
    extravars = {"vm_name": request.vm_name, "template_name": request.vm_template.value}
    ident = str(uuid.uuid1())
    crud.create_ansible_job(ident, "create-vm", "REST")
    executor_service.submit_job(ident, create_vm_config, extravars)
    return BaseResponse(job_uuid=ident)


@app_api.post("/config-backup", response_model=BaseResponse)
async def backup_network_configs() -> BaseResponse:
    ident = str(uuid.uuid1())
    crud.create_ansible_job(ident, "config-backup", "REST")
    executor_service.submit_job(ident, config_backup_config)
    return BaseResponse(job_uuid=ident)

@app_api.get("/jobs", response_model=List[AnsibleJob])
def get_jobs():
    return crud.get_ansible_jobs()

@app_api.get("/jobs/{job_uuid}", response_model=AnsibleJob)
def get_job_by_uuid(job_uuid: str):
    job = crud.get_ansible_job(job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")
app.mount("/api", app_api)
