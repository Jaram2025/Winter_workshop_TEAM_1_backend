FROM python:3.11-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /src

# Poetry 설치
RUN pip install "poetry==1.6.1"
RUN pip install fastapi uvicorn sqlalchemy pymysql python-multipart sqlmodel yarl pydantic_settings python-jose[cryptography] passlib[bcrypt] 
RUN pip install "pydantic[email]>=2.0.0"
RUN pip install pyjwt

# poetry의 정의 파일 복사
COPY pyproject.toml* poetry.lock* ./ 

# poetry로 라이브러리 설치
RUN poetry config virtualenvs.in-project true 
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

# uvicorn 서버 실행
ENTRYPOINT ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]