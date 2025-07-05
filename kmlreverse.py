#!/usr/bin/env python

import logging
import os.path
import sys
import xml.dom.minidom as minidom

NAME = os.path.basename(sys.argv[0])

LOG_NAME = "kmltools"
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(levelname)s: %(message)s'


def usage():
	print("""
	DESCRIPTION:
		Reverse track of kml file.

	USAGE:
		{} [file.kml]
	""".format(NAME))


def logger():
	log_formatter = logging.Formatter(LOG_FORMAT)

	stream_handler = logging.StreamHandler(sys.stdout)
	stream_handler.setFormatter(log_formatter)
	stream_handler.setLevel(LOG_LEVEL)

	log = logging.getLogger(LOG_NAME)
	log.setLevel(LOG_LEVEL)
	log.addHandler(stream_handler)

	return log


def kml_reverse(kml_file: str) -> minidom.Document | None:
	log = logging.getLogger(LOG_NAME)

	if not os.path.isfile(kml_file):
		log.warning("file {} not found.".format(kml_file))
		exit(2)

	try:
		dom = minidom.parse(kml_file)
		log.info("file {} loaded.".format(kml_file))
	except Exception as ex:
		log.error("cannot read {} file.".format(kml_file))
		log.error("EXCEPTION: {}.".format(ex))
		exit(3)

	# LineString

	linestring_nodes = dom.getElementsByTagName('LineString')
	if linestring_nodes:
		for ls_node in linestring_nodes:
			coord_node = ls_node.getElementsByTagName('coordinates')[0].firstChild
			coords_txt = coord_node.nodeValue.strip()
			coords_list = coords_txt.split(' ')
			coords_list.reverse()
			coords_txt = "\n\t\t\t\t" + " ".join(coords_list)
			coord_node.nodeValue = coords_txt

			placemark_node = ls_node.parentNode

			name_placemark_node = placemark_node.getElementsByTagName('name')[0].firstChild
			name_placemark_node_txt = name_placemark_node.nodeValue + '_reverse'
			name_placemark_node.nodeValue = name_placemark_node_txt

	else:
		log.warning("track <LineString> not found.")
		exit(3)

	document_name_node = dom.getElementsByTagName('name')[0].firstChild
	document_name_txt = document_name_node.nodeValue.replace('.kml', '_reverse.kml')
	document_name_node.nodeValue = document_name_txt

	return dom


def write_dom(dom: minidom.Document, filename: str):
	log = logging.getLogger(LOG_NAME)

	xml_txt = dom.toprettyxml()

	fd = open(filename, "w")
	for line in xml_txt.split('\n'):
		if line.strip():
			fd.write(line + "\n")
	fd.close()

	log.info("file {} created successfully.".format(filename))


def main():
	logger()
	args = sys.argv[1:]

	if not args:
		usage()
		exit(1)

	if args[0] == "--help" or args[0] == "-h":
		usage()
		exit(1)

	filename = args[0]
	dom = kml_reverse(filename)

	basename = os.path.splitext(filename)[0]

	new_filename = basename + "_reverse.kml"
	count = 1
	while os.path.exists(new_filename):
		new_filename = basename + '_reverse_{}.kml'.format(count)
		count += 1

	write_dom(dom, new_filename)
	exit(0)


if __name__ == "__main__":
	main()
