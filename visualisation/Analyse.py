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
import shutil
import seaborn as sns


import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from tools.Tools import *


class Analyse(Tools):
	def __init__(self, data, param = None, save_path = "./tmp/report"):
		
		Tools.__init__(self, data, param = None)
		self.cache = {}
		self.local_path = os.path.dirname(os.path.realpath(__file__))
		self.save_path = save_path
		if not os.path.exists(save_path):
					os.makedirs(save_path + "/images")

	def set_save_path(self,sp):
		self.save_path = sp


	def tek_load(self, path = None):
		"""
		Load a latek file from path
		"""
		if path == None:
			path = self.save_path + "/main.tex"

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
		#self.histogrammes()
		self.stats()
		self.dispertion()
		self.correlation()
		

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

		plt.close()


	def stats(self, lim = 0.01):
		"""
		Create latek table with mean, std
		"""
		desc = self.data.describe()
		table  = str(desc.round(2))
		struct = "|l|" + "c|"*(self.p - 1)
		table = self._add_table(table, "Tableau descriptif des données", "descript", struct)


		means = desc.values[1,:]
		stds = desc.values[2,:]

		self.cache['means'] = means
		self.cache['stds'] = stds


		em = np.std(means)
		es = np.std(stds)

		text = "Le tableau \\ref\{tab:descript\} donne une déscription des données. "
		if em > lim:
			text += "Les moyennes de chaque #variables n'étant pas centrées autour d'une même valeur, il sera préférable par la suite de centrer les données. "
		else :
			text += "Les moyennes de chaque #variables étant centrées autour d'une même valeur {}, il ne sera pas obligatoire de centrer les données par la suite. ".format(np.mean(means))

		if es > lim:
			text += "De plus, les écarts types de chaque variables sont dispersées. Donc il faudra réduire les données pour obtenir des valeurs comparables entre elles. "
		else:
			text += "De plus, les écarts types de chaque variables sont équivalentes, avec une valeur proche de {}. Donc il ne sera pas obligatoire de réduire les données pour obtenir des valeurs comparables entre elles. ".format(np.mean(stds))

		text += "\\\\ \n\n\n"
		self.main += text



	def correlation(self):
		"""
		Create the correlation matrix and add it to the latek file
		"""
		x = range(self.n)
		y = range(self.p)
		ax = sns.heatmap(self.data.iloc[x,y].corr(), annot=True, fmt=".2f", linewidths=.5, vmin=-1, vmax=1)
		figure = ax.get_figure()    
		
		figure.savefig(self.save_path+"/images/corr.png")
		self._add_figure("images/corr.png", 'Corrélation entre les différentes variables', 'corr')
		
		plt.close()


	def dispertion(self):
		"""
		Create the dispertion plots and the histogrammes, add it in the tex file
		"""
		g = sns.pairplot(self.data.iloc[range(self.n),range(self.p)], diag_kind="kde", markers="+",
		                  plot_kws=dict(s=50, edgecolor="b", linewidth=1),
		                  diag_kws=dict(shade=True))
		
		g.savefig(self.save_path+"/images/disp.png")
		self._add_figure("images/disp.png", 'Dispersion entre les différentes variables et correlation de chaque variable', 'disp')
		

		plt.close()


	def plot_series(self, legend, xlab, ylab, title, save = True):
		"""
		Plots and write latteksfile for time series
		"""
		plt.plot(self.data)
		plt.legend(legend, bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
		plt.xlabel(xlab);
		plt.ylabel(ylab);
		# plt.title('Séries temporelles pour ' +str(len(legend))+ ' indictateurs de '+title); 
		plt.grid(True)
		if save:
			i = 0
			while os.path.exists(self.save_path+"/images/plotSeries"+str(i)+".png"):
				i += 1

			plt.savefig(self.save_path+"/images/plotSeries"+str(i)+".png")
			plt.close()

			self._add_figure("images/plotSeries"+str(i)+".png", 'Séries temporelles pour ' +str(len(legend))+ ' indictateurs de '+title, "series"+str(i))

		else: 
			plt.show()


	
	


# data = pd.read_csv("notes.dat",sep='\t',index_col=0)
# ann = Analyse(data, save_path = "/home/myr/tmp/report")
# ann.tek_create()



