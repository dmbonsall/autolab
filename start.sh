cd $HOME
source $HOME/venv/bin/activate
uvicorn --host 0.0.0.0 autolab.api:app
