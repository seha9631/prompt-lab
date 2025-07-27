#!/bin/bash

# Prompt Lab API 배포 스크립트

set -e  # 에러 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 확인
check_environment() {
    log_info "환경 확인 중..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되어 있지 않습니다."
        exit 1
    fi
    
    log_success "환경 확인 완료"
}

# 기존 컨테이너 정리
cleanup() {
    log_info "기존 컨테이너 정리 중..."
    
    # 기존 컨테이너 중지 및 삭제
    docker-compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
    
    # 사용하지 않는 이미지 정리
    docker image prune -f
    
    log_success "정리 완료"
}

# 환경변수 설정
setup_environment() {
    log_info "환경변수 설정 중..."
    
    # JWT_SECRET_KEY가 설정되지 않은 경우 경고
    if [ -z "$JWT_SECRET_KEY" ]; then
        log_warning "JWT_SECRET_KEY가 설정되지 않았습니다. 기본값을 사용합니다."
        export JWT_SECRET_KEY="your-secret-key-here-change-in-production"
    fi
    
    log_success "환경변수 설정 완료"
}

# 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    log_success "이미지 빌드 완료"
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "서비스 시작 완료"
}

# 헬스체크
health_check() {
    log_info "헬스체크 중..."
    
    # 최대 60초 대기
    for i in {1..12}; do
        if curl -f http://localhost:8000/ >/dev/null 2>&1; then
            log_success "API 서버가 정상적으로 실행되고 있습니다."
            return 0
        fi
        
        log_info "서버 시작 대기 중... ($i/12)"
        sleep 5
    done
    
    log_error "서버 시작 시간 초과"
    return 1
}

# 로그 확인
show_logs() {
    log_info "서비스 로그 확인 중..."
    
    echo ""
    echo "=== API 서버 로그 ==="
    docker-compose -f docker-compose.prod.yml logs api --tail=20
    
    echo ""
    echo "=== PostgreSQL 로그 ==="
    docker-compose -f docker-compose.prod.yml logs postgres --tail=10
}

# 메인 함수
main() {
    log_info "Prompt Lab API 배포를 시작합니다..."
    
    check_environment
    cleanup
    setup_environment
    build_images
    start_services
    
    if health_check; then
        log_success "배포가 성공적으로 완료되었습니다!"
        log_info "API 서버: http://localhost:8000"
        log_info "API 문서: http://localhost:8000/docs"
        
        show_logs
    else
        log_error "배포 중 오류가 발생했습니다."
        show_logs
        exit 1
    fi
}

# 스크립트 실행
main "$@" 