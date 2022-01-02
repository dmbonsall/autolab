import datetime
from typing import Optional

from sqlalchemy.orm import Session

from .data_model import AnsibleJob, AnsibleRunnerStatus


def create_ansible_job(db: Session, job_uuid: str, start_time: datetime.datetime):
    ansible_job = AnsibleJob(job_uuid=job_uuid, start_time=start_time)
    db.add(ansible_job)
    db.commit()
    db.refresh(ansible_job)
    return ansible_job


def get_ansible_job(db: Session, job_uuid: str):
    return db.query(AnsibleJob).filter(AnsibleJob.job_uuid == job_uuid).one()


def get_ansible_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AnsibleJob).offset(skip).limit(limit).all()


def update_ansible_job_status(db: Session, job_uuid: str, status: AnsibleRunnerStatus, end_time: Optional[datetime.datetime] = None):
    updated_rows = db.query(AnsibleJob) \
                     .filter(AnsibleJob.job_uuid == job_uuid) \
                     .update({AnsibleJob.status: status, AnsibleJob.end_time: end_time})

    if updated_rows == 0:
        raise IndexError(f"No job with UUID: {job_uuid}")
    if updated_rows > 1:
        db.rollback()
        raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

    db.commit()
    return get_ansible_job(db, job_uuid)


def delete_ansible_job(db: Session, job_uuid:str):
    updated_rows = db.query(AnsibleJob) \
                     .filter(AnsibleJob.job_uuid == job_uuid) \
                     .delete()

    if updated_rows == 0:
        raise IndexError(f"No job with UUID: {job_uuid}")
    if updated_rows > 1:
        db.rollback()
        raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

    db.commit()
