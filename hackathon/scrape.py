# -*- coding: utf-8 -*-
# file: build_env_hashtag_maps.py

import os
import re
import json
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt
from folium import FeatureGroup
from folium.plugins import HeatMap, HeatMapWithTime, MarkerCluster
from datetime import datetime

# ================== ÇIKIŞ KLASÖRÜ ==================
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)

# ================== 81 İL KOORDİNATLARI ==================
CITY_COORDS = {
    "adana":[37.0000,35.3213],"adiyaman":[37.7648,38.2786],"afyonkarahisar":[38.7569,30.5387],
    "agri":[39.7191,43.0503],"aksaray":[38.3687,34.0370],"amasya":[40.6499,35.8353],
    "ankara":[39.9208,32.8541],"antalya":[36.8969,30.7133],"ardahan":[41.1105,42.7022],
    "artvin":[41.1828,41.8190],"aydin":[37.8450,27.8396],"balikesir":[39.6484,27.8826],
    "bartin":[41.6344,32.3375],"batman":[37.8874,41.1322],"bayburt":[40.2552,40.2249],
    "bilecik":[40.1419,29.9793],"bingol":[38.8854,40.4983],"bitlis":[38.4011,42.1078],
    "bolu":[40.7350,31.6066],"burdur":[37.7203,30.2908],"bursa":[40.1950,29.0600],
    "canakkale":[40.1467,26.4086],"cankiri":[40.6000,33.6167],"corum":[40.5506,34.9556],
    "denizli":[37.7830,29.0963],"diyarbakir":[37.9144,40.2306],"duzce":[40.8438,31.1565],
    "edirne":[41.6772,26.5556],"elazig":[38.6743,39.2220],"erzincan":[39.7505,39.4913],
    "erzurum":[39.9043,41.2679],"eskisehir":[39.7767,30.5206],"gaziantep":[37.0662,37.3833],
    "giresun":[40.9175,38.3874],"gumushane":[40.4607,39.4819],"hakkari":[37.5744,43.7408],
    "hatay":[36.2025,36.1600],"igdir":[39.9237,44.0450],"isparta":[37.7648,30.5566],
    "istanbul":[41.0082,28.9784],"izmir":[38.4192,27.1287],"kahramanmaras":[37.5753,36.9371],
    "karabuk":[41.1956,32.6227],"karaman":[37.1810,33.2150],"kars":[40.6013,43.0975],
    "kastamonu":[41.3887,33.7827],"kayseri":[38.7322,35.4853],"kilis":[36.7184,37.1212],
    "kirikkale":[39.8468,33.5153],"kirklareli":[41.7351,27.2253],"kirsehir":[39.1458,34.1639],
    "kocaeli":[40.8533,29.8815],"konya":[37.8713,32.4846],"kutahya":[39.4242,29.9833],
    "malatya":[38.3552,38.3337],"manisa":[38.6191,27.4289],"mardin":[37.3129,40.7339],
    "mersin":[36.8121,34.6415],"mugla":[37.2153,28.3636],"mus":[38.7433,41.5065],
    "nevsehir":[38.6247,34.7146],"nigde":[37.9667,34.6833],"ordu":[40.9862,37.8797],
    "osmaniye":[37.0742,36.2476],"rize":[41.0255,40.5177],"sakarya":[40.7731,30.3948],
    "samsun":[41.2867,36.3300],"sanliurfa":[37.1645,38.7955],"siirt":[37.9333,41.9500],
    "sinop":[42.0264,35.1551],"sivas":[39.7477,37.0179],"sirnak":[37.5200,42.4543],
    "tekirdag":[40.9773,27.5110],"tokat":[40.3167,36.5500],"trabzon":[41.0027,39.7168],
    "tunceli":[39.1062,39.5480],"usak":[38.6823,29.4082],"van":[38.5012,43.3723],
    "yalova":[40.6549,29.2842],"yozgat":[39.8181,34.8147],"zonguldak":[41.4564,31.7987]
}

# ================== HASHTAG NORMALİZE + KATEGORİ ==================
def normalize_tr(s: str) -> str:
    if not isinstance(s, str): return ""
    s = s.lower()
    # Türkçe karakter sadeleştirme
    tr_map = str.maketrans("şığöüçâîû", "sigouca iu".replace(" ", ""))
    s = s.translate(tr_map)
    return s.strip()

# alias -> base tag
TAG_ALIASES = {
    "iklimkrizi":"iklim","iklimdegisikligi":"iklim","iklimdeğişikliği":"iklim",
    "seragazi":"seragazi","sera_gazi":"seragazi","sera_gazı":"seragazi",
    "hava_kirliligi":"havakirliligi","havaKirliliği":"havakirliligi",
    "sıcakdalgası":"sicakdalgasi","kuraklik":"kuraklik","yangin":"yangin","deprem":"deprem",
    "taşkin":"taskin","taşkın":"taskin","taskin":"taskin","sel":"sel",
    "rüzgarenerjisi":"ruzgarenerjisi","gunesenerjisi":"gunesenerjisi",
    "biyoceşitlilik":"biyocesitlilik","biyoceşitlilik":"biyocesitlilik"
}

# kategori haritası
TAG_CATEGORY = {
    # Afet
    "deprem":"Afet","yangin":"Afet","sel":"Afet","taskin":"Afet",
    # İklim
    "iklim":"İklim","iklimkrizi":"İklim","kuraklik":"İklim","sicakdalgasi":"İklim","havakirliligi":"İklim","seragazi":"İklim","emisyon":"İklim",
    # Çevre
    "orman":"Çevre","su":"Çevre","susorunu":"Çevre","biyocesitlilik":"Çevre","cevre":"Çevre","dog a":"Çevre",
    # Enerji
    "yenilenebilir":"Enerji","gunesenerjisi":"Enerji","ruzgarenerjisi":"Enerji"
}

def base_tag(tag: str) -> str:
    t = normalize_tr(str(tag).lstrip("#"))
    if t in TAG_ALIASES: t = TAG_ALIASES[t]
    return t

def to_category(tag: str) -> str:
    bt = base_tag(tag)
    return TAG_CATEGORY.get(bt, "Diğer")

# ================== SÜTUN ADI ALGILAMA ==================
def pick_cols(df):
    cols = {c.lower().strip(): c for c in df.columns}
    def pick(*names):
        for n in names:
            if n in cols: return cols[n]
        return None
    return {
        "city": pick("city_guess","city","sehir","il"),
        "hashtag": pick("searched_hashtag","hashtag","tag","tags"),
        "date": pick("date","created_at","time"),
        "text": pick("content","text","tweet"),
        "url": pick("url","url_alt","tweet_url"),
        "hashtags_multi": pick("hashtags")  # virgülle birleşik olabilir
    }

# ================== VERİYİ YÜKLE & AGGREGA ==================
def load_and_aggregate():
    # Tercih sırası
    candidates = ["region_agg.csv", "tweets_env_cleaned.csv", "tweets_env_raw.csv"]
    path = next((p for p in candidates if os.path.exists(p)), None)
    if not path:
        raise FileNotFoundError("region_agg.csv veya tweets_env_cleaned.csv ya da tweets_env_raw.csv bulunamadı.")

    df = pd.read_csv(path)
    cols = pick_cols(df)

    # region_agg ise
    if {"city","hashtag"}.issubset(set(map(str.lower, df.columns))) and ("count" in map(str.lower, df.columns)):
        # normalizele
        df = df.rename(columns={cols["city"]:"city", cols["hashtag"]:"hashtag",
                                "count":"count"} if "count" in df.columns else { })
        df["city"] = df["city"].astype(str).str.lower().str.strip()
        df["hashtag"] = df["hashtag"].astype(str)
        df["base_tag"] = df["hashtag"].map(base_tag)
        df["category"] = df["base_tag"].map(to_category)
        # date yoksa sorun değil
        df["lat"] = df["city"].map(lambda c: CITY_COORDS.get(str(c).lower(), [None,None])[0])
        df["lon"] = df["city"].map(lambda c: CITY_COORDS.get(str(c).lower(), [None,None])[1])
        df = df.dropna(subset=["lat","lon"])
        return df, None  # ham yok
    else:
        # raw -> city+hashtag sayımı üret
        if cols["city"] is None:
            raise KeyError("Şehir kolonu (city_guess/city) bulunamadı.")
        # hashtag kaynağı: searched_hashtag > hashtag > hashtags (çoklu)
        hcol = cols["hashtag"]
        if hcol is None:
            # çoklu 'hashtags' varsa ilkini al
            if cols["hashtags_multi"]:
                tmp = df[cols["hashtags_multi"]].fillna("").astype(str).str.split(",", n=1, expand=True)
                df["__first_hash"] = tmp[0].str.strip()
                hcol = "__first_hash"
            else:
                raise KeyError("Hashtag bilgisi bulunamadı (searched_hashtag/hashtag/hashtags).")

        # tarih hamdan gelebilir (HeatMapWithTime için lazım)
        date_col = cols["date"]
        if date_col is not None:
            df["__date"] = pd.to_datetime(df[date_col], errors="coerce").dt.date
        else:
            df["__date"] = pd.NaT

        # normalize
        df["__city"] = df[cols["city"]].astype(str).str.lower().str.strip()
        df["__tag"]  = df[hcol].astype(str).str.lower().str.strip()
        df["__base"] = df["__tag"].map(base_tag)
        df["__cat"]  = df["__base"].map(to_category)

        # Sayım
        agg = (df.dropna(subset=["__city","__base"])
                 .groupby(["__city","__base","__cat"])
                 .size().reset_index(name="count")
                 .rename(columns={"__city":"city","__base":"base_tag","__cat":"category"}))
        agg["lat"] = agg["city"].map(lambda c: CITY_COORDS.get(str(c).lower(), [None,None])[0])
        agg["lon"] = agg["city"].map(lambda c: CITY_COORDS.get(str(c).lower(), [None,None])[1])
        agg = agg.dropna(subset=["lat","lon"]).copy()
        # ham df'yi geri ver (popup için örnek tweet linkleri vs.)
        return agg, df

# ================== HARİTA OLUŞTUR ==================
def build_map(dfg: pd.DataFrame, raw_df: pd.DataFrame=None):
    import numpy as np
    import folium
    from folium.plugins import HeatMap, MarkerCluster
    from folium import FeatureGroup

    # Kolonları garantiye al
    if "base_tag" not in dfg.columns:
        if "hashtag" in dfg.columns:
            dfg["base_tag"] = dfg["hashtag"].map(base_tag)
        else:
            raise ValueError("Giriş çerçevesinde base_tag veya hashtag bulunamadı.")
    if "category" not in dfg.columns:
        dfg["category"] = dfg["base_tag"].map(to_category)

    # Harita
    m = folium.Map(location=[39, 35], zoom_start=6, control_scale=True, tiles="cartodbpositron")

    # Tema katmanları (şimdilik sadece LayerControl için hazırlanıyor)
    cats = dfg["category"].dropna().unique().tolist()
    cat_groups = {c: FeatureGroup(name=f"Tema • {c}", show=True) for c in cats}
    for g in cat_groups.values():
        g.add_to(m)

    # Marker cluster
    cluster = MarkerCluster(name="Şehir Markerları", show=True)
    cluster.add_to(m)

    # Şehirde en çok geçen ilk 5 hashtag (büyüklük ve popup için)
    top5 = (
        dfg.groupby(["city", "base_tag"])["count"].sum()
          .reset_index()
          .sort_values(["city", "count"], ascending=[True, False])
          .groupby("city")
          .head(5)
    )

    # Ham veriden örnek linkleri (tweet URL + içerik) topla (uyarı vermeyen sürüm)
    raw_links = None
    if raw_df is not None:
        rc = raw_df.copy()

        # city normalize
        if "city_guess" in rc.columns:
            rc["__city"] = rc["city_guess"].astype(str).str.lower().str.strip()
        elif "city" in rc.columns:
            rc["__city"] = rc["city"].astype(str).str.lower().str.strip()
        else:
            rc["__city"] = np.nan

        # hashtag kaynağı
        hash_col = None
        if "searched_hashtag" in rc.columns:
            hash_col = "searched_hashtag"
        elif "hashtag" in rc.columns:
            hash_col = "hashtag"
        elif "hashtags" in rc.columns:
            tmp = rc["hashtags"].fillna("").astype(str).str.split(",", n=1, expand=True)
            rc["__first_hash"] = tmp[0].str.strip()
            hash_col = "__first_hash"

        if hash_col is not None:
            rc["__base"] = rc[hash_col].astype(str).map(base_tag)
            rc2 = rc.dropna(subset=["__city", "__base"])
            # küçük sözlük üret: (city, base_tag) -> ilk 2 örnek
            raw_links = {}
            for (ct, bt), g in rc2.groupby(["__city", "__base"]):
                ex = g.dropna(subset=["url"])[["url", "content"]].head(2).to_dict("records")
                raw_links[(ct, bt)] = ex

    # Şehir marker'ları
    for city, grp in dfg.groupby("city"):
        lat, lon = grp["lat"].iloc[0], grp["lon"].iloc[0]

        # Top 5 tag
        subt = top5[top5["city"] == city]
        if not subt.empty:
            lines = [f"{r.base_tag}: {int(r.count)}" for r in subt.itertuples(index=False)]
            top_html = "<br>".join(lines)
        else:
            top_html = "—"

        # Örnek linkler: baskın tag'den 1-2 tweet
        link_html = "—"
        if raw_links is not None and not subt.empty:
            dom_tag = subt.iloc[0]["base_tag"]
            key = (city, dom_tag)
            if key in raw_links and len(raw_links[key]) > 0:
                items = []
                for s in raw_links[key]:
                    u = s.get("url", "")
                    c = s.get("content", "")
                    if isinstance(c, str) and len(c) > 140:
                        c = c[:140] + "…"
                    items.append(f'<a href="{u}" target="_blank">tweet</a>: {c}')
                link_html = "<br>".join(items)

        popup_html = folium.IFrame(html=f"""
            <div style="font-size:13px">
              <b>{city.title()}</b><br>
              <b>Top Hashtag'ler:</b><br>{top_html}<br>
              <b>Örnekler:</b><br>{link_html}
            </div>
        """, width=320, height=220)

        folium.CircleMarker(
            location=[lat, lon],
            radius=float(np.clip(grp["count"].sum() * 0.15, 4, 22)),
            popup=folium.Popup(popup_html),
            color="#1f77b4",
            fill=True,
            fill_opacity=0.6
        ).add_to(cluster)

    # Toplam ısı haritası
    heat_data = dfg[["lat", "lon", "count"]].values.tolist()
    HeatMap(heat_data, name="Isı Haritası (Toplam)", radius=22, blur=18, max_zoom=6).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    map_path = os.path.join(OUT_DIR, "tweets_map.html")
    m.save(map_path)
    print(f"✅ Harita kaydedildi: {map_path}")

# ================== GRAFİK & RAPOR ==================
def build_charts_and_reports(dfg: pd.DataFrame):
    # Şehir toplamları
    city_totals = dfg.groupby("city")["count"].sum().sort_values(ascending=False).head(20)
    plt.figure(figsize=(10,6))
    city_totals.plot(kind="bar")
    plt.title("Şehirlere Göre Toplam Tweet (İlk 20)")
    plt.ylabel("Tweet Sayısı"); plt.xlabel("Şehir"); plt.xticks(rotation=45)
    plt.tight_layout()
    cpath = os.path.join(OUT_DIR, "city_totals.png")
    plt.savefig(cpath, dpi=160); plt.close()
    print(f"📊 Kaydedildi: {cpath}")

    # Hashtag (base_tag) toplamları
    tag_totals = dfg.groupby("base_tag")["count"].sum().sort_values(ascending=False).head(25)
    plt.figure(figsize=(10,6))
    tag_totals.plot(kind="bar")
    plt.title("En Çok Kullanılan Hashtag'ler (Top 25)")
    plt.ylabel("Tweet Sayısı"); plt.xlabel("Hashtag"); plt.xticks(rotation=45)
    plt.tight_layout()
    tpath = os.path.join(OUT_DIR, "tag_totals.png")
    plt.savefig(tpath, dpi=160); plt.close()
    print(f"📊 Kaydedildi: {tpath}")

    # Şehir başına en baskın hashtag
    top_per_city = (dfg.groupby(["city","base_tag"])["count"].sum()
                      .reset_index()
                      .sort_values(["city","count"], ascending=[True, False]))
    top_per_city = top_per_city.groupby("city").head(1).reset_index(drop=True)
    csv1 = os.path.join(OUT_DIR, "top_hashtag_per_city.csv")
    top_per_city.to_csv(csv1, index=False, encoding="utf-8-sig")
    print(f"🗂️ Kaydedildi: {csv1}")

    # Günlük toplamlar (varsa)
    if "date" in dfg.columns:
        dfg["__date"] = pd.to_datetime(dfg["date"], errors="coerce").dt.date
        daily = dfg.dropna(subset=["__date"]).groupby("__date")["count"].sum().reset_index()
        if not daily.empty:
            csv2 = os.path.join(OUT_DIR, "daily_counts.csv")
            daily.to_csv(csv2, index=False, encoding="utf-8-sig")
            print(f"🗂️ Kaydedildi: {csv2}")

def main():
    dfg, raw = load_and_aggregate()
    # dfg kolon standardizasyonu
    if "hashtag" in dfg.columns and "base_tag" not in dfg.columns:
        dfg["base_tag"] = dfg["hashtag"].map(base_tag)
    if "category" not in dfg.columns:
        dfg["category"] = dfg["base_tag"].map(to_category)
    # Tarih bilgisi region_agg'ta yoksa None kalır, sorun değil
    if "date" not in dfg.columns:
        dfg["date"] = np.nan

    build_map(dfg, raw_df=raw)
    build_charts_and_reports(dfg)

if __name__ == "__main__":
    main()
