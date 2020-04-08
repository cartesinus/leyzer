# Leyzer

## Patterns

### Pattern generation

You will need [JSGFTools](https://github.com/syntactic/JSGFTools) to expand grammars to patterns:
```bash
cd JSGFTools
python DeterministicGenerator.py ../leyzer/grammars/${lang}/${domain}.gram > ../leyzer/patterns/${lang}/${domain}.tsv
```

## Slot Values

- twitter values for messages has been extracted from [sentiment140](http://sentiment140.com/) corpora.
- phone names, phone email, calendar organizer, email message, email sender address, email subject and
  email to were taken from enron emails.

## Citation

If you use this, please cite:
```
@InProceedings{lejzer,
    title     = {Leyzer: A Dataset for Multilingual Virtual Assistants},
    author    = {Sowa\'{n}ski, Marcin and Janicki, Artur},
    booktitle = {},
    pages     = {},
    publisher = {},
    year      = {},
    month     = {},
    address   = {},
    url       = {}
}
```
