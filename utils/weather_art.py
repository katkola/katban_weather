WEATHER_CATEGORIES = [
    (['thunderstorm', 'thunder', 't-storm', 'hail', 'tornado'], 'storm'),
    (['snow', 'sleet', 'ice', 'blizzard'], 'snow'),
    (['rain', 'shower', 'drizzle'], 'rain'),
    (['fog', 'haze', 'mist', 'smoke'], 'fog'),
    (['wind', 'breez', 'gust'], 'windy'),
]

CLOUD_CATEGORIES = [
    (['partly cloudy', 'partly sunny', 'mostly sunny'], 'partly_cloudy'),
    (['mostly cloudy', 'mostly clear'], 'cloudy'),
    (['cloudy', 'overcast'], 'cloudy'),
]

SYMBOLS = {
    'sunny':         '\U0001F324',
    'night':         '\U0001F319',
    'partly_cloudy': '\u26C5',
    'cloudy':        '\u2601',
    'rain':          '\U0001F327',
    'snow':          '\U0001F328',
    'storm':         '\u26C8',
    'fog':           '\U0001F32B',
    'windy':         '\U0001F4A8',
}

ARTS = {
    'sunny':         '\U0001F324',
    'night':         '\U0001F319',
    'partly_cloudy': '\u26C5',
    'cloudy':        '\u2601',
    'rain':          '\U0001F327',
    'snow':          '\U0001F328',
    'storm':         '\u26C8',
    'fog':           '\U0001F32B',
    'windy':         '\U0001F4A8',
}


def _is_night(period_name):
    if not period_name:
        return False
    name_lower = period_name.lower()
    return 'tonight' in name_lower or 'night' in name_lower


def _categorize(short_forecast, is_night=False):
    if not short_forecast:
        return 'night' if is_night else 'sunny'
    f = short_forecast.lower()

    for keywords, category in WEATHER_CATEGORIES:
        if any(kw in f for kw in keywords):
            return category

    for keywords, category in CLOUD_CATEGORIES:
        if any(kw in f for kw in keywords):
            return category

    if 'sunny' in f:
        return 'sunny'

    if 'clear' in f:
        return 'night' if is_night else 'sunny'

    return 'night' if is_night else 'sunny'


def get_weather_symbol(short_forecast, period_name=None):
    is_night = _is_night(period_name)
    category = _categorize(short_forecast, is_night)
    return SYMBOLS.get(category, '\u2600')


def get_current_weather_art(short_forecast, period_name=None):
    is_night = _is_night(period_name)
    category = _categorize(short_forecast, is_night)
    return ARTS.get(category, ARTS['sunny'])
