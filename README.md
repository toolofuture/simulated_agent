# LLM 기반 미술품 검증 시뮬레이터

OpenAI API를 사용한 LLM 기반 가짜 미술품 검증 시뮬레이션 에이전트입니다.

## 기능

- 🤖 LLM 기반 검증 봇과 고객 봇
- 💬 자연스러운 대화 시뮬레이션
- 📊 실시간 진행 상황 및 통계
- 💾 결과 다운로드
- 🌐 Streamlit 웹 인터페이스

## 설치 방법

```bash
pip install -r requirements.txt
```

## 로컬 실행 방법

```bash
streamlit run app.py
```

## Streamlit Cloud 배포 방법

1. **GitHub 리포지토리 연결**
   - [Streamlit Cloud](https://share.streamlit.io/)에 접속
   - GitHub 계정으로 로그인
   - "New app" 클릭
   - Repository: `toolofuture/simulated_agent` 선택
   - Main file path: `app.py`
   - "Deploy!" 클릭

2. **Secrets 설정 (중요!)**
   - 앱이 배포된 후, 우측 상단의 "⚙️" (Settings) 아이콘 클릭
   - 또는 앱 메뉴에서 "Settings" 선택
   - "Secrets" 탭 클릭
   - 아래 형식으로 API Key 입력:
   
   ```toml
   [openai]
   api_key = "sk-your-openai-api-key-here"
   ```
   
   - "Save" 버튼 클릭
   - 앱이 자동으로 재시작됩니다

3. **접속**
   - 배포된 앱 URL로 접속하여 사용

## 사용 방법

1. **API Key 설정**
   - Streamlit Cloud: Settings → Secrets 탭에서 설정
   - 로컬: 설정 탭에서 직접 입력 또는 `.streamlit/secrets.toml` 파일 생성

2. **시뮬레이션 실행**
   - 시뮬레이션 탭에서 대화 횟수 설정 (1-1000)
   - "시뮬레이션 시작" 버튼 클릭
   - 실시간으로 진행 상황 확인
   - 결과 다운로드 가능

## 구조

- `app.py`: Streamlit 웹 인터페이스
- `llm_simulator.py`: LLM 기반 시뮬레이터 로직
- `simulation_results/`: 시뮬레이션 결과 저장 폴더

## 라이선스

MIT

