#!/usr/bin/env python

import os.path
import sys
from _kmltools_common import KmlParser

NAME = os.path.basename(sys.argv[0])


def usage():
	print("""
	DESCRIPTION:
		Concatenate multiple kml files with paths and waypoints.
	
	USAGE:
		{} [file.kml]...
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
	root_node = kml.kml_join()
	kml.write(basename=os.path.splitext(filename)[0] + "_join", xml_node=root_node)

	exit(0)


if __name__ == "__main__":
	main()
