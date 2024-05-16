import fastapi
from fastapi import HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from .captcha_solver.solve_captcha_with_model import CaptchaSolver

capsolver = CaptchaSolver('captcha_solver')
app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class SolveURLRequest(BaseModel):
    url: str


@app.post('/solve/url')
async def solve_url(request: SolveURLRequest):
    res = capsolver.solve_from_url(request.url)
    if res:
        return Response(status_code=HTTP_200_OK, content=res)
    raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8090)
