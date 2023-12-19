"""
Reveals output of LRB simulator run in a human readable format (some fields are hugely long).
The results are assumed to have been piped into a file

usage:
    python3 reveal_output.py <lrb_out.txt>
"""
import json
import sys


def main(argv):
    with open(argv[1], "r") as sim_out_f:
        data = json.load(sim_out_f)
    for key, value in data.items():
        if isinstance(value, list):
            value = str(value[:20]) + f"\tlen: {len(value)}"
        print(f"\t{key}: {value}")

if __name__ == "__main__":
    main(sys.argv)