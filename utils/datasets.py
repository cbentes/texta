# -*- coding: utf8 -*-
import json

from utils.es_manager import ES_Manager
from permission_admin.models import Dataset


class Datasets:
	""" Datasets class
	"""
	def __init__(self):
		self.datasets = self._build_datasets_map()
		self.mapping_id = None

	@staticmethod
	def _build_datasets_map():
		datasets = {}
		for dataset in Dataset.objects.all():
			pk = dataset.pk
			index = dataset.index
			mapping = dataset.mapping
			datasets[pk] = {'index': index, 'mapping': mapping}
		return datasets

	def activate_dataset(self, session):
		""" Activate dataset for a given session. If the session does not contain
			information about the dataset, initiates with the first valid dataset
			Returns: the session object containing the active dataset mapping_id
		"""
		if len(self.datasets.keys()) > 0:
			if 'dataset' not in session:
				# Activate first if not defined in session
				session['dataset'] = list(self.datasets.keys())[0]
			elif int(session['dataset']) not in self.datasets.keys():
				# Activate first if previously activated not present
				session['dataset'] = list(self.datasets.keys())[0]
			self.mapping_id = int(session['dataset'])
		return self

	def activate_dataset_by_id(self, _id):
		""" Activate dataset by ID
		"""
		if len(self.datasets.keys()) > 0:
			if _id not in self.datasets.keys():
				self.mapping_id = int(list(self.datasets.keys())[0])
			else:
				self.mapping_id = int(_id)

		return self

	def is_active(self):
		return self.mapping_id is not None

	def get_index(self):
		""" Returns: the active dataset index, None otherwise
		"""
		index = None
		if self.is_active():
			index = self.datasets[self.mapping_id]['index']
		return index

	def get_mapping(self):
		""" Returns: the active dataset mapping, None otherwise
		"""
		mapping = None
		if self.is_active():
			mapping = self.datasets[self.mapping_id]['mapping']
		return mapping

	def get_datasets(self):
		""" Returns: map of all dataset objects
		"""
		return self.datasets

	def build_manager(self, manager_class):
		""" Builds manager_class as:
			ManagerClass(index, mapping, date_range)
		"""
		index = self.get_index()
		mapping = self.get_mapping()
		return manager_class(index, mapping)

	def sort_datasets(self, indices):
		out = []
		open_indices = [index['index'] for index in indices if index['status'] == 'open']
		for dataset in sorted(self.datasets.items(), key=lambda l: l[1]['index']):
			ds = dataset[1]
			ds['id'] = dataset[0]
			if ds['index'] in open_indices:
				out.append(ds)
		return out

	def get_allowed_datasets(self, user):
		indices = ES_Manager.get_indices()
		datasets = self.sort_datasets(indices)
		return [dataset for dataset in datasets if user.has_perm('permission_admin.can_access_dataset_' + str(dataset['id']))]

