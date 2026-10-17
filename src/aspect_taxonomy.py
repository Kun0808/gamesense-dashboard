"""
aspect_taxonomy.py: aspect taxonomy of the GameSense project (version 5).

Single source of truth for the 12 aspects used by every notebook; notebooks import this file and never redefine the dictionary.

Each aspect has:
    label        display name. It is also the second segment of the Task 3 input ([CLS] sentence [SEP] label),
                 so changing a label changes what the trained models see.
    description  the definition shown to annotators and in the annotation tools.
    keywords     lowercase substrings used for lexicon pre-labelling and for the keyword baseline.

Seven aspects apply to every game (performance_stability, monetization_value, advertisement,
level_difficulty_balance, content_progression, paywall, account_support); five are genre-specific
(gacha_rates, character_operator_balance, matchmaking, cheating, grind_progression). Which aspects apply to which game
is defined in the notebooks (applicability mapping) and in the dashboard.

Change log: v4 -> v5 restored the description field of every aspect. It had been lost when a batch script
redefined ASPECT_TAXONOMY.
"""

ASPECT_TAXONOMY = {
    'performance_stability': {
        'label': 'Performance & Stability',
        'description': 'Crashes, freezes, lag, loading issues, bugs, glitches, battery/data drain.',
        'keywords': [
            'crash',
            'freeze',
            'froze',
            'lag',
            'glitch',
            'bug',
            'buggy',
            "won't load",
            'wont load',
            'force close',
            'not responding',
            'fps',
            'frame rate',
            'framerate',
            'low fps',
            'frame drop',
        ],
    },
    'monetization_value': {
        'label': 'Monetization & Value',
        'description': 'General spending, price fairness, in-app purchase value, currency economy, greed perception.',
        'keywords': [
            'expensive',
            'money',
            'spend',
            'spent',
            'cash',
            'purchase',
            'coins',
            'gems',
            'overpriced',
            'price',
            'rip off',
            'cash grab',
            'f2p',
            'free to play',
            'p2w',
            'whale',
            'whales',
        ],
    },
    'advertisement': {
        'label': 'Advertisements',
        'description': 'In-app ads: frequency, forced/unskippable ads, misleading ad content vs actual gameplay.',
        'keywords': [
            'ad ',
            ' ads',
            'advert',
            'advertisement',
            'misleading ad',
            'false advertising',
        ],
    },
    'level_difficulty_balance': {
        'label': 'Level Difficulty & Gameplay Balance',
        'description': 'Level difficulty spikes, balance between skill and pay-to-win, attempt limits, item scarcity at higher levels.',
        'keywords': [
            'difficult',
            'difficulty',
            'too hard',
            'impossible level',
            'stuck on level',
            'pay to win',
            'unfair',
            'rigged',
        ],
    },
    'content_progression': {
        'label': 'Content & Progression',
        'description': "Story/king's journey content, level variety, new content cadence, sense of progress.",
        'keywords': [
            'story',
            'repetitive',
            'boring after',
            'new content',
            'progression',
            'same levels',
            'no new levels',
            'skip button',
            'skip cutscene',
            "can't skip",
            'cant skip',
            'no skip',
            'new update',
            'latest update',
            'update broke',
        ],
    },
    'paywall': {
        'label': 'Paywall (genre-specific)',
        'description': 'Hard paywalls that block progress unless the player pays or waits (lives, boosters gated behind payment).',
        'keywords': [
            'paywall',
            'pay wall',
            'locked unless',
            'blocked until you pay',
            'need to buy to continue',
        ],
    },
    'gacha_rates': {
        'label': 'Gacha Rates (genre-specific: gacha)',
        'description': 'Complaints or comments about gacha pull rates, pity systems, drop rates, or banner odds for characters/items.',
        'keywords': [
            'gacha',
            'pity',
            'drop rate',
            'pull rate',
            'wish',
            'banner rate',
            'rigged pulls',
            '50/50',
            'guaranteed',
        ],
    },
    'character_operator_balance': {
        'label': 'Character/Operator Balance (genre-specific)',
        'description': 'Comments about specific characters or operators being overpowered, underpowered, needing a buff or nerf, or meta balance.',
        'keywords': [
            'op character',
            'overpowered',
            'underpowered',
            'nerf',
            'buff',
            'character balance',
            'operator balance',
            'meta',
        ],
    },
    'matchmaking': {
        'label': 'Matchmaking & Community (genre-specific: PvP)',
        'description': 'Complaints about unfair matchmaking, toxic teammates, ranking system, or PvP match quality.',
        'keywords': [
            'matchmaking',
            'match making',
            'unfair matches',
            'toxic',
            'toxicity',
            'teammates',
            'smurf',
            'rank system',
            'elo',
        ],
    },
    'cheating': {
        'label': 'Cheating & Fair Play (genre-specific: PvP/battle royale)',
        'description': 'Reports of cheaters, hackers, aimbot, wallhacks, or complaints about anti-cheat and reporting systems.',
        'keywords': [
            'cheater',
            'cheating',
            'hacker',
            'hacking',
            'aimbot',
            'wallhack',
            'esp',
            'report system',
        ],
    },
    'grind_progression': {
        'label': 'Grind & Progression Pace (genre-specific: strategy/gacha)',
        'description': 'Complaints about excessive grinding, farming, slow stamina/energy regeneration, or progression feeling too slow.',
        'keywords': [
            'grind',
            'grindy',
            'farming',
            'too slow to progress',
            'stamina',
            'energy system',
        ],
    },
    'account_support': {
        'label': 'Account, Login & Customer Support',
        'description': 'Account access, login issues, bans, and customer/developer support responsiveness.',
        'keywords': [
            'account banned',
            'account suspended',
            "can't login",
            'cant login',
            'login issue',
            'lost my account',
            'customer support',
            'customer service',
            'no response from support',
            'support team',
        ],
    },
}

ASPECT_IDS = list(ASPECT_TAXONOMY.keys())
SENTIMENT_LABELS = ["negative", "neutral", "positive"]
