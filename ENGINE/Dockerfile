FROM python

WORKDIR /dokerizacijaENGINE

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5001
CMD ["python3", "main.py"]