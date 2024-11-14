from fastapi import FastAPI, BackgroundTasks
from app.tasks import process_sales_data

app = FastAPI()


@app.post("/trigger")
async def trigger_report(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_sales_data)
    return {"message": "Report generation started"}
