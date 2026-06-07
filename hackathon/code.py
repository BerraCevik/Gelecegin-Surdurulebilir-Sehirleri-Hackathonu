import json, re, asyncio, time
import pandas as pd
from twikit import Client
from random import uniform

# === AYARLAR ===
COOKIES_JSON = r"C:\Users\ASUS1\Desktop\cookies.json"
PRODUCTS = ["Latest", "Top"]        # <- İstersen sadece "Latest" da kullanabilirsin
LIMIT_PER_TAG = 200  # veya 250, yani toplamda ~8800–11.000 tweet
SLEEP_EVERY = 3
SLEEP_SECONDS = (15, 30)
            # sleep aralığı (random: min, max)

HASHTAGS = [
    "#iklimkrizi", "#iklim", "#iklimdegisikligi", "#iklimdeğişikliği",
    "#kuraklık", "#sıcaklık", "#sıcakdalgası", "#havaKirliliği", "#havakirliliği",
    "#seragazı", "#seragazi", "#emisyon", "#orman", "#yangın", "#sel", "#taşkın",
    "#su", "#susorunu", "#biyoçeşitlilik", "#yenilenebilir", "#güneşenerjisi", "#rüzgarenerjisi"
]

TR_CITIES = [  # normalize kullanıyoruz
    "adana","adiyaman","afyonkarahisar","agri","aksaray","amasya","ankara","antalya","ardahan","artvin",
    "aydin","balikesir","bartin","batman","bayburt","bilecik","bingol","bitlis","bolu","burdur","bursa",
    "canakkale","cankiri","corum","denizli","diyarbakir","duzce","edirne","elazig","erzincan","erzurum",
    "eskisehir","gaziantep","giresun","gumushane","hakkari","hatay","igdir","isparta","istanbul","izmir",
    "kahramanmaras","karabuk","karaman","kars","kastamonu","kayseri","kilis","kirikkale","kirklareli",
    "kirsehir","kocaeli","konya","kutahya","malatya","manisa","mardin","mersin","mugla","mus","nevsehir",
    "nigde","ordu","osmaniye","rize","sakarya","samsun","sanliurfa","siirt","sinop","sivas","sirnak","tekirdag",
    "tokat","trabzon","tunceli","usak","van","yalova","yozgat","zonguldak"
]
CITY_ALIASES = {
    "k.maraş":"kahramanmaras","k.maras":"kahramanmaras","maras":"kahramanmaras",
    "mersın":"mersin","ıstanbul":"istanbul","izmir":"izmir","ankara":"ankara","bursa":"bursa",
    "sakarya":"sakarya","kocaeli":"kocaeli","adıyaman":"adiyaman","çanakkale":"canakkale",
    "şırnak":"sirnak","şanlıurfa":"sanliurfa","muğla":"mugla","kütahya":"kutahya"
}

def normalize(s: str) -> str:
    if not s: return ""
    s = s.lower()
    tr_map = str.maketrans("çıüğöşâîû", "ciugosa iu".replace(" ", ""))
    s = s.translate(tr_map)
    return s

def guess_city(text: str):
    if not text: return None
    t = normalize(text)
    for k,v in CITY_ALIASES.items():
        if k in t: t = t.replace(k, v)
    for c in TR_CITIES:
        if re.search(rf"\b{c}\b", t):
            return c
    return None

def cookie_dict_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict): return data
    return {c["name"]: c["value"] for c in data if "name" in c and "value" in c}

async def fetch_for_tag(client: Client, tag: str, product: str, limit: int):
    tweets = await client.search_tweet(f"{tag} lang:tr", product=product, count=limit)
    print(f"[DEBUG] Gerçek çekilen tweet sayısı: {len(tweets)} — tag: {tag}, product: {product}")
    rows = []
    for t in tweets:
        user = getattr(t, "user", None)
        entities = getattr(t, "entities", None)
        hashtags = ""
        if entities and getattr(entities, "hashtags", None):
            try: hashtags = ",".join([h.text for h in entities.hashtags])
            except: pass
        user_loc = getattr(user, "location", None) if user else None
        city = guess_city(user_loc) or guess_city(getattr(t, "text", ""))
        rows.append({
            "searched_hashtag": tag,
            "product": product,
            "id": t.id,
            "date": t.created_at,
            "content": t.text,
            "username": getattr(user, "name", None) if user else None,
            "screen_name": getattr(user, "screen_name", None) if user else None,
            "user_location": user_loc,
            "city_guess": city,
            "hashtags": hashtags,
            "url": f"https://twitter.com/{getattr(user,'screen_name','')}/status/{t.id}" if user else None,
            "url_alt": f"https://x.com/i/web/status/{t.id}",
        })
    return rows

async def main():
    client = Client("tr-TR")
    client.set_cookies(cookie_dict_from_json(COOKIES_JSON))
    all_rows = []

    for i, tag in enumerate(HASHTAGS):
        for product in PRODUCTS:
            rows = await fetch_for_tag(client, tag, product, LIMIT_PER_TAG)
            all_rows.extend(rows)
            print(f"✓ {tag} ({product}): {len(rows)} tweet")

        if (i + 1) % SLEEP_EVERY == 0:
            sleep_time = round(uniform(*SLEEP_SECONDS), 2)
            print(f"⏸️  Uyku: {sleep_time} saniye...")
            time.sleep(sleep_time)

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["id"])
    df.to_csv("tweets_env_raw.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ RAW kaydedildi: tweets_env_raw.csv — {len(df)} kayıt")

    dfg = (df.dropna(subset=["city_guess"])
             .groupby(["city_guess","searched_hashtag"])
             .size()
             .reset_index(name="count")
             .sort_values(["city_guess","count"], ascending=[True, False]))
    dfg.to_csv("region_agg.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Bölgesel özet kaydedildi: region_agg.csv — {len(dfg)} satır")

if __name__ == "__main__":
    asyncio.run(main())