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

This command creates the following structure:
- `engn.toml`: Configuration file
- `arch/`: Architecture artifacts directory
- `pm/`: Program management artifacts directory
- `ux/`: User experience artifacts directory

