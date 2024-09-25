# Open-o1

It thinks like o1

## TODO

[ ] Add fallback llms 
[ ] Better error handling
[ ] Add Tools (web, math, code)
[ ] Make cli


## What it does

- It takes a prompt , thinks, thinks again, critics itself, then returns answer 

## Installation

```bash
git clone https://github.com/tikendraw/open-o1.git

cd open-o1

streamlit run app.py
```

HAVE FUN.

## Helpful Papers

 1. To Cot or not to Cot? CHAIN-OF-THOUGHT HELPS MAINLY ON MATH AND SYMBOLIC REASONING

2. The Impact of Reasoning Step Length on Large Language Models

3. Towards Understanding Chain-of-Thought Prompting: An Empirical Study of What Matters [2212.10001](https://arxiv.org/abs/2212.10001)
```bibtex
@misc{wang2023understandingchainofthoughtpromptingempirical,
      title={Towards Understanding Chain-of-Thought Prompting: An Empirical Study of What Matters}, 
      author={Boshi Wang and Sewon Min and Xiang Deng and Jiaming Shen and You Wu and Luke Zettlemoyer and Huan Sun},
      year={2023},
      eprint={2212.10001},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2212.10001}, 
}
```