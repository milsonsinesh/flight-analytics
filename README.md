# ✈️ Flight Analytics Dashboard (India)

A real-time flight analytics dashboard built using **Streamlit**, **PostgreSQL**, and **free aviation APIs**.

## 🚀 Features
- Live aircraft tracking over India
- Airport explorer (Indian airports)
- Flight search & delay analysis
- Machine Learning delay prediction
- Interactive charts & maps

## 🛠 Tech Stack
- Python
- Streamlit
- PostgreSQL
- OpenSky (free APIs)
- Pandas, Plotly, Scikit-learn

## ▶️ Run Locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup_database.py
python run_etl.py
streamlit run streamlit_app/app.py


