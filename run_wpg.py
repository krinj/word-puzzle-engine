import argparse
from wpg.interface.interface import Interface


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="", type=str, help="HELP ME!")
    parser.add_argument("-u", "--used_keys", default="", type=str, help="HELP ME!")
    parser.add_argument('-f', '--flag', action="store_true", help="HELP YO!")
    return parser.parse_args()


args = get_args()
input_path = args.input_path if args.input_path != "" else None
used_keys_path = args.used_keys if args.used_keys != "" else None

if __name__ == "__main__":
    interface = Interface(initial_file=input_path, used_keys_path=used_keys_path)
    interface.run()
