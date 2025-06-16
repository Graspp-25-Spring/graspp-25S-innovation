# data_processor.py

import os
import glob
import shutil
import time
import re
import requests
import tqdm
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from industries import get_industries_id, get_industries_name

# 設定ファイルをインポート
import settings

class DataScraper:
    """
    指定されたURLからEXCELファイルをスクレイピングしてダウンロードするクラス。
    """
    def __init__(self, base_urls, download_dir, years):
        self.base_urls = base_urls
        self.download_dir = download_dir
        self.years = years
        
        if os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
        os.makedirs(self.download_dir)

    def sanitize_filename(self, text: str) -> str:
        name = re.sub(r"\s+", " ", text.strip())
        return re.sub(r'[\\/:"*?<>|]+', "_", name)

    def scrape_excel_links(self, page_url: str) -> list:
        try:
            resp = requests.get(page_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for span in soup.find_all("span", class_="stat-dl_text"):
                if span.get_text(strip=True) != "EXCEL":
                    continue
                dl_a = span.find_parent("a", href=True)
                if not dl_a:
                    continue
                download_url = urljoin(page_url, dl_a["href"])
                table_a = span.find_previous("a", class_="stat-link_text stat-dataset_list-detail-item-text js-data")
                table_name = table_a.get_text(separator=" ", strip=True) if table_a else download_url.split("/")[-1]
                results.append((download_url, table_name))
            return results
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {page_url}: {e}")
            return []
        except Exception as e:
            print(f"Error parsing {page_url}: {e}")
            return []

    def download_file(self, url: str, table_name: str, year: str):
        ext_match = re.search(r"\.xls[xm]?$", url)
        ext = ext_match.group(0) if ext_match else ".xls"
        safe_name = self.sanitize_filename(table_name)
        timestamp = int(time.time())
        filename = f"{safe_name}_{year}_{timestamp}{ext}"
        path = os.path.join(self.download_dir, filename)
        print(f"↓ Downloading {filename}")
        try:
            r = requests.get(url, stream=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(8 * 1024):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
        except Exception as e:
            print(f"Error saving {filename}: {e}")

    def run_scraper(self):
        for i, base_url in enumerate(self.base_urls):
            print(f"\n▶ Scraping {base_url}")
            items = self.scrape_excel_links(base_url)
            print(f"  → Found {len(items)} EXCEL links")
            for url, table_name in tqdm.tqdm(items):
                if i < len(self.years) and table_name in settings.TARGET_TABLE_NAMES:
                    self.download_file(url, table_name, str(self.years[i]))
                else:
                    # 年とURLの数が合わない場合はスキップ
                    print("Warning: More base URLs than years provided. Skipping year association.")
                    # self.download_file(url, table_name, "")

class BaseCleaner:
    """
    A base class for cleaning data.
    """
    def __init__(self, download_dir, cleaned_dir):
        self.download_dir = download_dir
        self.cleaned_dir = cleaned_dir

    def clean_data(self, target_file_name: str):
        """
        Placeholder for data cleaning method.
        """
        if os.path.exists(self.cleaned_dir + "/" + target_file_name):
            shutil.rmtree(self.cleaned_dir + "/" + target_file_name)
        os.makedirs(self.cleaned_dir + "/" + target_file_name)

        df_dict = {}
        file_paths = [fp for fp in os.listdir(self.download_dir) if target_file_name in fp]
        for file_path in file_paths:
            year = int(file_path.split("_")[1])
            if year < 2020:
                df = self.clean_data_before_2020(file_path, year)
            else:
                df = self.clean_data_after_2020(file_path)
            df_dict[year] = df
        return df_dict
    
    def clean_data_before_2020(self, filename, year):
        """
        Placeholder for data cleaning method for years before 2020.
        """
        raise NotImplementedError("This method should be overridden in subclasses.")
    
    def clean_data_after_2020(self, filename):
        """
        Placeholder for data cleaning method for years after 2020.
        """
        raise NotImplementedError("This method should be overridden in subclasses.")

class ResearchExpenseCleaner(BaseCleaner):
    """
    A class to clean and process research expense data.
    """
    def __init__(self, download_dir, cleaned_dir):
        super().__init__(download_dir, cleaned_dir)

    def clean_data_before_2020(self, filename, year):
        year = int(year)
        print(filename, year)
        df = pd.read_excel(os.path.join(self.download_dir, filename), header=1)
        # Drop all empty columns
        df = df.dropna(axis=1, how='all')

        # 結合されたセルとコピーが必要な回数
        merged_headers = {
            "研究開発": 9,
            "研究開発投資": 1,
            "能力開発": 1,
            "研究開発費": 4,
            "委託研究開発費（百万円）": 2,
            "受託研究費（百万円）": 2,
            "うち、関係会社への委託": 1,
            "うち、関係会社からの受託": 1
        }
        if year == 2010 or year == 2013 or year == 2014:
            merged_headers['研究開発'] = 10
            if year == 2010:
                # Remove rows 0 to 1
                df = df.iloc[2:].reset_index(drop=True)
        else:
            if year < 2011 or year > 2013:
                # Remove rows 0 to 2
                df = df.iloc[2:].reset_index(drop=True)
        if year == 2014:
            # Remove rows 0 to 1
            df = df.iloc[2:].reset_index(drop=True)
    
        # Remove all whitespaces from the dataframe
        df.replace(to_replace=r'\s+', value='', regex=True, inplace=True)
        
        # Handle merged cells based on merged_headers
        for key, value in merged_headers.items():
            # 5行目まではヘッダー行
            for row in range(5):
                if key in df.iloc[row].values:
                    # 結合された行を取得
                    col_index = df.iloc[row].tolist().index(key)
                    for i in range(value):
                        # 結合されたセルの右側の列に値をコピー
                        # 右側の列が空であれば値をコピー
                        if pd.isna(df.iloc[row, col_index + i + 1]):
                            df.iloc[row, col_index + i + 1] = key
                    break
        
        df.iloc[0,0] = "産業"
        # Process the first five rows to create a single header row
        header_rows = df.iloc[:5].fillna('').astype(str)
        header = header_rows.apply(lambda x: '_'.join(x).replace('__', '_').rstrip('_'), axis=0)

        # Update the dataframe with the new header
        df.columns = header
        df = df.iloc[5:].reset_index(drop=True)

        df = df.iloc[5:].reset_index(drop=True)
        df.replace({'X': np.nan, 'x': np.nan, '-': np.nan}, inplace=True)
        return df   

    # 2020年以降のデータ
    def clean_data_after_2020(self, filename):
        df = pd.read_excel(os.path.join(self.download_dir, filename), header=0)
        # Drop all empty columns
        df = df.dropna(axis=1, how='all')
        # drop columns 0, 1, 3
        df = df.drop(columns=[df.columns[0], df.columns[2], df.columns[3]])
        df.iloc[0, 0] = "産業"
        header_rows = df.iloc[:6].fillna('').astype(str)
        header = header_rows.apply(lambda x: '_'.join(x).replace('__', '_').replace('__', '_').rstrip('_').rstrip('_社'), axis=0)
        df.columns = header
        df = df.iloc[5:].reset_index(drop=True)
        df = df.iloc[7:].reset_index(drop=True)
        df.replace({'X': np.nan, 'x': np.nan, '-': np.nan}, inplace=True)
        return df  

class PatentCountCleaner(BaseCleaner):
    """
    A class to clean and process patent count data.
    """
    def __init__(self, download_dir, cleaned_dir):
        super().__init__(download_dir, cleaned_dir)

    def clean_data_before_2020(self, filename, year):
        df = pd.read_excel(os.path.join(self.download_dir, filename), header=1)
        # Remove all whitespaces from the dataframe
        df.replace(to_replace=r'\s+', value='', regex=True, inplace=True)
        df = df.copy()
        # 結合されたセルとコピーが必要な回数
        merged_headers = {
            "特許権": 3,
            "実用新案権": 3,
            "意匠権": 3,
            "件数": 2,
            "使用のもの（含供与）": 1
        }
        
        if year < 2011 or year > 2013:
            # remove column 0
            df = df.drop(columns=df.columns[0])
        if year >= 2014:
            df = df.iloc[2:].reset_index(drop=True)
        
        # Remove all whitespaces from the dataframe
        df.replace(to_replace=r'\s+', value='', regex=True, inplace=True)
        
        # Handle merged cells based on merged_headers
        for key, value in merged_headers.items():
            # 6行目まではヘッダー行
            for row in range(6):
                if key in df.iloc[row].values:
                    # 結合された行を取得
                    col_index = df.iloc[row].tolist().index(key)
                    for i in range(value):
                        # 結合されたセルの右側の列に値をコピー
                        # 右側の列が空であれば値をコピー
                        if pd.isna(df.iloc[row, col_index + i + 1]):
                            df.iloc[row, col_index + i + 1] = key
                    break
        
        # Process the first five rows to create a single header row
        df.iloc[0,0] = "産業"
        header_rows = df.iloc[:6].fillna('').astype(str)
        header = header_rows.apply(lambda x: '_'.join(x).replace('__', '_').replace('__', '_').rstrip('_'), axis=0)

        # Update the dataframe with the new header
        df.columns = header
        df = df.iloc[5:].reset_index(drop=True)

        df = df.iloc[6:].reset_index(drop=True)
        df.replace({'X': np.nan, 'x': np.nan,'Ｘ': np.nan, 'ｘ':np.nan, '***':np.nan, '-': np.nan}, inplace=True)
        return df   

    # 2020年以降の特許データ
    def clean_data_after_2020(self, filename):
        df = pd.read_excel(os.path.join(self.download_dir, filename), header=0)
        # Drop all empty columns
        df = df.dropna(axis=1, how='all')
        # drop columns 0, 1, 3
        df = df.drop(columns=[df.columns[0], df.columns[2], df.columns[3]])
        df.iloc[0,0] = "産業"
        header_rows = df.iloc[:6].fillna('').astype(str)
        header = header_rows.apply(lambda x: '_'.join(x).replace('__', '_').replace('__', '_').rstrip('_').rstrip('_社'), axis=0)
        header = header.str.replace('特許権_件数_所有数_件', '特許権_件数_所有数', regex=True)

        df.columns = header
        df = df.iloc[5:].reset_index(drop=True)
        df = df.iloc[7:].reset_index(drop=True)
        df.replace({'X': np.nan, 'x': np.nan,'Ｘ': np.nan,'ｘ':np.nan, '***':np.nan, '-': np.nan}, inplace=True)
        return df  

class DataCleaner:
    """
    ダウンロードされたEXCELファイルをクリーニングし、処理するクラス。
    """
    def __init__(self, download_dir, cleaned_dir):
        self.download_dir = download_dir
        self.cleaned_dir = cleaned_dir
        self.research_expense_cleaner = ResearchExpenseCleaner(download_dir, cleaned_dir)
        self.patent_count_cleaner = PatentCountCleaner(download_dir, cleaned_dir)
        
    def sanitize_filename(self, text: str) -> str:
        name = re.sub(r"\s+", " ", text.strip())
        return re.sub(r'[\\/:"*?<>|]+', "_", name)
    
    def clean_all_data(self):
        """
        ダウンロードされたすべてのデータをクリーニングする。
        """
        # 各クリーニング関数を呼び出す
        self.clean_labor_number_data(target_file_name=settings.LABOR_NUMBER_FILE_KEY)
        self.ResearchExpenseDict = self.research_expense_cleaner.clean_data(target_file_name=settings.RESEARCH_EXPENSE_FILE_KEY)
        self.PatentCountDict = self.patent_count_cleaner.clean_data(target_file_name=settings.PATENT_COUNT_FILE_KEY)

        # クリーニング済みデータをCSVファイルとして保存
        for key, df_to_save in self.ResearchExpenseDict.items():
            save_dir = os.path.join(self.cleaned_dir, settings.RESEARCH_EXPENSE_FILE_KEY)
            os.makedirs(save_dir, exist_ok=True)
            df_to_save.to_csv(os.path.join(save_dir, f"{key}.csv"), index=True)
            
        for key, df_to_save in self.PatentCountDict.items():
            save_dir = os.path.join(self.cleaned_dir, settings.PATENT_COUNT_FILE_KEY)
            os.makedirs(save_dir, exist_ok=True)
            df_to_save.to_csv(os.path.join(save_dir, f"{key}.csv"), index=True)

    def clean_labor_number_data(self, target_file_name):
        """
        Clean the labor number data from Excel files.
        """
        dfs = {}
        # 1. Get the list of files in the directory
        # 2. Open the workbook and list sheets
        # 3. Read and clean each sheet into a DataFrame
        # 4. Save each DataFrame to a CSV file

        if os.path.exists(self.cleaned_dir + "/" + target_file_name):
            shutil.rmtree(self.cleaned_dir + "/" + target_file_name)
        os.makedirs(self.cleaned_dir + "/" + target_file_name)

        filepaths = [fp for fp in os.listdir(self.download_dir) if target_file_name in fp]
        for file_path in filepaths:
            year = file_path[-8:-4] # This might need adjustment if timestamp is present
            # Adjust to find year correctly if filename format changed due to timestamp
            match = re.search(r"_(\d{4})_\d{10,}\.xls[xm]?$", file_path)
            if match:
                year = match.group(1)
            else:
                # Fallback or error handling if year cannot be extracted
                print(f"Could not extract year from filename: {file_path}. Skipping.")
                continue

            full_path = os.path.join(self.download_dir, file_path)
            # 2. Open the workbook and list sheets
            try:
                xls = pd.ExcelFile(full_path, engine='xlrd')
            except Exception as e:
                print(f"Error opening Excel file {full_path} with xlrd: {e}. Trying openpyxl.")
                try:
                    xls = pd.ExcelFile(full_path, engine='openpyxl')
                except Exception as e_opxl:
                    print(f"Error opening Excel file {full_path} with openpyxl: {e_opxl}. Skipping.")
                    continue

            print("Available sheets:", xls.sheet_names)
            # 3. Read and clean each sheet into a DataFrame
            for sheet in xls.sheet_names:
                try:
                    df = pd.read_excel(
                        full_path,
                        sheet_name=sheet,
                        engine='xlrd' if '.xls' == os.path.splitext(full_path)[1].lower() else 'openpyxl',
                        header=[0, 1],
                        skiprows=0
                    )
                except Exception as e:
                    print(f"Error reading sheet {sheet} from {full_path}: {e}. Skipping sheet.")
                    continue
                
                df.dropna(how='all', inplace=True)
                df.dropna(axis=1, how='all', inplace=True)

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [
                        "_".join([str(c).strip() for c in col if str(c).strip()])
                        for col in df.columns.values
                    ]
                else:
                    df.columns = [str(col).strip() for col in df.columns]

                if year == "2004" or year == "2005":
                    merged_headers = df.iloc[1:5].fillna('').astype(str).agg(' '.join, axis=0).str.strip()
                    df = df.iloc[5:] 
                    df.columns = merged_headers
                    df.columns.values[0] = "年度"
                    df.insert(0, "産業", None)
                    df.loc[~df.iloc[:, 1].str.contains("年度", na=False), "産業"] = df.iloc[:, 1]
                    df.loc[~df.iloc[:, 1].str.contains("年度", na=False), df.columns[1]] = None
                    df.iloc[:, 0] = df.iloc[:, 0].ffill()
                    df = df.dropna(subset=[df.columns[1]])
                elif year == "2007":
                    merged_headers = df.iloc[1:4].fillna('').astype(str).agg(' '.join, axis=0).str.strip()
                    df = df.iloc[4:] 
                    df.columns = merged_headers
                    df.columns.values[0] = "産業"
                    df.columns.values[1] = "年度"
                    df.iloc[:, 0] = df.iloc[:, 0].ffill()
                    df = df.drop(df.columns[2], axis=1)
                elif year == "2009" or year == "2011" or year == "2012" or year == "2013":
                    merged_headers = df.iloc[0:3].fillna('').astype(str).agg(' '.join, axis=0).str.strip()
                    df = df.iloc[3:] 
                    df.columns = merged_headers
                    df.columns.values[0] = "産業"
                    df.columns.values[1] = "年度"
                    df.iloc[:, 0] = df.iloc[:, 0].ffill()
                elif int(year) >= 2020:
                    merged_headers = df.iloc[0:1].fillna('').astype(str).agg(' '.join, axis=0).str.strip()
                    df = df.iloc[3:] 
                    df.columns = merged_headers
                    df.columns.values[1] = "産業"
                    df.columns.values[3] = "年度"
                    df = df.drop(df.columns[0], axis=1)
                else: 
                    merged_headers = df.iloc[2:5].fillna('').astype(str).agg(' '.join, axis=0).str.strip()
                    df = df.iloc[5:] 
                    df.columns = merged_headers
                    df.columns.values[0] = "産業"
                    df.columns.values[1] = "年度"
                    df.iloc[:, 0] = df.iloc[:, 0].ffill()
                    df = df.dropna(subset=[df.columns[1]])
                    if year == "2003" or year == "2006" or year == "2008": 
                        df = df.drop(df.columns[2], axis=1)
                
                try:    
                    df.iloc[:, 1] = df.iloc[:, 1].str.strip()
                except AttributeError:
                    pass
                
                dfs[f"{year}"] = df

        for key, df_to_save in dfs.items():
            df_to_save.to_csv(self.cleaned_dir + "/" + target_file_name + f"/{key}.csv", index=True)

class PanelDataProducer:
    def load_data_from_csv(directory_name: str):
        path = os.path.join(settings.CLEAND_DIR, directory_name, "*.csv")
        files = glob.glob(path)
        if not files:
            print(f"警告: ディレクトリ '{directory_name}' にCSVファイルが見つかりません。")
            return {}
        data_dict = {
            int(os.path.splitext(os.path.basename(f))[0]): pd.read_csv(f, index_col=0)
            for f in files
        }
        return data_dict

    def create_panel_data():
        """
        複数のデータソースを読み込み、マージして一枚のパネルデータを作成・保存する。
        """
        print("--- データ処理を開始します: パネルデータを生成 ---")

        # データをロード
        research_dict = PanelDataProducer.load_data_from_csv(settings.RESEARCH_EXPENSE_FILE_KEY)
        patent_dict = PanelDataProducer.load_data_from_csv(settings.PATENT_COUNT_FILE_KEY)
        labor_dict = PanelDataProducer.load_data_from_csv(settings.LABOR_NUMBER_FILE_KEY)
        if not research_dict or not patent_dict or not labor_dict:
            print("エラー: 必要なデータが読み込めませんでした。処理を中断します。")
            return None, None, None, None

        # パネルデータ作成
        panel_data_list = []
        rows = []
        for year, df_research in research_dict.items():
            randd_df = research_dict[year]
            patent_df = patent_dict.get(year)
            if patent_df is None:
                continue
            
            # Standardize column names for merging
            randd_df = randd_df.rename(columns={
                "産業": "industry",
                "研究開発_研究開発費_計": "randd_total",
                "研究開発_研究開発費_計_百万円": "randd_total",
                "研究開発_売上高（百万円）": "randd_sales",
                "研究開発_売上高_百万円": "randd_sales",
                "企業数": "company_count",
                "研究開発_企業数": "company_count"
            })
            patent_df = patent_df.rename(columns={
                "産業": "industry",
                "特許権_企業数": "patent_company_count",
                "特許権_企業数_社": "patent_company_count",
                "_特許権_企業数": "patent_company_count",
                "特許権_件数_所有数": "patent_count",
                "特許権_件数_所有数_件": "patent_count",
                "_特許権_件数_所有数": "patent_count",
                "実用新案権_企業数": "utility_company_count",
                "実用新案権_企業数_社": "utility_company_count",
                "実用新案権_件数_所有数": "utility_count",
                "実用新案権_件数_所有数_件": "utility_count",
                "意匠権_企業数": "design_company_count",
                "意匠権_企業数_社": "design_company_count",
                "意匠権_件数_所有数": "design_count",
                "意匠権_件数_所有数_件": "design_count"
            })

            # Merge on industry name
            merged = pd.merge(randd_df, patent_df, on="industry", how="inner")

            #if not merged:
             #   print("エラー: マージできるデータがありませんでした。")
              #  return None, None, None, None

            for _, row in merged.iterrows():
                industry_id = get_industries_id(row["industry"])
                industry_name = get_industries_name(industry_id)
                rows.append({
                    "year": year,
                    "industry": industry_name,
                    "industry_id": industry_id,
                    "企業数": row.get("company_count"),
                    "研究開発_売上高_百万円": row.get("randd_sales"),
                    "研究開発_研究開発費_計": row.get("randd_total"),
                    "特許権_企業数": row.get("patent_company_count"),
                    "特許権_件数_所有数": row.get("patent_count"),
                    "実用新案権_企業数": row.get("utility_company_count"),
                    "実用新案権_件数_所有数": row.get("utility_count"),
                    "意匠権_企業数": row.get("design_company_count"),
                    "意匠権_件数_所有数": row.get("design_count"),
                })
        
        panel_data = pd.DataFrame(rows, columns=[
                "year", "industry", "industry_id", "企業数", "研究開発_売上高_百万円",
                "研究開発_研究開発費_計", "特許権_企業数", "特許権_件数_所有数", "実用新案権_企業数",
                "実用新案権_件数_所有数", "意匠権_企業数", "意匠権_件数_所有数"
            ])
        # Remove rows with NaN
        panel_data = panel_data.replace(["", "ｘ", "x", "Ｘ", "***"], np.nan)
        panel_data.dropna(inplace=True)
        # 結果を保存
        os.makedirs(settings.PANELDATA_DIR, exist_ok=True)
        save_path = os.path.join(settings.PANELDATA_DIR, 'パネルデータ.csv')            
        panel_data.to_csv(save_path, index=False)
        
        panel_data.columns = [
            "year", "industry", "industry_id", "company_count", "randd_sales",
            "randd_total", "patent_company_count", "patent_count",
            "utility_company_count", "utility_count", "design_company_count",
            "design_count"
        ]
        # Remove rows with NaN
        panel_data = panel_data.replace(["", "ｘ", "x", "Ｘ", "***"], np.nan)
        panel_data.dropna(inplace=True)
        
        os.makedirs(settings.PANELDATA_DIR, exist_ok=True)
        save_path = os.path.join(settings.PANELDATA_DIR, 'panel_data.csv')
        panel_data.to_csv(save_path, index=False)
    
        print(f"✓ パネルデータを保存しました: {save_path}")
        print("--- データ処理完了 ---")
    
        return panel_data, research_dict, patent_dict, labor_dict

if __name__ == '__main__':
    PanelDataProducer.create_panel_data()
