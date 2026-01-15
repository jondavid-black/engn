# Engn CLI

The `engn` CLI provides core utilities for engineering and program management baselines within the Digital Engine suite.

## Usage

### Check Version

```bash
engn --version
```

### Initialize Project

Initialize a new `engn` project in the current directory:

```bash
engn init
```

Initialize a new `engn` project in a specific directory:

```bash
engn init my_project
```

Initialize a project non-interactively using command-line flags:

```bash
engn init my_project --name "My Project" --language "SysML v2" --strategy "unified python"
```

This command creates the following structure:
- `engn.jsonl`: Core configuration and data file (contains `ProjectConfig` and imported modules)
- `mbse/`: Model-Based System Engineering artifacts directory
- `pm/`: Program management artifacts directory

#### Initialization Options

- `--name`: The printable name of the project (e.g., "My Satellite Project").
- `--language`: The MBSE language to be used (e.g., "SysML v2").
- `--strategy`: The implementation strategy (e.g., "unified python", "python backend / typescript frontend").

