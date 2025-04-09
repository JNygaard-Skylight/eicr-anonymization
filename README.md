> [!IMPORTANT]
> **REPOSITORY ARCHIVED**  
> This repository has been archived and is no longer maintained here.
> 
> **The project has moved to an offical CDC repository: [https://github.com/CDCgov/eicr-anonymization](https://github.com/CDCgov/eicr-anonymization)**

# eICR Anonymization Tool
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)



> [!CAUTION]
> This tool should be considered in an early **alpha** (not feature complete) state. At this stage, you should assume sensitive data will be left in, or otherwise inappropriately removed or replaced. Every anonymized eICR should be thoroughly checked for sensitive data.

## Overview
This tool removes and replaces sensitive data in eICR XML files with fake Star Wars–themed data. Its aim is to preserve the original structure, formatting, and relationships in real-world eICRs so that the resulting files can still be helpful for testing and development. By replacing data with plausible but clearly fictitious values, it becomes possible to share eICRs for troubleshooting or collaboration without exposing private information.

### Problem Scope
Electronic Initial Case Reports (eICRs) contain sensitive patient information that cannot be shared or used freely for development and testing without serious privacy precautions. While fabricated eICRs can be used, these often fail to capture the quirks and irregularities of actual data. As a result:

- Developers must make assumptions when working solely with fabricated examples, potentially missing real-world edge cases.
- Users experiencing issues cannot safely share the exact eICRs related to the problem.
- Simple anonymization methods often remove or alter key data patterns and formatting, inadvertently making the files less representative of real-world data or otherwise unusable.

Therefore, there is a need for a tool that removes or replaces sensitive data while preserving as much of the document's original “flavor” as possible, adhering to anonymization best practices without sacrificing realism.

### Goals
The tool is designed around the following principles and requirements, in approximate order of importance:
1. **Adhere to De-Identification Best Practices**
   - The resulting eICR document should at least satisfy the [Safe Harbor method of de-identification](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html#safeharborguidance).
2. **Plausible Yet Clearly Fake Data:**
   - Substituted information should look realistic enough to test real-world scenarios but still be obviously fictional to avoid confusion with actual, sensitive data.
3. **Preserve Formatting:**
   - Maintain case, including uppercase, lowercase, and titlecase.
   - Keep whitespace, including leading and trailing spaces.
   - Retain punctuation, symbols, and other special characters.
4. **Consistent Replacement:**
   - Whenever the same value appears multiple times, it should be replaced by the same placeholder.
   - This includes when a value is formatted differently across instances.

## How to Use

### Requirements

#### Required
- [Python version >= 3.7](https://www.python.org/)
- [Pip (should be installed alongside Python)](http://pip.pypa.io/en/stable/)

#### Reccomended
If using the anonymization tool as a command-line tool outside of a Python virtual environment, it is recommended to use [Pipx](https://pipx.pypa.io/stable/) to avoid dependency conflicts.

### Installation
1. Clone this repo.
2. Install:
   At the root of the directory
   - With Pip:
   ```bash
   pip install .
   ```
    - With Pipx:
   ```bash
   pipx install .
   ```

### Use
#### Basic Usage
```bash
anonymize_eicr /path/to/eicrs
```
This will create a copy of each eicr file prepended with `.anonymized.xml` in the same directory.

#### Help
```bash
anonymize --help
usage: anonymize_eicr [-h] [--debug] input_location

Anonymize eICR XML files.

positional arguments:
  input_location  Directory containing eICR XML files.

options:
  -h, --help      show this help message and exit
  --debug, -d     Print table showing original and replacement tags. Will show sensitive information.
```
