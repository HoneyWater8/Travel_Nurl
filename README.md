# RIA (Recommend Image Area)

이 프로젝트는 FastAPI를 사용하여 구축된 웹 애플리케이션입니다. 이 README 파일은 프로젝트의 설치 방법, 사용법 및 기여 방법에 대한 정보를 제공합니다.

## 목차
- [소개](#소개)
- [기능](#기능)
- [설치 방법](#설치-방법)
- [사용법](#사용법)
- [API 문서](#api-문서)
- [기여하기](#기여하기)
- [라이선스](#라이선스)

## 소개

이 프로젝트는 FastAPI 프레임워크를 사용하여 RESTful API를 구현한 것입니다. FastAPI는 빠르고 효율적인 API 개발을 지원하며, 자동 문서화 기능이 뛰어납니다. 프로젝트의 목적은 관광지 사진을 통하여, 사용자에게 원하는 장소를 추천하고 관광 사업 활성화입니다.

## 기능

- RESTful API 엔드포인트
- 사용자 인증 및 권한 관리
- 데이터베이스 연동 (예: SQLAlchemy, Tortoise ORM)
- 자동화된 API 문서화 (Swagger UI 및 ReDoc)
- 이미지를 통한 장소 추천
- KAKAO 로그인

## 설치 방법

이 프로젝트를 로컬 시스템에 설치하기 위한 단계입니다.

1. **레포지토리 클론하기**
```   
      git clone <레포지토리 URL>
      cd <레포지토리 이름>
``` 
2. **가상 환경 만들기**

`python3 -m venv venv`
3. 가상 환경 활성화하기
- Linux / macOS:
`source venv/bin/activate`
- Windows:
`venv\Scripts\activate`
4. 의존성 설치하기

`pip install -r requirements.txt`
5. 설정 파일 추가하기
- app 파일에 config.yml 파일을 생성합니다.
- 이후 각 팀원을 공유한 파일을 config.yml 파일에 붙여넣기 바랍니다.
`touch app.config.yml`
.env 파일에 다음과 같은 내용을 추가합니다:

## 사용법
1. 서버 실행하기
`uvicorn main:app --reload`
- main: 파일 이름 (확장자는 제외)
- app: FastAPI 인스턴스의 이름
- --reload: 코드 변경 시 자동으로 서버가 재시작되도록 설정

2. 웹 브라우저에서 접근하기
기본적으로 애플리케이션은 http://localhost:8000에서 실행됩니다. 웹 브라우저에서 해당 URL을 입력하여 애플리케이션에 접근하세요.
- Swagger 접근 방법 : http://localhost:8000/docs
