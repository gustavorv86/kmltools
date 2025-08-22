#!/usr/bin/env python

import os.path
import sys
from _kmltools_common import KmlParser

NAME = os.path.basename(sys.argv[0])


def usage():
	print(f"""
	DESCRIPTION:
		Reverse track of kml file.

	USAGE:
		{NAME} [file.kml]
	""")


def main():
	args = sys.argv[1:]

	if not args:
		usage()
		exit(1)

	if args[0] == "--help" or args[0] == "-h":
		usage()
		exit(1)

	filename = args[0]
	kml = KmlParser(filename)
	kml.kml_reverse()
	basename = os.path.splitext(filename)[0] + "_reverse"
	kml.write(basename)

	exit(0)


if __name__ == "__main__":
	main()
