#!/bin/bash
pip install pandas
pip install numpy
pip install matplotlib
pip install scikit-learn
pip install pyyaml
pip install openai
pip install ollama
pip install tenacity
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
pip install torch==2.5.0 -f https://data.pyg.org/whl/torch-2.5.0+cu124.html
pip install torch-cluster -f https://data.pyg.org/whl/torch-2.5.0+cu124.html
fi