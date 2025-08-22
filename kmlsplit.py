#!/usr/bin/env python

import os.path
import sys
from _kmltools_common import KmlParser

NAME = os.path.basename(sys.argv[0])


def usage():
	print(f"""
	DESCRIPTION:
		Split a kml file with multiple paths into multiple kml files with a single path.

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
	root_nodes = kml.kml_split()

	basename = os.path.splitext(filename)[0]
	for i, root_node in enumerate(root_nodes):
		kml.write(basename + f"_split{i}", root_node)

	exit(0)


if __name__ == "__main__":
	main()
