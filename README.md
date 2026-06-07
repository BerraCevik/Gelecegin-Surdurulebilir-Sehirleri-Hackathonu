# 🌍 Sustainable Cities Environmental Analysis Dashboard

A Python-based data analysis and visualization project developed for the **TEKNOFEST 2025 "Geleceğin Sürdürülebilir Şehirleri" (Future Sustainable Cities) Hackathon** — where the team placed **4th in the finals** held in Istanbul.

---

## 🏆 About the Competition

This project was submitted to the **TEKNOFEST 2025 Geleceğin Sürdürülebilir Şehirleri Hackathonu**, organized under the theme of building smarter, more sustainable, and livable cities through innovative digital solutions. The hackathon focused on areas such as post-disaster management, environmental data analysis, and sustainable urban planning.

Out of all participating teams, this project reached the **finals in Istanbul** and finished **4th place**.

---

## 🚀 About the Project

The project collects environment- and climate-themed tweets from Twitter, maps them to Turkish cities, and presents city-based environmental sentiment analysis through an interactive dashboard with maps, charts, and data tables. The goal is to gain insight into which cities are most actively discussing environmental issues and what topics are trending in each city.

---

## ✨ Features

- 🐦 **Twitter Data Collection** — Gathered environment and climate-related tweets using the Twitter API
- 🏙️ **City Mapping** — Matched tweets to Turkish cities using regex-based city detection
- 🗺️ **Interactive Map** — Visualized tweet distribution and environmental activity across cities on an interactive map
- 📊 **Dashboard & Charts** — Built an analysis dashboard with graphs and data tables for city-based comparisons
- 🧹 **Data Cleaning** — Applied text preprocessing and cleaning pipelines for reliable analysis
- 🔍 **NLP & Pattern Matching** — Used regex-based methods to extract and classify environmental topics

---

## 🛠️ Tech Stack

| Technology | Description |
|------------|-------------|
| **Python** | Core programming language |
| **Twitter API** | Data collection source |
| **Pandas** | Data processing and cleaning |
| **Regex (re)** | City name extraction and text matching |
| **Plotly / Folium** | Interactive charts and map visualization |
| **Streamlit / Dash** | Dashboard interface |

---

## 🔄 Project Workflow

```
Twitter API
    │
    ▼
Tweet Collection (environment & climate keywords)
    │
    ▼
Data Cleaning & Preprocessing
    │
    ▼
Regex-Based City Matching (Turkish cities)
    │
    ▼
City-Based Analysis & Aggregation
    │
    ▼
Interactive Dashboard (Map + Charts + Table)
```

---

## 📁 Project Structure

```
Gelecegin-Surdurulebilir-Sehirleri-Hackathonu/
├── data/                  # Raw and cleaned tweet datasets
├── notebooks/             # Exploratory analysis notebooks
├── src/                   # Core scripts (collection, cleaning, matching)
├── dashboard/             # Dashboard and visualization code
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.8+
- Twitter Developer Account (API keys required)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BerraCevik/Gelecegin-Surdurulebilir-Sehirleri-Hackathonu.git
   cd Gelecegin-Surdurulebilir-Sehirleri-Hackathonu
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Twitter API credentials:**
   Create a `.env` file in the root directory:
   ```
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   ```

5. **Run the dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```

---

## 🏅 Achievement

> 🎉 **4th Place** — TEKNOFEST 2025 Geleceğin Sürdürülebilir Şehirleri Hackathonu Finals, Istanbul

---

## 📄 License

This project is open source and developed for educational and competition purposes.
