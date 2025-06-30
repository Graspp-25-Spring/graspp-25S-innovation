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


- $$i$$ : Industry category $$i$$
- $$t$$ : Time period (2010 ~ 2021) $$t$$
- $$\Delta Patent_{i,t}$$ : Annual change in patent count for industry $$i$$ in year $$t$$
- $$Sales_{i,t}$$ : Total sales revenue for industry $$i$$ in year $$t$$
- $$RD_{i,t}$$ : Total R&D expenditure for industry $$i$$ in year $$t$$
- $$\alpha_i$$ : Industry fixed effects
- $$\varepsilon_{i,t}$$ : Error term

### **Data Processing and Normalization**

The analysis employs several data transformation techniques to ensure robust panel data analysis and enable meaningful comparison across industries of different sizes:

**Size Adjustment through Sales Normalization**: All key variables are divided by sales revenue to control for industry size differences. This transformation allows for fair comparison between large and small industries by focusing on relative performance rather than absolute values.

**Patent Flow Variables**: Patent counts are converted to annual changes (first differences) to capture the flow of new patents generated each year, rather than cumulative stock measures.

**R&D Investment Ratios**: R&D expenditure is expressed as a proportion of sales revenue, providing a standardized measure of R&D investment commitment across industries.

**Lag Structure Implementation**: R&D variables are lagged by 1-2 periods to account for the time delay between R&D investment and patent output, reflecting the realistic timeline of innovation processes.

**Panel Data Structure**: Data is organized with industry major categories as cross-sectional units and years as the time dimension, enabling fixed effects analysis.

### **Key Transformed Variables**

- **Patent per Sales**:

  $$
  \frac{\Delta Patent_{i,t}}{Sales_{i,t}}
  $$

  - Annual patent generation relative to industry sales volume
- **R&D per Sales**:

  $$
  \frac{RD_{i,t-k}}{Sales_{i,t-k}}
  $$

  - R&D investment as a proportion of sales revenue (lagged by k periods)
- **Company Density**:

  $$
  \frac{Companies_{i,t}}{Sales_{i,t}}
  $$

  - Number of companies relative to total industry sales

### **Barcharts**

`image/barcharts`

### **Scatter Plots**

`image/plots`

### **Time Series**

`image/timeseries`

## (7) Regression Models

### **Model ① : One-Period Lag Fixed Effects Panel Model**

$$
\frac{\Delta Patent_{i,t}}{Sales_{i,t}} = \alpha_i + \beta_1 \cdot \frac{RD_{i,t-1}}{Sales_{i,t-1}} + \varepsilon_{i,t}
$$

**Economic Interpretation**: This model examines whether industries that invest a higher proportion of their sales in R&D (in the previous year) generate more patents per unit of sales in the current year. The coefficient

$$
\beta_1
$$

 represents the change in patent generation per sales unit when the R&D-to-sales ratio increases by one unit.

**Fixed Effects (**

**)**: Controls for time-invariant industry characteristics such as technological opportunities, regulatory environment, and industry-specific innovation patterns.

### **Model ② : Two-Period Lag Fixed Effects Panel Model**

$$
\frac{\Delta Patent_{i,t}}{Sales_{i,t}} = \alpha_i + \beta_1 \cdot \frac{RD_{i,t-1}}{Sales_{i,t-1}} + \beta_2 \cdot \frac{RD_{i,t-2}}{Sales_{i,t-2}} + \varepsilon_{i,t}
$$

**Extended Time Structure**: This model captures both immediate (t-1) and longer-term (t-2) effects of R&D investment on patent generation. The cumulative effect over two periods is measured as

$$
\beta_1 + \beta_2
$$

.

**Differential Impact Analysis**: The model allows for different impact patterns, where

$$
\beta_1
$$

 captures more immediate effects and

$$
\beta_2
$$

 captures longer-term research outcomes.

### **Panel Data Methodology**

The analysis employs fixed effects panel regression with the following specifications:

**Entity Fixed Effects**: Industry-level fixed effects control for unobserved time-invariant characteristics that affect both R&D investment and patent generation within each industry.

**Clustered Standard Errors**: Standard errors are clustered at the industry level to account for potential correlation of residuals within the same industry across time periods.

**Within-Industry Identification**: The fixed effects specification uses only within-industry variation over time for parameter identification, strengthening causal inference by controlling for industry-specific factors.

**Poolability Testing**: F-tests are conducted to validate the statistical necessity of including fixed effects versus pooled OLS estimation.

### **Implementation Details**

The regression analysis uses Python's `linearmodels.PanelOLS` with the following key features:

**Dependent Variable**: Annual patent generation divided by sales revenue
**Independent Variables**: Lagged R&D expenditure divided by sales revenue
**Panel Structure**: Industries as entities, years as time dimension
**Robustness Checks**: Clustered standard errors and comprehensive diagnostic testing

### **Statistical Significance Assessment**

The analysis evaluates statistical significance at multiple levels:

- *** p < 0.01 (1% significance level) - Highly significant
- ** p < 0.05 (5% significance level) - Significant
- * p < 0.1 (10% significance level) - Marginally significant

### **Model Performance Evaluation**

**Overall R²**: Measures the proportion of total variation in patent generation explained by the model
**Within R²**: Key metric for fixed effects models, measuring the proportion of within-industry variation explained
**Between R²**: Measures the proportion of between-industry variation explained

### **Economic Interpretation Framework**

**Coefficient Interpretation**: A coefficient of 0.3 on the R&D-to-sales ratio means that when an industry increases its R&D spending from 3% to 4% of sales, the patent generation per sales unit increases by 0.3 units.

**Policy Implications**: Positive and significant coefficients support policies that encourage R&D investment, providing evidence that increased R&D spending leads to measurable innovation outcomes.

**Industry Heterogeneity**: The fixed effects approach acknowledges that different industries have different baseline innovation capabilities and focuses on within-industry changes over time.

### **Addressing Previous Research Findings**

**Lag Structure Considerations**: Following Chuang et al. (2021), the analysis incorporates lags of up to two periods to capture the realistic time delay between R&D investment and patent output.

**Industry Heterogeneity Management**: The fixed effects specification directly addresses substantial heterogeneity across industries by controlling for time-invariant industry characteristics and using within-industry variation for identification.

#### **Future Research Directions**

Based on the current analysis framework, potential extensions include:

**Quantile Regression Analysis**: Examination of heterogeneous effects across different levels of patent performance within industries
**Industry Categorization Refinement**: More detailed industry classification schemes to capture technological similarities
**Dynamic Panel Models**: Incorporation of lagged dependent variables to model persistence in patent generation
**Interaction Effects Analysis**: Investigation of how R&D effectiveness varies across different industry characteristics and time periods

## (8) File Structure

### **Milestone 1**

`notebooks\assignment_group\HW1\Assignment1.ipynb`

### **Milestone 2**

`notebooks\assignment_group\HW2\Milestone_2.ipynb`

### **Our Special Challenge**

`\data\README.md`

We challenged to use DVC (Data Version Control) for reproducible data management and version control of our analysis pipeline.
