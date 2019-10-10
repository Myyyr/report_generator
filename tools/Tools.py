"""
This class is made to implement the function
of a data set. 
 - Create the plots
 - Create tables
 - write latek file
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
import seaborn as sns


class Tools():
	def __init__(self, data, param = None):
		self.data = data
		self.n, self.p = data.shape
		self.param = param
		
		self.local_path = os.path.dirname(os.path.realpath(__file__))
		self.main = ""


		

		plt.rcParams['font.size'] = 18
		plt.rcParams['figure.figsize'] = (18*2, 8*2)


		if param == None:
			self.param = {'title' : 'title',
						'exercice' : 'exercice',
						'donnees' : 'donnees',
						'contenue_donnees' : 'contenue_donnees',
						'cours' : 'cours'}



	def _add_table(self, text, caption, label, struct):
		"""
		Write latek table
		"""
		new_text = text.replace(" ", "&")
		while "&&" in new_text:
			new_text = new_text.replace("&&", "&")
		new_text = new_text.replace('&', ' & ')
		new_text = new_text.replace('%', '\\%')
		new_text = new_text.replace('_', '\\_')
		new_text = new_text.replace("\n", " \\\\\n\\hline\n")
		new_text = "\\hline\n" + new_text + " \\\\\n\\hline"
		
		tabular = self._read_file(self.local_path + "/table.txt")
		tabular = self._complete_texte(tabular, 'struct', struct)
		tabular = self._complete_texte(tabular, 'label', label)
		tabular = self._complete_texte(tabular, 'caption', caption)
		tabular = self._complete_texte(tabular, 'table', new_text)

		self.main += tabular

	def _read_file(self, path):
		"""
		Tool to get texte from a file
		"""
		file = open(path)
		text = file.read()
		file.close()

		return text


	def _complete_texte(self, texte, key, param = None):
		"""
		Complete the text where there is the key word by parameter
		"""
		index = texte.find('#'+key+'#')
		if param == None:
			return texte[:index] + self.param[key] + texte[(index + len(key) + 2):]
		else:
			return texte[:index] + param + texte[(index + len(key) + 2):]


	def _add_figure(self,path, caption, label):
		"""
		add figure in the latek file
		"""
		fig = self._read_file(self.local_path + "/figure.txt")
		fig = self._complete_texte(fig, 'file', param = path)
		fig = self._complete_texte(fig, 'caption', param = caption)
		fig = self._complete_texte(fig, 'label', param = label)

		self.main += fig