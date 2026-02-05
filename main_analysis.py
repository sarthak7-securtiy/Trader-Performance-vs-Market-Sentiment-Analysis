from src.data_loader import DataLoader
from src.analysis import Analyzer
import pandas as pd
import sys

def main():
    print("Trader Performance Analysis Tool")
    print("================================")
    
    sentiment_path = 'data/sentiment.csv'
    trades_path = 'data/trades.csv'
    
    try:
        loader = DataLoader(sentiment_path, trades_path)
        sentiment_df, trades_df = loader.load_data()
        sentiment_df, trades_df, merged_df = loader.preprocess_data(sentiment_df, trades_df)
        
        print("\n[Data Loaded Successfully]")
        print(f"Sentiment Data: {sentiment_df.shape}")
        print(f"Trades Data: {trades_df.shape}")
        
        analyzer = Analyzer(merged_df)
        
        print("\n--- Market Sentiment Analysis ---")
        comparison = analyzer.compare_sentiment_performance()
        print(comparison)
        
        print("\n--- Trader Segmentation Logic ---")
        segments = analyzer.segment_traders()
        print(segments.head())
        
        print("\n--- Suggested Strategies ---")
        recs = analyzer.get_strategy_recommendations()
        for r in recs:
            print(f"- {r}")
            
    except FileNotFoundError:
        print("\n[Error] Data files not found in 'data/' directory.")
        print("Please ensure 'sentiment.csv' and 'trades.csv' are present.")
    except Exception as e:
        print(f"\n[Error] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
