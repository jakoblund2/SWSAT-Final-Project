from fastapi import FastAPI
from backend.database.sqlite import (get_latest_schedule, read_rejectpass_from_schedule_id, initialize_database, get_specific_schedule, run_schedule)

app = FastAPI()

# POST
@app.post("/schedule/run")
def run_schedule_endpoint():
    run_schedule()
    return {"message": "schedule ran"}

# GET schedule
@app.get("/schedule")
def read_schedule():
    schedule = get_latest_schedule()
    return {"schedule": schedule}

# GET specific schedule based on id
@app.get("/schedule/{schedule_id}")
def read_specific_schedule(schedule_id: int):
    schedule = get_specific_schedule(schedule_id)
    return {"schedule": schedule}

# get rejected passes based on id
@app.get("/rejected-passes/{schedule_id}")
def get_rejected_passes(schedule_id: int):
    
    rejected_passes = read_rejectpass_from_schedule_id(schedule_id)
    return {"rejected_passes": rejected_passes}

