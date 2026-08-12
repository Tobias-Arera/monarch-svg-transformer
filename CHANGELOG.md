# Änderungshistorie / Changelog

**DE** — Das Format folgt lose [Keep a Changelog](https://keepachangelog.com/de/1.1.0/). Die Datumsangaben entsprechen den Dateiständen der Vorgeschichte außerhalb dieses Repositorys.

**EN** — The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The dates correspond to the file states of the history predating this repository.

---

## [1.0.0] – 2026-08-12

Erste Veröffentlichung als Repository / first release as a repository.

**DE** — Die Überarbeitung des Codes, die zweisprachige Dokumentation und der Aufbau dieses Repositorys entstanden KI-unterstützt (Claude, Anthropic). Fachliche Konzeption, Prüfung und Verantwortung liegen beim Autor.

**EN** — The revision of the code, the bilingual documentation and the setup of this repository were produced with AI assistance (Claude, Anthropic). The conceptual work, review and responsibility rest with the author.

### Behoben / Fixed

- **Zuordnung von MTEXT-Bezeichnungen.** `assign_numbers()` prüfte die Gültigkeit eines Bezeichnungsfeldes über die Anzahl der Dictionary-Schlüssel (`len(t) == 7`). `get_mtexts()` liefert nur sechs Schlüssel, weil MTEXT-Bezeichnungen keinen Sektor enthalten — MTEXT-Felder wurden dadurch nie zugeordnet. Geprüft wird jetzt das Vorhandensein von `Nummer` und `Anker`. / `assign_numbers()` checked validity via the number of dictionary keys; MTEXT labels carry only six and were never assigned. The presence of `Nummer` and `Anker` is checked instead.
- **Ungültige Bezeichnungsfelder.** Die Zuordnungsschleife lag außerhalb der Gültigkeitsprüfung und lief im Fehlerfall mit Nummer und Koordinaten des vorigen Durchlaufs weiter; eine bereits vergebene ID konnte ein zweites Mal gesetzt werden. Solche Felder werden jetzt übersprungen und gezählt gemeldet. / The assignment loop ran outside the validity check and continued with the previous iteration's values; such fields are now skipped and reported as a count.
- **Friedhofskürzel in `get_mtexts()`** war fest als `'wld'` eingetragen und stammt jetzt aus `map_id`. / was hard-coded and now comes from `map_id`.
- **Fehlendes `map_id`** wurde als Lesefehler des Stylesheets gemeldet und wird jetzt eigens geprüft. / was reported as a stylesheet read error and is now checked separately.
- **Fehlendes `marker-type` bzw. `marker-size`** führte zu einem `IndexError` und wird jetzt im Klartext samt Layername gemeldet. / caused an `IndexError` and is now reported in plain text including the layer name.

### Geändert / Changed

- **Fehlerbehandlung über Ausnahmen.** Alle `sys.exit(1)` sind durch `SVGTransformerError`, `StylesheetError` und `DXFError` ersetzt. In Jupyter überlebt der Kernel damit einen Fehlversuch, und aufrufender Code kann den Fehler abfangen. / All `sys.exit(1)` calls replaced by exceptions; the Jupyter kernel survives a failed attempt and calling code can handle the error.
- **`generate_gradient_color_table()`** nutzt `matplotlib.colormaps[…].resampled()` mit Rückfall auf `cm.get_cmap()`, das seit matplotlib 3.7 veraltet ist. / uses the colormap registry with a fallback to the deprecated `cm.get_cmap()`.
- **Dateiname** von `svgTransformer_JJJJMMTT.py` auf `svg_transformer.py`; die Versionierung übernimmt git. / file name changed; versioning is handled by git.

### Schema

- `set_aks` war global deklariert, aber im Wurzelelement nicht referenziert — Stylesheets mit diesem Attribut scheiterten an der Validierung. / was declared globally but not referenced in the root element.
- `svg_element` besaß mit optionalem `max_scale` gefolgt von `xs:any` kein deterministisches Inhaltsmodell; lxml verweigerte die Übersetzung des Schemas. Das `xs:any` ist durch eine Auswahl aus `path`, `circle`, `rect` und `tspan` ersetzt. / had no deterministic content model; the `xs:any` is replaced by a choice of the supported children.
- `marker-type` war zugleich `use="required"` und mit `default="path"` versehen; der Vorgabewert entfällt. / was both required and supplied with a default; the default is dropped.
- `map_id` ist verpflichtend, `offset_vert` auf `x1`, `x2`, `y1`, `y2` eingeschränkt, numerische Werte sind typisiert. / `map_id` is mandatory, `offset_vert` restricted, numeric values typed.
- Neu: `schema/stylesheet-1.1.xsd` mit acht `xs:assert`-Regeln für Validierer, die XML Schema 1.1 unterstützen. / New: `schema/stylesheet-1.1.xsd` with eight assertions for XSD 1.1 validators.
- XML-Deklaration von 1.1 auf 1.0, zweisprachige `xs:documentation` durchgängig ergänzt. / XML declaration changed, bilingual documentation added throughout.

---

## Vorgeschichte / History before this repository

| Stand / Date | Neu / Added |
|---|---|
| 2025-08-05 | Basisversion: DXF → SVG, Referenzrahmen mit beliebiger Drehung, Plankopf / base version |
| 2025-08-13 | Erweiterte Plankopf-Verarbeitung / extended title-block processing |
| 2025-10-31 | Kartierungsmodus mit `apply_mapping()`, Farbverläufe über `generate_gradient_color_table()` / mapping mode and colour gradients |
| 2025-11-02 | JSON-Modus: `export_json()`, `load_json()` / JSON mode |
| 2025-11-21 | Tooltips über `tooltip_cols`, URL-Verlinkung über `url_col` / tooltips and URL links |
