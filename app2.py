# BioVentureRx - Streamlit App for Drug NPV Graphing with Full Column Structure

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="BioVentureRx - Dynamic rNPV Explorer", layout="wide")

# Main Title
st.title("BioVentureRx - Dynamic rNPV Explorer")

# Short Introduction
st.write(
    "This app was created to provide a more interactive way to explore important financial modeling work in the life sciences. "
    "Using an illustrative case based on Entresto, as modeled by Richard Z. Xie, Tess Cameron, and Peter Kolchinsky, "
    "this app highlights how the Inflation Reduction Act (IRA) introduces policies that could significantly affect biotech investment. "
    "It is critical to showcase real-world examples of how early-stage innovation may be impacted."
)

# Info box giving full academic credit
st.info(
    "The Entresto-based example showcased here is based on research published by Richard Z. Xie, Tess Cameron, and Peter Kolchinsky: "
    "*The Impact of the Inflation Reduction Act on Investment in Innovative Medicines: A Project-Level Analysis*, "
    "published in Therapeutic Innovation & Regulatory Science (2025). "
    "The authors have made their model and findings publicly available to foster broader understanding. "
    "This app showcases their work, and similar studies in the future, purely for educational and illustrative purposes.\n\n"
    "**Original article link:** [https://doi.org/10.1007/s43441-025-00768-0](https://doi.org/10.1007/s43441-025-00768-0)"
)

# Upload CSV
uploaded_file = st.file_uploader("Upload your Drug Portfolio CSV", type=["csv"])

expected_columns = [
    'Drug', 'Approval Year', 'Molecule Type', 'Indication',
    'Market_Pre_IRA', 'Market_Post_IRA',
    'Filing_Pre_IRA', 'Filing_Post_IRA',
    'Phase 3_Pre_IRA', 'Phase 3_Post_IRA',
    'Phase 2_Pre_IRA', 'Phase 2_Post_IRA',
    'Phase 1_Pre_IRA', 'Phase 1_Post_IRA',
    'PC_Pre_IRA', 'PC_Post_IRA',
    'Seed_Pre_IRA', 'Seed_Post_IRA'
]

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in expected_columns):
        st.error("Uploaded file missing required columns. Please use the provided template.")
        st.stop()
else:
    # Default Entresto example
    data = {
        'Drug': ['Entresto'],
        'Approval Year': [2015],
        'Molecule Type': ['Small Molecule'],
        'Indication': ['Heart Failure'],
        'Market_Pre_IRA': [2976], 'Market_Post_IRA': [1782],
        'Filing_Pre_IRA': [2262], 'Filing_Post_IRA': [1355],
        'Phase 3_Pre_IRA': [1105], 'Phase 3_Post_IRA': [618],
        'Phase 2_Pre_IRA': [272], 'Phase 2_Post_IRA': [133],
        'Phase 1_Pre_IRA': [82], 'Phase 1_Post_IRA': [16],
        'PC_Pre_IRA': [32], 'PC_Post_IRA': [-34],
        'Seed_Pre_IRA': [7], 'Seed_Post_IRA': [-59]
    }
    df = pd.DataFrame(data)

# Sidebar Filters
st.sidebar.header("Portfolio Filters")
st.sidebar.selectbox("View Mode", options=["Drug View"], index=0)
phases_order = ['Market', 'Filing', 'Phase 3', 'Phase 2', 'Phase 1', 'PC', 'Seed']

selected_phase = st.sidebar.selectbox("Select Development Phase", options=["All Phases"] + phases_order)
selected_drug = st.sidebar.selectbox("Select Drug", options=df['Drug'].unique())

# Filter drug
drug_row = df[df['Drug'] == selected_drug].iloc[0]

# Build plot_df
plot_data = []
for phase in phases_order:
    pre = drug_row[f'{phase}_Pre_IRA']
    post = drug_row[f'{phase}_Post_IRA']
    drop = (pre - post) / pre * 100 if pre != 0 else 0
    plot_data.append({'Phase': phase, 'Pre-IRA': pre, 'Post-IRA': post, '% Drop': drop})

plot_df = pd.DataFrame(plot_data)

# Plotting
st.subheader(f":bar_chart: NPV Impact Graph - {selected_drug}")

if selected_phase == "All Phases":
    fig = go.Figure()
    fig.add_trace(go.Bar(x=plot_df['Phase'], y=plot_df['Pre-IRA'], name='Pre-IRA', marker_color='#003366'))
    fig.add_trace(go.Bar(x=plot_df['Phase'], y=plot_df['Post-IRA'], name='Post-IRA', marker_color='#3399FF'))
    fig.add_trace(go.Scatter(
        x=plot_df['Phase'],
        y=-plot_df['% Drop'],
        name='% NPV Drop',
        yaxis='y2',
        mode='lines+markers+text',
        text=[f"{round(val)}%" for val in -plot_df['% Drop']],
        textposition='top center',
        marker_color='black'
    ))

    fig.update_layout(
        title=f'NPV Impact (Pre vs Post IRA) - {selected_drug}',
        xaxis_title='Development Phase',
        yaxis=dict(title='Net Present Value ($M)', side='left'),
        yaxis2=dict(title='% Drop in NPV', overlaying='y', side='right', range=[-1000, 0]),
        barmode='group',
        legend=dict(x=0.8, y=1.2),
        height=600
    )
else:
    phase_df = plot_df[plot_df['Phase'] == selected_phase]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=['Pre-IRA', 'Post-IRA'], y=[phase_df['Pre-IRA'].values[0], phase_df['Post-IRA'].values[0]], marker_color=['#003366', '#3399FF']))
    fig.add_trace(go.Scatter(
        x=['Pre-IRA', 'Post-IRA'],
        y=[0, 0],
        mode='text',
        text=[f"{round(phase_df['% Drop'].values[0])}%" if phase_df['Pre-IRA'].values[0] != 0 else "", ""],
        textposition='top center',
        marker_color='black',
        showlegend=False
    ))
    fig.update_layout(title=f'NPV at {selected_phase} Phase - {selected_drug}', yaxis_title='Net Present Value ($M)', height=500)

st.plotly_chart(fig, use_container_width=True)

# Download Option
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(":calendar: Download Results as CSV", csv, "BioVentureRx_Phase_NPV_Results.csv", "text/csv")
