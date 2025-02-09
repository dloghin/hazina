import sys

import dotenv
# sys.path.append('../CryptoTrade')
from CryptoTrade.eth_env import ETHTradingEnv
from CryptoTrade.eth_trial import eth_run
from CryptoTrade.run_agent import get_parser

def print_msg(msg):
    print("{}".format(msg))


def run_trader_openai(callback=None, api_key=None):
    if not api_key:
        api_key = dotenv.get_key(".env", "OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")

    parser = get_parser()
    args = parser.parse_args()
    args.dataset = "eth"
    args.model = "gpt-4o"
    args.use_memory = True
    args.starting_date = "2023-10-01"
    args.ending_date = "2023-12-01"
    args.openai_key = api_key

    env = ETHTradingEnv(args)
    starting_state, reward, done, info = env.reset()
    eth_run(env, '', [], starting_state, args=args, callback=callback)


def run_trader_ollama(callback=None):
    parser = get_parser()
    args = parser.parse_args()
    args.dataset = "eth"
    args.model = "llama3.2"
    args.use_memory = True
    args.starting_date = "2023-10-01"
    args.ending_date = "2023-12-01"

    env = ETHTradingEnv(args)
    starting_state, reward, done, info = env.reset()
    eth_run(env, '', [], starting_state, args=args, callback=callback)


if __name__ == '__main__':
    run_trader_ollama(print_msg)