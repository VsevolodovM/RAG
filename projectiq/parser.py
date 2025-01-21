import os
import re
import json

INPUT_FOLDER = "documents"
OUTPUT_FOLDER = "output"

global_unique_id = 0


def extract_references(text, chapter_idx, section_name, paragraph_number):
    """
    Extracts references such as sections (denoted by §) from the given text.

    Args:
        text (str): The text to parse for references.
        chapter_idx (int): The current chapter index.
        section_name (str): The name of the section or chapter.
        paragraph_number (str): The paragraph number in the current section.

    Returns:
        list: A list of extracted references to sections (e.g., § X).
    """
    references = []

    section_references = re.findall(r"§\s*(\d+)", text)
    for section in section_references:
        references.append(f"§ {section}")

    unique_references = sorted(set(references), key=lambda x: int(re.search(r"\d+", x).group()))
    return unique_references


def clean_text_in_json(parsed_data):
    """
    Cleans up the 'Text' field in the parsed JSON data by removing unwanted \t and \n combinations.

    Args:
        parsed_data (list): List of dictionaries containing parsed legal text.

    Returns:
        list: Updated parsed data with cleaned 'Text' fields.
    """
    for item in parsed_data:
        if "Text" in item:
            item["Text"] = item["Text"].replace("\t", " ").replace("\n", " ")
            item["Text"] = re.sub(r'\s+', ' ', item["Text"]).strip()
    return parsed_data


def parse_text(text, act_name):
    """
    Parses the text of a legal document and extracts structured data.

    Args:
        text (str): The raw text of the legal document.
        act_name (str): The name of the act.

    Returns:
        list: A list of dictionaries containing structured information for each paragraph.
    """
    global global_unique_id
    result = []
    
    starts_with_chapter = text.lstrip().startswith("Chapter")
    has_chapters = bool(re.search(r"Chapter\s+[IVXLCDM]+", text))

    if starts_with_chapter or has_chapters:
        chapters = re.split(r"Chapter\s+[IVXLCDM]+", text)
        for chapter_idx, chapter in enumerate(chapters[1:], start=1):
            section_match = re.search(r"^[^\n§]+", chapter.strip())
            section_name = (
                section_match.group(0).strip()
                if section_match
                else f"Chapter {chapter_idx}"
            )

            paragraphs = re.split(r"\n§\s+(\d+)", chapter)
            if len(paragraphs) < 2:
                global_unique_id += 1
                result.append({
                    "GUID": global_unique_id,
                    "ActName": act_name,
                    "Section": section_name,
                    "Paragraph": "Entire Chapter",
                    "Text": chapter.strip(),
                    "WordCount": len(chapter.strip().split()),
                    "References": extract_references(chapter.strip(), chapter_idx, section_name, "Entire Chapter"),
                })
                continue

            for paragraph_idx in range(1, len(paragraphs) - 1, 2):
                paragraph_number = paragraphs[paragraph_idx]
                paragraph_text = paragraphs[paragraph_idx + 1].strip()

                global_unique_id += 1
                result.append(
                    {
                        "GUID": global_unique_id,
                        "ActName": act_name,
                        "Section": section_name,
                        "Paragraph": f"§ {paragraph_number}",
                        "Text": paragraph_text,
                        "WordCount": len(paragraph_text.split()),
                        "References": extract_references(
                            paragraph_text, chapter_idx, section_name, paragraph_number
                        ),
                    }
                )
    else:
        sections = re.split(r"\n§\s+(\d+)", text)
        if len(sections) < 2:
            global_unique_id += 1
            result.append({
                "GUID": global_unique_id,
                "ActName": act_name,
                "Section": "Entire Document",
                "Paragraph": "Entire Text",
                "Text": text.strip(),
                "WordCount": len(text.strip().split()),
                "References": extract_references(text.strip(), 1, "Entire Document", "Entire Text"),
            })
            return result

        for idx, section_idx in enumerate(range(1, len(sections) - 1, 2)):
            paragraph_number = sections[section_idx]
            paragraph_text = sections[section_idx + 1].strip()

            global_unique_id += 1
            result.append(
                {
                    "GUID": global_unique_id,
                    "ActName": act_name,
                    "Section": f"Section {idx + 1}",
                    "Paragraph": f"§ {paragraph_number}",
                    "Text": paragraph_text,
                    "WordCount": len(paragraph_text.split()),
                    "References": extract_references(
                        paragraph_text, idx + 1, f"Section {idx + 1}", paragraph_number
                    ),
                }
            )

    result = clean_text_in_json(result)

    return result


def extract_act_name(file_name):
    """
    Extracts the act name from the input file name.

    Args:
        file_name (str): The name of the input file.

    Returns:
        str: The extracted and formatted act name.
    """
    return os.path.splitext(file_name)[0].replace("_", " ").title()


os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for file_name in os.listdir(INPUT_FOLDER):
    if file_name.endswith(".txt"):
        input_path = os.path.join(INPUT_FOLDER, file_name)
        output_path = os.path.join(
            OUTPUT_FOLDER, f"{os.path.splitext(file_name)[0]}.json"
        )

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        act_name = extract_act_name(file_name)

        parsed_data = parse_text(text, act_name)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)

        print(f"Processed file: {file_name} -> {output_path}")
