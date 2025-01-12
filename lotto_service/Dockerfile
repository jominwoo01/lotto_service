# Python 3.10 slim 이미지를 기반으로 사용
FROM python:3.10-slim

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt /app/

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . /app/

# Django 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
