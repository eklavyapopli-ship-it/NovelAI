from fastapi import FastAPI, Query
from rq_client.rq_client import queue
from worker import process

app = FastAPI()

@app.get('/')
def root():
    return {"Server":'Server is up and running'}

@app.post('/chat')
def reply(query:str = Query(...,description="User Query"), bookName: str = Query(...,description="Book Name")):
    job = queue.enqueue(process,query)
    return {"status":"queued", "job_id":job.id}

@app.get("/job-status")
def getResult(
        job_id: str = Query(...,description="Job ID")
):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()
    return{"result": result}
