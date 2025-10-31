from fastapi import APIRouter, Query
from typing import Optional
from app.services.search_service import SearchService
from app.models.schemas import SearchResponse


router = APIRouter(prefix="/api", tags=["Search"])

search_service = SearchService()


@router.get("/search", response_model=SearchResponse)
async def search_trademarks(
    q: str = Query(..., min_length=1, max_length=100, description="검색 키워드"),
    status: Optional[str] = Query(None, description="등록 상태 필터 (등록/실효/거절/출원)"),
    code: Optional[str] = Query(None, description="상품 분류 코드 (예: 09, 25 등)"),
    date_from: Optional[str] = Query(None, regex=r"^\d{8}$", description="출원일 시작 (YYYYMMDD)"),
    date_to: Optional[str] = Query(None, regex=r"^\d{8}$", description="출원일 종료 (YYYYMMDD)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지당 결과 수")
):
    """
    상표 통합 검색 API
    
    키워드 기반 검색과 다양한 필터링 옵션을 제공합니다.
    한글, 영문, 초성 검색을 모두 지원하며, 등록 상태, 상품 코드,
    날짜 범위 등으로 결과를 필터링할 수 있습니다.
    
    **검색 기능:**
    - 한글 상표명 검색 (예: "삼성")
    - 영문 상표명 검색 (예: "SAMSUNG")
    - 초성 검색 (예: "ㅅㅅ")
    
    **필터링 옵션:**
    - status: 등록 상태별 필터링
    - code: 상품 분류 코드별 필터링
    - date_from/to: 출원일 범위 필터링
    
    **사용 예시:**
    GET /api/search?q=삼성
    GET /api/search?q=ㅅㅅ&status=등록
    GET /api/search?q=삼성&code=09&date_from=20200101&date_to=20231231
    """
    results, filters_applied = search_service.search(
        keyword=q,
        status=status,
        code=code,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=size
    )
    
    return SearchResponse(
        page=page,
        page_size=size,
        results=results,
        filters_applied=filters_applied
    )
