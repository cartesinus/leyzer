# Leyzer: A Dataset for Multilingual Virtual Assistants

Leyzer is a multilingual text corpus designed to study multilingual and cross-lingual natural language understanding (NLU) models and the strategies of localization of virtual assistants. It consists of 21 domains across three languages: English, Spanish and Polish, with 194 intents and a wide range of samples, ranging from 1 to 672 sentences per intent. For more stats please refer to [wiki](https://github.com/cartesinus/leyzer/wiki).

Named after [Ludwik Lejzer Zamenhof](https://en.wikipedia.org/wiki/L._L._Zamenhof), the inventor of the international language Esperanto, the most widely used constructed international auxiliary language in the world.

## Voice User Interface

In `./vui` you can find pdf files that visualize scope of each domain. They are suppose to be used by Language Experts when intent is added, removed or fixed to keep all languages in sync. It is probably best starting point if you want to see what commands (intents) and slots are available in Leyzer.

There is no mechanism that links VUIs with grammars, patterns and corpora, everything is synced manual and this leaves space for some mistakes and differences between files.

## Patterns

Patterns are sentences without slot values.

### Pattern generation

We use our fork of JSGFTools to expand grammars which is released as python package [JSGFToolsLeyzer](https://github.com/cartesinus/JSGFTools):
```bash
pip install JSGFToolsLeyzer
python scripts/generate_patterns.py -f grammars/${lang}/${domain}.gram > patterns/${lang}/${domain}.tsv
```

Grammar generation can also be run from config file (which is usefull for experiments):
```bash
python scripts/generate_patterns.py -c ~/projects/leyzer/experiments/massive_mapping/leyzer-expansion_small.conf
```
where config file is defined as:
```json
{
    "project_dir": "",
    "grammar_dir": "grammars/en-US/",
    "expand_output_dir": "",
    "expand": [
        {"domain": "", "intent": "", "expand-rate": 1}
    ]
}
```
expand-rate > 1 will generate N times all unique intent patterns. This is usefull when you want to generate 50 sentences that have different slot values for each pattern.


## Corpus

Different versions of our corpus can be found in `corpora/`. To convert patterns to corpus:
```bash
./scripts/expand-slots.sh ${lang} ./patterns/en-US/${domain}.tsv ./corpora/0.1.0/${domain}.tsv ${add_bio} ${repeat}
```
where:
- `${add_bio}` is either `true` or `false`. When set to `true` generated corpus will have BIO tags.
- `${repeat}` is either `true` or `false`. When set to `true` slot values, taken from `slot/${lang}`, will be repeated once if there is more sentences that values in slot file.

Because some slots (for example EMAIL.MESSAGE) have many values we duplicate some patterns many times (10x or even 50x) before we use `expand-slots.sh`.

## Experiments

Experiments described in our paper can be replicated with scripts provided in `experiments/`.

## Changelog

- 0.2.0 (current): Added new domain (Console), fixed many issues in grammars, introduced naturalness level and information about verb pattern.
- 0.1.0: 20 domains, 186 intents. Version described in publication (with some fixes made after publication).

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
