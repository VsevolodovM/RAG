import os
import re
import json

INPUT_FOLDER = "documents"
OUTPUT_FOLDER = "output"


def extract_references(text, chapter_idx, section_name, paragraph_number):
    """
    Extracts references such as paragraphs (Para), sections, and clauses from the given text.

    Args:
        text (str): The text to parse for references.
        chapter_idx (int): The current chapter index.
        section_name (str): The name of the section or chapter.
        paragraph_number (str): The paragraph number in the current section.

    Returns:
        list: A list of extracted references.
    """
    references = []

    # e.g. Para (1) -> Specifically extract para as paragraph
    para_matches = re.findall(r"Para\s+\((\d+)\)", text)
    for para in para_matches:
        references.append(f"Para ({para})")

    # e.g. Paras (1) and (2) or Paras (5) to (6) -> Handle multiple paras as paragraph
    para_range_matches = re.findall(
        r"Paras?\s+\((\d+)\)\s+(?:and|to)\s+\((\d+)\)", text
    )
    for start, end in para_range_matches:
        references.extend([f"Para ({num})" for num in range(int(start), int(end) + 1)])

    # e.g. Section X -> Extract sections as section
    section_matches = re.findall(r"Section\s+(\d+)", text)
    for section in section_matches:
        references.append(f"Section {section}")

    # e.g. para X, paras X to Y, § X, § X paras Y to Z
    para_matches_extended = re.findall(r"para\s+(\d+)", text, re.IGNORECASE)
    references.extend([f"Para {para}" for para in para_matches_extended])

    paras_range_matches_extended = re.findall(
        r"paras?\s+(\d+)\s+(?:and|to)\s+(\d+)", text, re.IGNORECASE
    )
    for start, end in paras_range_matches_extended:
        references.extend([f"Para {num}" for num in range(int(start), int(end) + 1)])

    section_paras_matches = re.findall(
        r"§\s*(\d+)\s*(?:paras?\s+(\d+)\s+(?:and|to)\s+(\d+))?", text
    )
    for section, start_para, end_para in section_paras_matches:
        if start_para and end_para:
            references.extend(
                [
                    f"§ {section} paras {num}"
                    for num in range(int(start_para), int(end_para) + 1)
                ]
            )
        else:
            references.append(f"§ {section}")

    unique_references = list(set(references))

    return unique_references


def parse_text(text, act_name):
    """
    Parses the text of a legal document and extracts structured data.

    Args:
        text (str): The raw text of the legal document.
        act_name (str): The name of the act.

    Returns:
        list: A list of dictionaries containing structured information for each paragraph and point.
    result = []
    """
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
            for paragraph_idx in range(1, len(paragraphs), 2):
                paragraph_number = paragraphs[paragraph_idx]
                paragraph_text = paragraphs[paragraph_idx + 1]

                points = re.split(r"^\((\d+)\)\s", paragraph_text, flags=re.MULTILINE)

                if points[0].strip():
                    point_text = points[0].strip()
                    result.append(
                        {
                            "ActName": act_name,
                            "Section": section_name,
                            "Paragraph": f"§ {paragraph_number}",
                            "PunctNum": "1",
                            "Text": point_text,
                            "References": extract_references(
                                point_text, chapter_idx, section_name, paragraph_number
                            ),
                        }
                    )
                else:
                    result.append(
                        {
                            "ActName": act_name,
                            "Section": section_name,
                            "Paragraph": f"§ {paragraph_number}",
                            "PunctNum": "1",
                            "Text": "",
                            "References": extract_references(
                                "", chapter_idx, section_name, paragraph_number
                            ),
                        }
                    )

                for point_idx in range(1, len(points), 2):
                    point_num = points[point_idx]
                    point_text = points[point_idx + 1].strip()

                    result.append(
                        {
                            "ActName": act_name,
                            "Section": section_name,
                            "Paragraph": f"§ {paragraph_number}",
                            "PunctNum": point_num,
                            "Text": point_text,
                            "References": extract_references(
                                point_text, chapter_idx, section_name, paragraph_number
                            ),
                        }
                    )
    else:
        sections = re.split(r"\n§\s+(\d+)", text)
        for idx, section_idx in enumerate(range(1, len(sections), 2)):
            paragraph_number = sections[section_idx]
            paragraph_text = sections[section_idx + 1]

            points = re.split(r"^\((\d+)\)\s", paragraph_text, flags=re.MULTILINE)

            if points[0].strip():
                point_text = points[0].strip()
                result.append(
                    {
                        "ActName": act_name,
                        "Section": f"Section {idx + 1}",
                        "Paragraph": f"§ {paragraph_number}",
                        "PunctNum": "1",
                        "Text": point_text,
                        "References": extract_references(
                            point_text, idx + 1, f"Section {idx + 1}", paragraph_number
                        ),
                    }
                )
            else:
                result.append(
                    {
                        "ActName": act_name,
                        "Section": f"Section {idx + 1}",
                        "Paragraph": f"§ {paragraph_number}",
                        "PunctNum": "1",
                        "Text": "",
                        "References": extract_references(
                            "", idx + 1, f"Section {idx + 1}", paragraph_number
                        ),
                    }
                )

            for point_idx in range(1, len(points), 2):
                point_num = points[point_idx]
                point_text = points[point_idx + 1].strip()

                result.append(
                    {
                        "ActName": act_name,
                        "Section": f"Section {idx + 1}",
                        "Paragraph": f"§ {paragraph_number}",
                        "PunctNum": point_num,
                        "Text": point_text,
                        "References": extract_references(
                            point_text, idx + 1, f"Section {idx + 1}", paragraph_number
                        ),
                    }
                )

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
