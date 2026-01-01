import logging
import os
import sys
import xmltodict


class KmlParser:

	LOG_NAME = "kmltools"
	LOG_LEVEL = logging.INFO
	LOG_FORMAT = '%(levelname)s: %(message)s'

	KML_TEMPLATE = """
	<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
	<Document>
		<name>track_template.kml</name>
		<Placemark>
			<name>track_template</name>
			<LineString>
				<tessellate>1</tessellate>
				<coordinates>
				</coordinates>
			</LineString>
		</Placemark>
	</Document>
	</kml>
	"""

	GPX_TEMPLATE = """
	<gpx version="1.0" xmlns="http://www.topografix.com/GPX/1/0">
		<!--
		<trk>
			<name>gpxname</name>
			<trkseg>
				<trkpt lat="0" lon="0">
					<ele>0</ele>
				</trkpt>
				<trkpt lat="1" lon="0">
					<ele>0</ele>
				</trkpt>
				<trkpt lat="2" lon="0">
					<ele>0</ele>
				</trkpt>
			</trkseg>
		</trk>
		-->
	</gpx>
	"""

	@staticmethod
	def _logger():
		log_formatter = logging.Formatter(KmlParser.LOG_FORMAT)

		stream_handler = logging.StreamHandler(sys.stdout)
		stream_handler.setFormatter(log_formatter)
		stream_handler.setLevel(KmlParser.LOG_LEVEL)

		log = logging.getLogger(KmlParser.LOG_NAME)
		log.setLevel(KmlParser.LOG_LEVEL)
		log.addHandler(stream_handler)

		return log

	def __init__(self, filename: str):
		if not os.path.isfile(filename):
			raise ValueError(f"file {filename} not found.")

		self.log = KmlParser._logger()
		self.basename, self.extension = os.path.splitext(filename)
		self.extension = self.extension[1:].lower()

		with open(filename) as fd:
			self.log.info(f"open file {filename}.")
			if self.extension == "kml":
				self.root_node = xmltodict.parse(fd.read())
			elif self.extension == "gpx":
				self._to_kml(xmltodict.parse(fd.read()))
			else:
				raise ValueError(f"Invalid extension {self.extension}.")

	def _to_kml(self, gpx_node: dict):
		self.root_node = xmltodict.parse(KmlParser.KML_TEMPLATE)
		self.root_node["kml"]["Document"]["name"] = os.path.basename(self.basename)
		self.root_node["kml"]["Document"]["Placemark"] = list()

		trk_nodes = self.find_nodes("trk", gpx_node)
		for i, trk_node in enumerate(trk_nodes):
			if "name" in trk_node:
				track_name = trk_node["name"]
			else:
				track_name = f"track_{i}"
			coordinates_txt = ""
			trkseg_nodes = self.find_nodes("trkseg", trk_node)
			for trkseg_node in trkseg_nodes:
				trkpt_nodes = self.find_nodes("trkpt", trkseg_node)
				for trkpt_node in trkpt_nodes:
					lat = trkpt_node["@lat"]
					lon = trkpt_node["@lon"]
					ele = trkpt_node["ele"]
					coordinates_txt += f"{lon},{lat},{ele} "

			self.root_node["kml"]["Document"]["Placemark"].append(
				{
					"name": track_name,
					"LineString": {
						"coordinates": coordinates_txt.strip()
					}
				}
			)


	def _find_nodes(self, tag: str, node: object) -> list:
		results = []

		if isinstance(node, list):

			for item in node:
				results += self._find_nodes(tag, item)

		if isinstance(node, dict):

			for key, item in node.items():
				if key == tag:

					if isinstance(item, list):
						results += item
					else:
						results.append(item)

				results += self._find_nodes(tag, item)

		return results

	def find_nodes(self, tag: str, node=None) -> list:
		if node is None:
			node = self.root_node
		return self._find_nodes(tag, node)

	def kml_reverse(self):
		document_node = self.root_node["kml"]["Document"]
		document_node["name"] += "_reverse"

		linestring_nodes = self.find_nodes("LineString", document_node, )
		self.log.info(f"number of linestring nodes found: {len(linestring_nodes)}.")

		for linestring_node in linestring_nodes:
			coordinates_txt = linestring_node["coordinates"]
			coordinates_list = coordinates_txt.split(' ')
			coordinates_list.reverse()
			linestring_node["coordinates"] = " ".join(coordinates_list)

	def kml_split(self) -> list[dict]:
		document_node = self.root_node["kml"]["Document"]
		document_name = self.root_node["kml"]["Document"]["name"]

		placemark_nodes = self.find_nodes("Placemark", document_node)
		self.log.info(f"number of placemark nodes found: {len(placemark_nodes)}.")

		new_root_nodes = []

		for i, placemark_node in enumerate(placemark_nodes):
			name = placemark_node["name"]

			if "LineString" not in placemark_node:
				continue

			coordinates = placemark_node["LineString"]["coordinates"]

			new_root_node = xmltodict.parse(KmlParser.KML_TEMPLATE)
			new_root_node["kml"]["Document"]["name"] = name
			new_root_node["kml"]["Document"]["Placemark"]["name"] = name
			new_root_node["kml"]["Document"]["Placemark"]["LineString"]["coordinates"] = coordinates

			new_root_nodes.append(new_root_node)

		return new_root_nodes

	def kml_join(self) -> dict:
		document_node = self.root_node["kml"]["Document"]
		document_name = document_node["name"]

		linestring_nodes = self.find_nodes("LineString", document_node, )
		self.log.info(f"number of linestring nodes found: {len(linestring_nodes)}.")

		sum_coordinates_txt = ""
		for linestring_node in linestring_nodes:
			coordinates_txt = linestring_node["coordinates"]
			sum_coordinates_txt += coordinates_txt + " "

		new_root_node = xmltodict.parse(KmlParser.KML_TEMPLATE)
		new_root_node["kml"]["Document"]["name"] = document_name + "_join"
		new_root_node["kml"]["Document"]["Placemark"]["name"] = document_name + "_join"
		new_root_node["kml"]["Document"]["Placemark"]["LineString"]["coordinates"] = sum_coordinates_txt.strip()

		return new_root_node

	@staticmethod
	def _to_gpx_trkpt_nodes(coordinates_txt: str) -> list:
		coordinates_list = coordinates_txt.split(' ')
		track_points = []
		for coordinate in coordinates_list:
			lon, lat, ele = coordinate.split(",")
			track_points.append((lon, lat, ele))

		trkpt_nodes = list()
		for lon, lat, ele in track_points:
			trkpt_node = {
				"@lat": lat,
				"@lon": lon,
				"ele": ele
			}
			trkpt_nodes.append(trkpt_node)

		return trkpt_nodes

	def to_gpx(self) -> dict:
		document_node = self.root_node["kml"]["Document"]

		placemark_nodes = self.find_nodes("Placemark", document_node)
		self.log.info(f"number of placemark nodes found: {len(placemark_nodes)}.")

		gpx_node = xmltodict.parse(KmlParser.GPX_TEMPLATE)
		gpx_node["gpx"]["trk"] = list()

		for placemark_node in placemark_nodes:
			name = placemark_node["name"]
			coordinates = placemark_node["LineString"]["coordinates"]

			new_trk_node = {
				"name": name,
				"trkseg": {
					"trkpt": KmlParser._to_gpx_trkpt_nodes(coordinates)
				}
			}

			gpx_node["gpx"]["trk"].append(new_trk_node)

		return gpx_node

	def write(self, basename: str = None, xml_node: dict = None, extension="kml") -> str:
		if basename is None:
			basename = self.basename

		filename = basename + "." + extension
		count = 1
		while os.path.exists(filename):
			filename = basename + f'_{count}.{extension}'
			count += 1

		if xml_node is None:
			xml_content = xmltodict.unparse(self.root_node, pretty=True)
		else:
			xml_content = xmltodict.unparse(xml_node, pretty=True)

		with open(filename, "w", encoding="utf-8") as f:
			f.write(xml_content)

		self.log.info(f"file {filename} created successfully.")
		return filename
