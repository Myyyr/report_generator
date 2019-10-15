"""
This class is made to make the ACP xork on a data set. 
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

from sklearn.decomposition import PCA

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from visualisation.Analyse import *


class Acp(Analyse):
	def __init__(self, data, param = None, save_path = "./tmp/report", norm = False):
		
		Tools.__init__(self, data, param = param)
		self.cache = {}
		self.local_path = os.path.dirname(os.path.realpath(__file__))
		self.save_path = save_path
		if not os.path.exists(save_path):
					os.makedirs(save_path + "/images")


		pop_list = list(data.index)
		var_list = list(data)

		indice_pop = np.array(range(len(pop_list)))
		indice_var = np.array(range(len(var_list)))

		self.pop_names = [pop_list[i] for i in indice_pop]
		self.var_names = [var_list[i] for i in indice_var]

		del pop_list,var_list,indice_pop,indice_var


		# normalise the data
		desc = self.data.describe()
		self.means = desc.values[1,:]
		self.stds = desc.values[2,:]
		if norm:
			self.data_norm = (data - self.means)/self.stds
		else:
			self.data_norm = data
		del desc

		# ACP

		self.acp = PCA()
		self.cp = self.acp.fit(self.data_norm)
		self.new_coords = self.acp.fit_transform(self.data_norm)

		

		corrOldNew = np.corrcoef(self.data_norm.T,self.new_coords.T)
		corrOldNew = corrOldNew[0:len(self.var_names),len(self.var_names):]
		self.var_new_coords  = pd.DataFrame(data=corrOldNew,
		                                       index=self.var_names,
		                                       columns=list(range(1,self.acp.n_features_+1)))
		del corrOldNew
		self.var_new_coords.columns = ['CP_' + str(col) for col in self.var_new_coords.columns]
		
		

	def get_var_new_coords(self):
		return self.var_new_coords

	def get_data_norm(self):
		return self.data_norm

	def get_new_coords(self):
		return self.new_coords


	def inertie(self, save = True):
		"""
		Compute the inertie of the singular values and plot it. Save is for the The latek part.
		"""
		plt.bar(np.arange(len(self.acp.explained_variance_ratio_))+1,self.acp.explained_variance_ratio_*100)
		plt.plot(np.arange(len(self.acp.explained_variance_ratio_))+1,np.cumsum(self.acp.explained_variance_ratio_*100),'r--o')
		plt.xlabel("Dimensions",fontsize=14)
		plt.ylabel("% d'inertie expliquée",fontsize=14)
		plt.grid(True)
		title = "Inertie expliquée en fonction du nombre de dimensions"
		if save == True:

			plt.savefig(self.save_path+"/images/inertie.png")
			self._add_figure("images/inertie.png", title, "inertie")
		else:
			plt.title(title)
			plt.show()
		plt.close()

		


	def pop_quality(self, save = True):
		"""
		Compute the representation quality of the population. Save it into latek file if save = True
		"""
		qual = self.new_coords*self.new_coords
		qual = (qual.T / qual.sum(axis=1)).T
		quality = pd.DataFrame(data=qual, index=self.pop_names, columns=list(range(1,self.acp.n_features_+1)))
		del qual
		#quality.add_prefix('CP_')
		quality.columns = ['CP_' + str(col) for col in quality.columns]
		quality=quality*100

		if save == False:
			return quality
		else:
			return None



	def pop_contribution(self, save =True):
		"""
		Compute the contribution of the population for the axes. Save it into latek file if save = True
		"""
		contr = self.new_coords*self.new_coords
		contr = contr / contr.sum(axis=0)
		contribution = pd.DataFrame(data=contr, index=self.pop_names, columns=list(range(1,self.acp.n_features_+1)))
		del contr
		contribution.columns = ['CP_' + str(col) for col in contribution.columns]
		contribution=contribution*100

		if save == False:
			return contribution
		else:
			return None

	def var_quality(self, save = True):
		"""
		Compute the representation quality of the variables. Save it into latek file if save = True
		"""
		qualVar = self.var_new_coords**2
		qualVar=qualVar*100

		if save == False:
			return qualVar
		else:
			return None


	def var_contribution(self, save = True):
		"""
		Compute the contribution of the variables for the new axes. Save it into latek file if save = True
		"""
		contrVar=(self.var_new_coords**2)/(self.var_new_coords**2).sum(axis=0)
		contrVar=contrVar*100

		if save == False:
			return contrVar
		else:
			return None


	def corr_circle(self, save = True):

		"""
		Compute the representation of variables in different factorial planes (variable cloud).
		Save into latek file if save = True
		"""
		# x_lim = [-1.1,1.1]
		# y_lim = [-1.1,1.1]
		# cpt = 0
		# plt.subplots(figsize=(10,10*d))
		# for i in range(d-1):
		#     for j in range(i+1,d):
		#         cpt += 1
		#         ax = plt.subplot('{}{}{}'.format(int(d*(d-1)/2),1,cpt))
		#         # cercle unitaire
		#         cercle = plt.Circle((0,0),1,color='red',fill=False)
		#         ax.add_artist(cercle)
		#         #
		#         # projection du nuage des variables 
		#         for k in range(len(nomDesVariables)):
		#             ax.arrow(0, 0, coordonneesDesVariables.iloc[k,i], coordonneesDesVariables.iloc[k,j],length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
		#             # Ornementation
		#             plt.text(coordonneesDesVariables.iloc[k,i], coordonneesDesVariables.iloc[k,j], nomDesVariables[k])#,fontsize=fontsize)
		#         if not coordonneesDesVariables_sup.shape[0] == 0:
		#             for k in range(len(nomDesVariables_sup)):
		#                 ax.arrow(0, 0, coordonneesDesVariables_sup.iloc[k,i], coordonneesDesVariables_sup.iloc[k,j],length_includes_head=True, head_width=0.05, head_length=0.1, fc='b', ec='b')
		#                 # Ornementation
		#                 plt.text(coordonneesDesVariables_sup.iloc[k,i], coordonneesDesVariables_sup.iloc[k,j], nomDesVariables_sup[k])#,fontsize=fontsize)
		#         plt.title('Axes {} et {}'.format(i+1,j+1))
		#         #
		#         # ajout d'une grille
		#         plt.grid(color='lightgray',linestyle='--')
		#         # Ajouter des deux axes correspondants aux axes factoriels
		#         ax.arrow(x_lim[0], 0, x_lim[1]-x_lim[0], 0,length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
		#         plt.plot(plt.xlim(), np.zeros(2),'k-')
		#         plt.text(x_lim[1], 0, "axe {:d}".format(i+1))
		#         #
		#         ax.arrow(0, y_lim[0], 0, y_lim[1]-y_lim[0],length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
		#         plt.plot(np.zeros(2),plt.ylim(),'k-')
		#         plt.text(0,y_lim[1], "axe {:d}".format(j+1))
		#         #        ax.set_ylim([-1.1, 1.1])
		#         ax.set_xlim(x_lim)
		#         ax.set_ylim(y_lim)
		#         ax.set_aspect('equal')

