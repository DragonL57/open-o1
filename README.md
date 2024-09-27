# Open-o1

It thinks like o1

## TODO

[ ] Add fallback llms 
[ ] Better error handling
[ ] Add Tools (web, math, code)
[ ] Make cli
[ ] better prompts for mathematical reasoning/reviewing

## What it does

- It taks the prompt, decides whether to use chain of thought or direct answer, if cot then generates answer and does self review, if direct answer then directly generates answer.
- Mathematical reasoning, symbolic reasoning and semi-symbolic reasoning kind of tasks generally improves with chain of thought, but direct answer is good for factual recall, simple inferences, commonsense reasoning, language understanding tasks.

## Installation

```bash
git clone https://github.com/tikendraw/open-o1.git

cd open-o1

streamlit run app.py
```

HAVE FUN.

## Helpful Papers

1. To Cot or not to Cot? CHAIN-OF-THOUGHT HELPS MAINLY ON MATH AND SYMBOLIC REASONING
```bibtex
@misc{sprague2024cotcotchainofthoughthelps,
      title={To CoT or not to CoT? Chain-of-thought helps mainly on math and symbolic reasoning}, 
      author={Zayne Sprague and Fangcong Yin and Juan Diego Rodriguez and Dongwei Jiang and Manya Wadhwa and Prasann Singhal and Xinyu Zhao and Xi Ye and Kyle Mahowald and Greg Durrett},
      year={2024},
      eprint={2409.12183},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2409.12183}, 
}
```

2. The Impact of Reasoning Step Length on Large Language Models
```bibtex
@misc{jin2024impactreasoningsteplength,
      title={The Impact of Reasoning Step Length on Large Language Models}, 
      author={Mingyu Jin and Qinkai Yu and Dong Shu and Haiyan Zhao and Wenyue Hua and Yanda Meng and Yongfeng Zhang and Mengnan Du},
      year={2024},
      eprint={2401.04925},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2401.04925}, 
}
```
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

# But me a Coffee

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/tikendraw)
