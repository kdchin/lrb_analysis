"""
Calculates statistics about a trace file dataset for LRB:
- total lines
- unique addresses
- Simulates LRU performance on the dataset and reports:
1. number of total evictions
2. number of evictions that were "bad" aka within the belady boundary

usage:
    python3 dataset_qualities.py <lrb_trace.tr> cache_size belady_boundary

`cache_size` is an integer representing how bytes are allowed in the cache. The cache implementation assumes we are using 4kb pages.
`belady_boundary` is an integer representing the timesteps of the belady boundary
"""
import sys
import re
from collections import OrderedDict
 
# copied from online
# https://www.geeksforgeeks.org/lru-cache-in-python-using-ordereddict/
class LRUCache:
 
    # initialising capacity
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
 
    # we return the value of the key
    # that is queried in O(1) and return -1 if we
    # don't find the key in out dict / cache.
    # And also move the key to the end
    # to show that it was recently used.
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]
 
    # first, we add / update the key by conventional methods.
    # And also move the key to the end to show that it was recently used.
    # But here we will also check whether the length of our
    # ordered dictionary has exceeded our capacity,
    # If so we remove the first key (least recently used)
    def put(self, key: int, value: int) -> int | None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            k, v = self.cache.popitem(last = False)
            return k
 

def main(argv):
    prog = re.compile(r"^(\d+) (\d+) (\d+)$")
    traces = set()
    cache_size = int(argv[2]) // (4 * 1024) #  4kb
    belady_boundary = int(argv[3])

    cache = LRUCache(cache_size) 
    n_evictions = 0
    bad_evictions = 0

    recent_evictions = []

    with open(argv[1], "r") as in_f:
        i = 0
        while line := in_f.readline():
            if m := prog.match(line):
                t, addr, size = m.groups()
                traces.add(addr)

                # evaluate good decision ratio
                new_recent_evictions = []
                for (t_evict, evicted_addr) in recent_evictions:
                    if t_evict + belady_boundary > i:
                        if evicted_addr == addr:
                            # we evicted too soon
                            bad_evictions += 1
                        else:
                            new_recent_evictions.append((t_evict, evicted_addr))
                recent_evictions = new_recent_evictions

                popped = cache.put(addr, addr)
                if popped:
                    n_evictions += 1
                    recent_evictions.append((i, popped))
                i += 1
    print(f"LRU_bad_evictions={bad_evictions}")
    print(f"LRU_n_evictions={n_evictions}")
    print(f"n_addresses={i}")
    print(f"uniq_addresses={len(traces)}")


if __name__ == "__main__":
    main(sys.argv)