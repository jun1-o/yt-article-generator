"""
USD/JPYのサンプルトレードデータを生成
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_sample_trades(num_trades=100, symbol="USDJPY"):
    """
    サンプルトレードデータを生成
    
    Args:
        num_trades: 生成するトレード数
        symbol: 通貨ペア
    """
    np.random.seed(42)
    random.seed(42)
    
    trades = []
    base_time = datetime.now() - timedelta(days=90)
    
    # USD/JPYの価格レンジ（現実的な値）
    base_price = 149.50
    
    for i in range(num_trades):
        # トランザクションタイム
        trade_time = base_time + timedelta(hours=random.randint(1, 2160))
        
        # トレードタイプ（買い=0, 売り=1）
        trade_type = random.choice([0, 1])
        
        # エントリー価格
        entry_price = base_price + np.random.uniform(-5, 5)
        
        # ロット数（0.01-1.0）
        volume = round(random.choice([0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]), 2)
        
        # pips（-50 to 100、勝率約55%になるよう調整）
        if random.random() < 0.55:  # 勝ちトレード
            pips = np.random.uniform(10, 100)
        else:  # 負けトレード
            pips = np.random.uniform(-50, -5)
        
        # 利益計算（1pips = volume * 1000円として簡易計算）
        profit = pips * volume * 1000
        
        # エグジット価格
        if trade_type == 0:  # 買い
            exit_price = entry_price + (pips / 100)
        else:  # 売り
            exit_price = entry_price - (pips / 100)
        
        trade = {
            'ticket': 1000000 + i,
            'time': int(trade_time.timestamp()),
            'time_msc': int(trade_time.timestamp() * 1000),
            'type': trade_type,
            'entry': 0,  # IN
            'magic': 0,
            'position_id': 1000000 + i,
            'reason': 0,
            'volume': volume,
            'price': entry_price,
            'commission': -volume * 300,  # 手数料
            'swap': 0,
            'profit': round(profit, 2),
            'fee': 0,
            'symbol': symbol,
            'comment': f'Trade_{i+1}',
            'external_id': ''
        }
        
        trades.append(trade)
    
    return pd.DataFrame(trades)


def main():
    """メイン関数"""
    print("USD/JPYサンプルトレードデータを生成中...")
    
    # トレードデータ生成
    trades_df = generate_sample_trades(num_trades=100, symbol="USDJPY")
    
    # CSVとして保存
    output_file = "data/trades/usdjpy_sample_trades.csv"
    trades_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✓ サンプルデータを生成しました: {output_file}")
    print(f"  トレード数: {len(trades_df)}件")
    print(f"  総損益: {trades_df['profit'].sum():,.2f}円")
    print(f"  勝率: {len(trades_df[trades_df['profit'] > 0]) / len(trades_df) * 100:.1f}%")
    
    # データのプレビュー
    print("\n【データプレビュー】")
    print(trades_df[['ticket', 'symbol', 'type', 'volume', 'price', 'profit']].head(10))


if __name__ == '__main__':
    main()
