from fastapi import FastAPI, Query
from rq_client.rq_client import queue
from fastapi.middleware.cors import CORSMiddleware
from worker import process

origins = ["http://localhost:3000"]  # Next.js frontend



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {"Server":'Server is up and running'}

@app.post('/chat')
def reply(query:str = Query(...,description="User Query")):
    job = queue.enqueue(process,query)
    return {"status":"queued", "job_id":job.id}

@app.get("/job-status")
def getResult(job_id: str = Query(...)):
    job = queue.fetch_job(job_id)

    if not job:
        return {"status": "not_found"}

    if job.is_finished:
        return {
            "status": "finished",
            "result": job.return_value()
        }

    if job.is_failed:
        return {"status": "failed"}

    return {"status": job.get_status()}

