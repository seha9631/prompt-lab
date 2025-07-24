-- 데이터베이스 생성
CREATE DATABASE prompt_lab;

-- prompt_lab 데이터베이스에 연결하여 확장 및 테이블 생성
\c prompt_lab;

-- pgcrypto 확장 설치
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- team 테이블 생성
CREATE TABLE team (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    payment VARCHAR NOT NULL DEFAULT 'free',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- user 테이블 생성
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    app_id VARCHAR NOT NULL,
    app_password VARCHAR NOT NULL,
    role VARCHAR NOT NULL DEFAULT 'user',
    team_id UUID NOT NULL REFERENCES team(id),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- 인덱스 생성 (성능 최적화를 위해)
CREATE INDEX idx_user_team_id ON "user"(team_id);
CREATE INDEX idx_user_app_id ON "user"(app_id);
CREATE INDEX idx_team_name ON team(name);

-- 기본 팀 데이터 삽입 (옵션)
INSERT INTO team (name, payment) VALUES ('Default Team', 'free');

-- 완료 메시지
\echo 'Database initialization completed successfully!' 