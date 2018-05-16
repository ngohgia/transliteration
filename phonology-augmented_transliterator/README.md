# PHONOLOGY-AUGMENTED TRANSLITERATION FOR LOW-RESOURCED LANGUAGES

## Data format

- Training: each line in the input file for training has one word in lower-cased Latin alphabets and a transliteration output, with the syllables of each word delimited by . (a dot).
- Testing: each line in input file for testing has one word in lower-cased Latin alphabets


## How to run
Since pronunciation of the source language is used in the back-off model, [CMU pronunciation dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict) needs to be installed.

Command:
```
python transliterator.py TRAIN_FILE TEST_FILE OUTPUT_FILE INTERMEDIATE_OUTPUT_DIR CMU_DECODER LOG_FILE
```
Example:
```
python transliterator.py sample_data/train.lex sample_data/test.lex sample_data/test.output sample_data/tmp ~/cmu_decoder/t2p_dt.pl sample_data/tmp/log.txt
```
