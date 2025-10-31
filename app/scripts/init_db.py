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
    print("=" * 60)
    print("상표 검색 API - 데이터베이스 초기화")
    print("=" * 60)
    
    print("\n1️⃣  데이터베이스 테이블 생성 중...")
    init_db()
    
    print("\n2️⃣  JSON 파일 읽는 중...")
    try:
        with open('data/trademark_sample.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   📦 {len(data)}개 데이터 발견")
    except FileNotFoundError:
        print("   ❌ 오류: data/trademark_sample.json 파일을 찾을 수 없습니다")
        print("   trademark_sample.json 파일을 data/ 폴더에 복사해주세요")
        return
    
    print("\n3️⃣  데이터베이스에 삽입 중...")
    
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
                print(f"   ⚠️  데이터 삽입 실패: {item.get('applicationNumber')} - {e}")
                skipped += 1
        
        conn.commit()
        print(f"   ✅ {inserted}개 삽입 완료")
        if skipped > 0:
            print(f"   ⏭️  {skipped}개 스킵 (중복 또는 오류)")
    
    print("\n" + "=" * 60)
    print("✨ 초기화 완료!")
    print("=" * 60)
    print("\n다음 명령어로 서버를 실행하세요:")
    print("  python -m app.main")
    print("\n또는:")
    print("  uvicorn app.main:app --reload")
    print("\n그 후 브라우저에서 다음 주소로 접속:")
    print("  http://localhost:8000/docs")


if __name__ == "__main__":
    load_data()
