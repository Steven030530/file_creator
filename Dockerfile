FROM python:3.10

WORKDIR /filecreator

COPY requirements.txt requirements.txt

RUN python3 -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python","-m","flask","run"]





