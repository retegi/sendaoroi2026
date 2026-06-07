def can_access_rosetta(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
