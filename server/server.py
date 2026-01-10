from fastapi import FastAPI, Query, WebSocket
from rq_client.rq_client import queue
import asyncio
from fastapi.responses import HTMLResponse
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

@app.websocket("/job-status")
async def getResult(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    while True:
        job = queue.fetch_job(data)

        if not job:
            await websocket.send_json({"status":"not found"})
            await websocket.close()
            return

        if job.is_finished:
            await websocket.send_json({
            "status": "finished",
            "result": job.return_value()
        })
            await websocket.close()
            return

        if job.is_failed:
            await websocket.send_json({"status": "failed"})
            await websocket.close()
            return

        await asyncio.sleep(1)


