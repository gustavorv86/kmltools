#!/usr/bin/env python

import logging
import os.path
import sys
import xml.dom.minidom as minidom

NAME = os.path.basename(sys.argv[0])

LOG_NAME = "kmltools"
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(levelname)s: %(message)s'

KML_TEMPLATE = """
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>track_template.kml</name>
	<StyleMap id="sm_default">
		<Pair>
			<key>normal</key>
			<styleUrl>#s_default</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#s_default_hl</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="s_default">
		<LineStyle>
			<color>ffaa00ff</color>
			<width>3</width>
		</LineStyle>
	</Style>
	<Style id="s_default_hl">
		<LineStyle>
			<color>ffaa00ff</color>
			<width>3</width>
		</LineStyle>
	</Style>
	<Placemark>
		<name>track_template</name>
		<styleUrl>#sm_default</styleUrl>
		<LineString>
			<tessellate>1</tessellate>
			<coordinates>
			</coordinates>
		</LineString>
	</Placemark>
</Document>
</kml>
"""


def usage():
	print("""
	DESCRIPTION:
		Split a kml file with multiple paths into multiple kml files with a single path.

	USAGE:
		{} [file.kml]
	""".format(NAME))


def logger():
	log_formatter = logging.Formatter(LOG_FORMAT)

	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(log_formatter)
	stream_handler.setLevel(LOG_LEVEL)

	log = logging.getLogger(LOG_NAME)
	log.setLevel(LOG_LEVEL)
	log.addHandler(stream_handler)

	return log


def kml_split(kml_file: str) -> list[minidom.Document]:
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

	placemark_nodes = dom.getElementsByTagName('Placemark')

	dom_list = []

	for placemark_node in placemark_nodes:

		name_node = placemark_node.getElementsByTagName('name')[0].firstChild
		name_txt = name_node.nodeValue.replace('.KML', '.kml').replace('.kml', '')

		coord_node = placemark_node.getElementsByTagName('coordinates')[0].firstChild
		coords_txt = coord_node.nodeValue

		output_dom = minidom.parseString(KML_TEMPLATE)

		name_node = output_dom.getElementsByTagName('name')[0].firstChild
		name_node.nodeValue = name_txt

		coords_node = output_dom.getElementsByTagName('coordinates')[0].firstChild
		coords_node.nodeValue = coords_txt

		placemark_node = coords_node.parentNode.parentNode.parentNode
		name_node = placemark_node.getElementsByTagName('name')[0].firstChild
		name_node.nodeValue = name_txt

		dom_list.append(output_dom)

	return dom_list


def write_dom(dom_list: list[minidom.Document]):
	log = logging.getLogger(LOG_NAME)

	for dom in dom_list:

		filename = dom.getElementsByTagName('name')[0].firstChild.nodeValue + ".kml"
		count = 1
		while os.path.exists(filename):
			filename = dom.getElementsByTagName('name')[0].firstChild.nodeValue + "_" + str(count) + ".kml"
			count += 1

		fd = open(filename, "w")
		fd.write(dom.toxml())
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
	dom_list = kml_split(filename)
	write_dom(dom_list)
	exit(0)


if __name__ == "__main__":
	main()
