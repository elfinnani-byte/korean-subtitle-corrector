# 배포 가이드 — Supabase(저장) + Render(백엔드)

이 문서에 있는 계정 생성·클릭 작업은 본인이 직접 해야 합니다 (AI가 대신 로그인/가입할 수 없음).
아래 순서대로 하면 됩니다.

## 1. Supabase — 저장소 만들기

1. https://supabase.com 에서 무료 계정 생성 → "New Project" 로 새 프로젝트 하나 만들기.
2. 프로젝트가 만들어지면, 왼쪽 메뉴 **SQL Editor** 로 들어가서 이 저장소의 `supabase_schema.sql` 파일 내용을 그대로 붙여넣고 실행(Run).
   - 이 SQL은 `reports` 테이블을 만들고, RLS(행 수준 보안)를 켜되 아무 정책도 만들지 않습니다.
   - 즉 브라우저(공개 키)는 이 테이블에 **절대 접근 불가**, 우리 서버(관리자 키)만 접근 가능한 구조입니다.
3. 왼쪽 메뉴 **Project Settings → API** 에서 두 값을 복사해두세요:
   - **Project URL** → `.env`의 `SUPABASE_URL`
   - **service_role** 키 (⚠️ "anon public" 키가 아니라 "service_role" 키!) → `.env`의 `SUPABASE_SERVICE_KEY`
   - service_role 키는 절대 프론트엔드(브라우저) 코드에 넣지 마세요. 이 키를 가진 사람은 RLS를 무시하고 뭐든 할 수 있습니다.

## 2. 로컬에서 먼저 테스트

```powershell
cd C:\Users\user\Documents\korean-subtitle-corrector
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # 이미 .env가 있다면 SUPABASE_* 두 줄만 추가
# .env 파일을 열어서 SUPABASE_URL / SUPABASE_SERVICE_KEY 채우기
.venv\Scripts\uvicorn subtitle_corrector.api:app --reload
```

브라우저에서 `http://127.0.0.1:8000` 열고 `examples/sample.srt` 파일을 업로드해보세요.
교정이 끝나면 주소가 `?id=...`로 바뀝니다 — 그 상태에서 새로고침(F5)해도 결과가 그대로 남아있으면 성공입니다.

## 3. GitHub에 푸시

Render는 GitHub 저장소를 연결해서 배포합니다. `git push`로 이 저장소를 GitHub에 올려두세요.
(`.env`는 `.gitignore`에 있어서 실수로 올라가지 않습니다 — 비밀키는 3단계에서 Render 대시보드에 직접 입력합니다.)

## 4. Render — 백엔드 올리기

1. https://render.com 무료 계정 생성 → **New → Web Service** → 방금 올린 GitHub 저장소 선택.
2. 설정값:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn subtitle_corrector.api:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
3. **Environment** 탭에서 아래 5개 환경변수를 각각 추가 (Key/Value 입력, `.env` 파일은 여기 올라가지 않으므로 직접 입력):
   - `STDICT_API_KEY`
   - `OPENDICT_API_KEY`
   - `KORNORMS_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
4. **Create Web Service** → 몇 분 기다리면 `https://<서비스이름>.onrender.com` 주소가 생깁니다.

## 확인할 것 (제출 전 보안 체크와 동일)

- [ ] 비밀값(API 키)이 코드에 직접 적혀있지 않고 환경변수로만 존재하는가 — `subtitle_corrector/dictionary.py`, `subtitle_corrector/store.py` 확인
- [ ] `SUPABASE_SERVICE_KEY`가 브라우저로 내려가는 응답(`static/index.html`, `/api/*` 응답)에 절대 포함되지 않는가
- [ ] RLS가 켜져 있고, anon 키로는 `reports` 테이블에 아무 요청도 성공하지 않는가 (Supabase 대시보드 Table Editor에서 anon 키로 직접 확인 가능)
- [ ] 무료 티어 한도: Render 무료 웹서비스는 15분 정도 요청이 없으면 잠들고, 첫 요청이 다시 뜨는 데 ~1분 걸림. Supabase 무료 프로젝트는 7일 이상 미사용 시 일시정지될 수 있음 — 시연 전에 한 번 접속해서 깨워두는 것을 추천.
