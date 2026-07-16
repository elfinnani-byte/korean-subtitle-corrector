-- Supabase 대시보드의 "SQL Editor"에서 한 번 실행하세요.
-- 이 테이블에는 서버(FastAPI)가 service_role 키로만 접근합니다.
-- service_role 키는 RLS를 무시하므로, 아래처럼 RLS를 켜고 정책을 하나도 만들지 않으면
-- 브라우저(anon 키)는 어떤 요청을 보내도 전부 거부되고, 오직 이 서버만 접근할 수 있습니다.

create table if not exists reports (
  id uuid primary key,
  created_at timestamptz not null default now(),
  original_srt text not null,
  corrected_srt text not null,
  flags jsonb not null default '[]',
  applied_log jsonb not null default '[]'
);

alter table reports enable row level security;
-- 정책을 만들지 않음 = anon/authenticated 역할은 아무것도 못 함 (기본값이 전부 거부).
-- service_role만 우회 접근 가능 — 우리 서버가 쓰는 키가 바로 이것.
