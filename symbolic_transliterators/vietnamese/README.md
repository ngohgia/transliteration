# Symbolic Transliteration for Vietnamese.

## Reference

- Ngo, H. G., Chen, N. F., Sivadas, S., Ma, B., & Li, H. (2014). [A minimal-resource transliteration framework for vietnamese](https://www.researchgate.net/publication/289730287_A_minimal-resource_transliteration_framework_for_Vietnamese). In Fifteenth Annual Conference of the International Speech Communication Association.
- Chen, N. F., Sivadas, S., Lim, B. P., Ngo, H. G., Xu, H., Ma, B., & Li, H. (2014, May). [Strategies for Vietnamese keyword search](http://ieeexplore.ieee.org/abstract/document/6854377/). In Acoustics, Speech and Signal Processing (ICASSP), 2014 IEEE International Conference on (pp. 4121-4125). IEEE.


## Data format
- Input: each line in the input file contains the input foreign words in lower-case Latin alphabets, followed by its corresponding phonetic symbols produced by [CMU pronunciation dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict).
Example input can be found in `example_inputs.txt`.
- Output: transliteration outputs are encoded with [X-SAMPA](https://en.wikipedia.org/wiki/X-SAMPA) symbols. Sub-syllabic units are separated by a whitespace and a dot "." separates consecutive syllables.

## How to run
```bash
python transliterate.py INPUT_FILE OUTPUT_FILE
```
Example:
```bash
python transliterate.py example_inputs.txt output.txt
```
