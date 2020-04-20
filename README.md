# Leyzer

## Patterns

Patterns are sentences without slot values.

### Pattern generation

First you will need [JSGFTools](https://github.com/cartesinus/JSGFTools) to expand grammars to patterns:
```bash
git clone https://github.com/cartesinus/JSGFTools
cd JSGFTools
python DeterministicGenerator.py ../leyzer/grammars/${lang}/${domain}.gram > ../leyzer/patterns/${lang}/${domain}.tsv
```

## Citation

If you use this corpus, please cite:
```
@InProceedings{leyzer,
    title     = {Leyzer: A Dataset for Multilingual Virtual Assistants},
    author    = {Sowa\'{n}ski, Marcin and Janicki, Artur},
}
```
