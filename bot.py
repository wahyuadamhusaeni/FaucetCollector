from FaucetCollector import FaucetCollector
import time
import pyfiglet 
from colorama import init, Fore
import argparse
import pathlib


init(autoreset=True)


def FaucetCollector_run():
    parser = argparse.ArgumentParser(description="Auto crypto claimer")
    parser.add_argument("path", type=str, help="File path to text file")
    args = parser.parse_args()

    crypto_faucets_file = pathlib.Path(args.path)

    if crypto_faucets_file.suffix != ".txt":
        raise SystemExit(
            f"Unsupported file type: {crypto_faucets_file.suffix}\nSupported file type: .txt"
        )

    bot = FaucetCollector()

    try:
        bot.collect_crypto_faucets(crypto_faucets_file)
        bot.start_collecting_crypto()
    except Exception as e:
        bot.error_handler(e)
        bot.quit()
    except KeyboardInterrupt:
        bot.quit()


if __name__ == "__main__":
    result = pyfiglet.figlet_format("Faucet Collector")
    print(Fore.LIGHTGREEN_EX + result +  Fore.RESET) 
    FaucetCollector_run()
