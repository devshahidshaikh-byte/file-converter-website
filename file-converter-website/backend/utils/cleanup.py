from pathlib import Path
import shutil
import time


# Temporary files older than this will be deleted.
CLEANUP_AFTER_HOURS = 1


def cleanup_directory(directory: str | Path) -> None:
    """
    Delete a directory and everything inside it.
    """

    directory = Path(directory)

    try:

        if directory.exists():
            shutil.rmtree(directory)

    except Exception as error:

        print(
            f"Cleanup failed for "
            f"{directory}: {error}"
        )


def cleanup_job(
    upload_directory: str | Path,
    output_directory: str | Path
) -> None:
    """
    Delete both upload and output directories.
    """

    cleanup_directory(upload_directory)
    cleanup_directory(output_directory)


def cleanup_old_files(
    upload_root: str | Path,
    output_root: str | Path
) -> None:
    """
    Delete temporary job folders that are older
    than CLEANUP_AFTER_HOURS.
    """

    upload_root = Path(upload_root)
    output_root = Path(output_root)

    cutoff_time = (
        time.time()
        - (CLEANUP_AFTER_HOURS * 60 * 60)
    )

    for root_directory in [
        upload_root,
        output_root
    ]:

        if not root_directory.exists():
            continue

        for item in root_directory.iterdir():

            try:

                if item.stat().st_mtime < cutoff_time:

                    if item.is_dir():

                        shutil.rmtree(item)

                    else:

                        item.unlink()

                    print(
                        f"Deleted old temporary item: "
                        f"{item}"
                    )

            except Exception as error:

                print(
                    f"Could not clean "
                    f"{item}: {error}"
                )