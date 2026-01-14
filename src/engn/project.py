import shutil
import subprocess
from pathlib import Path


def init_project_structure(target_path: Path) -> None:
    """
    Initialize an existing directory with engn and beads structures.
    """
    if not target_path.exists():
        target_path.mkdir(parents=True)

    # Create standard engn directories
    for dir_name in ["arch", "pm"]:
        (target_path / dir_name).mkdir(exist_ok=True)

    # Create engn.jsonl if it doesn't exist
    config_path = target_path / "engn.jsonl"
    if not config_path.exists():
        import json

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "engn_type": "type_def",
                        "name": "ProjectConfig",
                        "properties": [
                            {"name": "pm_path", "type": "str", "default": "pm"},
                            {"name": "sysengn_path", "type": "str", "default": "arch"},
                        ],
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "engn_type": "ProjectConfig",
                        "pm_path": "pm",
                        "sysengn_path": "arch",
                    }
                )
                + "\n"
            )

    # Initialize beads (bd) if installed and not already present
    if shutil.which("bd"):
        if not (target_path / ".beads").exists():
            try:
                subprocess.run(["bd", "init"], cwd=target_path, check=True)
                print("Initialized beads for issue tracking")
            except subprocess.CalledProcessError:
                # If bd init fails (e.g. already initialized but .beads missing or other issues)
                # we just continue as it's a "best effort" in this function
                pass
    else:
        print("Warning: 'bd' (beads) not found. Issue tracking not initialized.")
