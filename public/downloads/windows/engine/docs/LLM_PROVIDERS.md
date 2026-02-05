# LLM Providers (Gemini default, OpenAI optional)

선택
- `LLM_PROVIDER=gemini` (default)
- `LLM_PROVIDER=openai`

Gemini
- 패키지: google-genai
- 호출: `from google import genai`, `genai.Client().models.generate_content(...)`
- 키: GEMINI_API_KEY

OpenAI (옵션)
- 패키지: openai
- 호출: `from openai import OpenAI`, `client.responses.create(...)`
- 키: OPENAI_API_KEY

Fail-safe (개발 기본값)
- 키 미설정 시 LLM_DISABLED로 degrade
- 운영에서는 키 필수로 강제하는 옵션(예: LLM_REQUIRED=true) 추가를 권장
