# ratings/management/commands/populate_games.py

import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from ratings.models import Game, RatingTier, Flag
from django.db import transaction, IntegrityError

# --- EXTENDED SAMPLE GAME DATA w/ IMAGE URLS ---
# Image URLs are illustrative and may break.
GAME_DATA = [
    # --- Halal / Mubah Examples ---
    {
        "title": "Portal 2",
        "developer": "Valve", "publisher": "Valve",
        "release_date": datetime.date(2011, 4, 19),
        "rating_tier_id": "HAL", "requires_adjustment": True,
        "summary": "A first-person puzzle-platform video game.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg",
        # ... (rest of Portal 2 data remains the same) ...
        "aqidah_severity": "N", "aqidah_details": "", "aqidah_reason": "",
        "violence_severity": "N", "violence_details": "No direct combat. Environmental hazards exist.", "violence_reason": "",
        "immorality_severity": "L", "immorality_details": "Some dark humor/sarcasm. Co-op chat needs moderation.", "immorality_reason": "Potential Laghw in chat.",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "L", "audio_music_details": "Background ambient/electronic music. Generally okay, mutable.", "audio_music_reason": "Considered permissible by many.",
        "time_addiction_severity": "L", "time_addiction_details": "Finite puzzle game.", "time_addiction_reason": "",
        "online_conduct_severity": "L", "online_conduct_details": "Co-op requires coordination; chat needs control if with strangers.", "online_conduct_reason": "Limited interaction scope.",
        "flags_symbols": ["psychology", "forum"],
        "has_spoilers_in_details": True,
        "adjustment_guide": "Mute or disable voice/text chat if playing co-op with unknown individuals.",
        "steam_link": "https://store.steampowered.com/app/620/Portal_2/",
    },
    {
        "title": "Cities: Skylines",
        "developer": "Colossal Order", "publisher": "Paradox Interactive",
        "release_date": datetime.date(2015, 3, 10),
        "rating_tier_id": "HAL", "requires_adjustment": False,
        "summary": "A modern take on the classic city simulation genre.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/5/5c/Cities_Skylines_cover_art.jpg",
        # ... (rest of Cities: Skylines data remains the same) ...
        "aqidah_severity": "N", "aqidah_details": "", "aqidah_reason": "",
        "violence_severity": "N", "violence_details": "", "violence_reason": "",
        "immorality_severity": "N", "immorality_details": "Focus is on infrastructure and management.", "immorality_reason": "",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "L", "audio_music_details": "Standard background simulation music, mutable.", "audio_music_reason": "Considered permissible by many.",
        "time_addiction_severity": "M", "time_addiction_details": "Can be very engaging and time-consuming to perfect city.", "time_addiction_reason": "Risk of neglecting duties.",
        "online_conduct_severity": "N", "online_conduct_details": "", "online_conduct_reason": "",
        "flags_symbols": ["psychology", "hourglass_top", "paid"],
        "has_spoilers_in_details": False,
        "adjustment_guide": "",
        "steam_link": "https://store.steampowered.com/app/255710/Cities_Skylines/",
    },
     {
        "title": "Microsoft Flight Simulator (2020)",
        "developer": "Asobo Studio", "publisher": "Xbox Game Studios",
        "release_date": datetime.date(2020, 8, 18),
        "rating_tier_id": "HAL", "requires_adjustment": False,
        "summary": "A highly realistic flight simulation program.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/8/8b/Microsoft_Flight_Simulator_%282020%29_cover_art.jpg",
        # ... (rest of Flight Simulator data remains the same) ...
        "aqidah_severity": "N", "aqidah_details": "", "aqidah_reason": "",
        "violence_severity": "N", "violence_details": "", "violence_reason": "",
        "immorality_severity": "N", "immorality_details": "Focus is purely on flight simulation.", "immorality_reason": "",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "L", "audio_music_details": "Menu/loading music, ATC chatter. Generally okay, mutable.", "audio_music_reason": "Functional audio.",
        "time_addiction_severity": "L", "time_addiction_details": "Can be time-consuming for enthusiasts but less addictive mechanics.", "time_addiction_reason": "",
        "online_conduct_severity": "L", "online_conduct_details": "Optional live air traffic/multiplayer. Interaction is minimal/professional.", "online_conduct_reason": "Limited scope.",
        "flags_symbols": ["school", "forum"],
        "has_spoilers_in_details": False,
        "adjustment_guide": "",
        "steam_link": "https://store.steampowered.com/app/1250410/Microsoft_Flight_Simulator_40th_Anniversary_Edition/",
    },
    # --- Mashbouh Examples ---
    {
        "title": "Minecraft (Survival - Standard)",
        "developer": "Mojang Studios", "publisher": "Xbox Game Studios",
        "release_date": datetime.date(2011, 11, 18),
        "rating_tier_id": "MSH", "requires_adjustment": True,
        "summary": "A sandbox game about placing blocks and going on adventures.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/5/51/Minecraft_cover.png",
        # ... (rest of Minecraft data remains the same) ...
        "aqidah_severity": "L", "aqidah_details": "Enchanting and potion brewing use game mechanics resembling magic, though not explicitly occult.", "aqidah_reason": "Concern over normalization/imitation of magic-like actions (Sadd al-Dhara'i).",
        "violence_severity": "L", "violence_details": "Stylized combat against fictional monsters. No blood.", "violence_reason": "Contextual fantasy violence.",
        "immorality_severity": "L", "immorality_details": "Online chat requires moderation. Custom skins could potentially be problematic.", "immorality_reason": "Fitnah in online interactions.",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "L", "audio_music_details": "Background music, mutable.", "audio_music_reason": "Permissible by many.",
        "time_addiction_severity": "M", "time_addiction_details": "Open-ended nature leads to high time investment.", "time_addiction_reason": "Risk of neglecting duties.",
        "online_conduct_severity": "M", "online_conduct_details": "Public servers carry high risk of bad language/conduct.", "online_conduct_reason": "Lack of moderation/control on many servers.",
        "flags_symbols": ["forum", "hourglass_top", "auto_fix_high"],
        "has_spoilers_in_details": False,
        "adjustment_guide": "Play offline or on trusted, moderated servers. Disable chat or play only with known individuals. Avoid excessive focus on enchanting if concerned.",
        "steam_link": "https://www.minecraft.net/",
    },
    {
        "title": "Stardew Valley",
        "developer": "ConcernedApe", "publisher": "ConcernedApe",
        "release_date": datetime.date(2016, 2, 26),
        "rating_tier_id": "MSH", "requires_adjustment": False,
        "summary": "An open-ended country-life RPG.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a8/Stardew_Valley_cover_art.jpg",
        # ... (rest of Stardew Valley data remains the same) ...
         "aqidah_severity": "L", "aqidah_details": "Minor fantasy elements (Junimos, Wizard) presented fictionally. Some festivals may have pagan undertones. Marriage includes same-sex option.", "aqidah_reason": "Normalization concerns.",
        "violence_severity": "L", "violence_details": "Simple combat in mines.", "violence_reason": "Minimal/contextual.",
        "immorality_severity": "M", "immorality_details": "Marriage simulation includes same-sex option, normalization of alcohol (saloon), minor suggestive dialogue.", "immorality_reason": "Promotion/normalization of impermissible relationships/substances.",
        "substances_gambling_severity": "L", "substances_gambling_details": "Saloon setting, optional minor casino area.", "substances_gambling_reason": "Normalization/presence of themes.",
        "audio_music_severity": "L", "audio_music_details": "Pleasant music, mutable.", "audio_music_reason": "Permissible by many.",
        "time_addiction_severity": "H", "time_addiction_details": "Highly addictive gameplay loop.", "time_addiction_reason": "High risk of neglecting duties.",
        "online_conduct_severity": "L", "online_conduct_details": "Multiplayer usually with known friends.", "online_conduct_reason": "Limited risk.",
        "flags_symbols": ["hourglass_top", "favorite", "grass", "casino"],
        "has_spoilers_in_details": False,
        "adjustment_guide": "",
        "steam_link": "https://store.steampowered.com/app/413150/Stardew_Valley/",
    },
    {
        "title": "Assassin's Creed Mirage",
        "developer": "Ubisoft Bordeaux", "publisher": "Ubisoft",
        "release_date": datetime.date(2023, 10, 5),
        "rating_tier_id": "MSH", "requires_adjustment": True,
        "summary": "Action-adventure game set in 9th-century Baghdad.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/e/e3/Assassin%27s_Creed_Mirage_cover.jpg",
        # ... (rest of AC Mirage data remains the same) ...
        "aqidah_severity": "L", "aqidah_details": "Contains standard AC series Isu lore (precursor civilization) treated as sci-fi/mythology. Historical setting includes non-Islamic elements neutrally.", "aqidah_reason": "Avoid internalizing non-Islamic creation narratives.",
        "violence_severity": "M", "violence_details": "Stealth assassinations and combat are core gameplay. Blood effects can be disabled.", "violence_reason": "Depiction of killing, albeit often contextualized.",
        "immorality_severity": "L", "immorality_details": "Historical setting might depict attire/customs contrary to Islamic norms, but generally not focused on indecency.", "immorality_reason": "Contextual exposure.",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "L", "audio_music_details": "Score reflects setting, generally okay. Mutable.", "audio_music_reason": "Permissible by many.",
        "time_addiction_severity": "L", "time_addiction_details": "Story-focused, less open-ended grind than other AC games.", "time_addiction_reason": "",
        "online_conduct_severity": "N", "online_conduct_details": "", "online_conduct_reason": "",
        "flags_symbols": ["bloodtype", "warning", "history_edu"],
        "has_spoilers_in_details": True,
        "adjustment_guide": "Disable blood and gore effects in the game's settings menu.",
        "epic_link": "https://store.epicgames.com/en-US/p/assassins-creed-mirage",
    },
    # --- Haram Examples ---
     {
        "title": "Grand Theft Auto V",
        "developer": "Rockstar North", "publisher": "Rockstar Games",
        "release_date": datetime.date(2013, 9, 17),
        "rating_tier_id": "HRM", "requires_adjustment": False,
        "summary": "An open-world action-adventure game centered around criminal activities.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png",
        # ... (rest of GTA V data remains the same) ...
        "aqidah_severity": "M", "aqidah_details": "Contains satire potentially mocking religion, promotes nihilistic/materialistic views.", "aqidah_reason": "Potential mockery of religious values.",
        "violence_severity": "P", "violence_details": "Core gameplay involves required theft, murder, torture. Glorification of crime. Highly graphic.", "violence_reason": "Mandatory engagement in major sins, excessive gore.",
        "immorality_severity": "P", "immorality_details": "Explicit language, strip clubs ('Awrah), suggestive themes, normalization/promotion of crime, drugs, negative Akhlaq.", "immorality_reason": "Pervasive major sins and indecency.",
        "substances_gambling_severity": "H", "substances_gambling_details": "Drug use/dealing gameplay, simulated casinos/gambling.", "substances_gambling_reason": "Normalization and gameplay involving Haram.",
        "audio_music_severity": "H", "audio_music_details": "Licensed radio stations contain much impermissible music/lyrics. Integral part of atmosphere.", "audio_music_reason": "Pervasive Haram music.",
        "time_addiction_severity": "M", "time_addiction_details": "Extensive open world and online mode are time-consuming.", "time_addiction_reason": "High potential for wasting time.",
        "online_conduct_severity": "H", "online_conduct_details": "GTA Online has extremely high risk of exposure to vulgarity, insults, Fitnah due to unmoderated interactions.", "online_conduct_reason": "Pervasive negative interactions.",
        "flags_symbols": ["bloodtype", "warning", "music_note", "forum", "paid", "hourglass_top", "grass", "casino", "sentiment_dissatisfied", "favorite"],
        "has_spoilers_in_details": False,
        "adjustment_guide": "Core gameplay elements are considered impermissible and cannot be fundamentally adjusted.",
        "steam_link": "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/",
    },
     {
        "title": "Doom Eternal",
        "developer": "id Software", "publisher": "Bethesda Softworks",
        "release_date": datetime.date(2020, 3, 20),
        "rating_tier_id": "HRM", "requires_adjustment": False,
        "summary": "Fast-paced first-person shooter focused on killing demons.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/9/9d/Doom_Eternal_cover_art.jpg",
        # ... (rest of Doom Eternal data remains the same) ...
        "aqidah_severity": "H", "aqidah_details": "Heavy focus on demons, hellish landscapes, potentially blasphemous imagery related to angels/heaven, occult symbols pervasive.", "aqidah_reason": "Immersion in harmful themes, potential Tashabbuh, trivialization of serious matters.",
        "violence_severity": "P", "violence_details": "Extreme, constant, graphic 'glory kill' dismemberments are central gameplay mechanics.", "violence_reason": "Excessive brutality and gore as core feature.",
        "immorality_severity": "M", "immorality_details": "Dark, disturbing themes and imagery.", "immorality_reason": "Exposure to potentially harmful visuals.",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "H", "audio_music_details": "Intense heavy metal soundtrack is integral to the gameplay experience.", "audio_music_reason": "Impermissible instrumentation/association with violent atmosphere.",
        "time_addiction_severity": "L", "time_addiction_details": "Mission-based, less prone to endless grind.", "time_addiction_reason": "",
        "online_conduct_severity": "M", "online_conduct_details": "Multiplayer exists, potential for typical online negativity.", "online_conduct_reason": "Standard online interaction risks.",
        "flags_symbols": ["bloodtype", "warning", "music_note", "flare", "forum"],
        "has_spoilers_in_details": False,
        "adjustment_guide": "",
        "steam_link": "https://store.steampowered.com/app/782330/DOOM_Eternal/",
    },
     {
        "title": "The Sims 4 (Base Game)",
        "developer": "Maxis", "publisher": "Electronic Arts",
        "release_date": datetime.date(2014, 9, 2),
        "rating_tier_id": "HRM", "requires_adjustment": False,
        "summary": "A life simulation game where players create and control people.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/7/7f/Sims4_Rebrand.png",
        # ... (rest of Sims 4 data remains the same) ...
        "aqidah_severity": "L", "aqidah_details": "Secular worldview simulation. No overt religious themes usually.", "aqidah_reason": "Normalization of secular life.",
        "violence_severity": "L", "violence_details": "Stylized arguments, rare accidental deaths.", "violence_reason": "Minimal.",
        "immorality_severity": "H", "immorality_details": "Simulation encourages forming relationships outside marriage ('WooHoo'), allows same-sex relationships, focuses on material pursuits, potentially revealing clothing options.", "immorality_reason": "Normalization and active simulation of impermissible relationships/lifestyles/focus.",
        "substances_gambling_severity": "L", "substances_gambling_details": "Bars/drinks exist, represent alcohol.", "substances_gambling_reason": "Normalization.",
        "audio_music_severity": "M", "audio_music_details": "In-game radio features various genres, many likely impermissible. Can be turned off.", "audio_music_reason": "Presence of Haram music types.",
        "time_addiction_severity": "M", "time_addiction_details": "Open-ended simulation can be highly time-consuming.", "time_addiction_reason": "Risk of neglecting duties.",
        "online_conduct_severity": "L", "online_conduct_details": "Gallery feature for sharing creations, limited direct interaction.", "online_conduct_reason": "Minimal risk.",
        "flags_symbols": ["favorite", "music_note", "hourglass_top", "paid"],
        "has_spoilers_in_details": False,
        "adjustment_guide": "Core gameplay simulates aspects of life contrary to Islamic principles and cannot be fundamentally adjusted.",
        "steam_link": "https://store.steampowered.com/app/1222670/The_Sims_4/",
    },
    # --- Kufr / Shirk Examples ---
    {
        "title": "God of War (2018)",
        "developer": "Santa Monica Studio", "publisher": "Sony Interactive Entertainment",
        "release_date": datetime.date(2018, 4, 20),
        "rating_tier_id": "KFR", "requires_adjustment": False,
        "summary": "Action-adventure game based on Norse mythology.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/a/a3/God_of_War_4_cover.jpg",
        # ... (rest of God of War data remains the same) ...
        "aqidah_severity": "P", "aqidah_details": "Entire premise revolves around Norse mythology and its 'gods'. Player character is depicted as a god (Kratos), interacting with and fighting other pagan deities. Involves prayers/rituals to these entities.", "aqidah_reason": "Direct conflict with Tawhid, immersion in Shirk narratives/themes/actions.",
        "violence_severity": "H", "violence_details": "Intense, graphic, and often brutal combat including dismemberment/finishing moves against mythological creatures/deities.", "violence_reason": "Excessive gore and brutality.",
        "immorality_severity": "L", "immorality_details": "Contains some strong language. Primary concerns are ideological.", "immorality_reason": "Minor compared to Aqidah.",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "M", "audio_music_details": "Prominent orchestral score enhances atmosphere of pagan mythology and violence.", "audio_music_reason": "Association with prohibited themes.",
        "time_addiction_severity": "M", "time_addiction_details": "Story-driven but side content can extend playtime.", "time_addiction_reason": "",
        "online_conduct_severity": "N", "online_conduct_details": "", "online_conduct_reason": "",
        "flags_symbols": ["bloodtype", "warning", "flare", "sentiment_dissatisfied"],
        "has_spoilers_in_details": True,
        "adjustment_guide": "",
        "steam_link": "https://store.steampowered.com/app/1593500/God_of_War/",
    },
     {
        "title": "Persona 5 Royal",
        "developer": "P-Studio", "publisher": "Atlus / Sega",
        "release_date": datetime.date(2019, 10, 31),
        "rating_tier_id": "KFR", "requires_adjustment": False,
        "summary": "RPG where students awaken psychic powers (Personas) based on mythological/demonic figures.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/b/b0/Persona_5_Royal_Cover_Art.jpg",
        # ... (rest of Persona 5 data remains the same) ...
        "aqidah_severity": "P", "aqidah_details": "Core mechanic involves summoning and controlling 'Personas' which are explicitly based on demons, pagan deities, and occult figures from various mythologies. Narrative involves challenging god-like entities.", "aqidah_reason": "Direct engagement with/normalization of Shirk elements, demons, occult themes.",
        "violence_severity": "M", "violence_details": "Turn-based combat, stylized violence with special attacks.", "violence_reason": "Contextual fantasy violence.",
        "immorality_severity": "M", "immorality_details": "Mature themes including social commentary, some suggestive content, character relationships.", "immorality_reason": "Social themes may conflict with Islamic values.",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "M", "audio_music_details": "Stylish soundtrack, some potentially impermissible elements/themes in lyrics.", "audio_music_reason": "Content/style concerns.",
        "time_addiction_severity": "H", "time_addiction_details": "Very long RPG (100+ hours) with time management mechanics.", "time_addiction_reason": "Extreme time commitment.",
        "online_conduct_severity": "N", "online_conduct_details": "", "online_conduct_reason": "",
        "flags_symbols": ["warning", "hourglass_top", "flare", "music_note"],
        "has_spoilers_in_details": True,
        "adjustment_guide": "",
        "steam_link": "https://store.steampowered.com/app/1687950/Persona_5_Royal/",
    },
    {
        "title": "Hades",
        "developer": "Supergiant Games", "publisher": "Supergiant Games",
        "release_date": datetime.date(2020, 9, 17),
        "rating_tier_id": "KFR", "requires_adjustment": False,
        "summary": "Roguelike action dungeon crawler based on Greek mythology.",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/en/c/cc/Hades_cover_art.jpg",
        # ... (rest of Hades data remains the same) ...
        "aqidah_severity": "P", "aqidah_details": "Player character is the son of Hades, interacts extensively with Greek gods (Zeus, Poseidon, etc.) receiving 'boons' (powers) from them. Entire narrative steeped in pagan mythology.", "aqidah_reason": "Normalization and immersion in Shirk (Greek Pantheon). Seeking help/power from false deities.",
        "violence_severity": "M", "violence_details": "Fast-paced, isometric combat against mythological creatures. Stylized, not overly graphic.", "violence_reason": "Constant combat.",
        "immorality_severity": "L", "immorality_details": "Some suggestive dialogue/themes related to Greek myths. Focus is primarily gameplay/narrative.", "immorality_reason": "Mythological context.",
        "substances_gambling_severity": "N", "substances_gambling_details": "", "substances_gambling_reason": "",
        "audio_music_severity": "M", "audio_music_details": "Acclaimed rock/orchestral soundtrack. Can be muted.", "audio_music_reason": "Association with themes.",
        "time_addiction_severity": "H", "time_addiction_details": "Addictive roguelike loop encourages repeated runs.", "time_addiction_reason": "High replayability, potential time sink.",
        "online_conduct_severity": "N", "online_conduct_details": "", "online_conduct_reason": "",
        "flags_symbols": ["warning", "hourglass_top", "flare", "music_note"],
        "has_spoilers_in_details": True,
        "adjustment_guide": "",
        "steam_link": "https://store.steampowered.com/app/1145360/Hades/",
    },
    # Add more diverse examples here...
]


class Command(BaseCommand):
    help = 'Populates the database with initial game rating data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating games..."))

        # Pre-fetch flags and tiers for efficiency
        flags_cache = {flag.symbol: flag for flag in Flag.objects.all()}
        tiers_cache = {tier.tier_code: tier for tier in RatingTier.objects.all()}

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = 0

        for game_data_item in GAME_DATA:
            # Make a copy to modify safely
            game_data = game_data_item.copy()

            title = game_data.get('title')
            if not title:
                self.stderr.write(self.style.ERROR("Skipping entry with missing title."))
                errors += 1
                continue

            flags_symbols = game_data.pop('flags_symbols', [])
            tier_id = game_data.pop('rating_tier_id', None)

            if not tier_id:
                self.stderr.write(self.style.WARNING(f"Missing 'rating_tier_id' for game '{title}'. Skipping."))
                skipped_count += 1
                continue

            rating_tier = tiers_cache.get(tier_id)
            if not rating_tier:
                self.stderr.write(self.style.WARNING(f"RatingTier with code '{tier_id}' not found for game '{title}'. Skipping."))
                skipped_count += 1
                continue

            # Prepare defaults dictionary carefully
            defaults = {
                'rating_tier': rating_tier,
                'developer_slug': slugify(game_data.get('developer', '')),
                'publisher_slug': slugify(game_data.get('publisher', '')),
            }
            # Add all other keys from game_data to defaults, excluding 'title'
            for key, value in game_data.items():
                 if key != 'title':
                     defaults[key] = value

            try:
                # Use update_or_create based on title
                game, created = Game.objects.update_or_create(
                    title=title,
                    defaults=defaults
                )

                # Add flags
                current_flags = []
                for symbol_name in flags_symbols:
                    flag_obj = flags_cache.get(symbol_name)
                    if flag_obj:
                        current_flags.append(flag_obj)
                    else:
                         self.stderr.write(self.style.WARNING(f"Flag symbol '{symbol_name}' not found for game '{game.title}'. Skipping flag."))

                if current_flags or game.flags.exists():
                    game.flags.set(current_flags)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"  CREATED: {game.title}"))
                    created_count += 1
                else:
                    self.stdout.write(f"  Checked/Updated: {game.title}")
                    updated_count +=1

            except IntegrityError as e:
                 self.stderr.write(self.style.ERROR(f"Integrity error processing '{title}': {e}. Check for non-unique slugs or other constraints."))
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