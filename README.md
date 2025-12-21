# 🎵 Beatport Telegram Bot

Ein Telegram-Bot, der Tracks, Artists und Releases auf Beatport sucht und die direkten Links zurückgibt.

## 📋 Funktionen

- Suche nach Tracks auf Beatport
- Suche nach Artists
- Zeigt Track-Titel, Artists, Label und direkten Link
- Bis zu 5 Ergebnisse pro Suche

## 🚀 Installation

1. **Installiere die benötigten Pakete:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Starte den Bot:**
   ```bash
   python3 bot.py
   ```

## 💬 Verwendung

### Befehle:
- `/start` - Bot starten und Willkommensnachricht anzeigen
- `/help` - Hilfe und Beispiele anzeigen

### Suche:
Sende einfach den Namen eines Tracks oder Artists:
- `Amelie Lens`
- `Charlotte de Witte - Selected`
- `drumcode`

Der Bot sucht automatisch auf Beatport und zeigt dir die Ergebnisse mit direkten Links!

## 🔧 Konfiguration

Dein Bot-Token ist bereits in `bot.py` eingetragen. Wenn du ihn ändern möchtest, bearbeite die Zeile:
```python
BOT_TOKEN = "DEIN_TOKEN_HIER"
```

## 📝 Hinweise

- Der Bot braucht eine aktive Internetverbindung
- Beatport muss erreichbar sein
- Der Bot läuft solange das Terminal-Fenster offen ist

## 🛑 Bot stoppen

Drücke `Ctrl + C` im Terminal um den Bot zu stoppen.

## 🎉 Viel Spaß!

Dein Bot ist bereit, Tracks auf Beatport zu finden!
