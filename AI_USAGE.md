# AI_USAGE.md

## AI tool used

**ChatGPT** was used as a development assistant during the assignment.

## How AI assistance was used

AI assistance was used selectively for:

- Clarifying assignment requirements and edge cases.
- Discussing a clean project structure and separation of scraping/processing logic.
- Reviewing scraper behavior and debugging issues encountered during development.
- Suggesting test cases for cleaning, validation, and duplicate detection.
- Reviewing documentation and improving wording/clarity.

The implementation was reviewed and adapted during development rather than being accepted without verification.

## Representative prompts

Examples of the type of assistance requested:

1. "Review this scraper error and explain the likely cause and fix."
2. "Suggest unit-test cases for the cleaning, validation and deduplication functions."
3. "Review this implementation against the assignment requirements and point out missing edge cases."
4. "Help improve the README so the setup and execution steps are reproducible."

## Verification and review

The final implementation was verified by running the complete pipeline and inspecting the generated outputs:

```bash
python main.py
python -m pytest -q
```

The generated CSV, summary report and execution log were also checked for consistency. The final test suite completed successfully with all implemented tests passing.

## Responsibility

AI suggestions were treated as assistance during development. Final implementation decisions, testing, debugging, and verification were performed as part of the assignment process. I am responsible for understanding and explaining the submitted code.
