"""
Skannr AI Analytics Dashboard - Production Ready
All deprecation warnings fixed
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import engine
from models import TriageLog, ClinicianFeedback
from sqlalchemy.orm import sessionmaker

# ============================================
# PAGE CONFIG & STYLING
# ============================================
st.set_page_config(
    page_title="Skannr AI Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
    h1 { color: #f59e0b !important; font-weight: 700 !important; }
    h2, h3 { color: #e2e8f0 !important; font-weight: 600 !important; }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 16px;
        padding: 20px;
    }
    [data-testid="metric-container"] label { color: #94a3b8 !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f59e0b !important; font-size: 32px !important; font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #1e293b; border-radius: 12px; padding: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 8px; color: #94a3b8; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #1a1a2e !important; }
    [data-testid="stForm"] { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border: 1px solid #475569; border-radius: 16px; padding: 24px; }
    .stButton > button { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #1a1a2e; border: none; border-radius: 8px; font-weight: 600; }
    hr { border-color: #334155 !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Database session
Session = sessionmaker(bind=engine)
session = Session()

# ============================================
# LOAD DATA
# ============================================
try:
    triage_logs = session.query(TriageLog).all()
    triage_df = pd.DataFrame([{
        "id": t.id, "created_at": t.created_at, "symptoms_text": t.symptoms_text,
        "age": t.age, "sex": t.sex, "pregnancy": t.pregnancy, "implants": t.implants,
        "location": t.location, "triage": t.triage, "primary_modality": t.primary_modality,
        "primary_priority": t.primary_priority, "model_name": t.model_name
    } for t in triage_logs])
    if not triage_df.empty:
        triage_df['created_at'] = pd.to_datetime(triage_df['created_at'])
        triage_df['date'] = triage_df['created_at'].dt.date
except Exception as e:
    st.error(f"Error loading triage logs: {e}")
    triage_df = pd.DataFrame()

try:
    feedback_logs = (
        session.query(ClinicianFeedback, TriageLog)
        .join(TriageLog, ClinicianFeedback.triage_log_id == TriageLog.id)
        .order_by(ClinicianFeedback.id.desc()).all()
    )
    feedback_df = pd.DataFrame([{
        "id_fb": fb.id, "triage_log_id": tl.id, "clinician_scan": fb.clinician_scan,
        "accepted_recommendation": fb.accepted_recommendation, "comment": fb.comment,
        "created_at": tl.created_at, "primary_modality": tl.primary_modality, "symptoms_text": tl.symptoms_text,
    } for fb, tl in feedback_logs])
    if not feedback_df.empty:
        feedback_df['created_at'] = pd.to_datetime(feedback_df['created_at'])
except Exception as e:
    st.error(f"Error loading feedback: {e}")
    feedback_df = pd.DataFrame()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 28px; margin-bottom: 5px;">Skannr AI</h1>
        <p style="color: #94a3b8; font-size: 14px;">Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Quick Stats")
    if not triage_df.empty:
        st.metric("Total Cases", len(triage_df))
        st.metric("Emergencies", (triage_df["triage"] == "URGENT_EMERGENCY").sum())
        if not feedback_df.empty:
            st.metric("AI Accuracy", f"{feedback_df['accepted_recommendation'].mean() * 100:.1f}%")
    st.markdown("---")
    st.markdown('<p style="color: #64748b; font-size: 12px; text-align: center;">Dashboard v3.0</p>', unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Skannr AI Analytics")
    st.markdown('<p style="color: #94a3b8;">Real-time monitoring of AI triage performance</p>', unsafe_allow_html=True)
with col2:
    if not triage_df.empty:
        st.markdown("""
        <div style="background: #065f46; border-radius: 12px; padding: 15px; text-align: center;">
            <p style="color: #a7f3d0; font-size: 12px; margin: 0;">Status</p>
            <p style="color: #ecfdf5; font-size: 18px; font-weight: 700; margin: 5px 0;">● Online</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

if triage_df.empty:
    st.warning("⚠️ No triage logs found yet.")
    st.stop()

# ============================================
# KEY METRICS
# ============================================
total_cases = len(triage_df)
emergency_cases = (triage_df["triage"] == "URGENT_EMERGENCY").sum()
non_emergency_cases = (triage_df["triage"] == "NON_EMERGENCY").sum()
cases_with_feedback = feedback_df["triage_log_id"].nunique() if not feedback_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cases", f"{int(total_cases):,}")
col2.metric("Emergencies", f"{int(emergency_cases)}", f"{emergency_cases/total_cases*100:.1f}%")
col3.metric("Non-Emergency", f"{int(non_emergency_cases)}", f"{non_emergency_cases/total_cases*100:.1f}%")
col4.metric("Feedback", int(cases_with_feedback), f"{cases_with_feedback/total_cases*100:.1f}%")

st.markdown("---")

# ============================================
# AI PERFORMANCE
# ============================================
st.header("🤖 AI Performance")

if not feedback_df.empty:
    agreement_rate = feedback_df["accepted_recommendation"].mean()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=agreement_rate * 100,
            title={'text': "Agreement Rate", 'font': {'size': 16, 'color': '#e2e8f0'}},
            number={'suffix': "%", 'font': {'size': 36, 'color': '#f59e0b'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#f59e0b'},
                'bgcolor': '#1e293b',
                'steps': [
                    {'range': [0, 60], 'color': '#7f1d1d'},
                    {'range': [60, 80], 'color': '#78350f'},
                    {'range': [80, 100], 'color': '#14532d'}
                ],
                'threshold': {'line': {'color': '#22c55e', 'width': 4}, 'thickness': 0.75, 'value': 80}
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    col2.metric("Override Rate", f"{(1-agreement_rate)*100:.1f}%")
    col3.metric("Disagreements", min(5, len(feedback_df[~feedback_df["accepted_recommendation"]])))
    col4.metric("Coverage", f"{len(feedback_df)/total_cases*100:.1f}%")
else:
    st.info("Waiting for clinician feedback...")

st.markdown("---")

# ============================================
# AGREEMENT ANALYSIS
# ============================================
st.header("🎯 Agreement Analysis")

if not feedback_df.empty and len(feedback_df) > 0:
    tab1, tab2, tab3 = st.tabs(["Heatmap", "Disagreements", "Feedback"])
    
    with tab1:
        st.subheader("AI vs Clinician Decisions")
        
        comparison = feedback_df.groupby(["primary_modality", "clinician_scan"]).size().reset_index(name="count")
        comparison.columns = ["AI Scan", "Clinician Scan", "Count"]
        pivot = comparison.pivot(index="AI Scan", columns="Clinician Scan", values="Count").fillna(0)
        
        if not pivot.empty:
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values, x=pivot.columns, y=pivot.index,
                colorscale=[[0, '#1e293b'], [0.5, '#0ea5e9'], [1, '#f59e0b']],
                hovertemplate="AI: %{y}<br>Clinician: %{x}<br>Count: %{z}<extra></extra>",
                colorbar=dict(title=dict(text="Cases", font=dict(color='#e2e8f0')))
            ))
            
            for i, row in enumerate(pivot.index):
                for j, col in enumerate(pivot.columns):
                    val = pivot.iloc[i, j]
                    if val > 0:
                        fig.add_annotation(x=col, y=row, text=str(int(val)), showarrow=False,
                            font=dict(color='white', size=14, family='Arial Black'))
            
            fig.update_layout(
                title=dict(text='<b>Agreement Matrix</b>', font=dict(size=18, color='#e2e8f0')),
                xaxis=dict(
                    title=dict(text='Clinician Decision', font=dict(color='#e2e8f0')),
                    tickangle=45, tickfont=dict(size=11, color='#94a3b8'), gridcolor='#334155'
                ),
                yaxis=dict(
                    title=dict(text='AI Recommendation', font=dict(color='#e2e8f0')),
                    tickfont=dict(size=11, color='#94a3b8'), gridcolor='#334155'
                ),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0f172a',
                height=500, margin=dict(l=150, r=50, t=80, b=150)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Detailed Breakdown")
            st.dataframe(comparison.sort_values("Count", ascending=False), use_container_width=True, hide_index=True)
        
        # Agreement by scan type
        st.markdown("#### Agreement by Scan Type")
        scan_agreement = feedback_df.groupby('primary_modality').agg({
            'accepted_recommendation': ['sum', 'count', 'mean']
        }).reset_index()
        scan_agreement.columns = ['Scan Type', 'Agreements', 'Total', 'Rate']
        scan_agreement['Rate'] = scan_agreement['Rate'] * 100
        scan_agreement = scan_agreement.sort_values('Rate', ascending=True)
        
        colors = ['#ef4444' if r < 60 else '#f59e0b' if r < 80 else '#22c55e' for r in scan_agreement['Rate']]
        
        fig = go.Figure(go.Bar(
            y=scan_agreement['Scan Type'], x=scan_agreement['Rate'], orientation='h',
            marker=dict(color=colors),
            text=[f"{r:.0f}%" for r in scan_agreement['Rate']],
            textposition='outside', textfont=dict(color='#e2e8f0')
        ))
        fig.add_vline(x=80, line_dash="dash", line_color="#22c55e", annotation_text="Target: 80%")
        fig.update_layout(
            xaxis=dict(title=dict(text='Agreement Rate (%)', font=dict(color='#e2e8f0')), 
                      range=[0, 110], tickfont=dict(color='#94a3b8'), gridcolor='#334155'),
            yaxis=dict(tickfont=dict(color='#94a3b8')),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0f172a',
            height=max(300, len(scan_agreement) * 40), margin=dict(l=20, r=80, t=20, b=50)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Where AI Gets It Wrong")
        disagreements = feedback_df[~feedback_df["accepted_recommendation"]]
        
        if len(disagreements) > 0:
            col1, col2 = st.columns(2)
            with col1:
                ai_overridden = disagreements['primary_modality'].value_counts().head(5)
                fig = go.Figure(go.Bar(x=ai_overridden.values, y=ai_overridden.index, orientation='h',
                    marker=dict(color='#ef4444'), text=ai_overridden.values, textposition='outside'))
                fig.update_layout(title="Most Overridden AI Scans", paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='#0f172a', height=300, xaxis=dict(gridcolor='#334155'),
                    yaxis=dict(tickfont=dict(color='#94a3b8')))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                clinician_preferred = disagreements['clinician_scan'].value_counts().head(5)
                fig = go.Figure(go.Bar(x=clinician_preferred.values, y=clinician_preferred.index, orientation='h',
                    marker=dict(color='#22c55e'), text=clinician_preferred.values, textposition='outside'))
                fig.update_layout(title="Clinician Preferred", paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='#0f172a', height=300, xaxis=dict(gridcolor='#334155'),
                    yaxis=dict(tickfont=dict(color='#94a3b8')))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Recent Disagreements")
            disp = disagreements[['created_at', 'primary_modality', 'clinician_scan', 'comment']].head(5)
            disp.columns = ['Date', 'AI Said', 'Clinician Chose', 'Comment']
            st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 Perfect agreement!")
    
    with tab3:
        st.subheader("Recent Feedback")
        disp = feedback_df[['created_at', 'primary_modality', 'clinician_scan', 'accepted_recommendation', 'comment']].head(25)
        disp.columns = ['Date', 'AI Scan', 'Clinician Scan', 'Accepted', 'Comment']
        disp['Accepted'] = disp['Accepted'].apply(lambda x: '✅' if x else '❌')
        st.dataframe(disp, use_container_width=True, hide_index=True)
else:
    st.info("Waiting for feedback data...")

st.markdown("---")

# ============================================
# VOLUME & TRENDS
# ============================================
st.header("Volume & Trends")

col1, col2 = st.columns(2)

with col1:
    daily_volume = triage_df.groupby('date').size().reset_index(name='count')
    fig = go.Figure(go.Scatter(x=daily_volume['date'], y=daily_volume['count'], mode='lines+markers',
        line=dict(color='#f59e0b', width=3), fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.1)'))
    fig.update_layout(title="Daily Volume", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0f172a',
        xaxis=dict(gridcolor='#334155', tickfont=dict(color='#94a3b8')),
        yaxis=dict(gridcolor='#334155', tickfont=dict(color='#94a3b8')), height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    triage_counts = triage_df['triage'].value_counts()
    fig = go.Figure(go.Pie(labels=triage_counts.index, values=triage_counts.values, hole=0.6,
        marker=dict(colors=['#22c55e', '#ef4444']), textinfo='label+percent'))
    fig.update_layout(title="Classification", paper_bgcolor='rgba(0,0,0,0)', height=300,
        annotations=[dict(text=f'{total_cases}', x=0.5, y=0.5, font=dict(size=24, color='#e2e8f0'), showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# SCAN DISTRIBUTION
# ============================================
st.header("🔬 Scan Distribution")

scan_counts = triage_df['primary_modality'].value_counts().head(10)
fig = go.Figure(go.Bar(y=scan_counts.index, x=scan_counts.values, orientation='h',
    marker=dict(color=px.colors.sequential.YlOrBr[:len(scan_counts)][::-1]),
    text=scan_counts.values, textposition='outside', textfont=dict(color='#e2e8f0')))
fig.update_layout(title="Top Recommended Scans", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0f172a',
    xaxis=dict(gridcolor='#334155', tickfont=dict(color='#94a3b8')),
    yaxis=dict(tickfont=dict(color='#94a3b8')), height=400, margin=dict(r=80))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# CLINICIAN FEEDBACK FORM
# ============================================
st.header("Submit Clinician Feedback")

if not triage_df.empty:
    triage_df_display = triage_df.copy()
    triage_df_display["label"] = (
        triage_df_display["id"].astype(str) + " | " +
        triage_df_display["created_at"].astype(str) + " | " +
        triage_df_display["symptoms_text"].str.slice(0, 60)
    )

    selected_label = st.selectbox("Select Case", options=triage_df_display["label"], key="triage_selector")
    selected_row = triage_df_display[triage_df_display["label"] == selected_label].iloc[0]
    selected_id = int(selected_row["id"])

    st.markdown(f"""
    <div style="background: #1e3a5f; border-radius: 12px; padding: 20px; margin: 15px 0; border-left: 4px solid #f59e0b;">
        <p style="color: #94a3b8; font-size: 12px; margin: 0;">AI RECOMMENDATION</p>
        <p style="color: #f59e0b; font-size: 24px; font-weight: 700; margin: 5px 0;">{selected_row['primary_modality']}</p>
        <p style="color: #64748b; margin: 0;">Priority: {selected_row['primary_priority']}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("feedback_form"):
        clinician_scan = st.text_input("Your Decision", value=str(selected_row["primary_modality"] or ""))
        accepted = st.radio("Accept AI?", ["✅ Yes", "❌ No"], horizontal=True)
        comment = st.text_area("Notes (optional)")
        
        if st.form_submit_button(" Submit"):
            try:
                new_feedback = ClinicianFeedback(
                    triage_log_id=selected_id,
                    clinician_scan=clinician_scan,
                    accepted_recommendation=accepted.startswith("✅"),
                    comment=comment or None,
                )
                session.add(new_feedback)
                session.commit()
                st.success("✅ Saved! Refresh to see updates.")
            except Exception as e:
                session.rollback()
                st.error(f"Error: {e}")

st.markdown("---")

# ============================================
# RECENT LOGS
# ============================================
st.header("Recent Triage Logs")

recent = triage_df.sort_values("created_at", ascending=False).head(30)[[
    'created_at', 'symptoms_text', 'age', 'sex', 'triage', 'primary_modality'
]].copy()
recent['triage'] = recent['triage'].apply(lambda x: f" {x}" if x == "URGENT_EMERGENCY" else f" {x}")
recent.columns = ['Time', 'Symptoms', 'Age', 'Sex', 'Triage', 'Scan']
st.dataframe(recent, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #64748b;">Skannr AI | Dashboard v3.0</p>', unsafe_allow_html=True)