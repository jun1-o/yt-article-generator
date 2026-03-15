"""
USD/JPYトレード履歴分析スクリプト
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys


class TradeAnalyzer:
    """トレード履歴分析クラス"""
    
    def __init__(self, entry_file=None, exit_file=None):
        """
        初期化
        
        Args:
            entry_file: エントリーデータのCSVファイルパス
            exit_file: エグジットデータのCSVファイルパス
        """
        self.entry_file = entry_file or "data/trades/latest_entry_training.csv"
        self.exit_file = exit_file or "data/trades/latest_exit_training.csv"
        self.entry_data = None
        self.exit_data = None
        self.trades = None
        
    def load_data(self):
        """データを読み込む"""
        try:
            if Path(self.entry_file).exists():
                self.entry_data = pd.read_csv(self.entry_file, encoding='utf-8')
                print(f"✓ エントリーデータ読み込み完了: {len(self.entry_data)}件")
            else:
                print(f"⚠ エントリーデータが見つかりません: {self.entry_file}")
                
            if Path(self.exit_file).exists():
                self.exit_data = pd.read_csv(self.exit_file, encoding='utf-8')
                print(f"✓ エグジットデータ読み込み完了: {len(self.exit_data)}件")
            else:
                print(f"⚠ エグジットデータが見つかりません: {self.exit_file}")
                
        except Exception as e:
            print(f"❌ データ読み込みエラー: {e}")
            return False
            
        return True
    
    def load_mt5_history(self, symbol="USDJPY", days=90):
        """
        MT5から直接トレード履歴を取得
        
        Args:
            symbol: 通貨ペア（デフォルト: USDJPY）
            days: 取得する日数（デフォルト: 90日）
        """
        try:
            import MetaTrader5 as mt5
            
            # MT5に接続
            if not mt5.initialize():
                print(f"❌ MT5初期化失敗: {mt5.last_error()}")
                return False
            
            print(f"✓ MT5接続成功")
            
            # 取引履歴を取得
            from_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            to_date = datetime.now().timestamp()
            
            deals = mt5.history_deals_get(from_date, to_date)
            
            if deals is None or len(deals) == 0:
                print(f"⚠ {symbol}の取引履歴が見つかりません")
                mt5.shutdown()
                return False
            
            # DataFrameに変換
            df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
            
            # USD/JPYのみフィルタリング
            df = df[df['symbol'] == symbol].copy()
            
            if len(df) == 0:
                print(f"⚠ {symbol}の取引が見つかりません")
                mt5.shutdown()
                return False
            
            self.trades = df
            print(f"✓ {symbol}の取引履歴取得完了: {len(df)}件")
            
            mt5.shutdown()
            return True
            
        except ImportError:
            print("⚠ MetaTrader5モジュールがインストールされていません")
            print("  pip install MetaTrader5 でインストールしてください")
            return False
        except Exception as e:
            print(f"❌ MT5データ取得エラー: {e}")
            return False
    
    def calculate_statistics(self):
        """基本統計を計算"""
        if self.trades is None or len(self.trades) == 0:
            print("❌ 分析するデータがありません")
            return None
        
        df = self.trades.copy()
        
        # 利益/損失のある取引のみ
        if 'profit' in df.columns:
            profit_trades = df[df['profit'] != 0].copy()
        else:
            print("⚠ profitカラムが見つかりません")
            return None
        
        if len(profit_trades) == 0:
            print("⚠ 利益/損失データがありません")
            return None
        
        stats = {}
        
        # 基本情報
        stats['総取引回数'] = len(profit_trades)
        stats['勝ちトレード数'] = len(profit_trades[profit_trades['profit'] > 0])
        stats['負けトレード数'] = len(profit_trades[profit_trades['profit'] < 0])
        
        # 勝率
        if stats['総取引回数'] > 0:
            stats['勝率(%)'] = round((stats['勝ちトレード数'] / stats['総取引回数']) * 100, 2)
        else:
            stats['勝率(%)'] = 0
        
        # 損益
        stats['総損益'] = round(profit_trades['profit'].sum(), 2)
        stats['平均損益'] = round(profit_trades['profit'].mean(), 2)
        stats['最大利益'] = round(profit_trades['profit'].max(), 2)
        stats['最大損失'] = round(profit_trades['profit'].min(), 2)
        
        # 勝ちトレードの統計
        winning_trades = profit_trades[profit_trades['profit'] > 0]
        if len(winning_trades) > 0:
            stats['平均利益'] = round(winning_trades['profit'].mean(), 2)
        else:
            stats['平均利益'] = 0
        
        # 負けトレードの統計
        losing_trades = profit_trades[profit_trades['profit'] < 0]
        if len(losing_trades) > 0:
            stats['平均損失'] = round(losing_trades['profit'].mean(), 2)
        else:
            stats['平均損失'] = 0
        
        # プロフィットファクター（PF）
        total_profit = winning_trades['profit'].sum() if len(winning_trades) > 0 else 0
        total_loss = abs(losing_trades['profit'].sum()) if len(losing_trades) > 0 else 0
        
        if total_loss > 0:
            stats['プロフィットファクター'] = round(total_profit / total_loss, 2)
        else:
            stats['プロフィットファクター'] = float('inf') if total_profit > 0 else 0
        
        # 最大ドローダウンの計算
        cumulative = profit_trades['profit'].cumsum()
        running_max = cumulative.cummax()
        drawdown = cumulative - running_max
        stats['最大ドローダウン'] = round(drawdown.min(), 2)
        
        # リスクリワード比
        if stats['平均損失'] != 0:
            stats['リスクリワード比'] = round(stats['平均利益'] / abs(stats['平均損失']), 2)
        else:
            stats['リスクリワード比'] = float('inf') if stats['平均利益'] > 0 else 0
        
        return stats
    
    def generate_report(self, stats, output_file=None):
        """
        分析レポートを生成
        
        Args:
            stats: 統計データ
            output_file: 出力ファイルパス（Noneの場合は標準出力）
        """
        if stats is None:
            return
        
        report = []
        report.append("=" * 60)
        report.append("USD/JPY トレード履歴分析レポート")
        report.append("=" * 60)
        report.append(f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("【基本統計】")
        report.append(f"  総取引回数: {stats['総取引回数']}回")
        report.append(f"  勝ちトレード: {stats['勝ちトレード数']}回")
        report.append(f"  負けトレード: {stats['負けトレード数']}回")
        report.append(f"  勝率: {stats['勝率(%)']}%")
        report.append("")
        
        report.append("【損益】")
        report.append(f"  総損益: {stats['総損益']:,.2f}")
        report.append(f"  平均損益: {stats['平均損益']:,.2f}")
        report.append(f"  最大利益: {stats['最大利益']:,.2f}")
        report.append(f"  最大損失: {stats['最大損失']:,.2f}")
        report.append(f"  平均利益: {stats['平均利益']:,.2f}")
        report.append(f"  平均損失: {stats['平均損失']:,.2f}")
        report.append("")
        
        report.append("【パフォーマンス指標】")
        if stats['プロフィットファクター'] == float('inf'):
            report.append(f"  プロフィットファクター: ∞ (損失なし)")
        else:
            report.append(f"  プロフィットファクター: {stats['プロフィットファクター']}")
        
        if stats['リスクリワード比'] == float('inf'):
            report.append(f"  リスクリワード比: ∞ (損失なし)")
        else:
            report.append(f"  リスクリワード比: {stats['リスクリワード比']}")
        
        report.append(f"  最大ドローダウン: {stats['最大ドローダウン']:,.2f}")
        report.append("")
        
        # 評価
        report.append("【総合評価】")
        if stats['勝率(%)'] >= 50 and stats['プロフィットファクター'] >= 1.5:
            report.append("  ✓ 良好なトレード成績です")
        elif stats['勝率(%)'] >= 40 and stats['プロフィットファクター'] >= 1.2:
            report.append("  △ 改善の余地がありますが、利益は出ています")
        else:
            report.append("  ⚠ トレード戦略の見直しが必要です")
        
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        
        # 出力
        print(report_text)
        
        # ファイルに保存
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"\n✓ レポートを保存しました: {output_file}")
            except Exception as e:
                print(f"\n❌ レポート保存エラー: {e}")
    
    def analyze(self, use_mt5=True, symbol="USDJPY", output_file=None):
        """
        総合分析を実行
        
        Args:
            use_mt5: MT5から直接データを取得するか
            symbol: 通貨ペア
            output_file: レポート出力ファイル
        """
        print("=" * 60)
        print(f"USD/JPY トレード履歴分析を開始します")
        print("=" * 60)
        print()
        
        # データ取得
        if use_mt5:
            print("【ステップ1】MT5からデータを取得中...")
            if not self.load_mt5_history(symbol=symbol):
                print("\n⚠ MT5からのデータ取得に失敗しました")
                print("   CSVファイルからの読み込みを試みます...")
                if not self.load_data():
                    print("\n❌ データの取得に失敗しました")
                    return
        else:
            print("【ステップ1】CSVファイルからデータを読み込み中...")
            if not self.load_data():
                print("\n❌ データの読み込みに失敗しました")
                return
        
        print()
        
        # 統計計算
        print("【ステップ2】統計を計算中...")
        stats = self.calculate_statistics()
        
        if stats is None:
            print("\n❌ 統計の計算に失敗しました")
            return
        
        print("✓ 統計計算完了")
        print()
        
        # レポート生成
        print("【ステップ3】レポートを生成中...")
        self.generate_report(stats, output_file)


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='USD/JPYトレード履歴分析')
    parser.add_argument('--entry', default='data/trades/latest_entry_training.csv',
                        help='エントリーデータCSVファイル')
    parser.add_argument('--exit', default='data/trades/latest_exit_training.csv',
                        help='エグジットデータCSVファイル')
    parser.add_argument('--symbol', default='USDJPY', help='通貨ペア（デフォルト: USDJPY）')
    parser.add_argument('--no-mt5', action='store_true', help='MT5を使用せずCSVから読み込む')
    parser.add_argument('--output', help='レポート出力ファイルパス')
    parser.add_argument('--days', type=int, default=90, help='MT5から取得する日数（デフォルト: 90日）')
    
    args = parser.parse_args()
    
    # 分析実行
    analyzer = TradeAnalyzer(entry_file=args.entry, exit_file=args.exit)
    analyzer.analyze(use_mt5=not args.no_mt5, symbol=args.symbol, output_file=args.output)


if __name__ == '__main__':
    main()
