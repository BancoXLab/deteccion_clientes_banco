.PHONY: train

train:
	jupyter nbconvert --to notebook --execute models/baseline.ipynb --output models/baseline_output.ipynb
