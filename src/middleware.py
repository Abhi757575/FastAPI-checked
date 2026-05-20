from fastapi import FastAPI, Request, status
from fastapi.requests import Request
import time
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware


logger = logging.getLogger('uvicorn.access')
logger.disabled = True



def register_middleware(app: FastAPI):

    @app.middleware('http')
    async def custom_logging(request:Request, call_next):
        start_time = time.time()
        logger.info("Before")
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.client.port} {response.status_code} {request.url.path} completed in {process_time:.4f} seconds")
        return response
    
    '''
    @app.middleware('http')
    async def authorization(request: Request, call_next):
        if not 'Authorization' in request.headers:
            return JSONResponse(
                content={
                    "message": "Not Authenticated",
                    "resolution": "Please provide the right credentials",
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        response = await call_next(request)
        return response
    '''


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],    
        allow_credentials=True
    )

    #against http host header attacks
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )