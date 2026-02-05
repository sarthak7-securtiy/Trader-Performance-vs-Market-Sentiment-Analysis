import pandas as pd
import numpy as np

class DataLoader:
    def __init__(self, sentiment_path, trades_path):
        self.sentiment_path = sentiment_path
        self.trades_path = trades_path

    def load_data(self):
        try:
            sentiment_df = pd.read_csv(self.sentiment_path)
            trades_df = pd.read_csv(self.trades_path)
            
            return sentiment_df, trades_df
        except Exception as e:
            raise e

    def preprocess_data(self, sentiment_df, trades_df):
        # Normalize column names (strip whitespace, lowercase)
        sentiment_df.columns = sentiment_df.columns.str.strip()
        trades_df.columns = trades_df.columns.str.strip()
        
        # Find Date column in sentiment_df case-insensitively
        date_col = next((col for col in sentiment_df.columns if col.lower() == 'date'), None)
        if date_col:
            sentiment_df.rename(columns={date_col: 'Date'}, inplace=True)
            
        # Ensure Classification column exists (case-insensitive)
        class_col = next((col for col in sentiment_df.columns if col.lower() == 'classification'), None)
        if class_col:
            sentiment_df.rename(columns={class_col: 'Classification'}, inplace=True)
        else:
            print(f"Warning: 'Classification' column not found in sentiment data. Found: {list(sentiment_df.columns)}")

        sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date'], errors='coerce')
        
        if 'time' in trades_df.columns:
            trades_df['time'] = pd.to_datetime(trades_df['time'], unit='ms') if trades_df['time'].dtype == 'int64' else pd.to_datetime(trades_df['time'], errors='coerce')
            trades_df['date'] = trades_df['time'].dt.normalize()
        elif 'timestamp' in trades_df.columns:
            trades_df['date'] = pd.to_datetime(trades_df['timestamp']).dt.normalize()
        
        # Find Time column in trades_df case-insensitively
        time_col = next((col for col in trades_df.columns if col.lower() in ['time', 'timestamp', 'date', 'created_time']), None)
        
        if time_col:
            # Try converting assuming valid timestamp or string
            # Check if likely numeric (Unix timestamp in ms usually for crypto)
            if pd.api.types.is_numeric_dtype(trades_df[time_col]):
                # Assume ms if large numbers
                if trades_df[time_col].mean() > 1e10: # Rough check for ms
                    trades_df['date'] = pd.to_datetime(trades_df[time_col], unit='ms').dt.normalize()
                else: 
                    # Assume seconds
                    trades_df['date'] = pd.to_datetime(trades_df[time_col], unit='s').dt.normalize()
            else:
                trades_df['date'] = pd.to_datetime(trades_df[time_col], errors='coerce').dt.normalize()
        else:
            raise KeyError(f"Could not find a time/date column in trades data. Found: {list(trades_df.columns)}")
        
        # Standardize critical columns for analysis
        column_mapping = {
            'account': ['account', 'user', 'address', 'wallet', 'trader'],
            'symbol': ['symbol', 'pair', 'ticker', 'coin'],
            'closedPnL': ['closedpnl', 'pnl', 'profit', 'realized_pnl', 'closed_pnl', 'realizedpnl', 'closed pnl', 'realized pnl'],
            'leverage': ['leverage', 'lev'],
            'size': ['size', 'amount', 'quantity', 'position_size', 'size tokens', 'size usd'],
        }
        
        for standard, alternatives in column_mapping.items():
            if standard not in trades_df.columns:
                # Find matching column case-insensitively
                match = next((col for col in trades_df.columns if col.lower() == standard.lower() or col.lower() in alternatives), None)
                if match:
                    trades_df.rename(columns={match: standard}, inplace=True)
        
        # Fallback for closedPnL if truly missing (to avoid hard crash)
        if 'closedPnL' not in trades_df.columns:
            print("Warning: 'closedPnL' column not found. Creating placeholder with 0s.")
            trades_df['closedPnL'] = 0.0

        merged_df = pd.merge(trades_df, sentiment_df, left_on='date', right_on='Date', how='left')
        
        return sentiment_df, trades_df, merged_df

    def get_quality_report(self, df, name="Dataset"):
        report = {
            "name": name,
            "rows": df.shape[0],
            "columns": df.shape[1],
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": df.duplicated().sum()
        }
        return report
