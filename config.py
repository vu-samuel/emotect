import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# === Projektverzeichnis erkennen ===
BASE_DIR = Path(__file__).resolve().parent

# === .env laden ===
load_dotenv(dotenv_path=BASE_DIR / ".env")

# === API KEYS ===
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENFIGI_API_KEY = os.getenv("OPENFIGI_API_KEY")
YFINANCE_PROXY = os.getenv("YFINANCE_PROXY")

# === Ordnerstruktur ===
DATA_DIR = BASE_DIR / "data"
RAW_NEWS_DIR = DATA_DIR / "raw" / "headlines"
STOCK_PRICE_DIR = DATA_DIR / "raw" / "stock_prices"
PROCESSED_DIR = DATA_DIR / "processed"
REPORT_DIR = DATA_DIR / "reports"
LOG_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"
EMOTECT_LOGO = ASSETS_DIR / "emotect_logo.png"

# === Ausgabedateien ===
FULL_SENTIMENT_FILE = PROCESSED_DIR / "full_sentiment.csv"
Z_SCORE_FILE = PROCESSED_DIR / "z_scores.csv"

# === Analyse-Zeitraum ===
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime.now()


DUMMY_HEADLINES_DIR = BASE_DIR / "data" / "raw" / "dummy_headlines"
DUMMY_FULL_SENTIMENT_FILE = PROCESSED_DIR / "dummy_full_sentiment.csv"
DUMMY_Z_SCORE_FILE = PROCESSED_DIR / "dummy_z_scores.csv"

# === Hilfsfunktionen für Dateinamen ===
def get_news_filename(ticker: str) -> Path:
    #return RAW_NEWS_DIR / f"{ticker}_trusted.json"
    return DUMMY_HEADLINES_DIR / f"{ticker}_trusted.json"

def get_stock_price_filename(ticker: str) -> Path:
    return STOCK_PRICE_DIR / f"{ticker}.csv"

# === Logging vorbereiten (optional verwendbar in Modulen) ===
def setup_logging(logfile_name="emotect.log"):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / logfile_name),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("EMOTECT")

# === Dynamische Tickerliste aus COMPANY_INFO ===
def get_all_tickers(with_suffix: bool = False):
    from config import COMPANY_INFO
    return [f"{t}.DE" if with_suffix else t for t in COMPANY_INFO.keys()]



REPORT_TEMPLATE_FILE = BASE_DIR / "templates" / "report_template.html"

'''

# === Firmeninformationen ===
COMPANY_INFO = {
    "ADS":  {
        "name":"adidas AG",
        "city":"Herzogenaurach",
        "isin":"DE000A1EWWW0",
        "sector":"Consumer Discretionary",
        "lat":49.5678,
        "lon":10.9028
        },
    "AIR":  {
        "name":"Airbus SE",
        "city":"Leiden",
        "isin":"NL0000235190",
        "sector":"Aerospace & Defence",
        "lat":52.1601,
        "lon":4.4970
             },
    "ALV":  {
        "name":"Allianz SE",
        "city":"München",
        "isin":"DE0008404005",
        "sector":"Financials",
        "lat":48.1535,
        "lon":11.5586
        },
    "BAS":  {
        "name":"BASF SE",
        "city":"Ludwigshafen",
        "isin":"DE000BASF111",
        "sector":"Materials",
        "lat":49.4861,
        "lon":8.4464
        },
    "BAYN": {
        "name":"Bayer AG",
        "city":"Leverkusen",
        "isin":"DE000BAY0017",
        "sector":"Health Care",
        "lat":51.0333,
        "lon":6.9833
        },
    "BEI":  {
        "name":"Beiersdorf AG",
        "city":"Hamburg",
        "isin":"DE0005200000",
        "sector":"Consumer Staples",
        "lat":53.5637,
        "lon":9.9841
        },
    "BMW":  {
        "name":"BMW AG",
        "city":"München",
        "isin":"DE0005190003",
        "sector":"Consumer Discretionary",
        "lat":48.1767,
        "lon":11.5565
        },
    "BNR":  {
        "name":"Brenntag SE",
        "city":"Essen",
        "isin":"DE000A1DAHH0",
        "sector":"Chemicals",
        "lat":51.4556,
        "lon":7.0116
        },
    "CBK":  {
        "name":"Commerzbank AG",
        "city":"Frankfurt am Main",
        "isin":"DE000CBK1001",
        "sector":"Financials",
        "lat":50.1109,
        "lon":8.6821
        },
    "CON":  {
        "name":"Continental AG",
        "city":"Hannover",
        "isin":"DE0005439004",
        "sector":"Consumer Discretionary"
        ,"lat":52.3790,
        "lon":9.7580
        },
    "1COV": {
        "name":"Covestro AG",
        "city":"Leverkusen",
        "isin":"DE0006062144",
        "sector":"Materials",
        "lat":51.0333,
        "lon":6.9833
        },
    "DBK":  {
        "name":"Deutsche Bank AG",
        "city":"Frankfurt am Main",
        "isin":"DE0005140008",
        "sector":"Financials",
        "lat":50.1109,
        "lon":8.6821
        },
    "DB1":  {
        "name":"Deutsche Börse AG",
        "city":"Frankfurt am Main",
        "isin":"DE0005810055",
        "sector":"Financials",
        "lat":50.1109,
        "lon":8.6821
        },
    "DHL":  {
        "name":"DHL Group",
        "city":"Bonn",
        "isin":"DE0005552004",
        "sector":"Industrials",
        "lat":50.7374,
        "lon":7.0982
        },
    "DTE":  {
        "name":"Deutsche Telekom AG",
        "city":"Bonn",
        "isin":"DE0005557508",
        "sector":"Communication Services",
        "lat":50.7374,
        "lon":7.0982
        },
    "DWNI": {
        "name":"Deutsche Wohnen SE",
        "city":"Berlin",
        "isin":"DE000A0HN5C6",
        "sector":"Real Estate",
        "lat":52.5200,
        "lon":13.4050
        },
    "DTG":  {
        "name":"Daimler Truck Holding AG",
        "city":"Stuttgart",
        "isin":"DE000DTR0CK7",
        "sector":"Automotive",
        "lat":48.7784,
        "lon":9.1798
        },
    "ENR":  {
        "name":"Siemens Energy AG",
        "city":"München",
        "isin":"DE000ENER6Y0",
        "sector":"Industrials",
        "lat":48.1351,
        "lon":11.5820
        },
    "EOAN": {
        "name":"E.ON SE",
        "city":"Essen",
        "isin":"DE000ENAG999",
        "sector":"Utilities",
        "lat":51.4508,
        "lon":7.0131
        },
    "FRE":  {
        "name":"Fresenius SE & Co. KGaA",
        "city":"Bad Homburg",
        "isin":"DE0005785604",
        "sector":"Health Care",
        "lat":50.2268,
        "lon":8.6171
        },
    "FME":  {
        "name":"Fresenius Medical Care AG & Co. KGaA",
        "city":"Bad Homburg",
        "isin":"DE0005785802",
        "sector":"Health Care",
        "lat":50.2268,
        "lon":8.6171
        },
    "HNR1": {
        "name":"Hannover Rück SE",
        "city":"Hannover",
        "isin":"DE0008402215",
        "sector":"Financials",
        "lat":52.3719,
        "lon":9.7332
        },
    "HEI":  {
        "name":"Heidelberg Materials AG",
        "city":"Heidelberg",
        "isin":"DE0006047004",
        "sector":"Materials",
        "lat":49.3988,
        "lon":8.6724
        },
    "HEN3": {
        "name":"Henkel AG & Co. KGaA",
        "city":"Düsseldorf",
        "isin":"DE0006048432",
        "sector":"Consumer Staples",
        "lat":51.2277,
        "lon":6.7735
        },
    "IFX":  {
        "name":"Infineon Technologies AG",
        "city":"Neubiberg",
        "isin":"DE0006231004",
        "sector":"Information Technology",
        "lat":48.0736,
        "lon":11.6581
        },
    "LIN":  {
        "name":"Linde plc",
        "city":"Guildford",
        "isin":"IE00BZ12WP82",
        "sector":"Materials",
        "lat":51.2362,
        "lon":-0.5704
        },
    "MRK":  {
        "name":"Merck KGaA",
        "city":"Darmstadt",
        "isin":"DE0006599905",
        "sector":"Health Care",
        "lat":49.8728,
        "lon":8.6512
        },
    "MTX":  {
        "name":"MTU Aero Engines AG",
        "city":"München",
        "isin":"DE000A0D9PT0",
        "sector":"Industrials",
        "lat":48.1984,
        "lon":11.6141
        },
    "MUV2": {
        "name":"Münchener Rückversicherungs-Gesellschaft AG",
        "city":"München",
        "isin":"DE0008430026",
        "sector":"Financials",
        "lat":48.1486,
        "lon":11.5605
        },
    "PAH3": {
        "name":"Porsche Automobil Holding SE",
        "city":"Stuttgart",
        "isin":"DE000PAH0038",
        "sector":"Consumer Discretionary",
        "lat":48.7784,
        "lon":9.1798
        },
    "PUM":  {
        "name":"Puma SE",
        "city":"Herzogenaurach",
        "isin":"DE0006969603",
        "sector":"Consumer Discretionary",
        "lat":49.5677,
        "lon":10.9017
        },
    "QIA":  {
        "name":"Qiagen N.V.",
        "city":"Venlo",
        "isin":"NL0012169213",
        "sector":"Health Care",
        "lat":51.4408,
        "lon":5.4788
        },
    "RHM":  {
        "name":"Rheinmetall AG",
        "city":"Düsseldorf",
        "isin":"DE0007030009",
        "sector":"Industrials",
        "lat":51.2277,
        "lon":6.7735
        },
    "RWE":  {
        "name":"RWE AG",
        "city":"Essen",
        "isin":"DE0007037129",
        "sector":"Utilities",
        "lat":51.4508,
        "lon":7.0131
        },
    "SAP":  {
        "name":"SAP SE",
        "city":"Walldorf",
        "isin":"DE0007164600",
        "sector":"Information Technology",
        "lat":49.2933,
        "lon":8.6417
        },
    "SIE":  {
        "name":"Siemens AG",
        "city":"München",
        "isin":"DE0007236101",
        "sector":"Industrials",
        "lat":48.1351,
        "lon":11.5820
        },
    "SHL":  {
        "name":"Siemens Healthineers AG",
        "city":"Erlangen",
        "isin":"DE000SHL1006",
        "sector":"Health Care",
        "lat":49.6020,
        "lon":11.0037
        },
    "SRT3": {
        "name":"Sartorius AG",
        "city":"Göttingen",
        "isin":"DE0007165604",
        "sector":"Health Care",
        "lat":51.5359,
        "lon":9.9356
        },
    "SY1":  {
        "name":"Symrise AG",
        "city":"Holzminden",
        "isin":"DE000SYM9999",
        "sector":"Materials",
        "lat":51.8250,
        "lon":9.4592
        },
    "VNA":  {
        "name":"Vonovia SE",
        "city":"Bochum",
        "isin":"DE000A1ML7J1",
        "sector":"Real Estate",
        "lat":51.4818,
        "lon":7.2197
        },
    "VOW3": {
        "name":"Volkswagen AG",
        "city":"Wolfsburg",
        "isin":"DE0007664039",
        "sector":"Consumer Discretionary",
        "lat":52.4227,
        "lon":10.7865
        },
    "ZAL":  {
        "name":"Zalando SE",
        "city":"Berlin",
        "isin":"DE000ZAL1111",
        "sector":"Consumer Discretionary",
        "lat":52.5200,
        "lon":13.4050
        }

}
'''
#ONLY FOR TESTING __ PLEASE REMOVE

COMPANY_INFO = {
    "1COV": {"name": "Covestro", "lat": 51.0275, "lon": 6.9856},
    "ADS": {"name": "Adidas", "lat": 49.4861, "lon": 10.9266},
    "AIR": {"name": "Airbus", "lat": 48.5383, "lon": 7.7349},
    "ALV": {"name": "Allianz", "lat": 48.1533, "lon": 11.5533},
    "BAS": {"name": "BASF", "lat": 49.5216, "lon": 8.431},
    "BAYN": {"name": "Bayer", "lat": 51.0153, "lon": 7.0031},
    "BEI": {"name": "Beiersdorf", "lat": 53.5653, "lon": 9.9848},
    "BMW": {"name": "BMW", "lat": 48.1761, "lon": 11.5566},
    "BNR": {"name": "Brenntag", "lat": 51.45, "lon": 6.9833},
    "CBK": {"name": "Commerzbank", "lat": 50.1109, "lon": 8.6821},
    "CON": {"name": "Continental", "lat": 52.3794, "lon": 9.7558},
    "DAI": {"name": "Mercedes-Benz Group", "lat": 48.7758, "lon": 9.1829},
    "DB1": {"name": "Deutsche Börse", "lat": 50.1208, "lon": 8.6696},
    "DBK": {"name": "Deutsche Bank", "lat": 50.1115, "lon": 8.6785},
    "DTE": {"name": "Deutsche Telekom", "lat": 50.7323, "lon": 7.0998},
    "ENR": {"name": "Siemens Energy", "lat": 52.52, "lon": 13.405},
    "EOAN": {"name": "E.ON", "lat": 51.45, "lon": 7.0167},
    "FRE": {"name": "Fresenius", "lat": 50.1431, "lon": 8.7416},
    "HEI": {"name": "Heidelberg Materials", "lat": 49.4094, "lon": 8.6942},
    "HEN3": {"name": "Henkel", "lat": 51.2277, "lon": 6.7735},
    "HFG": {"name": "HelloFresh", "lat": 52.52, "lon": 13.405},
    "IFX": {"name": "Infineon Technologies", "lat": 48.2892, "lon": 11.624},
    "LEG": {"name": "LEG Immobilien", "lat": 51.45, "lon": 6.7833},
    "LIN": {"name": "Linde", "lat": 50.1109, "lon": 8.6821},
    "MRK": {"name": "Merck", "lat": 49.8728, "lon": 8.6512},
    "MTX": {"name": "MTU Aero Engines", "lat": 48.3538, "lon": 11.7861},
    "MUV2": {"name": "Münchener Rück", "lat": 48.1351, "lon": 11.5819},
    "PAH3": {"name": "Porsche", "lat": 48.8345, "lon": 9.1806},
    "PUM": {"name": "Puma", "lat": 49.4883, "lon": 11.0064},
    "QIA": {"name": "Qiagen", "lat": 50.7774, "lon": 6.0886},
    "RHM": {"name": "Rheinmetall", "lat": 51.2277, "lon": 6.7735},
    "RWE": {"name": "RWE", "lat": 51.45, "lon": 7.0167},
    "SAP": {"name": "SAP", "lat": 49.2933, "lon": 8.6417},
    "SHL": {"name": "Siemens Healthineers", "lat": 49.4717, "lon": 11.0026},
    "SIE": {"name": "Siemens", "lat": 48.1351, "lon": 11.5819},
    "SRT3": {"name": "Sartorius", "lat": 51.5322, "lon": 9.9356},
    "SY1": {"name": "Symrise", "lat": 51.8846, "lon": 10.5582},
    "VNA": {"name": "Vonovia", "lat": 51.4818, "lon": 7.2197},
    "VOW3": {"name": "Volkswagen", "lat": 52.4227, "lon": 10.7865},
    "ZAL": {"name": "Zalando", "lat": 52.531, "lon": 13.3849}
}



# Automatisch erzeugtes Mapping: Firmenname → Ticker
DAX_TICKERS = {v["name"]: k for k, v in COMPANY_INFO.items()}