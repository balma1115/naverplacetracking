// API 설정
const API_CONFIG = {
    development: 'http://localhost:8000',
    production: 'https://your-railway-app.railway.app'
};

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? API_CONFIG.development 
    : API_CONFIG.production;

// 전역 변수
let placeAnalysisData = null;
let rankingData = null;
let currentJobId = null;

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    checkApiConnection();
    setupEventListeners();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    // 키워드 입력에서 Enter 키
    document.getElementById('keywordInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addKeyword();
        }
    });
}

// 탭 전환
function switchTab(tabId) {
    // 모든 탭 비활성화
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // 선택된 탭 활성화
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
    
    // 통합 리포트 탭 선택시 리포트 업데이트
    if (tabId === 'integrated-report') {
        updateIntegratedReport();
    }
}

// API 서버 연결 확인
async function checkApiConnection() {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            statusDot.classList.add('connected');
            statusText.textContent = 'API 서버 연결됨';
        } else {
            throw new Error('서버 응답 오류');
        }
    } catch (error) {
        statusText.textContent = 'API 서버 연결 실패 - 데모 모드';
        console.error('API 연결 오류:', error);
    }
}

// 플레이스 정보 분석
async function analyzePlaceInfo() {
    const url = document.getElementById('placeUrl').value.trim();
    if (!url) {
        alert('네이버 플레이스 URL을 입력해주세요.');
        return;
    }
    
    // 진행 표시
    showPlaceAnalysisProgress();
    
    try {
        // API 호출 (실제로는 백엔드에서 플레이스 스크래핑 수행)
        const response = await fetch(`${API_BASE_URL}/api/analyze-place`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayPlaceAnalysisResults(data);
        } else {
            // 데모 모드 - 샘플 데이터 사용
            const sampleData = generateSamplePlaceData(url);
            displayPlaceAnalysisResults(sampleData);
        }
    } catch (error) {
        console.error('플레이스 분석 오류:', error);
        // 데모 모드 - 샘플 데이터 사용
        const sampleData = generateSamplePlaceData(url);
        displayPlaceAnalysisResults(sampleData);
    }
}

// 플레이스 분석 진행 표시
function showPlaceAnalysisProgress() {
    // 진행률 시뮬레이션
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress > 100) {
            progress = 100;
            clearInterval(interval);
        }
    }, 200);
}

// 샘플 플레이스 데이터 생성
function generateSamplePlaceData(url) {
    const businessName = extractBusinessNameFromUrl(url) || "미래엔영어수학 벌원학원";
    
    return {
        basic_info: {
            name: businessName,
            category: "영어학원",
            address: "광주광역시 서구 벌원동 123-45",
            phone: "062-123-4567",
            hours: "월~금 14:00-22:00, 토 09:00-18:00",
            rating: 4.2,
            review_count: 28
        },
        details: {
            description: "미래엔 교재를 사용하는 체계적인 영어교육 전문학원입니다. 초등부터 중등까지 단계별 맞춤 교육을 제공합니다.",
            facilities: ["주차장", "상담실", "독서실", "대기실"],
            programs: ["초등영어", "중등영어", "파닉스", "회화"],
            pricing: "월 12만원~18만원 (과정별 상이)",
            images: [
                "학원 외관", "교실 내부", "상담실", "교재", "수업 모습"
            ],
            coupons: ["무료 체험 수업", "형제 할인 10%"],
            keywords: ["벌원학원", "영어학원", "초등영어"]
        },
        analysis: {
            completeness_score: 75,
            missing_elements: ["상세 프로그램 설명", "교사 소개", "미래엔 브랜드 키워드"],
            strengths: ["기본 정보 완성", "이미지 등록", "할인 혜택"],
            recommendations: [
                {
                    priority: "high",
                    title: "브랜드 키워드 추가",
                    description: "'미래엔영어', '미래엔 교재' 등 브랜드 연관 키워드를 추가하세요."
                },
                {
                    priority: "medium", 
                    title: "프로그램 상세 설명",
                    description: "각 과정별 특징과 교육 방식을 구체적으로 설명하세요."
                },
                {
                    priority: "medium",
                    title: "이미지 콘텐츠 보강",
                    description: "미래엔 교재 활용 모습, 교사진 소개 사진을 추가하세요."
                }
            ]
        }
    };
}

// URL에서 업체명 추출
function extractBusinessNameFromUrl(url) {
    try {
        const matches = url.match(/search\/([^/]+)/);
        if (matches) {
            return decodeURIComponent(matches[1]);
        }
    } catch (error) {
        console.error('URL 파싱 오류:', error);
    }
    return null;
}

// 플레이스 분석 결과 표시
function displayPlaceAnalysisResults(data) {
    placeAnalysisData = data;
    
    // 점수 표시
    document.getElementById('placeScore').textContent = data.analysis.completeness_score;
    
    // 등급 표시
    const gradeElement = document.getElementById('placeGrade');
    const score = data.analysis.completeness_score;
    if (score >= 80) {
        gradeElement.textContent = '우수 🎉';
        gradeElement.className = 'status-indicator status-complete';
    } else if (score >= 60) {
        gradeElement.textContent = '보통 📈';
        gradeElement.className = 'status-indicator status-partial';
    } else {
        gradeElement.textContent = '개선 필요 📝';
        gradeElement.className = 'status-indicator status-incomplete';
    }
    
    // 기본 정보 표시
    const basicInfoList = document.getElementById('basicInfoList');
    basicInfoList.innerHTML = `
        <div class="info-item">
            <span class="info-label">업체명</span>
            <span class="info-value">${data.basic_info.name}</span>
        </div>
        <div class="info-item">
            <span class="info-label">업종</span>
            <span class="info-value">${data.basic_info.category}</span>
        </div>
        <div class="info-item">
            <span class="info-label">주소</span>
            <span class="info-value">${data.basic_info.address}</span>
        </div>
        <div class="info-item">
            <span class="info-label">전화번호</span>
            <span class="info-value">${data.basic_info.phone}</span>
        </div>
        <div class="info-item">
            <span class="info-label">평점</span>
            <span class="info-value">⭐ ${data.basic_info.rating} (${data.basic_info.review_count}개)</span>
        </div>
    `;
    
    // 상세 정보 카드들 표시
    const placeInfoGrid = document.getElementById('placeInfoGrid');
    placeInfoGrid.innerHTML = `
        <div class="place-info-card">
            <h4>📝 상세 설명</h4>
            <p>${data.details.description}</p>
        </div>
        
        <div class="place-info-card">
            <h4>🏢 편의시설</h4>
            <div class="keyword-list">
                ${data.details.facilities.map(facility => 
                    `<span class="keyword-tag">${facility}</span>`
                ).join('')}
            </div>
        </div>
        
        <div class="place-info-card">
            <h4>📚 프로그램</h4>
            <div class="keyword-list">
                ${data.details.programs.map(program => 
                    `<span class="keyword-tag">${program}</span>`
                ).join('')}
            </div>
        </div>
        
        <div class="place-info-card">
            <h4>💰 수강료</h4>
            <p>${data.details.pricing}</p>
        </div>
        
        <div class="place-info-card">
            <h4>🎫 쿠폰/이벤트</h4>
            <div class="keyword-list">
                ${data.details.coupons.map(coupon => 
                    `<span class="keyword-tag">${coupon}</span>`
                ).join('')}
            </div>
        </div>
        
        <div class="place-info-card">
            <h4>🏷️ 대표 키워드</h4>
            <div class="keyword-list">
                ${data.details.keywords.map(keyword => 
                    `<span class="keyword-tag">${keyword}</span>`
                ).join('')}
                <span class="keyword-tag missing">미래엔영어 (누락)</span>
                <span class="keyword-tag missing">파닉스 (누락)</span>
            </div>
        </div>
    `;
    
    // 추천사항 표시
    const placeRecommendations = document.getElementById('placeRecommendations');
    placeRecommendations.innerHTML = data.analysis.recommendations.map(rec => `
        <div class="recommendation-item priority-${rec.priority}">
            <strong>${rec.title}</strong><br>
            ${rec.description}
        </div>
    `).join('');
    
    // 결과 섹션 표시
    document.getElementById('placeResults').style.display = 'block';
}

// 키워드 추가
function addKeyword() {
    const input = document.getElementById('keywordInput');
    const keyword = input.value.trim();
    
    if (!keyword) {
        alert('키워드를 입력해주세요.');
        return;
    }
    
    // 중복 체크
    const existingKeywords = getKeywords();
    if (existingKeywords.includes(keyword)) {
        alert('이미 추가된 키워드입니다.');
        return;
    }
    
    // 키워드 태그 생성
    const keywordsList = document.getElementById('keywordsList');
    const keywordTag = document.createElement('div');
    keywordTag.className = 'keyword-tag';
    keywordTag.innerHTML = `${keyword} <span onclick="removeKeyword(this)" style="cursor: pointer; margin-left: 5px;">×</span>`;
    
    keywordsList.appendChild(keywordTag);
    input.value = '';
}

// 키워드 제거
function removeKeyword(element) {
    element.parentElement.remove();
}

// 현재 키워드 목록 가져오기
function getKeywords() {
    return Array.from(document.querySelectorAll('#keywordsList .keyword-tag')).map(tag => 
        tag.textContent.replace('×', '').trim()
    );
}

// 순위 확인 시작
async function startRankingCheck() {
    const targetBusiness = document.getElementById('targetBusiness').value.trim();
    const keywords = getKeywords();
    const latitude = parseFloat(document.getElementById('latitude').value) || 35.1379;
    const longitude = parseFloat(document.getElementById('longitude').value) || 126.7794;
    
    if (!targetBusiness) {
        alert('목표 업체명을 입력해주세요.');
        return;
    }
    
    if (keywords.length === 0) {
        alert('검색 키워드를 하나 이상 추가해주세요.');
        return;
    }
    
    // 진행 상황 표시
    document.getElementById('rankingProgress').style.display = 'block';
    document.getElementById('rankingResults').style.display = 'none';
    
    try {
        // API 호출
        const requestData = {
            target_business: targetBusiness,
            keywords: keywords,
            location: {
                type: 'coords',
                lat: latitude,
                lng: longitude
            },
            max_pages: 3
        };
        
        const response = await fetch(`${API_BASE_URL}/api/check-ranking`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const results = await response.json();
            displayRankingResults(results);
        } else {
            // 데모 모드 - 샘플 데이터 사용
            await simulateRankingCheck(keywords, targetBusiness);
        }
    } catch (error) {
        console.error('순위 확인 오류:', error);
        // 데모 모드 - 샘플 데이터 사용
        await simulateRankingCheck(keywords, targetBusiness);
    }
}

// 순위 확인 시뮬레이션
async function simulateRankingCheck(keywords, targetBusiness) {
    const progressFill = document.getElementById('rankingProgressFill');
    const progressText = document.getElementById('rankingProgressText');
    
    const results = [];
    
    for (let i = 0; i < keywords.length; i++) {
        const keyword = keywords[i];
        const progress = ((i + 1) / keywords.length) * 100;
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `"${keyword}" 검색 중... (${i + 1}/${keywords.length})`;
        
        // 시뮬레이션 지연
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 모의 순위 생성
        let rank;
        if (keyword.includes('벌원') && targetBusiness.includes('벌원')) {
            rank = 1; // 지역명이 일치하면 1위
        } else if (targetBusiness.toLowerCase().includes(keyword.toLowerCase())) {
            rank = Math.floor(Math.random() * 5) + 1; // 1-5위
        } else {
            rank = Math.random() < 0.7 ? Math.floor(Math.random() * 20) + 1 : null; // 1-20위 또는 찾을 수 없음
        }
        
        results.push({
            keyword: keyword,
            target_business: targetBusiness,
            found: rank !== null,
            rank: rank,
            total_results: rank ? rank + Math.floor(Math.random() * 30) : 0,
            pages_checked: rank ? Math.ceil(rank / 10) : 3,
            processing_time: 1.5
        });
    }
    
    progressText.textContent = '순위 확인 완료!';
    displayRankingResults(results);
}

// 순위 결과 표시
function displayRankingResults(results) {
    rankingData = results;
    
    const rankingList = document.getElementById('rankingList');
    rankingList.innerHTML = '';
    
    results.forEach((result, index) => {
        let rankClass, rankText;
        
        if (result.rank === 1) {
            rankClass = 'rank-1';
            rankText = '🥇 1위';
        } else if (result.rank && result.rank <= 10) {
            rankClass = 'rank-top10';
            rankText = `🏅 ${result.rank}위`;
        } else if (result.rank) {
            rankClass = 'rank-other';
            rankText = `📍 ${result.rank}위`;
        } else {
            rankClass = 'rank-not-found';
            rankText = '❌ 찾을 수 없음';
        }
        
        const rankingItem = document.createElement('div');
        rankingItem.className = 'ranking-item';
        rankingItem.innerHTML = `
            <div class="ranking-keyword">"${result.keyword}"</div>
            <div class="ranking-position ${rankClass}">${rankText}</div>
        `;
        
        // 애니메이션 효과
        rankingItem.style.opacity = '0';
        rankingItem.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            rankingItem.style.transition = 'all 0.5s ease-out';
            rankingItem.style.opacity = '1';
            rankingItem.style.transform = 'translateY(0)';
        }, index * 200);
        
        rankingList.appendChild(rankingItem);
    });
    
    // 진행 상황 숨기고 결과 표시
    setTimeout(() => {
        document.getElementById('rankingProgress').style.display = 'none';
        document.getElementById('rankingResults').style.display = 'block';
    }, results.length * 200 + 500);
}

// 통합 리포트 업데이트
function updateIntegratedReport() {
    const reportContent = document.getElementById('integratedReportContent');
    
    if (!placeAnalysisData && !rankingData) {
        reportContent.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #718096;">
                <h3>📊 분석을 완료해주세요</h3>
                <p>플레이스 분석과 순위 확인을 먼저 진행하시면<br>종합적인 분석 리포트를 제공해드립니다.</p>
            </div>
        `;
        return;
    }
    
    let reportHtml = '<div class="analysis-grid">';
    
    // 플레이스 분석 요약
    if (placeAnalysisData) {
        const score = placeAnalysisData.analysis.completeness_score;
        const grade = score >= 80 ? '우수' : score >= 60 ? '보통' : '개선 필요';
        
        reportHtml += `
            <div class="analysis-card">
                <h3>📊 플레이스 분석 요약</h3>
                <div class="score-display">
                    <div class="score-number">${score}</div>
                    <div class="score-label">플레이스 점수</div>
                </div>
                <p><strong>업체:</strong> ${placeAnalysisData.basic_info.name}</p>
                <p><strong>등급:</strong> ${grade}</p>
                <p><strong>주요 개선점:</strong> ${placeAnalysisData.analysis.missing_elements.slice(0, 2).join(', ')}</p>
            </div>
        `;
    }
    
    // 순위 확인 요약
    if (rankingData) {
        const firstPlaceCount = rankingData.filter(r => r.rank === 1).length;
        const topTenCount = rankingData.filter(r => r.rank && r.rank <= 10).length;
        const foundCount = rankingData.filter(r => r.found).length;
        
        reportHtml += `
            <div class="analysis-card">
                <h3>🏆 순위 확인 요약</h3>
                <div class="info-item">
                    <span class="info-label">총 키워드</span>
                    <span class="info-value">${rankingData.length}개</span>
                </div>
                <div class="info-item">
                    <span class="info-label">1위 달성</span>
                    <span class="info-value">${firstPlaceCount}개</span>
                </div>
                <div class="info-item">
                    <span class="info-label">TOP 10</span>
                    <span class="info-value">${topTenCount}개</span>
                </div>
                <div class="info-item">
                    <span class="info-label">검색됨</span>
                    <span class="info-value">${foundCount}개</span>
                </div>
            </div>
        `;
    }
    
    reportHtml += '</div>';
    
    // 종합 개선 제안
    if (placeAnalysisData && rankingData) {
        const lowRankingKeywords = rankingData.filter(r => !r.rank || r.rank > 10);
        
        reportHtml += `
            <div class="recommendations">
                <h3>🎯 종합 개선 전략</h3>
                
                <div class="recommendation-item priority-high">
                    <strong>플레이스 최적화 우선순위</strong><br>
                    현재 플레이스 점수 ${placeAnalysisData.analysis.completeness_score}점으로 ${placeAnalysisData.analysis.completeness_score < 80 ? '개선이 필요합니다' : '우수한 상태입니다'}. 
                    ${placeAnalysisData.analysis.recommendations[0]?.description || '브랜드 키워드 추가를 권장합니다.'}
                </div>
                
                <div class="recommendation-item priority-medium">
                    <strong>순위 개선 전략</strong><br>
                    ${lowRankingKeywords.length}개 키워드에서 순위가 낮거나 검색되지 않습니다. 
                    플레이스 정보 보강과 함께 해당 키워드들을 플레이스 설명에 자연스럽게 포함시키세요.
                </div>
                
                <div class="recommendation-item priority-medium">
                    <strong>지속적 관리 방안</strong><br>
                    주기적인 플레이스 정보 업데이트와 리뷰 관리를 통해 검색 순위를 유지하세요. 
                    월 1회 순위 점검과 분기별 플레이스 콘텐츠 업데이트를 권장합니다.
                </div>
            </div>
        `;
    }
    
    reportContent.innerHTML = reportHtml;
}

// 결과 내보내기
function exportResults() {
    if (!placeAnalysisData && !rankingData) {
        alert('내보낼 데이터가 없습니다. 분석을 먼저 진행해주세요.');
        return;
    }
    
    const exportData = {
        timestamp: new Date().toISOString(),
        place_analysis: placeAnalysisData,
        ranking_check: rankingData,
        summary: {
            place_score: placeAnalysisData?.analysis.completeness_score,
            ranking_summary: rankingData ? {
                total_keywords: rankingData.length,
                first_place_count: rankingData.filter(r => r.rank === 1).length,
                top_ten_count: rankingData.filter(r => r.rank && r.rank <= 10).length,
                found_count: rankingData.filter(r => r.found).length
            } : null
        }
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `naver_analysis_report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 페이지 하단에 내보내기 버튼 추가 (전역 버튼)
document.addEventListener('DOMContentLoaded', function() {
    const exportButton = document.createElement('div');
    exportButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-weight: 600;
        z-index: 1000;
        transition: transform 0.2s;
    `;
    exportButton.innerHTML = '📊 결과 내보내기';
    exportButton.onclick = exportResults;
    
    exportButton.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });
    
    exportButton.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
    
    document.body.appendChild(exportButton);
});