import os
from pkgutil import get_data
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import hashlib 
import base64

# Function to set background image
def set_background(image_path):
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
        }}
        .custom-label {{
            font-size: 18px;
            font-weight: bold;
            color: #FFFFFF; /* Change to any color */
        }}
        .password-label {{
            font-size: 18px;
            font-weight: bold;
            color: #338aff; /* Change to any color */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background (replace with your actual image path)
image_path = r"pic3.avif"
set_background(image_path)

# File to store user credentials
CREDENTIALS_FILE = "user_credentials.csv"
LOGGED_IN_USERS_FILE = "logged_in_users.csv"

# Ensure credentials file exists
if not os.path.exists(CREDENTIALS_FILE):
    df = pd.DataFrame(columns=["name", "username", "password"])
    df.to_csv(CREDENTIALS_FILE, index=False)

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "name" not in st.session_state:
    st.session_state["name"] = ""

# Function to load credentials
def load_credentials():
    return pd.read_csv(CREDENTIALS_FILE)

# Function to save new user credentials
def save_credentials(name, username, password):
    credentials_df = load_credentials()
    hashed_password = hash_password(password)  # Secure password storage
    new_user = pd.DataFrame({"name": [name], "username": [username], "password": [hashed_password]})
    credentials_df = pd.concat([credentials_df, new_user], ignore_index=True)
    credentials_df.to_csv(CREDENTIALS_FILE, index=False)

# Function to check if username exists
def username_exists(username):
    credentials_df = load_credentials()
    return username in credentials_df["username"].values

# Function to check login credentials
def check_login(username, password):
    credentials_df = load_credentials()
    hashed_password = hash_password(password)
    user_match = (credentials_df["username"] == username) & (credentials_df["password"] == hashed_password)
    
    if user_match.any():
        # Save logged-in user details
        logged_in_user = credentials_df[user_match].iloc[0]
        pd.DataFrame([logged_in_user]).to_csv(LOGGED_IN_USERS_FILE, mode='a', index=False, header=not os.path.exists(LOGGED_IN_USERS_FILE))
        st.session_state["name"] = logged_in_user["name"]  # Store the user's name in session state
        return True
    return False

# Streamlit UI
# Show login/register only if not authenticated
if not st.session_state.get("authenticated", False):
    # Choose Login or Register
    option = st.radio("Select an option:", ["Login", "Register"])

    if option == "Login":
        st.subheader("🔑 Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if check_login(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success(f"✅ Welcome, {st.session_state['name']}!")
                st.rerun()  # Rerun the app to show the navigation menu
            else:
                st.warning("⚠ Credentials are in the correct format but not found. Please register below.")
                st.session_state.show_register = True

    elif option == "Register" or st.session_state.get("show_register", False):
        st.subheader("📝 Register New Account")
        name = st.text_input("Full Name")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Re-enter Password", type="password")

        if st.button("Register"):
            if not name or not new_username or not new_password or not confirm_password:
                st.warning("⚠ All fields are required!")
            elif username_exists(new_username):
                st.error("❌ Username already exists. Choose a different one.")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match!")
            else:
                save_credentials(name, new_username, new_password)
                st.success("✅ Registration successful! You can now log in.")
                st.session_state.show_register = False
# Load GDP data
gdp_file = "gdp_dataset.csv"
gdp_data = None
if os.path.exists(gdp_file):
    gdp_data = pd.read_csv(gdp_file)
    gdp_data = gdp_data[gdp_data["Year"].isin([2019, 2020, 2021, 2022, 2023])]


# --- Main App (After Login) ---
if st.session_state.get("authenticated", False):
    # Sidebar Navigation Menu
    st.sidebar.title("🔍 Navigation")
    st.sidebar.markdown("Navigate through the GDP Statistics Dashboard to explore insights, analysis, and tools.")
    page = st.sidebar.radio("Go to", ["Home", "About", "Dashboard", "Insights & Analysis", "Feedback", "Chatbot"])

    if st.sidebar.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["name"] = ""
        st.rerun()  # Rerun the app to show the login/register page

    # --- Home Page ---
    if page == "Home":
        st.title("🌍 India City GDP Dashboard")
        st.write(f"Welcome, {st.session_state['name']}! This is showing about the GDP of different states in India.")
        st.subheader("\U0001F4DD Purpose")
        st.write("📈this creation of the web site is for the purpose of providing the gdp rates of different cities in the India.")
        st.write("📊 this gives the data insights of the gdp in different sectors.")
        st.write("💡this helps to make decisions of different things across the cities")
        st.subheader("📌 Target Audience & Scope")
        with st.expander("👔 Policy Makers & Economists"):
            st.write("- Understand economic trends for policy planning.")
            st.write("- Use data insights for national and local economic policies.")
        with st.expander("💰 Business Investors"):
            st.write("- Identify promising cities for investments.")
            st.write("- Use GDP data for market research and decision-making.")        
        with st.expander("📊 Researchers & Academics"):
            st.write("- Study economic patterns at the city level.")
            st.write("- Conduct in-depth research using real economic data.")
        with st.expander("🌍 General Public & Enthusiasts"):
            st.write("- Explore India's financial landscape.")
            st.write("- Gain awareness of economic growth and trends.") 
        st.subheader("🌟 Key Insights")
        st.write("🔹 *Fastest Growing Cities:* Cities with the highest GDP growth in recent years.")
        st.write("🔹 *Sector Contributions:* Identifying which sectors drive the most growth of gdp in India's cities.")
        st.write("🔹 *Employment Trends:* The correlation between GDP and employment in major cities.")
        st.write("🔹 *Investment Hotspots:* Areas showing the highest economic potential for businesses and startups.")
        st.subheader("📌 *Overview*")
        st.write("This dashboard provides interactive and visual insights into India's GDP trends across various cities.")
        st.write("It enables policymakers, researchers, and investors to analyze economic trends effectively and make data-driven decisions.")
        st.write("Users can explore interactive charts, sector-wise breakdowns, and dynamic GDP trends to better understand India's economic landscape.") 

        st.subheader("📊 *Visualizations*")
        
        if gdp_data is not None:
            # Dynamic GDP Trend Visualization
            gdp_trend = gdp_data.groupby("Year")["GDP (in billion $)"].sum().reset_index()
            fig = px.line(gdp_trend, x="Year", y="GDP (in billion $)", markers=True, title="GDP Trend (2019-2023)")
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)
            
            # Dynamic Sector Breakdown
            sectors = ["Agriculture (%)", "Industry (%)", "Services (%)"]
            sector_data = gdp_data[sectors].mean().reset_index()
            sector_data.columns = ["Sector", "Percentage"]
            fig2 = px.pie(sector_data, names="Sector", values="Percentage", title="Sector-wise GDP Breakdown")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.write("🚨 Data unavailable. Please check the source file.")
    

    # --- About Page ---
    elif page == "About":
        st.title("About")
        st.write("""
        This application is designed to provide dashboards, insights, and a chatbot for better user experience.
        You can navigate through different sections using the sidebar.
        """)
        st.subheader("📚 *Data Sources*")
        st.write("""
        The data used in this dashboard is taken from a combination of:
        - Research Papers
        - Kaggle datasets
        These sources are carefully selected and cleaned the data for the visualisation.
        """)

        st.subheader("🎯 *Key Features*")
        
        st.write("""
        ### GDP Analysis
        - *GDP by City:* Visual representation of GDP distribution across different cities. Key cities include Delhi, Mumbai, Kolkata, and Bengaluru.
        - *Sector-wise Contribution:* Breakdown of GDP by various sectors like Agriculture, ICT, Services, and Industry.
        - *Top GDP Cities:* Highlighting cities with the highest GDP values.
        
        ### Employment Trends
        - *Employment Analysis:* Insight into employment rates across various sectors like Tourism, ICT, and Services.
        - *Unemployment Trends:* Visualization of unemployment rates over the years and by city.
        - *Youth Employment:* Analysis of youth unemployment rates and trends.
        
        ### R&D Expenditure
        - *R&D Insights:* Examination of R&D expenditure as a percentage of GDP in different cities.
        - *Patents Analysis:* Correlation between R&D spending and the number of patents filed per 100,000 inhabitants.
        - *City-wise R&D Data:* Detailed breakdown of R&D expenditure by city.
        
        ### Population Data
        - *Population Impact:* Visualizations of population data, including growth trends and distribution across cities.
        - *City Population:* Highlighting cities with the highest population figures.
        - *Yearly Trends:* Year-over-year population growth and its economic implications.
        """)
        
        st.subheader("🌟 *Summary*")
        st.write("""
        This dashboard aims to provide a deep dive into the economic and demographic data of Indian cities. By presenting complex data in an accessible and interactive format, we hope to facilitate better understanding and decision-making for policymakers, researchers, and the general public.
        """)
        
        st.subheader("⚠ *Disclaimer*")
        st.write("""
        The data presented in this dashboard is intended for informational purposes only. While we strive for accuracy, the information is provided "as is" without any warranty of any kind.
        """)

    # --- Dashboard Page ---
    elif page == "Dashboard":
        st.title("📊 Dashboard")
        st.write(f"Welcome, {st.session_state['name']}! This is the dashboard page where you can see the charts and reports of Indian cities .")
        # Example Placeholder Chart
        power_bi_url = "https://app.powerbi.com/reportEmbed?reportId=31a2b374-2556-4b45-9990-4b225ce6e2ab&autoAuth=true&ctid=09429612-44e7-430e-bdfa-3c437016bdad"
        st.markdown(f'<iframe width="100%" height="600" src="{power_bi_url}" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)
         # Key Economic Metrics Summary
        st.markdown("### *📌 Key Economic Indicators*")
        col1, col2, col3,col4 = st.columns(4)

        with col1:
            st.metric(label="📈 GDP Growth Rate", value="7.2%", delta="+0.8% from last year")
    
        with col2:
            st.metric(label="💼 Employment Rate", value="89.6%", delta="+1.2% from last year")
    
        with col3:
            st.metric(label="🏭 Industrial Growth", value="5.5%", delta="+0.6% from last year")
        with col4:
            st.metric(label="Umemployment growth", value="7.48",delta="-0.2% from last year")

        st.markdown("---")
        st.markdown("### 🔍 Want to explore more? ")
        
        if st.button("Insights & Analysis"):
            st.session_state["page"] = "📈 Insights & Analysis"
            st.rerun()

    # --- Insights & Analysis Page ---
    elif page == "Insights & Analysis":
        st.title("📈 Insights & Analysis")
        st.write("Analyze your data and display insights here.")
        st.subheader("💡 Key Insight:")
        st.info("Our data shows the insigths of th gdp of diferent states over the years 2019-2023!")
        st.subheader("Deep Dive into India's GDP Data")

        # Filters
        years = gdp_data["Year"].unique()
        selected_year = st.selectbox("Select Year", sorted(years, reverse=True))
        cities = gdp_data["City"].unique()
        selected_city = st.selectbox("Select City", sorted(cities))

        # Filter Data
        filtered_data = gdp_data[(gdp_data["Year"] == selected_year) & (gdp_data["City"] == selected_city)]

        # GDP Growth Trend
        st.subheader(f"GDP Growth Trend in {selected_city} ({selected_year})")
        gdp_trend = gdp_data[gdp_data["City"] == selected_city].groupby("Year")["GDP (in billion $)"].sum().reset_index()
        fig = px.line(gdp_trend, x="Year", y="GDP (in billion $)", markers=True, title=f"GDP Growth Trend in {selected_city}")
        st.plotly_chart(fig, use_container_width=True)
        
        # GDP vs Unemployment Rate
        st.subheader("GDP vs Unemployment Rate")
        fig_gdp_unemployment = px.scatter(gdp_data, x="GDP (in billion $)", y="Unemployment Rate (%)", color="City", title="GDP vs Unemployment Rate")
        st.plotly_chart(fig_gdp_unemployment, use_container_width=True)
        
        # Choropleth Map: GDP by City
        st.subheader("GDP by City (Choropleth Map)")

        # Latitude and Longitude for all cities
        city_coords = {
            "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
            "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
            "Mumbai": {"lat": 19.0760, "lon": 72.8777},
            "Delhi": {"lat": 28.7041, "lon": 77.1025},
            "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "Kolkata": {"lat": 22.5726, "lon": 88.3639},
            "Chennai": {"lat": 13.0827, "lon": 80.2707},
            "Pune": {"lat": 18.5204, "lon": 73.8567},
            "Jaipur": {"lat": 26.9124, "lon": 75.7873},
            "Lucknow": {"lat": 26.8467, "lon": 80.9462},
            "Gurugram": {"lat": 28.4595, "lon": 77.0266},
            "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
            "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
            "Visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
            "Patna": {"lat": 25.5941, "lon": 85.1376},
            "Bhopal": {"lat": 23.2599, "lon": 77.4126},
            "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366},
            "Ernakulam": {"lat": 9.9312, "lon": 76.2673},
            "Amritsar": {"lat": 31.6340, "lon": 74.8723},
            "Shillong": {"lat": 25.5788, "lon": 91.8933},
            "Jorapokhar": {"lat": 23.7333, "lon": 86.4167},  # Approximate coordinates
            "Talcher": {"lat": 20.9497, "lon": 85.2336},
            "Guwahati": {"lat": 26.1445, "lon": 91.7362},
            "Aizawl": {"lat": 23.7271, "lon": 92.7176},
            "Amaravati": {"lat": 16.5726, "lon": 80.3573},
            "Brajrajnagar": {"lat": 21.8167, "lon": 83.9167},  # Approximate coordinates
            "Kochi": {"lat": 9.9312, "lon": 76.2673},
            "Gandhinagar": {"lat": 23.2156, "lon": 72.6369},
            "Indore": {"lat": 22.7196, "lon": 75.8577},
            "Vadodara": {"lat": 22.3072, "lon": 73.1812},
            "Surat": {"lat": 21.1702, "lon": 72.8311},
            "Kanpur": {"lat": 26.4499, "lon": 80.3319},
            "Nagpur": {"lat": 21.1458, "lon": 79.0882},
            "Ludhiana": {"lat": 30.9010, "lon": 75.8573},
            "Agra": {"lat": 27.1767, "lon": 78.0081},
            "Nashik": {"lat": 19.9975, "lon": 73.7898},
            "Faridabad": {"lat": 28.4089, "lon": 77.3178},
            "Meerut": {"lat": 28.9845, "lon": 77.7064},
            "Rajkot": {"lat": 22.3039, "lon": 70.8022},
            "Varanasi": {"lat": 25.3176, "lon": 82.9739},
            "Srinagar": {"lat": 34.0837, "lon": 74.7973},
            "Aurangabad": {"lat": 19.8762, "lon": 75.3433},
            "Dhanbad": {"lat": 23.7957, "lon": 86.4304},
            "Allahabad": {"lat": 25.4358, "lon": 81.8463},
            "Ranchi": {"lat": 23.3441, "lon": 85.3096},
        }   
        # Add latitude and longitude to the GDP data
        gdp_data["Latitude"] = gdp_data["City"].map(lambda x: city_coords[x]["lat"])
        gdp_data["Longitude"] = gdp_data["City"].map(lambda x: city_coords[x]["lon"])

        # Create the Choropleth Map
        fig_map = px.scatter_geo(gdp_data[gdp_data["Year"] == selected_year], 
                                lat="Latitude", 
                                lon="Longitude", 
                                size="GDP (in billion $)", 
                                color="City", 
                                hover_name="City", 
                                title="GDP by City (Choropleth Map)")
        st.plotly_chart(fig_map, use_container_width=True)

        # Sector-wise Contribution
        st.subheader("Sector-wise GDP Contribution")
        sectors = ["Agriculture (%)", "Industry (%)", "Services (%)"]
        sector_data = filtered_data[sectors].melt(var_name="Sector", value_name="Percentage")
        fig2 = px.pie(sector_data, names="Sector", values="Percentage", title="Sector-wise GDP Breakdown")
        st.plotly_chart(fig2, use_container_width=True)

        # Top 10 Cities by GDP
        st.subheader("Top 10 Cities by GDP")
        top_cities = gdp_data[gdp_data["Year"] == selected_year].nlargest(10, "GDP (in billion $)")
        fig3 = px.bar(top_cities, x="City", y="GDP (in billion $)", title="Top 10 Cities by GDP")
        st.plotly_chart(fig3, use_container_width=True)

        # Global GDP Comparison
        st.subheader("India vs Global GDP Growth")
        global_gdp = gdp_data.groupby("Year")[["GDP (in billion $)"]].sum().reset_index()
        fig4 = px.line(global_gdp, x="Year", y="GDP (in billion $)", title="India GDP vs Global GDP")
        st.plotly_chart(fig4, use_container_width=True)
        
         # Treemap: GDP Distribution by City and Sector
        st.subheader("GDP Distribution by City and Sector")
        treemap_data = gdp_data.melt(id_vars=["City", "Year"], value_vars=["Agriculture (%)", "Industry (%)", "Services (%)"], 
                                    var_name="Sector", value_name="Percentage")
        fig_treemap = px.treemap(treemap_data, path=["City", "Sector"], values="Percentage", 
                                    title="GDP Distribution by City and Sector")
        st.plotly_chart(fig_treemap, use_container_width=True)

        # Unemployment Rate Trends
        st.subheader(f"Unemployment Rate Trends in {selected_city}")
        unemployment_trend = gdp_data[gdp_data["City"] == selected_city].groupby("Year")["Unemployment Rate (%)"].sum().reset_index()
        fig_unemployment = px.line(unemployment_trend, x="Year", y="Unemployment Rate (%)", markers=True, title=f"Unemployment Rate Trends in {selected_city}")
        st.plotly_chart(fig_unemployment, use_container_width=True)
        
        # 3D Scatter Plot: GDP vs R&D vs Population
        st.subheader("GDP vs R&D vs Population (3D Scatter Plot)")
        fig_3d = px.scatter_3d(gdp_data, x="GDP (in billion $)", y="R&D Expenditure (% of GDP)", z="Population", 
                                color="City", title="GDP vs R&D vs Population (3D Scatter Plot)")
        st.plotly_chart(fig_3d, use_container_width=True)
        
        # Top 10 Cities by Patents
        st.subheader("Top 10 Cities by Patents")
        top_patent_cities = gdp_data[gdp_data["Year"] == selected_year].nlargest(10, "Patents per 100,000 Inhabitants")
        fig_top_patents = px.bar(top_patent_cities, x="City", y="Patents per 100,000 Inhabitants", title="Top 10 Cities by Patents")
        st.plotly_chart(fig_top_patents, use_container_width=True)
        
        # Area Chart: Sector-wise GDP Contribution Over Time
        st.subheader("Sector-wise GDP Contribution Over Time")
        sector_trend = gdp_data[gdp_data["City"] == selected_city].groupby("Year")[["Agriculture (%)", "Industry (%)", "Services (%)"]].mean().reset_index()
        sector_trend = sector_trend.melt(id_vars="Year", var_name="Sector", value_name="Percentage")
        fig_area = px.area(sector_trend, x="Year", y="Percentage", color="Sector", title="Sector-wise GDP Contribution Over Time")
        st.plotly_chart(fig_area, use_container_width=True)
        
        # Tourism Sector Employment Trends
        st.subheader(f"Tourism Sector Employment Trends in {selected_city}")
        tourism_trend = gdp_data[gdp_data["City"] == selected_city].groupby("Year")["Tourism Sector Employment (%)"].sum().reset_index()
        fig_tourism = px.line(tourism_trend, x="Year", y="Tourism Sector Employment (%)", markers=True, title=f"Tourism Sector Employment Trends in {selected_city}")
        st.plotly_chart(fig_tourism, use_container_width=True)
        
        # Histogram: GDP Distribution Across Cities
        st.subheader("GDP Distribution Across Cities")
        fig_hist = px.histogram(gdp_data[gdp_data["Year"] == selected_year], x="GDP (in billion $)", nbins=20, 
                                title="GDP Distribution Across Cities")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Polar Chart: Sector-wise GDP Contribution
        st.subheader("Sector-wise GDP Contribution (Polar Chart)")
        sector_data = filtered_data[["Agriculture (%)", "Industry (%)", "Services (%)"]].melt(var_name="Sector", value_name="Percentage")
        fig_polar = px.line_polar(sector_data, r="Percentage", theta="Sector", line_close=True, 
                        title="Sector-wise GDP Contribution (Polar Chart)")
        st.plotly_chart(fig_polar, use_container_width=True)
        
       
        
        st.markdown("---")
        st.subheader("📝 Insights Summary")
        st.write("✔ *GDP growth trends highlight economic hotspots.*")
        st.write("✔ *Sector contributions show the economic drivers of each city.*")
        st.write("✔ *Investment hotspots offer guidance for investors.*")
        st.write("✔ *India's GDP trends compared globally reveal growth potential.*")

    # --- Feedback Page ---
    elif page == "Feedback":
        st.title("📝 Feedback")
        st.write("We value your feedback. Please share your thoughts below.")
        name = st.text_input("Name")
        email = st.text_input("Your Email")
        category = st.selectbox("Feedback Category", ["General Feedback", "Bug Report", "Feature Request", "Other"])
        feedback_text = st.text_area("Write your feedback here:")
        # Slider for satisfaction level
        satisfaction_level = st.slider("How satisfied are you with the dashboard?", 1, 10, 1)
        if st.button("Submit Feedback"):
            st.success("✅ Thank you for your feedback!")

    # --- Chatbot Page ---
    elif page == "Chatbot":
        st.title("🤖 Chatbot")
        st.write("This is where a chatbot can be integrated.")
        chatbase_iframe_url = "https://www.chatbase.co/chatbot-iframe/47BlpnTPkr5z7R_hbm-UZ"
        st.components.v1.iframe(chatbase_iframe_url, width=700, height=700, scrolling=True)

else:
    st.warning("⚠ Please log in to access the application.")
