# ratings/management/commands/populate_games.py

import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from ratings.models import Game, RatingTier, Flag # Keep Flag import if Game model needs it
from django.db import transaction, IntegrityError
from django.utils.translation import gettext_lazy as _

# --- GAME DATA LIST (v2.2 Methodology Applied - Refined Logic & Final URLs) ---
# Severity Codes: N=None, L=Mild, M=Moderate, S=Severe
# rating_tier_id reflects the FINAL calculated tier based on the refined rules in models.py
GAME_DATA = [
    # === 1. Mini Motorways (HAL) ===
    {
        "title": "Mini Motorways",
        "developer": "Dinosaur Polo Club", "publisher": "Dinosaur Polo Club",
        "release_date": datetime.date(2021, 7, 20),
        "rating_tier_id": "HAL", # Music(L), Time(L). Total L=2 -> HAL
        "summary": "A minimalist strategy simulation game about drawing roads.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/1/1b/Mini_Motorways_cover_art.jpg", # User provided URL
        "steam_link": "https://store.steampowered.com/app/1127500/Mini_Motorways/",
        "available_pc": True, "available_switch": True, "available_ios": True,
        "rationale": "Excellent puzzle game focused on logic. Minimal concerns: mutable background music (Mild) and potential time sink (Mild). Meets 'Acceptable' criteria.",
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "N", "nudity_lewdness_severity": "N", "music_instruments_severity": "L", "gambling_severity": "N", "lying_severity": "N",
        "simulate_killing_severity": "N", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "N",
        "time_wasting_severity": "L", "financial_extravagance_severity": "N", "online_communication_severity": "N", "ugc_risks_severity": "N",
        "music_instruments_details": "Minimalist ambient electronic music.", "music_instruments_reason": "Can be muted.",
        "time_wasting_details": "Engaging puzzle loop, but generally played in shorter sessions.",
        # Add empty details/reason for 'N' fields if desired
        "forced_shirk_details": "", "forced_shirk_reason": "", "promote_shirk_details": "", "promote_shirk_reason": "", "insult_islam_details": "", "insult_islam_reason": "",
        "depict_unseen_details": "", "depict_unseen_reason": "", "magic_sorcery_details": "", "magic_sorcery_reason": "", "contradictory_ideologies_details": "", "contradictory_ideologies_reason": "",
        "nudity_lewdness_details": "", "nudity_lewdness_reason": "", "gambling_details": "", "gambling_reason": "", "lying_details": "", "lying_reason": "",
        "simulate_killing_details": "", "simulate_killing_reason": "", "simulate_theft_crime_details": "", "simulate_theft_crime_reason": "", "normalize_haram_rels_details": "", "normalize_haram_rels_reason": "",
        "normalize_substances_details": "", "normalize_substances_reason": "", "profanity_obscenity_details": "", "profanity_obscenity_reason": "", "time_wasting_reason": "",
        "financial_extravagance_details": "", "financial_extravagance_reason": "", "online_communication_details": "Leaderboards only.", "online_communication_reason": "", "ugc_risks_details": "", "ugc_risks_reason": "",
    },
    # === 2. Portal 2 (MSH) ===
    {
        "title": "Portal 2",
        "developer": "Valve", "publisher": "Valve",
        "release_date": datetime.date(2011, 4, 19),
        "rating_tier_id": "MSH", # Online Comm (M) -> MSH
        "summary": "A first-person puzzle-platform video game known for physics-based puzzles and dark humor.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg", # User provided URL
        "steam_link": "https://store.steampowered.com/app/620/Portal_2/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True,
        "rationale": "Core gameplay is permissible puzzle-solving. Rated 'Caution Required' due to Moderate risk in Online Communication (optional co-op chat). Mild concerns for mutable music, minor ideology (dark humor), time, and UGC.",
        "has_spoilers_in_details": True,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "N", "music_instruments_severity": "L", "gambling_severity": "N", "lying_severity": "N",
        "simulate_killing_severity": "N", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "N",
        "time_wasting_severity": "L", "financial_extravagance_severity": "N", "online_communication_severity": "M", "ugc_risks_severity": "L",
        "promote_shirk_details": "Themes of AI consciousness are fictional/sci-fi.",
        "contradictory_ideologies_details": "Some dark humor/sarcasm.",
        "music_instruments_details": "Contains background ambient/electronic music.", "music_instruments_reason": "Optional/mutable.",
        "simulate_killing_details": "No direct combat. Environmental hazards.",
        "time_wasting_details": "Finite puzzle game, community maps extend.",
        "online_communication_details": "Optional Co-op mode with voice/text chat risk.", "online_communication_reason": "Requires management.", # Moderate -> MSH
        "ugc_risks_details": "Community maps generally safe.",
        # Add empty details/reason for 'N' fields
        "forced_shirk_details": "", "forced_shirk_reason": "", "insult_islam_details": "", "insult_islam_reason": "", "depict_unseen_details": "", "depict_unseen_reason": "",
        "magic_sorcery_details": "", "magic_sorcery_reason": "", "contradictory_ideologies_reason": "", "nudity_lewdness_details": "", "nudity_lewdness_reason": "", "gambling_details": "", "gambling_reason": "",
        "lying_details": "", "lying_reason": "", "simulate_killing_reason": "", "simulate_theft_crime_details": "", "simulate_theft_crime_reason": "", "normalize_haram_rels_details": "", "normalize_haram_rels_reason": "",
        "normalize_substances_details": "", "normalize_substances_reason": "", "profanity_obscenity_details": "", "profanity_obscenity_reason": "", "time_wasting_reason": "",
        "financial_extravagance_details": "", "financial_extravagance_reason": "", "ugc_risks_reason": "",
    },
    # === 3. Skyrim (KFR) ===
    {
        "title": "The Elder Scrolls V: Skyrim",
        "developer": "Bethesda Game Studios", "publisher": "Bethesda Softworks",
        "release_date": datetime.date(2011, 11, 11),
        "rating_tier_id": "KFR", # Magic(S) -> KFR
        "summary": "An open-world action role-playing game.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/1/15/The_Elder_Scrolls_V_Skyrim_cover.png", # User provided URL
        "steam_link": "https://store.steampowered.com/app/489830/The_Elder_Scrolls_V_Skyrim_Special_Edition/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True, "available_switch": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Core gameplay involves polytheistic deities (Divines/Daedra) and detailed simulation/glorification of magic (Sihr). Severe risks from mods and time wastage.",
        "has_spoilers_in_details": True,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "M", "insult_islam_severity": "N", "depict_unseen_severity": "M", "magic_sorcery_severity": "S",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "L", "music_instruments_severity": "M", "gambling_severity": "N", "lying_severity": "M",
        "simulate_killing_severity": "M", "simulate_theft_crime_severity": "M", "normalize_haram_rels_severity": "L", "normalize_substances_severity": "M", "profanity_obscenity_severity": "L",
        "time_wasting_severity": "S", "financial_extravagance_severity": "L", "online_communication_severity": "N", "ugc_risks_severity": "S",
        "promote_shirk_details": "Interaction with polytheistic framework (Divines, Daedra).", "depict_unseen_details": "Depictions of souls, ghosts, Daedric realms.", "magic_sorcery_details": "Extensive magic system (spells, summoning, enchanting) core to gameplay.", "magic_sorcery_reason": "Detailed simulation/glorification of Sihr.",
        "contradictory_ideologies_details": "Themes of rebellion, racial tensions.", "nudity_lewdness_details": "Base game minimal; severe risk via mods.", "music_instruments_details": "Orchestral score, bards. Mutable.", "lying_details": "Optional deception.", "simulate_killing_details": "Violence central, optional civilian killing.",
        "simulate_theft_crime_details": "Theft/Assassination optional paths.", "normalize_haram_rels_details": "Marriage options can include impermissible via mods.", "normalize_substances_details": "Consumable alcohol/fictional drugs.", "profanity_obscenity_details": "Occasional mild profanity.",
        "time_wasting_details": "Vast world, endless quests.", "time_wasting_reason": "High potential for Israf.", "financial_extravagance_details": "Base game/DLC purchase. Creation Club paid mods (minor).",
        "ugc_risks_details": "Mods can introduce ANY Haram content.", "ugc_risks_reason": "Extreme risk from UGC.",
    },
    # === 4. GTA V (HRM) ===
    {
        "title": "Grand Theft Auto V",
        "developer": "Rockstar North", "publisher": "Rockstar Games",
        "release_date": datetime.date(2013, 9, 17),
        "rating_tier_id": "HRM", # Multiple 'S' -> HRM
        "summary": "Open-world action game centered on crime, satire, and violence.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png", # User provided URL
        "steam_link": "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True,
        "rationale": "Impermissible (Haram). Core gameplay simulates major sins. Unavoidable explicit content ('Awrah, Fahisha), promotes Haram lifestyles, normalizes vice. Highly problematic online.",
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "S", "nudity_lewdness_severity": "S", "music_instruments_severity": "S", "gambling_severity": "S", "lying_severity": "M",
        "simulate_killing_severity": "S", "simulate_theft_crime_severity": "S", "normalize_haram_rels_severity": "S", "normalize_substances_severity": "S", "profanity_obscenity_severity": "S",
        "time_wasting_severity": "S", "financial_extravagance_severity": "S", "online_communication_severity": "S", "ugc_risks_severity": "M",
        "contradictory_ideologies_details": "Promotes extreme materialism, nihilism, mocks values.", "nudity_lewdness_details": "Required strip club scenes, explicit 'Awrah.", "music_instruments_details": "Pervasive Haram themes/lyrics in soundtrack.", "gambling_details": "Online casino linked to real money.",
        "lying_details": "Deception required in missions.", "simulate_killing_details": "Glorified violence against civilians/police required.", "simulate_theft_crime_details": "Core gameplay is theft, robbery, etc.", "normalize_haram_rels_details": "Normalizes prostitution, adultery.", "normalize_substances_details": "Player use/dealing normalized.", "profanity_obscenity_details": "Constant extreme foul language.",
        "time_wasting_details": "Endless open world and online.", "financial_extravagance_details": "Heavy push for microtransactions.", "online_communication_details": "Extremely toxic online environment.", "ugc_risks_details": "Custom jobs/races risk.",
    },
    # === 5. God of War (KFR) ===
     {
        "title": "God of War (2018)",
        "developer": "Santa Monica Studio", "publisher": "Sony Interactive Entertainment",
        "release_date": datetime.date(2018, 4, 20),
        "rating_tier_id": "KFR", # ForcedShirk(S) -> KFR
        "summary": "Action game following a demigod in Norse mythology.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a3/God_of_War_4_cover.jpg", # User provided URL
        "steam_link": "https://store.steampowered.com/app/1593500/God_of_War/",
        "available_pc": True, "available_ps4": True, "available_ps5": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Game based on pagan mythology (Shirk). Player embodies/interacts with/fights false deities, contradicting Tawhid.",
        "has_spoilers_in_details": True,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "S", "promote_shirk_severity": "S", "insult_islam_severity": "N", "depict_unseen_severity": "S", "magic_sorcery_severity": "S",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "L", "music_instruments_severity": "M", "gambling_severity": "N", "lying_severity": "L",
        "simulate_killing_severity": "S", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "M",
        "time_wasting_severity": "M", "financial_extravagance_severity": "N", "online_communication_severity": "N", "ugc_risks_severity": "N",
        "forced_shirk_details": "Player IS a demigod, core gameplay involves false deities.", "promote_shirk_details": "Norse mythology presented as game's reality.", "depict_unseen_details": "Detailed depictions of mythological realms.", "magic_sorcery_details": "Runic magic, mythical weapons linked to Shirk framework.",
        "nudity_lewdness_details": "Some gore.", "music_instruments_details": "Orchestral score. Mutable.", "lying_details": "Narrative deception.",
        "simulate_killing_details": "Intense, graphic, brutal combat.", "profanity_obscenity_details": "Strong language present.", "time_wasting_details": "Long game with side content.",
    },
    # === 6. Stardew Valley (MSH) ===
    {
        "title": "Stardew Valley",
        "developer": "ConcernedApe", "publisher": "ConcernedApe",
        "release_date": datetime.date(2016, 2, 26),
        "rating_tier_id": "MSH", # NormHaramRels(M), NormSubs(M), Time(M) -> MSH
        "summary": "An open-ended country-life RPG focused on farming and socializing.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a8/Stardew_Valley_cover_art.jpg", # User provided URL
        "steam_link": "https://store.steampowered.com/app/413150/Stardew_Valley/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True, "available_switch": True, "available_android": True, "available_ios": True,
        "rationale": "Caution Required (Mashbouh). Normalization of alcohol (central saloon), optional gambling, option for impermissible relationships. Time sink potential is moderate. Core farming is permissible if problematic aspects are avoided.",
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "L", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "N", "music_instruments_severity": "L", "gambling_severity": "L", "lying_severity": "N",
        "simulate_killing_severity": "L", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "M", "normalize_substances_severity": "M", "profanity_obscenity_severity": "N",
        "time_wasting_severity": "M", "financial_extravagance_severity": "N", "online_communication_severity": "L", "ugc_risks_severity": "L",
        "promote_shirk_details": "Minor fantasy elements (Junimos, Wizard).", "music_instruments_details": "Mutable background music.", "gambling_details": "Optional casino area.",
        "simulate_killing_details": "Stylized combat vs monsters.", "normalize_haram_rels_details": "Same-sex marriage presented as standard option.", "normalize_substances_details": "Saloon is central social hub, normalizing alcohol.",
        "time_wasting_details": "Engaging loop, high potential for excessive play.", "online_communication_details": "Optional co-op usually with friends.", "ugc_risks_details": "Mods exist but less prevalent.",
    },
    # === 7. Elden Ring (KFR) ===
    {
        "title": "Elden Ring",
        "developer": "FromSoftware", "publisher": "Bandai Namco Entertainment",
        "release_date": datetime.date(2022, 2, 25),
        "rating_tier_id": "KFR", # Promote Shirk(S), Magic(S) -> KFR
        "summary": "An action RPG set in the Lands Between, featuring exploration and challenging combat.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg", # User provided URL
        "steam_link": "https://store.steampowered.com/app/1245620/ELDEN_RING/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Deeply embedded polytheistic lore. Extensive use of magic linked to these entities. Contains severe graphic violence.",
        "has_spoilers_in_details": True,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "S", "insult_islam_severity": "N", "depict_unseen_severity": "M", "magic_sorcery_severity": "S",
        "contradictory_ideologies_severity": "M", "nudity_lewdness_severity": "L", "music_instruments_severity": "M", "gambling_severity": "N", "lying_severity": "L",
        "simulate_killing_severity": "S", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "L",
        "time_wasting_severity": "S", "financial_extravagance_severity": "N", "online_communication_severity": "M", "ugc_risks_severity": "L",
        "promote_shirk_details": "Complex lore involving multiple god-like beings. Player interacts with items/powers derived from them.", "promote_shirk_reason": "Pervasive polytheistic framework.",
        "depict_unseen_details": "Depiction of spirits, spectral beings.", "magic_sorcery_details": "Sorceries/Incantations core systems, tied to lore figures/gods.", "magic_sorcery_reason": "Central role, link to Shirk.",
        "contradictory_ideologies_details": "Themes of ambition, despair.", "nudity_lewdness_details": "Some suggestive enemy designs.", "music_instruments_details": "Orchestral score. Mutable.",
        "lying_details": "Ambiguous NPC interactions.", "simulate_killing_details": "Challenging, graphic combat.", "simulate_killing_reason": "High graphic violence.",
        "profanity_obscenity_details": "Occasional mild profanity.", "time_wasting_details": "Vast world, difficult bosses.", "time_wasting_reason": "High Israf potential.",
        "online_communication_details": "Asynchronous messages, summons.", "ugc_risks_details": "Primarily texture/model swaps.",
    },
    # === 8. Genshin Impact (KFR) ===
    {
        "title": "Genshin Impact",
        "developer": "miHoYo", "publisher": "Cognosphere PTE. LTD.",
        "release_date": datetime.date(2020, 9, 28),
        "rating_tier_id": "KFR", # Promote Shirk(S) -> KFR
        "summary": "An open-world action RPG featuring gacha mechanics.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a6/Genshin_Impact_cover_art.png", # User provided URL
        "other_store_link": "https://genshin.hoyoverse.com/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_android": True, "available_ios": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Contains significant polytheistic themes ('Archons' worshipped as gods). Also includes severe gambling (Gacha/Maysir) and financial extravagance risks.",
        "has_spoilers_in_details": True,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "S", "insult_islam_severity": "N", "depict_unseen_severity": "M", "magic_sorcery_severity": "M",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "M", "music_instruments_severity": "M", "gambling_severity": "S", "lying_severity": "L",
        "simulate_killing_severity": "L", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "L", "normalize_substances_severity": "L",
        "profanity_obscenity_severity": "N", "time_wasting_severity": "S", "financial_extravagance_severity": "S", "online_communication_severity": "L", "ugc_risks_severity": "N",
        "promote_shirk_details": "World features 'Archons' worshipped as gods, central to lore/gameplay.", "promote_shirk_reason": "Normalization/central role of polytheism.", # Severe -> KFR
        "depict_unseen_details": "Elemental spirits, otherworldly beings.", "magic_sorcery_details": "Elemental 'Visions' grant magical powers.", "nudity_lewdness_details": "Stylized characters, some revealing outfits.",
        "music_instruments_details": "Extensive orchestral score. Assume mutable.", "gambling_details": "Core 'Wish' system (Gacha) uses premium currency linked to real money.", "gambling_reason": "Clear gambling mechanic.", # Severe
        "lying_details": "Some dialogue choices.", "simulate_killing_details": "Stylized combat.", "normalize_haram_rels_details": "Ambiguous character interactions.", "normalize_substances_details": "Possible alcohol references.",
        "time_wasting_details": "Gacha loop, daily tasks, events.", "time_wasting_reason": "Designed for addiction.", # Severe
        "financial_extravagance_details": "Gacha system strongly incentivizes spending.", "financial_extravagance_reason": "Predatory monetization.", # Severe
        "online_communication_details": "Optional co-op with limited chat.",
    },
    # === 9. EA SPORTS FC 24 (FIFA) (HRM) ===
    {
        "title": "EA SPORTS FC 24",
        "developer": "EA Vancouver & EA Romania", "publisher": "Electronic Arts",
        "release_date": datetime.date(2023, 9, 29),
        "rating_tier_id": "HRM", # Gambling (S), Music(S), Finance(S) -> HRM
        "summary": "A football simulation game featuring Ultimate Team.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/e/e9/FC_24_Cover_Art.jpg", # User provided URL
        "steam_link": "https://store.steampowered.com/app/2195250/EA_SPORTS_FC_24/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True, "available_switch": True,
        "rationale": "Impermissible (Haram) primarily due to Ultimate Team mode's 'packs' (loot boxes) constituting gambling (Maysir) linked to real money. Also contains pervasive music and encourages financial extravagance.",
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "N", "music_instruments_severity": "S", "gambling_severity": "S", # HRM Trigger
        "lying_severity": "N", "simulate_killing_severity": "N", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N",
        "profanity_obscenity_severity": "L", "time_wasting_severity": "M", "financial_extravagance_severity": "S", "online_communication_severity": "M", "ugc_risks_severity": "N",
        "contradictory_ideologies_details": "Potential promotion of excessive competitiveness.", "music_instruments_details": "Extensive licensed soundtrack with questionable lyrics/themes.", "music_instruments_reason": "Pervasive, hard to avoid.", # Severe
        "gambling_details": "Ultimate Team packs (loot boxes) core to mode, linked to real money.", "gambling_reason": "Clear gambling mechanic.", # Severe
        "profanity_obscenity_details": "Online chat/player names risk.", "time_wasting_details": "Ultimate Team requires significant time/money.",
        "financial_extravagance_details": "Ultimate Team strongly incentivizes buying packs.", "financial_extravagance_reason": "Pay-to-win / Gambling loop.", # Severe
        "online_communication_details": "Online matches risk toxic behavior.",
    },
]

# --- Command Class (Keep as is) ---
class Command(BaseCommand):
    help = 'Populates the database with initial game rating data (v2.2 Methodology - Final URLs & Ratings).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating games (v2.2 Methodology)..."))

        tiers_cache = {tier.tier_code: tier for tier in RatingTier.objects.all()}

        created_count = 0; updated_count = 0; skipped_count = 0; errors = 0

        for game_data_item in GAME_DATA:
            game_data = game_data_item.copy()
            title = game_data.get('title')
            if not title: self.stderr.write(self.style.ERROR("Skipping entry with missing title.")); errors += 1; continue

            tier_id = game_data.pop('rating_tier_id', None)
            if not tier_id: self.stderr.write(self.style.WARNING(f"Missing 'rating_tier_id' for game '{title}'. Skipping.")); skipped_count += 1; continue

            rating_tier = tiers_cache.get(tier_id)
            if not rating_tier: self.stderr.write(self.style.WARNING(f"RatingTier with code '{tier_id}' not found for game '{title}'. Skipping.")); skipped_count += 1; continue

            defaults = {
                'rating_tier': rating_tier,
                'developer_slug': slugify(game_data.get('developer', '')),
                'publisher_slug': slugify(game_data.get('publisher', '')),
                'available_pc': game_data.get('available_pc', False), 'available_ps5': game_data.get('available_ps5', False), 'available_ps4': game_data.get('available_ps4', False),
                'available_xbox_series': game_data.get('available_xbox_series', False), 'available_xbox_one': game_data.get('available_xbox_one', False), 'available_switch': game_data.get('available_switch', False),
                'available_android': game_data.get('available_android', False), 'available_ios': game_data.get('available_ios', False), 'available_quest': game_data.get('available_quest', False),
                'has_spoilers_in_details': game_data.get('has_spoilers_in_details', False),
                # Add ALL severity/details/reason fields with defaults
                'forced_shirk_severity': game_data.get('forced_shirk_severity', 'N'), 'forced_shirk_details': game_data.get('forced_shirk_details', ''), 'forced_shirk_reason': game_data.get('forced_shirk_reason', ''),
                'promote_shirk_severity': game_data.get('promote_shirk_severity', 'N'), 'promote_shirk_details': game_data.get('promote_shirk_details', ''), 'promote_shirk_reason': game_data.get('promote_shirk_reason', ''),
                'insult_islam_severity': game_data.get('insult_islam_severity', 'N'), 'insult_islam_details': game_data.get('insult_islam_details', ''), 'insult_islam_reason': game_data.get('insult_islam_reason', ''),
                'depict_unseen_severity': game_data.get('depict_unseen_severity', 'N'), 'depict_unseen_details': game_data.get('depict_unseen_details', ''), 'depict_unseen_reason': game_data.get('depict_unseen_reason', ''),
                'magic_sorcery_severity': game_data.get('magic_sorcery_severity', 'N'), 'magic_sorcery_details': game_data.get('magic_sorcery_details', ''), 'magic_sorcery_reason': game_data.get('magic_sorcery_reason', ''),
                'contradictory_ideologies_severity': game_data.get('contradictory_ideologies_severity', 'N'), 'contradictory_ideologies_details': game_data.get('contradictory_ideologies_details', ''), 'contradictory_ideologies_reason': game_data.get('contradictory_ideologies_reason', ''),
                'nudity_lewdness_severity': game_data.get('nudity_lewdness_severity', 'N'), 'nudity_lewdness_details': game_data.get('nudity_lewdness_details', ''), 'nudity_lewdness_reason': game_data.get('nudity_lewdness_reason', ''),
                'music_instruments_severity': game_data.get('music_instruments_severity', 'N'), 'music_instruments_details': game_data.get('music_instruments_details', ''), 'music_instruments_reason': game_data.get('music_instruments_reason', ''),
                'gambling_severity': game_data.get('gambling_severity', 'N'), 'gambling_details': game_data.get('gambling_details', ''), 'gambling_reason': game_data.get('gambling_reason', ''),
                'lying_severity': game_data.get('lying_severity', 'N'), 'lying_details': game_data.get('lying_details', ''), 'lying_reason': game_data.get('lying_reason', ''),
                'simulate_killing_severity': game_data.get('simulate_killing_severity', 'N'), 'simulate_killing_details': game_data.get('simulate_killing_details', ''), 'simulate_killing_reason': game_data.get('simulate_killing_reason', ''),
                'simulate_theft_crime_severity': game_data.get('simulate_theft_crime_severity', 'N'), 'simulate_theft_crime_details': game_data.get('simulate_theft_crime_details', ''), 'simulate_theft_crime_reason': game_data.get('simulate_theft_crime_reason', ''),
                'normalize_haram_rels_severity': game_data.get('normalize_haram_rels_severity', 'N'), 'normalize_haram_rels_details': game_data.get('normalize_haram_rels_details', ''), 'normalize_haram_rels_reason': game_data.get('normalize_haram_rels_reason', ''),
                'normalize_substances_severity': game_data.get('normalize_substances_severity', 'N'), 'normalize_substances_details': game_data.get('normalize_substances_details', ''), 'normalize_substances_reason': game_data.get('normalize_substances_reason', ''),
                'profanity_obscenity_severity': game_data.get('profanity_obscenity_severity', 'N'), 'profanity_obscenity_details': game_data.get('profanity_obscenity_details', ''), 'profanity_obscenity_reason': game_data.get('profanity_obscenity_reason', ''),
                'time_wasting_severity': game_data.get('time_wasting_severity', 'N'), 'time_wasting_details': game_data.get('time_wasting_details', ''), 'time_wasting_reason': game_data.get('time_wasting_reason', ''),
                'financial_extravagance_severity': game_data.get('financial_extravagance_severity', 'N'), 'financial_extravagance_details': game_data.get('financial_extravagance_details', ''), 'financial_extravagance_reason': game_data.get('financial_extravagance_reason', ''),
                'online_communication_severity': game_data.get('online_communication_severity', 'N'), 'online_communication_details': game_data.get('online_communication_details', ''), 'online_communication_reason': game_data.get('online_communication_reason', ''),
                'ugc_risks_severity': game_data.get('ugc_risks_severity', 'N'), 'ugc_risks_details': game_data.get('ugc_risks_details', ''), 'ugc_risks_reason': game_data.get('ugc_risks_reason', ''),
            }

            excluded_keys = {'title', 'rating_tier_id'}
            for key, value in game_data.items():
                 if key not in excluded_keys: defaults[key] = value

            try:
                game, created = Game.objects.update_or_create( title=title, defaults=defaults )
                game.save() # Trigger calculation and flag update
                game.refresh_from_db() # Get the final state

                if created:
                    self.stdout.write(self.style.SUCCESS(f"  CREATED: {game.title} -> Final Rating: {game.rating_tier.tier_code}"))
                    created_count += 1
                else:
                    self.stdout.write(f"  Checked/Updated: {game.title} -> Final Rating: {game.rating_tier.tier_code}")
                    updated_count += 1

            except IntegrityError as e: self.stderr.write(self.style.ERROR(f"Integrity error processing '{title}': {e}.")); errors += 1
            except Exception as e: self.stderr.write(self.style.ERROR(f"General error processing '{title}': {e}")); errors += 1

        total_processed = created_count + updated_count + errors + skipped_count
        if errors > 0 or skipped_count > 0:
             self.stdout.write(self.style.WARNING(f"Finished game population with {errors} errors and {skipped_count} skipped entries."))
        else:
            self.stdout.write(self.style.SUCCESS("Finished game population successfully."))
        self.stdout.write(f"Summary: Created={created_count}, Updated/Existing={updated_count}, Skipped={skipped_count}, Errors={errors}, Total Attempted={len(GAME_DATA)}")