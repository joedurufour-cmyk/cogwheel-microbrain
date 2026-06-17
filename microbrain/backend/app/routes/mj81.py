from fastapi import APIRouter
from pydantic import BaseModel

from app.engine.mj81_compiler import compile_mj81, compile_mj81_all_styles

router = APIRouter(prefix="/api/mj81", tags=["mj81"])


class CompileRequest(BaseModel):
    input_text: str
    params: dict = {}


@router.post("/compile")
def compile_endpoint(req: CompileRequest):
    return compile_mj81(req.input_text, req.params)


@router.post("/compile-styles")
def compile_styles_endpoint(req: CompileRequest):
    return compile_mj81_all_styles(req.input_text, req.params)
