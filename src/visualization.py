# produce plots
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.font_manager import FontProperties
from matplotlib.ticker import ScalarFormatter, PercentFormatter
from industries import get_industries_id, get_industries_name, industryjptoen_dict
import settings
import data_processor
import japanize_matplotlib

class Plotsproducer:
    @staticmethod
    def translate_industry_name_to_english(japanese_name):
        """Translate Japanese industry name to English using the dictionary"""
        return industryjptoen_dict.get(japanese_name, japanese_name)
    
    @staticmethod
    def translate_dataframe_industry_names(df):
        """Translate industry names in a dataframe from Japanese to English"""
        if 'industry_name' in df.columns:
            df = df.copy()
            df['industry_name'] = df['industry_name'].apply(Plotsproducer.translate_industry_name_to_english)
        return df

    def make_each_bar_chart(panel_data:pd.DataFrame, target_column:str, years:list, industry_id_list:list, save_dir: str, ax,
                            ylabel:str, file_name: str, title_name: str):
        print(f"✓ {file_name}を作成します")

        bar_chart_data = panel_data.copy()

        bar_chart_data = bar_chart_data[bar_chart_data["year"].isin(years) & bar_chart_data['industry_id'].isin(industry_id_list)]
        
        # r_and_d_total と r_and_d_sales カラムを数値型に変換
        # errors='coerce' を指定することで、変換できない値は NaN になる
        bar_chart_data["r_and_d_total"] = pd.to_numeric(bar_chart_data["r_and_d_total"], errors='coerce')
        bar_chart_data["r_and_d_sales"] = pd.to_numeric(bar_chart_data["r_and_d_sales"], errors='coerce')

        # NaN 値（数値変換できなかったものや元々欠損だったもの）を含む行を除外
        bar_chart_data = bar_chart_data.dropna(subset=["r_and_d_total", "r_and_d_sales"])

        # ゼロ除算を避けるために r_and_d_sales が 0 ではない行のみを保持
        bar_chart_data = bar_chart_data[bar_chart_data["r_and_d_sales"] != 0]

        years = [2010,2015,2020]

        if target_column == "r_and_d_total/r_and_d_sales":
            bar_chart_data["r_and_d_total/r_and_d_sales"] = bar_chart_data["r_and_d_total"]/bar_chart_data["r_and_d_sales"]

        # Translate industry names to English
        bar_chart_data = Plotsproducer.translate_dataframe_industry_names(bar_chart_data)

        bar_chart_pivot_df = bar_chart_data.pivot_table(
            index="industry_name",
            columns="year",
            values=target_column,
            aggfunc="sum"
        )

        bar_chart_pivot_df.plot(kind="bar", ax=ax, figsize=(20, 10))

        ax.set_title(f"{title_name}")
        ax.set_xlabel("Industries")
        ax.set_ylabel(f"{ylabel}")
        # ax.legend(title='year', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

        if target_column == "r_and_d_total/r_and_d_sales":
            formatter = PercentFormatter(xmax=1, decimals=0)
        else:
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_powerlimits((4, 4))
        ax.yaxis.set_major_formatter(formatter)

    def make_bar_charts(panel_data: pd.DataFrame, save_dir: str):
        target_large_industries_list = [
            # "C",  #鉱業、採石業、砂利採取業
            "E", #製造業,
            # "F", #電気・ガス業
            # "G", #情報通信業
            "I1", #卸売業
            # "I2", #小売業
            # "J1", #クレジットカード業、割賦金融業
            # "K1", #物品賃貸業
            "L", #学術研究、専門・技術サービス業
            # "M", #飲食サービス業
            # "N", #生活関連サービス業、娯楽業,
            # "O", #個人教授所
            # "R2", #サービス業（その他のサービス業
            # "Z", #その他の産業
        ]

        target_medium_industries_list = [
            "090", #食料品製造業
            "100", #飲料・たばこ・飼料製造業
            "110", #繊維工業
            "120", #木材・木製品製造業（家具を除く）
            "130", #家具・装備品製造業
            "140", #パルプ・紙・紙加工品製造業
            "150", #印刷・同関連業
            "160", #化学工業
            "170", #石油製品・石炭製品製造業
            "180", #プラスチック製品製造業
            "190", #ゴム製品製造業
            "200", #なめし革・同製品・毛皮製造業
            "210", #窯業・土石製品製造業
            "220", #鉄鋼業
            "230", #非鉄金属製造業
            "240", #金属製品製造業
            "250", #はん用機械器具製造業
            "260", #生産用機械器具製造業
            "270", #業務用機械器具製造業
            "280", #電子部品・デバイス・電子回路製造業
            "290", #電気機械器具製造業
            "300", #情報通信機械器具製造業
            "310", #輸送用機械器具製造業
            "320", #その他の製造業

            "511", #繊維品卸売業
            "512", #衣服・身の回り品卸売業
            "521", #農畜産物・水産物卸売業
            "522", #食料・飲料卸売業
            "531", #建築材料卸売業
            "532", #化学製品卸売業
            "533", #石油・鉱物卸売業
            "534", #鉄鋼製品卸売業
            "535", #非鉄金属卸売業
            "536", #再生資源卸売業
            "541", #産業機械器具卸売業
            "542", #自動車卸売業
            "543", #電気機械器具卸売業
            "549", #その他の機械器具卸売業
            "551", #家具・建具・じゅう器等卸売業
            "552", #医薬品・化粧品等卸売業
            "553", #紙、紙製品卸売業
            "559", #その他の卸売業

            "710", #学術・開発研究機関
            "726", #デザイン業
            "728", #エンジニアリング業
            "730", #広告業
            "743", #機械設計業
            "744", #商品・非破壊検査業
            "745", #計量証明業
            "746", #写真業
        ]


        industry_id_series = panel_data["industry_id"].unique()

        industry_id_list = list(industry_id_series)

        large_industry_id_list = [i for i in industry_id_list if len(i) in [1, 2] and i in target_large_industries_list]
        large_industry_id_exclude_manufacturing_list = [i for i in large_industry_id_list if i != "E"]


        medium_industry_id_list = [i for i in industry_id_list if 
                                    len(i) == 3
                                    and ((int(i) <= 330 and int(i) % 10 == 0) or int(i) > 330)
                                    and i in target_medium_industries_list
                                ]
        medium_industry_id_exclude_manufacturing_list = [i for i in medium_industry_id_list if int(i) >= 330]

        years = [2010,2015,2020]

        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

        Plotsproducer.make_each_bar_chart(panel_data, target_column="r_and_d_total", years=years,
                                          industry_id_list=large_industry_id_list, save_dir=save_dir, ax=axes[0], ylabel = "R&D expenditure",
                                          file_name="1_R&D",  title_name="Three years' worth of R&D expenditure")

        Plotsproducer.make_each_bar_chart(panel_data, target_column="patent_count", years=years,
                                          industry_id_list=large_industry_id_list, save_dir=save_dir, ax=axes[1], ylabel = "The Number of Patents",
                                          file_name="2_Patent_Count", title_name="Three years' worth of The Number of Patents")

        Plotsproducer.make_each_bar_chart(panel_data, target_column="r_and_d_total/r_and_d_sales", years=years,
                                          industry_id_list=large_industry_id_list, save_dir=save_dir, ax=axes[2], ylabel = "R&D Expenditure / Sales",
                                          file_name="3_R&D_per_Sales", title_name = "Three years' worth of R&D Expenditure / Sales")

        plt.tight_layout()

        save_path = os.path.join(save_dir, 'combined_bar_chart.png')
        plt.savefig(save_path)
        plt.close()
        print(f"✓ combined_figureを保存しました: {save_path}")

    def make_time_series(panel_data: pd.DataFrame, save_dir: str):
        """Time Series: 特許権所有件数の推移（産業別）をプロットする"""
        print("Produce Time Series")
        plt.figure(figsize=(8, 5))
        yearly_patent = panel_data.groupby("year")["patent_count"].sum()
        yearly_patent.plot(marker='o')
        plt.xlabel("Year")
        plt.ylabel("Patent count total")
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
        plt.ylabel("Patent count total pct change  (%)")
        plt.title("Year-Over-Year percent change in total patent count")
        plt.grid(True)
        save_path = os.path.join(save_dir, 'Year-over-year_percent_change_in_total_patent_count.png')
        plt.savefig(save_path)
        plt.close()
        print(f"✓ Time Seriesを保存しました: {save_path}")


    def make_each_scatter_plots(panel_data: pd.DataFrame, target_index: pd.Series, save_dir: str, file_name: str, title_name: str):
        print(f"✓ {file_name}を作成します")
        
        # Patch: Clean data before plotting
        df = panel_data[target_index].copy()
        df = df.dropna(subset=["industry_name", "r_and_d_total", "patent_count"])
        df["industry_name"] = df["industry_name"].astype(str)
        
        # Translate industry names to English
        df = Plotsproducer.translate_dataframe_industry_names(df)
        
        int_columns = [
            "company_count", "r_and_d_sales", "r_and_d_total",
            "patent_company_count", "patent_count",
            "utility_company_count", "utility_count",
            "design_company_count", "design_count"
        ]
        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        plt.figure(figsize=(10, 6))
        
        plot_df = df[(df["r_and_d_total"] > 0) & (df["patent_count"] > 0)].copy()
        if plot_df.empty:
            print(f"警告: {file_name}にはプロット可能なデータがありません。スキップします。")
            return

        plot_df["log_r_and_d_total"] = np.log10(plot_df["r_and_d_total"])
        plot_df["log_patent_count"] = np.log10(plot_df["patent_count"])

        plt.figure(figsize=(10, 6))
    
        ax = sns.scatterplot(data=plot_df, x="log_r_and_d_total", y="log_patent_count", hue="industry_name", palette="bright", style="industry_name")
        ax = sns.regplot(data=plot_df, x='log_r_and_d_total', y='log_patent_count', ax=ax, scatter=False, line_kws={'color': 'black', 'linewidth': 1})

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xlabel("R&D Expenditure (log10 scale)")
        plt.ylabel("Number of patents held by the firms (log10 scale)")
        plt.title(f"{title_name}")
        plt.tight_layout()
        plt.grid(True)

        save_path = os.path.join(save_dir, f'{file_name}.png')
        plt.savefig(save_path)
        plt.close()

        print(f"✓ {file_name}を保存しました: {save_path}")

    def make_scatter_plots(panel_data: pd.DataFrame, save_dir: str):
        """Scatter Plot: 研究開発費と特許所有数の関係性をプロットする"""
        print("Produce Scatter Plots")

        file_name = "1_R&D_vs_Patents_Major_Industry"
        title_name = "R&D expense vs Patents in Major Industry"
        target_index = panel_data["industry_id"].apply(len).isin([1,2])
        Plotsproducer.make_each_scatter_plots(panel_data, target_index, save_dir, file_name, title_name)

        file_name = "2_R&D_vs_Patents_Major_Industry_Excl_Manufacturing"
        title_name = "R&D expense vs Patents in Major Industry Excl Manufacturing"
        target_index = panel_data["industry_id"].apply(len).isin([1,2]) & ~panel_data["industry_id"].isin(["E"])
        Plotsproducer.make_each_scatter_plots(panel_data, target_index, save_dir, file_name, title_name)

        file_name = "3_R&D_vs_Patents_Manufacturing_Detail"
        title_name = "R&D expense vs Patents in Manufacturing Detail"
        manufacturing_industry_cd_list = ["090","091","092","093","099","100","101","102","110","111","112","113","114","115","119","120","121","129","130","140","141","142","150","160","161","162","163","164","169","170","171","179","180","190","191","199","200","210","211","212","219","220","221","222","230","231","232","240","241","249","250","251","252","253","259","260","261","262","270","271","273","274","275","276","280","290","291","292","293","299","300","301","302","310","311","319","320"]
        #If the last digit of industry_id is 0, it represents a medium classification; otherwise, it represents a small classification.
        medium_class_manufacturing_industry_cd_list = [i for i in manufacturing_industry_cd_list if int(i) % 10 == 0]
        target_index = panel_data["industry_id"].isin(medium_class_manufacturing_industry_cd_list)
        Plotsproducer.make_each_scatter_plots(panel_data, target_index, save_dir, file_name, title_name)

        file_name = "4_R&D_vs_Patents_Wholesale_Detail"
        title_name = "R&D expense vs Patents in Wholesale Detail"
        wholesale_industry_cd_list = ["511","512","521","522","531","532","533","534","535","536","541","542","543","549","551","552","553","559"]
        target_index = panel_data["industry_id"].isin(wholesale_industry_cd_list)
        Plotsproducer.make_each_scatter_plots(panel_data, target_index, save_dir, file_name, title_name)

        file_name = "5_R&D_vs_Patents_Research_Professional_Technical_Detail"
        title_name = "R&D expense vs Patents in Research Professional Technical Detail"
        academic_related_industry_cd_list = ["710","726","728","730","743","744","745","746"]
        target_index = panel_data["industry_id"].isin(academic_related_industry_cd_list)
        Plotsproducer.make_each_scatter_plots(panel_data, target_index, save_dir, file_name, title_name)
        print("End producing Scatter Plots")

### 実行関数 ###

    def generate_all_visualizations(panel_data: pd.DataFrame, patent_dict: dict):
        """すべてのグラフを生成するメイン関数"""
        print("\n--- 可視化を開始します ---")
        if panel_data.empty:
            print("警告: パネルデータが空です。一部の可視化をスキップします。")
            return
            
        # 要件①の場所にプロット用ディレクトリを作成
        os.makedirs(settings.BAR_CHARTS_DIR, exist_ok=True)
        os.makedirs(settings.TIMESERIES_DIR, exist_ok=True)
        os.makedirs(settings.PLOTS_DIR, exist_ok=True)
        
        # Notebook内の全プロットを生成
        Plotsproducer.make_bar_charts(panel_data, settings.BAR_CHARTS_DIR)
        Plotsproducer.make_time_series(panel_data, settings.TIMESERIES_DIR)
        Plotsproducer.make_scatter_plots(panel_data, settings.PLOTS_DIR)
        
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
