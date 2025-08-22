-- ========================================
-- Prompt Lab Seed Data Script
-- ========================================
-- 이 스크립트는 기본 데이터를 삽입합니다.
-- 배포 시 한 번만 실행하면 됩니다.

-- prompt_lab 데이터베이스에 연결
\c prompt_lab;

-- ========================================
-- Source 데이터 삽입
-- ========================================
INSERT INTO source (name) 
VALUES ('OpenAI')
ON CONFLICT (name) DO NOTHING;

-- ========================================
-- Source Model 데이터 삽입 (OpenAI GPT 모델들)
-- ========================================
-- GPT-4 모델들
INSERT INTO source_model (name, description, source_id) 
SELECT 
    'gpt-4o',
    'GPT-4 Omni - 가장 최신의 멀티모달 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'gpt-4o-mini',
    'GPT-4 Omni Mini - 빠르고 효율적인 GPT-4 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'gpt-4-turbo',
    'GPT-4 Turbo - 고성능 GPT-4 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'gpt-4',
    'GPT-4 - 강력한 언어 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

-- GPT-3.5 모델들
INSERT INTO source_model (name, description, source_id) 
SELECT 
    'gpt-3.5-turbo',
    'GPT-3.5 Turbo - 빠르고 효율적인 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'gpt-3.5-turbo-16k',
    'GPT-3.5 Turbo 16K - 긴 컨텍스트 지원',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

-- 기타 모델들
INSERT INTO source_model (name, description, source_id) 
SELECT 
    'dall-e-3',
    'DALL-E 3 - 고품질 이미지 생성 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'dall-e-2',
    'DALL-E 2 - 이미지 생성 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'whisper-1',
    'Whisper - 음성 인식 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'text-embedding-ada-002',
    'Text Embedding Ada 002 - 텍스트 임베딩 모델',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'text-embedding-3-small',
    'Text Embedding 3 Small - 최신 임베딩 모델 (소형)',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

INSERT INTO source_model (name, description, source_id) 
SELECT 
    'text-embedding-3-large',
    'Text Embedding 3 Large - 최신 임베딩 모델 (대형)',
    s.id
FROM source s 
WHERE s.name = 'OpenAI'
ON CONFLICT DO NOTHING;

-- ========================================
-- 완료 메시지
-- ========================================
\echo '========================================'
\echo 'Seed data insertion completed successfully!'
\echo '========================================'
\echo 'Data inserted:'
\echo '  - OpenAI source'
\echo '  - 12 GPT models'
\echo '========================================'
