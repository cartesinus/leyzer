# Leyzer: A Dataset for Multilingual Virtual Assistants

Leyzer is a multilingual text corpus designed to study multilingual and cross-lingual natural language understanding (NLU) models and the strategies of localization of virtual assistants. It consists of 20 domains across three languages: English, Spanish and Polish, with 186 intents and a wide range of samples, ranging from 1 to 672 sentences per intent. For more stats please refer to [wiki](https://github.com/cartesinus/leyzer/wiki).

## Patterns

Patterns are sentences without slot values.

### Pattern generation

We use our fork of [JSGFTools](https://github.com/cartesinus/JSGFTools) to expand grammars to patterns:
```bash
git clone https://github.com/cartesinus/JSGFTools
cd JSGFTools
python DeterministicGenerator.py ../leyzer/grammars/${lang}/${domain}.gram > ../leyzer/patterns/${lang}/${domain}.tsv
```

## Corpus

Different versions of our corpus can be found in `corpora/`. To convert patterns to corpus:
```bash
./scripts/expand-slots.sh ${lang} ./patterns/en-US/${domain}.tsv ./corpora/0.1.0/${domain}.tsv ${add_bio} ${repeat}
```
where:
- `${add_bio}` is either `true` or `false`. When set to `true` generated corpus will have BIO tags.
- `${repeat}` is either `true` or `false`. When set to `true` slot values, taken from `slot/${lang}`, will be repeated once if there is more sentences that values in slot file.

## Experiments

Experiments described in our paper can be replicated with scripts provided in `experiments/`.

## Citation

If you use this corpus, please cite:
```
@inproceedings{sowanski2020leyzer,
  title={Leyzer: A Dataset for Multilingual Virtual Assistants},
  author={Sowa{\'n}ski, Marcin and Janicki, Artur},
  booktitle={International Conference on Text, Speech, and Dialogue},
  pages={477--486},
  year={2020},
  organization={Springer}
}
```
