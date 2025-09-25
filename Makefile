.PHONY: train

train:
  jupyter nbconvert --to notebook --execute models/baseline.ipynb --output baseline_output.ipynb --output-dir=models