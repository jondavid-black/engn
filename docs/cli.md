# CLI Reference

```
usage: main.py [-h] [--version] [-v] {init,check,print} ...

Digital Engine - The Intelligent Engine for Building Systems

positional arguments:
  {init,check,print}  Available commands
    init              Initialize an engn project in a directory
    check             Check validity of data files
    print             Print enums, data types, and data in human-readable form

options:
  -h, --help          show this help message and exit
  --version           Show the version and exit
  -v, --verbose       Show detailed error traces
```

## engn init

```
usage: main.py init [-h] [--name NAME] [--language LANGUAGE]
                    [--strategy STRATEGY]
                    [path]

positional arguments:
  path                 Path to initialize (default: current directory)

options:
  -h, --help           show this help message and exit
  --name NAME          Printable project name
  --language LANGUAGE  MBSE language (e.g. SysML v1, SysML v2)
  --strategy STRATEGY  Implementation strategy (e.g. unified python, unified
                       go)
```

## engn check

```
usage: main.py check [-h] [-v] [target]

positional arguments:
  target         Path to JSONL file or directory to check (default: check all
                 configured paths)

options:
  -h, --help     show this help message and exit
  -v, --verbose  Show detailed error traces
```

## engn print

```
usage: main.py print [-h] [-v] [target]

positional arguments:
  target         Path to JSONL file or directory to print (default: print all
                 configured paths)

options:
  -h, --help     show this help message and exit
  -v, --verbose  Show detailed error traces
```
