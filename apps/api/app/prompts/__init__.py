"""シナリオプロンプト管理モジュール

このモジュールは、各シナリオのシステムプロンプトを管理し、
category と difficulty の組み合わせでプロンプトを取得できる機能を提供します。
"""

from typing import Dict, Optional
from .airport_checkin import AIRPORT_CHECKIN_PROMPT
from .business_meeting import BUSINESS_MEETING_PROMPT
from .restaurant_ordering import RESTAURANT_ORDERING_PROMPT
from .online_negotiation import ONLINE_NEGOTIATION_PROMPT
from .hotel_checkin import HOTEL_CHECKIN_PROMPT
from .best_vacation import BEST_VACATION_PROMPT
from .guide_japan import GUIDE_JAPAN_PROMPT
from .immigration_customs import IMMIGRATION_CUSTOMS_PROMPT
from .travel_planning_friend import TRAVEL_PLANNING_FRIEND_PROMPT
from .lost_wallet_police import LOST_WALLET_POLICE_PROMPT
from .customer_service import CUSTOMER_SERVICE_PROMPT
from .cafe_small_talk import CAFE_SMALL_TALK_PROMPT
from .show_tickets import SHOW_TICKETS_PROMPT
from .park_small_talk import PARK_SMALL_TALK_PROMPT
from .reschedule_meeting import RESCHEDULE_MEETING_PROMPT
from .schedule_meeting import SCHEDULE_MEETING_PROMPT
from .run_meeting import RUN_MEETING_PROMPT
from .contract_negotiation_detail import CONTRACT_NEGOTIATION_PROMPT
from .customer_survey_presentation import CUSTOMER_SURVEY_PRESENTATION_PROMPT
from .apologize_delay import APOLOGIZE_DELAY_PROMPT
from .sick_leave import SICK_LEAVE_PROMPT

# シナリオIDとプロンプトのマッピング
SCENARIO_PROMPTS: Dict[int, str] = {
    1: AIRPORT_CHECKIN_PROMPT,      # 空港チェックイン
    2: BUSINESS_MEETING_PROMPT,     # ビジネスミーティング
    3: RESTAURANT_ORDERING_PROMPT,  # レストランでの注文
    4: ONLINE_NEGOTIATION_PROMPT,   # オンライン商談
    5: HOTEL_CHECKIN_PROMPT,        # ホテルチェックイン
    # Issue #27 追加シナリオ（ID 6-21）
    6: BEST_VACATION_PROMPT,                    # 最高のバケーション
    7: GUIDE_JAPAN_PROMPT,                      # 日本を案内する
    8: IMMIGRATION_CUSTOMS_PROMPT,              # 入国審査・税関で
    9: TRAVEL_PLANNING_FRIEND_PROMPT,           # 旅行計画を友達と相談
    10: LOST_WALLET_POLICE_PROMPT,              # 財布を無くして警察に相談
    11: CUSTOMER_SERVICE_PROMPT,                # カスタマーサービスに相談
    12: CAFE_SMALL_TALK_PROMPT,                 # おしゃれカフェで店員と雑談
    13: SHOW_TICKETS_PROMPT,                    # ショーチケットを入手
    14: PARK_SMALL_TALK_PROMPT,                 # 公園で雑談
    15: RESCHEDULE_MEETING_PROMPT,              # ミーティングをリスケする
    16: SCHEDULE_MEETING_PROMPT,                # ミーティングを立てる
    17: RUN_MEETING_PROMPT,                     # 会議を進行する
    18: CONTRACT_NEGOTIATION_PROMPT,            # 契約条件の交渉
    19: CUSTOMER_SURVEY_PRESENTATION_PROMPT,    # 顧客満足度の調査結果をプレゼン
    20: APOLOGIZE_DELAY_PROMPT,                 # プロジェクトの遅延を謝罪する
    21: SICK_LEAVE_PROMPT,                      # 体調不良で休む
}

# カテゴリと難易度の組み合わせでプロンプトを取得する辞書
# キー: (category, difficulty) のタプル
# 値: プロンプト文字列
CATEGORY_DIFFICULTY_PROMPTS: Dict[tuple[str, str], str] = {
    # Travel カテゴリ
    ('travel', 'beginner'): AIRPORT_CHECKIN_PROMPT,
    ('travel', 'intermediate'): HOTEL_CHECKIN_PROMPT,
    
    # Business カテゴリ
    ('business', 'intermediate'): BUSINESS_MEETING_PROMPT,
    ('business', 'advanced'): ONLINE_NEGOTIATION_PROMPT,
    
    # Daily カテゴリ
    ('daily', 'beginner'): RESTAURANT_ORDERING_PROMPT,
}

# カテゴリ別のプロンプト辞書
CATEGORY_PROMPTS: Dict[str, Dict[str, str]] = {
    'travel': {
        'beginner': AIRPORT_CHECKIN_PROMPT,
        'intermediate': HOTEL_CHECKIN_PROMPT,
    },
    'business': {
        'intermediate': BUSINESS_MEETING_PROMPT,
        'advanced': ONLINE_NEGOTIATION_PROMPT,
    },
    'daily': {
        'beginner': RESTAURANT_ORDERING_PROMPT,
    },
}

# 難易度別のプロンプト辞書
DIFFICULTY_PROMPTS: Dict[str, Dict[str, str]] = {
    'beginner': {
        'travel': AIRPORT_CHECKIN_PROMPT,
        'daily': RESTAURANT_ORDERING_PROMPT,
    },
    'intermediate': {
        'travel': HOTEL_CHECKIN_PROMPT,
        'business': BUSINESS_MEETING_PROMPT,
    },
    'advanced': {
        'business': ONLINE_NEGOTIATION_PROMPT,
    },
}


def get_prompt_by_scenario_id(scenario_id: int) -> Optional[str]:
    """シナリオIDでプロンプトを取得する
    
    Args:
        scenario_id: シナリオID (1-5)
        
    Returns:
        プロンプト文字列、見つからない場合はNone
    """
    return SCENARIO_PROMPTS.get(scenario_id)


def get_prompt_by_category_difficulty(category: str, difficulty: str) -> Optional[str]:
    """カテゴリと難易度の組み合わせでプロンプトを取得する
    
    Args:
        category: カテゴリ ('travel', 'business', 'daily')
        difficulty: 難易度 ('beginner', 'intermediate', 'advanced')
        
    Returns:
        プロンプト文字列、見つからない場合はNone
    """
    return CATEGORY_DIFFICULTY_PROMPTS.get((category, difficulty))


def get_prompts_by_category(category: str) -> Dict[str, str]:
    """カテゴリでプロンプト一覧を取得する
    
    Args:
        category: カテゴリ ('travel', 'business', 'daily')
        
    Returns:
        難易度をキーとしたプロンプト辞書
    """
    return CATEGORY_PROMPTS.get(category, {})


def get_prompts_by_difficulty(difficulty: str) -> Dict[str, str]:
    """難易度でプロンプト一覧を取得する
    
    Args:
        difficulty: 難易度 ('beginner', 'intermediate', 'advanced')
        
    Returns:
        カテゴリをキーとしたプロンプト辞書
    """
    return DIFFICULTY_PROMPTS.get(difficulty, {})


def get_all_prompts() -> Dict[int, str]:
    """全てのシナリオプロンプトを取得する
    
    Returns:
        シナリオIDをキーとしたプロンプト辞書
    """
    return SCENARIO_PROMPTS.copy()


def get_available_combinations() -> list[tuple[str, str]]:
    """利用可能なカテゴリと難易度の組み合わせを取得する
    
    Returns:
        (category, difficulty) のタプルのリスト
    """
    return list(CATEGORY_DIFFICULTY_PROMPTS.keys())


# エクスポートする関数と変数
__all__ = [
    'SCENARIO_PROMPTS',
    'CATEGORY_DIFFICULTY_PROMPTS',
    'CATEGORY_PROMPTS',
    'DIFFICULTY_PROMPTS',
    'get_prompt_by_scenario_id',
    'get_prompt_by_category_difficulty',
    'get_prompts_by_category',
    'get_prompts_by_difficulty',
    'get_all_prompts',
    'get_available_combinations',
]
