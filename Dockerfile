FROM python:3.12-slim

RUN apt update && apt install -y git
RUN cd / && git clone https://github.com/dloghin/hazina.git
WORKDIR /hazina
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN ./scripts/install_cryptotrade_requirements.sh
RUN cd app && git clone https://github.com/Xtra-Computing/CryptoTrade.git && cd CryptoTrade && git apply ../../scripts/CryptoTrade.patch
WORKDIR /hazina/app
CMD ["python", "trader_server.py"]
EXPOSE 5000