from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from . import database, crud
from .ansible import PlaybookConfig, PlaybookExecutorFactory, get_ip_addrs
from .schema import AnsibleJob, BaseResponse, CreateVmRequest

database.Base.metadata.create_all(bind=database.engine)

# ===== create a register the playbook configs =====
create_vm_config = PlaybookConfig(private_data_dir="../../ansible-projects/pve-one-touch",
                                  playbook="create-vm.yml",
                                  quiet=False,
                                  finished_callback=get_ip_addrs)

config_backup_config = PlaybookConfig(private_data_dir="../../ansible-projects/config-backup",
                                      playbook="config-backup.yml",
                                      quiet=False)

executor_factory = PlaybookExecutorFactory()
executor_factory.register("create-vm", create_vm_config)
executor_factory.register("config-backup", config_backup_config)


app = FastAPI()
app_api = FastAPI()

@app_api.post("/create-vm", response_model=BaseResponse)
async def create_vm(request: CreateVmRequest) -> BaseResponse:
    extravars = {"vm_name": request.vm_name, "template_name": request.vm_template.value}
    executor = executor_factory.build_executor("create-vm")
    executor.start_playbook(extravars)
    return BaseResponse(job_uuid=executor.uuid)


@app_api.post("/config-backup", response_model=BaseResponse)
async def backup_network_configs() -> BaseResponse:
    executor = executor_factory.build_executor("config-backup")
    executor.start_playbook()
    return BaseResponse(job_uuid=executor.uuid)

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
