
PROJECT_NAME   = hf.sim
PROJECT_TYPE   = python

include $(HOME)/.makefile

dataclean::
	@rm -f data/*.plot
	@rm -f data/*.dat
	@rm -f data/*.png

