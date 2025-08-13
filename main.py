import re
from typing import TypedDict
import ahocorasick
import unicodedata
import xml.etree.ElementTree as ET
import os
import glob

class EnglishTranslation(TypedDict):
    translation: str
    usage: str | None
    notes: list[str]

class ValueType(TypedDict):
    word: str
    translations: list[EnglishTranslation]

class Ja2EnGlossaries:
    automaton: ahocorasick.Automaton

    def __init__(self):
        self.automaton = ahocorasick.Automaton()

    def load_file(self, filepath: str) -> None:
        with open(filepath, encoding="utf-8") as xmlfile:
            document = ET.parse(xmlfile)
            for entry_elem in document.findall("Entry"):
                word_elem = entry_elem.find("Word")
                assert word_elem is not None and word_elem.text is not None
                word = word_elem.text.strip()

                translations: list[EnglishTranslation] = []
                for translation_elem in entry_elem.findall("Trans"):
                    transword_elem = translation_elem.find("TransWord")
                    assert transword_elem is not None
                    if transword_elem.text is None:
                        continue
                    transword = transword_elem.text.strip()
            
                    usage_elem = translation_elem.find("Usage")
                    note1_elem = translation_elem.find("Note1")
                    note2_elem = translation_elem.find("Note2")

                    notes: list[str] = []
                    if note1_elem is not None and note1_elem.text is not None:
                        notes.append(note1_elem.text)
                    if note2_elem is not None and note2_elem.text is not None:
                        notes.append(note2_elem.text)

                    translations.append({
                        "translation": transword,
                        "usage": usage_elem.text if usage_elem is not None and usage_elem.text is not None else None,
                        "notes": notes
                    })

                key = unicodedata.normalize("NFKD", word)
                key = re.sub(r"\(.*?\)", "", key)
                if key in self.automaton:
                    data = self.automaton.get(key)
                    data["translations"] = translations
                else:
                    self.automaton.add_word(key, ValueType({
                        "word": word,
                        "translations": translations
                    }))
    
    def build(self) -> None:
        self.automaton.make_automaton()
    
    def find(self, text: str) -> list[ValueType]:
        text = unicodedata.normalize("NFKD", text)
        matches: dict[str, ValueType] = {}
        for (_, value) in self.automaton.iter_long(text):
            if value["word"] not in matches:
                matches[value["word"]] = value
        keys = list(matches.keys())
        keys.sort()
        return [matches[key] for key in keys]

glossaries = Ja2EnGlossaries()
glossaries.load_file("dictionary/law.je.dic.18.0.xml")
glossaries.load_file("dictionary/custom.xml")
glossaries.build()

def generate_prompt(input: str) -> str:
    global glossaries

    glossary_text = ""
    for match in glossaries.find(input):
        glossary_text += f"[{match['word']}]\n"
        translations = match["translations"]
        for i in range(len(translations)):
            translation = translations[i]
            glossary_text += f"{i + 1}. {translation['translation']}"
            if translation['usage'] is not None:
                glossary_text += f" ({translation['usage']})"
            glossary_text += "\n"
            for note in translation["notes"]:
                glossary_text += f"  {note}\n"
    glossary_text = glossary_text.strip()

    return f"""You are a quiet, reserved document translator. Please translate the following Japanese Markdown to English.

<instruction_for_agent>
【Translation Rules】
1. Preserve all Markdown syntax (#, *, `, ```, etc.) exactly
2. For interface elements, UI controls, and system-specific terms that users interact with, translate as "Translated English Text (`Original Japanese Text`)" to preserve the original Japanese context for users.
3. Use the following glossary for technical terms:
{glossary_text}

【Behavior Rules】
- Remain quiet and reserved — no greetings, acknowledgements, or conversational remarks.
- Do not include any questions, suggestions, or extra explanations.
- Output ONLY the translated Markdown, starting immediately with the content.

【Continuation Rule】
If output is cut off, continue exactly from the last word when the user types "Continue".
</instruction_for_agent>
<japanese_markdown>
{input}
</japanese_markdown>"""

if __name__ == "__main__":
    notes_dir = "notes"
    prompts_dir = "prompts"
    
    if not os.path.exists(prompts_dir):
        os.makedirs(prompts_dir)
    
    note_files = glob.glob(os.path.join(notes_dir, "*.md"))
    
    for note_file in note_files:
        filename = os.path.basename(note_file)
        prompt_file = os.path.join(prompts_dir, filename)
        
        # Skip if file with same name already exists in prompts directory
        if os.path.exists(prompt_file):
            print(f"Skipped: {filename} (already exists)")
            continue
        
        with open(note_file, 'r', encoding='utf-8') as f:
            input_content = f.read()
        
        prompt = generate_prompt(input_content)
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        print(f"Generated: {filename}")
