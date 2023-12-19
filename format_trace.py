"""
converts a PIN trace to one usable by the LRB simulator

e.g. PIN trace of:
    1221116.321004675: 0x7f600f5de293: W 0x7fffa490b578
to LRB trace of:
    1221116321004675 140735954335096 4096

usage:
    python3 format_trace.py <pinatrace.out> <lrb_trace.tr>
"""
import sys
import re

def hex_to_int(s: str) -> int:
    # convert to page addr by removing last 3 bits
    s = s[:-3] + "000"
    return int(s, 0)
    # return int_value & 4096

def main(argv):
    prog = re.compile(r"^(\d+).(\d+): (\w+): (R|W) (\w+)$")
    output = []
    print("clearing outfile...")
    with open(argv[2], "w") as out_f:
        out_f.write("")
    print(f"Starting read or {argv[1]}")
    with open(argv[2], "a") as out_f:
        with open(argv[1], "r") as in_f:
            i = 0
            while line := in_f.readline():
                if m := prog.match(line):
                    t_s, t_ns, _, _, addr = m.groups()
                    t_total = (int(t_s) * 10**9) + int(t_ns)
                    addr = hex_to_int(addr)
                    size = 4096 # pages are a constant 4kb size
                    output.append(f"{t_total} {addr} {size}")
                i += 1
                # reset and flush every 1M
                if (i % 1000000 == 0):
                    print(i)
                    out_f.write("\n".join(output) + "\n")
                    output = []
    print(f"Done! Writing to out_f {argv[2]}")
    with open(argv[2], "a") as out_f:
        out_f.write("\n".join(output))

if __name__ == "__main__":
    main(sys.argv)