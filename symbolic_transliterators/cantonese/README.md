# Symbolic Transliteration for Cantonese.

## Data format
- Input: each line in the input file contains the input foreign words in lower-case Latin alphabets. Example input can be found in `example_inputs.txt`.
- Output: transliteration outputs are encoded with [Jyutping](https://en.wikipedia.org/wiki/Jyutping) symbols. Sub-syllabic units are separated by a whitespace and a dot "." separates consecutive syllables.

## How to run
```bash
python transliterate.py -i INPUT_FILE -o OUTPUT_FILE
```
Example:
```bash
python transliterate.py -i example_inputs.txt -o output.txt
```
