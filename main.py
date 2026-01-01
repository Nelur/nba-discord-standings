"""
NBA順位 Discord自動投稿Bot
毎日指定チームの順位をDiscordに投稿する
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta
from nba_api.stats.endpoints import leaguestandingsv3

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
    "GSW": {"name": "ウォリアーズ", "emoji": "🌉", "conference": "West"},
    "HOU": {"name": "ロケッツ", "emoji": "🚀", "conference": "West"},
    "LAC": {"name": "クリッパーズ", "emoji": "⛵", "conference": "West"},
    "LAL": {"name": "レイカーズ", "emoji": "💜", "conference": "West"},
    "MEM": {"name": "グリズリーズ", "emoji": "🐻", "conference": "West"},
    "MIN": {"name": "ウルブズ", "emoji": "🐺", "conference": "West"},
    "NOP": {"name": "ペリカンズ", "emoji": "🦢", "conference": "West"},
    "OKC": {"name": "サンダー", "emoji": "⚡", "conference": "West"},
    "PHX": {"name": "サンズ", "emoji": "☀️", "conference": "West"},
    "POR": {"name": "ブレイザーズ", "emoji": "🌲", "conference": "West"},
    "SAC": {"name": "キングス", "emoji": "👑", "conference": "West"},
    "SAS": {"name": "スパーズ", "emoji": "🤠", "conference": "West"},
    "UTA": {"name": "ジャズ", "emoji": "🎷", "conference": "West"},
}

# チームIDの変換マップ（NBA APIの略称 → 標準ID）
TEAM_ABBR_MAP = {
    "ATL": "ATL", "BOS": "BOS", "BKN": "BKN", "CHA": "CHA", "CHI": "CHI",
    "CLE": "CLE", "DAL": "DAL", "DEN": "DEN", "DET": "DET", "GSW": "GSW",
    "HOU": "HOU", "IND": "IND", "LAC": "LAC", "LAL": "LAL", "MEM": "MEM",
    "MIA": "MIA", "MIL": "MIL", "MIN": "MIN", "NOP": "NOP", "NYK": "NYK",
    "OKC": "OKC", "ORL": "ORL", "PHI": "PHI", "PHX": "PHX", "POR": "POR",
    "SAC": "SAC", "SAS": "SAS", "TOR": "TOR", "UTA": "UTA", "WAS": "WAS",
}


def load_config():
    """設定ファイルを読み込む"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_current_season():
    """現在のNBAシーズンを取得（例: 2024-25）"""
    today = datetime.now()
    # NBAシーズンは10月開始。1-9月は前年開始のシーズン
    if today.month >= 10:
        start_year = today.year
    else:
        start_year = today.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def get_nba_standings():
    """NBA APIから順位データを取得"""
    season = get_current_season()
    print(f"シーズン {season} の順位を取得中...")
    
    try:
        standings = leaguestandingsv3.LeagueStandingsV3(
            league_id="00",
            season=season,
            season_type="Regular Season"
        )
        df = standings.get_data_frames()[0]
        return df
    except Exception as e:
        print(f"NBA API エラー: {e}")
        raise


def extract_team_standings(df, target_teams):
    """
    指定チームの順位情報を抽出
    
    Returns:
        dict: {"East": [...], "West": [...]}
    """
    results = {"East": [], "West": []}
    
    for team_config in target_teams:
        team_id = team_config["id"]
        
        # config.jsonの設定を優先、なければマスターデータを使用
        team_name = team_config.get("name", TEAM_MASTER.get(team_id, {}).get("name", team_id))
        team_emoji = team_config.get("emoji", TEAM_MASTER.get(team_id, {}).get("emoji", "🏀"))
        conference = TEAM_MASTER.get(team_id, {}).get("conference", "East")
        
        # DataFrameから該当チームを検索
        team_row = df[df["TeamSlug"].str.upper() == team_id.lower()]
        
        if team_row.empty:
            # TeamSlugで見つからない場合、TeamCityとTeamNameの組み合わせで検索
            for _, row in df.iterrows():
                slug = f"{row['TeamCity']} {row['TeamName']}"
                if team_id in row.get("TeamAbbreviation", "").upper() or team_id.upper() in slug.upper():
                    team_row = df[df.index == row.name]
                    break
        
        if team_row.empty:
            print(f"警告: チーム {team_id} が見つかりません")
            continue
        
        row = team_row.iloc[0]
        
        team_data = {
            "id": team_id,
            "name": team_name,
            "emoji": team_emoji,
            "rank": int(row["PlayoffRank"]),
            "wins": int(row["WINS"]),
            "losses": int(row["LOSSES"]),
            "last10": row["L10"],
            "conference": conference,
        }
        
        results[conference].append(team_data)
    
    # 順位でソート
    results["East"].sort(key=lambda x: x["rank"])
    results["West"].sort(key=lambda x: x["rank"])
    
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
            last10 = f"直近: {team['last10']}"
            lines.append(f"{rank_str} {team['emoji']} {team['name']} {record} {last10}")
        lines.append("")
    
    # Western Conference
    if standings_data["West"]:
        lines.append("【Western】")
        for team in standings_data["West"]:
            rank_str = f"{team['rank']:>2}位"
            record = f"({team['wins']}勝{team['losses']}敗)"
            last10 = f"直近: {team['last10']}"
            lines.append(f"{rank_str} {team['emoji']} {team['name']} {record} {last10}")
    
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
    
    # 3. NBA順位取得
    df = get_nba_standings()
    print(f"取得チーム数: {len(df)}")
    
    # 4. 指定チームの順位を抽出
    standings = extract_team_standings(df, target_teams)
    
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
