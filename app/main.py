from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import search
from app.core.database import init_db


app = FastAPI(
    title="상표 검색 API",
    description="""
    
    ### 기술 특징
    - 초성 검색으로 모바일 사용성 향상
    - 인덱스 기반 빠른 검색 성능
    - 확장 가능한 모듈 구조
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/", tags=["Root"])
async def root():
    """
    API 루트 엔드포인트
    
    API의 기본 정보를 제공합니다.
    """
    return {
        "message": "상표 검색 API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "키워드 검색 (한글/영문/초성)",
            "필터링 (상태/코드/날짜)",
            "페이지네이션"
        ]
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """
    서비스의 정상 작동 여부를 확인
    """
    return {"status": "healthy"}

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
