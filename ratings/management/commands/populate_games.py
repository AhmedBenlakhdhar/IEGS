# ratings/management/commands/populate_games.py
import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from ratings.models import Game, RatingTier, Flag
from django.db import transaction, IntegrityError
from django.utils.translation import gettext_lazy as _

# --- GAME DATA LIST (v2.3 - Removed Details/Reason/Spoiler fields) ---
GAME_DATA = [
    # === 1. Mini Motorways (HAL) ===
    {
        "title": "Mini Motorways", "developer": "Dinosaur Polo Club", "publisher": "Dinosaur Polo Club",
        "release_date": datetime.date(2021, 7, 20), "rating_tier_id": "HAL",
        "summary": "A minimalist strategy simulation game about drawing roads.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/1/1b/Mini_Motorways_cover_art.jpg",
        "steam_link": "https://store.steampowered.com/app/1127500/Mini_Motorways/",
        "available_pc": True, "available_switch": True, "available_ios": True,
        "rationale": "Excellent puzzle game focused on logic. Minimal concerns: mutable background music (Mild) and potential time sink (Mild). Meets 'Acceptable' criteria.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "N", "nudity_lewdness_severity": "N", "music_instruments_severity": "L", "gambling_severity": "N", "lying_severity": "N",
        "simulate_killing_severity": "N", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "N",
        "time_wasting_severity": "L", "financial_extravagance_severity": "N", "online_communication_severity": "N", "ugc_risks_severity": "N",
    },
    # === 2. Portal 2 (MSH) ===
    {
        "title": "Portal 2", "developer": "Valve", "publisher": "Valve",
        "release_date": datetime.date(2011, 4, 19), "rating_tier_id": "MSH",
        "summary": "A first-person puzzle-platform video game known for physics-based puzzles and dark humor.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg",
        "steam_link": "https://store.steampowered.com/app/620/Portal_2/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True,
        "rationale": "Core gameplay is permissible puzzle-solving. Rated 'Doubtful' due to Moderate risk in Online Communication (optional co-op chat). Mild concerns for mutable music, minor ideology (dark humor), time, and UGC.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "N", "music_instruments_severity": "L", "gambling_severity": "N", "lying_severity": "N",
        "simulate_killing_severity": "N", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "N",
        "time_wasting_severity": "L", "financial_extravagance_severity": "N", "online_communication_severity": "M", "ugc_risks_severity": "L",
    },
    # === 3. Skyrim (KFR) ===
    {
        "title": "The Elder Scrolls V: Skyrim", "developer": "Bethesda Game Studios", "publisher": "Bethesda Softworks",
        "release_date": datetime.date(2011, 11, 11), "rating_tier_id": "KFR",
        "summary": "An open-world action role-playing game.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/1/15/The_Elder_Scrolls_V_Skyrim_cover.png",
        "steam_link": "https://store.steampowered.com/app/489830/The_Elder_Scrolls_V_Skyrim_Special_Edition/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True, "available_switch": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Core gameplay involves polytheistic deities (Divines/Daedra) and detailed simulation/glorification of magic (Sihr). Severe risks from mods and time wastage.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "M", "insult_islam_severity": "N", "depict_unseen_severity": "M", "magic_sorcery_severity": "S",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "L", "music_instruments_severity": "M", "gambling_severity": "N", "lying_severity": "M",
        "simulate_killing_severity": "M", "simulate_theft_crime_severity": "M", "normalize_haram_rels_severity": "L", "normalize_substances_severity": "M", "profanity_obscenity_severity": "L",
        "time_wasting_severity": "S", "financial_extravagance_severity": "L", "online_communication_severity": "N", "ugc_risks_severity": "S",
    },
    # === 4. GTA V (HRM) ===
    {
        "title": "Grand Theft Auto V", "developer": "Rockstar North", "publisher": "Rockstar Games",
        "release_date": datetime.date(2013, 9, 17), "rating_tier_id": "HRM",
        "summary": "Open-world action game centered on crime, satire, and violence.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png",
        "steam_link": "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True,
        "rationale": "Impermissible (Haram). Core gameplay simulates major sins. Unavoidable explicit content ('Awrah, Fahisha), promotes Haram lifestyles, normalizes vice. Highly problematic online.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "S", "nudity_lewdness_severity": "S", "music_instruments_severity": "S", "gambling_severity": "S", "lying_severity": "M",
        "simulate_killing_severity": "S", "simulate_theft_crime_severity": "S", "normalize_haram_rels_severity": "S", "normalize_substances_severity": "S", "profanity_obscenity_severity": "S",
        "time_wasting_severity": "S", "financial_extravagance_severity": "S", "online_communication_severity": "S", "ugc_risks_severity": "M",
    },
    # === 5. God of War (KFR) ===
     {
        "title": "God of War (2018)", "developer": "Santa Monica Studio", "publisher": "Sony Interactive Entertainment",
        "release_date": datetime.date(2018, 4, 20), "rating_tier_id": "KFR",
        "summary": "Action game following a demigod in Norse mythology.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a3/God_of_War_4_cover.jpg",
        "steam_link": "https://store.steampowered.com/app/1593500/God_of_War/",
        "available_pc": True, "available_ps4": True, "available_ps5": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Game based on pagan mythology (Shirk). Player embodies/interacts with/fights false deities, contradicting Tawhid.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "S", "promote_shirk_severity": "S", "insult_islam_severity": "N", "depict_unseen_severity": "S", "magic_sorcery_severity": "S",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "L", "music_instruments_severity": "M", "gambling_severity": "N", "lying_severity": "L",
        "simulate_killing_severity": "S", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "M",
        "time_wasting_severity": "M", "financial_extravagance_severity": "N", "online_communication_severity": "N", "ugc_risks_severity": "N",
    },
    # === 6. Stardew Valley (MSH) ===
    {
        "title": "Stardew Valley", "developer": "ConcernedApe", "publisher": "ConcernedApe",
        "release_date": datetime.date(2016, 2, 26), "rating_tier_id": "MSH",
        "summary": "An open-ended country-life RPG focused on farming and socializing.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a8/Stardew_Valley_cover_art.jpg",
        "steam_link": "https://store.steampowered.com/app/413150/Stardew_Valley/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True, "available_switch": True, "available_android": True, "available_ios": True,
        "rationale": "Doubtful (Mashbouh). Normalization of alcohol (central saloon), optional gambling, option for impermissible relationships. Time sink potential is moderate. Core farming is permissible if problematic aspects are avoided.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "L", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "N", "music_instruments_severity": "L", "gambling_severity": "L", "lying_severity": "N",
        "simulate_killing_severity": "L", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "M", "normalize_substances_severity": "M", "profanity_obscenity_severity": "N",
        "time_wasting_severity": "M", "financial_extravagance_severity": "N", "online_communication_severity": "L", "ugc_risks_severity": "L",
    },
    # === 7. Elden Ring (KFR) ===
    {
        "title": "Elden Ring", "developer": "FromSoftware", "publisher": "Bandai Namco Entertainment",
        "release_date": datetime.date(2022, 2, 25), "rating_tier_id": "KFR",
        "summary": "An action RPG set in the Lands Between, featuring exploration and challenging combat.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
        "steam_link": "https://store.steampowered.com/app/1245620/ELDEN_RING/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Deeply embedded polytheistic lore. Extensive use of magic linked to these entities. Contains severe graphic violence.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "S", "insult_islam_severity": "N", "depict_unseen_severity": "M", "magic_sorcery_severity": "S",
        "contradictory_ideologies_severity": "M", "nudity_lewdness_severity": "L", "music_instruments_severity": "M", "gambling_severity": "N", "lying_severity": "L",
        "simulate_killing_severity": "S", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N", "profanity_obscenity_severity": "L",
        "time_wasting_severity": "S", "financial_extravagance_severity": "N", "online_communication_severity": "M", "ugc_risks_severity": "L",
    },
    # === 8. Genshin Impact (KFR) ===
    {
        "title": "Genshin Impact", "developer": "miHoYo", "publisher": "Cognosphere PTE. LTD.",
        "release_date": datetime.date(2020, 9, 28), "rating_tier_id": "KFR",
        "summary": "An open-world action RPG featuring gacha mechanics.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a6/Genshin_Impact_cover_art.png",
        "other_store_link": "https://genshin.hoyoverse.com/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_android": True, "available_ios": True,
        "rationale": "Impermissible (Contains Kufr/Shirk). Contains significant polytheistic themes ('Archons' worshipped as gods). Also includes severe gambling (Gacha/Maysir) and financial extravagance risks.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "S", "insult_islam_severity": "N", "depict_unseen_severity": "M", "magic_sorcery_severity": "M",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "M", "music_instruments_severity": "M", "gambling_severity": "S", "lying_severity": "L",
        "simulate_killing_severity": "L", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "L", "normalize_substances_severity": "L",
        "profanity_obscenity_severity": "N", "time_wasting_severity": "S", "financial_extravagance_severity": "S", "online_communication_severity": "L", "ugc_risks_severity": "N",
    },
    # === 9. EA SPORTS FC 24 (FIFA) (HRM) ===
    {
        "title": "EA SPORTS FC 24", "developer": "EA Vancouver & EA Romania", "publisher": "Electronic Arts",
        "release_date": datetime.date(2023, 9, 29), "rating_tier_id": "HRM",
        "summary": "A football simulation game featuring Ultimate Team.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/e/e9/FC_24_Cover_Art.jpg",
        "steam_link": "https://store.steampowered.com/app/2195250/EA_SPORTS_FC_24/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True, "available_switch": True,
        "rationale": "Impermissible (Haram) primarily due to Ultimate Team mode's 'packs' (loot boxes) constituting gambling (Maysir) linked to real money. Also contains pervasive music and encourages financial extravagance.",
        # --- Detailed Breakdown (Severity ONLY) ---
        "forced_shirk_severity": "N", "promote_shirk_severity": "N", "insult_islam_severity": "N", "depict_unseen_severity": "N", "magic_sorcery_severity": "N",
        "contradictory_ideologies_severity": "L", "nudity_lewdness_severity": "N", "music_instruments_severity": "S", "gambling_severity": "S",
        "lying_severity": "N", "simulate_killing_severity": "N", "simulate_theft_crime_severity": "N", "normalize_haram_rels_severity": "N", "normalize_substances_severity": "N",
        "profanity_obscenity_severity": "L", "time_wasting_severity": "M", "financial_extravagance_severity": "S", "online_communication_severity": "M", "ugc_risks_severity": "N",
    },
]

# --- Command Class (UPDATED defaults) ---
class Command(BaseCommand):
    help = 'Populates the database with game rating data (v2.3 - No Details/Reason).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating games (v2.3 - No Details/Reason)..."))

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
                # REMOVED has_spoilers_in_details default
                # --- Add ALL severity fields with defaults ---
                'forced_shirk_severity': game_data.get('forced_shirk_severity', 'N'),
                'promote_shirk_severity': game_data.get('promote_shirk_severity', 'N'),
                'insult_islam_severity': game_data.get('insult_islam_severity', 'N'),
                'depict_unseen_severity': game_data.get('depict_unseen_severity', 'N'),
                'magic_sorcery_severity': game_data.get('magic_sorcery_severity', 'N'),
                'contradictory_ideologies_severity': game_data.get('contradictory_ideologies_severity', 'N'),
                'nudity_lewdness_severity': game_data.get('nudity_lewdness_severity', 'N'),
                'music_instruments_severity': game_data.get('music_instruments_severity', 'N'),
                'gambling_severity': game_data.get('gambling_severity', 'N'),
                'lying_severity': game_data.get('lying_severity', 'N'),
                'simulate_killing_severity': game_data.get('simulate_killing_severity', 'N'),
                'simulate_theft_crime_severity': game_data.get('simulate_theft_crime_severity', 'N'),
                'normalize_haram_rels_severity': game_data.get('normalize_haram_rels_severity', 'N'),
                'normalize_substances_severity': game_data.get('normalize_substances_severity', 'N'),
                'profanity_obscenity_severity': game_data.get('profanity_obscenity_severity', 'N'),
                'time_wasting_severity': game_data.get('time_wasting_severity', 'N'),
                'financial_extravagance_severity': game_data.get('financial_extravagance_severity', 'N'),
                'online_communication_severity': game_data.get('online_communication_severity', 'N'),
                'ugc_risks_severity': game_data.get('ugc_risks_severity', 'N'),
            }

            # REMOVED all _details and _reason fields from defaults

            excluded_keys = {'title', 'rating_tier_id'}
            # Include only fields present in the model (keys in defaults or basic game info)
            model_fields = [f.name for f in Game._meta.get_fields()]
            for key, value in game_data.items():
                 if key not in excluded_keys and key in model_fields:
                      defaults[key] = value

            try:
                game, created = Game.objects.update_or_create( title=title, defaults=defaults )
                game.save() # Trigger calculation and flag update
                game.refresh_from_db()

                if created: self.stdout.write(self.style.SUCCESS(f"  CREATED: {game.title} -> Final Rating: {game.rating_tier.tier_code}")) ; created_count += 1
                else: self.stdout.write(f"  Checked/Updated: {game.title} -> Final Rating: {game.rating_tier.tier_code}"); updated_count += 1
            except IntegrityError as e: self.stderr.write(self.style.ERROR(f"Integrity error processing '{title}': {e}.")); errors += 1
            except Exception as e: self.stderr.write(self.style.ERROR(f"General error processing '{title}': {e}")); errors += 1

        if errors > 0 or skipped_count > 0: self.stdout.write(self.style.WARNING(f"Finished game population with {errors} errors and {skipped_count} skipped entries."))
        else: self.stdout.write(self.style.SUCCESS("Finished game population successfully."))
        self.stdout.write(f"Summary: Created={created_count}, Updated/Existing={updated_count}, Skipped={skipped_count}, Errors={errors}, Total Attempted={len(GAME_DATA)}")