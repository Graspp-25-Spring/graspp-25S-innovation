# produce plots
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib
import sys

from matplotlib.font_manager import FontProperties
from industries import get_industries_id, get_industries_name
import settings
import data_processor


def output_visualization(research_expense_dict, patent_count_dict, year=2020):
    """
    Output visualization of the cleaned data.
    """
    print(f"\nGenerating visualizations for year {year}...")
        
    os.makedirs(settings.PLOTS_DIR, exist_ok=True)
    
    # Font Setting
    try:
        fp = FontProperties(fname=settings.FONT_PATH, size=11)
        plt.rc('font', family=fp.get_name())
    except Exception as e:
        print(f"フォントの読み込みエラー: {e}")
        print("日本語が文字化けする可能性があります。")
        return

    # 1: Top 10 Industries by Total R&D Costs (2020)
    df_2020_research = research_expense_dict[year]
    df_2020_research['Total R&D Costs (Million Yen)'] = pd.to_numeric(df_2020_research['研究開発_研究開発費_計_百万円'], errors='coerce')
    top_rd_costs = df_2020_research.iloc[2:].nlargest(10, 'Total R&D Costs (Million Yen)')
    plt.figure(figsize=(10, 6))
    plt.bar(top_rd_costs['産業'], top_rd_costs['Total R&D Costs (Million Yen)'], color='skyblue')
    plt.title('Top 10 Industries by Total R&D Costs (2020)', fontsize=14)
    plt.xlabel('Industry', fontsize=12)
    plt.ylabel('R&D Costs (Million Yen)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    os.makedirs("plots", exist_ok=True)
    plt.savefig(f"plots/top10_rd_costs_{year}.png")
    plt.close()

    # 2: Top 10 Industries by R&D Cost as Percentage of Sales (2020)
    df_2020_research['R&D Cost as % of Sales'] = pd.to_numeric(df_2020_research['研究開発_売上高研究開発費比率_％'], errors='coerce')
    top_rd_percentage = df_2020_research.nlargest(10, 'R&D Cost as % of Sales')
    plt.figure(figsize=(10, 6))
    plt.bar(top_rd_percentage['産業'], top_rd_percentage['R&D Cost as % of Sales'], color='orange')
    plt.title('Top 10 Industries by R&D Cost as % of Sales (2020)', fontsize=14)
    plt.xlabel('Industry', fontsize=12)
    plt.ylabel('R&D Cost as % of Sales', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"plots/top10_rd_costs_percent_{year}.png")
    plt.close()

    # 3: Top 10 Industries by Number of Companies (2020) excluding 合計 and 総合計
    df_2020_research['Number of Companies'] = pd.to_numeric(df_2020_research['研究開発_企業数_社'], errors='coerce')
    top_companies = df_2020_research.iloc[2:].nlargest(10, 'Number of Companies')  # Exclude the first two rows
    plt.figure(figsize=(10, 6))
    plt.bar(top_companies['産業'], top_companies['Number of Companies'], color='green')
    plt.title('Top 10 Industries by Number of Companies (2020)', fontsize=14)
    plt.xlabel('Industry', fontsize=12)
    plt.ylabel('Number of Companies', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"plots/top10_num_companies_{year}.png")
    plt.close()

    # Plot 4: Total patents owned over the years
    years = sorted(patent_count_dict.PatentCountDict.keys())
    years = [yr for yr in years if yr >= 2010]  # Filter years from 2010 onwards
    total_patents = [patent_count_dict.PatentCountDict[yr]['特許権_件数_所有数'].dropna().astype(int).sum() for yr in years]

    print(patent_count_dict.PatentCountDict[year]['特許権_件数_所有数'])
    plt.figure(figsize=(10, 6))
    plt.plot(years, total_patents, marker='o', label='Total Patents Owned')
    plt.title('Total Patents Owned Over the Years')
    plt.xlabel('Year')
    plt.ylabel('Total Patents Owned')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"plots/total_patents_owned_{years[0]}_{years[-1]}.png")
    plt.close()

    # Plot 5: Top 5 industries with the most patents in the latest year
    latest_year = max(years)
    latest_df = patent_count_dict.PatentCountDict[latest_year].iloc[2:]
    top_industries = latest_df[['産業', '特許権_件数_所有数']].dropna()
    top_industries['特許権_件数_所有数'] = top_industries['特許権_件数_所有数'].astype(int)
    top_industries = top_industries.sort_values(by='特許権_件数_所有数', ascending=False).head(5)

    plt.figure(figsize=(10, 6))
    plt.bar(top_industries['産業'], top_industries['特許権_件数_所有数'], color='skyblue')
    plt.title(f'Top 5 Industries with Most Patents in {latest_year}')
    plt.xlabel('Industry')
    plt.ylabel('Number of Patents')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"plots/top5_industries_patents_{latest_year}.png")
    plt.close()

    # Plot 6: Comparison of patents owned vs. used for a specific year
    specific_df = patent_count_dict.PatentCountDict[year].iloc[2:]
    specific_df = specific_df[['産業', '特許権_件数_所有数', '特許権_件数_所有数_使用のもの（含供与）_件']].dropna()
    specific_df['特許権_件数_所有数'] = specific_df['特許権_件数_所有数'].astype(int)
    specific_df['特許権_件数_所有数_使用のもの（含供与）_件'] = specific_df['特許権_件数_所有数_使用のもの（含供与）_件'].astype(int)
    specific_df = specific_df.sort_values(by='特許権_件数_所有数', ascending=False).head(5)

    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    x = range(len(specific_df))
    plt.bar(x, specific_df['特許権_件数_所有数'], width=bar_width, label='Patents Owned', color='orange')
    plt.bar([p + bar_width for p in x], specific_df['特許権_件数_所有数_使用のもの（含供与）_件'], width=bar_width, label='Patents Used', color='green')
    plt.xticks([p + bar_width / 2 for p in x], specific_df['産業'], rotation=45)
    plt.title(f'Patents Owned vs. Used in {year}')
    plt.xlabel('Industry')
    plt.ylabel('Number of Patents')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"plots/patents_owned_vs_used_{year}.png")
    plt.close()
    
    print("Visualizations generated successfully.")

class Plotsproducer:
    
    #def plot_histograms(panel_data: pd.DataFrame, save_dir: str):
    #    """Histogram: 研究開発費と特許所有数の対数分布をプロットする"""
    #    plt.figure(figsize=(14, 6))
    #    plt.subplot(1, 2, 1)
    #    sns.histplot(panel_data['plot_histograms'], kde=True, bins=30)
    #    plt.title('研究開発費の対数分布')
    #    plt.subplot(1, 2, 2)
    #    sns.histplot(panel_data['log_patents_owned'], kde=True, bins=30, color='orange')
    #    plt.title('特許所有数の対数分布')
    #    plt.tight_layout()
    #    save_path = os.path.join(save_dir, 'hist_distributions.png')
    #    plt.savefig(save_path)
    #    plt.close()
    #    print(f"✓ Histogramを保存しました: {save_path}")

    def plot_time_series(panel_data: pd.DataFrame, save_dir: str):
        """Time Series: 特許権所有件数の推移（産業別）をプロットする"""
        print("Produce Time Series")
        plt.figure(figsize=(8, 5))
        yearly_patent = panel_data.groupby("year")["patent_count"].sum()
        yearly_patent.plot(marker='o')
        plt.xlabel("Year")
        plt.ylabel("patent_count_total")
        plt.yscale('log')
        plt.title("Annual trend of total patent count")
        plt.grid(True)
        save_path = os.path.join(save_dir, 'Annual_trend_of_total_patent_count.png')
        plt.savefig(save_path)
        plt.close()
        
        plt.figure(figsize=(8, 5))
        yearly_patent_change = yearly_patent.pct_change(1).multiply(100)
        yearly_patent_change.plot(marker='o')
        plt.xlabel("Year")
        plt.ylabel("patent_count_total_pct_change")
        plt.title("Year-over-year percent change in total patent count")
        plt.grid(True)
        save_path = os.path.join(save_dir, 'Year-over-year_percent_change_in_total_patent_count.png')
        plt.savefig(save_path)
        plt.close()
        print(f"✓ Time Seriesを保存しました: {save_path}")

    def plot_scatter_plots(panel_data: pd.DataFrame, save_dir: str):
        """Scatter Plot: 研究開発費と特許所有数の関係性をプロットする"""
        print("Produce Scatter Plots")
        
        panel_data['randd_total'] = pd.to_numeric(panel_data['randd_total'], errors='coerce')
        panel_data['patent_count'] = pd.to_numeric(panel_data['patent_count'], errors='coerce')
        panel_data.dropna(subset=['randd_total', 'patent_count'], inplace=True)
        
        plt.figure(figsize=(10, 7))
        target = panel_data["industry_id"].apply(len).isin([1,2])
        sns.regplot(data=panel_data[target], x='randd_total', y='patent_count', scatter_kws={'alpha':0.4})
        plt.xlabel("R&D費用(研究開発_研究開発費_計)")
        plt.ylabel("特許件数(特許権_件数_所有数)")
        plt.title("R&D費用 vs 特許件数(産業大分類)")
        plt.grid(True)
        save_path = os.path.join(save_dir, 'scatter_rd_vs_patents.png')
        plt.savefig(save_path)
        plt.close()
        print(f"✓ Scatter Plotを保存しました: {save_path}")

### 実行関数 ###

    def generate_all_visualizations(panel_data: pd.DataFrame, patent_dict: dict):
        """すべてのグラフを生成するメイン関数"""
        print("\n--- 可視化を開始します ---")
        if panel_data.empty:
            print("警告: パネルデータが空です。一部の可視化をスキップします。")
            return
            
        # 要件①の場所にプロット用ディレクトリを作成
        os.makedirs(settings.PLOTS_DIR, exist_ok=True)
        
        # Notebook内の全プロットを生成
        #Plotsproducer.plot_histograms(panel_data, settings.PLOTS_DIR)
        Plotsproducer.plot_time_series(panel_data, settings.PLOTS_DIR)
        Plotsproducer.plot_scatter_plots(panel_data, settings.PLOTS_DIR)
        
        print(f"--- 可視化完了 ---")

if __name__ == '__main__':
    # このスクリプト単体で実行する場合の処理
    panel_path = os.path.join(settings.PANELDATA_DIR, 'panel_data.csv')
    if os.path.exists(panel_path):
        panel_df = pd.read_csv(panel_path)
        # 時系列プロット用に特許データも読み込む
        patent_dict_main = data_processor.PanelDataProducer.load_data_from_csv(settings.PATENT_COUNT_FILE_KEY) # data_processorから関数を借用
        Plotsproducer.generate_all_visualizations(panel_df, patent_dict_main)
    else:
        print(f"エラー: {panel_path} が見つかりません。まず data_processor.py を実行してください。")
