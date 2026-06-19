#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib
SLOT=0x38; PA=0x23; PB=0x22

def parse(dump: bytes):
    objs=[]; base=0
    for pool,count in (("A",PA),("B",PB)):
        for slot in range(count):
            b=dump[base+slot*SLOT:base+(slot+1)*SLOT]
            u=lambda o:int.from_bytes(b[o:o+2],"little")
            objs.append({"pool":pool,"slot":slot,"active":u(0),"y":u(2),"x":u(4),"state":u(6),"sprite":u(8),"behavior":u(0x18)})
        base += count*SLOT
    return objs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('dump_a', type=Path)
    ap.add_argument('dump_b', type=Path)
    args=ap.parse_args()
    a=args.dump_a.read_bytes(); b=args.dump_b.read_bytes()
    print('sha256 A', hashlib.sha256(a).hexdigest())
    print('sha256 B', hashlib.sha256(b).hexdigest())
    print('identical', a==b)
    ao=parse(a); bo=parse(b)
    for x,y in zip(ao,bo):
        if x!=y:
            print('diff', x, y)
if __name__=='__main__':
    main()
