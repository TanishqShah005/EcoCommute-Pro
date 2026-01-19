import streamlit as st
import pandas as pd
import random
import time

# --- Project Configuration ---
st.set_page_config(page_title="EcoCommute Pro", page_icon="🌍", layout="wide")

# --- Initialize Session State (To store history) ---
if 'trips' not in st.session_state:
    st.session_state.trips = []

# --- DATA: ADVANCED EMISSION FACTORS (kg CO2 per km) ---
EMISSION_FACTORS = {
    "Walk/Cycle": 0.0,
    "Bus (Diesel)": 0.10,
    "Bus (Electric)": 0.04,
    "Metro/Train": 0.03,
    "Motorbike": 0.11,
    "Car (Petrol)": 0.19,
    "Car (Diesel)": 0.17,
    "Car (Electric)": 0.05,
    "Ride-share (Uber/Ola)": 0.22 
}

# --- AI LOGIC: SCORING ALGORITHM ---
def calculate_eco_score(total_emissions, total_distance):
    """
    AI Logic: Calculates a 'Sustainability Score' (0-100).
    100 = Perfect (Walking/Cycling).
    <50 = Needs Improvement.
    """
    if total_distance == 0: return 0
    avg_emissions_per_km = total_emissions / total_distance
    
    score = 100 - (avg_emissions_per_km / 0.19 * 100)
    return max(0, min(100, score)) 

def get_ai_consultation(trips_df):
    """
    AI Logic: Analyzes the ENTIRE itinerary pattern, not just one trip.
    """
    insights = []
    
    # 1. Detect Car Dependency
    car_trips = trips_df[trips_df['Mode'].str.contains("Car")]
    if not car_trips.empty:
        total_car_dist = car_trips['Distance'].sum()
        if total_car_dist < 5:
            insights.append("🚫 **Inefficiency Alert:** You are using a car for very short distances (<5km). This destroys your Eco-Score. Recommendation: Switch to Walking/Cycling for these legs.")
        elif total_car_dist > 20 and 'Passengers' in trips_df.columns:
            # Check if they are driving alone
            solo_drives = car_trips[car_trips['Passengers'] == 1]
            if not solo_drives.empty:
                 insights.append("🚗 **Carpool Opportunity:** You have long solo car drives. Sharing these rides would cut your specific emissions by 50-75%.")

    # 2. Positive Reinforcement
    if trips_df['Mode'].str.contains("Walk").any() or trips_df['Mode'].str.contains("Cycle").any():
        insights.append("✅ **Health Bonus:** Your itinerary includes active transport. This reduces carbon AND improves cardiovascular health.")

    # 3. Overall Benchmark
    total_co2 = trips_df['Emissions'].sum()
    if total_co2 < 2.0:
        insights.append("🏆 **Top Tier:** Your footprint is better than 80% of daily commuters.")
    
    return insights

# --- UI: SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Journey Settings")
    st.info("Build your daily travel plan here.")
    
    mode = st.selectbox("Transport Mode", list(EMISSION_FACTORS.keys()))
    distance = st.number_input("Distance (km)", min_value=0.1, max_value=100.0, value=5.0)
    passengers = st.number_input("Passengers (Inc. Driver)", min_value=1, max_value=6, value=1)
    
    if st.button("➕ Add Trip Leg"):
        # Calculate emissions for this specific leg
        raw_factor = EMISSION_FACTORS[mode]
        # Carpooling logic: Divide emissions by passengers
        actual_emissions = (raw_factor * distance) / passengers
        
        # Add to history
        st.session_state.trips.append({
            "Mode": mode,
            "Distance": distance,
            "Passengers": passengers,
            "Emissions": actual_emissions
        })
        st.success(f"Added: {mode} ({distance}km)")

    st.markdown("---")
    if st.button("🗑️ Reset All Trips"):
        st.session_state.trips = []
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("🌍 EcoCommute Pro: AI Sustainability Analytics")
st.markdown("**1M1B Project | AI-Driven Carbon Patterns Analysis**")

# TABS LAYOUT
tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Analytics", "📋 Trip Details", "ℹ️ About"])

with tab1:
    if len(st.session_state.trips) > 0:
        df = pd.DataFrame(st.session_state.trips)
        
        # KEY METRICS ROW
        total_dist = df['Distance'].sum()
        total_emissions = df['Emissions'].sum()
        eco_score = calculate_eco_score(total_emissions, total_dist)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Distance", f"{total_dist} km")
        col2.metric("Total Footprint", f"{total_emissions:.2f} kg CO2", delta_color="inverse")
        col3.metric("Eco-Score", f"{int(eco_score)}/100")
        col4.metric("Trees to Offset", f"{int(total_emissions/0.06)} Trees")

        st.markdown("---")

        # CHARTS ROW
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📉 Emissions vs Global Average")
            # Create comparison data
            avg_commuter = total_dist * 0.19 # Assumes car usage
            chart_data = pd.DataFrame({
                "Scenario": ["Your Itinerary", "Avg. Car Commuter"],
                "Emissions (kg)": [total_emissions, avg_commuter]
            })
            st.bar_chart(chart_data.set_index("Scenario"), color=["#00CC96"])
            
        with c2:
            st.subheader("🚗 Transport Mix")
            # Simple breakdown of distance by mode
            mode_breakdown = df.groupby("Mode")["Distance"].sum()
            st.bar_chart(mode_breakdown)

        # AI INSIGHTS SECTION
        st.markdown("---")
        st.subheader("🤖 AI Consultant Recommendations")
        with st.spinner("Analyzing your patterns..."):
            time.sleep(1)
            insights = get_ai_consultation(df)
            for i in insights:
                st.info(i)
                
    else:
        st.warning("👈 Start by adding your first trip in the Sidebar!")
        st.image("https://cdn-icons-png.flaticon.com/512/2942/2942076.png", width=100)
        st.write("No data to analyze yet.")

with tab2:
    st.subheader("Your Current Itinerary")
    if len(st.session_state.trips) > 0:
        st.dataframe(pd.DataFrame(st.session_state.trips), use_container_width=True)
        
        # Download Feature
        csv = pd.DataFrame(st.session_state.trips).to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Report (CSV)",
            csv,
            "my_eco_report.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.write("List is empty.")

with tab3:
    st.subheader("Project Methodology")
    st.markdown("""
    **1. Rule-Based AI Engine:**
    Unlike simple calculators, this tool uses a 'Scoring Algorithm' to grade user behavior against a standard sustainability index.
    
    **2. Dynamic Data Processing:**
    It handles 'Multi-Leg Journeys' (e.g., Bike -> Train -> Walk) to build a complete profile of a user's day.
    
    **3. Emission Factors Used (kg CO2/km):**
    * Car (Petrol): 0.19
    * Bus (Electric): 0.04
    * Train: 0.03
    """)