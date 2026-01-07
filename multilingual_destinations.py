#!/usr/bin/env python3
"""
Multilingual Destination Keywords Generator

Generates multilingual keyword vectors for travel destinations to:
- Improve global organic search discovery
- Reduce western-centric bias in travel recommendations
- Enable cross-cultural reference and asymmetric information advantage

Supports: PT, EN, ES, FR, HI (Hindi), ZH (Chinese), AR (Arabic), RU (Russian)
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

CONTEXT_DIR = Path(__file__).parent / "context"
OUTPUT_DIR = Path(__file__).parent / "output"
KEYWORDS_FILE = CONTEXT_DIR / "multilingual_destination_keywords.json"

LANGUAGES = ["pt", "en", "es", "fr", "hi", "zh", "ar", "ru"]
LANGUAGE_NAMES = {
    "pt": "Portuguese",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "hi": "Hindi",
    "zh": "Chinese",
    "ar": "Arabic",
    "ru": "Russian"
}


@dataclass
class Destination:
    """Represents a travel destination with multilingual keywords."""
    id: str
    name: str
    country: str
    region: str
    latitude: float
    longitude: float
    destination_type: str  # beach, mountain, safari, urban, island, desert, forest
    rarity_score: int  # 1-10 (10 = extremely rare experience)
    fauna: List[str] = field(default_factory=list)
    experiences: List[str] = field(default_factory=list)
    accommodation: List[str] = field(default_factory=list)
    context_tags: List[str] = field(default_factory=list)
    best_months: List[str] = field(default_factory=list)

    # Multilingual keyword vectors (generated)
    keywords_pt: str = ""
    keywords_en: str = ""
    keywords_es: str = ""
    keywords_fr: str = ""
    keywords_hi: str = ""
    keywords_zh: str = ""
    keywords_ar: str = ""
    keywords_ru: str = ""


class MultilingualKeywordGenerator:
    """Generates multilingual keyword vectors for destinations."""

    def __init__(self):
        self.vocabulary = self._load_vocabulary()

    def _load_vocabulary(self) -> Dict:
        """Load multilingual vocabulary from JSON."""
        if not KEYWORDS_FILE.exists():
            raise FileNotFoundError(f"Vocabulary file not found: {KEYWORDS_FILE}")

        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("vocabulary", {})

    def translate_keyword(self, keyword: str, category: str, language: str) -> Optional[str]:
        """Translate a keyword to the specified language."""
        category_vocab = self.vocabulary.get(category, {})
        keyword_data = category_vocab.get(keyword, {})
        return keyword_data.get(language)

    def generate_keyword_vector(self, destination: Destination, language: str) -> str:
        """Generate a comma-separated keyword string for a destination in a language."""
        keywords = []

        # Fauna keywords
        for fauna in destination.fauna:
            translated = self.translate_keyword(fauna, "fauna", language)
            if translated:
                keywords.append(translated)

        # Experience keywords
        for exp in destination.experiences:
            translated = self.translate_keyword(exp, "experiences", language)
            if translated:
                keywords.append(translated)

        # Accommodation keywords
        for acc in destination.accommodation:
            translated = self.translate_keyword(acc, "accommodation", language)
            if translated:
                keywords.append(translated)

        # Context tags
        for ctx in destination.context_tags:
            translated = self.translate_keyword(ctx, "context", language)
            if translated:
                keywords.append(translated)

        return ", ".join(keywords)

    def process_destination(self, destination: Destination) -> Destination:
        """Add all multilingual keyword vectors to a destination."""
        destination.keywords_pt = self.generate_keyword_vector(destination, "pt")
        destination.keywords_en = self.generate_keyword_vector(destination, "en")
        destination.keywords_es = self.generate_keyword_vector(destination, "es")
        destination.keywords_fr = self.generate_keyword_vector(destination, "fr")
        destination.keywords_hi = self.generate_keyword_vector(destination, "hi")
        destination.keywords_zh = self.generate_keyword_vector(destination, "zh")
        destination.keywords_ar = self.generate_keyword_vector(destination, "ar")
        destination.keywords_ru = self.generate_keyword_vector(destination, "ru")
        return destination


def get_sample_destinations() -> List[Destination]:
    """Return 30 curated destinations with asymmetric information value."""
    return [
        # MARINE / DIVING HOTSPOTS
        Destination(
            id="tofo-moz",
            name="Tofo Beach",
            country="Mozambique",
            region="Inhambane",
            latitude=-23.8544,
            longitude=35.5436,
            destination_type="beach",
            rarity_score=9,
            fauna=["whale_shark", "manta_ray", "whale", "dolphin", "sea_turtle"],
            experiences=["scuba_diving", "snorkeling", "marine_safari", "wildlife", "unique_biome"],
            accommodation=["eco_lodge", "glamping"],
            context_tags=["off_beaten_path", "value_for_money", "bucket_list", "authentic"],
            best_months=["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
        ),
        Destination(
            id="raja-ampat-idn",
            name="Raja Ampat",
            country="Indonesia",
            region="West Papua",
            latitude=-0.5000,
            longitude=130.5000,
            destination_type="island",
            rarity_score=10,
            fauna=["manta_ray", "whale_shark", "sea_turtle", "dolphin"],
            experiences=["scuba_diving", "snorkeling", "coral_reef", "unique_biome", "wildlife"],
            accommodation=["eco_lodge", "overwater_bungalow"],
            context_tags=["bucket_list", "exclusive", "hidden_gem", "sustainable"],
            best_months=["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
        ),
        Destination(
            id="komodo-idn",
            name="Komodo National Park",
            country="Indonesia",
            region="East Nusa Tenggara",
            latitude=-8.5500,
            longitude=119.4833,
            destination_type="island",
            rarity_score=9,
            fauna=["komodo_dragon", "manta_ray", "dolphin", "sea_turtle"],
            experiences=["wildlife", "scuba_diving", "snorkeling", "trekking", "unique_biome"],
            accommodation=["eco_lodge"],
            context_tags=["bucket_list", "adventure", "authentic"],
            best_months=["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
        ),
        Destination(
            id="socorro-mex",
            name="Revillagigedo (Socorro)",
            country="Mexico",
            region="Pacific Ocean",
            latitude=18.7500,
            longitude=-110.9500,
            destination_type="island",
            rarity_score=10,
            fauna=["whale_shark", "manta_ray", "whale", "dolphin"],
            experiences=["scuba_diving", "marine_safari", "wildlife", "unique_biome"],
            accommodation=["eco_lodge"],
            context_tags=["exclusive", "bucket_list", "remote", "adventure"],
            best_months=["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"]
        ),
        Destination(
            id="galapagos-ecu",
            name="Galapagos Islands",
            country="Ecuador",
            region="Pacific Ocean",
            latitude=-0.9538,
            longitude=-90.9656,
            destination_type="island",
            rarity_score=10,
            fauna=["whale_shark", "sea_turtle", "penguin", "dolphin"],
            experiences=["wildlife", "scuba_diving", "snorkeling", "unique_biome", "volcano"],
            accommodation=["eco_lodge"],
            context_tags=["bucket_list", "sustainable", "exclusive", "authentic"],
            best_months=["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        ),

        # SAFARI / WILDLIFE
        Destination(
            id="masai-mara-ken",
            name="Masai Mara",
            country="Kenya",
            region="Narok County",
            latitude=-1.5021,
            longitude=35.1446,
            destination_type="safari",
            rarity_score=9,
            fauna=["lion", "elephant", "giraffe"],
            experiences=["safari", "wildlife", "unique_landscape", "unique_biome"],
            accommodation=["glamping", "eco_lodge"],
            context_tags=["bucket_list", "authentic", "adventure"],
            best_months=["Jul", "Aug", "Sep", "Oct"]
        ),
        Destination(
            id="serengeti-tza",
            name="Serengeti",
            country="Tanzania",
            region="Mara Region",
            latitude=-2.3333,
            longitude=34.8333,
            destination_type="safari",
            rarity_score=9,
            fauna=["lion", "elephant", "giraffe"],
            experiences=["safari", "wildlife", "unique_landscape", "unique_biome"],
            accommodation=["glamping", "eco_lodge"],
            context_tags=["bucket_list", "authentic", "exclusive"],
            best_months=["Jun", "Jul", "Aug", "Sep", "Oct"]
        ),
        Destination(
            id="okavango-bwa",
            name="Okavango Delta",
            country="Botswana",
            region="North-West District",
            latitude=-19.0000,
            longitude=22.5000,
            destination_type="safari",
            rarity_score=10,
            fauna=["elephant", "lion", "giraffe"],
            experiences=["safari", "wildlife", "unique_biome", "unique_landscape"],
            accommodation=["eco_lodge", "glamping"],
            context_tags=["exclusive", "bucket_list", "sustainable", "luxury"],
            best_months=["May", "Jun", "Jul", "Aug", "Sep", "Oct"]
        ),
        Destination(
            id="bwindi-uga",
            name="Bwindi Impenetrable Forest",
            country="Uganda",
            region="Kanungu District",
            latitude=-1.0500,
            longitude=29.6833,
            destination_type="forest",
            rarity_score=10,
            fauna=["gorilla"],
            experiences=["wildlife", "trekking", "rainforest", "unique_biome"],
            accommodation=["eco_lodge"],
            context_tags=["bucket_list", "exclusive", "authentic", "sustainable"],
            best_months=["Jun", "Jul", "Aug", "Sep", "Dec", "Jan", "Feb"]
        ),
        Destination(
            id="borneo-mys",
            name="Borneo Rainforest",
            country="Malaysia",
            region="Sabah / Sarawak",
            latitude=4.5000,
            longitude=117.0000,
            destination_type="forest",
            rarity_score=9,
            fauna=["orangutan", "elephant"],
            experiences=["wildlife", "rainforest", "trekking", "unique_biome"],
            accommodation=["eco_lodge", "treehouse"],
            context_tags=["off_beaten_path", "authentic", "sustainable", "adventure"],
            best_months=["Mar", "Apr", "May", "Sep", "Oct"]
        ),

        # EXTREME LANDSCAPES / RARE NATURE
        Destination(
            id="atacama-chl",
            name="Atacama Desert",
            country="Chile",
            region="Antofagasta",
            latitude=-23.8634,
            longitude=-67.5232,
            destination_type="desert",
            rarity_score=10,
            fauna=[],
            experiences=["stargazing", "desert", "unique_landscape", "volcano", "hot_springs", "eclipse"],
            accommodation=["glamping", "eco_lodge"],
            context_tags=["bucket_list", "exclusive", "remote", "adventure"],
            best_months=["Mar", "Apr", "May", "Sep", "Oct", "Nov"]
        ),
        Destination(
            id="salar-uyuni-bol",
            name="Salar de Uyuni",
            country="Bolivia",
            region="Potosi",
            latitude=-20.1338,
            longitude=-67.4891,
            destination_type="desert",
            rarity_score=10,
            fauna=[],
            experiences=["unique_landscape", "desert", "stargazing"],
            accommodation=["eco_lodge"],
            context_tags=["bucket_list", "value_for_money", "adventure", "hidden_gem"],
            best_months=["May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
        ),
        Destination(
            id="svalbard-nor",
            name="Svalbard",
            country="Norway",
            region="Arctic",
            latitude=78.2253,
            longitude=15.6267,
            destination_type="arctic",
            rarity_score=10,
            fauna=["polar_bear", "whale"],
            experiences=["wildlife", "aurora_borealis", "glacier", "unique_landscape"],
            accommodation=["ice_hotel", "eco_lodge"],
            context_tags=["bucket_list", "exclusive", "remote", "adventure"],
            best_months=["Feb", "Mar", "Apr", "Sep", "Oct", "Nov"]
        ),
        Destination(
            id="tromso-nor",
            name="Tromso",
            country="Norway",
            region="Troms og Finnmark",
            latitude=69.6496,
            longitude=18.9560,
            destination_type="arctic",
            rarity_score=8,
            fauna=["whale"],
            experiences=["aurora_borealis", "wildlife", "fjord", "unique_landscape"],
            accommodation=["ice_hotel", "glamping"],
            context_tags=["bucket_list", "exclusive", "adventure"],
            best_months=["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
        ),
        Destination(
            id="iceland-ring",
            name="Iceland Ring Road",
            country="Iceland",
            region="Nationwide",
            latitude=64.9631,
            longitude=-19.0208,
            destination_type="mixed",
            rarity_score=9,
            fauna=["whale", "penguin"],
            experiences=["aurora_borealis", "glacier", "volcano", "hot_springs", "waterfall", "unique_landscape"],
            accommodation=["glamping", "eco_lodge"],
            context_tags=["bucket_list", "adventure", "authentic"],
            best_months=["Sep", "Oct", "Nov", "Feb", "Mar", "Jun", "Jul", "Aug"]
        ),
        Destination(
            id="patagonia-arg",
            name="Patagonia (El Chalten)",
            country="Argentina",
            region="Santa Cruz",
            latitude=-49.3314,
            longitude=-72.8867,
            destination_type="mountain",
            rarity_score=9,
            fauna=[],
            experiences=["glacier", "trekking", "mountain_climbing", "unique_landscape"],
            accommodation=["mountain_lodge", "glamping"],
            context_tags=["bucket_list", "adventure", "authentic", "value_for_money"],
            best_months=["Nov", "Dec", "Jan", "Feb", "Mar"]
        ),
        Destination(
            id="torres-paine-chl",
            name="Torres del Paine",
            country="Chile",
            region="Magallanes",
            latitude=-51.0000,
            longitude=-73.0000,
            destination_type="mountain",
            rarity_score=9,
            fauna=[],
            experiences=["glacier", "trekking", "unique_landscape", "wildlife"],
            accommodation=["mountain_lodge", "glamping", "eco_lodge"],
            context_tags=["bucket_list", "adventure", "sustainable"],
            best_months=["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
        ),

        # UNIQUE ACCOMMODATIONS
        Destination(
            id="cappadocia-tur",
            name="Cappadocia",
            country="Turkey",
            region="Nevsehir",
            latitude=38.6431,
            longitude=34.8287,
            destination_type="desert",
            rarity_score=8,
            fauna=[],
            experiences=["unique_landscape", "hot_springs"],
            accommodation=["cave_hotel"],
            context_tags=["bucket_list", "authentic", "value_for_money", "hidden_gem"],
            best_months=["Apr", "May", "Jun", "Sep", "Oct"]
        ),
        Destination(
            id="scottish-highlands-gbr",
            name="Scottish Highlands",
            country="United Kingdom",
            region="Scotland",
            latitude=57.0000,
            longitude=-5.0000,
            destination_type="mountain",
            rarity_score=7,
            fauna=[],
            experiences=["unique_landscape", "trekking"],
            accommodation=["castle", "mountain_lodge"],
            context_tags=["authentic", "off_beaten_path", "adventure"],
            best_months=["May", "Jun", "Jul", "Aug", "Sep"]
        ),
        Destination(
            id="maldives-mdv",
            name="Maldives",
            country="Maldives",
            region="Indian Ocean",
            latitude=3.2028,
            longitude=73.2207,
            destination_type="island",
            rarity_score=8,
            fauna=["whale_shark", "manta_ray", "sea_turtle", "dolphin"],
            experiences=["scuba_diving", "snorkeling", "coral_reef", "bioluminescence"],
            accommodation=["overwater_bungalow", "eco_lodge"],
            context_tags=["luxury", "exclusive", "bucket_list"],
            best_months=["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
        ),

        # BIOLUMINESCENCE / RARE PHENOMENA
        Destination(
            id="vieques-pri",
            name="Vieques Bioluminescent Bay",
            country="Puerto Rico",
            region="Vieques Island",
            latitude=18.0953,
            longitude=-65.4475,
            destination_type="island",
            rarity_score=9,
            fauna=["sea_turtle"],
            experiences=["bioluminescence", "snorkeling", "wildlife"],
            accommodation=["eco_lodge"],
            context_tags=["hidden_gem", "bucket_list", "authentic"],
            best_months=["Jan", "Feb", "Mar", "Apr", "May", "Aug", "Sep", "Oct", "Nov", "Dec"]
        ),
        Destination(
            id="halong-bay-vnm",
            name="Ha Long Bay",
            country="Vietnam",
            region="Quang Ninh",
            latitude=20.9101,
            longitude=107.1839,
            destination_type="island",
            rarity_score=8,
            fauna=["dolphin"],
            experiences=["unique_landscape", "snorkeling", "bioluminescence"],
            accommodation=["eco_lodge"],
            context_tags=["bucket_list", "value_for_money", "authentic"],
            best_months=["Mar", "Apr", "May", "Sep", "Oct", "Nov"]
        ),

        # UNIQUE FJORDS & WATERFALLS
        Destination(
            id="milford-sound-nzl",
            name="Milford Sound",
            country="New Zealand",
            region="Fiordland",
            latitude=-44.6414,
            longitude=167.8971,
            destination_type="fjord",
            rarity_score=9,
            fauna=["dolphin", "penguin", "sea_turtle"],
            experiences=["fjord", "waterfall", "wildlife", "unique_landscape", "rainforest"],
            accommodation=["eco_lodge"],
            context_tags=["bucket_list", "adventure", "authentic"],
            best_months=["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
        ),
        Destination(
            id="iguazu-arg",
            name="Iguazu Falls",
            country="Argentina/Brazil",
            region="Misiones / Parana",
            latitude=-25.6953,
            longitude=-54.4367,
            destination_type="forest",
            rarity_score=9,
            fauna=[],
            experiences=["waterfall", "rainforest", "wildlife", "unique_landscape"],
            accommodation=["eco_lodge"],
            context_tags=["bucket_list", "value_for_money", "adventure"],
            best_months=["Mar", "Apr", "May", "Aug", "Sep", "Oct", "Nov"]
        ),
        Destination(
            id="victoria-falls-zmb",
            name="Victoria Falls",
            country="Zambia/Zimbabwe",
            region="Livingstone / Vic Falls",
            latitude=-17.9243,
            longitude=25.8572,
            destination_type="forest",
            rarity_score=9,
            fauna=["elephant"],
            experiences=["waterfall", "safari", "wildlife", "unique_landscape"],
            accommodation=["eco_lodge", "glamping"],
            context_tags=["bucket_list", "adventure", "authentic"],
            best_months=["Feb", "Mar", "Apr", "May", "Jun", "Jul"]
        ),

        # VOLCANIC & GEOTHERMAL
        Destination(
            id="kamchatka-rus",
            name="Kamchatka Peninsula",
            country="Russia",
            region="Far East",
            latitude=53.0000,
            longitude=158.0000,
            destination_type="volcanic",
            rarity_score=10,
            fauna=["polar_bear", "whale"],
            experiences=["volcano", "hot_springs", "wildlife", "unique_landscape", "glacier"],
            accommodation=["eco_lodge", "glamping"],
            context_tags=["exclusive", "remote", "adventure", "hidden_gem", "bucket_list"],
            best_months=["Jun", "Jul", "Aug", "Sep"]
        ),
        Destination(
            id="azores-prt",
            name="Azores Islands",
            country="Portugal",
            region="Atlantic Ocean",
            latitude=37.7833,
            longitude=-25.5000,
            destination_type="island",
            rarity_score=8,
            fauna=["whale", "dolphin"],
            experiences=["volcano", "hot_springs", "wildlife", "unique_landscape", "scuba_diving"],
            accommodation=["eco_lodge"],
            context_tags=["hidden_gem", "value_for_money", "authentic", "sustainable"],
            best_months=["May", "Jun", "Jul", "Aug", "Sep", "Oct"]
        ),

        # RAINFOREST / BIODIVERSITY
        Destination(
            id="amazon-bra",
            name="Amazon Rainforest",
            country="Brazil",
            region="Amazonas",
            latitude=-3.4653,
            longitude=-62.2159,
            destination_type="forest",
            rarity_score=9,
            fauna=["dolphin"],
            experiences=["rainforest", "wildlife", "unique_biome"],
            accommodation=["eco_lodge", "treehouse"],
            context_tags=["bucket_list", "adventure", "authentic", "sustainable"],
            best_months=["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
        ),
        Destination(
            id="costa-rica-osa",
            name="Osa Peninsula",
            country="Costa Rica",
            region="Puntarenas",
            latitude=8.5000,
            longitude=-83.5000,
            destination_type="forest",
            rarity_score=9,
            fauna=["whale", "dolphin", "sea_turtle"],
            experiences=["rainforest", "wildlife", "scuba_diving", "unique_biome"],
            accommodation=["eco_lodge", "treehouse"],
            context_tags=["hidden_gem", "sustainable", "adventure", "authentic"],
            best_months=["Dec", "Jan", "Feb", "Mar", "Apr"]
        ),
    ]


def export_to_csv(destinations: List[Destination], output_path: Path) -> str:
    """Export destinations to CSV format."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    fieldnames = [
        "id", "name", "country", "region", "latitude", "longitude",
        "destination_type", "rarity_score",
        "fauna", "experiences", "accommodation", "context_tags", "best_months",
        "keywords_pt", "keywords_en", "keywords_es", "keywords_fr",
        "keywords_hi", "keywords_zh", "keywords_ar", "keywords_ru"
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for dest in destinations:
            row = asdict(dest)
            # Convert lists to pipe-separated strings
            row["fauna"] = "|".join(dest.fauna)
            row["experiences"] = "|".join(dest.experiences)
            row["accommodation"] = "|".join(dest.accommodation)
            row["context_tags"] = "|".join(dest.context_tags)
            row["best_months"] = "|".join(dest.best_months)
            writer.writerow(row)

    return str(output_path)


def export_to_json(destinations: List[Destination], output_path: Path) -> str:
    """Export destinations to JSON format."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_destinations": len(destinations),
            "languages": LANGUAGES,
            "purpose": "Multilingual destination keyword vectors for global travel discovery"
        },
        "destinations": [asdict(d) for d in destinations]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(output_path)


def main():
    """Main entry point."""
    print("=" * 60)
    print("Multilingual Destination Keywords Generator")
    print("=" * 60)

    # Initialize generator
    generator = MultilingualKeywordGenerator()
    print(f"Loaded vocabulary from: {KEYWORDS_FILE}")

    # Get sample destinations
    destinations = get_sample_destinations()
    print(f"Processing {len(destinations)} destinations...")

    # Process each destination
    processed = []
    for dest in destinations:
        processed_dest = generator.process_destination(dest)
        processed.append(processed_dest)
        print(f"  [OK] {dest.name}, {dest.country}")

    # Export to CSV
    csv_path = OUTPUT_DIR / "multilingual_destinations.csv"
    export_to_csv(processed, csv_path)
    print(f"\nCSV exported to: {csv_path}")

    # Export to JSON
    json_path = OUTPUT_DIR / "multilingual_destinations.json"
    export_to_json(processed, json_path)
    print(f"JSON exported to: {json_path}")

    # Print sample output
    print("\n" + "=" * 60)
    print("SAMPLE OUTPUT: Tofo Beach, Mozambique")
    print("=" * 60)
    tofo = processed[0]
    print(f"\nKeywords_PT: {tofo.keywords_pt}")
    print(f"\nKeywords_EN: {tofo.keywords_en}")
    print(f"\nKeywords_ES: {tofo.keywords_es}")
    print(f"\nKeywords_ZH: {tofo.keywords_zh}")
    print(f"\nKeywords_AR: {tofo.keywords_ar}")
    print(f"\nKeywords_RU: {tofo.keywords_ru}")

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"\nFiles generated:")
    print(f"  1. {csv_path}")
    print(f"  2. {json_path}")
    print(f"\nImport the CSV into:")
    print(f"  - Google Sheets / Excel")
    print(f"  - Notion (Database import)")
    print(f"  - Airtable (CSV import)")


if __name__ == "__main__":
    main()
