# ==============================================================================
# JOB STATE MANAGEMENT FILE
# ==============================================================================
from typing import Dict, Any

# This acts as our in-memory "database" to track job statuses
jobs: Dict[str, Dict[str, Any]] = {}

def get_job(job_id: str):
    return jobs.get(job_id)

def create_job(job_id: str):
    jobs[job_id] = {"status": "starting", "result_path": None, "error": None}

def update_job_status(job_id: str, status: str, error: str = None):
    if job_id in jobs:
        jobs[job_id]["status"] = status
        if error:
            jobs[job_id]["error"] = error

def set_job_result(job_id: str, result_path: str):
    if job_id in jobs:
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["result_path"] = result_path