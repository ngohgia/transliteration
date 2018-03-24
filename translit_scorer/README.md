# Transliteration Scorer

This is an error scorer for transliteration outputs. The words in the reference and hypothesis are matched by their syllables in order to minimize the errors on the syllable level. Detailed errors on individual components of a syllable are then computed.

## Data format
The scorer assumes each input files has one word per line, with the syllables of each word delimited by `.` (a dot) and a correct syllable assumes the form of `ONSET NUCLEUS CODA TONE`, with `NUCLEUS` as the only required component.

E.g.: a transliterated output for the word `nabski` in Vietnamese would be:
`n E p _2 . s @: _3 . k i _1`

See files under `sample` directory for more examples of the data format

## Language specification
The tokens specific to each component of a syllable needs to be specified for each language. See `VietnameseLang`, `MandarinLang`, and `CantoneseLang` for reference.

## How to run the scorer
### Requirements
`sclite` needs to be installed

### Command
```
python translit_scorer.py  path_to_hyp_file path_to_ref_file report_output_directory  report_name language_specs_file path_to_sclite_executable
```

Example:
```
python TranslitScorer.py sample/sample.out sample/sample.vie sample/ report VieLang/vie_lang_specs.txt ~/sclite/sclite
```

This command will score the hypothesis in `sample/sample.out` against `sample/sample.vie` and save the reports into `sample/` directory using Sclite executable at `~/sclite/sclite` 

### Error rate reports
There will be two reports:
- `<report_name>.summary.txt` - summary of erorr rates
```
String error rate: similar to string error rate by sclite
Syllable error rate: percentage of wrong syllables
Subsyllabic unit error rate: equivalent to token error rate by sclite, but scored after the syllables are matched
  ONSET: overall error rate at onset position
    S: substitution error rate at onset position
    D: deletion error rate at onset position
    I: inserstion error rate at onset position
  NUCLEUS:
    ...
  CODA:
    ...
  TONE:
    ...
String with wrong syllabic structure: percentage of strings with at least one syllable with a wrong structure
Out of XXXX% strings with correct syllabic structure: for the entries with all syllables with correct strucutre, the followings are detailed error rate at each position
  ONSET:
    ...
  NUCLEUS:
    ...
  CODA:
    ...
  TONE:
    ...

String with wrong toneless subsyllabic units XXXXX%: percentage of strings with at least one wrong token, tones excluded
Out of #####% strings with correct toneless subsyllabic units: for the entries with all correct tokens excluding tones, the followings are deatiled error rate for the tone
  I: ...
  S: ...
```


- `sample/report.full.csv` - detailed matching of each entry
