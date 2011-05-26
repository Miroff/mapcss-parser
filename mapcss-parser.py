#!/usr/bin/python

import sys
from mapcss_parser import MapCSSParser

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "usage: python mapcss.py inputfile"
        raise SystemExit

    content = open(sys.argv[1]).read()
    parser = MapCSSParser(debug=False)
    print parser.parse(content)
