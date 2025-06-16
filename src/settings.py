# Set the object required to execute main.py.
import os

# Windows: 'C:/Windows/Fonts/YuGothM.ttc'
# Ubuntu: '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_PATH = '/Library/Fonts/Arial Unicode.ttf'

# base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#folds path
#data path
DOWNLOAD_DIR = "data\\raw"
CLEAND_DIR = "data\cleand"
PANELDATA_DIR = "data\paneldata"

PLOTS_DIR = "image\plots"
TIMESERIES_DIR = "image\\timeseries"
BAR_CHARTS_DIR = "image\\barcharts"


emp_data_path = "data/cleand/3 産業別、売上高経常利益率別常時従業者数"
r_and_d_data_path = "data/cleand/第10表 産業別、企業数、売上高、研究開発費及び売上高比率、受託研究費、研究開発投資、能力開発費"
patent_data_path = "data/cleand/第11表 産業別、企業数、特許権、実用新案権、意匠権別の所有件数及び使用件数"

LABOR_NUMBER_FILE_KEY = "3 産業別、売上高経常利益率別常時従業者数"
RESEARCH_EXPENSE_FILE_KEY = "第10表 産業別、企業数、売上高、研究開発費及び売上高比率、受託研究費、研究開発投資、能力開発費"
PATENT_COUNT_FILE_KEY = "第11表 産業別、企業数、特許権、実用新案権、意匠権別の所有件数及び使用件数"

#outputs files
output_path = "reports"

# YEARS　TO　SCRAPE
YEARS_TO_SCRAPE = list(range(2023, 2009, -1))

#url
BASE_URL_SCRAPE = "https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00550100&kikan=00550&tstat=000001010832&cycle=7&tclass1=000001023579&tclass2="

UNIQUE_STRINGS_SCRAPE = [
    "000001218360", "000001206520", "000001166746", "000001152686",
    "000001141607", "000001131164", "000001117016", "000001105035",
    "000001086216", "000001079305", "000001079316", "000001079315",
    "000001075665", "000001045865", "000001041347", "000001041186",
    "000001023580", "000001023590", "000001079335", "000001079317",
    "000001079296", "000001079336", "000001079355", "000001079337",
    "000001079356", "000001079297", "000001079298", "000001079299",
    "000001079300", "000001079357",
]

# create perfect URL
BASE_URLs_scrape = [f"{BASE_URL_SCRAPE}{unique_str}&tclass3val=0" for unique_str in UNIQUE_STRINGS_SCRAPE]

# target files
TARGET_TABLE_NAMES = [
    "第10表　産業別、企業数、技術導入件数及び技術供与件数",
    "第10表　産業別、企業数、売上高、研究開発費及び売上高比率、受託研究費、研究開発投資、能力開発費",
    "第11表　産業別、企業数、特許権、実用新案権、意匠権別の所有件数及び使用件数",
    "3　産業別、売上高経常利益率別常時従業者数"
]
