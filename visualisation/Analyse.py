"""
This class is made to make the first unidimensional and bidimensional annalyse
of a data set. 
 - Create the plots
 - Save the plots
 - write latek file
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
import seaborn as sns



class Analyse():
	def __init__(self, data, param = None, save_path = "./tmp/report"):
		self.data = data
		self.n, self.p = data.shape
		self.param = param
		self.save_path = save_path
		self.local_path = os.path.dirname(os.path.realpath(__file__))
		self.main = ""


		if not os.path.exists(save_path):
			os.makedirs(save_path + "/images")

		plt.rcParams['font.size'] = 18
		plt.rcParams['figure.figsize'] = (18*2, 8*2)


		if param == None:
			self.param = {'title' : 'title',
						'exercice' : 'exercice',
						'donnees' : 'donnees',
						'contenue_donnees' : 'contenue_donnees',
						'cours' : 'cours'}

	def tek_load(self, path = None):
		"""
		Load a latek file from path
		"""
		if path == None:
			path = self.save_path + "/"+name

		self.main = self._read_file(path)


	def tek_create(self):
		"""
		Create a latek file from the begining : 
			- Head
			- Intro
			- Histogrammes
		"""
		self.tek_head()
		self.tek_intro()
		self.histogrammes()
		self.stats()

		self.tek_save()


	def tek_save(self,  name = 'main.tex'):
		"""
		Save the Latek main file
		"""
		file = open(self.save_path + "/"+name, 'w')
		file.write(self.main)
		file.close()

	

	def tek_head(self):
		"""
		Write the begining / head of the latek file
		"""
		
		head = self._read_file(self.local_path + "/head.txt")

		head = self._complete_texte(head, 'title')

		self.main += head


	def tek_intro(self):
		"""
		Write the introduction of the latek file
		"""

		intro = self._read_file(self.local_path + "/intro.txt")
		intro = self._complete_texte(intro, 'exercice')
		intro = self._complete_texte(intro, 'cours')
		intro = self._complete_texte(intro, 'donnees')
		intro = self._complete_texte(intro, 'contenue_donnees')

		self.main += intro


	def histogrammes(self, save = True):
		"""
		Create / show or save / write latek of histogram plots
		"""
		hist = self.data.hist()
		if save: 
			plt.savefig(self.save_path+"/images/histogrammes.png")
			self._add_figure("images/histogrammes.png", 'Histogrammes des différentes variables', 'histogrammes')
		else :
			plt.show()


	def stats(self):
		"""
		Create latek table with mean, std
		"""

		table  = str(self.data.describe().round(2))
		struct = "|l|" + "c|"*(self.p - 1)
		table = self._add_table(table, "Tableau descriptif des données", "descript", struct)






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
	


data = pd.read_csv("notes.dat",sep='\t',index_col=0)
ann = Analyse(data, save_path = "/home/myr/tmp/report")
ann.tek_create()



