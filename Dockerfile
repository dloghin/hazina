# To be used on Autonome (https://www.autono.meme/)

FROM python:3.12-slim

RUN apt update && apt install -y git gcc
RUN cd / && git clone https://github.com/dloghin/hazina.git
WORKDIR /hazina
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN ./scripts/install_cryptotrade_requirements.sh
RUN cd app && git clone https://github.com/Xtra-Computing/CryptoTrade.git && cd CryptoTrade && git apply ../../scripts/CryptoTrade.patch
WORKDIR /hazina/app
EXPOSE 5000
CMD ["python", "trader_server.py"]
