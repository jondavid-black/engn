import shutil
import subprocess
from pathlib import Path


def init_project_structure(
    target_path: Path,
    name: str = "New Project",
    mbse_language: str = "SysML v2",
    implementation_strategy: str = "unified python",
) -> None:
    """
    Initialize an existing directory with engn and beads structures.
    """
    if not target_path.exists():
        target_path.mkdir(parents=True)

    # Create standard engn directories
    for dir_name in ["mbse", "pm"]:
        (target_path / dir_name).mkdir(exist_ok=True)

    # Create engn.jsonl if it doesn't exist or update it
    config_path = target_path / "engn.jsonl"
    import json

    # Prepare lines for engn.jsonl
    # We want to preserve existing content but ensure ProjectConfig is present/updated
    lines = []
    type_def_found = False
    project_config_found = False

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if (
                    data.get("name") == "ProjectConfig"
                    and data.get("engn_type") == "type_def"
                ):
                    type_def_found = True
                    # Update type_def properties
                    data["properties"] = [
                        {"name": "name", "type": "str"},
                        {"name": "mbse_language", "type": "str"},
                        {"name": "implementation_strategy", "type": "str"},
                        {"name": "pm_path", "type": "str", "default": "pm"},
                        {"name": "sysengn_path", "type": "str", "default": "mbse"},
                    ]
                    lines.append(json.dumps(data))
                elif data.get("engn_type") == "ProjectConfig":
                    project_config_found = True
                    # Update instance
                    data["name"] = name
                    data["mbse_language"] = mbse_language
                    data["implementation_strategy"] = implementation_strategy
                    data["pm_path"] = data.get("pm_path", "pm")
                    data["sysengn_path"] = data.get("sysengn_path", "mbse")
                    lines.append(json.dumps(data))
                else:
                    lines.append(line)

    if not type_def_found:
        lines.insert(
            0,
            json.dumps(
                {
                    "engn_type": "type_def",
                    "name": "ProjectConfig",
                    "properties": [
                        {"name": "name", "type": "str"},
                        {"name": "mbse_language", "type": "str"},
                        {"name": "implementation_strategy", "type": "str"},
                        {"name": "pm_path", "type": "str", "default": "pm"},
                        {"name": "sysengn_path", "type": "str", "default": "mbse"},
                    ],
                }
            ),
        )

    if not project_config_found:
        lines.append(
            json.dumps(
                {
                    "engn_type": "ProjectConfig",
                    "name": name,
                    "mbse_language": mbse_language,
                    "implementation_strategy": implementation_strategy,
                    "pm_path": "pm",
                    "sysengn_path": "mbse",
                }
            )
        )

    with open(config_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    # Initialize beads (bd) if installed and not already present
    if shutil.which("bd"):
        if not (target_path / ".beads").exists():
            try:
                subprocess.run(["bd", "init"], cwd=target_path, check=True)
                print("Initialized beads for issue tracking")
            except subprocess.CalledProcessError:
                pass
    else:
        print("Warning: 'bd' (beads) not found. Issue tracking not initialized.")
