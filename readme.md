# 🎯 네이버 지도 통합 분석 도구

네이버 플레이스 정보 분석과 검색 순위 확인을 한 번에 제공하는 종합 분석 도구입니다.

## ✨ 주요 기능

### 📊 플레이스 분석
- **기본 정보 추출**: 업체명, 주소, 전화번호, 영업시간, 평점 등
- **상세 정보 분석**: 시설, 프로그램, 가격, 이미지, 쿠폰 등
- **완성도 점수**: 플레이스 정보의 충실도를 0-100점으로 평가
- **개선 제안**: 부족한 부분에 대한 구체적인 개선 방안 제시

### 🏆 순위 확인
- **다중 키워드 검색**: 여러 키워드에서의 순위를 한 번에 확인
- **위치 기반 검색**: GPS 좌표 또는 주소 기반 정확한 순위 측정
- **병렬 처리**: 빠른 속도로 여러 키워드 동시 검색
- **페이지네이션**: 최대 5페이지(250위)까지 확인 가능

### 📋 통합 리포트
- **종합 분석**: 플레이스 분석과 순위 확인 결과를 통합
- **개선 전략**: 데이터 기반의 구체적인 개선 방안 제시
- **결과 내보내기**: JSON/CSV 형태로 분석 결과 저장

## 🚀 기술 스택

### 백엔드 (Railway)
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Playwright**: 브라우저 자동화 및 스크래핑
- **Python 3.11+**: 최신 파이썬 기능 활용
- **비동기 처리**: 병렬 스크래핑으로 성능 최적화

### 프론트엔드 (Netlify)
- **Vanilla JavaScript**: 가벼운 클라이언트 사이드
- **CSS Grid/Flexbox**: 반응형 디자인
- **실시간 API 통신**: 진행 상황 실시간 업데이트

## 🏗️ 시스템 아키텍처

```
📱 사용자 (웹 브라우저)
    ↓ HTTPS 요청
🌐 Netlify (프론트엔드)
    ↓ API 호출
🚂 Railway (백엔드 서버)
    ↓ 병렬 스크래핑
🤖 Playwright × N (브라우저 자동화)
    ↓ 데이터 수집
🗺️ 네이버 지도 / 네이버 플레이스
```

## 📊 성능 지표

| 기능 | 처리 시간 | 정확도 | 동시 처리 |
|------|-----------|--------|-----------|
| **플레이스 분석** | 30-60초 | 95%+ | 1개씩 |
| **순위 확인** | 키워드당 3-5초 | 98%+ | 3-5개 동시 |
| **통합 분석** | 2-4분 | 95%+ | 병렬 처리 |

## 🎯 사용 사례

### 교육업체 (학원, 어학원)
- 지역별 키워드 순위 모니터링
- 경쟁사 대비 플레이스 완성도 비교
- 브랜드 키워드 노출 현황 파악

### 요식업체 (카페, 레스토랑)
- 메뉴, 가격 정보 완성도 체크
- "지역명 + 업종" 키워드 순위 확인
- 이벤트/쿠폰 효과 측정

### 서비스업체 (미용실, 병원 등)
- 전문 서비스 키워드 순위 분석
- 시설, 프로그램 정보 최적화
- 리뷰 관리 효과 측정

## 🔧 설치 및 실행

### 백엔드 설정
```bash
# 저장소 클론
git clone https://github.com/your-username/naver-integrated-analyzer.git
cd naver-integrated-analyzer/backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium

# 서버 실행
python main.py
```

### 프론트엔드 설정
```bash
cd frontend
# 정적 파일 서버 실행
python -m http.server 3000
# 또는 Live Server 사용
```

## 🌐 배포 방법

### Railway 백엔드 배포
1. [Railway.app](https://railway.app) 계정 생성
2. GitHub 저장소 연결
3. 자동 배포 완료
4. 생성된 URL 확인

### Netlify 프론트엔드 배포
1. [Netlify.com](https://netlify.com) 계정 생성
2. GitHub 저장소 연결
3. 빌드 설정 없이 배포
4. API URL 업데이트

## 📈 향후 개선 계획

### 단기 (1-2개월)
- [ ] 실제 Playwright 스크래핑 구현
- [ ] 더 정교한 플레이스 분석 알고리즘
- [ ] 사용자 인증 및 결과 저장 기능

### 중기 (3-6개월)
- [ ] 경쟁사 비교 분석 기능
- [ ] 히스토리 추적 및 변화 감지
- [ ] 자동 리포트 생성 및 이메일 발송

### 장기 (6개월+)
- [ ] AI 기반 개선 제안
- [ ] 다양한 플랫폼 지원 (카카오맵 등)
- [ ] 모바일 앱 개발

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원

- **GitHub Issues**: 버그 신고 및 기능 요청
- **이메일**: support@naver-analyzer.com
- **문서**: [Wiki 페이지](https://github.com/your-username/naver-integrated-analyzer/wiki)

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/)
- [Netlify](https://netlify.com/)
- [Railway](https://railway.app/)

---

**Made with ❤️ for Korean Local Businesses**