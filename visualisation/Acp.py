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

from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap



class Acp(Analyse):
	def __init__(self, data, param = None, save_path = "./tmp/report", norm = False, dimToKeepType = ('threshold', 95)):
		
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
		
		
		# Dimension to keep
		if dimToKeepType[0] == 'threshold':
			threshold = dimToKeepType[1]
			self.dim_to_Keep = np.argmax(np.cumsum(self.acp.explained_variance_ratio_)>=threshold/100)+1
		elif dimToKeepType[0] == 'fix':
			self.dim_to_Keep = dimToKeepType[1]
		else:
			self.dimToKeepType = 2


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


	def corr_circle(self, save = True, dims = []):

		"""
		Compute the representation of variables in different factorial planes (variable cloud).
		Save into latek file if save = True else plot it
		"""
		x_lim = [-1.1,1.1]
		y_lim = [-1.1,1.1]
		cpt = 0
		if dims == []:
			for i in range(self.dim_to_Keep-1):
				for j in range(i+1,self.dim_to_Keep):
					dims.append((i,j))
		
		plt.subplots(figsize=(10,10*len(dims)))

		# for i in range(self.dim_to_Keep-1):
		# 	for j in range(i+1,self.dim_to_Keep):
		for item in dims:

			i, j = item
			cpt += 1
			
			ax = plt.subplot('{}{}{}'.format(len(dims),1,cpt))
			# cercle unitaire
			cercle = plt.Circle((0,0),1,color='red',fill=False)
			ax.add_artist(cercle)
			#
			# projection du nuage des variables 
			for k in range(len(self.var_names)):
				ax.arrow(0, 0, self.var_new_coords.iloc[k,i], self.var_new_coords.iloc[k,j],length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
				# Ornementation
				plt.text(self.var_new_coords.iloc[k,i], self.var_new_coords.iloc[k,j], self.var_names[k])#,fontsize=fontsize)
			if save == False:
				plt.title('Axes {} et {}'.format(i+1,j+1))
			#
			# ajout d'une grille
			plt.grid(color='lightgray',linestyle='--')
			# Ajouter des deux axes correspondants aux axes factoriels
			ax.arrow(x_lim[0], 0, x_lim[1]-x_lim[0], 0,length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
			plt.plot(plt.xlim(), np.zeros(2),'k-')
			plt.text(x_lim[1], 0, "axe {:d}".format(i+1))
			#
			ax.arrow(0, y_lim[0], 0, y_lim[1]-y_lim[0],length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
			plt.plot(np.zeros(2),plt.ylim(),'k-')
			plt.text(0,y_lim[1], "axe {:d}".format(j+1))
			#		ax.set_ylim([-1.1, 1.1])
			ax.set_xlim(x_lim)
			ax.set_ylim(y_lim)
			ax.set_aspect('equal')

		if save == True:
			plt.close()
		else:
			plt.plot()



	def pop_cloud(self, save = True, categories = None, label = None, plot_threshold = 50, colortype = 'hsv' , size_factor = (5,500)):
		"""
		Compute the representation of the cloud of individuals (new coordinates).
		If save = True write latek file else plot it
		"""

		if len(self.pop_names) > 20:
			hsv = cm.get_cmap(colortype, 256)
			colormap = hsv(np.linspace(0,1,len(label)))
			
			qual = np.array(self.pop_quality(False))

		cpt = 0
		plt.subplots(figsize=(18,6*self.dim_to_Keep))
		for i in range(self.dim_to_Keep-1):
			for j in range(i+1,self.dim_to_Keep):
				cpt += 1
				ax = plt.subplot('{}{}{}'.format(int(self.dim_to_Keep*(self.dim_to_Keep-1)/2),1,cpt))
				
				if len(self.pop_names) != 0 and len(self.pop_names) <= 20 :
					plt.plot(self.new_coords[:,i],self.new_coords[:,j],'o')
					plt.title('Axes {} et {}'.format(i+1,j+1))
					for k in  range(len(self.pop_names)):
						plt.text(self.new_coords[k,i], self.new_coords[k,j], self.pop_names[k])#,fontsize=fontsize)
				elif len(self.pop_names) > 20:
					for lab in range(len(label)):
						coords = self.new_coords[categories == lab]
						qual_lab = qual[categories == lab]

						coords = coords[qual_lab[:,i]+qual_lab[:,j] >= plot_threshold]
						cmap = colormap[categories[categories == lab]]
						cmap = cmap[qual_lab[:,i]+qual_lab[:,j] >= plot_threshold]
						qual_lab = qual_lab[qual_lab[:,i]+qual_lab[:,j] >= plot_threshold]
						# print(coords[:,i].shape)
						# print((10+qual_lab[:,i]+qual_lab[:,j]*0.5).shape)
						# print((colormap[categories[categories == lab]]).shape)
						plt.scatter(coords[:,i],coords[:,j], 
									s=(((qual_lab[:,i]+qual_lab[:,j])/100)**size_factor[0])*size_factor[1], 
									alpha = 0.9,
									c=cmap, 
									label = label[lab],
									marker = '^')
					plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
					plt.title('Axes {} et {}'.format(i+1,j+1))

				# Ajouter les axes
				plt.grid(color='lightgray',linestyle='--')
				x_lim = plt.xlim()
				ax.arrow(x_lim[0], 0, x_lim[1]-x_lim[0], 0,length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
				plt.plot(plt.xlim(), np.zeros(2),'k-')
				plt.text(x_lim[1], 0, "axe {:d}".format(i+1))
				y_lim = plt.ylim()
				ax.arrow(0,y_lim[0], 0, y_lim[1]-y_lim[0],length_includes_head=True, head_width=0.05, head_length=0.1, fc='k', ec='k')
				plt.plot(np.zeros(2),plt.ylim(),'k-')
				plt.text(0,y_lim[1], "axe {:d}".format(j+1))

		if save == True:
			plt.close()
		else:
			plt.plot()



