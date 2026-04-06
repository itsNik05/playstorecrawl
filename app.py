import streamlit as st
import pandas as pd
import datetime
import io
from gplay_scraper import GPlayScraper

# Set Page Config
st.set_page_config(page_title="Play Store Scraper", layout="wide")

def get_top_apps(keyword, n=50, country='us'):
    # Initialize Scraper
    scraper = GPlayScraper(http_client="curl_cffi")
    
    results = scraper.search_analyze(
        query=keyword,
        count=n,
        lang="en",
        country=country
    )
    
    apps_data = []
    # Progress bar for the UI
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, result in enumerate(results[:n], 1):
        status_text.text(f"Processing #{idx}: {result.get('title', 'N/A')}")
        progress_bar.progress(idx / n)
        
        app_entry = {
            'Name': result.get('title', 'N/A'),
            'App ID': result.get('appId', 'N/A'),
            'Developer': result.get('developer', 'N/A'),
            'Rating': result.get('score', 'N/A'),
            'Price': result.get('price', 'Free'),
            'Free': result.get('free', True),
            'Currency': result.get('currency', 'N/A'),
            'Description': result.get('description', 'N/A')[:100],
            'URL': result.get('url', 'N/A'),
            'Initial Upload': 'N/A',
            'Last Upload': 'N/A',
            'Downloads': 'N/A',
            'Genre': 'N/A'
        }
        
        try:
            details = scraper.app_analyze(result['appId'], lang="en", country=country)
            app_entry['Initial Upload'] = details.get('released', 'N/A')
            app_entry['Last Upload'] = details.get('updated', 'N/A')
            app_entry['Downloads'] = details.get('installs', 'N/A')
            app_entry['Genre'] = details.get('genre', 'N/A')
        except Exception:
            pass
        
        apps_data.append(app_entry)
    
    status_text.text("Scraping Complete!")
    return apps_data

# --- STREAMLIT UI ---
st.title("📱 Google Play Store Scraper")
st.write("Enter your search details below to scrape app data into a table.")

# Sidebar for inputs
with st.sidebar:
    st.header("Search Settings")
    keyword = st.text_input("Enter Keyword", placeholder="e.g. Photo Editor")
    country = st.text_input("Country Code", value="us", help="us, in, gb, etc.")
    num_results = st.slider("Number of results", 5, 50, 20)
    start_button = st.button("Start Scraper")

if start_button:
    if not keyword:
        st.error("Please enter a keyword!")
    else:
        with st.spinner("Fetching data..."):
            data = get_top_apps(keyword, n=num_results, country=country)
            df = pd.DataFrame(data)
            
            # Show the data in the browser
            st.subheader(f"Results for '{keyword}'")
            st.dataframe(df)

            # Convert Dataframe to CSV for download
            csv = df.to_csv(index=False).encode('utf-8')
            
            # Download Button
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"gplay_{keyword}_{timestamp}.csv",
                mime='text/csv',
            )
