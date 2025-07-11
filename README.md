# 스타벅스 제주 매장 데이터 수집기

이 프로젝트는 스타벅스 공식 웹사이트에서 제주 지역의 모든 매장 정보를 자동으로 수집하는 파이썬 스크립트입니다.

## 기능

- 스타벅스 매장 지도 페이지 자동 접속
- 지역검색 → 제주 선택 → 전체 매장 선택 자동화
- 매장명, 주소, 전화번호 정보 수집
- CSV 및 JSON 형식으로 데이터 저장

## 설치 방법

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

2. Chrome 브라우저가 설치되어 있어야 합니다.

## 사용 방법

```bash
python starbucks_scraper.py
```

## 출력 파일

- `starbucks_jeju_stores.csv`: CSV 형식의 매장 데이터
- `starbucks_jeju_stores.json`: JSON 형식의 매장 데이터

## 수집되는 데이터

- 매장명
- 주소
- 전화번호
- 수집일시

## 주의사항

- 웹사이트 구조 변경 시 스크립트 수정이 필요할 수 있습니다.
- 과도한 요청은 서버에 부하를 줄 수 있으니 적절한 간격을 두고 사용하세요.
- 수집된 데이터는 개인적인 용도로만 사용하시기 바랍니다.

## 문제 해결

만약 스크래핑이 실패한다면:

1. Chrome 브라우저가 최신 버전인지 확인
2. 인터넷 연결 상태 확인
3. 웹사이트 접근 가능 여부 확인
4. CSS 선택자가 변경되었을 수 있으니 개발자 도구로 확인
