from concurrent.futures import ThreadPoolExecutor
from typing import List
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from autolab import database, config, data_model, services, utils
from autolab.schema import AnsibleJob, BaseResponse, CreateVmRequest, PlaybookType


# ===== Get the settings and initialize everything =====
settings = config.get_app_settings()

database.initialize(db_url=settings.db_url)
data_model.Base.metadata.create_all(bind=database.get_engine())

executor = ThreadPoolExecutor(max_workers=settings.max_executor_threads)
executor_service = services.PlaybookExecutorService(executor, utils.status_handler)


app = FastAPI()
app_api = FastAPI()

@app_api.post("/create-vm", response_model=BaseResponse)
async def create_vm(request: CreateVmRequest) -> BaseResponse:
    extravars = {"vm_name": request.vm_name, "template_name": request.vm_template.value}
    ident = str(uuid.uuid1())
    database.create_ansible_job(ident, "create-vm", "REST")
    executor_service.submit_job(ident, PlaybookType.CREATE_VM, extravars)
    return BaseResponse(job_uuid=ident)


@app_api.post("/config-backup", response_model=BaseResponse)
async def backup_network_configs() -> BaseResponse:
    ident = str(uuid.uuid1())
    database.create_ansible_job(ident, "config-backup", "REST")
    executor_service.submit_job(ident, PlaybookType.CONFIG_BACKUP)
    return BaseResponse(job_uuid=ident)

@app_api.get("/jobs", response_model=List[AnsibleJob])
def get_jobs():
    return database.get_ansible_jobs()

@app_api.get("/jobs/{job_uuid}", response_model=AnsibleJob)
def get_job_by_uuid(job_uuid: str):
    job = database.get_ansible_job(job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")
app.mount("/api", app_api)
