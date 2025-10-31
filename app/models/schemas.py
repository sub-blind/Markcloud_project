from pydantic import BaseModel, Field, validator
from typing import Optional, List


class TrademarkResponse(BaseModel):
    """
    응답 모델
    검색 결과로 반환되는 정보
    """
    app_number: str = Field(..., description="출원 번호")
    name_kr: Optional[str] = Field(None, description="상표명(한글)")
    name_en: Optional[str] = Field(None, description="상표명(영어)")
    status: Optional[str] = Field(None, description="등록 상태 (등록, 실효, 거절, 출원)")
    app_date: Optional[str] = Field(None, description="출원일 (YYYYMMDD)")
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    """
    검색 응답 모델
    """
    page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지 크기")
    results: List[TrademarkResponse] = Field(..., description="검색 결과")
    filters_applied: dict = Field(..., description="적용된 필터")


