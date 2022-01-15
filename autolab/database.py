from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .data_model import AnsibleJob, AnsibleRunnerStatus


class DatabaseNotInitializedError(RuntimeError):
    pass


def null_sessionmaker() -> Session:
    raise DatabaseNotInitializedError()


_SessionLocal = null_sessionmaker
_engine = None


def initialize(db_url):
    global _engine
    global _SessionLocal
    if _engine is None:
        _engine = create_engine(
            db_url, connect_args={"check_same_thread": False}
        )

        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    else:
        raise RuntimeWarning("Database already initialized.")

def get_engine():
    if _engine is None:
        raise DatabaseNotInitializedError()

    return _engine

def create_ansible_job(job_uuid: str, job_name: str, initiator: str):
    with _SessionLocal() as session:
        ansible_job = AnsibleJob(job_uuid=job_uuid, job_name=job_name, initiator=initiator,
                                 status=AnsibleRunnerStatus.CREATED)
        session.add(ansible_job)
        session.commit()
        session.refresh(ansible_job)
        return ansible_job


def get_ansible_job(job_uuid: str):
    with _SessionLocal() as session:
        return session.query(AnsibleJob).filter(AnsibleJob.job_uuid == job_uuid).one()


def get_ansible_jobs(skip: int = 0, limit: int = 100):
    with _SessionLocal() as session:
        return session.query(AnsibleJob).order_by(AnsibleJob.start_time.desc()).offset(skip).limit(limit).all()


def update_ansible_job(job_uuid: str, **kwargs):
    update_dict = {}
    if "status" in kwargs:
        update_dict[AnsibleJob.status] = kwargs["status"]

    if "start_time" in kwargs:
        update_dict[AnsibleJob.start_time] = kwargs["start_time"]

    if "end_time" in kwargs:
        update_dict[AnsibleJob.end_time] = kwargs["end_time"]

    if "result" in kwargs:
        update_dict[AnsibleJob.result] = kwargs["result"]

    if update_dict:
        with _SessionLocal() as session:
            updated_rows = session.query(AnsibleJob) \
                            .filter(AnsibleJob.job_uuid == job_uuid) \
                            .update(update_dict)

            if updated_rows == 0:
                raise IndexError(f"No job with UUID: {job_uuid}")
            if updated_rows > 1:
                session.rollback()
                raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

            session.commit()


def delete_ansible_job(job_uuid:str):
    with _SessionLocal() as session:
        updated_rows = session.query(AnsibleJob) \
                              .filter(AnsibleJob.job_uuid == job_uuid) \
                              .delete()

        if updated_rows == 0:
            raise IndexError(f"No job with UUID: {job_uuid}")
        if updated_rows > 1:
            session.rollback()
            raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

        session.commit()
