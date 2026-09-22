import os
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from pages.models import CollaboratingEntity, TeamMember


class Command(BaseCommand):
    help = "Import legacy static team images into the configured media storage for ImageField references."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Only report what would be imported.")

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        static_root = Path(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else Path("/app/static")
        imported = []
        skipped = []
        missing = []

        def resolve_legacy_path(value):
            if not value:
                return None
            relative = value.strip().lstrip("/")
            if relative.startswith("img/"):
                candidate = static_root / relative
                if candidate.exists():
                    return candidate
            candidate = static_root / "img" / Path(relative).name
            if candidate.exists():
                return candidate
            return static_root / relative

        for member in TeamMember.objects.all():
            field_name = "photo"
            current = getattr(member, field_name, None)
            if current and current.name and current.storage.exists(current.name):
                skipped.append(("TeamMember", member.pk, field_name, "already_has_valid_file"))
                continue

            legacy_name = (current.name if current and current.name else "").strip()
            if not legacy_name:
                skipped.append(("TeamMember", member.pk, field_name, "empty"))
                continue

            legacy_path = resolve_legacy_path(legacy_name)
            if not legacy_path or not legacy_path.exists():
                missing.append(("TeamMember", member.pk, field_name, legacy_name))
                continue

            if dry_run:
                imported.append(("TeamMember", member.pk, field_name, legacy_name))
                continue

            with legacy_path.open("rb") as fh:
                content = fh.read()

            if not content:
                missing.append(("TeamMember", member.pk, field_name, legacy_name))
                continue

            field_file = ContentFile(content, name=legacy_name)
            current.save(legacy_name, field_file, save=True)
            imported.append(("TeamMember", member.pk, field_name, legacy_name))

        for entity in CollaboratingEntity.objects.all():
            field_name = "logo"
            current = getattr(entity, field_name, None)
            if current and current.name and current.storage.exists(current.name):
                skipped.append(("CollaboratingEntity", entity.pk, field_name, "already_has_valid_file"))
                continue

            legacy_name = (current.name if current and current.name else "").strip()
            if not legacy_name:
                skipped.append(("CollaboratingEntity", entity.pk, field_name, "empty"))
                continue

            legacy_path = resolve_legacy_path(legacy_name)
            if not legacy_path or not legacy_path.exists():
                missing.append(("CollaboratingEntity", entity.pk, field_name, legacy_name))
                continue

            if dry_run:
                imported.append(("CollaboratingEntity", entity.pk, field_name, legacy_name))
                continue

            with legacy_path.open("rb") as fh:
                content = fh.read()

            if not content:
                missing.append(("CollaboratingEntity", entity.pk, field_name, legacy_name))
                continue

            field_file = ContentFile(content, name=legacy_name)
            current.save(legacy_name, field_file, save=True)
            imported.append(("CollaboratingEntity", entity.pk, field_name, legacy_name))

        self.stdout.write(self.style.SUCCESS(f"Imported: {len(imported)}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {len(skipped)}"))
        self.stdout.write(self.style.ERROR(f"Missing: {len(missing)}"))

        for item in imported:
            self.stdout.write(f"IMPORTED {item[0]} #{item[1]} {item[2]} -> {item[3]}")
        for item in skipped:
            self.stdout.write(f"SKIPPED {item[0]} #{item[1]} {item[2]} -> {item[3]}")
        for item in missing:
            self.stdout.write(f"MISSING {item[0]} #{item[1]} {item[2]} -> {item[3]}")
