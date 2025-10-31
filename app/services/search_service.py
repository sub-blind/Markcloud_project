from typing import Optional, List, Tuple
import math
from app.core.database import get_db
from app.models.schemas import TrademarkResponse, SearchResponse
from app.core.utils import get_chosung, is_chosung


class SearchService: 
    """
    상표 검색 서비스
    """
    def search(
        self,
        keyword: str,
        status: Optional[str] = None,
        code: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int =1,
        page_size: int=20
    ) -> Tuple[List[TrademarkResponse], dict]:
        with get_db() as conn:
            cursor = conn.cursor()

            # 1. 기본 쿼리 작성 한글, 영문, 초성
            chosung = get_chosung(keyword)
            query = """
                SELECT * FROM trademarks
                WHERE (name_kr LIKE ? OR name_en LIKE ? OR chosung LIKE ?)
            """
            params = [f"%{keyword}%", f"%{keyword}%", f"%{chosung}%"]

            # 2. 필터링 조건 추가
            filters_applied = {}

            # 상태 필터
            if status:
                query += " AND status = ?"
                params.append(status)
                filters_applied['status'] = status
            
            # 상품 코드 필터
            if code:
                query += " AND codes LIKE ?"
                params.append(f"%{code}%")
                filters_applied['code'] = code

            if date_from:
                query += " AND app_date >= ?"
                params.append(date_from)
                filters_applied['date_from'] = date_from

            if date_to:
                query += " AND app_date <= ?"
                params.append(date_to)
                filters_applied['date_to'] = date_to

            # 페이지네이션
            query += " LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])

            # 쿼리 실행
            rows = cursor.execute(query, params).fetchall()

            # 6. 결과 매핑
            results = [
                TrademarkResponse(
                    app_number=row['app_number'],
                    name_kr=row['name_kr'],
                    name_en=row['name_en'],
                    status=row['status'],
                    app_date=row['app_date']
                )
                for row in rows
            ]
            return results, filters_applied
        
