import streamlit as st
import pandas as pd
import datetime
from gplay_scraper import GPlayScraper

st.set_page_config(page_title="Play Store Top Charts", layout="wide")

# Mapping clean UI names to Google Play's internal API codes
COLLECTIONS = {
    "Top Free Apps": "topselling_free",
    "Top Paid Apps": "topselling_paid",
    "Top Grossing Apps": "topgrossing",
    "Top New Free": "topselling_new_free",
    "Top New Paid": "topselling_new_paid"
}

CATEGORIES = {
    "All Categories": None,  # None usually defaults to overall charts
    "Games": "GAME",
    "Action Games": "GAME_ACTION",
    "Business": "BUSINESS",
    "Education": "EDUCATION",
    "Entertainment": "ENTERTAINMENT",
    "Finance": "FINANCE",
    "Health & Fitness": "HEALTH_AND_FITNESS",
    "Lifestyle": "LIFESTYLE",
    "Productivity": "PRODUCTIVITY",
    "Shopping": "SHOPPING",
    "Social": "SOCIAL",
    "Tools": "TOOLS"
}

def get_top_charts(collection_code, category_code, count=100, country='us'):
    scraper = GPlayScraper(http_client="curl_cffi")
    
    # We only pass the category if it's not "All Categories" (None)
    kwargs = {
        "collection": collection_code,
        "count": count,
        "country": country,
        "lang": "en"
    }
    if category_code:
        kwargs["category"] = category_code

    # Fetch the top charts
    results = scraper.list_analyze(**kwargs)
    
    apps_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, result in enumerate(results[:count], 1):
        status_text.text(f"Processing #{idx}: {result.get('title', 'N/A')}")
        progress_bar.progress(idx / count)
        
        apps_data.append({
            'Rank': idx,
            'Name': result.get('title', 'N/A'),
            'App ID': result.get('appId', 'N/A'),
            'Developer': result.get('developer', 'N/A'),
            'Rating': result.get('score', 'N/A'),
            'Price': result.get('price', 'Free'),
            'Installs': result.get('installs', 'N/A'),
            'URL': result.get('url', 'N/A')
        })
        
    status_text.text("Chart Extraction Complete!")
    return apps_data

# --- STREAMLIT UI ---
st.title("🏆 Google Play Top Charts Scraper")
st.write("Extract the top apps by category and chart type directly to a spreadsheet.")

with st.sidebar:
    st.header("Chart Settings")
    
    # Dropdowns for user selection
    chart_type = st.selectbox("Select Chart Type", list(COLLECTIONS.keys()))
    category = st.selectbox("Select Category", list(CATEGORIES.keys()))
    country = st.text_input("Country Code", value="us", help="e.g., us, in, gb")
    num_results = st.slider("Number of apps to scrape", 10, 200, 100)
    
    start_button = st.button("Get Top Charts")

if start_button:
    collection_code = COLLECTIONS[chart_type]
    category_code = CATEGORIES[category]
    
    with st.spinner(f"Fetching top {num_results} {chart_type} in {category}..."):
        try:
            data = get_top_charts(
                collection_code=collection_code, 
                category_code=category_code, 
                count=num_results, 
                country=country
            )
            
            df = pd.DataFrame(data)
            
            # Display results
            st.subheader(f"{chart_type} - {category}")
            st.dataframe(df, use_container_width=True)

            # Download Setup
            csv = df.to_csv(index=False).encode('utf-8')
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            cat_name = category.replace(" & ", "_").replace(" ", "_")
            
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"Top_{num_results}_{cat_name}_{timestamp}.csv",
                mime='text/csv',
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Note: Some categories might not have Top Grossing or New charts available in certain countries.")
      
