# Google 소셜 로그인 설정 (선택 — 가점 항목)

`.streamlit/secrets.toml`의 `client_id`/`client_secret`을 비워두면 로그인 UI가 자동으로
숨겨지고 앱은 평소대로(비로그인 세션) 동작한다. 로그인을 켜려면 아래 절차로 Google OAuth
클라이언트를 **직접** 발급받아 채워 넣어야 한다 (본인 Google 계정 필요, 무료).

## 1. Google Cloud Console에서 OAuth 클라이언트 발급

1. https://console.cloud.google.com/ 접속 → 프로젝트 새로 만들기 (또는 기존 프로젝트 선택).
2. 좌측 메뉴 **API 및 서비스 → OAuth 동의 화면** → User Type: **외부(External)** 선택 → 앱 이름·이메일 등 최소 정보만 입력하고 저장.
   - "테스트 사용자" 단계에서 본인 Google 계정을 추가해 두면 게시(publish) 없이도 바로 로그인 테스트 가능.
3. **API 및 서비스 → 사용자 인증 정보 → + 사용자 인증 정보 만들기 → OAuth 클라이언트 ID**.
   - 애플리케이션 유형: **웹 애플리케이션**.
   - **승인된 리디렉션 URI**에 정확히 아래 값을 추가:
     ```
     http://localhost:8501/oauth2callback
     ```
     (포트를 바꿔 실행하면 `8501` 부분도 그 포트로 맞춰야 한다.)
4. 생성되면 **클라이언트 ID**와 **클라이언트 보안 비밀**이 발급된다.

## 2. `.streamlit/secrets.toml`에 채우기

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "이미 채워져 있음 — 그대로 둬도 됨"
client_id = "여기에 발급받은 클라이언트 ID"
client_secret = "여기에 발급받은 클라이언트 보안 비밀"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

저장 후 `streamlit run ui.py`를 재시작하면 사이드바에 **"🔐 Google로 로그인"** 버튼이 나타난다.

## 확인

- 로그인하면 사이드바에 이름/이메일이 표시되고, 대화 히스토리가 계정별로 쌓인다 (DB 저장 기능과 연동, `sessions.db`).
- 로그인하지 않아도 앱은 정상 동작한다 — 이 경우 대화는 브라우저 탭(URL의 `?sid=`)에 묶여서 새로고침해도 이어지지만, 계정 간 공유는 되지 않는다.
- `Authlib>=1.3.2`가 필요하다 (`requirements.txt`에 포함됨) — `pip install -r requirements.txt`로 설치.
