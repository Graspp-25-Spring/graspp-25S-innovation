# scrape_gijiroku
import time
import pandas as pd
import numpy as np
import tqdm
from industries import id2industries_dict
import os
import urllib
import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class common:
    def fetch_yonalog_counts(url: str, wait_seconds: float = 5.0):
        # 1) Configure headless Chrome
        chrome_opts = Options()
        chrome_opts.add_argument("--headless")
        chrome_opts.add_argument("--disable-gpu")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--window-size=1920,1080")
        
        # 2) Launch driver (auto-downloads chromedriver)
        driver = webdriver.Chrome(
            options=chrome_opts
        )
        
        try:
            # 3) Navigate
            driver.get(url)
            
            # 4) Wait for JS to render the chart
            time.sleep(wait_seconds)
            
            # 5) Extract the live chart options
            #    Highcharts.charts[0] is the first (and only) chart on the page
            cfg = driver.execute_script("return Highcharts.charts[0].options;")
            
        finally:
            driver.quit()
        
            return cfg
    
    def get_district_timeseries(cfg: dict, district_name: str):
        """
        Given the Highcharts options dict and a district name (e.g. "全議会" or "福岡県議会"),
        return an ordered dict mapping year → count for that single series.
        """
        # 1947 ~ 2024
        years = list(range(1947, 2025))
        for series in cfg["series"]:
            if district_name in series["name"]:
                counts = np.array(series["data"])[:, 1].astype(int)
                # Ensure both years and counts are Python ints
                return {int(year): int(count) for year, count in zip(years, counts)}
        raise ValueError(f"Series named '{district_name}' not found in chart")

    def refine_industry_name(industry: str) -> list[str]:
        industry = industry.replace("紙、", "")
        pulp_flag = False
        industry = industry.replace("，", "、").replace(",", "、")
        if "公園、" in industry:
            industry = industry.replace("公園、", "")
        if "同" in industry:
            industry = industry.replace("同", industry.split("・")[0])
        if "パルプ" in industry:
            pulp_flag = True
        if "（" in industry:
            industry = industry.split("（")[0]
        if "(" in industry:
            industry = industry.split("(")[0]
        industry = industry.strip()
        if "・" in industry:
            industry = industry.split("・")
            return [ind + "業" if not ind.endswith("業") else ind for ind in industry]
        if "、" in industry:
            if pulp_flag:
                return ["パルプ紙"] + industry.split("、")
            else:
                return industry.split("、")
        if pulp_flag:
            return ["パルプ紙"] + [industry] if industry else []
        return [industry] if industry else []

class gijiroku:
    def build_yonalog_url(queries):
        # URL encode each query and join with ' | '
        encoded_queries = [q if q.startswith('"') else f'"{q}"' for q in queries]
        joined = ' | '.join(encoded_queries)
        encoded = urllib.parse.quote(joined)
        base_url = "https://chiholog.net/yonalog/search.html?meeting_text="
        return f"{base_url}{encoded}"
    
    def get_industry_mention_counts(industry_name: list[str]):
        """
        Given the Highcharts options dict and an industry name (e.g. ["鉱業", "採石業", "砂利採取業"]),
        return a pandas dataframe with year as index and counts as a single column.
        The dataframe will have years from 1947 to 2024.
        """
        # 1947 ~ 2024
        cfg = common.fetch_yonalog_counts(gijiroku.build_yonalog_url(industry_name))
        dic = common.get_district_timeseries(cfg, "全議会")
        df = pd.DataFrame.from_dict(dic, orient='index', columns=['count'])
        return df
    


class kokkai:
    def build_yonalog_url(queries):
        # URL encode each query and join with ' | '
        encoded_queries = [q if q.startswith('"') else f'"{q}"' for q in queries]
        joined = ' | '.join(encoded_queries)
        encoded = urllib.parse.quote(joined)
        base_url = "https://kokalog.net/search.html?speech="
        return f"{base_url}{encoded}"
    
    def get_industry_mention_counts(industry_name: list[str]):
        """
        Given the Highcharts options dict and an industry name (e.g. ["鉱業", "採石業", "砂利採取業"]),
        return a pandas dataframe with year as index and counts as a single column.
        The dataframe will have years from 1947 to 2024.
        """
        # 1947 ~ 2024
        cfg = common.fetch_yonalog_counts(kokkai.build_yonalog_url(industry_name))
        dic = common.get_district_timeseries(cfg, "年の該当件数")
        df = pd.DataFrame.from_dict(dic, orient='index', columns=['count'])
        return df



def main():
    #gijiroku
    URL = "https://chiholog.net/yonalog/search.html?meeting_text=%22%E9%89%B1%E6%A5%AD%22+%7C+%22%E6%8E%A1%E7%9F%B3%E6%A5%AD%22+%7C+%22%E7%A0%82%E5%88%A9%E6%8E%A1%E5%8F%96%E6%A5%AD%22#google_vignette"
    checkpoint_path = "all_df_checkpoint.csv"
    indic = id2industries_dict
    indic2 = {k: gijiroku.refine_industry_name(v) for k, v in indic.items()}
    for k, v in tqdm.tqdm(indic2.items()):
        print(f"Processing {k} -> {v}")
    
    # Load checkpoint if exists
    if os.path.exists(checkpoint_path):
        all_df = pd.read_csv(checkpoint_path, index_col=0)
    else:
        all_df = pd.DataFrame()

    for k, industry in tqdm.tqdm(indic2.items()):
        col_name = ''.join(indic[k])
        if industry == ['合計'] or col_name in all_df.columns:
            continue
        try:
            df = gijiroku.get_industry_mention_counts(industry)
            df.columns = [col_name]
            if all_df.empty:
                all_df = df
            else:
                all_df = all_df.join(df, how='outer')
            # Save checkpoint after each successful column
            all_df.to_csv(checkpoint_path)
        except Exception as e:
            print(f"Error processing {k} ({industry}): {e}")
    
    indic= id2industries_dict
    reversed_indic = {v: k for k, v in indic.items()}
    all_df.loc['industry_id'] = [reversed_indic[col] for col in all_df.columns]
    all_df = all_df.loc[['industry_id'] + [idx for idx in all_df.index if idx != 'industry_id']]
    save_path = os.path.join(settings.DATA_DIR, "gikai_mention.csv")
    all_df.to_csv(save_path)
    
    # kokkai
    URL = "https://kokalog.net/search.html?speech=%22%E9%89%B1%E6%A5%AD%22+%7C+%22%E6%8E%A1%E7%9F%B3%E6%A5%AD%22+%7C+%22%E7%A0%82%E5%88%A9%E6%8E%A1%E5%8F%96%E6%A5%AD%22#google_vignette"
    checkpoint_path = "all_df_checkpoint.csv"
    indic = id2industries_dict
    indic2 = {k: kokkai.refine_industry_name(v) for k, v in indic.items()}
    for k, v in tqdm.tqdm(indic2.items()):
        print(f"Processing {k} -> {v}")
    # Load checkpoint if exists
    if os.path.exists(checkpoint_path):
        all_df = pd.read_csv(checkpoint_path, index_col=0)
    else:
        all_df = pd.DataFrame()

    for k, industry in tqdm.tqdm(indic2.items()):
        col_name = ''.join(indic[k])
        if industry == ['合計'] or col_name in all_df.columns:
            continue
        try:
            df = kokkai.get_industry_mention_counts(industry)
            df.columns = [col_name]
            if all_df.empty:
                all_df = df
            else:
                all_df = all_df.join(df, how='outer')
            # Save checkpoint after each successful column
            all_df.to_csv(checkpoint_path)
        except Exception as e:
            print(f"Error processing {k} ({industry}): {e}")
    indic = id2industries_dict
    reversed_indic = {v: k for k, v in indic.items()}
    all_df.loc['industry_id'] = [reversed_indic[col] for col in all_df.columns]
    all_df = all_df.loc[['industry_id'] + [idx for idx in all_df.index if idx != 'industry_id']]
    save_path = os.path.join(settings.DATA_DIR, "gikai_mention.csv")
    all_df.to_csv(save_path)
    # choose only rows after 2010
    df = pd.read_csv("all_df_checkpoint.csv", index_col=0)
    df = df.loc[df.index >= 2010]
    save_path2 = os.path.join(settings.DATA_DIR, "all_df_checkpoint_2010.csv")
    all_df.to_csv(save_path2)


if __name__ == "__main__":
    main()