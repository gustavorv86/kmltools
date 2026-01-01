#!/usr/bin/env python

import os.path
import sys
from _kmltools_common import KmlParser

NAME = os.path.basename(sys.argv[0])


def usage():
	print("""
	DESCRIPTION:
		Convert kml track file to gpx.

	USAGE:
		{} [file.kml]
	""".format(NAME))


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
	gpx = kml.to_gpx()
	kml.write(basename=os.path.splitext(filename)[0], xml_node=gpx, extension="gpx")

	exit(0)


if __name__ == "__main__":
	main()
