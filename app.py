import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from src.data_loader import DataLoader
from src.analysis import Analyzer

# Page Configuration
st.set_page_config(
    page_title="Market Sentiment Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #000000 !important;
        font-weight: 700 !important;
        text-align: center;
        padding: 1.5rem 0;
    }
    
    h2 {
        color: #000000 !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    h3 {
        color: #000000 !important;
        font-weight: 600;
    }
    
    h4 {
        color: #000000 !important;
        font-weight: 600;
    }
    
    /* General text */
    p {
        color: #000000 !important;
    }
    
    /* Streamlit default text */
    .stMarkdown {
        color: #000000 !important;
    }
    
    /* Custom white heading class */
    .white-heading h3 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #4b5563;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e0e7ff 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1e40af;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        background-color: white;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        border: 2px dashed #667eea;
    }
    
    /* Cards */
    div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div style='text-align: center; padding: 2rem; background: white; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
        <h1 style='font-size: 3rem; margin: 0;'>📊 Market Sentiment Analysis</h1>
        <p style='color: #6b7280; font-size: 1.2rem; margin-top: 0.5rem;'>
            Understanding How Fear & Greed Drive Trading Behavior on Hyperliquid
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Data Configuration")
    st.markdown("---")
    
    # File uploaders with better styling
    st.markdown("#### 📈 Sentiment Data")
    sentiment_file = st.file_uploader(
        "Upload sentiment CSV file",
        type=['csv'],
        key="sentiment",
        help="Upload a CSV file containing market sentiment data"
    )
    
    st.markdown("#### 💹 Trading Data")
    trades_file = st.file_uploader(
        "Upload trades CSV file",
        type=['csv'],
        key="trades",
        help="Upload a CSV file containing trading data"
    )
    
    st.markdown("---")
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center;'>
            <p style='margin: 0; font-weight: 600;'>💡 Quick Tip</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                Upload your CSV files above or place them in the 'data/' folder
            </p>
        </div>
    """, unsafe_allow_html=True)

# Check local data folder if no uploads
local_sentiment = 'data/sentiment.csv'
local_trades = 'data/trades.csv'
local_data_exists = os.path.exists(local_sentiment) and os.path.exists(local_trades)

if (sentiment_file and trades_file) or local_data_exists:
    try:
        with st.spinner('🔄 Loading and processing data...'):
            if sentiment_file and trades_file:
                loader = DataLoader(sentiment_file, trades_file)
                sentiment_df, trades_df, merged_df = loader.preprocess_data(
                    pd.read_csv(sentiment_file), 
                    pd.read_csv(trades_file)
                )
            elif local_data_exists:
                st.info("📂 No files uploaded. Using local files from 'data/' folder.")
                loader = DataLoader(local_sentiment, local_trades)
                s_df = pd.read_csv(local_sentiment)
                t_df = pd.read_csv(local_trades)
                sentiment_df, trades_df, merged_df = loader.preprocess_data(s_df, t_df)

        analyzer = Analyzer(merged_df)
        
        # Key Metrics Section
        st.markdown("<div class='white-heading'><h3>📊 Key Metrics Overview</h3></div>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📈 Total Trades",
                value=f"{len(trades_df):,}",
                delta="Active dataset"
            )
        
        with col2:
            st.metric(
                label="👥 Total Traders",
                value=f"{trades_df['account'].nunique():,}",
                delta="Unique accounts"
            )
        
        with col3:
            total_pnl = merged_df['closedPnL'].sum()
            st.metric(
                label="💰 Total PnL",
                value=f"${total_pnl:,.2f}",
                delta=f"{'Profit' if total_pnl > 0 else 'Loss'}"
            )
        
        with col4:
            avg_leverage = merged_df['leverage'].mean() if 'leverage' in merged_df.columns else 1.0
            st.metric(
                label="⚡ Avg Leverage",
                value=f"{avg_leverage:.2f}x",
                delta="Overall"
            )
        
        st.markdown("---")
        
        # Tabbed Interface
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Data Overview",
            "📊 Performance Analysis",
            "🎯 Trader Segmentation",
            "🚀 Strategy Recommendations"
        ])
        
        with tab1:
            st.markdown("### 📋 Data Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 😨😄 Sentiment Data Sample")
                st.dataframe(
                    sentiment_df.head(10),
                    width='stretch',
                    hide_index=False
                )
                
                # Sentiment distribution
                if 'Classification' in sentiment_df.columns:
                    sentiment_counts = sentiment_df['Classification'].value_counts()
                    fig_sentiment = px.pie(
                        values=sentiment_counts.values,
                        names=sentiment_counts.index,
                        title="Market Sentiment Distribution",
                        color_discrete_sequence=['#ef4444', '#22c55e'],
                        hole=0.4
                    )
                    fig_sentiment.update_layout(
                        font=dict(size=14),
                        showlegend=True,
                        height=400
                    )
                    st.plotly_chart(fig_sentiment, width='stretch')
            
            with col2:
                st.markdown("#### 💹 Trading Data Sample")
                st.dataframe(
                    trades_df.head(10),
                    width='stretch',
                    hide_index=False
                )
                
                # PnL distribution
                fig_pnl_dist = px.histogram(
                    trades_df,
                    x='closedPnL',
                    nbins=50,
                    title="PnL Distribution",
                    color_discrete_sequence=['#667eea']
                )
                fig_pnl_dist.update_layout(
                    xaxis_title="Closed PnL ($)",
                    yaxis_title="Frequency",
                    height=400
                )
                st.plotly_chart(fig_pnl_dist, width='stretch')

        with tab2:
            st.markdown("### 📊 Performance Analysis")
            
            comparison = analyzer.compare_sentiment_performance()
            
            # Display comparison table
            st.markdown("#### 📈 Sentiment Performance Comparison")
            
            # Flatten MultiIndex columns for display
            comparison_display = comparison.copy()
            comparison_display.columns = [
                '_'.join(col).strip('_') if isinstance(col, tuple) else col 
                for col in comparison_display.columns
            ]
            st.dataframe(comparison_display, width='stretch')
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Flatten MultiIndex for plotting
                comparison_flat = comparison.reset_index()
                comparison_flat.columns = [
                    '_'.join(col).strip('_') if isinstance(col, tuple) else col 
                    for col in comparison_flat.columns
                ]
                
                fig_pnl = px.bar(
                    comparison_flat,
                    x='Classification',
                    y='closedPnL_mean',
                    title="Average PnL by Sentiment",
                    color='Classification',
                    color_discrete_map={'Fear': '#ef4444', 'Greed': '#22c55e'}
                )
                fig_pnl.update_layout(
                    xaxis_title="Market Sentiment",
                    yaxis_title="Average PnL ($)",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_pnl, width='stretch')
            
            with col2:
                # Win rate comparison
                fig_win = px.bar(
                    comparison_flat,
                    x='Classification',
                    y='win_rate_mean',
                    title="Win Rate by Sentiment",
                    color='Classification',
                    color_discrete_map={'Fear': '#ef4444', 'Greed': '#22c55e'}
                )
                fig_win.update_layout(
                    xaxis_title="Market Sentiment",
                    yaxis_title="Win Rate",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_win, width='stretch')
            
            # Leverage analysis
            if 'leverage' in merged_df.columns:
                st.markdown("#### ⚡ Leverage Distribution Analysis")
                
                # Create a copy to avoid modifying the original dataframe
                leverage_df = merged_df.copy()
                leverage_df['leverage'] = pd.to_numeric(leverage_df['leverage'], errors='coerce')
                
                # Remove null values and filter out extreme outliers for better visualization
                leverage_df = leverage_df.dropna(subset=['leverage', 'Classification'])
                
                # Optional: Filter extreme outliers (leverage > 100x is unusual)
                leverage_df = leverage_df[leverage_df['leverage'] <= 100]
                
                if len(leverage_df) > 0:
                    fig_lev = px.box(
                        leverage_df,
                        x='Classification',
                        y='leverage',
                        title="Leverage Distribution by Market Sentiment",
                        color='Classification',
                        color_discrete_map={'Fear': '#ef4444', 'Greed': '#22c55e'}
                    )
                    fig_lev.update_layout(
                        xaxis_title="Market Sentiment",
                        yaxis_title="Leverage (x)",
                        showlegend=False,
                        height=400
                    )
                    st.plotly_chart(fig_lev, width='stretch')
                    
                    # Add summary statistics
                    col1, col2 = st.columns(2)
                    with col1:
                        fear_lev = leverage_df[leverage_df['Classification'] == 'Fear']['leverage']
                        if len(fear_lev) > 0:
                            st.metric(
                                "😨 Avg Leverage (Fear)",
                                f"{fear_lev.mean():.2f}x",
                                f"Median: {fear_lev.median():.2f}x"
                            )
                    with col2:
                        greed_lev = leverage_df[leverage_df['Classification'] == 'Greed']['leverage']
                        if len(greed_lev) > 0:
                            st.metric(
                                "😄 Avg Leverage (Greed)",
                                f"{greed_lev.mean():.2f}x",
                                f"Median: {greed_lev.median():.2f}x"
                            )
                else:
                    st.warning("⚠️ No valid leverage data available after cleaning.")

        with tab3:
            st.markdown("### 🎯 Trader Segmentation Analysis")
            
            segments = analyzer.segment_traders()
            
            # Cluster visualization
            fig_cluster = px.scatter(
                segments,
                x='leverage',
                y='win_rate',
                color='cluster',
                size='total_trades',
                hover_data=[segments.index],
                title="Trader Clusters: Leverage vs Win Rate",
                color_continuous_scale='viridis',
                labels={
                    'leverage': 'Average Leverage (x)',
                    'win_rate': 'Win Rate',
                    'cluster': 'Cluster ID'
                }
            )
            fig_cluster.update_layout(height=500)
            st.plotly_chart(fig_cluster, width='stretch')
            
            # Cluster statistics
            st.markdown("#### 📊 Cluster Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                cluster_stats = segments.groupby('cluster').mean()
                st.dataframe(cluster_stats, width='stretch')
            
            with col2:
                cluster_counts = segments['cluster'].value_counts().sort_index()
                fig_cluster_dist = px.bar(
                    x=cluster_counts.index,
                    y=cluster_counts.values,
                    title="Traders per Cluster",
                    labels={'x': 'Cluster ID', 'y': 'Number of Traders'},
                    color=cluster_counts.values,
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_cluster_dist, width='stretch')

        with tab4:
            st.markdown("### 🚀 Actionable Strategy Recommendations")
            
            recs = analyzer.get_strategy_recommendations()
            
            for i, rec in enumerate(recs, 1):
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; 
                                border-radius: 10px; 
                                margin: 1rem 0;
                                color: white;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                        <h4 style='margin: 0; color: white;'>💡 Strategy #{i}</h4>
                        <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem;'>{rec}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Additional insights
            st.markdown("---")
            st.markdown("### 📈 Key Insights")
            
            comparison = analyzer.compare_sentiment_performance()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div style='background-color: #fef3c7; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #f59e0b;'>
                        <h4 style='color: #92400e; margin-top: 0;'>⚠️ Risk Considerations</h4>
                        <ul style='color: #78350f;'>
                            <li>Monitor leverage levels during high volatility periods</li>
                            <li>Implement strict stop-loss mechanisms</li>
                            <li>Diversify trading strategies across market conditions</li>
                            <li>Consider sentiment shifts as early warning signals</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div style='background-color: #dbeafe; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #3b82f6;'>
                        <h4 style='color: #1e40af; margin-top: 0;'>✅ Best Practices</h4>
                        <ul style='color: #1e3a8a;'>
                            <li>Track historical sentiment patterns for better predictions</li>
                            <li>Combine sentiment analysis with technical indicators</li>
                            <li>Regularly review and adjust position sizes</li>
                            <li>Maintain detailed trading logs for continuous improvement</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        
        with st.expander("🔍 Debug Information"):
            if 'sentiment_df' in locals():
                st.write("**Sentiment Columns:**", list(sentiment_df.columns))
            if 'trades_df' in locals():
                st.write("**Trades Columns:**", list(trades_df.columns))
            st.write("**Expected Columns:**")
            st.markdown("""
                - **Sentiment Data:** 'Date', 'Classification'
                - **Trades Data:** 'time'/'timestamp', 'account', 'closedPnL'
            """)

else:
    # Welcome screen
    st.markdown("""
        <div style='text-align: center; padding: 3rem 2rem 2rem 2rem; background: white; border-radius: 20px; margin-top: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <h2 style='color: #667eea; margin-bottom: 1rem; font-size: 2.5rem;'>🚀 Get Started</h2>
            <p style='color: #6b7280; font-size: 1.2rem; margin-bottom: 2rem;'>
                Upload your data files to begin analyzing market sentiment and trading performance
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Using Streamlit columns for better compatibility
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); 
                        border-radius: 15px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>📁</div>
                <h3 style='color: #0369a1; margin: 1rem 0;'>Upload Files</h3>
                <p style='color: #334155; font-size: 1rem;'>Use the sidebar to upload your sentiment and trading data</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                        border-radius: 15px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>📂</div>
                <h3 style='color: #15803d; margin: 1rem 0;'>Local Files</h3>
                <p style='color: #334155; font-size: 1rem;'>Place CSV files in the 'data/' folder for automatic loading</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                        border-radius: 15px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>📊</div>
                <h3 style='color: #a16207; margin: 1rem 0;'>Analyze</h3>
                <p style='color: #334155; font-size: 1rem;'>Get insights on how sentiment affects trading performance</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #ffffff; padding: 1rem;'>
        <p style='margin: 0; color: #ffffff;'>Built using Streamlit | Market Sentiment Analysis Dashboard</p>
    </div>
""", unsafe_allow_html=True)
