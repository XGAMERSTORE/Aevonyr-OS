"""Display-independent application search for Orbit."""
def matching_apps(apps, query):
    """Every word must match; an exact name and then a prefix rank first."""
    words = query.casefold().split()
    query = query.strip().casefold()
    matches = [app for app in apps if all(
        word in (app.name + ' ' + app.source).casefold() for word in words)]
    return sorted(matches, key=lambda app: (
        app.name.casefold() != query,
        not app.name.casefold().startswith(query), app.name.casefold()))

