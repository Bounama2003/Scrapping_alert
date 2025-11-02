# ...existing code...
from datetime import datetime
from pathlib import Path
import requests
from selectolax.parser import HTMLParser
import re
import sys
from dotenv import load_dotenv
import os
import json

from loguru import logger

load_dotenv()


PRICE_FILEPATH=Path(__file__).parent / "prices.json"

logger.remove()
logger.add(sys.stderr, level="DEBUG")
logger.add("logs/debug.log", level="WARNING", rotation="1 MB")
def write_price_to_file(price: int):
    logger.info(f"Writing price {price} to file")
    if PRICE_FILEPATH.exists():
        with open(PRICE_FILEPATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append({
        "price": price,
        "timestamp": datetime.now().isoformat()
    })
    with open(PRICE_FILEPATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
#print(os.environ["PUSHOVER_TOKEN"])

def get_prices_difference(current_price: int) -> int:
    logger.info("Getting prices difference")
    if PRICE_FILEPATH.exists():
        with open(PRICE_FILEPATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        previous_price = data[-1]["price"]
    else:
        previous_price = current_price

    try:
        return round((previous_price-current_price)/previous_price*100)
    except ZeroDivisionError as e:
        logger.error(f"Division by zero error: {e}")
        raise e

    

def send_alert(message: str):
    logger.info(f"Sending alert with message {message}")
    try:
        response=requests.post("https://api.pushover.net/1/messages.json", 
                  data={
                      "token": os.environ["PUSHOVER_TOKEN"],
                      "user": os.environ["PUSHOVER_USER_KEY"],
                      "message": message
                  })
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to send alert due to: {e}")
        raise e
    
# ...existing code...
def get_current_price(asin: str):
    proxies = {
        "http": os.environ.get("BRIGHTDATA_PROXY"),
        "https": os.environ.get("BRIGHTDATA_PROXY"),
    }
    url = f'https://www.alibaba.com/product-detail/Cellular-sun-solar-tracking-systems-satellite_{asin}.html'
    try:
        response = requests.get(url, proxies={k: v for k, v in proxies.items() if v}, timeout=15, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Couldn't fetch content from: {url} due to: {e}")
        return None

    html_content = response.text
    with open("alibaba.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    tree = HTMLParser(html_content)

    selectors = [
        'meta[property="product:price:amount"]',
        'meta[property="og:price:amount"]',
        'meta[itemprop="price"]',
        'meta[name="price"]',
        '[itemprop="price"]',
        'span[class*="price"]',
        'div[class*="price"]',
        '.price',
        '.product-price',
        '.ma-ref-price',
        '#price',
    ]

    raw_price = None
    for sel in selectors:
        node = tree.css_first(sel)
        if node:
            raw_price = node.attributes.get('content') or (node.text().strip() if node.text() else None)
            if raw_price:
                break

    # fallback: collect all currency occurrences in the whole HTML
    if not raw_price:
        found = re.findall(r'[¥€£$]\s?[\d,]+(?:\.\d+)?', html_content)
        if found:
            raw_price = " ".join(found)

    logger.debug(f"Raw price string: {raw_price}")

    if not raw_price:
        logger.warning("Prix non trouvé dans le HTML")
        return None

    # extraire tous les montants numériques (ex: "$32" et "$19") et choisir le plus bas
    amount_matches = re.findall(r'[¥€£$]\s*([\d,]+(?:\.\d+)?)', raw_price)
    if not amount_matches:
        logger.warning("Aucun montant numérique extrait")
        return None

    try:
        numbers = [float(s.replace(',', '')) for s in amount_matches]
    except ValueError as e:
        logger.error(f"Erreur de parsing des nombres: {e}")
        return None

    unit_price = max(numbers)
    # convertir en int si entier
    if unit_price.is_integer():
        unit_price = int(unit_price)

    logger.info(f"Parsed unit price: {unit_price}")
    return unit_price

def main(asin: str):
    current_price = get_current_price(asin=asin)
    if current_price is None:
        logger.error("Aucun prix courant récupéré — arrêt.")
        return

    price_difference = get_prices_difference(current_price=current_price)
    write_price_to_file(price=current_price)
    if price_difference > 0:
        send_alert(f"Le prix a baissé de {price_difference}% et est maintenant de {current_price} $!")
# ...existing code...

if __name__ == "__main__":
    # soit passe l'ASIN/url en argument, soit utilises les valeurs ci-dessous
    import time
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        asin = "1601404685103"
        #url = f"https://www.alibaba.com/product-detail/Cellular-sun-solar-tracking-systems-satellite_{asin}.html"
    #for i in range(10):
    main(asin)
    #write_price_to_file(100)
    #send_alert("Bonjour le monde")
        #time.sleep(0.5)
# ...existing code...