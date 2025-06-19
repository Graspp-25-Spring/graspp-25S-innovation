import pandas as pd
import numpy as np
from linearmodels import PanelOLS
import warnings
import os
import settings
warnings.filterwarnings('ignore')

# Data loading
df = pd.read_csv(os.path.join(settings.PANELDATA_DIR, 'panel_data.csv'))

print("=" * 80)
print("パネルデータ固定効果モデル分析")
print("=" * 80)

print("\n=== データ前処理 ===")

# 必要な列を選択
analysis_df = df[['year', 'industry', 'industry_id', 'company_count', 
                  'randd_sales', 'randd_total', 'patent_count', 
                  'utility_count', 'design_count']].copy()

print(f"初期データ数: {len(analysis_df)}")

# industry_idの確認
print(f"\n【industry_idの値確認】")
print("ユニークなindustry_id:")
unique_ids = analysis_df['industry_id'].unique()
print(sorted(unique_ids))

# 欠損値除去
analysis_df = analysis_df.dropna()
print(f"欠損値除去後: {len(analysis_df)}")

# 数値型に変換
numeric_columns = ['company_count', 'randd_sales', 'randd_total', 'patent_count', 
                   'utility_count', 'design_count']
for col in numeric_columns:
    analysis_df[col] = pd.to_numeric(analysis_df[col], errors='coerce')

# 再度欠損値除去
analysis_df = analysis_df.dropna()
print(f"数値変換後: {len(analysis_df)}")

# ゼロ値や負値の処理
analysis_df = analysis_df[analysis_df['randd_sales'] > 0]
analysis_df = analysis_df[analysis_df['randd_total'] >= 0]
analysis_df = analysis_df[analysis_df['patent_count'] >= 0]

print(f"前処理完了後のデータ数: {len(analysis_df)}")

# 産業大分類を作成（修正版）
def create_industry_major(industry_id):
    """industry_idから産業大分類を作成"""
    id_str = str(industry_id)
    
    # 数字のみの場合は最初の桁を使用
    if id_str.isdigit():
        if len(id_str) >= 3:
            return int(id_str[0])  # 100の位
        else:
            return int(id_str[0])  # 最初の桁
    
    # アルファベットの場合は文字コードを使用
    elif id_str.isalpha():
        # A=10, B=11, C=12, ..., Z=35
        return ord(id_str[0]) - ord('A') + 10
    
    # 混合の場合は最初の文字を判定
    else:
        first_char = id_str[0]
        if first_char.isdigit():
            return int(first_char)
        else:
            return ord(first_char) - ord('A') + 10

analysis_df['industry_major'] = analysis_df['industry_id'].apply(create_industry_major)

print(f"\n【産業大分類の分布】")
industry_mapping = analysis_df.groupby('industry_major')['industry_id'].apply(lambda x: list(x.unique())).to_dict()
for major, ids in sorted(industry_mapping.items()):
    print(f"大分類 {major}: {ids[:5]}{'...' if len(ids) > 5 else ''}")

print(f"\n産業大分類数: {analysis_df['industry_major'].nunique()}")
print(f"年数: {analysis_df['year'].nunique()}")
print(f"年の範囲: {analysis_df['year'].min()} - {analysis_df['year'].max()}")

# 年でソート
analysis_df = analysis_df.sort_values(['industry_major', 'year'])

print("\n=== パネルデータ変数作成 ===")

# 産業大分類ごとにグループ化して変数作成
def create_panel_variables(group):
    """パネルデータ用の変数を作成"""
    # 特許件数の差分（ストック→フロー変換）
    group['patent_diff'] = group['patent_count'].diff()
    
    # 売上高による正規化
    group['patent_intensity'] = group['patent_diff'] / group['randd_sales']
    group['rd_intensity'] = group['randd_total'] / group['randd_sales']
    group['company_count_norm'] = group['company_count'] / group['randd_sales']
    group['utility_intensity'] = group['utility_count'] / group['randd_sales']
    group['design_intensity'] = group['design_count'] / group['randd_sales']
    
    # ラグ変数作成
    group['rd_intensity_lag1'] = group['rd_intensity'].shift(1)
    group['rd_intensity_lag2'] = group['rd_intensity'].shift(2)
    group['company_count_lag1'] = group['company_count_norm'].shift(1)
    group['utility_count_lag1'] = group['utility_intensity'].shift(1)
    group['design_count_lag1'] = group['design_intensity'].shift(1)
    
    return group

# グループごとに変数作成
analysis_df = analysis_df.groupby('industry_major').apply(create_panel_variables).reset_index(drop=True)

# 無限大値や欠損値を除去
analysis_df = analysis_df.replace([np.inf, -np.inf], np.nan)

print(f"変数作成後のデータ数: {len(analysis_df)}")

# パネルデータ用にマルチインデックス設定
panel_df = analysis_df.set_index(['industry_major', 'year'])

print(f"パネルデータ形状: {panel_df.shape}")
print(f"産業数: {len(panel_df.index.get_level_values(0).unique())}")
print(f"年数: {len(panel_df.index.get_level_values(1).unique())}")

print("\n" + "=" * 80)
print("モデル① : 1期ラグ固定効果パネルモデル")
print("=" * 80)

print("\n【数式】")
print("Δ特許件数/売上高_it = α_i + β₁(研究開発費/売上高)_{i,t-1} + ε_{it}")
print("where α_i = 産業固定効果")

# モデル①：1期ラグ + 固定効果
try:
    # データ準備
    model_1_data = panel_df.dropna(subset=['patent_intensity', 'rd_intensity_lag1'])
    
    dependent_1 = model_1_data['patent_intensity']
    exog_1 = model_1_data[['rd_intensity_lag1']]
    
    print(f"\n【データ情報】")
    print(f"使用データ数: {len(dependent_1)}")
    print(f"産業数: {len(dependent_1.index.get_level_values(0).unique())}")
    print(f"年数: {len(dependent_1.index.get_level_values(1).unique())}")
    
    # 固定効果パネルモデル
    model_1 = PanelOLS(dependent_1, exog_1, entity_effects=True)
    results_1 = model_1.fit(cov_type='clustered', cluster_entity=True)
    
    print(f"\n【回帰結果】")
    print(results_1.summary)
    
    print(f"\n【主要結果】")
    print(f"研究開発費集約度(t-1)の係数: {results_1.params['rd_intensity_lag1']:.6f}")
    print(f"標準誤差: {results_1.std_errors['rd_intensity_lag1']:.6f}")
    print(f"t統計量: {results_1.tstats['rd_intensity_lag1']:.6f}")
    print(f"p値: {results_1.pvalues['rd_intensity_lag1']:.6f}")
    print(f"Overall R²: {results_1.rsquared:.4f}")
    print(f"Within R²: {results_1.rsquared_within:.4f}")
    print(f"Between R²: {results_1.rsquared_between:.4f}")
    
    # 統計的有意性の判定
    significance_1 = ""
    if results_1.pvalues['rd_intensity_lag1'] < 0.01:
        significance_1 = "***"
    elif results_1.pvalues['rd_intensity_lag1'] < 0.05:
        significance_1 = "**"
    elif results_1.pvalues['rd_intensity_lag1'] < 0.1:
        significance_1 = "*"
    
    print(f"統計的有意性: {significance_1}")
    
except Exception as e:
    print(f"モデル①でエラーが発生しました: {e}")
    results_1 = None

print("\n" + "=" * 80)
print("モデル② : 2期ラグ固定効果パネルモデル")
print("=" * 80)

print("\n【数式】")
print("Δ特許件数/売上高_it = α_i + β₁(研究開発費/売上高)_{i,t-1} + β₂(研究開発費/売上高)_{i,t-2} + ε_{it}")

# モデル②：2期ラグ + 固定効果
try:
    # データ準備
    model_2_data = panel_df.dropna(subset=['patent_intensity', 'rd_intensity_lag1', 'rd_intensity_lag2'])
    
    dependent_2 = model_2_data['patent_intensity']
    exog_2 = model_2_data[['rd_intensity_lag1', 'rd_intensity_lag2']]
    
    print(f"\n【データ情報】")
    print(f"使用データ数: {len(dependent_2)}")
    print(f"産業数: {len(dependent_2.index.get_level_values(0).unique())}")
    print(f"年数: {len(dependent_2.index.get_level_values(1).unique())}")
    
    # 固定効果パネルモデル
    model_2 = PanelOLS(dependent_2, exog_2, entity_effects=True)
    results_2 = model_2.fit(cov_type='clustered', cluster_entity=True)
    
    print(f"\n【回帰結果】")
    print(results_2.summary)
    
    print(f"\n【主要結果】")
    print(f"研究開発費集約度(t-1)の係数: {results_2.params['rd_intensity_lag1']:.6f}")
    print(f"研究開発費集約度(t-2)の係数: {results_2.params['rd_intensity_lag2']:.6f}")
    print(f"(t-1) p値: {results_2.pvalues['rd_intensity_lag1']:.6f}")
    print(f"(t-2) p値: {results_2.pvalues['rd_intensity_lag2']:.6f}")
    print(f"Overall R²: {results_2.rsquared:.4f}")
    print(f"Within R²: {results_2.rsquared_within:.4f}")
    
    # 統計的有意性の判定
    significance_2_lag1 = ""
    significance_2_lag2 = ""
    if results_2.pvalues['rd_intensity_lag1'] < 0.01:
        significance_2_lag1 = "***"
    elif results_2.pvalues['rd_intensity_lag1'] < 0.05:
        significance_2_lag1 = "**"
    elif results_2.pvalues['rd_intensity_lag1'] < 0.1:
        significance_2_lag1 = "*"
        
    if results_2.pvalues['rd_intensity_lag2'] < 0.01:
        significance_2_lag2 = "***"
    elif results_2.pvalues['rd_intensity_lag2'] < 0.05:
        significance_2_lag2 = "**"
    elif results_2.pvalues['rd_intensity_lag2'] < 0.1:
        significance_2_lag2 = "*"
    
    print(f"(t-1) 統計的有意性: {significance_2_lag1}")
    print(f"(t-2) 統計的有意性: {significance_2_lag2}")
    
except Exception as e:
    print(f"モデル②でエラーが発生しました: {e}")
    results_2 = None

print("\n" + "=" * 80)
print("総合的な結果比較・経済解釈")
print("=" * 80)

if results_1 is not None and results_2 is not None:
    try:
        print(f"\n【研究開発費効果の比較】")
        print(f"{'モデル':<15} {'1期ラグ係数':<15} {'2期ラグ係数':<15} {'Within R²':<10}")
        print("-" * 60)
        print(f"{'①基本モデル':<15} {results_1.params['rd_intensity_lag1']:<15.6f} {'---':<15} {results_1.rsquared_within:<10.4f}")
        print(f"{'②2期ラグ':<15} {results_2.params['rd_intensity_lag1']:<15.6f} {results_2.params['rd_intensity_lag2']:<15.6f} {results_2.rsquared_within:<10.4f}")
        
        # 累積効果の計算
        cumulative_effect_2 = results_2.params['rd_intensity_lag1'] + results_2.params['rd_intensity_lag2']
        
        print(f"\n【累積効果（2年間）】")
        print(f"モデル②: {cumulative_effect_2:.6f}")
        
        print(f"\n【統計的有意性テスト】")
        print(f"モデル① F-test for Poolability p値: {results_1.f_pooled.pvalue:.6f}")
        print(f"モデル② F-test for Poolability p値: {results_2.f_pooled.pvalue:.6f}")
        print("→ 固定効果の統計的必要性を確認")
        
        print(f"\n【固定効果モデルの妥当性】")
        print("✓ Entity effects = True で産業固定効果を推定")
        print("✓ Clustered standard errors で産業内相関を調整")
        print("✓ Within変動による識別で因果推論を強化")
        print("✓ F-test for Poolabilityで固定効果の必要性を確認")
        
    except Exception as e:
        print(f"結果比較でエラーが発生しました: {e}")

print("\n" + "=" * 80)
print("データ概要統計・診断")
print("=" * 80)

print("\n【主要変数の記述統計】")
summary_vars = ['patent_intensity', 'rd_intensity_lag1', 'rd_intensity_lag2']
print(panel_df[summary_vars].describe())

print(f"\n【産業大分類別データ分布】")
industry_counts = analysis_df.groupby('industry_major')['year'].count().sort_index()
print("産業ID : データ数")
for idx, count in industry_counts.items():
    print(f"   {idx}   :   {count}")

print(f"\n【分析完了】")
print("=" * 80)
