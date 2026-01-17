# TextAttack Tutorial

**Level**: Beginner to Advanced
**Category**: NLP / Adversarial AI

TextAttack is a Python framework for adversarial attacks, data augmentation, and model training in NLP. It is widely used to test the robustness of NLP models by trying to "fool" them.

## 📦 Installation

```bash
pip install textattack[tensorflow]  # or [pytorch] depending on your backend
```

## 🚀 Beginner: Data Augmentation

Generate new training examples by swapping words with synonyms (using WordNet).

```python
from textattack.augmentation import Augmenter

# Create an augmenter using WordNet wrapper
augmenter = Augmenter(transformation='wordnet')

s = "I am incredibly happy about the amazing service."
results = augmenter.augment(s)

print(results)
# Output might include:
# "I am incredibly happy about the astonishing service."
# "I am incredibly felicity about the amazing service."
```

## 🏃 Intermediate: Running an Attack (CLI)

TextAttack is famously easy to use from the command line.

**Goal**: Attack a pre-trained BERT model on the IMDb dataset (Sentiment Analysis) to find examples where changing a few words flips the prediction from Positive to Negative.

```bash
textattack attack --recipe textfooler --model bert-base-uncased-imdb --num-examples 10
```

1.  `--recipe textfooler`: Uses the "TextFooler" attack strategy (very effective).
2.  `--model`: Uses a pre-trained model from Hugging Face.
3.  `--num-examples`: Only run on 10 samples.

## 🧠 Advanced: Building a Custom Attack (Python API)

An attack consists of a **Goal Function**, **Constraints**, **Transformation**, and **Search Method**.

```python
import textattack
from textattack.goal_functions import UntargetedClassification
from textattack.constraints.pre_transformation import RepeatModification, StopwordModification
from textattack.search_methods import GreedySearch
from textattack.transformations import WordSwapWordNet
from textattack.models.wrappers import HuggingFaceModelWrapper
import transformers

# 1. Load Model
model = transformers.AutoModelForSequenceClassification.from_pretrained("textattack/bert-base-uncased-imdb")
tokenizer = transformers.AutoTokenizer.from_pretrained("textattack/bert-base-uncased-imdb")
model_wrapper = HuggingFaceModelWrapper(model, tokenizer)

# 2. Define Components
goal_function = UntargetedClassification(model_wrapper)
constraints = [RepeatModification(), StopwordModification()]
transformation = WordSwapWordNet()
search_method = GreedySearch()

# 3. Build Attack
attack = textattack.Attack(goal_function, constraints, transformation, search_method)

# 4. Attack a specific string
from textattack.datasets import Dataset
dataset = Dataset([("This movie was absolutely wonderful.", 1)]) # 1 = Positive

results = attack.attack_dataset(dataset)
for result in results:
    print(result.__str__(color_method="ansi"))
```

## 💡 Use Cases

1.  **Robustness Testing**: Verify if your chatbot can be tricked by simple typos or synonym swaps.
2.  **Data Augmentation**: Increase the size of your training dataset to improve model generalization.
3.  **Adversarial Training**: Train your model *on* the attacked examples to make it immune to them.
