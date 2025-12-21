#!/bin/bash

# Beatport Telegram Bot Starter
echo "🎵 Starte Beatport Telegram Bot..."
echo ""

# Prüfe ob .env existiert
if [ ! -f .env ]; then
    echo "❌ .env Datei nicht gefunden!"
    echo "Bitte erstelle eine .env Datei mit deinen Credentials:"
    echo ""
    echo "BOT_TOKEN=dein_token"
    echo "BEATPORT_USERNAME=dein_username"
    echo "BEATPORT_PASSWORD=dein_passwort"
    exit 1
fi

# Lade Environment Variables aus .env
export $(cat .env | grep -v '^#' | xargs)

# Prüfe ob alle Variables gesetzt sind
if [ -z "$BOT_TOKEN" ] || [ -z "$BEATPORT_USERNAME" ] || [ -z "$BEATPORT_PASSWORD" ]; then
    echo "❌ Nicht alle Environment Variables sind gesetzt!"
    echo "Bitte fülle die .env Datei aus:"
    echo ""
    echo "BOT_TOKEN=dein_token"
    echo "BEATPORT_USERNAME=dein_username"
    echo "BEATPORT_PASSWORD=dein_passwort"
    exit 1
fi

echo "✅ Environment Variables geladen"
echo "🚀 Starte Bot..."
echo ""

# Bot starten
python3 bot.py
