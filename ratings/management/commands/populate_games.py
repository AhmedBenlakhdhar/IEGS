# ratings/management/commands/populate_games.py

import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from ratings.models import Game, RatingTier, Flag # Assuming User/date fields aren't populated by script
from django.db import transaction, IntegrityError
from django.utils.translation import gettext_lazy as _ # Import needed if using _() here

# --- GAME DATA LIST (v1.2 Methodology Applied - English Only - FIXED NOT NULL) ---
# Added default empty strings "" for all new _details and _reason fields
# Assumes model field names are:
# - haram_depictions_severity, haram_depictions_details, haram_depictions_reason
# - simulation_haram_severity, simulation_haram_details, simulation_haram_reason
# - normalization_haram_severity, normalization_haram_details, normalization_haram_reason
GAME_DATA = [
    # === 1. Halal (Recommended) Example ===
    {
        "title": "Mini Motorways",
        "developer": "Dinosaur Polo Club", "publisher": "Dinosaur Polo Club",
        "release_date": datetime.date(2021, 7, 20), # PC release
        "rating_tier_id": "HAL",
        "requires_adjustment": False,
        "summary": "A minimalist strategy simulation game about drawing roads to build a bustling city.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/1/1b/Mini_Motorways_cover_art.jpg",
        "steam_link": "https://store.steampowered.com/app/1127500/Mini_Motorways/",
        "available_pc": True, "available_switch": True, "available_ios": True, "available_android": False, # Example platforms
        # --- MGC Rating & Supporting ---
        "flags_symbols": [],
        "adjustable_flags_symbols": [], # Not adjustable
        "rationale": "Excellent puzzle game focused on logic and planning. No concerning themes identified.",
        "adjustment_guide": "",
        # "suitability_notes": "", # Removed based on user request
        # "positive_aspects": "", # Removed based on user request
        # "is_recommended": True, # Removed based on user request
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown (Mostly 'N', added defaults for new fields) ---
        "aqidah_severity": "N", "aqidah_details": "", "aqidah_reason": "",
        "haram_depictions_severity": "N", "haram_depictions_details": "", "haram_depictions_reason": "", # ADDED ""
        "simulation_haram_severity": "N", "simulation_haram_details": "", "simulation_haram_reason": "", # ADDED ""
        "normalization_haram_severity": "N", "normalization_haram_details": "", "normalization_haram_reason": "", # ADDED ""
        "violence_severity": "N", "violence_details": "", "violence_reason": "",
        "time_addiction_severity": "L", "time_addiction_details": "Gameplay loop can be engaging, but sessions are relatively short. Less prone to addiction than many games.", "time_addiction_reason": "",
        "online_conduct_severity": "N", "online_conduct_details": "Primarily single-player. Leaderboards exist but no direct chat.", "online_conduct_reason": "",
    },
    # === 2. Halal (Standard - Requires Adjustment for Audio) Example ===
    {
        "title": "Portal 2",
        "developer": "Valve", "publisher": "Valve",
        "release_date": datetime.date(2011, 4, 19),
        "rating_tier_id": "HAL", # Final achievable tier
        "original_rating_tier_id": "HAL", # Original state before adjustments (still Halal)
        "requires_adjustment": True, # Due to optional music and co-op chat
        "summary": "A first-person puzzle-platform video game known for its physics-based puzzles and dark humor.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg",
        "steam_link": "https://store.steampowered.com/app/620/Portal_2/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True, # Via compatibility/collections
        # --- MGC Rating & Supporting ---
        "flags_symbols": ["forum", "music_off"], # Added music_off flag
        "adjustable_flags_symbols": ["forum", "music_off"], # Chat and music are adjustable
        "rationale": "Core gameplay is focused on permissible puzzle-solving. Requires adjustment for optional co-op chat (potential Laghw/Fitnah) and background music (disputed permissibility).",
        "adjustment_guide": "1. Mute background music via in-game settings if concerned about its permissibility. \n2. Disable voice/text chat or play co-op only with known/trusted individuals to avoid Laghw or negative interactions.",
        # "suitability_notes": "", # Removed based on user request
        # "positive_aspects": "", # Removed based on user request
        # "is_recommended": False, # Removed based on user request
        "has_spoilers_in_details": True, # Story elements might be spoiled
        # --- Detailed Breakdown (Added defaults for new fields) ---
        "aqidah_severity": "N", "aqidah_details": "Themes of AI consciousness are fictional/sci-fi.", "aqidah_reason": "",
        "haram_depictions_severity": "L", # Changed from N to L due to music being present
        "haram_depictions_details": "Contains background ambient/electronic music. Some dark humor/sarcasm.", # Moved sarcasm here
        "haram_depictions_reason": "Music is considered Mashbouh/Haram by some scholars, but it's optional/mutable. Sarcasm is contextual.",
        "simulation_haram_severity": "N", "simulation_haram_details": "", "simulation_haram_reason": "", # ADDED ""
        "normalization_haram_severity": "L", # Lowered from M as sarcasm isn't strong normalization
        "normalization_haram_details": "", # Moved sarcasm to depictions
        "normalization_haram_reason": "", # ADDED ""
        "violence_severity": "N", "violence_details": "No direct combat. Environmental hazards (turrets, lasers) exist but are part of puzzles, not depicted graphically.", "violence_reason": "",
        "time_addiction_severity": "L", "time_addiction_details": "Finite puzzle game, though community maps extend playtime.", "time_addiction_reason": "",
        "online_conduct_severity": "M", # Moderate risk due to chat
        "online_conduct_details": "Optional Co-op mode requires coordination. Voice/text chat with strangers carries risk of Laghw, insults, or Fitnah.",
        "online_conduct_reason": "Potential for negative interaction if not adjusted.",
    },
    # === 3. Mashbouh Example (Minecraft - Normalization/Optional elements) ===
     {
        "title": "Minecraft (Survival - Standard)",
        "developer": "Mojang Studios", "publisher": "Xbox Game Studios / Microsoft",
        "release_date": datetime.date(2011, 11, 18),
        "rating_tier_id": "MSH", # Final achievable tier (if careful)
        "original_rating_tier_id": "MSH", # Original state with optional magic/servers is Mashbouh
        "requires_adjustment": True,
        "summary": "A sandbox game about placing blocks, crafting items, and going on adventures.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/5/51/Minecraft_cover.png",
        "other_store_link": "https://www.minecraft.net/", # Official site
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True, "available_switch": True, "available_android": True, "available_ios": True,
        # --- MGC Rating & Supporting ---
        "flags_symbols": ["forum", "hourglass_top"],
        "adjustable_flags_symbols": ["forum"],
        "rationale": "Mashbouh primarily due to optional gameplay systems (enchanting, potions) resembling magic, potential normalization concerns, and significant risks in unmoderated online play. Core building/exploration can be Halal if questionable elements are avoided and online play is managed.",
        "adjustment_guide": "1. Play offline, on LAN, or only on trusted, well-moderated private servers ('Realms' or similar).\n2. Disable multiplayer chat features or restrict communication to known individuals.\n3. Avoid deep engagement with enchanting/potion systems if concerned about resemblance to Sihr (Sadd al-Dhara'i). Focus on building, farming, exploration.",
        # "suitability_notes": "", # Removed
        # "positive_aspects": "", # Removed
        # "is_recommended": False, # Removed
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown (Added defaults for new fields) ---
        "aqidah_severity": "L",
        "aqidah_details": "Enchanting items and brewing potions use specific mechanics and materials. While fictional, the process can resemble ritualistic aspects of magic, raising concerns of Tashabbuh (imitation) or trivializing Sihr.",
        "aqidah_reason": "Concern based on Sadd al-Dhara'i (blocking the means) regarding normalization or imitation of magic-like actions, even if fictional.",
        "haram_depictions_severity": "L",
        "haram_depictions_details": "Contains mutable background music. Some fictional monsters (zombies, skeletons) might be considered mildly disturbing by some. Custom skins could potentially show 'Awrah.", # Added skin note here
        "haram_depictions_reason": "Music permissibility is disputed. Monster depictions are stylized. Player skins are user-generated risk.",
        "simulation_haram_severity": "L",
        "simulation_haram_details": "Player can simulate killing passive animals (cows, sheep, chickens) for resources. Also involves combat against fictional hostile monsters.",
        "simulation_haram_reason": "Simulating killing, even animals/monsters, requires context assessment. Stylized nature keeps it Low.",
        "normalization_haram_severity": "L",
        "normalization_haram_details": "Enchanting/potions presented as neutral game mechanics.", # Removed skin note
        "normalization_haram_reason": "Neutral presentation of magic-like systems.", # ADDED ""
        "violence_severity": "L",
        "violence_details": "Stylized combat against fictional monsters (zombies, spiders, etc.) and animals. No blood or gore.",
        "violence_reason": "", # ADDED ""
        "time_addiction_severity": "M",
        "time_addiction_details": "Open-ended ('sandbox') nature allows for potentially endless gameplay and large projects. Can easily consume significant time.",
        "time_addiction_reason": "High risk of Israf (wastefulness) of time and neglecting duties if not self-controlled.",
        "online_conduct_severity": "H",
        "online_conduct_details": "Public multiplayer servers often lack moderation. High risk of exposure to Fahisha (foul language), insults, Fitnah (arguments, inappropriate discussions/behavior), and encountering problematic user-created content/skins.",
        "online_conduct_reason": "Significant risk in unmanaged online environments requires adjustment (avoiding public servers/chat).",
    },
    # === 4. Haram Example (GTA V - Multiple P/H severities) ===
     {
        "title": "Grand Theft Auto V",
        "developer": "Rockstar North", "publisher": "Rockstar Games",
        "release_date": datetime.date(2013, 9, 17),
        "rating_tier_id": "HRM",
        "requires_adjustment": False,
        "summary": "An open-world action-adventure game centered around criminal activities, satire, and violence.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png",
        "steam_link": "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/",
        "available_pc": True, "available_ps5": True, "available_ps4": True, "available_xbox_series": True, "available_xbox_one": True,
        # --- MGC Rating & Supporting ---
        "flags_symbols": ["visibility_off", "record_voice_over", "casino", "local_bar", "music_off", "forum", "hourglass_top"],
        "adjustable_flags_symbols": [],
        "rationale": "Impermissible (Haram). Core gameplay requires engaging in and simulating major sins (theft, murder, interaction with indecency). Contains unavoidable explicit 'Awrah, pervasive foul language, promotion of Haram lifestyles (crime, drugs, Zina), and normalization of violence and vice. Online mode is highly problematic.",
        "adjustment_guide": "",
        # "suitability_notes": "", # Removed
        # "positive_aspects": "", # Removed
        # "is_recommended": False, # Removed
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown (Added defaults for new fields) ---
        "aqidah_severity": "M",
        "aqidah_details": "Contains cynical satire that may touch upon or mock religious/moral values. Promotes a nihilistic and materialistic worldview.",
        "aqidah_reason": "Potential mockery/trivialization of values, promotion of anti-Islamic worldview.",
        "haram_depictions_severity": "P",
        "haram_depictions_details": "Required interaction with environments containing explicit nudity ('Awrah exposure in strip clubs). Pervasive use of extreme foul language (Fahisha) in mandatory dialogue. Licensed radio stations feature music with impermissible themes/lyrics (Ghina' Muharram), hard to avoid completely.",
        "haram_depictions_reason": "Direct, often unavoidable exposure to Haram sights and sounds is integral to the game's atmosphere and required missions.",
        "simulation_haram_severity": "P",
        "simulation_haram_details": "Core gameplay mechanics *require* the player to simulate major sins: Grand Theft (theft/robbery), murder (including unjustified killing of civilians/police), torture (in one specific mission), engaging in simulated interactions related to Zina.",
        "simulation_haram_reason": "Mandatory simulation of actions categorized as major sins in Islam.",
        "normalization_haram_severity": "P",
        "normalization_haram_details": "Crime, violence, drug use/dealing, alcohol consumption (Khamr), and impermissible relationships/lifestyles are presented as normal, cool, or integral parts of the game world and narrative. Criminal protagonists are often glorified.",
        "normalization_haram_reason": "Extreme and pervasive normalization and often positive portrayal of major sins and Haram lifestyles.",
        "violence_severity": "P",
        "violence_details": "Gameplay centers on high levels of violence, including shootings, explosions, vehicular violence. Can involve killing innocent civilians and law enforcement. Contains graphic depictions of injury and death. Torture sequence in one mission.",
        "violence_reason": "Excessive, graphic, often unjustified violence is a core gameplay element and requirement.",
        "time_addiction_severity": "M",
        "time_addiction_details": "Vast open world with numerous activities and a compelling online mode (GTA Online) designed for long-term engagement and potential microtransactions.",
        "time_addiction_reason": "High potential for Israf (wastefulness) of time due to engaging design and online features.",
        "online_conduct_severity": "H",
        "online_conduct_details": "GTA Online is notorious for extremely toxic player interactions, including pervasive foul language, insults, harassment, cheating, and exposure to Fitnah. Moderation is often ineffective.",
        "online_conduct_reason": "Very high probability of exposure to severely negative and harmful online conduct.",
    },
    # === 5. Kufr Example (God of War - Shirk Themes) ===
     {
        "title": "God of War (2018)",
        "developer": "Santa Monica Studio", "publisher": "Sony Interactive Entertainment",
        "release_date": datetime.date(2018, 4, 20),
        "rating_tier_id": "KFR",
        "requires_adjustment": False,
        "summary": "Action-adventure game following Kratos, a demigod, and his son Atreus in the world of Norse mythology.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a3/God_of_War_4_cover.jpg",
        "steam_link": "https://store.steampowered.com/app/1593500/God_of_War/",
        "available_pc": True, "available_ps4": True, "available_ps5": True,
        # --- MGC Rating & Supporting ---
        "flags_symbols": ["gpp_bad"],
        "adjustable_flags_symbols": [],
        "rationale": "Impermissible (Kufr). The game's entire narrative and world are based on Norse pagan mythology (Shirk). The player embodies a demigod, interacts extensively with, seeks help from, and fights false deities. This directly contradicts the core principle of Tawhid.",
        "adjustment_guide": "",
        # "suitability_notes": "", # Removed
        # "positive_aspects": "", # Removed
        # "is_recommended": False, # Removed
        "has_spoilers_in_details": True,
        # --- Detailed Breakdown (Added defaults for new fields) ---
        "aqidah_severity": "P",
        "aqidah_details": "Game is entirely centered around Norse pagan mythology. Player character (Kratos) is portrayed as a god/demigod. Gameplay involves interacting with, fighting against, and sometimes receiving aid/power from figures explicitly depicted as Norse gods (Odin, Thor, Freya etc.). Involves travelling through mythological realms (Asgard, Helheim).",
        "aqidah_reason": "Direct and unavoidable immersion in and engagement with narratives and characters representing Shirk (polytheism), fundamentally contradicting Tawhid.",
        "haram_depictions_severity": "L",
        "haram_depictions_details": "Contains occasional strong language (Fahisha).",
        "haram_depictions_reason": "Language is present but not pervasive compared to the Aqidah issues.",
        "simulation_haram_severity": "L",
        "simulation_haram_details": "Player simulates killing mythological creatures and beings portrayed as gods/demigods.",
        "simulation_haram_reason": "While killing itself needs context, the primary issue here is the *target* being false deities within a Shirk framework.",
        "normalization_haram_severity": "P",
        "normalization_haram_details": "The entire premise normalizes the existence and power of false deities. Pagan mythology is presented as the game's reality.",
        "normalization_haram_reason": "Inescapable normalization of Shirk through world-building and narrative.",
        "violence_severity": "H",
        "violence_details": "Intense, graphic, and often brutal combat. Includes dismemberment, finishing moves, and significant blood effects against mythological creatures and humanoid deities.",
        "violence_reason": "High level of graphic brutality, though context is fantasy/mythological combat.",
        "time_addiction_severity": "M",
        "time_addiction_details": "Story-driven but contains significant side content, exploration, and collectibles that can extend playtime considerably.",
        "time_addiction_reason": "Potential for significant time investment.",
        "online_conduct_severity": "N",
        "online_conduct_details": "", "online_conduct_reason": "", # ADDED ""
    },
    # === 6. Mashbouh (Stardew Valley - Normalization/Optional Haram) ===
    {
        "title": "Stardew Valley",
        "developer": "ConcernedApe", "publisher": "ConcernedApe",
        "release_date": datetime.date(2016, 2, 26),
        "rating_tier_id": "MSH", # Final achievable tier (if careful)
        "original_rating_tier_id": "MSH", # Arguably Mashbouh due to normalization/options even before adjustment
        "requires_adjustment": True,
        "summary": "An open-ended country-life RPG focused on farming, socializing, and exploration.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a8/Stardew_Valley_cover_art.jpg",
        "steam_link": "https://store.steampowered.com/app/413150/Stardew_Valley/",
        "available_pc": True, "available_ps4": True, "available_xbox_one": True, "available_switch": True, "available_android": True, "available_ios": True,
        # --- MGC Rating & Supporting ---
        "flags_symbols": ["record_voice_over", "casino", "local_bar", "hourglass_top", "forum"],
        "adjustable_flags_symbols": ["local_bar", "casino", "record_voice_over", "forum"],
        "rationale": "Mashbouh due to normalization of alcohol (saloon is a central social hub), optional gambling mechanics, promotion of impermissible relationships (same-sex marriage option), and minor non-Islamic spiritual elements. Core farming/crafting gameplay is permissible, but avoiding problematic social aspects requires player vigilance.",
        "adjustment_guide": "1. Avoid purchasing/consuming alcohol items and minimize time spent in the Saloon.\n2. Do not engage with the Casino area/mechanics.\n3. Choose only permissible marriage candidates according to Islamic guidelines.\n4. Treat fictional spiritual elements (Junimos, Wizard) purely as game mechanics, avoiding belief in them.\n5. Manage online co-op interactions carefully if playing multiplayer.",
        # "suitability_notes": "", # Removed
        # "positive_aspects": "", # Removed
        # "is_recommended": False, # Removed
        "has_spoilers_in_details": False,
        # --- Detailed Breakdown (Added defaults for new fields) ---
        "aqidah_severity": "L",
        "aqidah_details": "Minor fantasy elements (Junimos, Wizard) presented fictionally. Some festivals might have subtle pagan undertones. Marriage system normalization (see Normalization) touches upon worldview.",
        "aqidah_reason": "Fictional context keeps severity Low, but presence requires awareness.",
        "haram_depictions_severity": "L",
        "haram_depictions_details": "Contains mutable background music. Depicts alcoholic beverages available for purchase/gifting.",
        "haram_depictions_reason": "Music disputed. Alcohol depiction is Haram but avoidable.",
        "simulation_haram_severity": "N", # Changed from L, gifting alcohol is too indirect
        "simulation_haram_details": "", # Player doesn't simulate drinking/eating haram directly
        "simulation_haram_reason": "", # ADDED ""
        "normalization_haram_severity": "M",
        "normalization_haram_details": "Saloon (bar) is a central social hub where many villagers gather, normalizing alcohol presence/consumption. Optional casino area normalizes gambling. Marriage system presents same-sex marriage as a standard, equal option, normalizing impermissible relationships.",
        "normalization_haram_reason": "Neutral-to-positive presentation of Haram elements (alcohol, gambling, relationship types) as normal parts of social life.",
        "violence_severity": "L",
        "violence_details": "Simple, stylized combat against monsters (slimes, bats, etc.) in the mines.",
        "violence_reason": "Minimal, contextual fantasy violence.",
        "time_addiction_severity": "H",
        "time_addiction_details": "Very engaging daily loop, collection mechanics, and progression systems create high potential for addiction and excessive playtime.",
        "time_addiction_reason": "Significant risk of Israf (wastefulness) of time.",
        "online_conduct_severity": "L",
        "online_conduct_details": "Optional co-op mode exists. Usually played with known friends, limiting risks compared to public servers.",
        "online_conduct_reason": "Low risk assuming play with trusted individuals.",
    },
]


class Command(BaseCommand):
    help = 'Populates the database with initial game rating data (v1.2 Methodology - Fixed Defaults).' # Updated help text

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating games (v1.2 Methodology - Fixed Defaults)...")) # Updated notice

        # Pre-fetch flags and tiers for efficiency
        flags_cache = {flag.symbol: flag for flag in Flag.objects.all()}
        tiers_cache = {tier.tier_code: tier for tier in RatingTier.objects.all()}

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

            # Separate flag lists before creating defaults
            flags_symbols = game_data.pop('flags_symbols', [])
            adjustable_flags_symbols = game_data.pop('adjustable_flags_symbols', [])
            tier_id = game_data.pop('rating_tier_id', None)
            original_tier_id = game_data.pop('original_rating_tier_id', None) # <-- Get original tier

            if not tier_id:
                self.stderr.write(self.style.WARNING(f"Missing 'rating_tier_id' for game '{title}'. Skipping."))
                skipped_count += 1
                continue

            rating_tier = tiers_cache.get(tier_id)
            if not rating_tier:
                self.stderr.write(self.style.WARNING(f"RatingTier with code '{tier_id}' not found for game '{title}'. Skipping."))
                skipped_count += 1
                continue

            original_rating_tier_obj = None
            if original_tier_id:
                original_rating_tier_obj = tiers_cache.get(original_tier_id)
                if not original_rating_tier_obj:
                     self.stderr.write(self.style.WARNING(f"Original RatingTier with code '{original_tier_id}' not found for game '{title}'. Skipping original tier assignment."))


            # Prepare defaults dictionary carefully
            # Ensure all Boolean fields have a default in case not provided in GAME_DATA
            defaults = {
                'rating_tier': rating_tier,
                **({'original_rating_tier': original_rating_tier_obj} if original_rating_tier_obj else {}),
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
                'has_spoilers_in_details': game_data.get('has_spoilers_in_details', False),
                'requires_adjustment': game_data.get('requires_adjustment', False),
                # Add defaults for TextFields that might be missing (ensure they are blank=True in model)
                'summary': game_data.get('summary', ''),
                'rationale': game_data.get('rationale', ''),
                'adjustment_guide': game_data.get('adjustment_guide', ''),
                'aqidah_details': game_data.get('aqidah_details', ''),
                'aqidah_reason': game_data.get('aqidah_reason', ''),
                'haram_depictions_details': game_data.get('haram_depictions_details', ''),
                'haram_depictions_reason': game_data.get('haram_depictions_reason', ''),
                'simulation_haram_details': game_data.get('simulation_haram_details', ''),
                'simulation_haram_reason': game_data.get('simulation_haram_reason', ''),
                'normalization_haram_details': game_data.get('normalization_haram_details', ''),
                'normalization_haram_reason': game_data.get('normalization_haram_reason', ''),
                'violence_details': game_data.get('violence_details', ''),
                'violence_reason': game_data.get('violence_reason', ''),
                'time_addiction_details': game_data.get('time_addiction_details', ''),
                'time_addiction_reason': game_data.get('time_addiction_reason', ''),
                'online_conduct_details': game_data.get('online_conduct_details', ''),
                'online_conduct_reason': game_data.get('online_conduct_reason', ''),
            }

            # Add remaining keys from game_data, prioritizing explicit values over defaults if present
            for key, value in game_data.items():
                 if key != 'title': # Title is used for lookup
                     defaults[key] = value # Overwrite default if key exists in game_data

            try:
                game, created = Game.objects.update_or_create(
                    title=title,
                    defaults=defaults
                )

                # --- Add Flags ---
                current_flags_qs = []
                for symbol_name in flags_symbols:
                    flag_obj = flags_cache.get(symbol_name)
                    if flag_obj:
                        current_flags_qs.append(flag_obj)
                    else:
                         self.stderr.write(self.style.WARNING(f"Flag symbol '{symbol_name}' for 'flags' not found in cache for game '{game.title}'. Skipping."))
                if current_flags_qs or game.flags.exists():
                    game.flags.set(current_flags_qs)

                # --- Add Adjustable Flags ---
                current_adj_flags_qs = []
                for symbol_name in adjustable_flags_symbols:
                     flag_obj = flags_cache.get(symbol_name)
                     if flag_obj:
                         current_adj_flags_qs.append(flag_obj)
                     else:
                          self.stderr.write(self.style.WARNING(f"Flag symbol '{symbol_name}' for 'adjustable_flags' not found in cache for game '{game.title}'. Skipping."))
                if current_adj_flags_qs or game.adjustable_flags.exists():
                     game.adjustable_flags.set(current_adj_flags_qs)


                if created:
                    self.stdout.write(self.style.SUCCESS(f"  CREATED: {game.title}"))
                    created_count += 1
                else:
                    self.stdout.write(f"  Checked/Updated: {game.title}")
                    updated_count +=1

            except IntegrityError as e:
                 self.stderr.write(self.style.ERROR(f"Integrity error processing '{title}': {e}. Check constraints."))
                 errors += 1
            except Exception as e:
                 self.stderr.write(self.style.ERROR(f"General error processing '{title}': {e}"))
                 errors += 1


        total_processed = created_count + updated_count + errors
        if errors > 0 or skipped_count > 0:
             self.stdout.write(self.style.WARNING(f"Finished game population with {errors} errors and {skipped_count} skipped entries."))
        else:
            self.stdout.write(self.style.SUCCESS("Finished game population successfully."))

        self.stdout.write(f"Summary: Created={created_count}, Updated/Existing={updated_count}, Skipped={skipped_count}, Errors={errors}, Total Attempted={len(GAME_DATA)}")