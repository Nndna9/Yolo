import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Zai | Artist Intelligence",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    .big-font { font-size:40px !important; font-weight: bold; }
    .card-box { background-color: #1E1E1E; border-radius: 10px; padding: 15px; border: 1px solid #333; margin-bottom: 20px; }
    .metric-label { color: #AAAAAA; font-size: 14px; }
    .metric-value { font-size: 24px; font-weight: bold; color: white; }
    .artist-container:hover { transform: translateY(-5px); transition: 0.3s; border-color: white; }
    h1 { font-weight: 800; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_all_data():
    artists = []
    files = os.listdir("artist_data")
    
    metadata = {
        "taylor_swift.csv": {"name": "Taylor Swift", "color": "#A52A2A", "img": "https://upload.wikimedia.org/wikipedia/commons/f/f2/Taylor_Swift_and_Fans.png"},
        "the_weeknd.csv": {"name": "The Weeknd", "color": "#800080", "img": "https://upload.wikimedia.org/wikipedia/commons/8/8d/The_Weeknd_in_2019.jpg"},
        "drake.csv": {"name": "Drake", "color": "#4682B4", "img": "https://upload.wikimedia.org/wikipedia/commons/3/38/Drake_-_2016.jpg"},
        "bad_bunny.csv": {"name": "Bad Bunny", "color": "#FFD700", "img": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Bad_Bunny_2022_by_Glenn_Francis.jpg"},
        "dua_lipa.csv": {"name": "Dua Lipa", "color": "#FF007F", "img": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Dua_Lipa_2018.jpg"}
    }

    for file in files:
        if file.endswith(".csv"):
            path = os.path.join("artist_data", file)
            df = pd.read_csv(path)
            df['Date'] = pd.to_datetime(df['Date'])
            artists.append({
                "file": file,
                "data": df,
                "info": metadata[file]
            })
    return artists

all_artists = load_all_data()

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_artist' not in st.session_state:
    st.session_state.selected_artist = None

def go_home():
    st.session_state.page = 'home'
    st.session_state.selected_artist = None

def select_artist(artist_idx):
    st.session_state.page = 'dashboard'
    st.session_state.selected_artist = all_artists[artist_idx]

# --- PAGE 1: HOME (ARTIST SELECTION) ---
if st.session_state.page == 'home':
    st.title("🎵 Global Artist Intelligence")
    st.markdown("Select an artist to analyze campaign performance and audience engagement.")
    
    # Sort by Total Streams
    artist_stats = []
    for i, art in enumerate(all_artists):
        total_streams = art['data']['Streams'].sum()
        artist_stats.append({"index": i, "name": art['info']['name'], "streams": total_streams, "img": art['info']['img'], "color": art['info']['color']})
    
    artist_stats.sort(key=lambda x: x['streams'], reverse=True)
    
    # Display Cards
    cols = st.columns(len(artist_stats))
    for i, col in enumerate(cols):
        stat = artist_stats[i]
        with col:
            st.markdown(f"""
            <div class="card-box artist-container" style="border-left: 5px solid {stat['color']}; text-align: center;">
                <img src="{stat['img']}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 10px;">
                <h2 style="color: white; margin: 0;">{stat['name']}</h2>
                <p class="big-font" style="color: {stat['color']}; margin: 5px 0;">{stat['streams']:,}</p>
                <p class="metric-label">Total Streams</p>
                <br>
                <button onclick="alert('Please use the analyze button below')" style="pointer-events: none;">Analysis</button>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Analyze Dashboard", key=f"btn_{i}", on_click=select_artist, args=(stat['index'],), use_container_width=True, type="primary"):
                pass

# --- PAGE 2: DASHBOARD ---
elif st.session_state.page == 'dashboard':
    current_artist = st.session_state.selected_artist
    df = current_artist['data']
    info = current_artist['info']
    
    # SIDEBAR FILTERS
    with st.sidebar:
        st.header("Global Filters")
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        date_sel = st.slider("Date Range", min_date, max_date, (min_date, max_date))
        
        all_regions = df['Region'].unique()
        region_sel = st.multiselect("Regions", all_regions, default=all_regions)
        
        # Apply Filters
        mask = (df['Date'].between(pd.to_datetime(date_sel[0]), pd.to_datetime(date_sel[1]))) & (df['Region'].isin(region_sel))
        df_filtered = df[mask].copy()

    # HEADER
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        st.button("← Back to Artists", on_click=go_home, use_container_width=True)
    with c2:
        st.title(info['name'])
        st.caption("Real-time Analytics Dashboard")
    with c3:
        st.image(info['img'], width=80)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📊 Engagement", "🌍 Global Impact", "🚀 Campaign ROI"])

    # ===============================
    # TAB 1: ENGAGEMENT (3 VISUALIZATIONS)
    # ===============================
    with tab1:
        # KPIs
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Streams", f"{df_filtered['Streams'].sum():,}")
        k2.metric("Avg Skip Rate", f"{df_filtered['Skip_Rate'].mean():.2%}")
        k3.metric("Playlist Reach", f"{df_filtered['Playlist_Reach'].sum():,}")

        # Chart 1: Stream Trend (Time Series)
        st.subheader("1. Stream Volume Over Time")
        trend_df = df_filtered.groupby('Date')['Streams'].sum().reset_index()
        fig1 = px.line(trend_df, x='Date', y='Streams', color_discrete_sequence=[info['color']], template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Hitmaker Matrix (Scatter)
        # Decision: High Streams + Low Skip Rate = Perfect Campaign Target
        st.subheader("2. Hitmaker Matrix (Streams vs Skip Rate)")
        song_stats = df_filtered.groupby('Track').agg({'Streams':'sum', 'Skip_Rate':'mean'}).reset_index()
        fig2 = px.scatter(song_stats, x='Streams', y='Skip_Rate', color='Track', size='Streams', 
                          hover_data={'Streams':':,', 'Skip_Rate':':.2%'}, template="plotly_dark")
        fig2.update_layout(yaxis_title="Skip Rate (Lower is Better)", xaxis_title="Total Streams")
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: Song Breakdown (Treemap)
        st.subheader("3. Song Popularity Breakdown")
        fig3 = px.treemap(song_stats, path=['Track'], values='Streams', color='Skip_Rate', 
                          color_continuous_scale='RdYlGn_r', template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

    # ===============================
    # TAB 2: GLOBAL IMPACT (3 VISUALIZATIONS)
    # ===============================
    with tab2:
        # Chart 1: Geographic Distribution
        st.subheader("1. Global Stream Distribution")
        region_data = df_filtered.groupby('Region')['Streams'].sum().reset_index()
        fig4 = px.bar(region_data, x='Region', y='Streams', color='Streams', 
                      color_continuous_scale='Viridis', template="plotly_dark")
        st.plotly_chart(fig4, use_container_width=True)

        # Chart 2: Growth Momentum (Unique)
        # Decision: Which region is growing the FASTEST? (Where to spend money next)
        st.subheader("2. Regional Growth Momentum (Last 30 Days)")
        recent_data = df_filtered[df_filtered['Date'] >= (df_filtered['Date'].max() - pd.Timedelta(days=30))]
        growth_df = recent_data.groupby('Region')['Streams'].sum().reset_index()
        growth_df['Growth_Rate'] = growth_df['Streams'].pct_change().fillna(0)
        
        fig5 = px.bar(growth_df, x='Region', y='Streams', color='Growth_Rate', 
                      color_continuous_scale='Plasma', template="plotly_dark",
                      title="Bar Height = Volume | Color = Growth Rate")
        st.plotly_chart(fig5, use_container_width=True)

        # Chart 3: Listening Hour Heatmap
        # (Simulated hour based on random seed since CSV is daily, adding a dummy hour for viz)
        st.subheader("3. Peak Listening Hours (Heatmap)")
        # Create dummy hour data for visualization demo
        dummy_hours = df_filtered.sample(1000).copy()
        dummy_hours['Hour'] = np.random.randint(0, 24, size=len(dummy_hours))
        heat_df = dummy_hours.groupby(['Region', 'Hour'])['Streams'].sum().reset_index()
        heat_pivot = heat_df.pivot(index='Region', columns='Hour', values='Streams').fillna(0)
        
        fig6 = px.imshow(heat_pivot, color_continuous_scale='Hot', labels=dict(x="Hour of Day", y="Region", color="Streams"),
                         template="plotly_dark")
        st.plotly_chart(fig6, use_container_width=True)

    # ===============================
    # TAB 3: CAMPAIGN ROI (3 VISUALIZATIONS)
    # ===============================
    with tab3:
        # Chart 1: Conversion Funnel
        st.subheader("1. Premium Conversion Funnel")
        funnel_df = df_filtered.groupby('Campaign_Type').agg({
            'Streams':'sum', 
            'Premium_Conversions':'sum'
        }).reset_index()
        funnel_df['Non_Converted'] = funnel_df['Streams'] - funnel_df['Premium_Conversions']
        
        fig7 = go.Figure(go.Funnel(
            y = funnel_df['Campaign_Type'],
            x = funnel_df['Streams'] # Showing total reach at top, converting down
        ))
        fig7.update_layout(template="plotly_dark")
        st.plotly_chart(fig7, use_container_width=True)

        # Chart 2: Cost Efficiency Matrix (Scatter)
        # Decision: High Premium Conversion + Low CPA = Best Campaign
        st.subheader("2. Campaign Efficiency Matrix (Cost vs Conversion)")
        camp_perf = df_filtered.groupby('Campaign_Type').agg({
            'Premium_Conversions':'sum',
            'Cost_Per_Acquisition':'mean'
        }).reset_index()
        
        fig8 = px.scatter(camp_perf, x='Cost_Per_Acquisition', y='Premium_Conversions', 
                         size='Premium_Conversions', color='Campaign_Type',
                         hover_data={'Cost_Per_Acquisition':':$,.2f', 'Premium_Conversions':':,'},
                         template="plotly_dark")
        fig8.update_layout(xaxis_title="Cost Per Acquisition ($)", yaxis_title="Premium Users Acquired")
        st.plotly_chart(fig8, use_container_width=True)

        # Chart 3: Financial ROI (Bar)
        st.subheader("3. ROI by Campaign Type")
        roi_df = df_filtered.groupby('Campaign_Type')['ROI'].mean().reset_index()
        roi_df['ROI_Percent'] = roi_df['ROI'] * 100
        
        fig9 = px.bar(roi_df, x='Campaign_Type', y='ROI_Percent', 
                     color='ROI_Percent', color_continuous_scale='RdYlGn',
                     template="plotly_dark", text_auto=True)
        fig9.update_layout(yaxis_title="Return on Investment (%)", xaxis_title="Campaign Type")
        st.plotly_chart(fig9, use_container_width=True)
        
        # Insight Box
        best_camp = roi_df.loc[roi_df['ROI_Percent'].idxmax()]
        st.info(f"🚀 **Insight:** The '{best_camp['Campaign_Type']}' campaign yields the highest ROI ({best_camp['ROI_Percent']:.1f}%). Recommendation: Increase budget allocation here.")
