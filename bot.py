import telebot
import requests
import os
import re
import json
from datetime import datetime, timedelta
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from apscheduler.schedulers.background import BackgroundScheduler

# Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Beatport Credentials (aus Environment Variables)
BEATPORT_USERNAME = os.environ.get("BEATPORT_USERNAME")
BEATPORT_PASSWORD = os.environ.get("BEATPORT_PASSWORD")

# Bot initialisieren
bot = telebot.TeleBot(BOT_TOKEN)

# Beatport API v4 Konfiguration
BEATPORT_API_BASE = "https://api.beatport.com/v4"
BEATPORT_REDIRECT_URI = f"{BEATPORT_API_BASE}/auth/o/post-message/"

# Token-Cache (im Speicher)
beatport_token = None
token_expires_at = None


def fetch_beatport_client_id():
    """Holt die Client ID von der Beatport API Docs Seite"""
    try:
        print("Hole Beatport Client ID...")
        response = requests.get(f"{BEATPORT_API_BASE}/docs/", timeout=10)
        response.raise_for_status()

        # Suche nach JavaScript-Dateien
        js_urls = re.findall(r'src="(/static/js/[^"]+)"', response.text)

        for js_url in js_urls:
            try:
                full_url = f"{BEATPORT_API_BASE}{js_url}"
                js_response = requests.get(full_url, timeout=5)
                match = re.search(r"API_CLIENT_ID: '([^']+)'", js_response.text)
                if match:
                    client_id = match.group(1)
                    print(f"Client ID gefunden: {client_id}")
                    return client_id
            except:
                continue

        # Fallback zur bekannten funktionierenden Client ID
        print("Verwende bekannte Client ID")
        return "0GIvkCltVIuPkkwSJHp6NDb3s0potTjLBQr388Dd"

    except Exception as e:
        print(f"Fehler beim Holen der Client ID: {e}")
        return "0GIvkCltVIuPkkwSJHp6NDb3s0potTjLBQr388Dd"


def get_beatport_token():
    """Holt oder erneuert das Beatport Access Token"""
    global beatport_token, token_expires_at

    # Prüfe ob Token noch gültig ist
    if beatport_token and token_expires_at and datetime.now() < token_expires_at:
        return beatport_token

    try:
        print("Authentifiziere mit Beatport API...")
        client_id = fetch_beatport_client_id()

        # Session erstellen um Cookies zu behalten
        session = requests.Session()

        # Schritt 1: Login (setzt Session-Cookies)
        print(f"Login mit Username: {BEATPORT_USERNAME}")
        login_data = {
            "username": BEATPORT_USERNAME,
            "password": BEATPORT_PASSWORD
        }
        login_response = session.post(
            f"{BEATPORT_API_BASE}/auth/login/",
            json=login_data
        )
        print(f"Login Response Status: {login_response.status_code}")
        login_response.raise_for_status()
        print(f"Session Cookies gesetzt: {list(session.cookies.keys())}")

        # Schritt 2: Authorization Code holen (nutzt Session-Cookies!)
        auth_params = {
            "client_id": client_id,
            "redirect_uri": BEATPORT_REDIRECT_URI,
            "response_type": "code"
        }
        print(f"Authorization Request mit Client ID: {client_id[:20]}...")
        auth_response = session.get(
            f"{BEATPORT_API_BASE}/auth/o/authorize/",
            params=auth_params,
            allow_redirects=False
        )
        print(f"Auth Response Status: {auth_response.status_code}")

        # Extrahiere Authorization Code aus Redirect
        location = auth_response.headers.get("Location", "")
        print(f"Redirect Location: {location[:100] if location else 'None'}...")
        code_match = re.search(r"code=([^&]+)", location)
        if not code_match:
            print(f"Response Headers: {dict(auth_response.headers)}")
            print(f"Response Body: {auth_response.text[:500]}")
            raise Exception("Konnte Authorization Code nicht erhalten")

        auth_code = code_match.group(1)
        print(f"Authorization Code erhalten: {auth_code[:20]}...")

        # Schritt 3: Access Token holen
        token_data = {
            "client_id": client_id,
            "redirect_uri": BEATPORT_REDIRECT_URI,
            "code": auth_code,
            "grant_type": "authorization_code"
        }
        token_response = requests.post(
            f"{BEATPORT_API_BASE}/auth/o/token/",
            data=token_data
        )
        token_response.raise_for_status()
        token_json = token_response.json()

        beatport_token = token_json.get("access_token")
        expires_in = token_json.get("expires_in", 3600)
        token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

        print("Beatport Authentifizierung erfolgreich!")
        return beatport_token

    except Exception as e:
        print(f"Fehler bei Beatport Authentifizierung: {e}")
        return None


def search_beatport(query, search_type="tracks", limit=5):
    """Sucht auf Beatport nach Tracks oder Releases"""
    try:
        token = get_beatport_token()
        if not token:
            return None

        headers = {
            "Authorization": f"Bearer {token}"
        }

        params = {
            "q": query,
            "type": search_type,
            "per_page": limit
        }

        print(f"Suche nach: {query}")
        response = requests.get(
            f"{BEATPORT_API_BASE}/catalog/search/",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()

        results = []
        items = data.get(search_type, [])

        for item in items[:limit]:
            if search_type == "tracks":
                results.append({
                    'title': item.get('name', 'Unbekannt'),
                    'artists': ', '.join([a.get('name', '') for a in item.get('artists', [])]),
                    'remixers': ', '.join([r.get('name', '') for r in item.get('remixers', [])]),
                    'label': item.get('release', {}).get('label', {}).get('name', ''),
                    'genre': item.get('genre', {}).get('name', ''),
                    'bpm': item.get('bpm', ''),
                    'key': item.get('key', {}).get('name', ''),
                    'release_date': item.get('release', {}).get('publish_date', ''),
                    'link': f"https://www.beatport.com/track/{item.get('slug', '')}/{item.get('id', '')}"
                })
            elif search_type == "releases":
                results.append({
                    'title': item.get('name', 'Unbekannt'),
                    'artists': ', '.join([a.get('name', '') for a in item.get('artists', [])]),
                    'label': item.get('label', {}).get('name', ''),
                    'release_date': item.get('publish_date', ''),
                    'track_count': item.get('track_count', 0),
                    'link': f"https://www.beatport.com/release/{item.get('slug', '')}/{item.get('id', '')}"
                })

        return results

    except Exception as e:
        print(f"Fehler bei der Suche: {e}")
        import traceback
        traceback.print_exc()
        return None


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "🎵 Willkommen beim Beatport Search Bot!\n\n"
                 "Sende mir einfach den Namen eines Tracks oder Artists "
                 "und ich suche ihn auf Beatport für dich!\n\n"
                 "Befehle:\n"
                 "/start - Bot starten\n"
                 "/help - Hilfe anzeigen\n"
                 "/release [Name] - Nach Releases suchen\n\n"
                 "Beispiel: 'Amelie Lens - Feel It'\n\n"
                 "✨ Nutzt die offizielle Beatport API v4!")


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
                 "📖 Hilfe\n\n"
                 "So funktioniert's:\n"
                 "1. Sende mir einen Track- oder Artist-Namen\n"
                 "2. Ich suche auf Beatport danach\n"
                 "3. Du bekommst die Top-Ergebnisse mit Details\n\n"
                 "Befehle:\n"
                 "• Normaler Text = Track-Suche\n"
                 "• /release [Name] = Release/Album-Suche\n\n"
                 "Beispiele:\n"
                 "• 'Charlotte de Witte'\n"
                 "• 'Amelie Lens - Feel It'\n"
                 "• '/release drumcode'\n\n"
                 "Tipp: Je genauer deine Suche, desto bessere Ergebnisse! 🎯")


@bot.message_handler(commands=['release'])
def search_release(message):
    query = message.text.replace('/release', '').strip()

    if not query:
        bot.reply_to(message, "❌ Bitte gib einen Release-Namen an!\nBeispiel: /release Drumcode")
        return

    bot.send_message(message.chat.id, f"🔍 Suche nach Release '{query}' auf Beatport...\n⏳ Bitte warte...")

    results = search_beatport(query, search_type="releases", limit=5)

    if results is None:
        bot.send_message(message.chat.id,
                        "❌ Es gab ein Problem bei der Suche. Bitte versuche es später nochmal.")
        return

    if not results:
        bot.send_message(message.chat.id,
                        f"😔 Keine Releases für '{query}' gefunden.\n\n"
                        "Versuche es mit anderen Suchbegriffen!")
        return

    response = f"💿 Releases auf Beatport ({len(results)} Ergebnisse):\n\n"

    for i, result in enumerate(results, 1):
        response += f"{i}. {result['title']}\n"
        if result['artists']:
            response += f"   👤 {result['artists']}\n"
        if result['label']:
            response += f"   🏷️ {result['label']}\n"
        if result['track_count']:
            response += f"   📀 {result['track_count']} Tracks\n"
        if result['release_date']:
            response += f"   📅 {result['release_date']}\n"
        response += f"   🔗 {result['link']}\n\n"

    if len(response) > 4096:
        for i in range(0, len(response), 4096):
            bot.send_message(message.chat.id, response[i:i+4096])
    else:
        bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: True)
def search_track(message):
    query = message.text.strip()

    if not query:
        bot.reply_to(message, "❌ Bitte sende mir einen Suchbegriff!")
        return

    bot.send_message(message.chat.id, f"🔍 Suche nach '{query}' auf Beatport...\n⏳ Bitte warte...")

    results = search_beatport(query, search_type="tracks", limit=5)

    if results is None:
        bot.send_message(message.chat.id,
                        "❌ Es gab ein Problem bei der Suche. Bitte versuche es später nochmal.")
        return

    if not results:
        bot.send_message(message.chat.id,
                        f"😔 Keine Tracks für '{query}' gefunden.\n\n"
                        "Versuche es mit:\n"
                        "• Anderen Suchbegriffen\n"
                        "• Nur dem Artist-Namen\n"
                        "• /release für Release-Suche")
        return

    response = f"🎵 Tracks auf Beatport ({len(results)} Ergebnisse):\n\n"

    for i, result in enumerate(results, 1):
        track_name = result['title']
        if result['remixers']:
            track_name += f" ({result['remixers']} Remix)"

        response += f"{i}. 🎧 {track_name}\n"
        if result['artists']:
            response += f"   👤 {result['artists']}\n"
        if result['label']:
            response += f"   🏷️ {result['label']}\n"
        if result['genre']:
            response += f"   🎼 {result['genre']}"
            if result['bpm']:
                response += f" • {result['bpm']} BPM"
            if result['key']:
                response += f" • {result['key']}"
            response += "\n"
        if result['release_date']:
            response += f"   📅 {result['release_date']}\n"
        response += f"   🔗 {result['link']}\n\n"

    if len(response) > 4096:
        for i in range(0, len(response), 4096):
            bot.send_message(message.chat.id, response[i:i+4096])
    else:
        bot.send_message(message.chat.id, response)


# Health Check Server für Render (damit Web Service funktioniert)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Beatport Bot is running!')
    
    def log_message(self, format, *args):
        # Keine Logs für Health Checks
        pass


def run_health_server():
    """Startet einen einfachen HTTP Server für Render Health Checks"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"✅ Health Check Server läuft auf Port {port}")
    server.serve_forever()


def keep_alive():
    """Keep-Alive Funktion - hält den Bot wach"""
    try:
        print("⏰ Keep-Alive: Aktualisiere Beatport Token...")
        token = get_beatport_token()
        if token:
            print("✅ Keep-Alive: Token erfolgreich aktualisiert")
        else:
            print("⚠️ Keep-Alive: Token-Aktualisierung fehlgeschlagen")
    except Exception as e:
        print(f"❌ Keep-Alive Fehler: {e}")


# Bot starten
if __name__ == "__main__":
    try:
        if not BOT_TOKEN:
            print("❌ Fehler: BOT_TOKEN environment variable nicht gesetzt!")
            exit(1)

        if not BEATPORT_USERNAME or not BEATPORT_PASSWORD:
            print("❌ Fehler: BEATPORT_USERNAME und BEATPORT_PASSWORD environment variables müssen gesetzt sein!")
            exit(1)

        # Lösche alle Webhooks und stoppe alte Polling-Sessions
        print("🧹 Bereinige alte Bot-Instanzen...")
        max_retries = 3
        for i in range(max_retries):
            try:
                bot.remove_webhook()
                print("✅ Webhooks gelöscht")
                # Warte kurz um sicherzustellen dass alte Instanzen gestoppt sind
                import time
                time.sleep(2)
                break
            except Exception as e:
                print(f"⚠️ Versuch {i+1}/{max_retries} Webhook zu löschen fehlgeschlagen: {e}")
                if i < max_retries - 1:
                    import time
                    time.sleep(3)

        # Health Check Server in separatem Thread starten
        health_thread = Thread(target=run_health_server, daemon=True)
        health_thread.start()

        # Keep-Alive Scheduler starten (alle 10 Minuten)
        scheduler = BackgroundScheduler()
        scheduler.add_job(keep_alive, 'interval', minutes=10)
        scheduler.start()
        print("✅ Keep-Alive Scheduler gestartet (alle 10 Minuten)")

        print("🎵 Beatport Search Bot (API v4) ist gestartet...")
        print("Bereit für Suchanfragen!")

        # Starte Polling mit Retry-Logik bei 409 Fehler
        while True:
            try:
                bot.infinity_polling(timeout=10, long_polling_timeout=5, restart_on_change=False)
                break
            except Exception as e:
                if "409" in str(e) or "Conflict" in str(e):
                    print("⚠️ 409 Konflikt erkannt - warte 5 Sekunden und versuche erneut...")
                    import time
                    time.sleep(5)
                    try:
                        bot.remove_webhook()
                        time.sleep(2)
                    except:
                        pass
                else:
                    raise
    except KeyboardInterrupt:
        print("\nBot wird beendet...")
        try:
            scheduler.shutdown(wait=False)
        except:
            pass
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()