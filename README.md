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

The primary interest of this group lies in understanding the extent to which innovation can be driven by financial investment.
Globally, innovation across various fields is a vital factor in determining a nation's prosperity. This trend is expected to continue and will have a significant impact on national strength in the future.

How to foster innovation remains a challenging question both at the national and corporate levels. One major source of innovation is research conducted at universities and private companies. However, such research requires funding. To promote innovation at the national level, in addition to mobilizing private sector investment, government subsidies are considered an effective approach.

On the other hand, a key challenge lies in measuring the extent to which innovation is actually occurring. One potential indicator is the number of patents filed when new technologies or services are developed. This can serve as a proxy for gauging innovation activity.

## (3) Research Question

The analysis aims to investigate the relationship between research and development investment and the number of patents filed in different industrial sectors in Japan.

## (4) Previous Research

Chung-Chu Chuang & Chung-Min Tsai & Hsiao-Chen Chang & Yi-Hsien Wang, 2021. "Applying Quantile Regression to Assess the Relationship between R&D, Technology Import and Patent Performance in Taiwan," JRFM, MDPI, vol. 14(8), pages 1-14, August.

This paper supports the conclusion that R&D investment promotion policies are most effective when targeted at specific industries.

## (5) Hypothesis

There is a positive correlation between the amount of R&D spending and the number of patents obtained across industries.

## (6) Data and Variables

### Data Resources

- Keizai Sangyoushou Kigyokatsudo Kihon Chosa(経済産業省企業活動基本調査)
- https://www.meti.go.jp/statistics/tyo/kikatu/index.html

### Data Subject

- Ministry in charge: METI Ministry of Economy, Trade and Industry(経済産業省)
- Source: www.e-stat.go.jp
- Country/Entity: Japan
- Description: Industry Type

### Specific Tables

- 第10表　産業別、企業数、技術導入件数及び技術供与件数
- 第10表  産業別、企業数、売上高、研究開発費及び売上高比率、受託研究費、研究開発投資、能力開発費
- 第11表　産業別、資本金規模別、企業数、研究開発費及び売上高比率、受託研究費、有形固定資産のうち研究開発関連当期取得額

### Variables

- $year$ : year 2010 ~ 2021
- $i$ : Industry $i$
- $patent_{i, year}$ : The number of patents obtained by industry $i$ in year year$t$R&D expenditure of industry $i$ in year $year$
- $RDexp_{i, year}$ :
- $empl_{i, year}$ : Number of employees inindustry $i$ in year $year$
- $e_{i, year}$ : Error term

### Barcharts

`image/barcharts`

### Scatter Plots

`image/plots`

### Time Series

`image/timeseries`

## (7) Regression Models

### Simple Regression Model

$$
patent_{i, year} = const + RDexp_{i, year} + e_{i, year}
$$

### Fixed Effects Model

$$
patent_{i, year} = const + RDexp_{i, year} + empl_{i, year} + e_{i, year}
$$

### Regression Analysis

#### It is not statistically significant

So, why is it insignificant?

##### 1. Is a lag of up to two periods insufficient?

* According to Chuang et al. (2021), the effect is significantly positive for lags of up to two years (specifically for firms in the high quantile of patent performance).
  →This suggests that merely extending the lag period may not resolve the issue.

##### 2. A more likely reason is the substantial heterogeneity across industries.

* Chuang et al. (2021) found that the impact of R&D varies across quantiles, being negative for low-quantile firms but positive for mid-to-high-quantile firms.
* To address this, we can analyze the heterogeneity directly by introducing an interaction term between industry characteristics and R&D spending.
  →In their study, Chuang et al. (2021) classified firms into six categories based on "industry characteristics" and demonstrated that the interaction term between these characteristics and R&D expenditure was significantly positive.

#### Future Directions

* Perform quantile regression on patent levels.
* Arbitrarily categorize industries.

## (8) The file path

### Milestone 1

`notebooks\assignment_group\HW1\Assignment1.ipynb`

### Milestone 2

`notebooks\assignment_group\HW2\Milestone_2.ipynb`

### Our Special Challenge

`\data\README.md`

We challenged to use DVC.
