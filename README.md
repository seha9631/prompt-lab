# Prompt Lab API

DDD(Domain-Driven Design) 구조로 구성된 사용자 및 팀 관리 API

## 🚀 빠른 시작

### 개발 환경

#### 1. 데이터베이스 실행

##### 옵션 1: 전체 환경 (데이터 영속성 유지)

```bash
# API 서버와 DB를 함께 실행 (데이터 영속성 유지)
docker-compose up -d
```

또는 자동 배포 스크립트 사용:

```bash
./deploy-full.sh
```

##### 옵션 2: 개발용 (DB 매번 초기화)

```bash
# 개발 중에는 DB만 배포 (매번 초기화)
docker-compose -f docker-compose.dev.yml up -d
```

또는 자동 배포 스크립트 사용:

```bash
./deploy-dev.sh
```

#### 2. API 서버 실행

```bash
cd backend
python main.py
```

또는

```bash
cd backend
uvicorn main:app --reload
```

### 프로덕션 배포

#### 1. 자동 배포 (권장)

```bash
# 배포 스크립트 실행
./deploy.sh
```

#### 2. 수동 배포

```bash
# 환경변수 설정 (선택사항)
export JWT_SECRET_KEY="your-secure-secret-key"

# Docker Compose로 배포
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 3. 배포 확인

```bash
# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f api

# 헬스체크
curl http://localhost:8000/
```

## 📊 데이터베이스 초기화

### 자동 초기화

- Docker 컨테이너 시작 시 `init.sql` 스크립트가 자동으로 실행됩니다
- 기존 테이블과 데이터를 완전히 삭제하고 새로 생성합니다

### 수동 초기화

```bash
# 컨테이너 재시작으로 초기화
docker-compose down
docker-compose up -d

# 또는 개발용
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

## 🏗️ 프로젝트 구조

```
prompt-lab/
├── backend/
│   ├── src/
│   │   ├── auth/                    # 인증 도메인
│   │   │   ├── application/         # 애플리케이션 레이어
│   │   │   ├── domain/             # 도메인 레이어
│   │   │   ├── infra/              # 인프라 레이어
│   │   │   └── presentation/       # 프레젠테이션 레이어
│   │   └── shared/                 # 공통 모듈
│   │       ├── exception/          # 예외 처리
│   │       ├── logging/            # 로깅 시스템
│   │       ├── response/           # 공통 응답
│   │       └── web/                # 웹 설정
│   └── main.py
├── backend/
│   ├── Dockerfile                  # API 서버 Docker 이미지
│   ├── .dockerignore               # Docker 빌드 제외 파일
│   └── env.example                 # 환경변수 예시
├── nginx/
│   └── nginx.conf                  # Nginx 리버스 프록시 설정
├── docker-compose.yml              # 기본 설정 (API 서버 + DB, 데이터 영속성)
├── docker-compose.dev.yml          # 개발용 (DB만 배포, 매번 초기화)
├── docker-compose.prod.yml         # 프로덕션용 (전체 서비스)
├── deploy.sh                       # 프로덕션 자동 배포 스크립트
├── deploy-full.sh                  # 전체 환경 자동 배포 스크립트 (API + DB, 데이터 영속성)
├── deploy-dev.sh                   # 개발 DB 자동 배포 스크립트 (매번 초기화)
└── init.sql                        # 데이터베이스 초기화 스크립트
```

## 🔧 API 엔드포인트

### 인증

- `POST /api/v1/login` - 로그인 (JWT 토큰 발급)
- `POST /api/v1/refresh` - 액세스 토큰 갱신

### 사용자 관리

- `POST /api/v1/users` - 새 팀과 함께 사용자 생성
- `POST /api/v1/teams/{team_id}/users` - 기존 팀에 사용자 추가
- `GET /api/v1/users/{app_id}` - 앱 ID로 사용자 조회 (인증 필요)
- `PATCH /api/v1/users/{owner_user_id}/approve` - 사용자 승인 (owner 권한 필요)

### 팀 관리

- `GET /api/v1/teams/{team_id}/users` - 팀의 모든 사용자 조회 (인증 필요)
- `PATCH /api/v1/users/{owner_user_id}/role` - 사용자 권한 변경 (owner 권한 필요)

### 헬스체크

- `GET /` - API 상태 확인

## 🛠️ 기술 스택

- **Framework**: FastAPI
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Email Validation**: Pydantic EmailStr
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Deployment**: Automated deployment script
- **Architecture**: DDD (Domain-Driven Design)
- **Container**: Docker & Docker Compose

## 📝 로그 및 에러 처리

- 구조화된 로깅 시스템
- 계층별 예외 처리
- 일관된 API 응답 형식
- 색상이 있는 콘솔 로그 출력

## 🔄 데이터 초기화 옵션

| 옵션     | 파일                      | 데이터 영속성 | 용도         |
| -------- | ------------------------- | ------------- | ------------ |
| 기본     | `docker-compose.yml`      | ❌            | 테스트, 데모 |
| 개발     | `docker-compose.dev.yml`  | ✅            | 개발 중      |
| 프로덕션 | `docker-compose.prod.yml` | ❌            | 프로덕션     |
