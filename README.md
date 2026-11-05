# Warum verschwinden Socken in der Waschmaschine? – eine Untersuchung

Dieses Python-Skript rendert einen kurzen, animierten Erklärfilm im Hochkantformat (720 × 1280) als MP4. Der Film enthält animierte Illustrationen und deutsche Texteinblendungen, aber keine Sprachaufnahme.

## Starten

Voraussetzung ist Python 3.9 oder neuer. Installiere die Abhängigkeiten und starte das Skript:

```bash
python -m pip install -r requirements.txt
python socken_untersuchung.py
```

Das Video wird als `socken_untersuchung.mp4` im aktuellen Verzeichnis gespeichert. Die benötigte FFmpeg-Binärdatei wird über `imageio-ffmpeg` bereitgestellt.

## Anpassen

- Länge und Bildrate: `SCENE_SECONDS` und `FPS` in `socken_untersuchung.py`.
- Format: `WIDTH` und `HEIGHT`.
- Texte, Farben und Zeichnungen: in `scene_frame()` und den Hilfsfunktionen.

Der Film stellt mögliche alltägliche Erklärungen dar; welche davon zutrifft, hängt vom jeweiligen Waschmaschinenmodell und der Situation ab. Geräte nicht ohne Herstelleranleitung auseinanderbauen.
