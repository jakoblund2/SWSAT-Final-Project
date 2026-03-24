from fastapi import FastAPI
from backend.database.sqlite import (get_latest_schedule, read_rejectpass_from_id, initialize_database, get_specific_schedule, run_schedule)

app = FastAPI()

# Define your API endpoints here




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
@app.get("/schedule/{id}")
def read_specific_schedule(id: int):
    schedule = get_specific_schedule(id)
    return {"schedule": schedule}

# get rejected passes based on id
@app.get("/rejected-passes/{id}")
def get_rejected_passes(id: int):
    
    rejected_passes = read_rejectpass_from_id(id)
    return {"rejected_passes": rejected_passes}

