from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from responder import ReplyRequest, generate_reply

app = FastAPI(title="AI Customer Message Auto-Responder")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/reply", response_class=HTMLResponse)
async def reply(
    request: Request,
    business_name: str = Form(...),
    brand_voice: str = Form("professional"),
    policy_notes: str = Form(""),
    customer_message: str = Form(...),
):
    req = ReplyRequest(
        business_name=business_name,
        brand_voice=brand_voice,
        policy_notes=policy_notes,
        customer_message=customer_message,
    )
    result = await generate_reply(req)
    return templates.TemplateResponse("result.html", {"request": request, "req": req, "result": result})
