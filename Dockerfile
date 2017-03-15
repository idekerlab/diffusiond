FROM continuumio/anaconda:4.2.0

RUN pip install grpcio-tools networkx

ADD . /app

CMD ["python","/app/heat_diffusion_service.py"]
