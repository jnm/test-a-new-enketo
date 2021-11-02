FROM python:3
RUN pip install requests
COPY index.py /opt
USER nobody
CMD ["python", "/opt/index.py"]
