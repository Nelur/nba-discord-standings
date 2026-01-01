"""
NBA順位 Discord自動投稿Bot
ESPN非公式APIを使用して順位を取得し、Discordに投稿する
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

# ESPN API エンドポイント（認証不要）
ESPN_STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"

# ===== 全チームのマスターデータ =====
TEAM_MASTER = {
    # Eastern Conference
    "ATL": {"name": "ホークス", "emoji": "🦅", "conference": "East"},
    "BOS": {"name": "セルツ", "emoji": "☘️", "conference": "East"},
    "BKN": {"name": "ネッツ", "emoji": "🕸️", "conference": "East"},
    "CHA": {"name": "ホーネッツ", "emoji": "🐝", "conference": "East"},
    "CHI": {"name": "ブルズ", "emoji": "🐂", "conference": "East"},
    "CLE": {"name": "キャブス", "emoji": "⚔️", "conference": "East"},
    "DET": {"name": "ピストンズ", "emoji": "🔧", "conference": "East"},
    "IND": {"name": "ペイサーズ", "emoji": "🏎️", "conference": "East"},
    "MIA": {"name": "ヒート", "emoji": "🔥", "conference": "East"},
    "MIL": {"name": "バックス", "emoji": "🦌", "conference": "East"},
    "NYK": {"name": "ニックス", "emoji": "🗽", "conference": "East"},
    "ORL": {"name": "マジック", "emoji": "✨", "conference": "East"},
    "PHI": {"name": "シクサーズ", "emoji": "🔔", "conference": "East"},
    "TOR": {"name": "ラプターズ", "emoji": "🦖", "conference": "East"},
    "WAS": {"name": "ウィザーズ", "emoji": "🧙", "conference": "East"},
    # Western Conference
    "DAL": {"name": "マブス", "emoji": "🐴", "conference": "West"},
    "DEN": {"name": "ナゲッツ", "emoji": "⛏️", "conference": "West"},
    "GS": {"name": "ウォリアーズ", "emoji": "🌉", "conference": "West"},
    "GSW": {"name": "ウォリアーズ", "emoji": "🌉", "conference": "West"},
    "HOU": {"name": "ロケッツ", "emoji": "🚀", "conference": "West"},
    "LAC": {"name": "クリッパーズ", "emoji": "⛵", "conference": "West"},
    "LAL": {"name": "レイカーズ", "emoji": "💜", "conference": "West"},
    "MEM": {"name": "グリズリーズ", "emoji": "🐻", "conference": "West"},
    "MIN": {"name": "ウルブズ", "emoji": "🐺", "conference": "West"},
    "NO": {"name": "ペリカンズ", "emoji": "🦢", "conference": "West"},
    "NOP": {"name": "ペリカンズ", "emoji": "🦢", "conference": "West"},
    "OKC": {"name": "サンダー", "emoji": "⚡", "conference": "West"},
    "PHX": {"name": "サンズ", "emoji": "☀️", "conference": "West"},
    "POR": {"name": "ブレイザーズ", "emoji": "🌲", "conference": "West"},
    "SAC": {"name": "キングス", "emoji": "👑", "conference": "West"},
    "SA": {"name": "スパーズ", "emoji": "🤠", "conference": "West"},
    "SAS": {"name": "スパーズ", "emoji": "🤠", "conference": "West"},
    "UTA": {"name": "ジャズ", "emoji": "🎷", "conference": "West"},
    "UTAH": {"name": "ジャズ", "emoji": "🎷", "conference": "West"},
}

# チーム略称の正規化マップ（ESPN APIの略称 → 標準ID）
TEAM_ABBR_NORMALIZE = {
    "GS": "GSW",
    "NO": "NOP", 
    "NY": "NYK",
    "SA": "SAS",
    "UTAH": "UTA",
    "WSH": "WAS",
    "PHO": "PHX",
    "PHOE": "PHX",
}


def load_config():
    """設定ファイルを読み込む"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_team_abbr(abbr):
    """チーム略称を正規化"""
    upper_abbr = abbr.upper()
    return TEAM_ABBR_NORMALIZE.get(upper_abbr, upper_abbr)


def get_espn_standings():
    """ESPN APIから順位データを取得"""
    print("ESPN APIから順位を取得中...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        response = requests.get(ESPN_STANDINGS_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        print("✅ ESPN APIからデータ取得成功！")
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ ESPN API エラー: {e}")
        raise


def parse_standings(data, target_teams):
    """
    ESPNのデータから指定チームの順位情報を抽出
    
    Returns:
        dict: {"East": [...], "West": [...]}
    """
    results = {"East": [], "West": []}
    
    # 設定ファイルからチームIDのセットを作成
    target_ids = set()
    for team in target_teams:
        team_id = team["id"].upper()
        target_ids.add(team_id)
        # 正規化されたIDも追加
        for orig, norm in TEAM_ABBR_NORMALIZE.items():
            if norm == team_id:
                target_ids.add(orig)
    
    # 設定からチーム情報を取得する辞書を作成
    team_config_map = {}
    for team in target_teams:
        team_id = team["id"].upper()
        team_config_map[team_id] = team
        # 正規化前のIDでもマッピング
        for orig, norm in TEAM_ABBR_NORMALIZE.items():
            if norm == team_id:
                team_config_map[orig] = team
    
    # ESPNのデータ構造を解析
    # children配列にカンファレンスごとのデータが入っている
    if "children" not in data:
        print("❌ 予期しないデータ構造です")
        return results
    
    for conference_data in data["children"]:
        conf_name = conference_data.get("name", "")
        conf_abbr = conference_data.get("abbreviation", "")
        
        # カンファレンスを判定
        if "East" in conf_name or conf_abbr == "East":
            conf_key = "East"
        elif "West" in conf_name or conf_abbr == "West":
            conf_key = "West"
        else:
            continue
        
        # standings配列を取得
        standings = conference_data.get("standings", {}).get("entries", [])
        
        for entry in standings:
            team_info = entry.get("team", {})
            team_abbr = team_info.get("abbreviation", "").upper()
            normalized_abbr = normalize_team_abbr(team_abbr)
            
            # 追跡対象のチームかチェック
            if team_abbr not in target_ids and normalized_abbr not in target_ids:
                continue
            
            # 設定からチーム情報を取得
            config = team_config_map.get(team_abbr) or team_config_map.get(normalized_abbr)
            if not config:
                continue
            
            # 統計情報を取得
            stats = {}
            for stat in entry.get("stats", []):
                stat_name = stat.get("name", "")
                stat_value = stat.get("value", stat.get("displayValue", ""))
                stats[stat_name] = stat_value
            
            # 順位、勝敗を取得
            wins = int(stats.get("wins", 0))
            losses = int(stats.get("losses", 0))
            
            # 直近10試合の成績を取得
            # ESPNでは "record" や特定のstatで取得可能
            last10 = stats.get("Last Ten Games Record", stats.get("streak", ""))
            if not last10:
                # 代替: streakを使用
                streak_val = stats.get("streak", "")
                last10 = streak_val if streak_val else "-"
            
            # playoffSeedから順位を取得
            rank = int(stats.get("playoffSeed", 0))
            if rank == 0:
                # clincher等から順位を推測
                rank = int(stats.get("leagueRanking", 0))
            
            team_data = {
                "id": normalized_abbr,
                "name": config.get("name", TEAM_MASTER.get(normalized_abbr, {}).get("name", team_abbr)),
                "emoji": config.get("emoji", TEAM_MASTER.get(normalized_abbr, {}).get("emoji", "🏀")),
                "rank": rank,
                "wins": wins,
                "losses": losses,
                "last10": last10,
                "conference": conf_key,
            }
            
            results[conf_key].append(team_data)
    
    # 順位でソート
    results["East"].sort(key=lambda x: x["rank"] if x["rank"] > 0 else 999)
    results["West"].sort(key=lambda x: x["rank"] if x["rank"] > 0 else 999)
    
    return results


def format_message(standings_data):
    """Discord投稿用のメッセージを整形"""
    # 日本時間で日付を取得
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y/%m/%d")
    
    lines = [f"🏀 NBA順位 ({today})", ""]
    
    # Eastern Conference
    if standings_data["East"]:
        lines.append("【Eastern】")
        for team in standings_data["East"]:
            rank_str = f"{team['rank']:>2}位"
            record = f"({team['wins']}勝{team['losses']}敗)"
            last10 = f"直近: {team['last10']}" if team['last10'] and team['last10'] != "-" else ""
            line = f"{rank_str} {team['emoji']} {team['name']} {record}"
            if last10:
                line += f" {last10}"
            lines.append(line)
        lines.append("")
    
    # Western Conference
    if standings_data["West"]:
        lines.append("【Western】")
        for team in standings_data["West"]:
            rank_str = f"{team['rank']:>2}位"
            record = f"({team['wins']}勝{team['losses']}敗)"
            last10 = f"直近: {team['last10']}" if team['last10'] and team['last10'] != "-" else ""
            line = f"{rank_str} {team['emoji']} {team['name']} {record}"
            if last10:
                line += f" {last10}"
            lines.append(line)
    
    return "\n".join(lines)


def post_to_discord(message, webhook_url):
    """Discord Webhookにメッセージを投稿"""
    payload = {"content": message}
    
    response = requests.post(webhook_url, json=payload)
    
    if response.status_code == 204:
        print("✅ Discordへの投稿が完了しました")
        return True
    else:
        print(f"❌ Discord投稿エラー: {response.status_code}")
        print(response.text)
        return False


def main():
    """メイン処理"""
    print("=" * 50)
    print("NBA順位 Discord投稿Bot 開始")
    print("=" * 50)
    
    # 1. 設定読み込み
    config = load_config()
    target_teams = config["teams"]
    print(f"追跡チーム数: {len(target_teams)}")
    
    # 2. Webhook URL取得（環境変数から）
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ エラー: DISCORD_WEBHOOK_URL が設定されていません")
        return False
    
    # 3. ESPN APIから順位取得
    data = get_espn_standings()
    
    # 4. 指定チームの順位を抽出
    standings = parse_standings(data, target_teams)
    
    found_teams = len(standings["East"]) + len(standings["West"])
    print(f"取得チーム数: {found_teams}")
    
    if found_teams == 0:
        print("⚠️ 警告: チームが見つかりませんでした")
        # デバッグ用にデータ構造を出力
        print("データ構造を確認中...")
        print(json.dumps(data, indent=2)[:2000])
        return False
    
    # 5. メッセージ整形
    message = format_message(standings)
    print("\n--- 投稿内容 ---")
    print(message)
    print("--- ここまで ---\n")
    
    # 6. Discord投稿
    success = post_to_discord(message, webhook_url)
    
    print("=" * 50)
    print("処理完了")
    print("=" * 50)
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
