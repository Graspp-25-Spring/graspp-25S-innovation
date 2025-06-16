# regression
# src/regression.py

import os
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS
import settings

def run_regressions(panel_data: pd.DataFrame):
    """
    パネルデータに対してOLSおよび固定効果モデルの回帰分析を実行し、結果を保存する。
    """
    print("\n--- 回帰分析を開始します ---")
    
    if panel_data.empty:
        print("警告: パネルデータが空です。回帰分析をスキップします。")
        return

    # OLS (Ordinary Least Squares)
    ols_model = smf.ols('log_patents_owned ~ log_rd_cost', data=panel_data)
    ols_results = ols_model.fit()
    
    # PanelOLS (固定効果モデル)
    panel_data_indexed = panel_data.set_index(['industry', 'year'])
    fe_model = PanelOLS.from_formula('log_patents_owned ~ log_rd_cost + EntityEffects', data=panel_data_indexed)
    fe_results = fe_model.fit()

    # 要件①の場所に結果をテキストファイルに保存
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    save_path = os.path.join(settings.REPORTS_DIR, 'regression_summary.txt')
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("====================================================\n")
        f.write("            OLS Regression Results\n")
        f.write("====================================================\n")
        f.write(str(ols_results.summary()))
        f.write("\n\n\n")
        f.write("====================================================\n")
        f.write("      Fixed Effect (Panel) Regression Results\n")
        f.write("====================================================\n")
        f.write(str(fe_results))

    print(f"✓ 回帰分析の結果を保存しました: {save_path}")
    print("--- 回帰分析完了 ---")

if __name__ == '__main__':
    panel_data_path = os.path.join(settings.DATA_DIR, 'panel_data.csv')
    if os.path.exists(panel_data_path):
        panel_data = pd.read_csv(panel_data_path)
        run_regressions(panel_data)
    else:
        print(f"エラー: {panel_data_path} が見つかりません。まず data_processor.py を実行してください。")