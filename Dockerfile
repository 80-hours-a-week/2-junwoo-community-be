# AWS Lambda Python 3.12 전용 베이스 이미지 사용
FROM public.ecr.aws/lambda/python:3.12

# 컨테이너 내 작업 디렉토리 설정 (Lambda 기본 경로인 /var/task 사용)
WORKDIR /var/task

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사 (community_api 폴더 안의 app 폴더 전체를 /var/task/app 경로로 복사)
# 이렇게 해야 app.main:handler 모듈을 람다가 찾을 수 있습니다.
COPY community_api/app ./app

# Lambda 실행 시 호출할 핸들러 지정 (파일명.변수명)
# app 폴더 안의 main.py 파일 내에 정의된 handler 변수(Mangum 객체)를 가리킴
CMD ["app.main.handler"]
