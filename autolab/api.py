from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .ansible import CreateVMExecutor
from .data_model import CreateVmRequest, CreateVmResponse, get_ansible_configuration


create_vm_executor = CreateVMExecutor(get_ansible_configuration())

app = FastAPI()
app_api = FastAPI()

@app_api.post("/create-vm")
async def create_vm(request: CreateVmRequest) -> CreateVmResponse:
    return await create_vm_executor.execute(request)

app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")
app.mount("/api", app_api)
