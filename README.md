# 상표 검색 API
---

## 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화
```bash
python -m app.scripts.init_db
```

### 3. 서버 실행
```bash
python -m app.main
```

### 4. API 테스트
브라우저에서 http://localhost:8000/docs 접속

### 5. 검색 예시
```bash
# 기본 검색
curl "http://localhost:8000/api/search?q=삼성"

# 초성 검색
curl "http://localhost:8000/api/search?q=ㅅㅅ"

# 필터링
curl "http://localhost:8000/api/search?q=삼성&status=등록&code=09"
```

---

## 구현된 기능

### 1. 상표 검색 API (GET /api/search)

**주요 기능:**
- 키워드 검색 (한글/영문/초성 모두 지원)
- 다중 필터링 (상태, 상품 코드, 날짜 범위)

**파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| q | string | ✅ | 검색 키워드 |
| status | string | ❌ | 등록 상태 (등록/실효/거절/출원) |
| code | string | ❌ | 상품 분류 코드 (예: 09) |
| date_from | string | ❌ | 출원일 시작 (YYYYMMDD) |
| date_to | string | ❌ | 출원일 종료 (YYYYMMDD) |
| page | int | ❌ | 페이지 번호 (기본: 1) |
| size | int | ❌ | 페이지 크기 (기본: 20) |

**응답 예시:**
```json
{
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "app_number": "4019700000623",
      "name_kr": "삼성전자",
      "name_en": "SAMSUNG",
      "status": "등록",
      "app_date": "19900101"
    }
  ],
  "filters_applied": {
    "status": "등록"
  }
}
```

### 2. 초성 검색
- "ㅅㅅ" 입력 시 "삼성" 자동 매칭
- 모바일 환경 최적화

---

## 🛠 기술적 의사결정

### 1. FastAPI 선택

**이유:**
- Swagger 자동 생성으로 API 문서화 및 테스트 간편
- Pydantic 기반 자동 검증으로 개발 속도 향상
- 비동기 지원으로 높은 성능

### 2. SQLite 선택

**이유:**
- 설치 불필요, 단일 파일로 배포 간편
- 500개 데이터에서 충분한 성능
- SQL 표준 지원으로 PostgreSQL 전환 쉬움

**확장성:**
- 10만 건까지는 SQLite로 충분
- 이후 PostgreSQL GIN 인덱스로 전환 계획

### 3. 초성 검색 구현

**이유:**
- 모바일 환경에서 한글 입력 불편함 해결

**구현 방법:**
- 한글 유니코드 분해 알고리즘 직접 구현
- DB에 초성 컬럼 추가 및 인덱스 생성
- SQL LIKE 연산으로 간단히 검색

### 4. 모듈 구조 설계

**이유:**
- API / 비즈니스 로직 / 데이터 계층 분리
- 각 모듈 100줄 이내로 가독성 유지
- 테스트 및 유지보수 용이

**구조:**
```
app/
├── api/           # 라우터 (HTTP 처리)
├── services/      # 비즈니스 로직
├── models/        # 데이터 모델
└── core/          # DB, 유틸리티
```

---

## 💡 문제 해결 과정

### 1. 결측치 처리 문제

**문제:**
- 검색 시 null 데이터 처리 방법

**해결:**
```python
# SQL LIKE 연산은 null을 자동으로 제외
WHERE name_kr LIKE '%삼성%' OR name_en LIKE '%SAMSUNG%'
```

- 별도 null 체크 불필요
- 한글/영문 둘 다 검색하여 커버율 향상
- Optional 타입으로 API에서 명시적 처리

### 2. 배열 필드 검색 문제

**문제:**
- asignProductMainCodeList가 JSON 배열
- SQLite에서 배열 검색 어려움

**시도한 방법:**
1. 별도 테이블로 정규화 → 복잡도 증가
2. SQLite JSON1 확장 → 호환성 문제
3. JSON 문자열로 저장 + LIKE 검색 ✓

**최종 해결:**
```python
codes = json.dumps(['09', '16'])  # '["09","16"]'
query += " AND codes LIKE ?"
params.append(f'%"{code}"%')
```

**장점:**
- 간단하고 직관적
- 인덱스 불필요 (500개 데이터)
- PostgreSQL JSONB로 쉽게 전환 가능

### 3. 초성 검색 성능 문제

**문제:**
- 매 검색마다 초성 추출하면 느림

**해결:**
```python
# 데이터 로드 시 미리 초성 추출하여 저장
chosung = get_chosung(item.get('productName', ''))

# 인덱스 생성으로 빠른 검색
CREATE INDEX idx_chosung ON trademarks(chosung)
```

**성능 개선:**
- 초기 로딩 시간만 약간 증가 (1회성)

---

## 🔮 개선하고 싶은 부분

### 시간이 더 있었다면 구현했을 기능

#### 1. 자동완성 API
**현재:** 전체 키워드 입력 필요
**개선:**
```python
@app.get("/api/autocomplete")
def autocomplete(q: str):
    # 초성/글자 일부만으로도 추천
    return ["삼성전자", "삼성화재", "삼성생명"]
```

#### 2. 테스트 코드
**현재:** 수동 테스트만
**개선:**
```python
def test_search_basic():
    response = client.get("/api/search?q=삼성")
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0
```
- pytest로 자동화 테스트
- CI/CD 파이프라인 구축

#### 3. 캐싱 전략
**현재:** 매번 DB 조회
**개선:**
- Redis로 인기 검색어 캐싱
- 응답 속도 10배 향상 가능

### 알고 있는 한계점

#### 1. SQLite 동시성 제한
- 현재: 읽기는 동시 가능, 쓰기는 순차
- 영향: 검색만 하므로 문제 없음
- 개선: PostgreSQL 전환 시 해결

#### 2. 대용량 데이터 대응
- 현재: 500개로 최적화
- 한계: 100만 건에서는 느려질 수 있음
- 개선: Elasticsearch 도입 또는 PostgreSQL GIN 인덱스

---

## 📁 프로젝트 구조

```
trademark-api/
├── app/
│   ├── main.py              # FastAPI 앱
│   ├── api/
│   │   └── search.py        # 검색 API 라우터
│   ├── services/
│   │   └── search_service.py # 검색 비즈니스 로직
│   ├── models/
│   │   └── schemas.py       # 데이터 모델
│   └── core/
│       ├── database.py      # DB 연결
│       └── utils.py         # 유틸리티
├── scripts/
│   └── init_db.py           # DB 초기화
├── requirements.txt
├── README.md
└── data/
    └── trademark_sample.json
```

---
