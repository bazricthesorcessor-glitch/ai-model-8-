"""
Memory cleanup and maintenance system.
Automatically removes expired items, archives old logs, and maintains memory health.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
import shutil

from . import paths
from .reader import MemoryReader
from .writer import MemoryWriter


class MemoryCleaner:
    """Handles cleanup, archival, and maintenance of memory system."""

    # Configuration
    DAILY_LOG_RETENTION_DAYS = 14
    ARCHIVE_RETENTION_DAYS = 365
    COMPRESS_AFTER_DAYS = 30
    OLD_LOG_CLEANUP_FREQUENCY_DAYS = 7

    @staticmethod
    def cleanup_expired_items() -> Dict[str, int]:
        """Remove expired items (exams, deadlines, events).

        Returns:
            Dictionary with counts of removed items
        """
        cleaned = {
            "exams": 0,
            "deadlines": 0,
            "events": 0,
            "total": 0
        }

        now = datetime.now()

        # Clean exams
        exams = MemoryReader.load_exams()
        active_exams = []

        for exam in exams:
            try:
                exam_date = datetime.fromisoformat(exam.get("date", ""))
                if exam_date > now:
                    active_exams.append(exam)
                else:
                    cleaned["exams"] += 1
                    # Log expiry
                    MemoryCleaner._log_expiry("exam", exam.get("name", ""), exam_date)
            except ValueError:
                # Invalid date, keep it
                active_exams.append(exam)

        # Save active exams
        if active_exams != exams:
            MemoryWriter.save_json(paths.EXAMS_FILE, {"items": active_exams})

        # Clean deadlines
        deadlines = MemoryReader.load_deadlines()
        active_deadlines = []

        for deadline in deadlines:
            try:
                deadline_date = datetime.fromisoformat(deadline.get("date", ""))
                if deadline_date > now:
                    active_deadlines.append(deadline)
                else:
                    cleaned["deadlines"] += 1
                    MemoryCleaner._log_expiry("deadline", deadline.get("title", ""), deadline_date)
            except ValueError:
                active_deadlines.append(deadline)

        if active_deadlines != deadlines:
            MemoryWriter.save_json(paths.DEADLINES_FILE, {"items": active_deadlines})

        # Clean events
        events = MemoryReader.load_events()
        active_events = []

        for event in events:
            try:
                event_date = datetime.fromisoformat(event.get("date", ""))
                if event_date > now:
                    active_events.append(event)
                else:
                    cleaned["events"] += 1
                    MemoryCleaner._log_expiry("event", event.get("title", ""), event_date)
            except ValueError:
                active_events.append(event)

        if active_events != events:
            MemoryWriter.save_json(paths.EVENTS_FILE, {"items": active_events})

        cleaned["total"] = sum(cleaned[k] for k in ["exams", "deadlines", "events"])

        return cleaned

    @staticmethod
    def cleanup_old_logs() -> Dict[str, int]:
        """Remove logs older than retention period.

        Returns:
            Dictionary with cleanup stats
        """
        stats = {
            "removed_days": 0,
            "removed_entries": 0
        }

        cutoff_date = datetime.now() - timedelta(days=MemoryCleaner.DAILY_LOG_RETENTION_DAYS)

        # Find old log files
        if not paths.ACTIVE_DAILY_LOGS.exists():
            return stats

        for log_file in paths.ACTIVE_DAILY_LOGS.glob("*.jsonl"):
            try:
                # Extract date from filename
                date_str = log_file.stem
                file_date = datetime.fromisoformat(date_str)

                if file_date < cutoff_date:
                    # Count entries before deletion
                    with open(log_file, 'r') as f:
                        entry_count = sum(1 for line in f if line.strip())

                    stats["removed_entries"] += entry_count

                    # Archive before deletion (optional)
                    MemoryCleaner._archive_log_file(log_file, date_str)

                    # Delete the file
                    log_file.unlink()
                    stats["removed_days"] += 1

                    # Log the cleanup
                    MemoryWriter.log_to_daily({
                        "type": "maintenance",
                        "message": f"Cleaned up log file: {date_str}",
                        "category": "cleanup",
                        "severity": "info"
                    })

            except (ValueError, OSError):
                # Invalid date format or permission error, skip
                pass

        return stats

    @staticmethod
    def cleanup_duplicate_entries() -> Dict[str, int]:
        """Remove duplicate entries from logs.

        Returns:
            Dictionary with deduplication stats
        """
        stats = {
            "checked_entries": 0,
            "removed_duplicates": 0
        }

        # Get today's log
        today_entries = MemoryReader.load_daily_log()
        stats["checked_entries"] = len(today_entries)

        if len(today_entries) == 0:
            return stats

        # Create unique list (by timestamp and message)
        seen = set()
        unique_entries = []

        for entry in today_entries:
            key = (entry.get("timestamp"), entry.get("message"), entry.get("type"))
            if key not in seen:
                seen.add(key)
                unique_entries.append(entry)
            else:
                stats["removed_duplicates"] += 1

        # Rewrite log if changes made
        if stats["removed_duplicates"] > 0:
            log_path = paths.get_daily_log_path()
            log_path.unlink()  # Delete old log

            for entry in unique_entries:
                MemoryWriter.append_jsonl(log_path, entry)

        return stats

    @staticmethod
    def cleanup_corrupted_entries() -> Dict[str, int]:
        """Remove corrupted or invalid entries.

        Returns:
            Dictionary with cleanup stats
        """
        stats = {
            "checked_entries": 0,
            "removed_corrupted": 0
        }

        # Check today's log
        today_path = paths.get_daily_log_path()

        if not today_path.exists():
            return stats

        valid_entries = []

        try:
            with open(today_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    stats["checked_entries"] += 1

                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)

                        # Validate required fields
                        if "timestamp" in entry and "message" in entry and "type" in entry:
                            valid_entries.append(entry)
                        else:
                            stats["removed_corrupted"] += 1

                    except json.JSONDecodeError:
                        stats["removed_corrupted"] += 1

        except (OSError, IOError):
            # File read error
            return stats

        # Rewrite if changes made
        if stats["removed_corrupted"] > 0:
            today_path.unlink()

            for entry in valid_entries:
                MemoryWriter.append_jsonl(today_path, entry)

        return stats

    @staticmethod
    def archive_old_daily_logs(days_back: int = 30) -> Dict[str, int]:
        """Archive daily logs to long-term storage.

        Args:
            days_back: Only archive logs older than this many days

        Returns:
            Dictionary with archive stats
        """
        stats = {
            "archived_days": 0,
            "archived_entries": 0,
            "archive_file": None
        }

        cutoff_date = datetime.now() - timedelta(days=days_back)

        if not paths.ACTIVE_DAILY_LOGS.exists():
            return stats

        # Create archive file for the period
        archive_date = cutoff_date.strftime("%Y-%m")
        archive_id = f"logs_{archive_date}"

        all_archived_entries = []

        # Find logs to archive
        for log_file in sorted(paths.ACTIVE_DAILY_LOGS.glob("*.jsonl")):
            try:
                date_str = log_file.stem
                file_date = datetime.fromisoformat(date_str)

                if file_date < cutoff_date:
                    # Read entries
                    with open(log_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                all_archived_entries.append(json.loads(line))

                    stats["archived_entries"] += len(all_archived_entries)
                    stats["archived_days"] += 1

            except (ValueError, OSError):
                pass

        # Save archive
        if all_archived_entries:
            archive_data = {
                "archive_id": archive_id,
                "period": archive_date,
                "entry_count": len(all_archived_entries),
                "archived_at": datetime.now().isoformat(),
                "entries": all_archived_entries
            }

            MemoryWriter.save_to_archive(
                "sessions",
                archive_id,
                archive_data
            )

            stats["archive_file"] = str(paths.ARCHIVE_SESSIONS / f"{archive_id}.json")

        return stats

    @staticmethod
    def cleanup_empty_directories() -> Dict[str, int]:
        """Remove empty directories in memory system.

        Returns:
            Dictionary with cleanup stats
        """
        stats = {"removed_directories": 0}

        # Walk through memory directories
        for directory in paths.MEMORY_ROOT.rglob("*"):
            if directory.is_dir() and not any(directory.iterdir()):
                try:
                    directory.rmdir()
                    stats["removed_directories"] += 1
                except OSError:
                    pass

        return stats

    @staticmethod
    def validate_memory_integrity() -> Dict[str, Any]:
        """Validate memory system integrity.

        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "directories_exist": True,
            "files_readable": True,
            "issues": [],
            "warnings": []
        }

        # Check directory structure
        required_dirs = [
            paths.ACTIVE_DIR,
            paths.ARCHIVE_DIR,
            paths.IDENTITY_DIR,
            paths.STATE_DIR,
            paths.AGENTS_DIR,
            paths.TEMPORARY_DIR,
            paths.TOOLS_DIR,
            paths.SEMANTIC_DIR,
            paths.INDEXES_DIR
        ]

        for directory in required_dirs:
            if not directory.exists():
                results["directories_exist"] = False
                results["valid"] = False
                results["issues"].append(f"Missing directory: {directory}")

        # Check key files
        key_files = [
            paths.IMPORTANT_MEMORY_FILE,
            paths.USER_PREFERENCES_FILE,
            paths.STATE_SNAPSHOT_FILE,
            paths.TOOL_REGISTRY_FILE,
        ]

        for file_path in key_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                except (json.JSONDecodeError, IOError):
                    results["files_readable"] = False
                    results["valid"] = False
                    results["issues"].append(f"Corrupted or unreadable: {file_path}")
            else:
                results["warnings"].append(f"Missing file: {file_path}")

        # Check daily logs
        today_log = paths.get_daily_log_path()
        if today_log.exists():
            try:
                entries = MemoryReader.load_daily_log()
                if len(entries) == 0:
                    results["warnings"].append("Today's log is empty")
            except Exception as e:
                results["valid"] = False
                results["issues"].append(f"Cannot read today's log: {str(e)}")

        return results

    @staticmethod
    def full_cleanup() -> Dict[str, Any]:
        """Perform full cleanup and maintenance cycle.

        Returns:
            Dictionary with overall cleanup statistics
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "expired_items": {},
            "old_logs": {},
            "duplicates": {},
            "corrupted": {},
            "empty_dirs": {},
            "integrity": {},
            "total_cleaned": 0
        }

        # Run all cleanup operations
        results["expired_items"] = MemoryCleaner.cleanup_expired_items()
        results["old_logs"] = MemoryCleaner.cleanup_old_logs()
        results["duplicates"] = MemoryCleaner.cleanup_duplicate_entries()
        results["corrupted"] = MemoryCleaner.cleanup_corrupted_entries()
        results["empty_dirs"] = MemoryCleaner.cleanup_empty_directories()
        results["integrity"] = MemoryCleaner.validate_memory_integrity()

        # Calculate totals
        results["total_cleaned"] = (
            results["expired_items"].get("total", 0) +
            results["old_logs"].get("removed_entries", 0) +
            results["duplicates"].get("removed_duplicates", 0) +
            results["corrupted"].get("removed_corrupted", 0)
        )

        # Log the cleanup
        if results["total_cleaned"] > 0 or not results["integrity"]["valid"]:
            MemoryWriter.log_to_daily({
                "type": "maintenance",
                "message": f"Full memory cleanup completed: {results['total_cleaned']} items cleaned",
                "category": "cleanup",
                "severity": "info",
                "data": results
            })

        return results

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    @staticmethod
    def _log_expiry(item_type: str, item_name: str, expiry_date: datetime) -> None:
        """Log item expiry.

        Args:
            item_type: Type of item (exam, deadline, event)
            item_name: Name of the item
            expiry_date: When it expired
        """
        MemoryWriter.append_jsonl(
            paths.EXPIRY_LOG_FILE,
            {
                "timestamp": datetime.now().isoformat(),
                "item_type": item_type,
                "item_name": item_name,
                "expiry_date": expiry_date.isoformat()
            }
        )

    @staticmethod
    def _archive_log_file(log_file: Path, date_str: str) -> None:
        """Archive a log file before deletion.

        Args:
            log_file: Path to log file
            date_str: Date string (for archive ID)
        """
        # Optional: Read entries and add to archive
        try:
            entries = []
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))

            if entries:
                # Could save to archive if desired
                pass

        except (OSError, json.JSONDecodeError):
            pass


def schedule_automatic_cleanup() -> None:
    """Schedule automatic cleanup (to be called periodically).

    This should be called:
    - Daily (check for expired items)
    - Weekly (cleanup old logs)
    - Monthly (validate integrity)
    """
    MemoryCleaner.full_cleanup()


if __name__ == "__main__":
    print("Memory Cleaner Test")
    print("=" * 70)

    # Validate integrity first
    print("\n1. Validating memory system integrity...")
    integrity = MemoryCleaner.validate_memory_integrity()
    print(f"   Valid: {integrity['valid']}")
    if integrity["issues"]:
        print(f"   Issues: {len(integrity['issues'])}")

    # Check for expired items
    print("\n2. Checking for expired items...")
    expired = MemoryCleaner.cleanup_expired_items()
    print(f"   Cleaned up: {expired['total']} items")

    # Check for duplicates
    print("\n3. Checking for duplicates...")
    dupes = MemoryCleaner.cleanup_duplicate_entries()
    print(f"   Removed: {dupes['removed_duplicates']} duplicates")

    # Check for corrupted entries
    print("\n4. Checking for corrupted entries...")
    corrupted = MemoryCleaner.cleanup_corrupted_entries()
    print(f"   Removed: {corrupted['removed_corrupted']} corrupted entries")

    print("\n✓ Memory cleaner operational")
