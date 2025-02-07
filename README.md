# hazina
Hazina - Smart Crypto Wallet with AI Agents

## How to Run

```
python -m venv .venv
pip install -r requirments.txt
cd app
# to run as local app
flet run app.py
# or run as browser app
flet run --web app.py
```

## Prerequisite

Note: this is not an exhaustive list. Depending on your system, you may need to install some packages.

### On Ubuntu

```
sudo apt install libmpv-dev libmpv2
sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1
```

### On MacOS

```
brew install pkg-config
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
# then run pip install -r requirments.txt
pip install -r requirments.txt
```

## About

[Hazina](https://github.com/dloghin/hazina) is a crypto wallet in the form of an AI chat. It is based on Coinbase [AgentKit](https://github.com/coinbase/agentkit). The UI is based in [Flet](https://flet.dev/).

Word meaning: "hazina" is derived from ["hazna"](https://en.wiktionary.org/wiki/hazna) meaning treasure in Balkan languages.

## License

This repo is licensed under the [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) license.