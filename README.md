# graspp-25S-innovation

## Our Interests
The primary interest of this group lies in understanding the extent to which innovation can be driven by financial investment.
Globally, innovation across various fields is a vital factor in determining a nation's prosperity. This trend is expected to continue and will have a significant impact on national strength in the future.

How to foster innovation remains a challenging question both at the national and corporate levels. One major source of innovation is research conducted at universities and private companies. However, such research requires funding. To promote innovation at the national level, in addition to mobilizing private sector investment, government subsidies are considered an effective approach.

On the other hand, a key challenge lies in measuring the extent to which innovation is actually occurring. One potential indicator is the number of patents filed when new technologies or services are developed. This can serve as a proxy for gauging innovation activity.

## Research Question
The analysis aims to investigate the relationship between research and development investment and the number of patents filed in different industrial sectors in Japan.

## Hypothesis
There is a positive correlation between the amount of R&D spending and the number of patents obtained across industries.

## The File Path

### Milestone 1
`notebooks\assignment_group\Milestone1\Milestone_1.ipynb`

### Milestone 2
`notebooks\assignment_group\Milestone2\Milestone_2.ipynb`

## Data source

### Descriptive Characteristics of Data
- Country: Japan
- Time Period: from 2003 to 2023 
- Data classification: By industry (More than 150 industries of various sizes)

### Links to the Data Source
- 経済産業省企業活動基本調査: https://www.meti.go.jp/statistics/tyo/kikatu/index.html
- 経済財政運営と改革の基本方針(骨太方針): https://www5.cao.go.jp/keizai-shimon/kaigi/cabinet/honebuto/honebuto-index.html

### Specific Excel Files to be used from 経済産業省企業活動基本調査
- 3 産業別、売上高経常利益率別常時従業者数
- (- 第10表　産業別、企業数、技術導入件数及び技術供与件数)
- 第10表  産業別、企業数、売上高、研究開発費及び売上高比率、受託研究費、研究開発投資、能力開発費
- 第11表　産業別、資本金規模別、企業数、研究開発費及び売上高比率、受託研究費、有形固定資産のうち研究開発関連当期取得額

### Specific Text Data to be used from 経済財政運営と改革の基本方針(骨太方針)
under update

### Specific Case Studies to be referenced
under update

## Regression Models

### Variables
- $year$ : year 2010 ~ 2021
- $i$ : Industry $i$
- $patent_{i, year}$ : The number of patents obtained by industry $i$ in year
- $RDexp_{i, year}$ : R&D expenditure of industry $i$ in year
- $empl_{i, year}$ : Number of employees of industry $i$ in year
- $e_{i, year}$ : Error term

### Simple Regression Model
$$
patent_{i, year} = const + RDexp_{i, year} + e_{i, year}
$$

### Fixed Effects Model
$$
patent_{i, year} = const + RDexp_{i, year} + empl_{i, year} + e_{i, year}
$$

## Our Special Challenge
`data\README_dvc.md`
We challenged to use DVC.

## Team members
- Yoshiya Bito
- Kohsuke Sagara
- Shuma Suzuki
- Rin Nitta
- Joseph Chen