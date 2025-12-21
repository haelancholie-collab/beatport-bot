# Beatport Telegram Bot - Kostenlos Hosten

Dieser Guide zeigt dir, wie du den Bot **kostenlos 24/7** auf Railway hosten kannst.

## Warum Railway?

- ✅ 500 Stunden/Monat kostenlos (~20 Tage Non-Stop)
- ✅ Sehr einfaches Setup
- ✅ Automatische Deployments bei Git-Push
- ✅ Keine Kreditkarte nötig für Basis-Tier

---

## Schritt 1: Vorbereitung

### 1.1 Beatport Account
Du brauchst einen **Beatport Account** (kostenlos):
1. Gehe zu https://www.beatport.com
2. Registriere dich (falls noch nicht geschehen)
3. Merke dir Username und Passwort

### 1.2 Telegram Bot Token
Falls noch nicht gemacht:
1. Öffne Telegram und suche nach `@BotFather`
2. Sende `/newbot` und folge den Anweisungen
3. Kopiere den **Bot Token** (z.B. `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

---

## Schritt 2: Code auf GitHub hochladen

### 2.1 Repository erstellen
1. Gehe zu https://github.com
2. Klicke auf "New Repository"
3. Name: `beatport-telegram-bot`
4. Mache es **Private** (damit deine Credentials sicher sind)
5. Klicke "Create repository"

### 2.2 Code hochladen
```bash
cd /Users/axibert/Downloads/beatport_telegram_bot

# Git initialisieren (falls noch nicht geschehen)
git init

# Dateien hinzufügen
git add bot_beatport_api.py requirements_api.txt Procfile runtime.txt .gitignore

# Commit erstellen
git commit -m "Initial Beatport API bot"

# Mit GitHub verbinden (ersetze USERNAME und REPO)
git remote add origin https://github.com/USERNAME/beatport-telegram-bot.git
git branch -M main
git push -u origin main
```

---

## Schritt 3: Railway Setup

### 3.1 Account erstellen
1. Gehe zu https://railway.app
2. Klicke "Login" → "Login with GitHub"
3. Autorisiere Railway

### 3.2 Projekt erstellen
1. Klicke auf "New Project"
2. Wähle "Deploy from GitHub repo"
3. Wähle dein Repository `beatport-telegram-bot`
4. Railway erkennt automatisch Python und startet das Deployment

### 3.3 Environment Variables setzen
1. Klicke auf dein Projekt
2. Gehe zu "Variables"
3. Füge folgende Variables hinzu:

```
BOT_TOKEN=dein_telegram_bot_token_hier
BEATPORT_USERNAME=dein_beatport_username
BEATPORT_PASSWORD=dein_beatport_passwort
```

4. Klicke "Add" für jede Variable

### 3.4 Requirements anpassen
Railway sucht automatisch nach `requirements.txt`. Benenne die Datei um:

```bash
# Lokal auf deinem Mac
mv requirements_api.txt requirements.txt

git add requirements.txt
git commit -m "Rename requirements for Railway"
git push
```

Railway deployed automatisch neu!

---

## Schritt 4: Bot testen

1. Warte 1-2 Minuten bis Deployment fertig ist
2. Öffne Telegram und suche deinen Bot
3. Sende `/start`
4. Teste eine Suche: `Amelie Lens`

---

## Alternative: Render.com

Falls Railway nicht funktioniert, hier die Schritte für Render:

### 1. Account erstellen
1. Gehe zu https://render.com
2. Signup mit GitHub

### 2. Web Service erstellen
1. Klicke "New +" → "Background Worker"
2. Verbinde dein GitHub Repository
3. Einstellungen:
   - **Name:** beatport-bot
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot_beatport_api.py`

### 3. Environment Variables
Füge die gleichen Variables wie bei Railway hinzu:
- `BOT_TOKEN`
- `BEATPORT_USERNAME`
- `BEATPORT_PASSWORD`

### 4. Deploy
Klicke "Create Background Worker"

---

## Troubleshooting

### Bot antwortet nicht
1. Check Railway/Render Logs:
   - Railway: Klick auf dein Projekt → "Logs"
   - Render: Gehe zu deinem Service → "Logs"
2. Prüfe ob alle Environment Variables korrekt gesetzt sind

### "Authentication Error"
- Prüfe ob Beatport Username/Password stimmen
- Versuche dich manuell auf beatport.com einzuloggen

### Bot stoppt nach einiger Zeit
- Railway Free Tier: 500 Stunden/Monat
- Render Free Tier: Schläft nach 15 Min Inaktivität

---

## Kosten

### Railway Free Tier
- **500 Stunden/Monat** (~20 Tage Non-Stop)
- Danach: $5/Monat für unlimited

### Render Free Tier
- **Kostenlos**, aber:
  - Schläft nach 15 Min Inaktivität
  - Startet automatisch bei neuer Nachricht (langsame erste Antwort)

---

## Nächste Schritte

- ✅ Bot läuft 24/7 kostenlos
- ✅ Automatische Updates bei Git-Push
- ✅ Keine Wartung nötig

**Bei Fragen:** Schau in die Railway/Render Docs oder frag mich!
