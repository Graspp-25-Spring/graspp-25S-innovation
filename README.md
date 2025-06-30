# graspp-25S-innovation

## (1) Team members

- Yoshiya Bito
- Kohsuke Sagara
- Rin Nitta
- Joseph Chen
- Shuma Suzuki

### Responsibilities

Joseph Chen: Data scraping/cleaning, DVC and Scraping Documents（議事録）

Kohsuke Sagara: Model Structuring and Regression

Rin Nitta: Model Structuring and Interpritation

Shuma Suzuki: Visualization -Sctter Plots and Bar charts-

Yoshiya Bito: Visualization -Time Series-, Refactoring Mian.py


## (2) Our Interests

The primary interest of this group lies in understanding the extent to which innovation can be driven by financial investment. Globally, innovation across various fields is a vital factor in determining a nation's prosperity. This trend is expected to continue and will have a significant impact on national strength in the future.

How to foster innovation remains a challenging question both at the national and corporate levels. One major source of innovation is research conducted at universities and private companies. However, such research requires funding. To promote innovation at the national level, in addition to mobilizing private sector investment, government subsidies are considered an effective approach.

On the other hand, a key challenge lies in measuring the extent to which innovation is actually occurring. One potential indicator is the number of patents filed when new technologies or services are developed. This can serve as a proxy for gauging innovation activity.

## (3) Research Question

The analysis aims to investigate the relationship between research and development investment and the number of patents filed in different industrial sectors in Japan using panel data analysis with industry fixed effects.

## (4) Previous Research

Chung-Chu Chuang & Chung-Min Tsai & Hsiao-Chen Chang & Yi-Hsien Wang, 2021. "Applying Quantile Regression to Assess the Relationship between R&D, Technology Import and Patent Performance in Taiwan," JRFM, MDPI, vol. 14(8), pages 1-14, August.

This paper supports the conclusion that R&D investment promotion policies are most effective when targeted at specific industries. The study found that the impact of R&D varies across quantiles, being negative for low-quantile firms but positive for mid-to-high-quantile firms, with effects being significantly positive for lags of up to two years.

## (5) Hypothesis

There is a positive correlation between the amount of R&D spending and the number of patents obtained across industries, with lagged effects of R&D investment on patent generation.

## (6) Data and Variables

### **Data Resources**

- Keizai Sangyoushou Kigyokatsudo Kihon Chosa(経済産業省企業活動基本調査)
- https://www.meti.go.jp/statistics/tyo/kikatu/index.html

### **Data Subject**

- Ministry in charge: METI Ministry of Economy, Trade and Industry(経済産業省)
- Source: www.e-stat.go.jp
- Country/Entity: Japan
- Description: Industry Type

### **Specific Tables**

- 第10表　産業別、企業数、技術導入件数及び技術供与件数
- 第10表  産業別、企業数、売上高、研究開発費及び売上高比率、受託研究費、研究開発投資、能力開発費
- 第11表　産業別、資本金規模別、企業数、研究開発費及び売上高比率、受託研究費、有形固定資産のうち研究開発関連当期取得額

### **Variables**

- $$year$$ : year 2010 ~ 2021
- $$i$$ : Industry major category $$i$$
- $$t$$ : Time period $$t$$
- $$patent\_intensity_{i,t}$$ : Change in patent count normalized by sales ($$\Delta$$Patent Count / Sales) for industry $$i$$ in year $$t$$
- $$rd\_intensity_{i,t-k}$$ : R&D expenditure normalized by sales (R&D / Sales) for industry $$i$$ in year $$t-k$$ (where $$k$$ is the lag period)
- $$company\_count_{i,t}$$ : Number of companies in industry $$i$$ in year $$t$$
- $$\alpha_i$$ : Industry fixed effects
- $$\varepsilon_{i,t}$$ : Error term

### **Data Processing**

The analysis employs several data transformation techniques to ensure robust panel data analysis:

- **Industry Classification**: Creation of major industry categories from detailed industry IDs
- **Normalization**: All variables are normalized by sales revenue to control for industry size effects
- **Flow Variables**: Patent counts are converted to flow variables using first differences to capture annual patent generation
- **Lag Structure**: R&D variables are lagged by 1-2 periods to account for the time delay between R&D investment and patent output
- **Panel Structure**: Data is organized with industry major categories as entities and years as time dimension

### **Barcharts**

`image/barcharts`

### **Scatter Plots**

`image/plots`

### **Time Series**

`image/timeseries`

## (7) Regression Models

### **Model ① : One-Period Lag Fixed Effects Panel Model**


$$patent\_intensity_{i,t} = \alpha_i + \beta_1 \cdot rd\_intensity_{i,t-1} + \varepsilon_{i,t}$$

Where:
- $$\alpha_i$$ represents industry fixed effects
- $$\beta_1$$ captures the effect of lagged R&D intensity on current patent intensity
- The model uses within-industry variation for identification

### **Model ② : Two-Period Lag Fixed Effects Panel Model**


$$patent\_intensity_{i,t} = \alpha_i + \beta_1 \cdot rd\_intensity_{i,t-1} + \beta_2 \cdot rd\_intensity_{i,t-2} + \varepsilon_{i,t}$$

This extended model allows for:
- Cumulative effects of R&D investment over two periods
- Different impact patterns between immediate (t-1) and longer-term (t-2) effects
- More comprehensive capture of the R&D-to-patent conversion process

### **Panel Data Methodology**

The analysis employs fixed effects panel regression with the following specifications:

- **Entity Effects**: Industry fixed effects to control for time-invariant industry characteristics
- **Clustered Standard Errors**: Standard errors clustered at the industry level to account for within-industry correlation
- **Balanced Panel**: Analysis focuses on industries with sufficient time series observations
- **Poolability Test**: F-test for poolability to validate the necessity of fixed effects

### **Regression Analysis Results**

The implementation uses Python's `linearmodels.PanelOLS` with the following key features:

- **Dependent Variable**: Patent intensity (normalized patent flow)
- **Independent Variables**: Lagged R&D intensity measures
- **Fixed Effects**: Industry-level fixed effects
- **Robustness**: Clustered standard errors and diagnostic tests

#### **Statistical Significance Assessment**

The analysis evaluates statistical significance at multiple levels:
- *** p < 0.01 (1% significance level)
- ** p < 0.05 (5% significance level) 
- * p < 0.1 (10% significance level)

#### **Model Performance Metrics**

- **Overall R²**: Proportion of total variation explained
- **Within R²**: Proportion of within-industry variation explained (key metric for fixed effects)
- **Between R²**: Proportion of between-industry variation explained

#### **Economic Interpretation**

The models address potential issues identified in preliminary analysis:

##### **1. Lag Structure Considerations**

Following Chuang et al. (2021), the analysis incorporates lags of up to two periods to capture the time delay between R&D investment and patent output. The extended lag structure allows for more comprehensive assessment of R&D effectiveness.

##### **2. Industry Heterogeneity**

The fixed effects specification directly addresses substantial heterogeneity across industries by:
- Controlling for time-invariant industry characteristics
- Using within-industry variation for identification
- Allowing for industry-specific intercepts

#### **Future Directions**

Based on the current analysis framework, potential extensions include:

- **Quantile Regression**: Analysis of heterogeneous effects across different patent performance levels
- **Industry Categorization**: More detailed industry classification schemes
- **Dynamic Panel Models**: Incorporation of lagged dependent variables
- **Interaction Effects**: Analysis of R&D effectiveness across different industry characteristics

## (8) File Structure

### **Milestone 1**

`notebooks\assignment_group\HW1\Assignment1.ipynb`

### **Milestone 2**

`notebooks\assignment_group\HW2\Milestone_2.ipynb`

### **Our Special Challenge**

`\data\README.md`

We challenged to use DVC (Data Version Control) for reproducible data management and version control of our analysis pipeline.
