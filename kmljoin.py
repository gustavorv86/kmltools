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
			<color>99ffac59</color>
			<width>6</width>
		</LineStyle>
	</Style>
	<Style id="s_default_hl">
		<LineStyle>
			<color>ff0000ff</color>
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
		Concatenate multiple kml files with paths and waypoints.
	
	USAGE:
		{} [file.kml]...
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


def kml_merge(kml_list: list) -> minidom.Document:
	log = logging.getLogger(LOG_NAME)

	output_name_txt = ""
	output_coords_txt = ""
	output_placemark_waypoint_list = []

	for kml_file in kml_list:
		if not os.path.isfile(kml_file):
			log.warning("file {} not found.".format(kml_file))
			continue

		try:
			input_dom = minidom.parse(kml_file)
			log.info("file {} loaded.".format(kml_file))
		except Exception as ex:
			log.error("cannot read {} file.".format(kml_file))
			log.error("EXCEPTION: {}.".format(ex))
			continue

		# Waypoints

		waypoint_nodes = input_dom.getElementsByTagName('Point')
		if waypoint_nodes:
			for wp in waypoint_nodes:
				placemark_node = wp.parentNode
				output_placemark_waypoint_list.append(placemark_node)

		# LineString

		linestring_nodes = input_dom.getElementsByTagName('LineString')
		if linestring_nodes:
			for ls_node in linestring_nodes:
				coord_node = ls_node.getElementsByTagName('coordinates')[0].firstChild
				coords_txt = coord_node.nodeValue
				output_coords_txt += coords_txt

			name_txt = input_dom.getElementsByTagName('name')[0].firstChild.nodeValue
			output_name_txt += name_txt.replace('.kml', '_')

	# End kml loop

	output_dom = minidom.parseString(KML_TEMPLATE)

	name_node = output_dom.getElementsByTagName('name')[0].firstChild
	name_node.nodeValue = output_name_txt[:-1]

	coords_node = output_dom.getElementsByTagName('coordinates')[0].firstChild
	coords_node.nodeValue = output_coords_txt

	placemark_node = coords_node.parentNode.parentNode.parentNode
	name_node = placemark_node.getElementsByTagName('name')[0].firstChild
	name_node.nodeValue = output_name_txt[:-1]

	document_node = output_dom.getElementsByTagName('Document')[0]
	for wp in output_placemark_waypoint_list:
		document_node.appendChild(wp)

	return output_dom


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

	dom = kml_merge(args)

	basename = ""
	for file in args:
		basename += os.path.splitext(file)[0]

	new_filename = basename + "_join.kml"
	count = 1
	while os.path.exists(new_filename):
		new_filename = basename + "_join_{}.kml".format(count)
		count += 1

	write_dom(dom, new_filename)
	exit(0)


if __name__ == "__main__":
	main()
