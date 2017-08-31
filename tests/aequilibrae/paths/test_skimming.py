import os, sys
from unittest import TestCase
from aequilibrae.paths import network_skimming, Graph
from aequilibrae.paths.results import SkimResults
from aequilibrae.matrix import AequilibraeMatrix

# Adds the folder with the data to the path and collects the paths to the files
lib_path = os.path.abspath(os.path.join('..', '..'))
sys.path.append(lib_path)
from data import path_test, test_graph


class TestSkimming(TestCase):
    def test_skimming(self):

        # graph
        g = Graph()
        g.load_from_disk(test_graph)
        g.set_graph(centroids=29, cost_field='distance', skim_fields=None)
        # None implies that only the cost field will be skimmed


        # matrix
        a = AequilibraeMatrix(cores=1,
                              zones=g.centroids+1,
                              names=['test_skimming']
                              )
        g.storage_path = os.path.join(path_test, 'aequilibrae_skimmint_test.aem')


        # skimming results
        res = SkimResults()
        res.prepare(g)

        # test single threaded procedure
        # self.fail('Failed when skimming')
