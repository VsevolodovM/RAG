## Legal Document Parser
Introduction
The Legal Document Parser is a Python-based tool designed to process legal documents in plain text (.txt) format. It extracts structured information such as chapters, sections, paragraphs, and references, saving the results as JSON files. This parser is particularly useful for organizing and analyzing legal texts, automating tasks like legal research, compliance checks, and document management.

## Features
Parses legal documents into a structured JSON format. <br>
Extracts:
- Chapters and sections.
- Paragraphs and sub-points.
- Cross-references such as Para (1), Paras (1) to (5), Section 3, and § 2 paras 3 to 6.
- Handles Roman numeral chapters and nested references.
- Outputs clean and ready-to-use JSON files.

## Usage
#### Preparing Input Files
- Place your .txt files in the documents/ folder.
- File names should describe the legal act or document (e.g., <b> Act of legal usage.txt</b>).

#### Running the Script
- Execute the script with: python parser.py
- The script processes all .txt files in the documents/ folder.

#### Checking the Output
- Processed files are saved in the output/ folder with the same base name as the input file, but with a .json extension (e.g., <b> Act of legal usage.json</b>).