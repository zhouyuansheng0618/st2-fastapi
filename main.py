# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from fastapi import FastAPI, Request
import uvicorn
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from utils.logger import logger
from app.rpa import get_rpa_report, get_rpa_report_excel
from model.rpaModel import DateDuration

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"参数不对{request.method} {request.url}")
    logger.error(f"参数不对{request.method} {request.url}")
    return JSONResponse({"code": "400", "message": exc.errors()})


@app.post("/rpaReport")
def rpa_report(dateDuration: DateDuration):
    reportData = get_rpa_report(dateDuration.fiscal, dateDuration.quarter)['responseData']
    reponse = {
        'message': '',
        'status': 1,
        'data': reportData
    }
    logger.info(f"RPA Report result:{reportData}")
    return reponse


@app.get("/rpaReportExport")
async def rpa_report_export(fiscal: str, quarter: str):

    output = get_rpa_report_excel(fiscal, quarter)
    headers = {
        'Content-Disposition': 'attachment; filename="rpaReport.xlsx"'
    }
    return StreamingResponse(output, headers=headers)


if __name__ == '__main__':
    # uvicorn.run(app=app, host="0.0.0.0", port=800, ssl_keyfile="./ssl/st2.key", ssl_certfile="./ssl/st2.crt")
    uvicorn.run(app=app, host="0.0.0.0", port=800)