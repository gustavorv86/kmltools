#!/usr/bin/env python

import logging
import os.path
import sys
import xml.dom.minidom as minidom

NAME = os.path.basename(sys.argv[0])

LOG_NAME = "kmltools"
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(levelname)s: %(message)s'

COLORS = {
	"Magenta": 'ffff00ff',
	"Blue": 'ff0000ff',
	"Green": 'ff00ff00',
	"Orange": 'ffffaa00'
}


XML_COLORS = """
<Document>
	<Style id="styleMagenta">
		<LineStyle>
			<color>ffff00ff</color>
			<width>3</width>
		</LineStyle>
	</Style>
	<StyleMap id="styleMapMagenta">
		<Pair>
			<key>normal</key>
			<styleUrl>#styleMagenta</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#styleMagenta</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="styleBlue">
		<LineStyle>
			<color>ff0000ff</color>
			<width>3</width>
		</LineStyle>
	</Style>
	<StyleMap id="styleMapBlue">
		<Pair>
			<key>normal</key>
			<styleUrl>#styleBlue</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#styleBlue</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="styleGreen">
		<LineStyle>
			<color>ff00ff00</color>
			<width>3</width>
		</LineStyle>
	</Style>
	<StyleMap id="styleMapGreen">
		<Pair>
			<key>normal</key>
			<styleUrl>#styleGreen</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#styleGreen</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="styleOrange">
		<LineStyle>
			<color>ffffaa00</color>
			<width>3</width>
		</LineStyle>
	</Style>
	<StyleMap id="styleMapOrange">
		<Pair>
			<key>normal</key>
			<styleUrl>#styleOrange</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#styleOrange</styleUrl>
		</Pair>
	</StyleMap>
</Document>
"""


def usage():
	print("""
	DESCRIPTION:
		Inspect kml file.

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


def get_element_id(dom, id_value) -> minidom.Element:
	"""
	Devuelve el primer nodo que tenga atributo id = id_value.
	Si no encuentra ninguno, devuelve None.
	"""

	for node in dom.getElementsByTagName("*"):  # * = todos los nodos
		if node.hasAttribute("id") and node.getAttribute("id") == id_value:
			return node
	return None


def get_key_color(value):
	for key, val in COLORS.items():
		if val == value:
			return key
	return None


def kml_fix(kml_file: str) -> minidom.Document | None:
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

	# Add StyleMaps
	document_node = dom.getElementsByTagName('Document')[0]

	styles_dom = minidom.parseString(XML_COLORS)

	styles_nodes = styles_dom.getElementsByTagName('Style')
	for style_node in styles_nodes:
		document_node.appendChild(style_node)

	stylemaps_nodes = styles_dom.getElementsByTagName('StyleMap')
	for style_node in stylemaps_nodes:
		document_node.appendChild(style_node)

	stylemap_remove_set = set()
	style_remove_set = set()

	# Placemark
	placemark_nodes = dom.getElementsByTagName('Placemark')
	if placemark_nodes:
		for placemark_node in placemark_nodes:
			placemark_name = placemark_node.getElementsByTagName('name')[0].firstChild.nodeValue.strip()
			placemark_styleurl_node = placemark_node.getElementsByTagName('styleUrl')[0]
			placemark_styleurl_txt = placemark_styleurl_node.firstChild.nodeValue.strip()[1:]  # Delete the first character '#'.

			stylemap_node = get_element_id(dom, placemark_styleurl_txt)

			styleurl_nodes = stylemap_node.getElementsByTagName('styleUrl')

			styleurl_list = []
			for styleurl_node in styleurl_nodes:
				styleurl_txt = styleurl_node.firstChild.nodeValue.strip()[1:]  # Delete the first character '#'.
				styleurl_list.append(styleurl_txt)

			styleurl_txt = styleurl_list[0]

			style_node = get_element_id(dom, styleurl_txt)
			color_node = style_node.getElementsByTagName('color')[0]  # TODO un waypoint no tiene color.
			color_txt = color_node.firstChild.nodeValue.strip()

			color_name = get_key_color(color_txt)

			print(f"track {placemark_name}, color {color_txt}, {color_name}.")

			if color_name is None:
				print(f"Error: color {color_name} not found.")

			else:

				placemark_styleurl_node.firstChild.nodeValue = "styleMap" + color_name

				stylemap_remove_set.add(placemark_styleurl_txt)
				style_remove_set.update(styleurl_list)

	return dom

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
	dom = kml_fix(filename)

	basename = os.path.splitext(filename)[0]

	new_filename = basename + "_fix.kml"
	count = 1
	while os.path.exists(new_filename):
		new_filename = basename + '_fix_{}.kml'.format(count)
		count += 1

	write_dom(dom, new_filename)
	exit(0)


if __name__ == "__main__":
	main()
