# 📁 data 폴더 사용법

이 폴더에 매주 시상 Excel 파일 2개를 push하면 앱이 자동으로 최신 파일을 감지합니다.

## 파일 명명 규칙

```
PRIZE_SUM_OUT_YYYYMMDD.xlsx       ← 주차별 시상 데이터
PRIZE_6_BRIDGE_OUT_YYYYMMDD.xlsx  ← 브릿지/연속가동 데이터
```

## 업로드 프로세스

```bash
# 1. 파일을 data/ 폴더에 복사
cp PRIZE_SUM_OUT_20260422.xlsx data/
cp PRIZE_6_BRIDGE_OUT_20260422.xlsx data/

# 2. GitHub push
git add data/
git commit -m "4월 3주차 시상 데이터"
git push
```

→ Streamlit Cloud가 자동 배포하여 최신 데이터 반영

## 주의사항

- 파일명의 날짜(YYYYMMDD)가 가장 큰 파일이 자동 선택됩니다
- 오래된 파일은 삭제해도 되고 그대로 둬도 됩니다 (최신만 사용)
- BRIDGE 파일이 없으면 SUM 파일만으로 운영됩니다
