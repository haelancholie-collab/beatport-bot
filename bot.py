import telebot
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import os

# Dein Bot-Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Bot initialisieren
bot = telebot.TeleBot(BOT_TOKEN)

# Chrome Driver einmalig initialisieren (wird wiederverwendet)
driver = None

def init_driver():
    """Initialisiert den Chrome WebDriver"""
    global driver
    if driver is None:
        print("Initialisiere Chrome WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Kein sichtbares Fenster
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Versuche verschiedene ChromeDriver Pfade
        chromedriver_paths = [
            '/usr/local/bin/chromedriver',  # Homebrew Intel
            '/opt/homebrew/bin/chromedriver',  # Homebrew ARM (M1/M2/M3)
            '/usr/bin/chromedriver',
        ]
        
        service = None
        for path in chromedriver_paths:
            if os.path.exists(path):
                print(f"Verwende ChromeDriver von: {path}")
                service = Service(path)
                break
        
        if service is None:
            print("Kein ChromeDriver gefunden. Versuche automatischen Download...")
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome WebDriver bereit!")

def search_beatport(query):
    """Sucht auf Beatport nach einem Track/Release mit Selenium"""
    try:
        init_driver()
        
        # Beatport Suche URL
        search_url = f"https://www.beatport.com/search?q={urllib.parse.quote(query)}"
        
        print(f"Suche nach: {query}")
        print(f"URL: {search_url}")
        
        driver.get(search_url)
        
        # Warte bis die Seite geladen ist
        print("Warte auf Suchergebnisse...")
        time.sleep(3)  # Gib der Seite Zeit zum Laden
        
        results = []
        
        # Versuche verschiedene Selektoren für Tracks
        try:
            # Warte auf Track-Elemente
            wait = WebDriverWait(driver, 10)
            
            # Methode 1: Suche nach Track-Links
            track_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/track/"]')
            print(f"Gefundene Track-Links: {len(track_links)}")
            
            seen_urls = set()
            
            for link in track_links[:10]:  # Maximal 10 Links durchgehen
                try:
                    url = link.get_attribute('href')
                    
                    # Überspringe Duplikate
                    if url in seen_urls or not url:
                        continue
                    seen_urls.add(url)
                    
                    # Versuche Informationen zu extrahieren
                    # Gehe zum Parent-Element um mehr Infos zu finden
                    parent = link
                    for _ in range(5):  # Gehe bis zu 5 Ebenen hoch
                        try:
                            parent = parent.find_element(By.XPATH, '..')
                            
                            # Versuche Track-Titel zu finden
                            try:
                                title_elem = parent.find_element(By.CSS_SELECTOR, '[class*="title"], [class*="Title"], [class*="name"], [class*="Name"]')
                                title = title_elem.text.strip()
                            except:
                                title = link.text.strip()
                            
                            # Versuche Artist zu finden
                            try:
                                artist_elem = parent.find_element(By.CSS_SELECTOR, '[class*="artist"], [class*="Artist"]')
                                artists = artist_elem.text.strip()
                            except:
                                artists = ""
                            
                            # Versuche Label zu finden
                            try:
                                label_elem = parent.find_element(By.CSS_SELECTOR, '[class*="label"], [class*="Label"]')
                                label = label_elem.text.strip()
                            except:
                                label = ""
                            
                            if title or artists:
                                break
                        except:
                            continue
                    
                    if not title:
                        title = link.text.strip() or "Track"
                    
                    if not artists:
                        artists = "Siehe Link für Details"
                    
                    results.append({
                        'title': title,
                        'artists': artists,
                        'label': label,
                        'link': url
                    })
                    
                    if len(results) >= 5:
                        break
                        
                except Exception as e:
                    print(f"Fehler beim Parsen von Link: {e}")
                    continue
            
        except Exception as e:
            print(f"Fehler beim Finden von Tracks: {e}")
        
        # Falls keine Ergebnisse, speichere HTML für Debug
        if not results:
            with open('debug_selenium.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("HTML gespeichert in debug_selenium.html")
        
        print(f"Endergebnis: {len(results)} Tracks gefunden")
        return results
    
    except Exception as e:
        print(f"Fehler bei der Suche: {e}")
        import traceback
        traceback.print_exc()
        return None

# /start Befehl
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 "🎵 Willkommen beim Beatport Search Bot!\n\n"
                 "Sende mir einfach den Namen eines Tracks, Artists oder Releases "
                 "und ich suche ihn auf Beatport für dich!\n\n"
                 "Befehle:\n"
                 "/start - Bot starten\n"
                 "/help - Hilfe anzeigen\n\n"
                 "Beispiel: 'Amelie Lens - Feel It'\n\n"
                 "⚠️ Hinweis: Die erste Suche kann etwas länger dauern, "
                 "da der Browser initialisiert wird.")

# /help Befehl
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
                 "📖 Hilfe\n\n"
                 "So funktioniert's:\n"
                 "1. Sende mir einen Track- oder Artist-Namen\n"
                 "2. Ich suche auf Beatport danach\n"
                 "3. Du bekommst die Top-Ergebnisse mit Links\n\n"
                 "Beispiele:\n"
                 "• 'Charlotte de Witte'\n"
                 "• 'Amelie Lens - Feel It'\n"
                 "• 'drumcode'\n\n"
                 "Tipp: Je genauer deine Suche, desto bessere Ergebnisse! 🎯")

# Auf alle Text-Nachrichten antworten
@bot.message_handler(func=lambda message: True)
def search_track(message):
    query = message.text.strip()
    
    if not query:
        bot.reply_to(message, "❌ Bitte sende mir einen Suchbegriff!")
        return
    
    # Suche wird gestartet
    bot.send_message(message.chat.id, f"🔍 Suche nach '{query}' auf Beatport...\n⏳ Bitte warte einen Moment...")
    
    results = search_beatport(query)
    
    if results is None:
        bot.send_message(message.chat.id, 
                        "❌ Es gab ein Problem bei der Suche. Bitte versuche es später nochmal.")
        return
    
    if not results:
        bot.send_message(message.chat.id, 
                        f"😔 Keine Ergebnisse für '{query}' gefunden.\n\n"
                        "Versuche es mit:\n"
                        "• Anderen Suchbegriffen\n"
                        "• Nur dem Artist-Namen\n"
                        "• Nur dem Track-Titel")
        return
    
    # Ergebnisse formatieren und senden
    response = f"🎵 Gefunden auf Beatport ({len(results)} Ergebnisse):\n\n"
    
    for i, result in enumerate(results, 1):
        response += f"{i}. 🎧 {result['title']}\n"
        if result['artists']:
            response += f"   👤 {result['artists']}\n"
        if result['label']:
            response += f"   🏷️ {result['label']}\n"
        response += f"   🔗 {result['link']}\n\n"
    
    # Nachricht kann zu lang sein, also aufteilen falls nötig
    if len(response) > 4096:
        for i in range(0, len(response), 4096):
            bot.send_message(message.chat.id, response[i:i+4096])
    else:
        bot.send_message(message.chat.id, response)

# Cleanup beim Beenden
def cleanup():
    global driver
    if driver:
        print("Schließe Browser...")
        driver.quit()

# Bot starten
try:
    print("🎵 Beatport Search Bot ist gestartet...")
    print("Bereit für Suchanfragen!")
    print("⚠️ Selenium-Modus: Verwendet echten Browser für JavaScript-Support")
    bot.infinity_polling()
except KeyboardInterrupt:
    print("\nBot wird beendet...")
    cleanup()
except Exception as e:
    print(f"Fehler: {e}")
    cleanup()
