# Stylesheet-Referenz / Stylesheet reference

**DE** — Das XML-Stylesheet liefert sämtliche Eingaben für den Transformationsvorgang: die Gruppenstruktur der SVG-Datei, die Darstellungs-Styles, die Zuordnung der DXF-Layer zu Gruppen und Styles, die Referenzen für Rahmen und Bezeichnungsfelder sowie die statischen Elemente des Plankopfs. Validiert wird gegen **`schema/stylesheet.xsd`** (XML Schema 1.0); strengere, bedingte Regeln stehen in **`schema/stylesheet-1.1.xsd`** (XML Schema 1.1).

**EN** — The XML stylesheet supplies all inputs for the transformation: the group structure of the SVG file, the display styles, the assignment of DXF layers to groups and styles, the references for frame and label fields, and the static elements of the title block. It is validated against **`schema/stylesheet.xsd`** (XML Schema 1.0); stricter, conditional rules are held in **`schema/stylesheet-1.1.xsd`** (XML Schema 1.1).

Siehe auch / see also: [../README.md](../README.md)

---

## Elementbaum / Element tree

```
MonArch_stylesheet          @class @svg_width @map_id @set_aks
├── svg_group_sequence
│   ├── background-group*   @group_name
│   └── active-group        @group_name
├── svg_style_sequence
│   └── svg_style+          @style_name
│       ├── fill / fill-opacity / stroke / stroke-width
│       ├── stroke-dasharray / stroke-miterlimit / stroke-linejoin
│       └── font-family / font-size
├── dxf_layer_sequence
│   └── layer+              @layer_name @map_to @style_ref
│                           @marker-type @marker-size @marker_array
├── dxf_references
│   ├── reference_frame     @layer_name
│   └── reference_declaration*  @layer_name
│       └── offset{4}       @offset_vert
└── svg_element_sequence?   @scale_factor
    └── svg_element*        @group_name @style_ref @map_to
                            @translate-x @translate-y
        ├── max_scale?
        └── (path | circle | rect | tspan)*
```

`+` = mindestens einmal / at least once · `*` = beliebig oft / any number · `?` = optional · `{4}` = genau viermal / exactly four times

---

## Wurzelelement / Root element

### `MonArch_stylesheet`

| Attribut / Attribute | Typ / Type | Pflicht / Required | Bedeutung / Meaning |
|---|---|:--:|---|
| `class` | `accurate` \| `simplified` \| `marker` | ✔ | Darstellungsart. `accurate`: maßstäbliche Grabsteinumrisse. `marker`: Kreissymbole für Kartierungen / representation type |
| `svg_width` | `int` | ✔ | Breite des erzeugten SVG in Pixeln. Die Höhe ergibt sich aus dem Seitenverhältnis des Referenzrahmens plus 100 px für den Plankopf / width of the generated SVG in pixels; height derives from the reference frame ratio plus 100 px for the title block |
| `map_id` | `[a-z]{3}` | ✔ | Dreibuchstabiges Friedhofskürzel, z. B. `wld`. Wird für Grabstätten-IDs und die `id` des SVG-Wurzelelements verwendet. Seit 2026-08-12 verpflichtend, da der Transformer es zwingend benötigt / three-letter cemetery code; mandatory since 2026-08-12, as the transformer strictly requires it |
| `set_aks` | `boolean` | – | Reserviert; wird vom Transformer nicht ausgewertet / reserved; not evaluated by the transformer |

**DE** — Konvention der Dateinamen: `<map_id>-<class>_<schema>_<datum>.xml`, wobei `<schema>` für `wb` (weißer Grund / helles Schema) oder `bb` (schwarzer Grund / dunkles Schema) steht — etwa `wld-accurate_bb.xml`.

**EN** — File-name convention: `<map_id>-<class>_<scheme>_<date>.xml`, where `<scheme>` is `wb` (white background / light scheme) or `bb` (black background / dark scheme) — e.g. `wld-accurate_bb.xml`.

---

## `svg_group_sequence`

**DE** — Definiert die Gruppen (`<g>`) der SVG-Datei in Zeichenreihenfolge: die zuerst genannte Gruppe liegt hinten. Jede Gruppe wird als direktes Kind des SVG-Wurzelelements angelegt, wodurch die enthaltenen Elemente auf der obersten Ebene liegen und in MonArch annotierbar sind.

**EN** — Defines the SVG groups (`<g>`) in drawing order: the first group listed lies at the back. Each group is created as a direct child of the SVG root element, so the contained elements sit on the top level and can be annotated in MonArch.

| Element | Attribut / Attribute | Bedeutung / Meaning |
|---|---|---|
| `background-group` | `group_name` (ID, Pflicht) | Hintergrundgruppe, beliebig viele / background group, any number |
| `active-group` | `group_name` (ID, Pflicht) | Genau eine. Enthält die annotierbaren Grabstätten-Elemente / exactly one; holds the annotatable grave elements |

**DE** — Der Gruppenname `title-block` ist reserviert: Diese Gruppe wird stets zuerst erzeugt und nimmt die Elemente der `svg_element_sequence` auf.

**EN** — The group name `title-block` is reserved: this group is always created first and receives the elements of the `svg_element_sequence`.

```xml
<svg_group_sequence>
    <background-group group_name="title-block"/>
    <background-group group_name="area"/>
    <background-group group_name="wall"/>
    <background-group group_name="pathway"/>
    <background-group group_name="structures"/>
    <background-group group_name="enframing"/>
    <active-group group_name="active_element"/>
</svg_group_sequence>
```

---

## `svg_style_sequence`

**DE** — Sammlung benannter Styles. Die Kindelemente eines `svg_style` werden eins zu eins als SVG-Präsentationsattribute auf das jeweilige Element übertragen: Der Tag-Name wird zum Attributnamen, der Textinhalt zum Attributwert.

**EN** — Collection of named styles. The child elements of an `svg_style` are transferred one-to-one as SVG presentation attributes: the tag name becomes the attribute name, the text content the attribute value.

| Element | Typ / Type | Werte / Values |
|---|---|---|
| `fill` | Hexwert oder Schlüsselwort / hex or keyword | `#RRGGBB`, `#RGB`, `none`, `inherit`, `currentColor` |
| `fill-opacity` | `decimal` | `0`–`1` |
| `stroke` | Hexwert oder Schlüsselwort / hex or keyword | `#RRGGBB`, `#RGB`, `none`, `inherit`, `currentColor` |
| `stroke-width` | `decimal` ≥ 0 | z. B. / e.g. `0.25` |
| `stroke-dasharray` | `string` | z. B. / e.g. `2,2` |
| `stroke-miterlimit` | `decimal` ≥ 1 oder / or `inherit` | Veraltet zugelassen: `miter`, `bevel`, `round` — gehören zu `stroke-linejoin` / deprecated but permitted: they belong to `stroke-linejoin` |
| `stroke-linejoin` | Enum | `miter` \| `bevel` \| `round` \| `inherit` |
| `font-family` | `string` | Default `Tahoma, Tahoma` |
| `font-size` | `decimal` | |

**DE** — Die Reihenfolge der Kindelemente ist durch das Schema festgelegt (siehe `style_group` in der XSD) und muss eingehalten werden; jedes Element darf höchstens einmal vorkommen. `style_name` ist vom Typ `xs:ID` und muss dokumentweit eindeutig sein.

**EN** — The order of the child elements is fixed by the schema (see `style_group` in the XSD) and must be observed; each element may appear at most once. `style_name` is of type `xs:ID` and must be unique across the document.

```xml
<svg_style_sequence>
    <svg_style style_name="style_pathway">
        <fill>none</fill>
        <stroke>#000000</stroke>
        <stroke-width>0.35</stroke-width>
        <stroke-dasharray>2,2</stroke-dasharray>
        <stroke-miterlimit>round</stroke-miterlimit>
        <stroke-linejoin>round</stroke-linejoin>
    </svg_style>
    <svg_style style_name="style_active_element">
        <fill>#FFFFFF</fill>
        <stroke>#000000</stroke>
        <stroke-width>0.25</stroke-width>
    </svg_style>
</svg_style_sequence>
```

**DE** — Hier liegt der Unterschied zwischen hellem und dunklem Schema: Für das helle Schema transparente SVGs mit schwarzen Linien, für das dunkle Schema weiße Linien. Alles Übrige bleibt identisch.

**EN** — This is where light and dark schemes differ: transparent SVGs with black lines for the light scheme, white lines for the dark one. Everything else stays identical.

---

## `dxf_layer_sequence`

**DE** — Ordnet die Layer der DXF-Zeichnung den SVG-Gruppen und Styles zu. Da das Layerset nicht standardisiert ist, ist dieser Abschnitt für jede Zeichnung anzupassen. Layer, die hier nicht aufgeführt sind, werden nicht übernommen.

**EN** — Maps the DXF layers to SVG groups and styles. Since the layer set is not standardised, this section must be adapted for every drawing. Layers not listed here are not transferred.

| Attribut / Attribute | Typ / Type | Pflicht / Required | Bedeutung / Meaning |
|---|---|:--:|---|
| `layer_name` | `string` | ✔ | Exakter Layername in der DXF-Datei / exact layer name in the DXF file |
| `map_to` | `IDREF` | ✔ | `group_name` der Zielgruppe / `group_name` of the target group |
| `style_ref` | `IDREF` | ✔ | `style_name` des zu verwendenden Styles / `style_name` of the style to use |
| `marker-type` | `path` \| `circle` \| `array` | ✔ | Geometrieform im SVG. `path`: Polygon übernehmen. `circle`: durch Kreis ersetzen. Ohne diese Angabe ist nicht entscheidbar, welches Element entstehen soll; ein Vorgabewert wäre eine Unterstellung / geometry form in the SVG; without it there is no deciding which element to produce |
| `marker-size` | `float` | (✔) | Radius bei `marker-type="circle"`. Im Schema optional, weil für `path`-Layer bedeutungslos; bei `circle` zwingend. In XSD 1.0 nicht ausdrückbar — geprüft von `schema/stylesheet-1.1.xsd` und vom Transformer / optional in the schema because meaningless for `path` layers, mandatory with `circle`; not expressible in XSD 1.0 — checked by `schema/stylesheet-1.1.xsd` and by the transformer |
| `marker_array` | `string` | – | Reserviert für `marker-type="array"` / reserved for `marker-type="array"` |

**DE** — Mehrere Layer dürfen auf dieselbe Gruppe verweisen. Nur Layer mit `map_to="active_element"` — genauer: mit dem `group_name` der `active-group` — werden bei der ID-Zuordnung berücksichtigt.

**EN** — Several layers may point to the same group. Only layers with `map_to="active_element"` — more precisely, with the `group_name` of the `active-group` — are considered during ID assignment.

```xml
<dxf_layer_sequence>
    <layer layer_name="Zeichnung Flaeche" map_to="area"
           style_ref="style_area" marker-type="path"/>
    <layer layer_name="Zeichnung Wege" map_to="pathway"
           style_ref="style_pathway" marker-type="path"/>
    <layer layer_name="Zeichnung Grabsteine" map_to="active_element"
           style_ref="style_active_element" marker-type="path"/>
    <layer layer_name="Neue Steine Fragmente" map_to="active_element"
           style_ref="style_active_element" marker-type="circle" marker-size="1.75"/>
</dxf_layer_sequence>
```

**DE** — Für die abstrahierte Variante (`class="marker"`) erhalten sämtliche Grabstein-Layer `marker-type="circle"` mit einheitlicher `marker-size`.

**EN** — For the abstracted variant (`class="marker"`), all grave-stone layers receive `marker-type="circle"` with a uniform `marker-size`.

---

## `dxf_references`

### `reference_frame`

**DE** — Benennt den Layer, der den Referenzrahmen trägt. Dieser Layer muss **genau ein Rechteck** (LWPOLYLINE mit vier Punkten) und **genau einen Punkt** (POINT) im gewünschten Nullpunkt enthalten — nicht mehr und nicht weniger, sonst bricht der Transformer ab.

**EN** — Names the layer carrying the reference frame. This layer must contain **exactly one rectangle** (LWPOLYLINE with four vertices) and **exactly one point** (POINT) at the intended origin — no more and no fewer, otherwise the transformer aborts.

**DE** — Aus dem Rechteck werden Ursprung, Drehwinkel und Maße abgeleitet: Vom Referenzpunkt gehen zwei Kanten aus; die längere wird zur X-Achse, das SVG also im Querformat ausgegeben. Bei einem Quadrat wird die Kante gewählt, die näher an der X-Achse liegt; liegen beide exakt bei 45°, fragt das Programm interaktiv nach der Drehrichtung.

**EN** — Origin, rotation angle and dimensions are derived from the rectangle: two edges start at the reference point; the longer one becomes the X-axis, so the SVG is produced in landscape. For a square, the edge closer to the X-axis is chosen; if both lie exactly at 45°, the program asks interactively for the direction of rotation.

```xml
<reference_frame layer_name="Rahmen"/>
```

### `reference_declaration`

**DE** — Benennt einen Layer mit Bezeichnungsfeldern (TEXT oder MTEXT) und definiert das **Latenzrechteck**, innerhalb dessen ein Ankerpunkt einem Polygon-Eckpunkt zugerechnet wird. Weil die Bezeichnungen händisch gesetzt werden, liegen die Ankerpunkte nicht exakt auf den Eckpunkten; das Latenzrechteck fängt diese Ungenauigkeit auf.

**EN** — Names a layer with label fields (TEXT or MTEXT) and defines the **latency rectangle** within which an anchor point is attributed to a polygon vertex. Since labels are placed by hand, anchor points do not sit exactly on the vertices; the latency rectangle absorbs this imprecision.

**DE** — Genau vier `offset`-Elemente sind erforderlich. Die Werte sind relativ zum Ankerpunkt in DXF-Einheiten:

**EN** — Exactly four `offset` elements are required. The values are relative to the anchor point, in DXF units:

| `offset_vert` | Bedeutung / Meaning | Vorzeichen / Sign |
|---|---|---|
| `x1` | linke Grenze / left boundary | negativ / negative |
| `x2` | rechte Grenze / right boundary | positiv / positive |
| `y1` | obere Grenze / upper boundary | positiv / positive |
| `y2` | untere Grenze / lower boundary | negativ / negative |

```xml
<dxf_references>
    <reference_frame layer_name="Rahmen"/>
    <reference_declaration layer_name="Zeichnung Grabsteine Text">
        <offset offset_vert="x1">-0.01</offset>
        <offset offset_vert="x2">0.01</offset>
        <offset offset_vert="y1">0.01</offset>
        <offset offset_vert="y2">-0.01</offset>
    </reference_declaration>
    <reference_declaration layer_name="Zeichnung Grabsteine Text ausgeblendet">
        <offset offset_vert="x1">-0.01</offset>
        <offset offset_vert="x2">0.01</offset>
        <offset offset_vert="y1">0.01</offset>
        <offset offset_vert="y2">-0.01</offset>
    </reference_declaration>
</dxf_references>
```

**DE** — Ziel ist, dass jedem Grabstätten-Polygon **genau ein** Bezeichnungsfeld zugeordnet wird. Ein zu großes Latenzrechteck erzeugt Mehrfachtreffer, ein zu kleines Fehltreffer. `assign_numbers()` meldet beide Fälle auf der Konsole in der Form `<Nummer> - <Anzahl>`; diese Ausgabe ist nach jedem Lauf zu kontrollieren.

**EN** — The aim is that **exactly one** label field is assigned to each grave polygon. A latency rectangle that is too large produces multiple hits, one that is too small produces misses. `assign_numbers()` reports both cases on the console as `<number> - <count>`; this output should be checked after every run.

> **Achtung / Note** — Aktuell liest `assign_numbers()` die vier Offsets über XPath ohne Layer-Bezug aus, greift also stets auf die erste `reference_declaration` zu. Bei mehreren Deklarationen sollten die Offsets daher identisch sein. / Currently `assign_numbers()` reads the four offsets via XPath without a layer reference, i.e. it always uses the first `reference_declaration`. With several declarations, the offsets should therefore be identical.

---

## `svg_element_sequence`

**DE** — Statische Elemente des Plankopfs. Alle werden in die Gruppe `title-block` einsortiert, die unterhalb der eigentlichen Planzeichnung liegt (Basis-Y = Planhöhe + 30 px). Optionales Attribut `scale_factor` (`decimal`) auf der Sequenz.

**EN** — Static elements of the title block. All are placed in the `title-block` group, which sits below the plan drawing itself (base Y = plan height + 30 px). Optional attribute `scale_factor` (`decimal`) on the sequence.

| Attribut / Attribute | Typ / Type | Pflicht / Required | Bedeutung / Meaning |
|---|---|:--:|---|
| `group_name` | `ID` | ✔ | Steuert die Spezialbehandlung, siehe unten / controls special handling, see below |
| `style_ref` | `IDREF` | ✔ | Style, der auf die gesamte Gruppe gesetzt wird / style applied to the whole group |
| `map_to` | `IDREF` | ✔ | Zielgruppe, in der Praxis `title-block` / target group, in practice `title-block` |
| `translate-x` | `float` | – | Horizontale Verschiebung, Default 0 / horizontal shift, default 0 |
| `translate-y` | `float` | – | Vertikale Verschiebung relativ zur Basis-Y, Default 0 / vertical shift relative to base Y, default 0 |

### Reservierte Gruppennamen / Reserved group names

| `group_name` | Verhalten / Behaviour |
|---|---|
| `north-arrow` | Innere Gruppe mit Rotation entsprechend dem Drehwinkel des Referenzrahmens / inner group rotated according to the reference frame angle |
| `scale-bar` | Maßstabsleiste wird aus `max_scale` und der Planbreite berechnet, Beschriftungen werden generiert / scale bar computed from `max_scale` and plan width, labels generated |
| `plan_header` | Textblock; `tspan`-Kinder werden in ein `<text>` eingefügt / text block; `tspan` children inserted into a `<text>` |
| alle anderen / all others | Kindelemente werden direkt übernommen (z. B. Logo als `rect`-Folge) / child elements copied directly (e.g. logo as a series of `rect`) |

**DE** — Bei nicht reservierten Gruppennamen werden ausschließlich die Kindelemente `path` (mit `d`), `circle` (mit `cx`, `cy`, `r`), `rect` (mit `x`, `y`, `width`, `height`) und `tspan` (mit `x`, `y`) verarbeitet; `max_scale` wird übersprungen. Alle übrigen Tags erzeugen eine Konsolenwarnung und landen nicht im SVG. Fehlt eines der genannten Pflichtattribute, wird das Element stillschweigend ausgelassen.

**EN** — For non-reserved group names, only the child elements `path` (with `d`), `circle` (with `cx`, `cy`, `r`), `rect` (with `x`, `y`, `width`, `height`) and `tspan` (with `x`, `y`) are processed; `max_scale` is skipped. All other tags produce a console warning and do not reach the SVG. If one of the listed mandatory attributes is missing, the element is silently omitted.

### `max_scale`

**DE** — Nur bei `scale-bar` relevant: Länge der Maßstabsleiste in Metern (`integer`). Die Beschriftung wird daraus in Schritten generiert; das Attribut `two-digit-x` auf einem `tspan` korrigiert den Versatz zweistelliger Zahlen.

**EN** — Relevant for `scale-bar` only: length of the scale bar in metres (`integer`). Labels are generated from it in steps; the `two-digit-x` attribute on a `tspan` corrects the offset of two-digit numbers.

```xml
<svg_element_sequence>
    <svg_element group_name="north-arrow" style_ref="style-north-arrow"
                 map_to="title-block" translate-x="0" translate-y="0">
        <path d="M 20,20 L 23.2,20 L 20,0 L 16.8,20 L 20,20 z"/>
        <path d="M 20,20 L 20,40"/>
        <circle cx="20" cy="20" r="20"/>
    </svg_element>
    <svg_element group_name="plan_header" style_ref="style-header"
                 map_to="title-block" translate-x="0" translate-y="0">
        <tspan x="170" y="28.5">JÜDISCHER FRIEDHOF WALSDORF (wld), Steinerne Zeugen digital</tspan>
        <tspan x="170" y="40.5">Lea Puglisi, Fabio Vohl, Tobias Arera-Rütenik (KDWT, Uni-Bamberg 2025) CC-BY-SA 4.0</tspan>
    </svg_element>
    <svg_element group_name="scale-bar" style_ref="style-scale-bar"
                 map_to="title-block" translate-x="0" translate-y="0">
        <max_scale>80</max_scale>
        <rect x="55.8247847" y="0" height="2"/>
        <tspan x="53.6481934" y="9.3286743" two-digit-x="-4.3675619">0</tspan>
    </svg_element>
    <svg_element group_name="SZd-logo" style_ref="style-logo"
                 map_to="title-block" translate-x="0" translate-y="0">
        <rect x="78.3023791" y="21.0489799" width="4.9049263" height="4.9049215"/>
        <rect x="65.7529911" y="21.0474368" width="4.003581"  height="4.9049221"/>
    </svg_element>
</svg_element_sequence>
```

**DE** — Die Vorlagen `Plankopf.svg` und `Logo_SZd_RGB.svg` im Projektverzeichnis liefern die Koordinaten für Nordpfeil, Maßstab und Logo.

**EN** — The templates `Plankopf.svg` and `Logo_SZd_RGB.svg` in the project directory provide the coordinates for north arrow, scale bar and logo.

---

## Validierung / Validation

**DE** — Das Stylesheet verweist im Wurzelelement auf das Schema:

**EN** — The stylesheet references the schema in its root element:

```xml
<MonArch_stylesheet xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="../../schema/stylesheet.xsd"
    class="accurate" svg_width="2400" map_id="wld" set_aks="false">
```

**DE** — Validierung auf der Kommandozeile, etwa mit `xmllint`:

**EN** — Validation on the command line, e.g. with `xmllint`:

```bash
xmllint --noout --schema schema/stylesheet.xsd examples/stylesheets/wld-accurate_bb.xml
```

**DE** — Der Transformer selbst validiert nicht gegen das Schema; er greift per XPath direkt auf die erwarteten Knoten zu. Fehlende Pflichtattribute führen daher zu einem `IndexError` statt zu einer verständlichen Fehlermeldung — eine Validierung vor dem Lauf lohnt sich.

**EN** — The transformer itself does not validate against the schema; it accesses the expected nodes directly via XPath. Missing mandatory attributes therefore cause an `IndexError` rather than a readable error message — validating before a run is worthwhile.

**DE** — Validierung aus Python heraus:

**EN** — Validation from within Python:

```python
from lxml import etree as et

xsd = et.XMLSchema(et.parse("schema/stylesheet.xsd"))
doc = et.parse("examples/stylesheets/wld-accurate_bb.xml")
print(xsd.validate(doc))
for e in xsd.error_log:
    print(e.message)
```

### Die zwei Schema-Dateien / The two schema files

**DE** — Manche Regeln setzen mehrere Angaben zueinander in Beziehung — etwa „`marker-size` ist erforderlich, wenn `marker-type="circle"`". Solche Bedingungen lassen sich erst ab XSD 1.1 mit `xs:assert` ausdrücken. Validierer, die nur XSD 1.0 beherrschen (lxml, xmllint), brechen bei einem Schema mit Assertions bereits die Übersetzung ab. Deshalb zwei Dateien:

**EN** — Some rules relate several entries to one another — for instance "`marker-size` is required when `marker-type="circle"`". Such conditions can only be expressed from XSD 1.1 onwards, using `xs:assert`. Validators limited to XSD 1.0 (lxml, xmllint) already abort compilation of a schema containing assertions. Hence two files:

| Datei / File | Version | Verwendung / Use |
|---|---|---|
| `schema/stylesheet.xsd` | XSD 1.0 | Ziel der `schemaLocation` in allen Stylesheets, überall verwendbar / target of the `schemaLocation` in all stylesheets, usable everywhere |
| `schema/stylesheet-1.1.xsd` | XSD 1.1 | Strenge Prüfung in oXygen, Saxon EE oder dem Python-Paket `xmlschema` / strict checking in oXygen, Saxon EE or the Python package `xmlschema` |

**DE** — `schema/stylesheet-1.1.xsd` übernimmt per `xs:override` das vollständige Schema aus `schema/stylesheet.xsd` und ergänzt nur die Assertions; die Definitionen stehen also weiterhin an einer Stelle.

**EN** — `schema/stylesheet-1.1.xsd` adopts the complete schema from `schema/stylesheet.xsd` via `xs:override` and adds only the assertions, so the definitions remain in one place.

#### Zusätzliche Prüfungen in XSD 1.1 / Additional checks in XSD 1.1

| Prüfung / Check | Fängt ab / Catches |
|---|---|
| `marker-size` bei `marker-type="circle"` | Kreis ohne Radius — bricht den Lauf ab / circle without radius — aborts the run |
| `marker-size` nur bei `circle` | Vergessener Wechsel der Geometrieform / forgotten change of geometry form |
| Vier verschiedene `offset_vert` | Doppelter Wert lässt eine Kante des Latenzrechtecks undefiniert / duplicate leaves one edge undefined |
| `x1 < x2` und `y2 < y1` | Vertauschte Vorzeichen — die Zuordnung findet dann kein Polygon / swapped signs — the assignment then finds no polygon |
| `scale-bar` mit `max_scale`, `rect`, `tspan` | Unvollständige Maßstabsleiste / incomplete scale bar |
| `max_scale` nur in `scale-bar` | Angabe, die stillschweigend übergangen würde / entry that would be silently ignored |
| `plan_header` mit `tspan` | Leerer Plankopf-Text / empty title-block text |
| Mindestens ein Layer auf die `active-group` | Plan ohne annotierbare Elemente / plan without annotatable elements |

#### Einrichtung in oXygen / Setup in oXygen

**DE**

1. *Dokument > Validierung > Validierungsszenario konfigurieren*
2. Neues Szenario anlegen, als Schema `schema/stylesheet-1.1.xsd` wählen.
3. Als Schemaversion **XML Schema 1.1** einstellen — sonst meldet der Validierer die `xs:assert`-Elemente als unbekannt.
4. Das Szenario dem Ordner der Stylesheets zuordnen.

Der Verweis `xsi:noNamespaceSchemaLocation` in den Dateien zeigt weiterhin auf `schema/stylesheet.xsd`; das Validierungsszenario hat Vorrang. Dadurch bleiben die Dateien auch außerhalb von oXygen prüfbar.

**EN**

1. *Document > Validation > Configure Validation Scenario*
2. Create a new scenario, select `schema/stylesheet-1.1.xsd` as the schema.
3. Set the schema version to **XML Schema 1.1** — otherwise the validator reports the `xs:assert` elements as unknown.
4. Associate the scenario with the stylesheet folder.

The `xsi:noNamespaceSchemaLocation` reference in the files keeps pointing at `schema/stylesheet.xsd`; the validation scenario takes precedence. This keeps the files checkable outside oXygen as well.

**DE** — Was gegenüber früheren Schema-Ständen geändert wurde, steht im [CHANGELOG](../CHANGELOG.md).

**EN** — What changed compared to earlier schema states is recorded in the [CHANGELOG](../CHANGELOG.md).

---

## Checkliste für ein neues Stylesheet / Checklist for a new stylesheet

**DE**

1. `map_id`, `class` und `svg_width` im Wurzelelement setzen.
2. Layernamen der DXF-Zeichnung auslesen und in `dxf_layer_sequence` eintragen — sie müssen exakt übereinstimmen.
3. Jedem Layer eine Gruppe (`map_to`) und einen Style (`style_ref`) zuweisen; alle referenzierten Namen müssen in `svg_group_sequence` bzw. `svg_style_sequence` definiert sein.
4. Referenzrahmen-Layer benennen und in der CAD-Zeichnung prüfen: genau ein Rechteck, genau ein Punkt.
5. Latenzrechteck in `reference_declaration` festlegen und nach dem ersten Lauf anhand der Konsolenausgabe nachjustieren.
6. Plankopf-Elemente aus `Plankopf.svg` übernehmen und `max_scale` an die Friedhofsgröße anpassen.
7. Gegen `schema/stylesheet.xsd` validieren, dann den Transformer starten.

**EN**

1. Set `map_id`, `class` and `svg_width` in the root element.
2. Read the layer names from the DXF drawing and enter them in `dxf_layer_sequence` — they must match exactly.
3. Assign a group (`map_to`) and a style (`style_ref`) to every layer; all referenced names must be defined in `svg_group_sequence` resp. `svg_style_sequence`.
4. Name the reference frame layer and check the CAD drawing: exactly one rectangle, exactly one point.
5. Define the latency rectangle in `reference_declaration` and readjust it after the first run based on the console output.
6. Take the title-block elements from `Plankopf.svg` and adapt `max_scale` to the size of the cemetery.
7. Validate against `schema/stylesheet.xsd`, then start the transformer.
