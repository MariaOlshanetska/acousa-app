from fastapi import FastAPI
from core.config import init_app

from routers.home import router as home_router
from routers.recursos import router as recursos_router
from routers.clinica import router as clinica_router
from routers.tfg_mails import router as tfg_mails_router

app = FastAPI()
init_app(app)

app.include_router(home_router)
app.include_router(recursos_router)
app.include_router(clinica_router)
app.include_router(tfg_mails_router)

