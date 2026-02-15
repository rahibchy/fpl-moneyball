# ⚽ FPL Moneyball Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B)
![Plotly](https://img.shields.io/badge/Plotly-5.18-3F4F75)
![Status](https://img.shields.io/badge/Status-Live-success)

**An interactive data science tool to identify undervalued Fantasy Premier League (FPL) assets using regression analysis.**

## 📖 Project Overview
This project applies **"Moneyball" principles** to Fantasy Premier League data. Instead of relying on total points (descriptive), it analyzes the relationship between **Price** and **ICT Index** (predictive) to find players who are statistically underpriced.

The dashboard automates data retrieval from the official FPL API, processes it using Pandas, and visualizes market inefficiencies using an interactive Streamlit web app.

### 🎯 Key Features
* **Automated ETL Pipeline:** Fetches live data directly from the FPL `bootstrap-static` API endpoint.
* **Moneyball Regression Analysis:** Uses OLS (Ordinary Least Squares) regression to establish a "Fair Value" trendline for every price point.
* **Value Identification:** Instantly highlights players **above the trendline** (Undervalued/Gems) vs. those below it (Overpriced).
* **Interactive Filtering:** Users can filter by Position, Price Range (£4.0m - £14.0m), and Minimum Minutes played to remove noise.
* **Dynamic ROI Metrics:** Calculates "Points Per Million" (ROI) dynamically for all filtered players.

## 📊 Dashboard Preview

*(Place a screenshot of your dashboard here. Name it 'dashboard_preview.png' and add it to your repo)*
![Dashboard Example](dashboard_preview.png)

## 🛠️ Tech Stack
* **Core Logic:** Python (Pandas, NumPy)
* **Data Visualization:** Plotly Express (Interactive Scatter Plots)
* **Web Framework:** Streamlit
* **Statistical Modeling:** Statsmodels (OLS Regression)
* **Data Source:** [FPL Official API](https://fantasy.premierleague.com/api/bootstrap-static/)

## 🚀 How to Run Locally

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/fpl-moneyball.git](https://github.com/yourusername/fpl-moneyball.git)
    cd fpl-moneyball
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## 📂 Project Structure
```text
├── app.py                # Main application script
├── requirements.txt      # List of dependencies
├── README.md             # Project documentation
└── .gitignore           # Git ignore rules

🧠 Strategic Insights
The core hypothesis of this tool is that Price should correlate with Influence, Creativity, and Threat (ICT).

Trendline: Represents the league-average performance for a given price.

Residuals: The vertical distance from a player bubble to the trendline represents their Value Over Replacement.

Positive Residual: The player is generating more underlying stats than their price tag implies (Buy).

Negative Residual: The player is underperforming relative to their cost (Sell/Avoid).

🔜 Roadmap
[ ] Fixture Difficulty Integration: Overlay next 5 fixtures on the tooltip.

[ ] xG/xA Import: Replace ICT Index with Understat xG data for higher precision.

[ ] Historical Analysis: Compare current season trends with previous seasons.

Created by Rahib Mabsur Chowdhury
