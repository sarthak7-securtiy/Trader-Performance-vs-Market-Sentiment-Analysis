import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class Analyzer:
    def __init__(self, df):
        self.df = df
        
    def calculate_metrics(self):
        self.df['win'] = self.df['closedPnL'] > 0
        
        # Calculate leverage if missing
        if 'leverage' not in self.df.columns:
            # Assuming leverage = Size USD / Margin ... but margin is usually not given clearly in basic dumps
            # If we have Size USD and Entry Price/Size Tokens, we can't infer leverage directly without Margin used.
            # We will default to 1x leverage if not provided to allow pipeline to continue.
            self.df['leverage'] = 1.0
            
        aggregations = {
            'closedPnL': 'sum',
            'win': 'mean',
            'size': 'mean',
            'symbol': 'count'
        }
        
        if 'leverage' in self.df.columns:
             aggregations['leverage'] = 'mean'
            
        trader_daily_metrics = self.df.groupby(['account', 'date', 'Classification']).agg(aggregations).rename(columns={'symbol': 'trade_count', 'win': 'win_rate', 'size': 'avg_size', 'leverage': 'avg_leverage'}).reset_index()
        
        if 'avg_leverage' not in trader_daily_metrics.columns:
            trader_daily_metrics['avg_leverage'] = 1.0
        
        return trader_daily_metrics

    def compare_sentiment_performance(self):
        metrics = self.calculate_metrics()
        comparison = metrics.groupby('Classification').agg({
            'closedPnL': ['mean', 'median', 'std'],
            'win_rate': 'mean',
            'avg_leverage': 'mean',
            'trade_count': 'mean'
        })
        return comparison

    def segment_traders(self):
        trader_stats = self.df.groupby('account').agg({
            'closedPnL': 'sum',
            'leverage': 'mean',
            'symbol': 'count',
            'win': 'mean'
        }).rename(columns={'symbol': 'total_trades', 'win': 'win_rate'})
        
        features = trader_stats[['leverage', 'total_trades', 'win_rate']].fillna(0)
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
        trader_stats['cluster'] = kmeans.fit_predict(scaled_features)
        
        return trader_stats

    def get_strategy_recommendations(self):
        comparison = self.compare_sentiment_performance()
        recommendations = []
        
        fear_pnl = comparison.loc['Fear', ('closedPnL', 'mean')] if 'Fear' in comparison.index else 0
        greed_pnl = comparison.loc['Greed', ('closedPnL', 'mean')] if 'Greed' in comparison.index else 0
        
        if fear_pnl < greed_pnl:
            recommendations.append("Trend Following in Greed: Increase position sizes during Greed periods.")
            recommendations.append("Risk Management in Fear: Reduce leverage and tighten stop-losses during Fear periods.")
        else:
            recommendations.append("Contrarian Approach: Look for mean reversion opportunities during Fear periods.")
            recommendations.append("Capital Preservation: Reduce exposure during high volatility Greed periods.")
            
        return recommendations
