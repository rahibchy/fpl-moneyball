import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="FPL Moneyball Dashboard", page_icon="⚽", layout="wide")

st.title("⚽ FPL Moneyball: xG & Fixture Analysis")
st.markdown("Identify undervalued assets using **Expected Goal Involvement (xGI)** and **Upcoming Fixture Difficulty**.")

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    # A. Fetch Main Data (Players & Teams)
    url_static = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response_static = requests.get(url_static).json()
    
    # B. Fetch Fixtures (Schedule)
    url_fixtures = 'https://fantasy.premierleague.com/api/fixtures/'
    response_fixtures = requests.get(url_fixtures).json()
    
    # --- PROCESS TEAMS ---
    teams = pd.DataFrame(response_static['teams'])
    team_map = pd.Series(teams.name.values, index=teams.id).to_dict()
    team_short_map = pd.Series(teams.short_name.values, index=teams.id).to_dict() # e.g., 1 -> 'ARS'
    
    # --- PROCESS FIXTURES (Next 5) ---
    # Convert fixtures to DataFrame
    fixtures = pd.DataFrame(response_fixtures)
    # Filter for future fixtures only
    next_fixtures = fixtures[fixtures['finished'] == False].copy()
    
    # Create a simplified dictionary: {team_id: "ARS(H), CHE(A)..."}
    team_schedule = {i: [] for i in range(1, 21)}
    
    for idx, row in next_fixtures.iterrows():
        # Iterate through upcoming games and assign to both Home and Away teams
        # We limit to next 5 games per team logic later, but collect all first
        if row['team_h'] in team_schedule:
            opp_name = team_short_map.get(row['team_a'], "Unknown")
            diff = row['team_h_difficulty']
            team_schedule[row['team_h']].append(f"{opp_name} (H)")
            
        if row['team_a'] in team_schedule:
            opp_name = team_short_map.get(row['team_h'], "Unknown")
            diff = row['team_a_difficulty']
            team_schedule[row['team_a']].append(f"{opp_name} (A)")
            
    # Keep only next 5 and join into string
    final_schedule_map = {}
    for team_id, matches in team_schedule.items():
        final_schedule_map[team_id] = ", ".join(matches[:5]) # Top 5 only

    # --- PROCESS PLAYERS ---
    players = pd.DataFrame(response_static['elements'])
    
    # Map Basic Info
    players['team_name'] = players['team'].map(team_map)
    players['next_5_fixtures'] = players['team'].map(final_schedule_map) # <--- ADD FIXTURES TO PLAYER
    
    pos_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    players['position'] = players['element_type'].map(pos_map)
    
    players['price'] = players['now_cost'] / 10
    
    # --- METRIC UPGRADE: Use xG/xA instead of ICT ---
    # Convert string columns to numbers
    players['minutes'] = pd.to_numeric(players['minutes'], errors='coerce')
    players['expected_goals'] = pd.to_numeric(players['expected_goals'], errors='coerce')
    players['expected_assists'] = pd.to_numeric(players['expected_assists'], errors='coerce')
    players['expected_goal_involvements'] = pd.to_numeric(players['expected_goal_involvements'], errors='coerce')
    
    # Calculate xGI per 90 (Fairer comparison than raw total)
    # Avoid division by zero
    players['xgi_per_90'] = (players['expected_goal_involvements'] / players['minutes']) * 90
    players['xgi_per_90'] = players['xgi_per_90'].fillna(0)
    
    # Return clean DataFrame
    return players[[
        'web_name', 'team_name', 'position', 'price', 
        'minutes', 'total_points', 'expected_goal_involvements', 'xgi_per_90', 
        'next_5_fixtures', 'chance_of_playing_next_round'
    ]]

df = load_data()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.header("🎯 Filter Options")

# Position
selected_pos = st.sidebar.multiselect("Position", ['GKP', 'DEF', 'MID', 'FWD'], default=['MID', 'FWD'])

# Price
min_p, max_p = float(df['price'].min()), float(df['price'].max())
price_range = st.sidebar.slider("Price (£m)", min_p, max_p, (5.0, 12.0))

# Minutes (Crucial for per 90 stats)
min_mins = st.sidebar.number_input("Min Minutes Played", 0, 3000, 400)

# Filter Data
filtered_df = df[
    (df['position'].isin(selected_pos)) &
    (df['price'].between(price_range[0], price_range[1])) &
    (df['minutes'] >= min_mins)
].copy()

# --- 4. MAIN CHART ---
st.subheader("Price vs. Expected Goal Involvement (xGI)")

if not filtered_df.empty:
    # A. Color Palette (Classy/Vibrant)
    custom_colors = {
        'GKP': '#FFBC42', # Sunflower (Yellow/Orange)
        'DEF': '#0496FF', # Bright Blue
        'MID': '#D81159', # Ruby Red
        'FWD': '#8F2D56'  # Deep Violet
    }
    
    # B. The Plot
    fig = px.scatter(
        filtered_df,
        x="price",
        y="expected_goal_involvements", # Using Total xGI (Switch to 'xgi_per_90' if preferred)
        color="position",
        size="xgi_per_90", # Bubble size = Efficiency
        
        # C. The Rich Tooltip
        hover_name="web_name",
        hover_data={
            "team_name": True,
            "price": ":.1f",
            "expected_goal_involvements": ":.2f",
            "next_5_fixtures": True, # <--- THE FIXTURE LIST
            "position": False
        },
        
        color_discrete_map=custom_colors,
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override="#FFFFFF", # White trendline for contrast
        title="<b>Moneyball Matrix:</b> Bubble Size = xGI per 90"
    )
    
    # D. Styling
    fig.update_layout(
        template="plotly_dark", # Switch to Dark mode for better contrast
        height=650,
        xaxis_title="Price (£m)",
        yaxis_title="Total Expected Goal Involvements (xGI)",
        legend_title=dict(text='Position'),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. DATA TABLE ---
    st.markdown("### 📋 Detailed Data View")
    st.dataframe(
        filtered_df.sort_values(by='xgi_per_90', ascending=False),
        column_config={
            "next_5_fixtures": st.column_config.TextColumn("Upcoming Fixtures", width="medium"),
            "xgi_per_90": st.column_config.NumberColumn("xGI/90", format="%.2f"),
        }
    )

else:
    st.warning("No players found. Try lowering the Minutes filter.")