# 🏡 Real Estate Market Analysis in Germany

## 📌 Project Overview

This project is an end-to-end data analysis pipeline based on publicly available real estate listings in Germany.

It covers the full workflow:

* Data collection (web scraping)
* Data cleaning and preprocessing
* Feature engineering
* Machine learning model for price estimation
* Interactive dashboards in Tableau

The goal is to analyze regional price differences and build a model to identify overpriced and underpriced listings.

---

## 🚀 Project Highlights

* End-to-end data pipeline from raw data to ML predictions
* Custom web scraping module with retry logic and logging
* Data validation layer to ensure data quality
* Feature engineering with domain-specific metrics (e.g., price per sqm, market saturation)
* Integration of external datasets (population data)
* Machine learning model for price estimation
* Interactive dashboard built in Tableau
* Modular and production-like project structure

---

## 📊 Interactive Dashboard

🔗 **Tableau Public:**
[real_estates_germany | Tableau Public](https://public.tableau.com/app/profile/halyna.mann/viz/real_estates_germany/Immowelt_project?publish=yes)

---

## ⚙️ Tech Stack

* Python (Pandas, NumPy, scikit-learn)
* Web scraping (requests, BeautifulSoup)
* SQLite (optional storage)
* Tableau (data visualization)
* Logging & data validation

---

## 📊 Data Sources

- Real estate listings: scraped from immowelt.de  
- Population data: [source if available]  
- Regional data (Bundesland, cities): publicly available datasets  

---

## 🔄 Data Pipeline

1. Collecting real estate listing data

2. Cleaning and transforming raw data

3. Feature engineering:

   * price per sqm
   * market saturation (listings per 1K residents)

4. Enriching data with population and regional datasets

5. Validating data quality

6. Training regression model

7. Generating predictions and price classification

---

## 🤖 Machine Learning

* Model: Linear Regression
* Target: Price per square meter

### Feature engineering:

* price per sqm (normalized price metric)
* market saturation (listings per 1K residents)
* additional derived features for modeling and analysis


### Modeling Approach

- Separate models were trained for rental and purchase listings due to different pricing structures.
- Cross-validation was performed using city-level splits to ensure more robust evaluation.

### Model Coefficients

| Feature                   | Coefficient|
|---------------------------|------------|
| size_sqm                  | 10.866     |
| listings_per_1k_bundesland|  0.048     |
| listings_per_1k_city      | -1.311     |
| density_city              |  0.112     |
| city_te (target encoding) |  0.911     |
| object_type_te            |  0.401     |


### 📈 Model Insights

* Good performance for rental properties (low MAE)
* Higher error for purchase prices
* Errors increase for high-priced properties (outliers)

### Model Interpretation

The model reflects both property characteristics and market conditions.

Higher market saturation is associated with lower prices, while property size shows a positive relationship with price per sqm, likely due to correlations with location or quality.

Some features have a weaker influence, indicating that supply-demand dynamics play a key role in pricing.

### Model Limitations

The model does not include detailed location or property quality features, which limits prediction accuracy.
Nevertheless, it captures general pricing patterns and market dynamics.

---

## 📊 Key Insights

* Prices vary significantly across regions in Germany
* High supply does not necessarily lead to lower prices
* Southern regions remain the most expensive
* Market structure differs across regions and cities

---

## 📂 Data

The data used in this project was collected from publicly available real estate listing pages.

Due to potential usage restrictions and dataset size, the full raw dataset is not included in this repository.

A small sample dataset is provided in the `/data` folder for demonstration purposes.

The dataset includes: price, living area (sqm), number of rooms, location (city / region), derived features (price per sqm, market metrics) etc.

All sensitive or potentially identifiable information (e.g., exact addresses, descriptions) has been removed.

---

## 🧪 Data Quality

Custom validation checks were implemented:

* missing values monitoring
* logical constraints (price/sqm, size)
* data quality reporting

---

## 📁 Project Structure

See `/src` for modular pipeline implementation:

* `pipeline.py` → main data pipeline
* `modeling.py` → model training & prediction
* `validation.py` → data quality checks
* `evaluation.py` → model metrics

---

## ⚙️ Setup

1. Clone the repository

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`

4. Run the pipeline:

```bash
python main.py
```

The `.env` file is used to configure scraping and runtime parameters and is not included in the repository.

---

## ⚠️ Disclaimer

This project is intended for educational purposes only.

The data was collected from publicly available sources and processed for analysis.

The repository does not include the full dataset and does not aim to replicate or redistribute the original platform data.

---

## 👩‍💻 Author

Halyna Merkotan
