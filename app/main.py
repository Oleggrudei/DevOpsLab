from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as router_auth
from app.admin.router import router as router_admin
app = FastAPI()

app.include_router(router_auth, prefix='/auth', tags=['Auth'])
app.include_router(router_admin, prefix='/admin', tags=['Admin'])

origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", 'PUT'],
    allow_headers=["Content-Type", "Access-Control-Allow-Origin", "Access-Control-Allow-Headers", "Set-Cookie",
                   "Authorization"],
)