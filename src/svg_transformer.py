#!/usr/bin/env python3
"""
SVG-Transformer / SVG transformer
=================================

Version 2026-08-12 (Nachfolger von / successor of svgTransformer_20251121.py)

Änderungen gegenüber der Vorversion / Changes compared to the previous
version:

1. assign_numbers(): Die Gültigkeitsprüfung der Bezeichnungsfelder erfolgt
   nicht mehr über die Anzahl der Dictionary-Schlüssel (len(t) == 7), sondern
   über das Vorhandensein von 'Nummer' und 'Anker'. MTEXT-Deklarationen
   besitzen nur sechs Schlüssel (ohne 'Sektor') und wurden dadurch bisher
   nie zugeordnet. /
   assign_numbers(): Validity of label fields is no longer checked via the
   number of dictionary keys (len(t) == 7) but via the presence of 'Nummer'
   and 'Anker'. MTEXT declarations only carry six keys (without 'Sektor')
   and were therefore never assigned.

2. assign_numbers(): Ungültige Bezeichnungsfelder werden übersprungen
   (continue). Bisher lief die Zuordnungsschleife auch im Fehlerfall weiter
   und verwendete Nummer und Koordinaten des vorigen Durchlaufs, wodurch
   eine bereits vergebene ID ein zweites Mal gesetzt werden konnte. /
   assign_numbers(): Invalid label fields are skipped (continue). Previously
   the assignment loop also ran in the error case, using number and
   coordinates of the previous iteration, so an already assigned ID could be
   set a second time.

3. get_mtexts(): Das Friedhofskürzel wird aus self.map_id übernommen statt
   fest als 'wld' gesetzt. /
   get_mtexts(): The cemetery code is taken from self.map_id instead of
   being hard-coded as 'wld'.

4. generate_gradient_color_table(): Verwendet matplotlib.colormaps
   (matplotlib >= 3.6) mit Rückfall auf cm.get_cmap(). Letzteres ist seit
   matplotlib 3.7 als veraltet markiert; die Entfernung ist für 3.11
   angekündigt. /
   generate_gradient_color_table(): Uses matplotlib.colormaps
   (matplotlib >= 3.6) with a fallback to cm.get_cmap(). The latter has been
   deprecated since matplotlib 3.7; removal is announced for 3.11.

5. __main__-Block: Aufruf auf die aktuelle Schlüsselwort-Signatur des
   Konstruktors umgestellt; der bisherige Beispielaufruf verwendete noch die
   alte positionale Signatur und war nicht lauffähig. /
   __main__ block: Call adapted to the current keyword signature of the
   constructor; the previous example used the old positional signature and
   was not runnable.

6. make_path(): Ein fehlendes marker-type führte zu einem IndexError.
   Das Attribut bleibt verpflichtend — ohne die Angabe ist nicht
   entscheidbar, ob ein <path> oder ein <circle> entsteht —, gemeldet wird
   der Mangel jetzt aber im Klartext samt Layername. /
   make_path(): A missing marker-type caused an IndexError. The attribute
   remains mandatory — without it there is no deciding whether a <path> or
   a <circle> is produced — but the defect is now reported in plain text
   including the layer name.

7. geom_type(): Ein fehlendes marker-size bei marker-type='circle' führte
   ebenfalls zu einem IndexError und wird nun im Klartext gemeldet. Die
   Bedingung „erforderlich, wenn marker-type='circle'" lässt sich in XSD 1.0
   nicht ausdrücken und wird deshalb im Code geprüft. /
   geom_type(): A missing marker-size with marker-type='circle' likewise
   caused an IndexError and is now reported in plain text. The condition
   "required when marker-type='circle'" cannot be expressed in XSD 1.0 and
   is therefore checked in the code.

8. parse_stylesheet(): Ein fehlendes map_id wurde als Lesefehler des
   Stylesheets gemeldet. Es wird jetzt eigens geprüft und im Klartext
   benannt; im Schema ist das Attribut nun verpflichtend. /
   parse_stylesheet(): A missing map_id was reported as a read error of the
   stylesheet. It is now checked separately and named in plain text; in the
   schema the attribute is now mandatory.

9. Fehlerbehandlung durchgängig auf Ausnahmen umgestellt: Alle bisherigen
   sys.exit(1) in parse_stylesheet(), parse_dxf(), find_reference_frame(),
   load_svg() und load_csv() lösen jetzt StylesheetError, DXFError oder
   SVGTransformerError aus. In Jupyter überlebt der Kernel damit einen
   Fehlversuch, die Meldung erscheint im Traceback statt als nacktes
   SystemExit, und aufrufender Code kann den Fehler abfangen. /
   Error handling converted to exceptions throughout: all former sys.exit(1)
   calls in parse_stylesheet(), parse_dxf(), find_reference_frame(),
   load_svg() and load_csv() now raise StylesheetError, DXFError or
   SVGTransformerError. In Jupyter the kernel survives a failed attempt, the
   message appears in the traceback instead of a bare SystemExit, and
   calling code can handle the error.

Dokumentation / documentation: README.md, STYLESHEET.md
"""

import ezdxf
from lxml import etree as et
import pandas as pd
import math
import json
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from typing import Dict, List, Optional


# ======================================================================
# Ausnahmen / Exceptions
# ======================================================================

class SVGTransformerError(Exception):
    """
    Basisklasse für alle Fehler des Transformers. Fehlerhafte Eingaben
    beenden nicht mehr den Prozess (bisher sys.exit(1)), sondern lösen eine
    Ausnahme aus. Damit bleibt ein Jupyter-Kernel am Leben, die Meldung ist
    im Traceback lesbar, und aufrufender Code kann den Fehler abfangen.
    ---
    Base class for all transformer errors. Faulty input no longer terminates
    the process (previously sys.exit(1)) but raises an exception. This keeps
    a Jupyter kernel alive, makes the message readable in the traceback and
    allows calling code to handle the error.
    """


class StylesheetError(SVGTransformerError):
    """
    Fehler im XML-Stylesheet: nicht lesbar, unvollständig oder mit
    fehlenden Pflichtangaben.
    ---
    Error in the XML stylesheet: unreadable, incomplete or with missing
    mandatory entries.
    """


class DXFError(SVGTransformerError):
    """
    Fehler in der DXF-Zeichnung: nicht lesbar oder mit einem Referenzrahmen,
    der die Bedingungen nicht erfüllt.
    ---
    Error in the DXF drawing: unreadable or with a reference frame that does
    not meet the conditions.
    """


# Gemeinsamer Hinweis zum Aufbau des Referenzrahmen-Layers. /
# Shared hint on the structure of the reference frame layer.
REF_FRAME_HINT = (
    "Die Ebene für den Referenzrahmen darf nur genau einen rechteckigen "
    "Rahmen (als CAD-Polylinie gezeichnet) sowie genau einen Referenzpunkt "
    "(als CAD-Punkt gezeichnet) im gewünschten 0,0-Koordinatenursprung "
    "enthalten.\n"
    "The layer for the reference frame must contain exactly one rectangular "
    "frame (drawn as a CAD polyline) and exactly one reference point (drawn "
    "as a CAD point) at the desired 0,0 origin."
)


class SVGTransformer:
    """
    Klasse zur Umwandlung von DXF-Daten in SVG unter Verwendung eines Stylesheets.
    Unterstützt jetzt auch beliebige Drehung und Ursprung des Referenzrechtecks.
    Erweitert um Mapping-Funktionalität für Farb-Mapping auf bestehende SVG-Dateien.
    Erweitert um JSON-Funktionalität für die Speicherung von Objekten und Metadaten
    sowie direkte Generierung von SVG aus JSON-Dateien.
    Modi:
    - "dxf" (default): DXF-zu-SVG-Transformation
    - "json": SVG direkt aus vorbereiteter JSON-Datei
    - "mapping": Farb-Mapping auf bestehende SVG-Dateien basierend auf CSV-Daten
    ---
    Class for transforming DXF data into SVG using a stylesheet.
    Now also supports arbitrary rotation and origin of the reference rectangle.
    Extended with mapping functionality for color mapping on existing SVG files.
    Extended with JSON functionality for storing objects and metadata
    and direct SVG generation from JSON files.
    Modes:
    - "dxf" (default): DXF-to-SVG transformation
    - "json": SVG directly from prepared JSON file
    - "mapping": Color mapping on existing SVG files based on CSV data
    """
    def __init__(
            self,
            dxf_filepath=None,
            stylesheet_filepath=None,
            svg_filepath=None,
            csv_filepath=None,
            json_filepath=None,
            mode: str = "dxf"):
        """
        Initialisiert den SVGTransformer mit direkten Dateipfaden.
        Unterstützt drei Modi:
        - "dxf": DXF zu SVG + CSV/JSON
        - "mapping": bestehendes SVG + CSV für Farb-Mapping
        - "json": SVG direkt aus vorbereiteter JSON-Datei
        ---
        Initializes the SVGTransformer with full file paths.
        Supports three modes:
        - "dxf": DXF to SVG + CSV/JSON
        - "mapping": color mapping on existing SVG using CSV
        - "json": direct SVG generation from preprocessed JSON
        """
        self.mode = mode

        # Datei-Pfade
        self.dxf_filepath = dxf_filepath
        self.stylesheet_filepath = stylesheet_filepath
        self.svg_filepath = svg_filepath
        self.csv_filepath = csv_filepath
        self.json_filepath = json_filepath

        # Stylesheet und DXF
        self.stylesheet = None
        self.msp = None

        # Geometrische Referenzwerte
        self.dxf_x_offset = 0
        self.dxf_y_offset = 0
        self.dxf_width = 0
        self.dxf_height = 0
        self.ref_origin = (0, 0)
        self.ref_angle = 0.0  # in Radiant

        # Inhaltliche Daten
        self.map_id = None
        self.obj_list = []
        self.decl_list = []

        # Mapping-Modus
        self.tree = None
        self.root = None
        self.df = None


    def parse_stylesheet(self):
        """
        Lädt und parst das Stylesheet (XML) und speichert das Wurzelelement
        sowie die map_id.
        Output/Beispiel: self.stylesheet ist ein lxml-Element, self.map_id
        ist z.B. 'wld'.
        ---
        Loads and parses the stylesheet (XML), storing the root element and
        map_id.
        Output/Example: self.stylesheet is an lxml element, self.map_id
        is e.g. 'wld'.
        """
        try:
            stylesheet_file = et.parse(self.stylesheet_filepath)
            self.stylesheet = stylesheet_file.getroot()
        except Exception as e:
            raise StylesheetError(
                f"Stylesheet konnte nicht gelesen werden: "
                f"{self.stylesheet_filepath}\n"
                f"Stylesheet could not be read: "
                f"{self.stylesheet_filepath}\n"
                f"({e})") from e

        # map_id getrennt prüfen, damit ein fehlendes Kürzel nicht als
        # Lesefehler gemeldet wird. Der Wert bildet den Präfix aller
        # Grabstätten-IDs und ist deshalb unverzichtbar. /
        # Check map_id separately so that a missing code is not reported as a
        # read error. The value forms the prefix of all grave IDs and is
        # therefore indispensable.
        map_ids = self.stylesheet.xpath('./@map_id')
        if not map_ids:
            raise StylesheetError(
                f"Im Stylesheet fehlt das Attribut map_id (dreibuchstabiges "
                f"Friedhofskürzel, z. B. 'wld'): "
                f"{self.stylesheet_filepath}\n"
                f"The stylesheet lacks the attribute map_id (three-letter "
                f"cemetery code, e.g. 'wld'): "
                f"{self.stylesheet_filepath}")
        self.map_id = map_ids[0]

    def parse_dxf(self):
        """
        Lädt die DXF-Datei und initialisiert das Modelspace-Objekt (self.msp).
        Output/Beispiel: self.msp ist ein ezdxf Modelspace-Objekt.
        ---
        Loads the DXF file and initializes the modelspace object (self.msp).
        Output/Example: self.msp is an ezdxf Modelspace object.
        """
        try:
            doc = ezdxf.readfile(self.dxf_filepath)
            self.msp = doc.modelspace()
        except Exception as e:
            raise DXFError(
                f"DXF-Datei konnte nicht geladen werden: "
                f"{self.dxf_filepath}\n"
                f"DXF file could not be loaded: {self.dxf_filepath}\n"
                f"({e})") from e

    def find_reference_frame(self):
        """
        Bestimmt den Referenzrahmen anhand des Stylesheets und berechnet
        Offsets, Maße, Ursprung und Drehwinkel.
        Vom durch den Punkt auf dem Referenzrahmenlayer (in der DXF-Zeichnung)
        deklarierten Ursprung gehen zwei Kanten des Rahmens (Rechteck) aus.
        Die längere der beiden Kanten wird als X-Achse (SVG-Querformat)
        verwendet.
        Ist das Rechteck ein Quadrat, wird die Kante gewählt, die näher an
        der X-Achse liegt.
        Sind beide Kanten gleich lang und beide 45° zur X-Achse, wird der
        User gefragt, ob im oder gegen den Uhrzeigersinn gedreht werden soll.
        Gibt eine Fehlermeldung und eine Anweisung aus, falls die Bedingungen
        nicht erfüllt sind.
        ---
        Determines the reference frame using the stylesheet and calculates
        offsets, dimensions, origin and rotation angle.
        From the origin point (POINT on the reference_frame layer), two edges
        of the rectangle (LWPOLYLINE) start.
        The longer of the two edges is used as the X-axis (landscape SVG).
        If the rectangle is a square, the edge closer to the X-axis is chosen.
        If both edges are exactly the same length and both are at 45° to the
        X-axis, the user is asked whether to rotate clockwise or
        counterclockwise.
        Prints an error and instruction if the conditions are not met.
        """
        ref_frame_layers = self.stylesheet.xpath(
            './/reference_frame/@layer_name')
        if len(ref_frame_layers) != 1:
            raise StylesheetError(
                f"Es muss genau ein reference_frame im Stylesheet geben, "
                f"gefunden: {len(ref_frame_layers)}.\n"
                f"There must be exactly one reference_frame in the "
                f"stylesheet, found: {len(ref_frame_layers)}.")
        ref_frame_layer = ref_frame_layers[0]
        x_values, y_values = [], []
        rectangles = []
        # Alle Rechtecke (LWPOLYLINE mit 4 Punkten) sammeln /
        # Collect all rectangles (LWPOLYLINE with 4 points)
        for pline in self.msp.query(
                f'LWPOLYLINE[layer=="{ref_frame_layer}"]'):
            points = [v for v in pline.vertices()]
            if len(points) == 4:
                rectangles.append(points)
        if len(rectangles) == 0:
            raise DXFError(
                f"Auf dem Layer '{ref_frame_layer}' wurde kein Rechteck (LWPOLYLINE mit 4 Punkten) gefunden.\\n"
                f"On layer '{ref_frame_layer}' no rectangle (LWPOLYLINE with 4 vertices) was found.\\n"
                + REF_FRAME_HINT)
        if len(rectangles) > 1:
            raise DXFError(
                f"Auf dem Layer '{ref_frame_layer}' wurde mehrere Rechtecke (LWPOLYLINE mit 4 Punkten) gefunden.\\n"
                f"On layer '{ref_frame_layer}' multiple rectangles (LWPOLYLINE with 4 vertices) was found.\\n"
                + REF_FRAME_HINT)
        rect_points = rectangles[0]
        for v in rect_points:
            if v[0] not in x_values:
                x_values.append(v[0])
            if v[1] not in y_values:
                y_values.append(v[1])
        # Ursprungspunkt suchen (POINT auf dem Layer) /
        # Find origin point (POINT on the layer)
        points = [pt for pt in self.msp.query(
            f'POINT[layer=="{ref_frame_layer}"]')]
        if len(points) == 0:
            raise DXFError(
                f"Auf dem Layer '{ref_frame_layer}' wurde kein Referenzpunkt (POINT) gefunden.\\n"
                f"On layer '{ref_frame_layer}' no reference point (POINT) was found.\\n"
                + REF_FRAME_HINT)
        if len(points) > 1:
            raise DXFError(
                f"Auf dem Layer '{ref_frame_layer}' wurde mehrere Referenzpunkte (POINT) gefunden.\\n"
                f"On layer '{ref_frame_layer}' multiple reference points (POINT) was found.\\n"
                + REF_FRAME_HINT)
        self.ref_origin = (
            points[0].dxf.location[0], points[0].dxf.location[1])
        # Finde die beiden Kanten, die vom Ursprungspunkt ausgehen /
        # Find the two edges starting from the origin
        # Suche den Index des Ursprungs im Rechteck /
        # Find the index of the origin in the rectangle
        try:
            idx_origin = rect_points.index(self.ref_origin)
        except ValueError:
            # Falls der Ursprungspunkt nicht exakt auf einem Rechteckpunkt
            # liegt, suche den nächsten / If the origin is not exactly on a
            # rectangle point, find the nearest
            idx_origin = min(
                range(4),
                key=lambda i: (
                    (rect_points[i][0] - self.ref_origin[0])**2 +
                    (rect_points[i][1] - self.ref_origin[1])**2))
            self.ref_origin = rect_points[idx_origin]
        # Die beiden angrenzenden Punkte / The two adjacent points
        idx_next = (idx_origin + 1) % 4
        idx_prev = (idx_origin - 1) % 4
        p0 = self.ref_origin
        p1 = rect_points[idx_next]
        p2 = rect_points[idx_prev]
        # Vektoren und Längen / Vectors and lengths
        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p2[0] - p0[0], p2[1] - p0[1])
        len1 = math.hypot(*v1)
        len2 = math.hypot(*v2)
        # Auswahl der X-Achse / Choose the X-axis
        if abs(len1 - len2) > 1e-6:
            # Längere Kante als X-Achse / Use longer edge as X-axis
            x_vec = v1 if len1 > len2 else v2
        else:
            # Quadrat: Wähle die Kante, die näher an der X-Achse liegt /
            # Square: choose the edge closer to the X-axis
            angle1 = abs(math.atan2(v1[1], v1[0]))
            angle2 = abs(math.atan2(v2[1], v2[0]))
            if abs(angle1 - angle2) > 1e-6:
                x_vec = v1 if angle1 < angle2 else v2
            else:
                # Beide Kanten gleich lang und beide 45°: User fragen /
                # Both edges same length and both 45°: ask user
                print("Das Referenzrechteck ist ein Quadrat und beide Kanten "
                      "vom Ursprung liegen exakt bei 45°. Soll im oder gegen "
                      "den Uhrzeigersinn gedreht werden?\nThe reference "
                      "rectangle is a square and both edges from the origin "
                      "are exactly at 45°. Should it be rotated clockwise or "
                      "counterclockwise?")
                print("Geben Sie 'u' für Uhrzeigersinn oder 'g' für gegen den "
                      "Uhrzeigersinn ein:\nEnter 'u' for clockwise or 'g' "
                      "for counterclockwise:")
                while True:
                    inp = input("[u/g]: ").strip().lower()
                    if inp == 'u':
                        x_vec = v1
                        break
                    elif inp == 'g':
                        x_vec = v2
                        break
                    else:
                        print("Bitte 'u' oder 'g' eingeben! / "
                              "Please enter 'u' or 'g'!")
        # Winkel berechnen / Calculate angle
        self.ref_angle = -math.atan2(x_vec[1], x_vec[0])
        # Neue Breite/Höhe basierend auf Vektor-Längen vom Ursprungspunkt aus
        # / New width/height based on vector lengths from the origin point
        # outwards
        if len1 > len2:
            self.dxf_width = len1
            self.dxf_height = len2
        else:
            self.dxf_width = len2
            self.dxf_height = len1

        # Offset bleibt Referenzpunkt
        self.dxf_x_offset = self.ref_origin[0]
        self.dxf_y_offset = self.ref_origin[1]
        print(f"DXF-Referenzrahmen: Breite={self.dxf_width}, "
              f"Höhe={self.dxf_height}, Ursprung={self.ref_origin}, "
              f"Winkel={math.degrees(self.ref_angle):.2f}°\nDXF reference "
              f"frame: width={self.dxf_width}, height={self.dxf_height}, "
              f"origin={self.ref_origin}, angle="
              f"{math.degrees(self.ref_angle):.2f}°")

    
    def get_lwpolylines(self, layername):
        obj_list = []
        for pline in self.msp.query(
                f'LWPOLYLINE[layer=="{layername}"]'):
            obj_dict = {
                'layer': layername,
                'entity': 'LWPOLYLINE',
                'is_closed': pline.is_closed
            }
            # Original-Koordinaten / Original coordinates
            vertice_list = [v for v in pline.vertices()]
            obj_dict['verts'] = vertice_list
            x = [v[0] for v in vertice_list]
            y = [v[1] for v in vertice_list]
            obj_dict['center'] = (
                (max(x) + min(x)) / 2, (max(y) + min(y)) / 2)
            obj_list.append(obj_dict)
        return obj_list
    
    def get_circles(self, layername):
        obj_list = []
        for circle in self.msp.query(f'CIRCLE[layer=="{layername}"]'):
            obj_dict = {
                'layer': layername,
                'entity': 'CIRCLE',
            }
            center_x = circle.dxf.center[0]
            center_y = circle.dxf.center[1]
            obj_dict['verts'] = [(center_x, center_y)]
            obj_dict['center'] = (center_x, center_y)
            obj_list.append(obj_dict)
        return obj_list
    
    def get_mtexts(self, layername):
        obj_list = []
        for declare in self.msp.query(
                f'MTEXT[layer=="{layername}"]'):
            # Friedhofskürzel aus dem Stylesheet statt fest verdrahtet. /
            # Cemetery code taken from the stylesheet instead of hard-coded.
            obj_dict = {'Friedhof': self.map_id}
            text = declare.text
            if len(text) == 25:
                obj_dict['Reihe'] = text[-11:-8]
                obj_dict['Platz'] = text[-7:-4]
                obj_dict['Zusatz'] = text[-3:-1]
                obj_dict['Nummer'] = (
                    f"{self.map_id}-{text[14:17]}.{text[18:21]}-"
                    f"{text[22:24]}")
            else:
                obj_dict['Reihe'] = text[-8:-5]
                obj_dict['Platz'] = text[-4:-1]
                obj_dict['Zusatz'] = '00'
                obj_dict['Nummer'] = (
                    f"{self.map_id}-{text[14:17]}.{text[18:21]}-00")
            obj_dict['Anker'] = (
                declare.dxf.insert[0], declare.dxf.insert[1])
            obj_list.append(obj_dict)
        return obj_list
    
    def get_texts(self, layername):
        obj_list = []
        for declare in self.msp.query(
                f'TEXT[layer=="{layername}"]'):
            obj_dict = {'Friedhof': self.map_id}
            text = declare.dxf.text
            if len(text) == 10:
                obj_dict['Sektor'] = text[:2]
                obj_dict['Reihe'] = text[3:6]
                obj_dict['Platz'] = text[7:10]
                obj_dict['Zusatz'] = '00'
                obj_dict['Nummer'] = (
                    f"{self.map_id}-{text[:2]}.{text[3:6]}.{text[7:10]}-00")
            elif len(text) == 13:
                obj_dict['Sektor'] = text[:2]
                obj_dict['Reihe'] = text[3:6]
                obj_dict['Platz'] = text[7:10]
                obj_dict['Zusatz'] = text[11:13]
                obj_dict['Nummer'] = (
                    f"{self.map_id}-{text[:2]}.{text[3:6]}.{text[7:10]}-"
                    f"{text[11:13]}")
            obj_dict['Anker'] = (
                declare.dxf.insert[0], declare.dxf.insert[1])
            obj_list.append(obj_dict)
        return obj_list

    @staticmethod
    def rotate_and_translate(x, y, origin, angle):
        """
        Wendet eine Translation (zum Ursprung) und eine Rotation (um den
        Ursprung) auf die Koordinaten an.
        Beispiel:
        Eingabe: x=110, y=220, origin=(100,200), angle=0.523 (30°)
        Ausgabe: (x', y')
        ---
        Applies translation (to origin) and rotation (around origin) to the
        coordinates.
        Example:
        Input: x=110, y=220, origin=(100,200), angle=0.523 (30°)
        Output: (x', y')
        """
        # Translation / Translation
        x_rel = x - origin[0]
        y_rel = y - origin[1]
        # Rotation / Rotation
        x_rot = math.cos(angle) * x_rel - math.sin(angle) * y_rel
        y_rot = math.sin(angle) * x_rel + math.cos(angle) * y_rel
        return (x_rot, y_rot)

    def convert_coords(
            self, vert, svg_width, svg_height, dxf_width, dxf_height):
        """
        Wandelt ein Koordinatenpaar (x, y) aus dem DXF-System in das
        SVG-System um, inkl. Ursprung und Drehung.
        Beispiel-Output: (svg_x, svg_y)
        ---
        Converts a coordinate pair (x, y) from the DXF system to the SVG
        system, including origin and rotation.
        Example output: (svg_x, svg_y)
        """
        # 1. Translation und Rotation auf das Referenzsystem /
        # 1. Translation and rotation onto the reference system
        x_rot, y_rot = SVGTransformer.rotate_and_translate(
            vert[0], vert[1], self.ref_origin, self.ref_angle)
        # 2. Normale SVG-Skalierung / 2. Normal SVG scaling
        svg_x = (x_rot * svg_width) / dxf_width
        svg_y = svg_height - ((y_rot * svg_height) / dxf_height)
        return (svg_x, svg_y)

    def d_string(
            self, vert_list, svg_width, svg_height, dxf_width, dxf_height,
            closed):
        """
        Erzeugt einen SVG-d-String aus einer Liste von Koordinaten.
        Beispiel-Output: 'M 10.0,20.0 L 30.0,40.0 L 50.0,60.0 z'
        ---
        Generates an SVG d-string from a list of coordinates.
        Example output: 'M 10.0,20.0 L 30.0,40.0 L 50.0,60.0 z'
        """
        if not vert_list:
            return ''
        first_svg_x, first_svg_y = self.convert_coords(
            vert_list[0], svg_width, svg_height, dxf_width, dxf_height
        )
        d_str = f"M {first_svg_x},{first_svg_y}"
        for coord in vert_list[1:]:
            svg_x, svg_y = self.convert_coords(
                coord, svg_width, svg_height, dxf_width, dxf_height
            )
            d_str += f" L {svg_x},{svg_y}"
        if closed:
            d_str += ' z'
        return d_str

    def set_attrib(self, elem, xpath):
        """
        Setzt Style-Attribute aus dem Stylesheet auf ein SVG-Element.
        Beispiel: elem.attrib['stroke'] = '#000000', elem.attrib['fill'] =
        'none'
        ---
        Sets style attributes from the stylesheet on an SVG element.
        Example: elem.attrib['stroke'] = '#000000', elem.attrib['fill'] =
        'none'
        """
        for s in xpath:
            elem.attrib[s.tag] = s.text

    def set_id(self, o, elem, obj_id_template, obj_counter):
        """
        Setzt die id für ein SVG-Element.
        Beispiel: elem.attrib['id'] = 'wld-Gruppe-1'
        ---
        Sets the id and optionally the aks attribute for an SVG element.
        Example: elem.attrib['id'] = 'wld-Gruppe-1', elem.attrib['aks'] =
        'wld-Gruppe-1'
        """
        if 'SZd-ID' in o:
            elem.attrib['id'] = o['SZd-ID']
        else:
            elem.attrib['id'] = obj_id_template + str(obj_counter)
        return obj_counter + 1

    def geom_type(
            self, group, l, o, layer_name, marker_type, svg_width,
            svg_height, dxf_width, dxf_height, obj_id_template, obj_counter):
        """
        Erzeugt das passende SVG-Element für ein Objekt und fügt es der Gruppe
        hinzu.
        Beispiel: erzeugt ein <path> oder <circle>-Element mit den passenden
        Attributen.
        ---
        Creates the appropriate SVG element for an object and adds it to the
        group.
        Example: creates a <path> or <circle> element with the correct
        attributes.
        """
        entity = o.get('entity', None)
        if marker_type == 'circle':
            entity = 'CIRCLE'
        if entity == 'LWPOLYLINE':
            vert_list = o['verts']
            closed = o['is_closed']
            elem = et.SubElement(group, 'path')
            obj_counter = self.set_id(
                o, elem, obj_id_template, obj_counter)
            elem.attrib['d'] = self.d_string(
                vert_list, svg_width, svg_height, dxf_width, dxf_height,
                closed)
        elif entity == 'CIRCLE':
            center = self.convert_coords(
                o['center'], svg_width, svg_height, dxf_width, dxf_height)
            elem = et.SubElement(group, 'circle')
            obj_counter = self.set_id(
                o, elem, obj_id_template, obj_counter)
            # marker-size ist im Schema optional, weil es für path-Layer
            # bedeutungslos ist; bei marker-type='circle' ist es jedoch
            # zwingend. Diese Bedingung lässt sich in XSD 1.0 nicht
            # ausdrücken und wird deshalb hier geprüft. Ein Ersatzradius
            # würde einen Konfigurationsfehler in einen unauffällig falschen
            # Plan verwandeln. /
            # marker-size is optional in the schema because it is meaningless
            # for path layers; with marker-type='circle' it is mandatory.
            # This condition cannot be expressed in XSD 1.0 and is therefore
            # checked here. A fallback radius would turn a configuration
            # error into an inconspicuously wrong plan.
            marker_size = l.get('marker-size')
            if marker_size is None:
                raise StylesheetError(
                    f"Layer '{layer_name}': marker-type='circle' erfordert "
                    f"die Angabe marker-size.\n"
                    f"Layer '{layer_name}': marker-type='circle' requires "
                    f"the attribute marker-size.")
            elem.attrib['r'] = marker_size
            elem.attrib['cx'] = str(center[0])
            elem.attrib['cy'] = str(center[1])
        # Hole den style_ref vom Layer und finde den entsprechenden Style /
        # Get the style_ref from the layer and find the corresponding style
        style_ref = l.xpath('./@style_ref')[0]
        self.set_attrib(
            elem, self.stylesheet.xpath(
                f'.//svg_style_sequence/svg_style[@style_name="{style_ref}"]/*'))
        return obj_counter

    def make_path(
            self, group, l, obj_id_template, obj_list, svg_width, svg_height,
            dxf_width, dxf_height, obj_counter):
        """
        Erzeugt SVG-Elemente für alle Objekte einer Ebene und fügt sie der
        Gruppe hinzu.
        Beispiel: Fügt mehrere <path> oder <circle>-Elemente zu einer
        SVG-Gruppe hinzu.
        ---
        Creates SVG elements for all objects of a layer and adds them to the
        group.
        Example: Adds multiple <path> or <circle> elements to an SVG group.
        """
        layer_name = l.xpath('./@layer_name')[0]
        # marker-type ist im Schema verpflichtend und wird hier vorausgesetzt:
        # Ohne die Angabe lässt sich nicht entscheiden, ob ein <path> oder ein
        # <circle> entstehen soll. Ein Vorgabewert würde eine Entscheidung
        # unterstellen, die das Stylesheet nicht hergibt. Statt eines
        # IndexError gibt es deshalb eine Meldung im Klartext. /
        # marker-type is mandatory in the schema and required here: without it
        # there is no way to decide whether a <path> or a <circle> should be
        # produced. A default would presume a decision the stylesheet does not
        # provide. Hence a plain-text message instead of an IndexError.
        marker_type = l.get('marker-type')
        if marker_type is None:
            raise StylesheetError(
                f"Layer '{layer_name}': Pflichtattribut marker-type fehlt "
                f"(zulässig: path, circle, array).\n"
                f"Layer '{layer_name}': mandatory attribute marker-type is "
                f"missing (permitted: path, circle, array).")
        for o in obj_list:
            if o['layer'] == layer_name:
                obj_counter = self.geom_type(
                    group, l, o, layer_name, marker_type,
                    svg_width, svg_height, dxf_width, dxf_height,
                    obj_id_template, obj_counter)
        return obj_counter

    def extract_objects(self):
        """
        Extrahiert alle relevanten Objekte (Polylinien, Kreise, Texte) aus der
        DXF und speichert sie in self.obj_list und self.decl_list.
        Beispiel: self.obj_list = [dict1, dict2, ...], self.decl_list =
        [dict3, dict4, ...]
        ---
        Extracts all relevant objects (polylines, circles, texts) from the
        DXF and stores them in self.obj_list and self.decl_list.
        Example: self.obj_list = [dict1, dict2, ...], self.decl_list =
        [dict3, dict4, ...]
        """
        self.obj_list = []
        for l in self.stylesheet.xpath(
                './/dxf_layer_sequence/layer/@layer_name'):
            self.obj_list += self.get_lwpolylines(l)
            self.obj_list += self.get_circles(l)
        self.decl_list = []
        for l in self.stylesheet.xpath(
                './/dxf_references/reference_declaration/@layer_name'):
            self.decl_list += self.get_texts(l)
            self.decl_list += self.get_mtexts(l)

    def assign_numbers(self):
        """
        Ordnet den Objekten in self.obj_list die passenden Nummern aus
        self.decl_list zu, basierend auf den Koordinaten und Layern.
        Ein Bezeichnungsfeld gilt als gültig, wenn es die Schlüssel 'Nummer'
        und 'Anker' besitzt und 'Nummer' nicht leer ist. Ungültige Felder
        werden übersprungen und am Ende gezählt gemeldet.
        Beispiel: obj['SZd-ID'] = 'wld-001.002-03'
        ---
        Assigns the correct numbers from self.decl_list to the objects in
        self.obj_list, based on coordinates and layers.
        A label field is considered valid if it carries the keys 'Nummer'
        and 'Anker' and 'Nummer' is not empty. Invalid fields are skipped
        and reported as a count at the end.
        Example: obj['SZd-ID'] = 'wld-001.002-03'
        """
        offset_x1 = float(self.stylesheet.xpath(
            './/dxf_references/reference_declaration/'
            'offset[@offset_vert="x1"]/text()')[0])
        offset_x2 = float(self.stylesheet.xpath(
            './/dxf_references/reference_declaration/'
            'offset[@offset_vert="x2"]/text()')[0])
        offset_y1 = float(self.stylesheet.xpath(
            './/dxf_references/reference_declaration/'
            'offset[@offset_vert="y1"]/text()')[0])
        offset_y2 = float(self.stylesheet.xpath(
            './/dxf_references/reference_declaration/'
            'offset[@offset_vert="y2"]/text()')[0])
        list_active = self.stylesheet.xpath(
            './/dxf_layer_sequence/layer[@map_to="active_element"]/@layer_name')
        skipped = 0
        mismatched = 0
        assigned = 0
        for t in self.decl_list:
            # Gültigkeitsprüfung über die tatsächlich benötigten Schlüssel.
            # Eine Prüfung über die Anzahl der Schlüssel (len(t) == 7) wäre
            # falsch, da MTEXT-Deklarationen keinen 'Sektor' enthalten und
            # deshalb nur sechs Schlüssel besitzen. /
            # Validity is checked via the keys actually required. Checking
            # the number of keys (len(t) == 7) would be wrong, because MTEXT
            # declarations contain no 'Sektor' and therefore carry only six
            # keys.
            if not t.get('Nummer') or not t.get('Anker'):
                print('Kein gültiges Bezeichnungsfeld (Nummer/Anker fehlt): '
                      f'{t}\n'
                      'Invalid label field (number/anchor missing): '
                      f'{t}')
                skipped += 1
                # Überspringen, damit die Zuordnungsschleife nicht mit
                # Nummer und Koordinaten des vorigen Durchlaufs weiterläuft. /
                # Skip, so the assignment loop does not continue with number
                # and coordinates of the previous iteration.
                continue

            num = t['Nummer']
            x1 = t['Anker'][0] + offset_x1
            x2 = t['Anker'][0] + offset_x2
            y1 = t['Anker'][1] + offset_y1
            y2 = t['Anker'][1] + offset_y2
            g_count = 0

            for g in self.obj_list:
                match = False
                if g['layer'] in list_active:
                    for v in g['verts']:
                        if x1 < v[0] < x2 and y2 < v[1] < y1:
                            match = True
                            g['SZd-ID'] = num
                    if match:
                        g_count += 1

            # Jedem Bezeichnungsfeld muss genau ein Polygon entsprechen.
            # Abweichungen deuten auf ein zu großes oder zu kleines
            # Latenzrechteck hin (siehe reference_declaration/offset). /
            # Exactly one polygon must correspond to each label field.
            # Deviations indicate a latency rectangle that is too large or
            # too small (see reference_declaration/offset).
            if g_count == 1:
                assigned += 1
            else:
                mismatched += 1
                print(f"{num} - {g_count} Polygone / polygons")

        print(f"Anzahl deklarierter Objekte: {len(self.decl_list)}\n"
              f"Number of declared objects: {len(self.decl_list)}")
        print(f"Eindeutig zugeordnet: {assigned} | "
              f"Mehrdeutig oder ohne Treffer: {mismatched} | "
              f"Übersprungen: {skipped}\n"
              f"Uniquely assigned: {assigned} | "
              f"Ambiguous or unmatched: {mismatched} | "
              f"Skipped: {skipped}")

    def generate_svg(self):
        """
        Generiert das SVG-Element und speichert es als Datei.
        Beispiel: Erstellt eine SVG-Datei mit mehreren Gruppen und Pfaden/Kreisen.
        ---
        Generates the SVG element and saves it as a file.
        Example: Creates an SVG file with multiple groups and paths/circles.
        """
        svg_width = int(self.stylesheet.xpath('./@svg_width')[0])
        svg_height_original = (svg_width * self.dxf_height) / self.dxf_width
        svg_height = svg_height_original + 100
        svg = et.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'id': self.map_id,
            'width': str(svg_width),
            'height': str(svg_height),
            'class': self.stylesheet.xpath('./@class')[0]
        })
        
        # Erstelle den Plankopf (title-block) als separate Gruppe /
        # Create the plan header (title-block) as a separate group
        title_block = et.SubElement(svg, 'g', id='title-block')
        
        # Füge SVG-Elemente aus der svg_element_sequence hinzu /
        # Add SVG elements from the svg_element_sequence
        self.add_svg_elements(title_block, svg_height_original)
        
        # Erstelle die Hauptgruppen für die Planzeichnung /
        # Create the main groups for the plan drawing
        for g in self.stylesheet.xpath('.//svg_group_sequence/*'):
            group_name = g.xpath('./@group_name')[0]
            
            # Überspringe title-block, da es bereits erstellt wurde /
            # Skip title-block, as it has already been created
            if group_name == 'title-block':
                # Verwende die bereits existierende title-block Gruppe /
                # Use the already existing title-block group
                group = svg.xpath('.//g[@id="title-block"]')[0]
            else:
                group = et.SubElement(svg, 'g', id=group_name)
            
            obj_id_template = f"{self.map_id}-{group_name}-"
            obj_counter = 1
            for l in self.stylesheet.xpath(
                    f'.//layer[@map_to="{group_name}"]'):
                obj_counter = self.make_path(
                    group, l, obj_id_template, self.obj_list, svg_width,
                    svg_height_original, self.dxf_width, self.dxf_height,
                    obj_counter)
        
        svg_map = et.ElementTree(svg)
        try:
            svg_map.write(self.svg_filepath, pretty_print=True)
            print(f"SVG erfolgreich gespeichert: {self.svg_filepath}\n"
                  f"SVG successfully saved: {self.svg_filepath}")
        except Exception as e:
            print(f"Fehler beim Speichern der SVG: {e}\n"
                  f"Error saving SVG: {e}")

    def add_svg_elements(self, title_block, svg_height_original):
        """
        Fügt SVG-Elemente aus der svg_element_sequence des Stylesheets zum
        Plankopf hinzu.
        ---
        Adds SVG elements from the svg_element_sequence of the stylesheet to
        the title block.
        """
        try:
            svg_width = int(self.stylesheet.xpath('./@svg_width')[0])
            base_y = svg_height_original + 30
            
            svg_elements = self.stylesheet.xpath(
                './/svg_element_sequence/svg_element')
            for element in svg_elements:
                group_name = element.xpath('./@group_name')[0]
                style_ref = element.xpath('./@style_ref')[0]
                map_to = element.xpath('./@map_to')[0]
                translate_x = (
                    float(element.xpath('./@translate-x')[0])
                    if element.xpath('./@translate-x') else 0)
                translate_y = (
                    float(element.xpath('./@translate-y')[0])
                    if element.xpath('./@translate-y') else 0)
                
                # Berechne die finale y-Position /
                # Calculate the final y-position
                final_y = base_y + translate_y
                
                # Erstelle eine Gruppe für dieses Element /
                # Create a group for this element
                element_group = et.SubElement(title_block, 'g', id=group_name)
                
                # Füge Style-Attribute hinzu / Add style attributes
                style_elements = self.stylesheet.xpath(
                    f'.//svg_style_sequence/svg_style[@style_name="'
                    f'{style_ref}"]/*')
                self.set_attrib(element_group, style_elements)
                
                # Füge Transformation hinzu / Add transformation
                element_group.set(
                    'transform', f'translate({translate_x},{final_y})')
                
                # Spezielle Behandlung für verschiedene Gruppen /
                # Special handling for different groups
                if group_name == 'north-arrow':
                    self.process_north_arrow(element_group, element)
                elif group_name == 'scale-bar':
                    self.process_scale_bar(element_group, element, svg_width)
                elif group_name == 'plan_header':
                    self.process_plan_header(element_group, element)
                else:
                    # Standard-Verarbeitung für andere Elemente /
                    # Standard processing for other elements
                    self.process_standard_element(element_group, element)
                        
        except Exception as e:
            print(f"Fehler beim Hinzufügen der SVG-Elemente: {e}")

    def process_north_arrow(self, element_group, element):
        """
        Verarbeitet den Nordpfeil mit Rotation.
        ---
        Processes the north arrow with rotation.
        """
        # Erstelle innere Gruppe für Rotation /
        # Create inner group for rotation
        inner_group = et.SubElement(element_group, 'g')
        
        # Finde den Kreis für Rotationszentrum /
        # Find the circle for the rotation center
        circle_elem = element.xpath('./circle')[0]
        cx = float(circle_elem.get('cx'))
        cy = float(circle_elem.get('cy'))
        
        # Winkel in Grad umrechnen und in entgegengesetzte Richtung drehen /
        # Convert the angle to degrees and rotate in the opposite direction
        angle_degrees = -math.degrees(self.ref_angle)
        
        # Rotation anwenden / Apply rotation
        inner_group.set('transform', f'rotate({angle_degrees} {cx} {cy})')
        
        # Alle Kind-Elemente zur inneren Gruppe hinzufügen /
        # Add all child elements to the inner group
        for child in element:
            if child.tag == 'path':
                path_data = child.get('d')
                if path_data:
                    et.SubElement(inner_group, 'path', d=path_data)
            elif child.tag == 'circle':
                cx = child.get('cx')
                cy = child.get('cy')
                r = child.get('r')
                if cx and cy and r:
                    et.SubElement(inner_group, 'circle', cx=cx, cy=cy, r=r)

    def process_scale_bar(self, element_group, element, svg_width):
        """
        Verarbeitet die Maßstabsleiste mit dynamischen Rechtecken.
        ---
        Processes the scale bar with dynamic rectangles.
        """
        # Hole max_scale Wert / Get the max_scale value
        max_scale_elem = element.xpath('./max_scale')[0]
        max_scale = int(max_scale_elem.text)
        
        # Hole Style-Referenz für Füllung / Get the style_ref for the fill
        style_ref = element.xpath('./@style_ref')[0]
        style_elements = self.stylesheet.xpath(
            f'.//svg_style_sequence/svg_style[@style_name="{style_ref}"]/*')
        
        # Finde das erste Rechteck für Referenz /
        # Find the first rectangle for reference
        first_rect = element.xpath('./rect')[0]
        start_x = float(first_rect.get('x'))
        start_y = float(first_rect.get('y'))
        height = float(first_rect.get('height'))
        
        # Berechne Breite für 1 Meter (1 DXF-Einheit) /
        # Calculate the width for 1 meter (1 DXF unit)
        one_meter_width = (1.0 * svg_width) / self.dxf_width
        
        current_x = start_x
        rect_count = 0
        
        # Erstelle 5 Rechtecke für 1 Meter / Create 5 rectangles for 1 meter
        for i in range(5):
            rect = et.SubElement(element_group, 'rect')
            rect.set('x', str(current_x))
            rect.set('y', str(start_y))
            rect.set('width', str(one_meter_width))
            rect.set('height', str(height))
            
            # Füllung nur für 1., 3., 5. Rechteck /
            # Fill only for the 1., 3., 5. rectangle
            if i % 2 == 0:  # 0, 2, 4 (1., 3., 5.)
                # Gefüllte Rechtecke erben Style von der Gruppe /
                # Filled rectangles inherit style from the group
                pass
            else:
                # Leere Rechtecke: explizit fill="none" setzen /
                # Empty rectangles: explicitly set fill="none"
                rect.set('fill', 'none')
            
            current_x += one_meter_width
            rect_count += 1
        
        # Erstelle 1 Rechteck für 5 Meter / Create 1 rectangle for 5 meters
        five_meter_width = (5.0 * svg_width) / self.dxf_width
        rect = et.SubElement(element_group, 'rect')
        rect.set('x', str(current_x))
        rect.set('y', str(start_y))
        rect.set('width', str(five_meter_width))
        rect.set('height', str(height))
        
        # Keine Füllung für 5-Meter-Rechteck / No fill for 5-meter rectangle
        rect.set('fill', 'none')
        
        current_x += five_meter_width
        rect_count += 1
        
        # Erstelle Rechtecke für 10 Meter / Create rectangles for 10 meters
        ten_meter_width = (10.0 * svg_width) / self.dxf_width
        # Anzahl der 10-Meter-Rechtecke / Number of 10-meter rectangles
        ten_meter_count = (max_scale - 10) // 10
        
        for i in range(ten_meter_count):
            rect = et.SubElement(element_group, 'rect')
            rect.set('x', str(current_x))
            rect.set('y', str(start_y))
            rect.set('width', str(ten_meter_width))
            rect.set('height', str(height))
            
            # Füllung nur für ungerade 10-Meter-Rechtecke (1., 3., 5., ...) /
            # Fill only for odd 10-meter rectangles (1., 3., 5., ...)
            if i % 2 == 0:  # 0, 2, 4, ... (1., 3., 5., ...)
                # Gefüllte Rechtecke erben Style von der Gruppe /
                # Filled rectangles inherit style from the group
                pass
            else:
                # Leere Rechtecke: explizit fill="none" setzen /
                # Empty rectangles: explicitly set fill="none"
                rect.set('fill', 'none')
            
            current_x += ten_meter_width
            rect_count += 1
        
        # Erstelle Text-Labels / Create text labels
        self.create_scale_labels(
            element_group, element, start_x, start_y, one_meter_width,
            five_meter_width, ten_meter_width, ten_meter_count, style_ref)

    def create_scale_labels(
            self, element_group, element, start_x, start_y, one_meter_width,
            five_meter_width, ten_meter_width, ten_meter_count, style_ref):
        """
        Erstellt die Text-Labels für die Maßstabsleiste.
        ---
        Creates the text labels for the scale bar.
        """
        # Finde das erste tspan für Referenz / Find the first tspan for reference
        first_tspan = element.xpath('./tspan')[0]
        label_start_x = float(first_tspan.get('x'))
        label_start_y = float(first_tspan.get('y'))
        two_digit_x_offset = float(first_tspan.get('two-digit-x', 0))
        
        # Hole max_scale Wert für die letzte Zahl /
        # Get the max_scale value for the last number
        max_scale_elem = element.xpath('./max_scale')[0]
        max_scale = int(max_scale_elem.text)
        
        # Erstelle Text-Element (erbt Style von der Gruppe) /
        # Create text element (inherits style from the group)
        text_elem = et.SubElement(element_group, 'text')
        text_elem.set('stroke', 'none')
        
        # Label bei 0 Metern (kein Offset) / Label at 0 meters (no offset)
        tspan = et.SubElement(text_elem, 'tspan')
        tspan.set('x', str(label_start_x))
        tspan.set('y', str(label_start_y))
        tspan.text = '0'
        
        # Labels alle 10 Meter / Labels at 10 meters each
        current_x = label_start_x
        for i in range(1, ten_meter_count + 1):
            meters = i * 10
            current_x += ten_meter_width
            
            tspan = et.SubElement(text_elem, 'tspan')
            
            # Berechne x-Position mit two-digit-x Offset für alle Zahlen
            # außer 0 / Calculate x-position with two-digit-x offset for all
            # numbers except 0
            tspan_x = current_x + two_digit_x_offset
            
            tspan.set('x', str(tspan_x))
            tspan.set('y', str(label_start_y))
            tspan.text = str(meters)
        
        # Letzte Zahl (max_scale) hinzufügen / Add the last number (max_scale)
        if max_scale > ten_meter_count * 10:
            # Berechne Position für die letzte Zahl / Calculate position for the last number
            current_x += ten_meter_width  # +10m weiter / 10m further
            tspan = et.SubElement(text_elem, 'tspan')
            tspan_x = current_x + two_digit_x_offset
            tspan.set('x', str(tspan_x))
            tspan.set('y', str(label_start_y))
            tspan.text = str(max_scale)

    def process_plan_header(self, element_group, element):
        """
        Verarbeitet den Planheader mit Text-Wrapper.
        ---
        Processes the plan header with text wrapper.
        """
        # Erstelle Text-Element als Wrapper / Create text element as wrapper
        text_elem = et.SubElement(element_group, 'text')
        
        # Füge alle tspan-Elemente hinzu / Add all tspan elements
        for child in element:
            if child.tag == 'tspan':
                x = child.get('x')
                y = child.get('y')
                text_content = child.text if child.text else ''
                if x and y:
                    tspan = et.SubElement(text_elem, 'tspan', x=x, y=y)
                    tspan.text = text_content

    def process_standard_element(self, element_group, element):
        """
        Verarbeitet Standard-SVG-Elemente.
        ---
        Processes standard SVG elements.
        """
        # Füge alle Kind-Elemente hinzu / Add all child elements
        for child in element:
            if child.tag == 'path':
                path_data = child.get('d')
                if path_data:
                    et.SubElement(element_group, 'path', d=path_data)
            elif child.tag == 'circle':
                cx = child.get('cx')
                cy = child.get('cy')
                r = child.get('r')
                if cx and cy and r:
                    et.SubElement(element_group, 'circle', cx=cx, cy=cy, r=r)
            elif child.tag == 'rect':
                x = child.get('x')
                y = child.get('y')
                width = child.get('width')
                height = child.get('height')
                if x and y and width and height:
                    et.SubElement(
                        element_group, 'rect', x=x, y=y, width=width,
                        height=height)
            elif child.tag == 'tspan':
                x = child.get('x')
                y = child.get('y')
                text_content = child.text if child.text else ''
                if x and y:
                    text_elem = et.SubElement(element_group, 'text')
                    tspan = et.SubElement(text_elem, 'tspan', x=x, y=y)
                    tspan.text = text_content
            elif child.tag == 'max_scale':
                # Max_scale-Element (wird ignoriert, da es nur ein Wert ist) /
                # Max_scale element (ignored, as it is only a value)
                pass
            else:
                print(f"Unbekanntes Element-Tag: {child.tag}\n"
                      f"Example: Unknown element tag: {child.tag}")

    def export_csv(self):
        """
        Exportiert die Objektliste als CSV-Datei.
        Beispiel: Erstellt 'wld_obj_list.csv' mit allen Objektdaten.
        ---
        Exports the object list as a CSV file.
        Example: Creates 'wld_obj_list.csv' with all object data.
        """
        try:
            df_dxf = pd.DataFrame.from_records(self.obj_list)
            df_dxf.to_csv(self.csv_filepath, sep=';')
            print(f"Objektliste als CSV gespeichert: {self.csv_filepath}\n"
                  f"Example: Object list saved as CSV: {self.csv_filepath}")
        except Exception as e:
            print(f"Fehler beim Speichern der CSV: {e}\n"
                  f"Example: Error saving CSV: {e}")
    
    def export_json(self, filepath=None):
        """
        Exportiert die transformierten Objektdaten und Metadaten in eine JSON-Datei.
        ---
        Exports transformed objects and geometry meta-data (like dxf_width/height)
        to a single JSON file.
        """
        if filepath:
            self.json_filepath = filepath
        elif not self.json_filepath:
            raise ValueError("Pfad für JSON-Datei nicht gesetzt / JSON path not set.")
        data = {
            "meta": {
                "dxf_width": self.dxf_width,
                "dxf_height": self.dxf_height,
                "ref_origin": self.ref_origin,
                "ref_angle_deg": math.degrees(self.ref_angle)
            },
            "objects": self.obj_list
        }
        try:
            with open(self.json_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"JSON-Datei gespeichert: {self.json_filepath}\n"
                  f"JSON file saved: {self.json_filepath}")
        except Exception as e:
            print(f"Fehler beim Speichern der JSON: {e}\n"
                  f"Error saving JSON: {e}")
    
    def load_json(self, filepath=None):
        """
        Lädt Objekte und Metadaten aus einer JSON-Datei.
        ---
        Loads object data and geometry metadata from a JSON file.
        """
        if filepath:
            self.json_filepath = filepath
        if not self.json_filepath:
            raise ValueError("Pfad für JSON-Datei nicht gesetzt / JSON path not set.")
        try:
            with open(self.json_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.dxf_width = data["meta"]["dxf_width"]
            self.dxf_height = data["meta"]["dxf_height"]
            self.ref_origin = tuple(data["meta"]["ref_origin"])
            self.ref_angle = math.radians(data["meta"]["ref_angle_deg"])
            self.obj_list = data["objects"]
            print(f"JSON-Datei geladen: {self.json_filepath}\n"
                  f"JSON file loaded: {self.json_filepath}")
        except Exception as e:
            print(f"Fehler beim Laden der JSON: {e}\n"
                  f"Error loading JSON: {e}")
    
    def run(self):
        """
        Führt den gesamten Transformationsprozess aus: Stylesheet und DXF
        laden, Objekte extrahieren, Nummern zuordnen, SVG und CSV
        exportieren.
        Im Mapping-Modus: lädt SVG und CSV und wendet Farb-Mapping an.
        ---
        Runs the complete transformation process: loads stylesheet and DXF,
        extracts objects, assigns numbers, exports SVG and CSV.
        In mapping mode: loads SVG and CSV and applies color mapping.
        """
        if self.mode == "dxf":
            self.parse_stylesheet()
            self.parse_dxf()
            self.find_reference_frame()
            self.extract_objects()
            self.assign_numbers()
            self.generate_svg()
            self.export_json()
            self.export_csv()
        elif self.mode == "json":
            self.parse_stylesheet()
            self.load_json()
            self.generate_svg()
        elif self.mode == "mapping":
            if not self.svg_filepath or not self.csv_filepath:
                raise ValueError(
                    "SVG- und CSV-Pfade müssen im Mapping-Modus gesetzt sein.\n"
                    "SVG and CSV paths must be set in mapping mode.")
            self.load_svg()
            self.load_csv()
            # apply_mapping muss manuell mit color_table aufgerufen werden
            # Beispiel: transformer.apply_mapping(color_table={"wert1": "#FF0000"})
            print(
                "SVG und CSV geladen. Rufen Sie apply_mapping() mit einer "
                "color_table auf, um das Mapping anzuwenden.\n"
                "SVG and CSV loaded. Call apply_mapping() with a "
                "color_table to apply the mapping.")
            print(
                "Beispiel: transformer.apply_mapping("
                "color_table={'wert1': '#FF0000', 'wert2': '#00FF00'})" "\n"
                "Example: transformer.apply_mapping("
                "color_table={'wert1': '#FF0000', 'wert2': '#00FF00'})")
            print(
                "Danach können Sie save_svg() aufrufen, um das Ergebnis zu "
                "speichern.\n"
                "After calling apply_mapping(), you can call save_svg() "
                "to save the result.")
        else:
            raise ValueError(f"Unbekannter Modus: {self.mode}\n"
                             f"Example: Unknown mode: {self.mode}")

    # --- Mapping-Modus-Methoden ---
    def set_mapping_inputs(self, svg_path: str, csv_path: str):
        """
        Setzt die SVG- und CSV-Pfade für den Mapping-Modus.
        ---
        Sets the SVG and CSV paths for mapping mode.
        """
        self.svg_filepath = svg_path
        self.csv_filepath = csv_path

    def load_svg(self, svg_path: Optional[str] = None):
        """
        Lädt die SVG-Datei für den Mapping-Modus.
        Parameter:
        svg_path: Optionaler Pfad zur SVG-Datei. Falls nicht 
        angegeben, wird self.svg_filepath verwendet.
        ---
        Loads the SVG file for mapping mode.
        Parameters:
        svg_path: Optional path to SVG file. If not provided, 
        uses self.svg_filepath.
        """
        filepath = svg_path or self.svg_filepath
        if not filepath:
            raise ValueError("SVG-Pfad muss gesetzt sein." + "\n"
                             "SVG path must be set.")
        try:
            self.tree = et.parse(filepath)
            self.root = self.tree.getroot()
            # Setze auch self.svg_filepath, falls über Parameter gesetzt /
            # Also set self.svg_filepath if set via parameter
            if svg_path:
                self.svg_filepath = svg_path
        except Exception as e:
            raise SVGTransformerError(
                f"SVG-Datei konnte nicht geladen werden: {filepath}\n"
                f"SVG file could not be loaded: {filepath}\n"
                f"({e})") from e

    def load_csv(
            self,
            csv_path: Optional[str] = None,
            dtype: Optional[Dict[str, type]] = None):
        """
        Lädt die CSV-Datei für den Mapping-Modus.
        ---
        Loads the CSV file for mapping mode.
        
        Parameters:
        csv_path: Optional path to CSV file. If not provided, uses self.csv_filepath.
                Beispiel: Optionaler Pfad zur CSV-Datei. Falls nicht angegeben,
                wird self.csv_filepath verwendet.
        dtype: Optional dictionary mapping column names to data types.
            Beispiel: {"mapping": int, "SZd-ID": str}
            Achtung: int-Spalten mit NaN sollten mit pd.Int64Dtype() angegeben werden.
        """
        filepath = csv_path or self.csv_filepath
        if not filepath:
            raise ValueError("CSV-Pfad muss gesetzt sein.\nCSV path must be set.")

        try:
            # Optional: dtype-Anpassung für Integer mit NaN
            if dtype:
                dtype = {
                    col: (pd.Int64Dtype() if typ is int else typ)
                    for col, typ in dtype.items()
                }

            self.df = pd.read_csv(
                filepath,
                sep=';',
                dtype=dtype,
                keep_default_na=True,
                na_values=["", "NA", "N/A"]
            )

            # Falls Pfad über Parameter übergeben wurde, merken
            if csv_path:
                self.csv_filepath = csv_path

        except Exception as e:
            raise SVGTransformerError(
                f"CSV-Datei konnte nicht geladen werden: {filepath}\n"
                f"CSV file could not be loaded: {filepath}\n"
                f"({e})") from e

    def apply_mapping(
            self,
            id_col: str = "SZd-ID",
            value_col: str = "mapping",
            color_table: Optional[Dict] = None,
            tooltip_cols: Optional[List[str]] = None,
            url_col: Optional[str] = None,
            require_tooltip_if_any: bool = True):
        """
        Wendet das Farb-Mapping auf SVG-Elemente basierend auf CSV-Daten an.
        Fügt zusätzlich Tooltip-Texte als <title> und data-tooltip-Attribute hinzu
        und kann optional URL-Links aus einer CSV-Spalte setzen.

        Parameter:
        ----------
        id_col:
            Name der Spalte mit SVG-Element-IDs (Default: "SZd-ID")
        value_col:
            Spalte mit Mapping-Werten (Default: "mapping")
        color_table:
            Dictionary mit Mapping-Werten (int/str) → Farbwerte (z.B. "#ff0000")
        tooltip_cols:
            Liste von Spaltennamen, die im Tooltip angezeigt werden sollen.
            Wenn None, werden [id_col, value_col] verwendet.
        url_col:
            Name der Spalte, die eine URL enthält. Falls gesetzt und in der Zeile
            ein Wert vorhanden ist, wird das SVG-Element in ein <a>-Element
            mit href und target="_blank" eingewickelt.
        require_tooltip_if_any:
            - True (Default):
                Zeilen ohne Mapping-Wert (value_col) werden trotzdem verarbeitet,
                solange in den Tooltip-Spalten mindestens eine Information steht.
                Ergebnis: Element kann nur Tooltip, nur URL oder beides haben.
            - False:
                Verhalten wie „klassisches“ Mapping:
                Zeilen ohne Mapping-Wert werden komplett übersprungen
                (kein Tooltip, keine URL, keine Farbe).

        ---
        Applies color mapping to SVG elements based on CSV data.
        Optionally adds tooltips (<title> + data-tooltip) and wraps elements
        with <a href target="_blank"> using URLs from the CSV.
        """

        if self.tree is None or self.df is None:
            raise RuntimeError(
                "SVG oder CSV nicht geladen.\n"
                "SVG or CSV not loaded."
            )
        if color_table is None:
            raise ValueError(
                "color_table muss angegeben werden.\n"
                "color_table must be specified."
            )

        # Namespace-Map für XPath (SVG-Namespace)
        ns = {'svg': self.root.nsmap.get(None, 'http://www.w3.org/2000/svg')}

        for _, row in self.df.iterrows():
            # Ohne ID kann nichts gemappt werden → überspringen
            if pd.isna(row.get(id_col)):
                continue

            elem_id = str(row[id_col])
            value = row.get(value_col)

            # Wenn require_tooltip_if_any == False und kein Mapping-Wert:
            # Zeile komplett ignorieren (wie bisheriges Verhalten)
            if (not require_tooltip_if_any) and pd.isna(value):
                continue

            # SVG-Element per ID suchen
            xpath = f".//*[@id='{elem_id}']"
            elem_list = self.root.xpath(xpath)
            if not elem_list:
                print(
                    f"Warnung: Kein SVG-Element mit id='{elem_id}' gefunden.\n"
                    f"Warning: No SVG element with id='{elem_id}' found."
                )
                continue

            elem = elem_list[0]

            # ------------------------------------------------------------
            # 1) Optional: URL-Link-Wrapper aus CSV (url_col)
            # ------------------------------------------------------------
            url = None
            if url_col is not None:
                raw_url = row.get(url_col)
                if pd.notna(raw_url):
                    url = str(raw_url).strip()

            if url:
                parent = elem.getparent()
                if parent is not None:
                    # Nicht doppelt verlinken, falls already in <a>
                    parent_local = parent.tag.split('}')[-1]
                    if parent_local != 'a':
                        ns_svg = self.root.nsmap.get(
                            None, 'http://www.w3.org/2000/svg'
                        )
                        a_elem = et.Element(f'{{{ns_svg}}}a')
                        # Moderner SVG-2-Weg
                        a_elem.set('href', url)
                        a_elem.set('target', '_blank')

                        # Optional: xlink:href nur dann setzen, wenn Namespace
                        # bereits in der root.nsmap existiert (nicht dynamisch setzen)
                        if 'xlink' in self.root.nsmap:
                            a_elem.set(
                                '{http://www.w3.org/1999/xlink}href', url
                            )

                        # elem durch <a><elem/></a> ersetzen
                        idx = parent.index(elem)
                        parent.remove(elem)
                        a_elem.append(elem)
                        parent.insert(idx, a_elem)
                # elem bleibt das Kind (path/circle), darauf setzen wir weiter Styles/Tooltips

            # ------------------------------------------------------------
            # 2) Farbe (Mapping) setzen – nur wenn value vorhanden
            # ------------------------------------------------------------
            color = None
            if pd.notna(value):
                # Versuch: numerische Werte sinnvoll in int verwandeln
                try:
                    if isinstance(value, (int, float)):
                        val_key = int(float(value))
                    else:
                        # z.B. "3", "4.0" → 3, 4
                        val_key = int(float(str(value).strip()))
                except (ValueError, TypeError):
                    # Wenn nicht numerisch, als String-Schlüssel verwenden
                    val_key = str(value).strip()

                # Farbzuweisung mit Fallbacks:
                if val_key in color_table:
                    color = color_table[val_key]
                elif str(val_key) in color_table:
                    color = color_table[str(val_key)]
                else:
                    # Falls val_key numerisch ist, Clipping auf min/max numeric keys
                    if isinstance(val_key, (int, float)):
                        numeric_keys = [
                            k for k in color_table.keys()
                            if isinstance(k, (int, float))
                        ]
                        if numeric_keys:
                            min_k = min(numeric_keys)
                            max_k = max(numeric_keys)
                            clipped = max(min_k, min(max_k, int(val_key)))
                            if clipped in color_table:
                                color = color_table[clipped]

            # Farbe via style setzen (nur wenn color gesetzt)
            if color:
                style_str = elem.attrib.get("style", "")
                style_dict = {}
                if style_str:
                    for part in style_str.split(";"):
                        if ":" in part:
                            key, val = part.strip().split(":", 1)
                            style_dict[key.strip()] = val.strip()
                style_dict["fill"] = color
                new_style = "; ".join(
                    f"{k}: {v}" for k, v in style_dict.items()
                )
                elem.attrib["style"] = new_style

            # ------------------------------------------------------------
            # 3) Tooltip-Texte (SVG <title> + data-tooltip)
            # ------------------------------------------------------------
            cols = tooltip_cols if tooltip_cols else [id_col, value_col]
            tooltip_lines = []
            for col in cols:
                val = row.get(col)
                if pd.notna(val):
                    tooltip_lines.append(f"{col}: {val}")

            # Tooltip nur erzeugen, wenn wenigstens eine Info vorhanden ist
            if tooltip_lines:
                tooltip_text = "\\n".join(tooltip_lines)

                # bestehendes <title> ggf. entfernen
                existing_title = elem.xpath("./svg:title", namespaces=ns)
                if existing_title:
                    elem.remove(existing_title[0])

                title_elem = et.SubElement(
                    elem, "{http://www.w3.org/2000/svg}title"
                )
                title_elem.text = tooltip_text.replace("\\n", "\n")

                # data-tooltip für JS-Tooltipsystem
                elem.set("data-tooltip", tooltip_text)

        # ------------------------------------------------------------
        # 4) JavaScript-Fallback für hübsche Tooltips (nur wenn tooltip_cols gesetzt)
        # ------------------------------------------------------------
        if tooltip_cols:
            existing_script = self.root.xpath(".//svg:script", namespaces=ns)
            if not existing_script:
                script = et.Element(
                    "{http://www.w3.org/2000/svg}script",
                    attrib={"type": "text/javascript"}
                )
                script.text = """
(function() {
  'use strict';
  
  function createTooltip() {
    var tooltip = document.createElement('div');
    tooltip.id = 'svg-tooltip';
    tooltip.style.cssText = 'position:fixed;background:#222;color:#fff;padding:5px 8px;' +
      'border-radius:4px;pointer-events:none;font-size:12px;display:none;z-index:99999;' +
      'max-width:300px;word-wrap:break-word;';
    
    var container = document.body || document.documentElement || document.querySelector('svg');
    if (container) {
      container.appendChild(tooltip);
    }
    return tooltip;
  }
  
  function getTooltip() {
    var existing = document.getElementById('svg-tooltip');
    return existing || createTooltip();
  }
  
  function getEventPosition(e) {
    var x = 0, y = 0;
    if (e.clientX !== undefined && e.clientY !== undefined) {
      x = e.clientX;
      y = e.clientY;
      if (window.scrollX !== undefined) {
        x += window.scrollX;
        y += window.scrollY;
      } else if (window.pageXOffset !== undefined) {
        x += window.pageXOffset;
        y += window.pageYOffset;
      }
    } else if (e.pageX !== undefined && e.pageY !== undefined) {
      x = e.pageX;
      y = e.pageY;
    }
    return {x: x, y: y};
  }
  
  function showTooltip(e, text) {
    var tooltip = getTooltip();
    if (!tooltip) return;
    
    var pos = getEventPosition(e);
    tooltip.style.left = (pos.x + 12) + 'px';
    tooltip.style.top = (pos.y + 12) + 'px';
    tooltip.innerHTML = text ? text.replace(/\\n/g, '<br>') : '';
    tooltip.style.display = 'block';
  }
  
  function hideTooltip() {
    var tooltip = document.getElementById('svg-tooltip');
    if (tooltip) {
      tooltip.style.display = 'none';
    }
  }
  
  function initTooltips() {
    try {
      var elements = document.querySelectorAll('[data-tooltip]');
      for (var i = 0; i < elements.length; i++) {
        (function(el) {
          var text = el.getAttribute('data-tooltip');
          if (!text) return;
          
          el.addEventListener('mouseenter', function(e) {
            showTooltip(e, text);
          }, false);
          el.addEventListener('mousemove', function(e) {
            showTooltip(e, text);
          }, false);
          el.addEventListener('mouseleave', function(e) {
            hideTooltip();
          }, false);
        })(elements[i]);
      }
    } catch (err) {
      console.error('Tooltip initialization error:', err);
    }
  }
  
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(initTooltips, 10);
  } else {
    if (document.addEventListener) {
      document.addEventListener('DOMContentLoaded', initTooltips, false);
    }
    if (window.addEventListener) {
      window.addEventListener('load', initTooltips, false);
    }
  }
  
  if (window.addEventListener) {
    window.addEventListener('load', function() {
      setTimeout(initTooltips, 100);
    }, false);
  }
})();
"""
                self.root.append(script)

        print("Farb-Mapping, Tooltips und URLs angewendet.\n"
              "Color mapping, tooltips and URLs applied.")

    def generate_gradient_color_table(
            self, min_val: int, max_val: int, cmap_name: str = "RdYlBu_r",
            steps: int = 100) -> Dict[int, str]:
        """
        Generiert eine Farbtabelle mit Gradienten-Farben basierend auf einem
        Wertebereich.
        Parameters:
        min_val: Minimaler Wert im Wertebereich
        max_val: Maximaler Wert im Wertebereich
        cmap_name: Name der matplotlib Colormap (Standard: "RdYlBu_r")
        steps: Anzahl der Schritte für die Colormap (Standard: 100)
        Returns:
        Dictionary mit Werten als Keys und Hex-Farbcodes als Value
        ---
        Generates a color table with gradient colors based on a value range.
        Parameters:
        min_val: Minimum value in the value range
        max_val: Maximum value in the value range  
        cmap_name: Name of the matplotlib Colormap (default: "RdYlBu_r")
        steps: Number of steps for the Colormap (default: 100)
        Returns:
        Dictionary with values as keys and hex color codes as values
        """
        norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
        # cm.get_cmap() ist seit matplotlib 3.7 veraltet und wird in 3.11
        # entfernt; die Registry matplotlib.colormaps (ab 3.6) tritt an
        # seine Stelle. Der except-Zweig hält ältere Installationen
        # lauffähig. /
        # cm.get_cmap() has been deprecated since matplotlib 3.7 and will be
        # removed in 3.11; the registry matplotlib.colormaps (from 3.6)
        # takes its place. The except branch keeps older installations
        # working.
        try:
            cmap = mpl.colormaps[cmap_name].resampled(steps)
        except (AttributeError, KeyError):
            cmap = cm.get_cmap(cmap_name, steps)

        value_to_color = {}
        for val in range(min_val, max_val + 1):
            rgba = cmap(norm(val))
            hex_color = mcolors.to_hex(rgba)
            value_to_color[val] = hex_color
        return value_to_color

    def save_svg(self, out_path: str):
        """
        Speichert die gemappte SVG-Datei.
        ---
        Saves the mapped SVG file.
        """
        if self.tree is None:
            raise RuntimeError("SVG nicht geladen.\n"
                               "SVG not loaded.")
        try:
            self.tree.write(
                out_path, encoding="utf-8", xml_declaration=True,
                pretty_print=True)
            print(f"Gemappte SVG erfolgreich gespeichert: {out_path}\n"
                  f"Mapped SVG successfully saved: {out_path}")
        except Exception as e:
            print(f"Fehler beim Speichern der gemappten SVG: {e}\n"
                  f"Error saving mapped SVG: {e}")
if __name__ == "__main__":
    # Beispielaufruf gegen die mitgelieferten Daten unter examples/.
    # Aus dem Repository-Wurzelverzeichnis ausführen:
    #     python src/svg_transformer.py
    # Der Konstruktor erwartet vollständige Dateipfade als
    # Schlüsselwort-Argumente. /
    # Example call against the sample data under examples/.
    # Run from the repository root:
    #     python src/svg_transformer.py
    # The constructor expects full file paths as keyword arguments.
    import os

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    examples = os.path.join(repo, "examples")
    out_dir = os.path.join(examples, "output")
    os.makedirs(out_dir, exist_ok=True)

    dxf_filepath = os.path.join(examples, "dxf", "walsdorf.dxf")
    stylesheet_filepath = os.path.join(
        examples, "stylesheets", "wld-accurate_bb.xml")
    svg_filepath = os.path.join(out_dir, "wld-accurate_bb.svg")
    csv_filepath = os.path.join(out_dir, "wld-objects.csv")
    json_filepath = os.path.join(out_dir, "wld-objects.json")

    # Modus 1: DXF-zu-SVG-Transformation (Standard) /
    # Mode 1: DXF-to-SVG transformation (default)
    transformer = SVGTransformer(
        dxf_filepath=dxf_filepath,
        stylesheet_filepath=stylesheet_filepath,
        svg_filepath=svg_filepath,
        csv_filepath=csv_filepath,
        json_filepath=json_filepath,
        mode="dxf")
    transformer.run()

    # Modus 2: SVG direkt aus vorbereiteter JSON-Datei erzeugen. Sinnvoll,
    # wenn nur das Stylesheet geändert wurde und die Geometrie unverändert
    # bleibt. /
    # Mode 2: Generate SVG directly from a prepared JSON file. Useful when
    # only the stylesheet has changed and the geometry stays the same.
    #
    # transformer = SVGTransformer(
    #     stylesheet_filepath=os.path.join(
    #         examples, "stylesheets", "wld-accurate_wb.xml"),
    #     json_filepath=json_filepath,
    #     svg_filepath=os.path.join(out_dir, "wld-accurate_wb.svg"),
    #     mode="json")
    # transformer.run()

    # Modus 3: Farb-Mapping auf ein bestehendes SVG anhand einer CSV.
    # apply_mapping() wird nach dem Laden manuell aufgerufen, da die
    # Farbtabelle als Argument übergeben werden muss. /
    # Mode 3: Colour mapping onto an existing SVG using a CSV.
    # apply_mapping() is called manually after loading, because the colour
    # table has to be passed as an argument.
    #
    # transformer = SVGTransformer(mode="mapping")
    # transformer.load_svg(os.path.join(examples, "prepared",
    #                                   "wld-marker_wb.svg"))
    # transformer.load_csv(
    #     os.path.join(examples, "data", "wld-belegung.csv"),
    #     dtype={"SZd-ID": str, "Datierung": int})
    # gradient = transformer.generate_gradient_color_table(
    #     min_val=1630, max_val=1920, cmap_name="jet", steps=290)
    # transformer.apply_mapping(
    #     id_col="SZd-ID",
    #     value_col="Datierung",
    #     color_table=gradient,
    #     tooltip_cols=["SZd-ID", "Sterbejahr", "epidat"],
    #     url_col="Weblink",
    #     require_tooltip_if_any=True)
    # transformer.save_svg(os.path.join(out_dir, "wld-belegung.svg"))
