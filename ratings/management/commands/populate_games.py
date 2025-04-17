# ratings/management/commands/populate_games.py
import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from ratings.models import Game, RatingTier, Flag # Keep RatingTier for fallback check
from django.db import transaction, IntegrityError
# from django.utils.translation import gettext_lazy as _ # Not currently needed

# --- GAME DATA LIST (v3.2 - Consolidated Summary/Rationale) ---
# NOTE: Severity ratings are illustrative.
# - 'summary': Contains BOTH the short game overview AND the rating reasoning.
GAME_DATA = [
    # === 1. Mini Motorways (Expected Tier: HAL - Acceptable) ===
    {
        "title": "Mini Motorways", "developer": "Dinosaur Polo Club", "publisher": "Dinosaur Polo Club",
        "release_date": datetime.date(2021, 7, 20),
        # Consolidated summary and rationale
        "summary": "Mini Motorways is a minimalist puzzle-strategy game where players design road networks for growing cities. The focus is purely on spatial logic and planning.\n\nMGC Rating: Acceptable. Only Mild concerns identified for optional background music and the potentially engaging gameplay loop (Time Waste).",
        "steam_link": "https://store.steampowered.com/app/1127500/Mini_Motorways/",
        "available_pc": True, "available_switch": True, "available_ios": True, "available_android": False,
        # --- Detailed Breakdown (Severity ONLY - N/L/M/S) ---
        "distorting_islam_severity": "N", "promoting_kufr_severity": "N", "assuming_divinity_severity": "N",
        "tampering_ghaib_severity": "N", "deviant_ideologies_severity": "N",
        "gambling_severity": "N", "lying_severity": "N", "indecency_severity": "N",
        "music_instruments_severity": "L", "time_waste_severity": "L",
        "disdain_arrogance_severity": "N", "magic_severity": "N", "intoxicants_severity": "N",
        "crime_violence_severity": "N", "profanity_severity": "N",
        "horror_fear_severity": "N", "despair_severity": "N", "spending_severity": "N",
        "online_interactions_severity": "N", "user_content_severity": "N",
    },
    # === 2. Portal 2 (Expected Tier: MSH - Doubtful) ===
    {
        "title": "Portal 2", "developer": "Valve", "publisher": "Valve",
        "release_date": datetime.date(2011, 4, 19),
        # Consolidated summary and rationale
        "summary": "Portal 2 is an acclaimed first-person puzzle-platformer set in a dilapidated science facility. Players solve physics-based puzzles using a portal gun, guided by AI characters known for dark humor.\n\nMGC Rating: Doubtful. Core gameplay is permissible. Moderate risks arise from Online Interactions (co-op chat) and Normalization (dark humor/sarcasm). Mild concerns for Music and Time Waste (community maps).",
        "steam_link": "https://store.steampowered.com/app/620/Portal_2/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True,
        # --- Detailed Breakdown (Severity ONLY - N/L/M/S) ---
        "distorting_islam_severity": "N", "promoting_kufr_severity": "N", "assuming_divinity_severity": "N",
        "tampering_ghaib_severity": "N", "deviant_ideologies_severity": "L",
        "gambling_severity": "N", "lying_severity": "L", "indecency_severity": "N",
        "music_instruments_severity": "L", "time_waste_severity": "L",
        "disdain_arrogance_severity": "M", "magic_severity": "N", "intoxicants_severity": "N",
        "crime_violence_severity": "N", "profanity_severity": "L",
        "horror_fear_severity": "N", "despair_severity": "N", "spending_severity": "N",
        "online_interactions_severity": "M", "user_content_severity": "L",
    },
     # === 3. Stardew Valley (Expected Tier: MSH - Doubtful) ===
    {
        "title": "Stardew Valley", "developer": "ConcernedApe", "publisher": "ConcernedApe",
        "release_date": datetime.date(2016, 2, 26),
        # Consolidated summary and rationale
        "summary": "Stardew Valley is an open-ended country-life RPG focused on farming, socializing, and exploration. Players restore a farm, interact with villagers, and can pursue relationships.\n\nMGC Rating: Doubtful. Core farming is okay. Moderate concerns include Normalization of Intoxicants (saloon hub), Gambling (optional casino), Deviant Ideologies & Indecency (relationship options). Severe concern for Time Waste.",
        "steam_link": "https://store.steampowered.com/app/413150/Stardew_Valley/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True, "available_switch": True, "available_android": True, "available_ios": True,
        # --- Detailed Breakdown (Severity ONLY - N/L/M/S) ---
        "distorting_islam_severity": "N", "promoting_kufr_severity": "L", "assuming_divinity_severity": "N",
        "tampering_ghaib_severity": "L", "deviant_ideologies_severity": "M",
        "gambling_severity": "M", "lying_severity": "N", "indecency_severity": "M",
        "music_instruments_severity": "L", "time_waste_severity": "S",
        "disdain_arrogance_severity": "L", "magic_severity": "L", "intoxicants_severity": "M",
        "crime_violence_severity": "L", "profanity_severity": "N",
        "horror_fear_severity": "N", "despair_severity": "N", "spending_severity": "N",
        "online_interactions_severity": "L", "user_content_severity": "L",
    },
    # === 4. GTA V (Expected Tier: HRM - Haram) ===
     {
        "title": "Grand Theft Auto V", "developer": "Rockstar North", "publisher": "Rockstar Games",
        "release_date": datetime.date(2013, 9, 17),
        # Consolidated summary and rationale
        "summary": "Grand Theft Auto V is an open-world action game centered on crime, violence, and satire in a modern city. Players engage in heists, driving, and shooting.\n\nMGC Rating: Impermissible (Haram). Contains Severe Prohibition Exposure (mandatory indecency, pervasive music, gambling elements) and Severe Normalization Risks (crime, violence, intoxicants, profanity). Core gameplay requires simulating major sins. Severe Player Risks include online toxicity and spending.",
        "steam_link": "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True,
        # --- Detailed Breakdown (Severity ONLY - N/L/M/S) ---
        "distorting_islam_severity": "N", "promoting_kufr_severity": "N", "assuming_divinity_severity": "N",
        "tampering_ghaib_severity": "N", "deviant_ideologies_severity": "M",
        "gambling_severity": "S", "lying_severity": "S", "indecency_severity": "S",
        "music_instruments_severity": "S", "time_waste_severity": "M",
        "disdain_arrogance_severity": "M", "magic_severity": "N", "intoxicants_severity": "S",
        "crime_violence_severity": "S", "profanity_severity": "S",
        "horror_fear_severity": "L", "despair_severity": "M", "spending_severity": "S",
        "online_interactions_severity": "S", "user_content_severity": "M",
    },
    # === 5. God of War (2018) (Expected Tier: KFR - Kufr/Shirk) ===
     {
        "title": "God of War (2018)", "developer": "Santa Monica Studio", "publisher": "Sony Interactive Entertainment",
        "release_date": datetime.date(2018, 4, 20),
        # Consolidated summary and rationale
        "summary": "God of War (2018) is an action-adventure game following the demigod Kratos in the world of Norse mythology, battling gods and mythical creatures.\n\nMGC Rating: Impermissible (Kufr/Shirk). The game fundamentally promotes polytheism (Severe Promoting Kufr/Shirk), requires the player to assume a divine/demigod role (Severe Assuming Divinity), and involves mythological magic/powers (Severe Tampering Ghaib/Magic).",
        "steam_link": "https://store.steampowered.com/app/1593500/God_of_War/",
        "available_pc": True, "available_ps4": True, "available_ps5": True,
        # --- Detailed Breakdown (Severity ONLY - N/L/M/S) ---
        "distorting_islam_severity": "N", "promoting_kufr_severity": "S", "assuming_divinity_severity": "S",
        "tampering_ghaib_severity": "S", "deviant_ideologies_severity": "L",
        "gambling_severity": "N", "lying_severity": "L", "indecency_severity": "M",
        "music_instruments_severity": "M", "time_waste_severity": "M",
        "disdain_arrogance_severity": "M", "magic_severity": "S", "intoxicants_severity": "L",
        "crime_violence_severity": "S", "profanity_severity": "M",
        "horror_fear_severity": "M", "despair_severity": "L", "spending_severity": "N",
        "online_interactions_severity": "N", "user_content_severity": "N",
    },
]

# --- Command Class (Updated defaults mapping) ---
class Command(BaseCommand):
    help = 'Populates/Synchronizes the database with game rating data (v3.2 - Consolidated Summary).' # Updated help text

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating/Syncing games (v3.2 - Consolidated Summary)...")) # Updated notice

        try: RatingTier.objects.get(tier_code='MSH')
        except RatingTier.DoesNotExist: self.stderr.write(self.style.ERROR("CRITICAL: Default RatingTier 'MSH' not found. Run populate_tiers first.")); return

        created_count = 0; updated_count = 0; skipped_count = 0; errors = 0

        for game_data_item in GAME_DATA:
            game_data = game_data_item.copy()
            title = game_data.get('title')
            if not title: self.stderr.write(self.style.ERROR("Skipping entry with missing title.")); errors += 1; continue

            # Prepare defaults dictionary
            defaults = {
                'developer_slug': slugify(game_data.get('developer', '')),
                'publisher_slug': slugify(game_data.get('publisher', '')),
                'available_pc': game_data.get('available_pc', False), 'available_ps5': game_data.get('available_ps5', False),
                'available_ps4': game_data.get('available_ps4', False), 'available_xbox_series': game_data.get('available_xbox_series', False),
                'available_xbox_one': game_data.get('available_xbox_one', False), 'available_switch': game_data.get('available_switch', False),
                'available_android': game_data.get('available_android', False), 'available_ios': game_data.get('available_ios', False),
                'available_quest': game_data.get('available_quest', False),
                'steam_link': game_data.get('steam_link') or None, 'epic_link': game_data.get('epic_link') or None,
                'gog_link': game_data.get('gog_link') or None, 'other_store_link': game_data.get('other_store_link') or None,
                # Use the single 'summary' field from GAME_DATA
                'summary': game_data.get('summary', ''),
                # REMOVED rationale mapping
                'release_date': game_data.get('release_date'),
                'developer': game_data.get('developer', ''),
                'publisher': game_data.get('publisher', ''),
            }

            # Add the 20 severity fields
            for field_name in Game.ALL_DESCRIPTOR_FIELDS_IN_ORDER:
                severity_value = game_data.get(field_name, 'N')
                defaults[field_name] = severity_value if severity_value in dict(Game.SEVERITY_CHOICES) else 'N'

            try:
                game, created = Game.objects.update_or_create( title=title, defaults=defaults )
                game.save() # Explicitly call save for calculations
                game.refresh_from_db()
                final_tier_code = game.rating_tier.tier_code if game.rating_tier else 'N/A'
                if created: self.stdout.write(self.style.SUCCESS(f"  CREATED: {game.title} -> Calculated Rating: {final_tier_code}")); created_count += 1
                else: self.stdout.write(f"  Checked/Updated: {game.title} -> Calculated Rating: {final_tier_code}"); updated_count += 1
            except IntegrityError as e: self.stderr.write(self.style.ERROR(f"Integrity error processing '{title}': {e}.")); errors += 1
            except Exception as e: import traceback; self.stderr.write(self.style.ERROR(f"General error processing '{title}': {e}\n{traceback.format_exc()}")); errors += 1

        if errors > 0 or skipped_count > 0: self.stdout.write(self.style.WARNING(f"Finished game population with {errors} errors and {skipped_count} skipped entries."))
        else: self.stdout.write(self.style.SUCCESS("Finished game population/sync successfully."))
        self.stdout.write(f"Summary: Created={created_count}, Updated/Existing={updated_count}, Skipped={skipped_count}, Errors={errors}, Total Attempted={len(GAME_DATA)}")