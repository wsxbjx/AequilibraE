"""
 -----------------------------------------------------------------------------------------------------------
 Package:    AequilibraE

 Name:       Traffic assignment
 Purpose:    Implement traffic assignment algorithms based on Cython's network loading procedures

 Original Author:  Pedro Camargo (c@margo.co)
 Contributors:
 Last edited by: Pedro Camargo

 Website:    www.AequilibraE.com
 Repository:  https://github.com/AequilibraE/AequilibraE

 Created:    15/09/2013
 Updated:    2017-05-07
 Copyright:   (c) AequilibraE authors
 Licence:     See LICENSE.TXT
 -----------------------------------------------------------------------------------------------------------
 """

import sys
sys.dont_write_bytecode = True

import numpy as np
import thread
from multiprocessing.dummy import Pool as ThreadPool
try:
    from PyQt4.QtCore import SIGNAL
    pyqt = True
except:
    pyqt = False

from multi_threaded_aon import MultiThreadedAoN
try:
    from AoN import one_to_all, path_computation
except:
    pass

from ..utils import WorkerThread


class allOrNothing(WorkerThread):
    def __init__(self, matrix, graph, results):
        WorkerThread.__init__(self, None)

        self.matrix = matrix
        self.graph = graph
        self.results = results
        self.aux_res = MultiThreadedAoN()
        self.report = []
        self.cumulative = 0

        if results.__graph_id__ != graph.__id__:
            raise ValueError("Results object not prepared. Use --> results.prepare(graph)")

        if results.__graph_id__ is None:
            raise ValueError('The results object was not prepared. Use results.prepare(graph)')

        elif results.__graph_id__ != graph.__id__:
            raise ValueError('The results object was prepared for a different graph')

        elif matrix.matrix_view is None:
            raise ValueError('Matrix was not prepared for assignment. '
                             'Please create a matrix_procedures view with all classes you want to assign')

        elif not np.array_equal(matrix.index, graph.centroids):
            raise ValueError('Matrix and graph do not have compatible set of centroids.')

    def doWork(self):
        self.execute()

    def execute(self):
        if pyqt:
            self.emit(SIGNAL("assignment"), ['zones finalized', 0])

        self.aux_res.prepare(self.graph, self.results)
        self.matrix.matrix_view = self.matrix.matrix_view.reshape((self.graph.num_zones, self.graph.num_zones,
                                                                   self.results.classes['number']))
        mat = self.matrix.matrix_view
        pool = ThreadPool(self.results.cores)
        all_threads = {'count': 0}
        for orig in self.matrix.index:
            i = int(self.graph.nodes_to_indices[orig])
            if np.nansum(mat[i, :, :]) > 0:
                if self.graph.fs[i] == self.graph.fs[i+1]:
                    self.report.append("Centroid " + str(orig) + " is not connected")
                else:
                    pool.apply_async(self.func_assig_thread, args=(orig, all_threads))
                    # self.func_assig_thread(orig, all_threads)
        pool.close()
        pool.join()
        self.results.link_loads = np.sum(self.aux_res.temp_link_loads, axis=2)

        if pyqt:
            self.emit(SIGNAL("assignment"), ['text AoN', "Saving Outputs"])
            self.emit(SIGNAL("assignment"), ['finished_threaded_procedure', None])

    def func_assig_thread(self, O, all_threads):
        if thread.get_ident() in all_threads:
            th = all_threads[thread.get_ident()]
        else:
            all_threads[thread.get_ident()] = all_threads['count']
            th = all_threads['count']
            all_threads['count'] += 1
        x = one_to_all(O, self.matrix, self.graph, self.results, self.aux_res, th)
        self.cumulative += 1
        if x != O:
            self.report.append(x)
        if pyqt:
            self.emit(SIGNAL("assignment"), ['zones finalized', self.cumulative])
            txt = str(self.cumulative) + ' / ' + str(self.matrix.zones)
            self.emit(SIGNAL("assignment"), ['text AoN', txt])