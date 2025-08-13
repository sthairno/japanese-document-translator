# Japanese Document Translator

A tool for translating Japanese Markdown files to English. It utilizes legal and technical terminology dictionaries to generate accurate translations.

## Setup

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd japanese-document-translator
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. Place Japanese Markdown files you want to translate in the `notes/` directory.

2. Run the script:
```bash
python3 main.py
```

3. Translation prompt files will be generated in the `prompts/` directory.

4. Paste the generated prompt into ChatGPT or Cursor

### Directory Structure

```
japanese-document-translator/
├── main.py          # Main script
├── requirements.txt # Dependencies
├── notes/           # Source Japanese Markdown files
│   └── *.md
├── prompts/         # Generated translation prompt files
│   └── *.md
└── dictionary/      # Dictionary files
    ├── law.je.dic.18.0.xml # Legal terminology dictionary
    └── custom.xml          # Custom dictionary
```

### Dictionary Configuration

#### Adding Custom Dictionary

You can add custom dictionary entries to the `dictionary/custom.xml` file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Dictionary Version="16.0">
    <Entry>
        <Word>専門用語</Word>
        <Trans>
            <TransWord>Technical Term</TransWord>
            <Usage>Context</Usage>
            <Note1>Additional note 1</Note1>
            <Note2>Additional note 2</Note2>
        </Trans>
    </Entry>
</Dictionary>
```

#### Dictionary Entry Structure

- `Word`: Japanese word
- `TransWord`: English translation
- `Usage`: Usage context or situation (optional)
- `Note1`, `Note2`: Additional notes (optional)

## License

### `dictionary/law.je.dic.18.0.xml`

This dictionary data was downloaded from [Japanese Law Translation](https://www.japaneselawtranslation.go.jp/en/dicts/download) and is used under the [Public Data License (Version 1.0)](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0).
