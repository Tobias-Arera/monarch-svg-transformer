# SVG-Transformer

**DE** — Transformiert AutoCAD-Zeichnungen (DXF) von Friedhofsplänen in strukturierte SVG-Dateien, deren Elemente im MonArch-System annotierbar sind. Bestehende Pläne lassen sich zusätzlich aus CSV-Tabellen heraus thematisch einfärben.

**EN** — Transforms AutoCAD drawings (DXF) of cemetery plans into structured SVG files whose elements can be annotated in the MonArch system. Existing plans can additionally be colour-coded thematically from CSV tables.

Entwickelt von Tobias Arera-Rütenik, Arbeitsgruppe Bauforschung und Bauerhalt am Kompetenzzentrum Denkmalwissenschaften und Denkmaltechnologien (KDWT) der Otto-Friedrich-Universität Bamberg, im Projekt *Steinerne Zeugen digital* (SZd).

---

## Inhalt / Contents

- [Kontext und Zielstellung](#kontext-und-zielstellung--context-and-objective)
- [Aufbau des Repositorys](#aufbau-des-repositorys--repository-layout)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Die drei Modi](#die-drei-modi--the-three-modes)
- [Konstruktor-Referenz](#konstruktor-referenz--constructor-reference)
- [API-Referenz](#api-referenz--api-reference)
- [Kartierungsbeispiel](#kartierungsbeispiel--mapping-example)
- [Datenformate](#datenformate--data-formats)
- [Fehlerbehandlung](#fehlerbehandlung--error-handling)
- [Einschränkungen](#einschränkungen--limitations)
- [Lizenz und Zitation](#lizenz-und-zitation--licence-and-citation)

**DE** — Der Aufbau der XML-Stylesheets ist separat dokumentiert: **[docs/stylesheet.md](docs/stylesheet.md)**. Die Änderungen gegenüber früheren Ständen stehen im **[CHANGELOG](CHANGELOG.md)**.

**EN** — The structure of the XML stylesheets is documented separately: **[docs/stylesheet.md](docs/stylesheet.md)**. Changes compared to earlier states are recorded in the **[CHANGELOG](CHANGELOG.md)**.

---

## Kontext und Zielstellung / Context and objective

**DE**

Im Projekt SZd werden Punktwolken jüdischer Friedhöfe in 2D-Pläne umgezeichnet. Die Zeichenelemente liegen dabei auf verschiedenen CAD-Layern — Friedhofsmauer, Friedhofsareal, Wege, Bäume, Gebäude und vor allem die einzelnen Grabstätten bzw. Grabmale. Dieses Layerset ist nicht standardisiert und weicht von Zeichnung zu Zeichnung ab.

Entscheidend ist, dass die Zeichnungselemente einer Grabstätte im MonArch-System dem entsprechenden Strukturelement zugewiesen werden können. Die Elemente müssen in der SVG-Datei also eine `id` tragen, die der ID des Strukturelements entspricht. Da sich solche IDs in CAD-Dateien nicht ohne Weiteres setzen lassen, wird neben dem Grabstätten-Polygon ein Bezeichnungsfeld (TEXT oder MTEXT) platziert, dessen Inhalt der ID entspricht. Der Transformer wertet die Nähe des Text-Ankerpunkts zu den Eckpunkten des Polygons aus und überträgt die Bezeichnung als `id` in das SVG.

Weiterhin zu beachten:

- **Nur Elemente auf der obersten Ebene der SVG-Datei sind in MonArch annotierbar.** Die Gruppenstruktur des Stylesheets bildet dies ab.
- Es existieren zwei Darstellungsschemata: hell (weißer Grund, schwarze Linien) und dunkel (dunkelgrauer Grund, weiße Linien), gesteuert über getrennte Stylesheets. Die Dateinamen führen sie als `wb` und `bb`.
- Es existieren zwei Darstellungsarten: `accurate` (jeder Grabstein maßstäblich in tatsächlicher Größe und Form) und `marker` (jeder Grabstein als Kreis-Symbol). Die abstrahierte Variante wird für Kartierungen verwendet, weil die standardisierte Größe eine gleichgewichtige Darstellung der Kriterien erlaubt.

**EN**

In the SZd project, point clouds of Jewish cemeteries are redrawn as 2D plans. The drawing elements are distributed across several CAD layers — cemetery wall, cemetery area, pathways, trees, buildings and, most importantly, the individual graves and grave monuments. This layer set is not standardised and varies between drawings.

The decisive requirement is that the drawing elements of a grave can be assigned to the corresponding structure element in MonArch. Elements must therefore carry an `id` in the SVG file that matches the ID of the structure element. Since such IDs cannot readily be set in CAD files, a label field (TEXT or MTEXT) whose content corresponds to the ID is placed next to the grave polygon. The transformer evaluates the proximity of the text anchor point to the polygon vertices and transfers the label into the SVG as an `id`.

Further points to note:

- **Only elements on the top level of the SVG file can be annotated in MonArch.** The group structure of the stylesheet reflects this.
- Two display schemes exist: light (white background, black lines) and dark (dark grey background, white lines), controlled via separate stylesheets. File names carry them as `wb` and `bb`.
- Two representation types exist: `accurate` (each grave stone to scale in its actual size and shape) and `marker` (each grave stone as a circle symbol). The abstracted variant is used for thematic maps, since the standardised size allows a balanced visual weighting of criteria.

---

## Aufbau des Repositorys / Repository layout

```
├── src/
│   └── svg_transformer.py        Der Transformer / the transformer
├── schema/
│   ├── stylesheet.xsd            XML Schema 1.0, überall verwendbar
│   └── stylesheet-1.1.xsd        XML Schema 1.1, strengere Prüfungen
├── docs/
│   └── stylesheet.md             Referenz der Stylesheet-Struktur
├── examples/
│   ├── dxf/walsdorf.dxf          Beispielzeichnung / sample drawing
│   ├── stylesheets/*.xml         Vier Darstellungsvarianten / four variants
│   ├── data/wld-belegung.csv     Kartierungsdaten / mapping data
│   ├── prepared/                 Eingaben für die Modi json und mapping
│   ├── output/                   Zielverzeichnis der Läufe / output directory
│   └── LICENSE                   CC BY-SA 4.0 für die Beispieldaten
├── notebooks/
│   └── svg-transformer-demo.ipynb  Alle drei Modi zum Nachvollziehen
├── CHANGELOG.md
├── CITATION.cff
├── LICENSE                       MIT für Code und Schemata
└── requirements.txt
```

---

## Installation

**DE** — Python 3.9 oder neuer.

**EN** — Python 3.9 or later.

```bash
git clone https://github.com/Tobias-Arera/monarch-svg-transformer.git
cd monarch-svg-transformer
pip install -r requirements.txt
```

| Paket / Package | Verwendung / Purpose                                                                  |
| --------------- | ------------------------------------------------------------------------------------- |
| `ezdxf`         | DXF einlesen, Layer und Entities abfragen / reading DXF, querying layers and entities |
| `lxml`          | SVG erzeugen und manipulieren (XPath) / generating and manipulating SVG (XPath)       |
| `pandas`        | Objektlisten und Mapping-CSVs / object lists and mapping CSVs                         |
| `matplotlib`    | Farbverläufe für den Kartierungsmodus / colour gradients for mapping mode             |

**DE** — Der Transformer ist ein einzelnes Modul ohne Paketinstallation. Entweder liegt `svg_transformer.py` neben dem Aufrufskript, oder `src/` wird dem Suchpfad hinzugefügt:

**EN** — The transformer is a single module without package installation. Either place `svg_transformer.py` next to the calling script, or add `src/` to the search path:

```python
import sys
sys.path.insert(0, "src")

from svg_transformer import SVGTransformer
```

---

## Quickstart

**DE** — Vollständige Transformation der Beispielzeichnung in einen SVG-Plan, inklusive CSV- und JSON-Export. Alle Pfade sind relativ zum Repository-Wurzelverzeichnis:

**EN** — Complete transformation of the sample drawing into an SVG plan, including CSV and JSON export. All paths are relative to the repository root:

```python
import sys
sys.path.insert(0, "src")

from svg_transformer import SVGTransformer

transformer = SVGTransformer(
    dxf_filepath="examples/dxf/walsdorf.dxf",
    stylesheet_filepath="examples/stylesheets/wld-accurate_bb.xml",
    svg_filepath="examples/output/wld-accurate_bb.svg",
    csv_filepath="examples/output/wld-objects.csv",
    json_filepath="examples/output/wld-objects.json",
    mode="dxf",
)

transformer.run()
```

**DE** — Dasselbe direkt von der Kommandozeile, mit dem Beispielaufruf am Ende des Moduls:

**EN** — The same directly from the command line, using the example call at the end of the module:

```bash
python src/svg_transformer.py
```

**DE** — Alle Pfade werden als vollständige Dateipfade übergeben; es gibt keine getrennten Verzeichnis- und Dateinamen-Parameter.

**EN** — All paths are passed as full file paths; there are no separate directory and file-name parameters.

---

## Die drei Modi / The three modes

**DE** — Der Modus wird über den Parameter `mode` gesetzt und steuert, welche Schritte `run()` ausführt. Das Notebook unter `notebooks/` führt alle drei nacheinander vor.

**EN** — The mode is set via the `mode` parameter and controls which steps `run()` executes. The notebook under `notebooks/` demonstrates all three in sequence.

### `mode="dxf"` (Standard / default)

**DE** — Vollständige Transformation: DXF + Stylesheet → SVG + JSON + CSV.

**EN** — Full transformation: DXF + stylesheet → SVG + JSON + CSV.

```
parse_stylesheet()      XML-Stylesheet laden, map_id ermitteln
        ↓
parse_dxf()             DXF laden, Modelspace initialisieren
        ↓
find_reference_frame()  Referenzrahmen, Ursprung, Drehwinkel, Maße bestimmen
        ↓
extract_objects()       Polylinien, Kreise und Bezeichnungsfelder auslesen
        ↓
assign_numbers()        Bezeichnungen den Polygonen als SZd-ID zuordnen
        ↓
generate_svg()          SVG mit Gruppen, Pfaden, Kreisen und Plankopf schreiben
        ↓
export_json()           Objekte + Geometrie-Metadaten sichern
        ↓
export_csv()            Objektliste als CSV sichern
```

**Benötigte Pfade / required paths:** `dxf_filepath`, `stylesheet_filepath`, `svg_filepath`, `csv_filepath`, `json_filepath`

### `mode="json"`

**DE** — SVG direkt aus einer zuvor exportierten JSON-Datei erzeugen. Kein DXF-Zugriff, damit deutlich schneller. Sinnvoll, wenn nur das Stylesheet geändert wird — Farben, Strichstärken, Plankopf — und die Geometrie unverändert bleibt.

**EN** — Generates the SVG directly from a previously exported JSON file. No DXF access, therefore much faster. Useful when only the stylesheet changes — colours, stroke widths, title block — while the geometry stays the same.

```
parse_stylesheet() → load_json() → generate_svg()
```

**Benötigte Pfade / required paths:** `stylesheet_filepath`, `json_filepath`, `svg_filepath`

```python
transformer = SVGTransformer(
    stylesheet_filepath="examples/stylesheets/wld-marker_wb.xml",
    json_filepath="examples/prepared/walsdorf-objects.json",
    svg_filepath="examples/output/wld-marker_wb.svg",
    mode="json",
)
transformer.run()
```

### `mode="mapping"`

**DE** — Thematische Einfärbung eines bestehenden SVG-Plans anhand einer CSV-Tabelle. `run()` lädt hier nur SVG und CSV; das eigentliche Mapping wird anschließend mit `apply_mapping()` ausgelöst, weil die Farbtabelle als Argument übergeben werden muss.

**EN** — Thematic colour-coding of an existing SVG plan from a CSV table. Here `run()` only loads SVG and CSV; the actual mapping is then triggered via `apply_mapping()`, because the colour table must be passed as an argument.

```
load_svg() → load_csv() → apply_mapping() → save_svg()
```

**Benötigte Pfade / required paths:** `svg_filepath`, `csv_filepath`

**DE** — In der Praxis wird `run()` in diesem Modus meist übersprungen und die Methoden werden direkt aufgerufen (siehe [Kartierungsbeispiel](#kartierungsbeispiel--mapping-example)).

**EN** — In practice, `run()` is usually skipped in this mode and the methods are called directly (see [mapping example](#kartierungsbeispiel--mapping-example)).

---

## Konstruktor-Referenz / Constructor reference

```python
SVGTransformer(
    dxf_filepath=None,
    stylesheet_filepath=None,
    svg_filepath=None,
    csv_filepath=None,
    json_filepath=None,
    mode="dxf",
)
```

| Parameter             | Typ / Type | Default |  `dxf`  | `json`  | `mapping` | Bedeutung / Meaning                                                |
| --------------------- | ---------- | ------- | :-----: | :-----: | :-------: | ------------------------------------------------------------------ |
| `dxf_filepath`        | `str`      | `None`  |    ✔    |    –    |     –     | Pfad zur DXF-Zeichnung / path to the DXF drawing                   |
| `stylesheet_filepath` | `str`      | `None`  |    ✔    |    ✔    |     –     | Pfad zum XML-Stylesheet / path to the XML stylesheet               |
| `svg_filepath`        | `str`      | `None`  | ✔ (out) | ✔ (out) |  ✔ (in)   | Ziel- bzw. Quell-SVG / target resp. source SVG                     |
| `csv_filepath`        | `str`      | `None`  | ✔ (out) |    –    |  ✔ (in)   | Objektliste bzw. Mapping-Tabelle / object list resp. mapping table |
| `json_filepath`       | `str`      | `None`  | ✔ (out) | ✔ (in)  |     –     | Objekt- und Metadaten-Cache / object and metadata cache            |
| `mode`                | `str`      | `"dxf"` |         |         |           | `"dxf"`, `"json"` oder / or `"mapping"`                            |

**DE** — Wichtige Instanzattribute nach dem Lauf:

**EN** — Key instance attributes after the run:

| Attribut / Attribute | Inhalt / Content |
|---|---|
| `map_id` | Dreibuchstabiges Friedhofskürzel aus dem Stylesheet, z. B. `"wld"` / three-letter cemetery code from the stylesheet |
| `obj_list` | Liste der Zeichnungsobjekte als Dictionaries / list of drawing objects as dictionaries |
| `decl_list` | Liste der ausgelesenen Bezeichnungsfelder / list of extracted label fields |
| `dxf_width`, `dxf_height` | Maße des Referenzrahmens in DXF-Einheiten / dimensions of the reference frame in DXF units |
| `ref_origin`, `ref_angle` | Ursprung und Drehwinkel (Radiant) / origin and rotation angle (radians) |
| `df` | Geladene Mapping-CSV als `pandas.DataFrame` / loaded mapping CSV as a `pandas.DataFrame` |
| `tree`, `root` | Geladener SVG-Baum im Mapping-Modus / loaded SVG tree in mapping mode |

---

## API-Referenz / API reference

### Ablaufsteuerung / Workflow control

| Methode / Method | Beschreibung / Description |
|---|---|
| `run()` | Führt die dem Modus entsprechende Pipeline aus / runs the pipeline matching the mode |

### Einlesen / Parsing

| Methode / Method | Beschreibung / Description |
|---|---|
| `parse_stylesheet()` | Lädt das XML-Stylesheet, setzt `stylesheet` und `map_id` / loads the XML stylesheet |
| `parse_dxf()` | Lädt die DXF-Datei und initialisiert `msp` (Modelspace) / loads the DXF file and initialises the modelspace |
| `find_reference_frame()` | Bestimmt Ursprung, Drehwinkel und Maße aus dem Referenzrahmen-Layer / determines origin, rotation angle and dimensions |

### Objektextraktion / Object extraction

| Methode / Method | Beschreibung / Description |
|---|---|
| `get_lwpolylines(layername)` | Liest alle LWPOLYLINE eines Layers / reads all LWPOLYLINE entities of a layer |
| `get_circles(layername)` | Liest alle CIRCLE eines Layers / reads all CIRCLE entities of a layer |
| `get_texts(layername)` | Liest TEXT-Bezeichnungsfelder und zerlegt sie in Sektor, Reihe, Platz, Zusatz / reads TEXT labels and splits them |
| `get_mtexts(layername)` | Wie `get_texts()`, aber für MTEXT (mit vorangestelltem Formatierungs-String) / same for MTEXT |
| `extract_objects()` | Ruft die vier Getter für alle im Stylesheet deklarierten Layer auf / calls the four getters for all layers declared in the stylesheet |
| `assign_numbers()` | Ordnet jedem aktiven Polygon über das Latenzrechteck genau ein Bezeichnungsfeld zu und setzt `SZd-ID` / assigns exactly one label field per active polygon |

### Geometrie / Geometry

| Methode / Method | Beschreibung / Description |
|---|---|
| `rotate_and_translate(x, y, origin, angle)` | Statisch. Translation zum Ursprung plus Rotation / static; translation to origin plus rotation |
| `convert_coords(vert, svg_width, svg_height, dxf_width, dxf_height)` | DXF-Koordinatenpaar → SVG-Koordinatenpaar / DXF coordinate pair → SVG coordinate pair |
| `d_string(vert_list, …, closed)` | Erzeugt den `d`-String eines SVG-Pfads / builds the `d` string of an SVG path |

### SVG-Erzeugung / SVG generation

| Methode / Method | Beschreibung / Description |
|---|---|
| `generate_svg()` | Baut das SVG: Gruppen aus `svg_group_sequence`, Elemente je Layer, Plankopf; schreibt die Datei / builds and writes the SVG |
| `geom_type(…)` | Erzeugt `<path>` oder `<circle>` je nach Entity und `marker-type` / creates `<path>` or `<circle>` |
| `make_path(…)` | Erzeugt alle Elemente eines Layers in einer Gruppe / creates all elements of a layer within a group |
| `set_attrib(elem, xpath)` | Überträgt Style-Kindelemente des Stylesheets als SVG-Attribute / transfers stylesheet style children as SVG attributes |
| `set_id(o, elem, obj_id_template, obj_counter)` | Setzt `id` — die `SZd-ID`, falls vorhanden, sonst `<map_id>-<group>-<n>` / sets the `id` |
| `add_svg_elements(title_block, svg_height_original)` | Fügt die Elemente der `svg_element_sequence` in den Plankopf ein / inserts the elements of the `svg_element_sequence` |
| `process_north_arrow`, `process_scale_bar`, `process_plan_header`, `process_standard_element`, `create_scale_labels` | Spezialbehandlung einzelner Plankopf-Gruppen / special handling of individual title-block groups |

### Export und Cache / Export and cache

| Methode / Method | Beschreibung / Description |
|---|---|
| `export_csv()` | Schreibt `obj_list` als semikolongetrennte CSV / writes `obj_list` as a semicolon-separated CSV |
| `export_json(filepath=None)` | Schreibt Objekte und Geometrie-Metadaten als JSON / writes objects and geometry metadata as JSON |
| `load_json(filepath=None)` | Lädt Objekte und Metadaten aus einer JSON-Datei / loads objects and metadata from a JSON file |

### Kartierungsmodus / Mapping mode

| Methode / Method | Beschreibung / Description |
|---|---|
| `set_mapping_inputs(svg_path, csv_path)` | Setzt beide Pfade nachträglich / sets both paths after construction |
| `load_svg(svg_path=None)` | Lädt das SVG in `tree` / `root` / loads the SVG into `tree` / `root` |
| `load_csv(csv_path=None, dtype=None)` | Lädt die CSV (Trennzeichen `;`). `dtype` erzwingt Spaltentypen; `int` wird automatisch zu `pd.Int64Dtype()`, damit Leerzellen zulässig bleiben / loads the CSV; `int` is auto-converted to `pd.Int64Dtype()` so empty cells remain valid |
| `generate_gradient_color_table(min_val, max_val, cmap_name="RdYlBu_r", steps=100)` | Erzeugt `{Wert: Hexfarbe}` über eine matplotlib-Colormap / builds `{value: hex colour}` from a matplotlib colormap |
| `apply_mapping(…)` | Färbt Elemente, ergänzt Tooltips und optional Links / colours elements, adds tooltips and optional links |
| `save_svg(out_path)` | Schreibt das gemappte SVG / writes the mapped SVG |

#### `apply_mapping()` im Detail / in detail

```python
apply_mapping(
    id_col="SZd-ID",
    value_col="mapping",
    color_table=None,
    tooltip_cols=None,
    url_col=None,
    require_tooltip_if_any=True,
)
```

| Parameter | Bedeutung / Meaning |
|---|---|
| `id_col` | CSV-Spalte mit den SVG-Element-IDs / CSV column holding the SVG element IDs |
| `value_col` | CSV-Spalte mit den zu kartierenden Werten / CSV column holding the values to map |
| `color_table` | Pflicht. Dictionary Wert → Hexfarbe / mandatory; dictionary value → hex colour |
| `tooltip_cols` | Spalten für den Tooltip; ohne Angabe `[id_col, value_col]` / columns for the tooltip; defaults to `[id_col, value_col]` |
| `url_col` | Spalte mit URLs. Vorhandene Werte hüllen das Element in `<a href … target="_blank">` / column with URLs; wraps the element in an anchor |
| `require_tooltip_if_any` | `True`: Zeilen ohne Mapping-Wert werden dennoch für Tooltip und Link verarbeitet. `False`: solche Zeilen werden übersprungen / `True`: rows without a mapping value are still processed for tooltip and link; `False`: such rows are skipped |

**DE** — Verhalten im Detail:

- Die Farbe wird als `style="fill: …"` gesetzt; bestehende Style-Deklarationen bleiben erhalten.
- Numerische Werte werden zu `int` normalisiert; liegt ein Wert außerhalb der Farbtabelle, wird auf deren kleinsten bzw. größten numerischen Schlüssel geklemmt.
- Fehlt eine ID im SVG, wird eine Warnung ausgegeben und die Zeile übersprungen — der Lauf bricht nicht ab.
- Ist `tooltip_cols` gesetzt, wird zusätzlich einmalig ein `<script>`-Block mit einem JavaScript-Tooltipsystem in das SVG eingefügt.

**EN** — Behaviour in detail:

- The colour is set as `style="fill: …"`; existing style declarations are preserved.
- Numeric values are normalised to `int`; values outside the colour table are clipped to its smallest resp. largest numeric key.
- If an ID is missing in the SVG, a warning is printed and the row is skipped — the run does not abort.
- If `tooltip_cols` is set, a `<script>` block with a JavaScript tooltip system is additionally injected once into the SVG.

---

## Kartierungsbeispiel / Mapping example

**DE** — Datierung der Grabsteine als Farbverlauf, mit Tooltips und Links zur epidat-Datenbank:

**EN** — Dating of the grave stones as a colour gradient, with tooltips and links to the epidat database:

```python
import sys
sys.path.insert(0, "src")

from svg_transformer import SVGTransformer

transformer = SVGTransformer(mode="mapping")

transformer.load_svg("examples/prepared/wld-marker_wb.svg")
transformer.load_csv(
    "examples/data/wld-belegung.csv",
    dtype={"SZd-ID": str, "Datierung": int},
)

gradient = transformer.generate_gradient_color_table(
    min_val=1630,
    max_val=1920,
    cmap_name="jet",
    steps=290,
)

transformer.apply_mapping(
    id_col="SZd-ID",
    value_col="Datierung",
    color_table=gradient,
    tooltip_cols=["SZd-ID", "Sterbejahr", "epidat"],
    url_col="Weblink",
    require_tooltip_if_any=True,
)

transformer.save_svg("examples/output/wld-belegung.svg")
```

**DE** — Für diskrete Kategorien statt eines Verlaufs genügt eine handgeschriebene Farbtabelle:

**EN** — For discrete categories instead of a gradient, a hand-written colour table is sufficient:

```python
color_table = {
    1: "#1b9e77",   # erhalten / preserved
    2: "#d95f02",   # beschädigt / damaged
    3: "#7570b3",   # Fragment / fragment
}

transformer.apply_mapping(
    value_col="Zustand",
    color_table=color_table,
    tooltip_cols=["SZd-ID", "Zustand", "Bemerkung"],
)
```

---

## Datenformate / Data formats

### Objekt-Dictionary / object dictionary

**DE** — Jedes Element in `obj_list` ist ein Dictionary mit folgenden Schlüsseln:

**EN** — Every element in `obj_list` is a dictionary with the following keys:

| Schlüssel / Key | Typ / Type | Inhalt / Content |
|---|---|---|
| `layer` | `str` | Name des DXF-Layers / name of the DXF layer |
| `entity` | `str` | `"LWPOLYLINE"` oder / or `"CIRCLE"` |
| `is_closed` | `bool` | Nur bei LWPOLYLINE / LWPOLYLINE only |
| `verts` | `list[tuple]` | Stützpunkte in DXF-Koordinaten / vertices in DXF coordinates |
| `center` | `tuple` | Mittelpunkt der Bounding-Box bzw. Kreismittelpunkt / bounding-box centre resp. circle centre |
| `SZd-ID` | `str` | Zugeordnete Grabstätten-ID; nur bei aktiven Elementen / assigned grave ID; active elements only |

### Bezeichnungsfeld-Dictionary / label field dictionary

**DE** — Jedes Element in `decl_list` (aus TEXT bzw. MTEXT):

**EN** — Every element in `decl_list` (from TEXT resp. MTEXT):

| Schlüssel / Key | Beispiel / Example | Bemerkung / Note |
|---|---|---|
| `Friedhof` | `wld` | Friedhofskürzel aus `map_id` / cemetery code from `map_id` |
| `Sektor` | `01` | Nur bei TEXT / TEXT only |
| `Reihe` | `002` | |
| `Platz` | `003` | |
| `Zusatz` | `00` | Puffer; `00`, wenn in der Zeichnung weggelassen / buffer; `00` if omitted in the drawing |
| `Nummer` | `wld-01.002.003-00` | Zusammengesetzte ID / composed ID |
| `Anker` | `(x, y)` | Einfügepunkt des Textes / insertion point of the text |

**DE** — Zur Zeichenlänge: `get_texts()` erwartet 10 Zeichen (ohne Puffer) oder 13 Zeichen (mit Puffer); `get_mtexts()` erwartet 25 Zeichen und sliced von hinten, weil MTEXT-Inhalte nach dem Auslesen mit ezdxf einen vorangestellten Formatierungs-String enthalten. Weicht die Zeichenlänge ab, bleibt `Nummer` leer, und das Feld wird bei der Zuordnung übersprungen und gemeldet.

**EN** — On character length: `get_texts()` expects 10 characters (without buffer) or 13 characters (with buffer); `get_mtexts()` expects 25 characters and slices from the end, because MTEXT content carries a leading formatting string after being read with ezdxf. If the length deviates, `Nummer` stays empty and the field is skipped during assignment and reported.

### JSON

```json
{
  "meta": {
    "dxf_width": 193.0564759676517,
    "dxf_height": 76.65992703258098,
    "ref_origin": [-72.24777855019556, 117.4231307654648],
    "ref_angle_deg": -5.183288001504192
  },
  "objects": [ /* obj_list */ ]
}
```

### Mapping-CSV

**DE** — Semikolon als Trennzeichen; `""`, `NA` und `N/A` gelten als Leerwerte. Erforderlich sind eine ID-Spalte (Standardname `SZd-ID`) und eine Wertespalte (Standardname `mapping`). Weitere Spalten können als Tooltip- oder URL-Quelle dienen.

**EN** — Semicolon as separator; `""`, `NA` and `N/A` are treated as empty values. An ID column (default name `SZd-ID`) and a value column (default name `mapping`) are required. Additional columns may serve as tooltip or URL sources.

```csv
SZd-ID;Datierung;Sterbejahr;epidat;epidat_;Weblink
wld-01.001.001-00;1825;1825?;wdf-754;wdf-0754;http://www.steinheim-institut.de/cgi-bin/epidat?id=wdf-754
```

---

## Fehlerbehandlung / Error handling

**DE** — Fehlerhafte Eingaben lösen Ausnahmen aus. In Jupyter überlebt der Kernel damit einen Fehlversuch, und die Meldung erscheint im Traceback.

**EN** — Faulty input raises exceptions. In Jupyter the kernel survives a failed attempt, and the message appears in the traceback.

| Ausnahme / Exception | Ausgelöst bei / Raised on |
|---|---|
| `SVGTransformerError` | Basisklasse; direkt bei nicht ladbarem SVG oder CSV im Mapping-Modus / base class; used directly for unloadable SVG or CSV in mapping mode |
| `StylesheetError` | Stylesheet nicht lesbar, fehlendes `map_id`, kein oder mehr als ein `reference_frame`, fehlendes `marker-type`, fehlendes `marker-size` bei `marker-type="circle"` / stylesheet unreadable, missing `map_id`, no or more than one `reference_frame`, missing `marker-type`, missing `marker-size` with `marker-type="circle"` |
| `DXFError` | DXF nicht ladbar; Referenzrahmen-Layer ohne genau ein Rechteck und genau einen Punkt / DXF unloadable; reference frame layer without exactly one rectangle and exactly one point |

```python
from svg_transformer import SVGTransformer, StylesheetError, DXFError

try:
    transformer.run()
except StylesheetError as e:
    print("Stylesheet prüfen:", e)
except DXFError as e:
    print("CAD-Zeichnung prüfen:", e)
```

**DE** — Alle Meldungen sind zweisprachig und nennen die betroffene Datei bzw. den betroffenen Layer:

**EN** — All messages are bilingual and name the file resp. layer concerned:

```
StylesheetError: Layer 'Neue Steine Fragmente': marker-type='circle' erfordert die Angabe marker-size.
                 Layer 'Neue Steine Fragmente': marker-type='circle' requires the attribute marker-size.
```

---

## Einschränkungen / Limitations

**DE**

- **Nur geradlinige Geometrien.** Polylinien in der DXF-Datei dürfen ausschließlich gerade Liniensegmente enthalten; Bögen werden nicht ausgewertet.
- **Genau ein Bezeichnungsfeld pro Grabstätten-Polygon.** `assign_numbers()` meldet am Ende, wie viele Bezeichnungen eindeutig zugeordnet, mehrdeutig oder übersprungen wurden. Abweichungen deuten auf ein zu großes oder zu kleines Latenzrechteck hin.
- **Referenzrahmen-Layer.** Er muss genau ein Rechteck (LWPOLYLINE mit vier Punkten) und genau einen Punkt (POINT) im gewünschten Nullpunkt enthalten.
- **Quadratischer Rahmen bei 45°.** In diesem Sonderfall fragt `find_reference_frame()` interaktiv über `input()` nach der Drehrichtung — im Batchbetrieb blockiert das.
- **Ein Latenzrechteck für alle Deklarationen.** `assign_numbers()` liest die vier Offsets ohne Layer-Bezug und verwendet stets die erste `reference_declaration`. Bei mehreren Deklarationen sollten die Offsets identisch sein.
- **Keine Schema-Validierung zur Laufzeit.** Der Transformer prüft das Stylesheet nicht gegen das Schema, sondern greift per XPath auf die erwarteten Knoten zu. Pflichtangaben werden punktuell geprüft; eine vollständige Prüfung ersetzt das nicht.

**EN**

- **Straight-line geometries only.** Polylines in the DXF file may contain straight segments only; arcs are not evaluated.
- **Exactly one label field per grave polygon.** `assign_numbers()` reports at the end how many labels were uniquely assigned, ambiguous or skipped. Deviations indicate a latency rectangle that is too large or too small.
- **Reference frame layer.** It must contain exactly one rectangle (LWPOLYLINE with four vertices) and exactly one point (POINT) at the intended origin.
- **Square frame at 45°.** In this edge case `find_reference_frame()` asks interactively via `input()` for the direction of rotation — which blocks in batch operation.
- **One latency rectangle for all declarations.** `assign_numbers()` reads the four offsets without a layer reference and always uses the first `reference_declaration`. With several declarations, the offsets should be identical.
- **No schema validation at runtime.** The transformer does not check the stylesheet against the schema but accesses the expected nodes via XPath. Mandatory entries are checked selectively; this does not replace full validation.

---

## Lizenz und Zitation / Licence and citation

**DE**

- **Code und Schemata** stehen unter der [MIT-Lizenz](LICENSE).
- **Beispieldaten** unter `examples/` stehen unter [CC BY-SA 4.0](examples/LICENSE); Namensnennung: Lea Puglisi, Fabio Vohl, Tobias Arera-Rütenik (KDWT, Otto-Friedrich-Universität Bamberg, 2025).

**EN**

- **Code and schemas** are licensed under the [MIT licence](LICENSE).
- **Sample data** under `examples/` is licensed under [CC BY-SA 4.0](examples/LICENSE); attribution: Lea Puglisi, Fabio Vohl, Tobias Arera-Rütenik (KDWT, University of Bamberg, 2025).

**DE** — Zur Zitation der Software siehe [CITATION.cff](CITATION.cff). Die epigraphischen Angaben in `examples/data/wld-belegung.csv` verweisen auf die Datenbank [epidat](https://www.steinheim-institut.de/) des Salomon-Ludwig-Steinheim-Instituts.

**EN** — For citing the software see [CITATION.cff](CITATION.cff). The epigraphic entries in `examples/data/wld-belegung.csv` refer to the [epidat](https://www.steinheim-institut.de/) database of the Salomon Ludwig Steinheim Institute.
