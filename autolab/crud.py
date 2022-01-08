import datetime

from sqlalchemy.orm import Session

from .autowire import autowire
from .data_model import AnsibleJob
from .database import get_db


@autowire("db", get_db)
def create_ansible_job(job_uuid: str, start_time: datetime.datetime, db: Session = None):
    ansible_job = AnsibleJob(job_uuid=job_uuid, start_time=start_time)
    db.add(ansible_job)
    db.commit()
    db.refresh(ansible_job)
    return ansible_job


@autowire("db", get_db)
def get_ansible_job(job_uuid: str, db: Session = None):
    return db.query(AnsibleJob).filter(AnsibleJob.job_uuid == job_uuid).one()


@autowire("db", get_db)
def get_ansible_jobs(skip: int = 0, limit: int = 100, db: Session = None):
    return db.query(AnsibleJob).order_by(AnsibleJob.start_time.desc()).offset(skip).limit(limit).all()


@autowire("db", get_db)
def update_job(job_uuid: str, db: Session = None, **kwargs):
    update_dict = {}
    if "status" in kwargs:
        update_dict[AnsibleJob.status] = kwargs["status"]

    if "end_time" in kwargs:
        update_dict[AnsibleJob.end_time] = kwargs["end_time"]

    if "result" in kwargs:
        update_dict[AnsibleJob.result] = kwargs["result"]

    if update_dict:
        updated_rows = db.query(AnsibleJob) \
                        .filter(AnsibleJob.job_uuid == job_uuid) \
                        .update(update_dict)

        if updated_rows == 0:
            raise IndexError(f"No job with UUID: {job_uuid}")
        if updated_rows > 1:
            db.rollback()
            raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

        db.commit()


@autowire("db", get_db)
def delete_ansible_job(job_uuid:str, db: Session = None):
    updated_rows = db.query(AnsibleJob) \
                     .filter(AnsibleJob.job_uuid == job_uuid) \
                     .delete()

    if updated_rows == 0:
        raise IndexError(f"No job with UUID: {job_uuid}")
    if updated_rows > 1:
        db.rollback()
        raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

    db.commit()
