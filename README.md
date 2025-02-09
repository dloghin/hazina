![logo](assets/banner.png)

# Hazina - Smart Crypto Wallet with AI Agents

Hazina is a smart crypto wallet that uses AI agents to interact with the user and trade cryptocurrencies. We built this project to offer more privacy to end users by running the trading engine locally or on cloud servers with trusted execution environments (TEE).

The AI agent interacting with the user is build on Coinbase [AgentKit](https://github.com/coinbase/agentkit). The UI is developed with [Flet](https://flet.dev/).

The trading engine is a multi-agent system that uses AI agents to trade cryptocurrencies. This engine is taken from the
paper [**CryptoTrade: A Reflective LLM-based Agent to Guide Zero-shot Cryptocurrency Trading**](https://arxiv.org/abs/2407.09546). and its code is available at https://github.com/Xtra-Computing/CryptoTrade. We modified the code such that:
- it can run with [Ollama](https://ollama.com/) local models (in addition to the default OpenAI models)
- it takes on-chain and market data from [Coinbase](https://docs.cdp.coinbase.com/exchange/docs/welcome).

Word meaning: _"hazina"_ is derived from [_"hazna"_](https://en.wiktionary.org/wiki/hazna) meaning _"treasure"_ in Balkan languages.

## Features
- supports running all the agents locally via Ollama. In particular, we tested Hazina with [llama3.2](https://ollama.com/library/llama3.2) and [deepseek-r1](https://ollama.com/library/deepseek-r1).
- AgentKit can also use Ollama to run locally (with [llama3-groq-tool-use](https://ollama.com/library/llama3-groq-tool-use) model) but this requires some changes in chainlang package. Please see [this commit](https://github.com/dloghin/langchain/commit/52f58d97c3a2824262b497f0517ce112186447e8).


## How to Run

First, install all the [prerequisites](#prerequisites). Then:

```
python -m venv .venv
pip install -r requirements.txt
cd app
# to run as local app
flet run app.py
# or run as browser app
flet run --web app.py
```

## Prerequisites

Note: this is not an exhaustive list. Depending on your system, you may need to install some packages.

### Trading Engine

```
./scripts/install_cryptotrade_requirements.sh
cd app
git clone https://github.com/Xtra-Computing/CryptoTrade.git
cd CryptoTrade
git apply ../../scripts/CryptoTrade.patch
```

Test:
```
cd app
python trader.py
```

### On Ubuntu

```
sudo apt install libmpv-dev libmpv2
sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1
```

### On MacOS

```
brew install pkg-config
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
# then run pip install -r requirements.txt
pip install -r requirements.txt
```

## License

This repo is licensed under the [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) license.