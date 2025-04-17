# ratings/management/commands/populate_games.py
import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from ratings.models import Game, RatingTier, Flag
from django.db import transaction, IntegrityError
# from django.utils.translation import gettext_lazy as _ # Not needed currently

# --- GAME DATA LIST (v3.1 - Refined Rationale, Kept Summary) ---
# NOTE: Severity ratings are illustrative.
# - 'summary': Very short description for lists/cards.
# - 'rationale': Longer text for detail view - includes non-spoiler game overview + rating reasoning.
GAME_DATA = [
    # === 1. Mini Motorways (Expected Tier: HAL - Acceptable) ===
    {
        "title": "Mini Motorways", "developer": "Dinosaur Polo Club", "publisher": "Dinosaur Polo Club",
        "release_date": datetime.date(2021, 7, 20),
        "summary": "Minimalist strategy game about drawing city roads.", # Short summary
        "steam_link": "https://store.steampowered.com/app/1127500/Mini_Motorways/",
        "available_pc": True, "available_switch": True, "available_ios": True, "available_android": False,
        # Combined rationale
        "rationale": "Mini Motorways is a minimalist puzzle-strategy game where players design road networks for growing cities. The focus is purely on spatial logic and planning. MGC Rating: Acceptable. Only Mild concerns identified for optional background music and the potentially engaging gameplay loop (Time Waste).",
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
        "summary": "Acclaimed first-person physics-based puzzle-platformer.", # Short summary
        "steam_link": "https://store.steampowered.com/app/620/Portal_2/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True,
        # Combined rationale
        "rationale": "Portal 2 involves solving physics-based puzzles using a portal gun within a dilapidated science facility, featuring prominent AI characters and dark humor. MGC Rating: Doubtful. While core puzzle gameplay is permissible, Moderate risks arise from potential negative Online Interactions in co-op chat and Moderate Normalization risks from the AI's dark humor/sarcasm (Disdain/Arrogance). Mild concerns for optional Music and potential Time Waste via community maps.",
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
        "summary": "Open-ended country-life RPG focused on farming and socializing.", # Short summary
        "steam_link": "https://store.steampowered.com/app/413150/Stardew_Valley/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True, "available_switch": True, "available_android": True, "available_ios": True,
        # Combined rationale
        "rationale": "Stardew Valley is a farming simulation and social RPG where players restore a farm, interact with villagers, explore caves, and build relationships. MGC Rating: Doubtful. Core farming/crafting is permissible. Moderate concerns arise from the normalization of intoxicants (Saloon as a social hub), optional gambling mechanics (Casino), normalization of impermissible relationships (same-sex marriage option presented equally), and minor indecency/suggestive themes. Severe concern for potential Time Waste due to addictive gameplay loop.",
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
        "summary": "Open-world action game centered on crime, satire, and violence.", # Short summary
        "steam_link": "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True,
        # Combined rationale
        "rationale": "Grand Theft Auto V is an open-world action game where players control criminals engaging in heists, driving, shooting, and various illicit activities in a satirical modern city. MGC Rating: Impermissible (Haram). Contains Severe unavoidable Prohibition Exposure (mandatory indecency/Fahisha in missions/environments, pervasive impermissible music/themes, required gambling elements). Core gameplay requires simulating and Normalizing major sins (Severe Crime/Violence, Severe Intoxicants, Severe Profanity). Also presents Moderate risk regarding Deviant Ideologies (materialism, cynicism) and Severe Player Risks (predatory Spending in online mode, toxic Online Interactions).",
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
        "summary": "Action game following a demigod in Norse mythology.", # Short summary
        "steam_link": "https://store.steampowered.com/app/1593500/God_of_War/",
        "available_pc": True, "available_ps4": True, "available_ps5": True,
        # Combined rationale
        "rationale": "God of War (2018) is an action-adventure game where the player controls Kratos, a demigod, navigating the realms of Norse mythology, battling gods and monsters. MGC Rating: Impermissible (Kufr/Shirk). The game contains Severe Risks to Faith as its entire narrative and world are fundamentally based on promoting Norse polytheism (Shirk), requires the player to assume a divine/demigod role, and involves significant interaction with and normalization of false deities and mythological powers (Tampering Ghaib, Magic).",
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

# --- Command Class (Ensure both summary and rationale are mapped) ---
class Command(BaseCommand):
    help = 'Populates/Synchronizes the database with game rating data (v3.1 - Refined Rationale).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating/Syncing games (v3.1 - Refined Rationale)..."))

        try:
            RatingTier.objects.get(tier_code='MSH')
        except RatingTier.DoesNotExist:
            self.stderr.write(self.style.ERROR("CRITICAL: Default RatingTier 'MSH' not found. Run populate_tiers first."))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = 0

        for game_data_item in GAME_DATA:
            game_data = game_data_item.copy()
            title = game_data.get('title')
            if not title:
                self.stderr.write(self.style.ERROR("Skipping entry with missing title."))
                errors += 1
                continue

            # Prepare defaults dictionary for all relevant fields
            defaults = {
                'developer_slug': slugify(game_data.get('developer', '')),
                'publisher_slug': slugify(game_data.get('publisher', '')),
                'available_pc': game_data.get('available_pc', False),
                'available_ps5': game_data.get('available_ps5', False),
                'available_ps4': game_data.get('available_ps4', False),
                'available_xbox_series': game_data.get('available_xbox_series', False),
                'available_xbox_one': game_data.get('available_xbox_one', False),
                'available_switch': game_data.get('available_switch', False),
                'available_android': game_data.get('available_android', False),
                'available_ios': game_data.get('available_ios', False),
                'available_quest': game_data.get('available_quest', False),
                'steam_link': game_data.get('steam_link') or None,
                'epic_link': game_data.get('epic_link') or None,
                'gog_link': game_data.get('gog_link') or None,
                'other_store_link': game_data.get('other_store_link') or None,
                # Map BOTH summary and rationale
                'summary': game_data.get('summary', ''), # Short description for lists
                'rationale': game_data.get('rationale', ''), # Longer description + rating reasoning
                'release_date': game_data.get('release_date'),
                'developer': game_data.get('developer', ''),
                'publisher': game_data.get('publisher', ''),
            }

            # Add the 20 severity fields
            for field_name in Game.ALL_DESCRIPTOR_FIELDS_IN_ORDER:
                severity_value = game_data.get(field_name, 'N')
                defaults[field_name] = severity_value if severity_value in dict(Game.SEVERITY_CHOICES) else 'N'

            try:
                game, created = Game.objects.update_or_create(
                    title=title,
                    defaults=defaults
                )

                game.save() # Explicitly call save to trigger tier/flag calculation
                game.refresh_from_db()

                final_tier_code = game.rating_tier.tier_code if game.rating_tier else 'N/A'
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  CREATED: {game.title} -> Calculated Rating: {final_tier_code}"))
                    created_count += 1
                else:
                    # Determine if update actually occurred (more complex check needed if desired)
                    self.stdout.write(f"  Checked/Updated: {game.title} -> Calculated Rating: {final_tier_code}")
                    updated_count += 1

            except IntegrityError as e:
                 self.stderr.write(self.style.ERROR(f"Integrity error processing '{title}': {e}."))
                 errors += 1
            except Exception as e:
                 import traceback
                 self.stderr.write(self.style.ERROR(f"General error processing '{title}': {e}\n{traceback.format_exc()}"))
                 errors += 1

        if errors > 0 or skipped_count > 0:
             self.stdout.write(self.style.WARNING(f"Finished game population with {errors} errors and {skipped_count} skipped entries."))
        else:
            self.stdout.write(self.style.SUCCESS("Finished game population/sync successfully."))

        self.stdout.write(
            f"Summary: Created={created_count}, Updated/Existing={updated_count}, "
            f"Skipped={skipped_count}, Errors={errors}, Total Attempted={len(GAME_DATA)}"
        )