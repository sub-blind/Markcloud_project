import json
import sys
from pathlib import Path
from app.core.database import init_db, get_db
from app.core.utils import get_chosung

sys.path.append(str(Path(__file__).parent.parent))

def load_data():
    """
    JSON 데이터를 데이터베이스에 로드하는 메인 함수
    처리 단계:
    1. 데이터베이스 테이블 및 인덱스 생성
    2. JSON 파일 읽기
    3. 각 레코드의 초성 추출 및 데이터 변환
    4. 데이터베이스에 삽입
    """
    init_db()
    try:
        with open('data/trademark_sample.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("1")
        return
    
    with get_db() as conn:
        cursor = conn.cursor()
        inserted = 0
        skipped = 0
        
        for item in data:
            try:
                chosung = get_chosung(item.get('productName', ''))
                codes = json.dumps(item.get('asignProductMainCodeList'))
                
                cursor.execute("""
                INSERT OR IGNORE INTO trademarks (
                    app_number, name_kr, name_en, status, 
                    app_date, codes, chosung
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('applicationNumber'),
                    item.get('productName'),
                    item.get('productNameEng'),
                    item.get('registerStatus'),
                    item.get('applicationDate'),
                    codes,
                    chosung
                ))
                
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            
            except Exception as e:
                skipped += 1
        
        conn.commit()

if __name__ == "__main__":
    load_data()
