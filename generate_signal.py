#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MT5 GOLD取引シグナル生成スクリプト
XGBoostを使用してエントリーとエグジットのシグナルを生成します
"""

import os
import sys
import pandas as pd
import xgboost as xgb
from datetime import datetime
import numpy as np


def load_training_data():
    """トレーニングデータをロード"""
    entry_path = "data/trades/latest_entry_training.csv"
    exit_path = "data/trades/latest_exit_training.csv"
    
    if not os.path.exists(entry_path):
        raise FileNotFoundError(f"エントリーデータが見つかりません: {entry_path}")
    if not os.path.exists(exit_path):
        raise FileNotFoundError(f"エグジットデータが見つかりません: {exit_path}")
    
    entry_df = pd.read_csv(entry_path, encoding='utf-8')
    exit_df = pd.read_csv(exit_path, encoding='utf-8')
    
    print(f"[✓] エントリーデータ読み込み完了: {len(entry_df)} 行")
    print(f"[✓] エグジットデータ読み込み完了: {len(exit_df)} 行")
    
    return entry_df, exit_df


def prepare_features(df, is_entry=True):
    """特徴量の準備"""
    target_col = 'entry_signal' if is_entry else 'exit_signal'
    
    feature_cols = [
        'rsi', 'macd', 'signal', 'bb_upper', 'bb_lower', 
        'atr', 'ema_fast', 'ema_slow', 'stoch_k', 'stoch_d'
    ]
    
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    return X, y, feature_cols


def train_entry_model(entry_df):
    """エントリーシグナル予測モデルをトレーニング"""
    print("\n[🤖] エントリーモデルをトレーニング中...")
    
    X, y, feature_cols = prepare_features(entry_df, is_entry=True)
    
    params = {
        'objective': 'binary:logistic',
        'max_depth': 5,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'random_state': 42,
        'eval_metric': 'logloss'
    }
    
    model = xgb.XGBClassifier(**params)
    model.fit(X, y, verbose=False)
    
    accuracy = model.score(X, y)
    print(f"[✓] エントリーモデル精度: {accuracy:.2%}")
    
    return model, feature_cols


def train_exit_model(exit_df):
    """エグジットシグナル予測モデルをトレーニング"""
    print("\n[🤖] エグジットモデルをトレーニング中...")
    
    X, y, feature_cols = prepare_features(exit_df, is_entry=False)
    
    params = {
        'objective': 'binary:logistic',
        'max_depth': 5,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'random_state': 42,
        'eval_metric': 'logloss'
    }
    
    model = xgb.XGBClassifier(**params)
    model.fit(X, y, verbose=False)
    
    accuracy = model.score(X, y)
    print(f"[✓] エグジットモデル精度: {accuracy:.2%}")
    
    return model, feature_cols


def generate_latest_signals(entry_model, exit_model, entry_df, exit_df, feature_cols):
    """最新データからシグナルを生成"""
    print("\n[📊] 最新シグナルを生成中...")
    
    latest_entry = entry_df.iloc[-1:][feature_cols]
    latest_exit = exit_df.iloc[-1:][feature_cols]
    
    entry_prob = entry_model.predict_proba(latest_entry)[0]
    exit_prob = exit_model.predict_proba(latest_exit)[0]
    
    entry_signal = entry_model.predict(latest_entry)[0]
    exit_signal = exit_model.predict(latest_exit)[0]
    
    return {
        'entry_signal': int(entry_signal),
        'entry_probability': float(entry_prob[1]),
        'exit_signal': int(exit_signal),
        'exit_probability': float(exit_prob[1]),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def save_signals(signals, output_path='data/trades/latest_signals.csv'):
    """シグナルをCSVに保存"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df = pd.DataFrame([signals])
    
    if os.path.exists(output_path):
        existing_df = pd.read_csv(output_path, encoding='utf-8')
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n[💾] シグナル保存完了: {output_path}")


def display_signals(signals):
    """シグナルを表示"""
    print("\n" + "="*60)
    print("📈 MT5 GOLD 取引シグナル生成結果")
    print("="*60)
    print(f"⏰ タイムスタンプ: {signals['timestamp']}")
    print(f"\n🔵 エントリーシグナル: {'買い' if signals['entry_signal'] == 1 else '待機'}")
    print(f"   確率: {signals['entry_probability']:.2%}")
    print(f"\n🔴 エグジットシグナル: {'決済' if signals['exit_signal'] == 1 else '保持'}")
    print(f"   確率: {signals['exit_probability']:.2%}")
    print("="*60 + "\n")


def main():
    """メイン処理"""
    try:
        print("\n🚀 MT5 GOLD取引シグナル生成を開始します...\n")
        
        entry_df, exit_df = load_training_data()
        
        entry_model, entry_features = train_entry_model(entry_df)
        exit_model, exit_features = train_exit_model(exit_df)
        
        signals = generate_latest_signals(
            entry_model, exit_model, entry_df, exit_df, entry_features
        )
        
        display_signals(signals)
        
        save_signals(signals)
        
        print("✅ シグナル生成が正常に完了しました！\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
