import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --- 1. SYSTEM CONFIGURATION & DYNAMIC THEME ---
st.set_page_config(page_title="USSD Security Framework", layout="wide")

# Logical switch for background color
# If not logged in as personnel, the background is Maroon (#800000)
if 'personnel_auth' not in st.session_state or not st.session_state.personnel_auth:
    page_bg = "#800000"
    content_color = "#FFFFFF"
else:
    # Once logged in as personnel, background shifts to a professional grey
    page_bg = "#F0F2F6"
    content_color = "#000000"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {page_bg};
    }}
    h1, h2, h3, p, span, .stMarkdown {{
        color: {content_color} !important;
    }}
    /* USSD Mobile UI Simulation */
    .ussd-container {{
        background-color: #000000;
        color: #00FF00;
        padding: 30px;
        border-radius: 35px;
        border: 8px solid #333333;
        max-width: 380px;
        margin: auto;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 0px 20px 40px rgba(0,0,0,0.6);
    }}
    /* Custom Maroon Button for the USSD Interface */
    .stButton>button {{
        background-color: #5a0000;
        color: white;
        border: 1px solid #ffffff;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND DATA PERSISTENCE ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Incident", "Location", "Weight", "Time", "Device_ID"])
if 'audit_trail' not in st.session_state:
    st.session_state.audit_trail = pd.DataFrame(columns=["Timestamp", "Personnel", "Action"])
if 'personnel_auth' not in st.session_state:
    st.session_state.personnel_auth = False

LANDMARKS = {
    "Market Area": [6.5244, 3.3792],
    "School Zone": [6.4550, 3.3841],
    "Residential Area": [6.5000, 3.3670]
}

# --- 3. SIDEBAR: PERSONNEL ONLY LOGIN ---
# This is the only place where a password (thesis2026) is required.
st.sidebar.title("👮 Personnel Command")
if not st.session_state.personnel_auth:
    with st.sidebar.form("personnel_login"):
        p_id = st.text_input("Personnel ID")
        p_key = st.text_input("Access Key", type="password")
        if st.form_submit_button("Enter Dashboard"):
            if p_key.lower() == "thesis2026":
                st.session_state.personnel_auth = True
                st.session_state.current_user = p_id
                # Record login action
                log = pd.DataFrame([{"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                     "Personnel": p_id, "Action": "Accessed Tactical View"}])
                st.session_state.audit_trail = pd.concat([st.session_state.audit_trail, log], ignore_index=True)
                st.rerun()
            else:
                st.sidebar.error("Invalid Personnel Key")
else:
    st.sidebar.success(f"Active Session: {st.session_state.current_user}")
    if st.sidebar.button("Log Out"):
        st.session_state.personnel_auth = False
        st.rerun()

# --- 4. PORTAL ROUTING ---

# SCENARIO A: Public Access (No Password Required)
if not st.session_state.personnel_auth:
    st.title("🛡️ Hybrid USSD Security Mapping Framework")
    st.subheader("Simulating Zero-Data Offline Incident Reporting")
    st.divider()

    col_sim, col_doc = st.columns([1, 1.2])

    with col_sim:
        st.markdown('<div class="ussd-container">', unsafe_allow_html=True)
        st.markdown("### GSM TERMINAL")
        st.markdown("**Session: *123#**")
        st.markdown("---")
        st.markdown("1. Robbery<br>2. Kidnapping<br>3. Suspicious Activity", unsafe_allow_html=True)
        
        with st.form("ussd_report", clear_on_submit=True):
            user_input = st.text_input("Select Option (1-3)")
            user_loc = st.selectbox("Current Landmark", list(LANDMARKS.keys()))
            if st.form_submit_button("SEND SIGNAL"):
                mapping = {"1": "Robbery", "2": "Kidnapping", "3": "Suspicious Activity"}
                if user_input in mapping:
                    report = pd.DataFrame([{
                        "Incident": mapping[user_input],
                        "Location": user_loc,
                        "Weight": 20 if user_input == "2" else 10,
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Device_ID": "SIM_GSM_803" # Simulated ID
                    }])
                    st.session_state.db = pd.concat([st.session_state.db, report], ignore_index=True)
                    st.success("✔ Emergency signal transmitted to headquarters.")
                else:
                    st.error("Invalid USSD Selection")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_doc:
        st.markdown("### Dissertation Simulation Logic")
        st.write("""
        - **Barrier-Free Reporting:** Ordinary citizens can access this reporting terminal instantly. 
        - **Accountability:** Though no password is used by the citizen, the system captures a unique `Device_ID` via the GSM signaling layer.
        - **Low Connectivity:** This represents the offline USSD interface used in rural or low-signal areas.
        """)
        st.info("The Responder Dashboard is restricted. Please use the sidebar to log in as security personnel.")

# SCENARIO B: Personnel Access (Dashboard View)
else:
    st.title(f"👮 Tactical Command Center: {st.session_state.current_user}")
    
    t1, t2 = st.tabs(["🗺️ Incident Intensity Map", "📑 Audit & Accountability"])
    
    with t1:
        if not st.session_state.db.empty:
            m_df = st.session_state.db.copy()
            m_df['lat'] = m_df['Location'].map(lambda x: LANDMARKS[x][0])
            m_df['lon'] = m_df['Location'].map(lambda x: LANDMARKS[x][1])
            
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v10',
                initial_view_state=pdk.ViewState(latitude=6.5, longitude=3.37, zoom=10, pitch=45),
                layers=[pdk.Layer(
                    'ColumnLayer', data=m_df, get_position='[lon, lat]',
                    get_elevation='Weight * 180', radius=400,
                    get_fill_color='[128, 0, 0, 180]', pickable=True
                )]
            ))
        else:
            st.info("No threats currently detected in monitored sectors.")

    with t2:
        st.subheader("Live Incident Database")
        st.dataframe(st.session_state.db.iloc[::-1], use_container_width=True)
        st.divider()
        st.subheader("Personnel Activity Logs")
        st.table(st.session_state.audit_trail.iloc[::-1])
