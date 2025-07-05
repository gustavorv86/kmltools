#!/usr/bin/env python

import logging
import os.path
import sys
import xml.dom.minidom as minidom

NAME = os.path.basename(sys.argv[0])

LOG_NAME = "kmltools"
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(levelname)s: %(message)s'

GPX_TEMPLATE = """
<gpx version="1.0" xmlns="http://www.topografix.com/GPX/1/0">
	<!--
	<trk>
		<name>gpxname</name>
		<trkseg>
			<trkpt lat="0" lon="0">
				<ele>0</ele>
			</trkpt>
		</trkseg>
	</trk>
	-->
</gpx>
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


def kml2gpx(kml_file: str) -> minidom.Document | None:
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

	track_segments = []

	placemark_nodes = dom.getElementsByTagName('Placemark')
	if not placemark_nodes:
		log.error("track <Placemark> not found.")
		exit(3)

	for placemark_node in placemark_nodes:
		track_name_txt = placemark_node.getElementsByTagName('name')[0].firstChild.nodeValue
		linestring_nodes = placemark_node.getElementsByTagName('LineString')

		for ls_node in linestring_nodes:
			coord_node = ls_node.getElementsByTagName('coordinates')[0].firstChild
			coords_node_txt = coord_node.nodeValue.strip()
			coords_node_list = coords_node_txt.split(' ')
			track_path = []
			for coords in coords_node_list:
				lon, lat, ele = coords.split(",")
				track_path.append((lon, lat, ele))

			track_segments.append((track_name_txt, track_path))

	output_dom = minidom.parseString(GPX_TEMPLATE)

	gpx_node = output_dom.getElementsByTagName('gpx')[0]

	for track_name_txt, track_path in track_segments:
		trk_node = output_dom.createElement('trk')

		track_name_dom = output_dom.createElement('name')
		track_name_txt_dom = output_dom.createTextNode(track_name_txt)

		trk_node.appendChild(track_name_dom)
		track_name_dom.appendChild(track_name_txt_dom)

		trkseg_node = output_dom.createElement('trkseg')

		for lon, lat, ele in track_path:
			child_point_dom = output_dom.createElement('trkpt')
			child_point_dom.setAttribute("lat", lat)
			child_point_dom.setAttribute("lon", lon)

			child_ele_dom = output_dom.createElement('ele')
			child_ele_text_dom = output_dom.createTextNode(ele)

			child_point_dom.appendChild(child_ele_dom)
			child_ele_dom.appendChild(child_ele_text_dom)

			trkseg_node.appendChild(child_point_dom)

		trk_node.appendChild(trkseg_node)
		gpx_node.appendChild(trk_node)

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
	dom = kml2gpx(filename)

	basename = os.path.splitext(filename)[0]

	new_filename = basename + ".gpx"
	count = 1
	while os.path.exists(new_filename):
		new_filename = basename + '_{}.gpx'.format(count)
		count += 1

	write_dom(dom, new_filename)
	exit(0)


if __name__ == "__main__":
	main()
