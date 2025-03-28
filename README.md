# eICR Anonymization Tool
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[!CAUTION]
This tool should be considered to be in an early **alpha** (not feature complete) state. At this stage you should assume sensitive data will be missed, or otherwise inappropaitely removed or replaced. Every anonimyzed eICR should be thorughly checked for sensitive data.

## Overview
This tool removes and replaces sensitive data in eICR XML files with Star Wars–themed fake data. The aim is to preserve the original structure, formatting, and relationships found in real-world eICRs so that the resulting files can still be useful for testing and development. By replacing data with plausible but clearly fictitious values, it becomes possible to share eICRs for troubleshooting or collaboration without exposing private information.

### Problem Scope
Electronic Initial Case Reports (eICRs) contain sensitive patient information that cannot be shared or used freely for development and testing without serious privacy precautions. While fabricated eICRs can be used, these often fail to capture the quirks and irregularities of real data. As a result:

- Developers must make assumptions when working solely with fabricated examples, potentially missing real-world edge cases.
- Users experiencing issues cannot safely share the exact eICRs related to the problem if those files.
- Simple anonymization methods often remove or alter key data patterns and formatting, inadvertently making the files less representative of real-world data or otherwise unusable.

There is a need for a tool that removes or replaces sensitive data while preserving as much of the original “flavor” of the document as possible, adhering to anonymization best practices without sacrificing realism.

### Goals
The tool is designed around the following principles and requirements, in approximate order of importance:
1. **Adhere to De-identification Best Practises**
   - The resulting eICR document should at the least satisfy the [Safe Harbor method of de-identification](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html#safeharborguidance).
2. **Plausible Yet Clearly Fake Data:**
   - Substituted information should look realistic enough to test real-world scenarios but still be obviously fictional to avoid confusion with actual, sensitive data.
3. **Preserve Formatting:**
   - Maintain case, including uppercase, lowercase, and titlecase.
   - Keep whitespace, including leading and trailing spaces.
   - Retain punctuation, symbols, and other special characters.
4. **Consistent Replacement:**
   - Whenever the same value appears multiple times it should be replaced by the same placeholder each time.
   - This includes when a value is formatted differently across instances.

## How to Use

### Requirements

#### Required
- [Python version >= 3.7](https://www.python.org/)
- [Pip (should be installed along side Python)](http://pip.pypa.io/en/stable/)

#### Reccomended
If using the anonymization tool as a command line tool, outside of a Python virtual enviroment it is reccomended to use [Pipx](https://pipx.pypa.io/stable/) to avoid dependency conflicts.

### Installation
1. Download the wheel (.whl) file from the release page
2. Install:
   - With Pip:
   ```bash
   pip install anonymize_eicr.whl
   ```
    - With Pipx:
   ```bash
   pipx install anonymize_eicr.whl
   ```

### Use
#### Basic Usage
```bash
anonymize_eicr /path/to/eicrs
```
This will create a copy of each eicr file with prepended with `.anonimized.xml` in the same directory given

#### Help
```bash
anonymize --help
usage: anonymize [-h] [--debug] input_location

Anonymize eICR XML files.

positional arguments:
  input_location  Directory containing eICR XML files.

options:
  -h, --help      show this help message and exit
  --debug, -d     Print table showing original and replacement tags. Will show sensitive information.
```

## Development


<!-- Sections left -->
## Example
## Development
### Testing
### Debugging
## Use
### Download/Install
### Run
## Future Features
## Safe Harbor Method Overview