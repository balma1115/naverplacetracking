# main.py - 완전한 통합 백엔드 서버
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import uuid
from datetime import datetime
import logging
import os
import re
import urllib.parse
import random

# 플레이스 스크래핑 관련 import
from playwright.async_api import async_playwright, TimeoutError

app = FastAPI(
    title="네이버 지도 통합 분석 API",
    description="플레이스 정보 분석 + 순위 확인 통합 서비스",
    version="3.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 진행 중인 작업 저장소
active_jobs: Dict[str, Dict[str, Any]] = {}

# ============ Request Models ============
class LocationSettings(BaseModel):
    type: str = Field(..., regex="^(coords|address|url)$")
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    name: Optional[str] = None
    address: Optional[str] = None
    url: Optional[str] = None

class PlaceAnalysisRequest(BaseModel):
    url: str = Field(..., description="네이버 플레이스 URL")

class RankingRequest(BaseModel):
    target_business: str = Field(..., min_length=1, max_length=100)
    keywords: List[str] = Field(..., min_items=1, max_items=20)
    location: LocationSettings
    max_pages: int = Field(3, ge=1, le=5)
    max_concurrent: Optional[int] = Field(3, ge=1, le=5)

class IntegratedAnalysisRequest(BaseModel):
    place_url: str = Field(..., description="네이버 플레이스 URL")
    target_business: str = Field(..., min_length=1, max_length=100)
    keywords: List[str] = Field(..., min_items=1, max_items=20)
    location: LocationSettings
    max_pages: int = Field(3, ge=1, le=5)

# ============ Response Models ============
class BasicInfo(BaseModel):
    name: str
    category: str
    address: str
    phone: str
    hours: str
    rating: float
    review_count: int

class PlaceDetails(BaseModel):
    description: str
    facilities: List[str]
    programs: List[str]
    pricing: str
    images: List[str]
    coupons: List[str]
    keywords: List[str]

class PlaceAnalysis(BaseModel):
    completeness_score: int
    missing_elements: List[str]
    strengths: List[str]
    recommendations: List[Dict[str, str]]

class PlaceAnalysisResult(BaseModel):
    basic_info: BasicInfo
    details: PlaceDetails
    analysis: PlaceAnalysis

class RankingResult(BaseModel):
    keyword: str
    target_business: str
    found: bool
    rank: Optional[int]
    total_results: int
    pages_checked: int
    processing_time: float
    error: Optional[str] = None

# ============ API Endpoints ============
@app.get("/")
async def root():
    return {
        "message": "네이버 지도 통합 분석 API v3.0",
        "status": "running",
        "features": ["플레이스 분석", "순위 확인", "통합 리포트", "병렬 처리"],
        "endpoints": {
            "place_analysis": "/api/analyze-place",
            "ranking_check": "/api/check-ranking", 
            "integrated_analysis": "/api/integrated-analysis",
            "health_check": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_jobs": len(active_jobs),
        "message": "통합 API 서버가 정상적으로 실행 중입니다",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze-place", response_model=PlaceAnalysisResult)
async def analyze_place(request: PlaceAnalysisRequest):
    """
    네이버 플레이스 정보 분석
    실제로는 Playwright로 스크래핑, 데모에서는 샘플 데이터 반환
    """
    try:
        logger.info(f"플레이스 분석 요청: {request.url}")
        
        # URL에서 업체명 추출 시도
        business_name = extract_business_name_from_url(request.url)
        if not business_name:
            business_name = "분석 대상 업체"
        
        # 실제로는 scrape_naver_place_info 함수 호출
        # place_data = await scrape_naver_place_info(request.url)
        
        # 데모용 샘플 데이터 생성
        place_data = generate_sample_place_analysis(business_name)
        
        logger.info(f"플레이스 분석 완료: {business_name}")
        return place_data
        
    except Exception as e:
        logger.error(f"플레이스 분석 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"플레이스 분석 실패: {str(e)}")

@app.post("/api/check-ranking", response_model=List[RankingResult])
async def check_ranking(request: RankingRequest):
    """순위 확인 API (동기식)"""
    try:
        logger.info(f"순위 확인 요청: {len(request.keywords)}개 키워드")
        
        # 실제로는 병렬 스크래핑 수행
        # results = await search_multiple_keywords_parallel(...)
        
        # 데모용 결과 생성
        results = []
        for keyword in request.keywords:
            await asyncio.sleep(0.5)  # 시뮬레이션 지연
            
            # 모의 순위 생성
            rank = generate_mock_rank(keyword, request.target_business)
            
            result = RankingResult(
                keyword=keyword,
                target_business=request.target_business,
                found=rank is not None,
                rank=rank,
                total_results=rank * 10 if rank else 0,
                pages_checked=min(3, (rank // 10) + 1) if rank else 3,
                processing_time=0.5
            )
            results.append(result)
        
        logger.info(f"순위 확인 완료: {len(results)}개 결과")
        return results
        
    except Exception as e:
        logger.error(f"순위 확인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-ranking-parallel")
async def start_parallel_ranking_check(
    request: RankingRequest,
    background_tasks: BackgroundTasks
):
    """병렬 순위 확인 작업 시작 (비동기)"""
    
    try:
        # 작업 ID 생성
        job_id = str(uuid.uuid4())
        
        # 작업 상태 초기화
        active_jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0.0,
            "total_keywords": len(request.keywords),
            "completed_keywords": 0,
            "started_at": datetime.now(),
            "results": []
        }
        
        # 백그라운드 실행
        background_tasks.add_task(execute_parallel_ranking, job_id, request)
        
        return {
            "job_id": job_id,
            "status": "started",
            "total_keywords": len(request.keywords),
            "message": f"{len(request.keywords)}개 키워드 병렬 검색이 시작되었습니다"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 시작 실패: {str(e)}")

@app.post("/api/integrated-analysis")
async def start_integrated_analysis(
    request: IntegratedAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """통합 분석 시작 (플레이스 분석 + 순위 확인)"""
    
    # 작업 ID 생성
    job_id = str(uuid.uuid4())
    
    # 작업 상태 초기화
    active_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0.0,
        "steps": {
            "place_analysis": "pending",
            "ranking_check": "pending"
        },
        "started_at": datetime.now(),
        "results": {
            "place_analysis": None,
            "ranking_results": None
        }
    }
    
    # 백그라운드 실행
    background_tasks.add_task(execute_integrated_analysis, job_id, request)
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "통합 분석이 시작되었습니다",
        "estimated_time": "2-3분"
    }

@app.get("/api/job-status/{job_id}")
async def get_job_status(job_id: str):
    """작업 진행 상황 확인"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    return active_jobs[job_id]

@app.get("/api/integrated-status/{job_id}")
async def get_integrated_status(job_id: str):
    """통합 분석 진행 상황 확인"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    return active_jobs[job_id]

@app.get("/api/integrated-results/{job_id}")
async def get_integrated_results(job_id: str):
    """통합 분석 결과 가져오기"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    job_data = active_jobs[job_id]
    
    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"분석이 아직 완료되지 않았습니다. 현재 상태: {job_data['status']}"
        )
    
    return {
        "job_id": job_id,
        "place_analysis": job_data["results"]["place_analysis"],
        "ranking_results": job_data["results"]["ranking_results"],
        "summary": generate_integrated_summary(job_data["results"]),
        "completed_at": job_data.get("completed_at")
    }

@app.delete("/api/job/{job_id}")
async def cancel_or_delete_job(job_id: str):
    """작업 취소 또는 삭제"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    job_status = active_jobs[job_id]["status"]
    
    if job_status in ["pending", "running"]:
        active_jobs[job_id]["status"] = "cancelled"
        return {"message": "작업이 취소되었습니다"}
    else:
        del active_jobs[job_id]
        return {"message": "작업이 삭제되었습니다"}

@app.get("/api/active-jobs")
async def get_active_jobs():
    """현재 활성 작업 목록"""
    jobs_summary = []
    for job_id, job_data in active_jobs.items():
        jobs_summary.append({
            "job_id": job_id,
            "status": job_data["status"],
            "progress": job_data.get("progress", 0),
            "started_at": job_data["started_at"],
            "type": "integrated" if "steps" in job_data else "ranking"
        })
    
    return {
        "active_jobs_count": len(active_jobs),
        "jobs": jobs_summary
    }

# ============ Background Tasks ============
async def execute_parallel_ranking(job_id: str, request: RankingRequest):
    """병렬 순위 확인 실행"""
    try:
        active_jobs[job_id]["status"] = "running"
        
        results = []
        for i, keyword in enumerate(request.keywords):
            # 진행률 업데이트
            progress = (i / len(request.keywords)) * 100
            active_jobs[job_id]["progress"] = progress
            active_jobs[job_id]["completed_keywords"] = i
            
            # 시뮬레이션 지연
            await asyncio.sleep(2)
            
            # 모의 결과 생성
            rank = generate_mock_rank(keyword, request.target_business)
            result = {
                "keyword": keyword,
                "target_business": request.target_business,
                "found": rank is not None,
                "rank": rank,
                "total_results": rank * 10 if rank else 0,
                "pages_checked": min(3, (rank // 10) + 1) if rank else 3,
                "processing_time": 2.0
            }
            results.append(result)
        
        # 완료 처리
        active_jobs[job_id].update({
            "status": "completed",
            "progress": 100.0,
            "completed_keywords": len(request.keywords),
            "results": results,
            "completed_at": datetime.now()
        })
        
        logger.info(f"병렬 순위 확인 완료: {job_id}")
        
    except Exception as e:
        active_jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })
        logger.error(f"병렬 순위 확인 실패: {job_id} - {str(e)}")

async def execute_integrated_analysis(job_id: str, request: IntegratedAnalysisRequest):
    """통합 분석 실행"""
    try:
        # 1단계: 플레이스 분석
        active_jobs[job_id]["status"] = "running"
        active_jobs[job_id]["steps"]["place_analysis"] = "running"
        active_jobs[job_id]["progress"] = 25.0
        
        business_name = extract_business_name_from_url(request.place_url)
        place_analysis = generate_sample_place_analysis(business_name or request.target_business)
        
        active_jobs[job_id]["steps"]["place_analysis"] = "completed"
        active_jobs[job_id]["results"]["place_analysis"] = place_analysis.dict()
        active_jobs[job_id]["progress"] = 50.0
        
        await asyncio.sleep(2)  # 시뮬레이션 지연
        
        # 2단계: 순위 확인
        active_jobs[job_id]["steps"]["ranking_check"] = "running"
        active_jobs[job_id]["progress"] = 75.0
        
        ranking_results = []
        for keyword in request.keywords:
            rank = generate_mock_rank(keyword, request.target_business)
            result = {
                "keyword": keyword,
                "target_business": request.target_business,
                "found": rank is not None,
                "rank": rank,
                "total_results": rank * 10 if rank else 0,
                "pages_checked": min(3, (rank // 10) + 1) if rank else 3,
                "processing_time": 1.0
            }
            ranking_results.append(result)
            await asyncio.sleep(0.5)
        
        active_jobs[job_id]["steps"]["ranking_check"] = "completed"
        active_jobs[job_id]["results"]["ranking_results"] = ranking_results
        active_jobs[job_id]["progress"] = 100.0
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["completed_at"] = datetime.now()
        
        logger.info(f"통합 분석 완료: {job_id}")
        
    except Exception as e:
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)
        logger.error(f"통합 분석 실패: {job_id} - {str(e)}")

# ============ Helper Functions ============
def extract_business_name_from_url(url: str) -> Optional[str]:
    """URL에서 업체명 추출"""
    try:
        # search/ 패턴에서 추출
        match = re.search(r'search/([^/]+)', url)
        if match:
            return urllib.parse.unquote(match.group(1))
        
        # place/ 패턴에서 추출
        match = re.search(r'place/([^/]+)', url)
        if match:
            return urllib.parse.unquote(match.group(1))
            
    except Exception as e:
        logger.error(f"URL 파싱 오류: {e}")
    
    return None

def generate_mock_rank(keyword: str, target_business: str) -> Optional[int]:
    """모의 순위 생성"""
    keyword_lower = keyword.lower()
    business_lower = target_business.lower()
    
    # 키워드와 업체명의 연관성에 따라 순위 결정
    if any(word in keyword_lower for word in business_lower.split()):
        # 연관성이 높으면 상위 순위
        return random.randint(1, 5)
    elif any(word in business_lower for word in keyword_lower.split()):
        # 중간 연관성
        return random.randint(3, 15)
    else:
        # 낮은 연관성
        return random.randint(10, 50) if random.random() > 0.3 else None

def generate_sample_place_analysis(business_name: str) -> PlaceAnalysisResult:
    """샘플 플레이스 분석 데이터 생성"""
    
    # 업체명에 따른 동적 데이터 생성
    is_academy = any(word in business_name for word in ['학원', '아카데미', '스쿨'])
    is_english = any(word in business_name for word in ['영어', 'English', '미래엔'])
    
    if is_academy and is_english:
        category = "영어학원"
        programs = ["초등영어", "중등영어", "파닉스", "회화"]
        keywords = ["영어학원", "초등영어", "중등영어"]
        pricing = "월 12만원~18만원 (과정별 상이)"
        coupons = ["무료 체험 수업", "형제 할인 10%"]
        facilities = ["주차장", "상담실", "독서실", "대기실"]
        description = f"{business_name}는 미래엔 교재를 사용하는 체계적인 영어교육 전문학원입니다."
    else:
        category = "교육업"
        programs = ["기본과정", "심화과정", "특별과정"]
        keywords = ["학원", "교육", "수업"]
        pricing = "월 10만원~15만원"
        coupons = ["체험 수업", "신규 할인"]
        facilities = ["주차장", "상담실", "대기실"]
        description = f"{business_name}는 전문적인 교육 서비스를 제공합니다."
    
    # 점수 계산
    base_score = 70
    if "미래엔" in business_name:
        base_score += 10
    if len(programs) > 3:
        base_score += 5
    if len(facilities) > 3:
        base_score += 5
    
    completeness_score = min(base_score, 100)
    
    # 누락 요소 계산
    missing_elements = []
    if completeness_score < 80:
        missing_elements.extend(["상세 프로그램 설명", "교사 소개"])
    if "미래엔" not in keywords and "미래엔" in business_name:
        missing_elements.append("브랜드 키워드")
    
    # 추천사항 생성
    recommendations = []
    if "미래엔" not in keywords and "미래엔" in business_name:
        recommendations.append({
            "priority": "high",
            "title": "브랜드 키워드 추가",
            "description": "'미래엔영어', '미래엔 교재' 등 브랜드 연관 키워드를 추가하세요."
        })
    
    if completeness_score < 75:
        recommendations.append({
            "priority": "medium",
            "title": "프로그램 상세 설명",
            "description": "각 과정별 특징과 교육 방식을 구체적으로 설명하세요."
        })
    
    recommendations.append({
        "priority": "medium",
        "title": "이미지 콘텐츠 보강",
        "description": "학원 시설, 수업 모습, 교재 등의 사진을 추가하세요."
    })
    
    return PlaceAnalysisResult(
        basic_info=BasicInfo(
            name=business_name,
            category=category,
            address="광주광역시 서구 벌원동 123-45",
            phone="062-123-4567",
            hours="월~금 14:00-22:00, 토 09:00-18:00",
            rating=4.2,
            review_count=28
        ),
        details=PlaceDetails(
            description=description,
            facilities=facilities,
            programs=programs,
            pricing=pricing,
            images=["외관", "교실", "상담실", "교재", "수업모습"],
            coupons=coupons,
            keywords=keywords
        ),
        analysis=PlaceAnalysis(
            completeness_score=completeness_score,
            missing_elements=missing_elements,
            strengths=["기본 정보 완성", "프로그램 다양성", "할인 혜택"],
            recommendations=recommendations
        )
    )

def generate_integrated_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """통합 분석 요약 생성"""
    summary = {}
    
    # 플레이스 분석 요약
    if results.get("place_analysis"):
        place_data = results["place_analysis"]
        summary["place_summary"] = {
            "score": place_data["analysis"]["completeness_score"],
            "grade": "우수" if place_data["analysis"]["completeness_score"] >= 80 else 
                    "보통" if place_data["analysis"]["completeness_score"] >= 60 else "개선 필요",
            "business_name": place_data["basic_info"]["name"],
            "category": place_data["basic_info"]["category"],
            "top_recommendations": place_data["analysis"]["recommendations"][:2]
        }
    
    # 순위 확인 요약
    if results.get("ranking_results"):
        ranking_data = results["ranking_results"]
        first_place_count = sum(1 for r in ranking_data if r.get("rank") == 1)
        top_ten_count = sum(1 for r in ranking_data if r.get("rank") and r["rank"] <= 10)
        found_count = sum(1 for r in ranking_data if r.get("found"))
        
        summary["ranking_summary"] = {
            "total_keywords": len(ranking_data),
            "first_place_count": first_place_count,
            "top_ten_count": top_ten_count,
            "found_count": found_count,
            "success_rate": round((found_count / len(ranking_data)) * 100, 1),
            "top_performing_keywords": [
                r["keyword"] for r in ranking_data 
                if r.get("rank") and r["rank"] <= 3
            ][:3]
        }
    
    return summary

# ============ 실제 스크래핑 함수들 (향후 구현용) ============
async def scrape_naver_place_info(url: str) -> Dict[str, Any]:
    """
    실제 네이버 플레이스 정보 스크래핑
    기존 scrape_naver_place 함수를 API용으로 수정
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="load", timeout=90000)
            
            # iframe 방식과 직접 접근 방식 모두 지원
            try:
                # iframe 방식 시도
                entry_iframe = await page.wait_for_selector("#entryIframe", timeout=10000)
                frame = await entry_iframe.content_frame()
                await frame.wait_for_selector("#_title", timeout=20000)
                
                # 기본 정보 추출
                place_name = await get_text_or_default(frame, "#_title > div > span.GHAhO")
                category = await get_text_or_default(frame, "#_title > div > span.lnJFt")
                
            except TimeoutError:
                # 직접 접근 방식 시도
                frame = page
                place_name = await get_text_or_default(frame, "h1", "업체명 정보 없음")
                category = await get_text_or_default(frame, ".category", "업종 정보 없음")
            
            # 기본 정보 수집
            main_content_selector = "#app-root > div > div > div:nth-child(6)"
            
            address = await get_text_or_default(frame, f"{main_content_selector} .LDgIH")
            phone = await get_text_or_default(frame, f"{main_content_selector} .xlx7Q")
            
            # 편의시설 정보
            facilities = await get_facilities(frame, f"{main_content_selector} .Uv6Eo")
            
            # 가격 정보
            pricing = await get_list_items_as_text(frame, f"{main_content_selector} .tXI2c li")
            
            return {
                "basic_info": {
                    "name": place_name,
                    "category": category,
                    "address": address,
                    "phone": phone,
                    "rating": 4.0,  # 실제로는 스크래핑
                    "review_count": 0  # 실제로는 스크래핑
                },
                "details": {
                    "description": "스크래핑된 설명",
                    "facilities": facilities.split(", ") if facilities != "정보 없음" else [],
                    "pricing": pricing
                }
            }
            
        except Exception as e:
            logger.error(f"플레이스 스크래핑 오류: {e}")
            raise
        finally:
            await browser.close()

async def get_text_or_default(frame, selector, default="정보 없음"):
    """텍스트 안전 추출"""
    try:
        await frame.wait_for_selector(selector, state='attached', timeout=2000)
        return await frame.locator(selector).first.inner_text(timeout=1000)
    except TimeoutError:
        return default

async def get_facilities(frame, container_selector, default="정보 없음"):
    """편의시설 정보 추출"""
    try:
        await frame.wait_for_selector(container_selector, state='visible', timeout=3000)
        items = await frame.locator(f"{container_selector} span").all()
        if not items: 
            return default
        texts = await asyncio.gather(*(item.inner_text() for item in items))
        return ", ".join(filter(None, texts))
    except TimeoutError:
        return default

async def get_list_items_as_text(frame, list_selector, default="정보 없음"):
    """리스트 아이템들을 텍스트로 변환"""
    try:
        await frame.wait_for_selector(list_selector, state='attached', timeout=3000)
        items = await frame.locator(list_selector).all()
        if not items: 
            return default
        texts = await asyncio.gather(*(item.inner_text() for item in items))
        return "\n".join(texts)
    except TimeoutError:
        return default

# ============ 서버 실행 ============
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)