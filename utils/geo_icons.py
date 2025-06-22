# geo_icons.py

import os

# Ordnerstruktur für Wetter- und Vulkansymbole
WEATHER_ICON_PATH = "assets/weather_icons"
VOLCANO_ICON_PATH = "assets/volcano_icons"

# Zuordnung: Sentiment-Zustand → Wetter-Icon-Dateiname
WEATHER_ICONS = {
    "sunny": os.path.join(WEATHER_ICON_PATH, "sunny.png"),
    "cloudy": os.path.join(WEATHER_ICON_PATH, "cloudy.png"),
    "stormy": os.path.join(WEATHER_ICON_PATH, "stormy.png"),
    "rainy": os.path.join(WEATHER_ICON_PATH, "rainy.png"),
    "foggy": os.path.join(WEATHER_ICON_PATH, "foggy.png"),
}

# Zuordnung: Vulkanstufe → Vulkan-Icon-Dateiname
VOLCANO_ICONS = {
    "calm": os.path.join(VOLCANO_ICON_PATH, "volcano_calm.png"),
    "smoking": os.path.join(VOLCANO_ICON_PATH, "volcano_smoking.png"),
    "hot": os.path.join(VOLCANO_ICON_PATH, "volcano_hot.png"),
    "eruption": os.path.join(VOLCANO_ICON_PATH, "volcano_eruption.png"),
}


def get_volcano_icon_path(score: float) -> str:
    """
    Gibt den Dateinamen des passenden Vulkan-Icons zurück
    basierend auf dem durchschnittlichen Sentiment Score.
    """
    if score > 0.5:
        return "calm.png"
    elif score > 0.1:
        return "smoking.png"
    elif score > -0.3:
        return "hot.png"
    else:
        return "eruption.png"
