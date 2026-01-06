import pandas as pd
import numpy as np
import os
import random

# Create directory
if not os.path.exists("artist_data"):
    os.makedirs("artist_data")

# Real Artists and Song Titles
artists_data = [
    {
        "id": "taylor_swift",
        "name": "Taylor Swift",
        "color": "#A52A2A",
        "songs": ["Cruel Summer", "Anti-Hero", "Blank Space", "Shake It Off", "Love Story", "Fortnight"],
        "peak_streams": 15000000
    },
    {
        "id": "the_weeknd",
        "name": "The Weeknd",
        "color": "#800080",
        "songs": ["Blinding Lights", "Starboy", "Save Your Tears", "Die For You", "The Hills"],
        "peak_streams": 12000000
    },
    {
        "id": "drake",
        "name": "Drake",
        "color": "#4682B4",
        "songs": ["God's Plan", "One Dance", "Hotline Bling", "Started From The Bottom", "Toosie Slide"],
        "peak_streams": 13500000
    },
    {
        "id": "bad_bunny",
        "name": "Bad Bunny",
        "color": "#FFD700",
        "songs": ["Tití Me Preguntó", "Me Porto Bonito", "Dakiti", "Yo Perreo Sola", "MIA"],
        "peak_streams": 11000000
    },
    {
        "id": "dua_lipa",
        "name": "Dua Lipa",
        "color": "#FF007F",
        "songs": ["Levitating", "Don't Start Now", "New Rules", "Physical", "IDGAF"],
        "peak_streams": 9000000
    }
]

regions = ["USA", "UK", "Canada", "Mexico", "Brazil", "Germany", "France", "Japan", "Australia", "India"]
campaigns = ["Spotify Wrapped Promo", "TikTok Challenge", "Radio Push", "Playlist Feature", "TV Commercial"]

def generate_realistic_csv(artist):
    rows = []
    start_date = pd.to_datetime("2023-01-01")
    
    for day in range(365): # 1 year of data
        current_date = start_date + pd.Timedelta(days=day)
        
        # Simulate daily volume fluctuation
        daily_multiplier = np.sin(day / 30) * 0.2 + 1.0 
        base_volume = artist['peak_streams'] * daily_multiplier * random.uniform(0.7, 1.3)
        
        for region in regions:
            # Regional weight
            region_weight = random.uniform(0.1, 0.3)
            total_streams = int(base_volume * region_weight)
            
            # Pick a song for this day/region (simulate rotation)
            song = random.choice(artist['songs'])
            
            # Metrics Calculation
            likes = int(total_streams * random.uniform(0.05, 0.12))
            shares = int(total_streams * random.uniform(0.01, 0.05))
            
            # Skip Rate (Decision metric: High skip rate = bad for campaigns)
            skip_rate = random.uniform(0.15, 0.45) # 15% to 45%
            
            # Playlist Reach (How many people saw it on a playlist)
            playlist_reach = int(total_streams * random.uniform(1.2, 1.8))
            
            # Campaign Logic
            active_campaign = random.choice(campaigns)
            
            # Conversion Logic (Premium Users)
            # TikTok has high volume, low conversion. Playlist has high conversion.
            if active_campaign == "TikTok Challenge":
                conv_rate = 0.005
                cost_per_acq = 12.50
            elif active_campaign == "Playlist Feature":
                conv_rate = 0.025
                cost_per_acq = 4.50
            elif active_campaign == "Spotify Wrapped Promo":
                conv_rate = 0.018
                cost_per_acq = 3.20
            else:
                conv_rate = 0.01
                cost_per_acq = 8.00
                
            premium_conversions = int(total_streams * conv_rate)
            revenue = (total_streams * 0.003) + (premium_conversions * 5.00) # Ad rev + Sub rev
            total_spend = premium_conversions * cost_per_acq
            
            rows.append({
                "Date": current_date,
                "Region": region,
                "Track": song,
                "Streams": total_streams,
                "Likes": likes,
                "Shares": shares,
                "Skip_Rate": round(skip_rate, 2),
                "Playlist_Reach": playlist_reach,
                "Campaign_Type": active_campaign,
                "Premium_Conversions": premium_conversions,
                "Revenue": revenue,
                "Cost_Per_Acquisition": round(cost_per_acq, 2),
                "ROI": round((revenue - total_spend) / total_spend, 2) if total_spend > 0 else 0
            })
            
    df = pd.DataFrame(rows)
    path = f"artist_data/{artist['id']}.csv"
    df.to_csv(path, index=False)
    print(f"Created {path}")

# Run Generation
print("Generating Realistic Data Files...")
for art in artists_data:
    generate_realistic_csv(art)
print("Done! 5 CSV files created in 'artist_data' folder.")
