-- ========================================
-- Prompt Lab Database Initialization Script
-- ========================================
-- 이 스크립트는 Docker 컨테이너 시작 시 실행됩니다.
-- 기존 데이터를 완전히 삭제하고 새로운 데이터베이스를 초기화합니다.

-- 기존 데이터 완전 삭제 (테이블이 존재하는 경우)
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS team CASCADE;
DROP TABLE IF EXISTS source_model CASCADE;
DROP TABLE IF EXISTS source CASCADE;
DROP TABLE IF EXISTS credential CASCADE;

-- pgcrypto 확장 설치 (UUID 생성용)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ========================================
-- 테이블 생성
-- ========================================

-- team 테이블 생성
CREATE TABLE team (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    payment VARCHAR(20) NOT NULL DEFAULT 'free',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- user 테이블 생성
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    app_id VARCHAR(50) NOT NULL UNIQUE,
    app_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    team_id UUID NOT NULL REFERENCES team(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- source 테이블 생성
CREATE TABLE source (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- source_model 테이블 생성
CREATE TABLE source_model (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    source_id UUID NOT NULL REFERENCES source(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- credential 테이블 생성
CREATE TABLE credential (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES team(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    source_id UUID NOT NULL REFERENCES source(id) ON DELETE CASCADE,
    api_key TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- llm_request 테이블 생성
CREATE TABLE llm_request (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES team(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    file_paths TEXT[] NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    result TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- ========================================
-- 인덱스 생성 (성능 최적화)
-- ========================================
CREATE INDEX idx_user_team_id ON "user"(team_id);
CREATE INDEX idx_user_app_id ON "user"(app_id);
CREATE INDEX idx_team_name ON team(name);
CREATE INDEX idx_user_created_at ON "user"(created_at);
CREATE INDEX idx_team_created_at ON team(created_at);
CREATE INDEX idx_source_model_source_id ON source_model(source_id);
CREATE INDEX idx_source_name ON source(name);
CREATE INDEX idx_credential_team_id ON credential(team_id);
CREATE INDEX idx_credential_source_id ON credential(source_id);
CREATE INDEX idx_credential_name ON credential(name);
CREATE INDEX idx_llm_request_team_id ON llm_request(team_id);
CREATE INDEX idx_llm_request_user_id ON llm_request(user_id);
CREATE INDEX idx_llm_request_status ON llm_request(status);
CREATE INDEX idx_llm_request_created_at ON llm_request(created_at);

-- ========================================
-- 제약 조건 추가
-- ========================================
-- app_id는 고유해야 함
ALTER TABLE "user" ADD CONSTRAINT uk_user_app_id UNIQUE (app_id);

-- 팀 이름은 고유해야 함
ALTER TABLE team ADD CONSTRAINT uk_team_name UNIQUE (name);

-- source 이름은 고유해야 함
ALTER TABLE source ADD CONSTRAINT uk_source_name UNIQUE (name);

-- 팀 내에서 credential 이름은 고유해야 함
ALTER TABLE credential ADD CONSTRAINT uk_credential_team_name UNIQUE (team_id, name);

-- ========================================
-- 기본 데이터 삽입 (옵션)
-- ========================================
-- 기본 팀 생성
INSERT INTO team (name, payment) 
VALUES ('Default Team', 'free')
ON CONFLICT (name) DO NOTHING;

-- ========================================
-- 완료 메시지
-- ========================================
\echo '========================================'
\echo 'Database initialization completed successfully!'
\echo '========================================'
\echo 'Tables created:'
\echo '  - team'
\echo '  - user'
\echo '  - source'
\echo '  - source_model'
\echo '  - credential'
\echo '  - llm_request'
\echo '========================================' 