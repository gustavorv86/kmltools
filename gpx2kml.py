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
			<color>ff0000ff</color>
			<width>3</width>
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
		Convert kml track file to gpx.

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


def gpx2kml(gpx_file: str) -> minidom.Document | None:
	log = logging.getLogger(LOG_NAME)

	if not os.path.isfile(gpx_file):
		log.warning("file {} not found.".format(gpx_file))
		exit(2)

	try:
		dom = minidom.parse(gpx_file)
		log.info("file {} loaded.".format(gpx_file))
	except Exception as ex:
		log.error("cannot read {} file.".format(gpx_file))
		log.error("EXCEPTION: {}.".format(ex))
		exit(3)

	coords_list = []

	trkpt_nodes = dom.getElementsByTagName("trkpt")
	for pt_node in trkpt_nodes:
		lat = pt_node.getAttribute("lat")
		lon = pt_node.getAttribute("lon")
		ele_node = pt_node.getElementsByTagName("ele")[0]
		ele = ele_node.firstChild.nodeValue
		coords_list.append((lon, lat, ele))

	output_name_txt = os.path.splitext(os.path.basename(gpx_file))[0]

	output_dom = minidom.parseString(KML_TEMPLATE)
	name_node = output_dom.getElementsByTagName('name')[0].firstChild
	name_node.nodeValue = output_name_txt

	placemark_node = output_dom.getElementsByTagName('Placemark')[0]
	name_node = placemark_node.getElementsByTagName('name')[0].firstChild
	name_node.nodeValue = output_name_txt

	coordinates_txt = ""
	for lon, lat, ele in coords_list:
		coordinates_txt += "{},{},{} ".format(lon, lat, ele)

	coordinate_node = output_dom.getElementsByTagName("coordinates")[0].firstChild
	coordinate_node.nodeValue = coordinates_txt

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

	filename = args[0]
	dom = gpx2kml(filename)

	basename = os.path.splitext(filename)[0]

	new_filename = basename + ".kml"
	count = 1
	while os.path.exists(new_filename):
		new_filename = basename + '_{}.kml'.format(count)
		count += 1

	write_dom(dom, new_filename)
	exit(0)


if __name__ == "__main__":
	main()
