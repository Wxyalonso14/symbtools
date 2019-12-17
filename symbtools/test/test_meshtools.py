# -*- coding: utf-8 -*-
"""
Created on 2019-12-12 00:14:14

@author: Carsten Knoll
"""

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3

import symbtools.meshtools as met
import ipydex as ipd

import unittest


class TestGrid2d(unittest.TestCase):
    def setUp(self):
        xx = np.linspace(-4, 4, 9)
        yy = np.linspace(-4, 4, 9)

        XX, YY = mg = np.meshgrid(xx, yy, indexing="ij")

        self.mg = mg

    def test_create_cell(self):
        # met.create_nodes_from_mg(self.mg)
        grid = met.Grid(self.mg)

        l1 = len(grid.cells)
        self.assertEqual(len(grid.ndb.levels[0]), 81)

        self.assertEqual(grid.idx_edge_pairs, [(0, 1), (0, 2), (1, 3), (2, 3)])

        childs1 = grid.cells[0].make_childs()

        self.assertEqual(len(childs1), 4)
        expected_vertices = np.array([[-4., -4.], [-4., -3.5], [-3.5, -4.],  [-3.5, -3.5]])
        self.assertTrue(np.all(childs1[0].get_vertex_coords() == expected_vertices))

        # five nodes had to be inserted
        self.assertEqual(len(grid.ndb.levels[1]), 5)

        childs2 = childs1[0].make_childs()
        self.assertEqual(len(grid.ndb.levels[2]), 5)

        self.assertEqual(childs1[0].child_cells, childs2)
        self.assertEqual(childs2[0].parent_cell, childs1[0])

        self.assertEqual(len(grid.levels[0]), l1)
        self.assertEqual(len(grid.levels[1]), len(childs1))
        self.assertEqual(len(grid.levels[2]), len(childs2))

        if 0:
            plt.plot(*grid.all_mg_points, '.')
            plot_cells2d([gc]+childs1+childs2, show=True)

    def _test_plot(self):
        # create images where each new cell is shown
        grid = met.Grid(self.mg)

        plt.plot(*grid.all_mg_points, '.')
        plt.savefig("tmp_0.png")
        for i, cell in enumerate(grid.cells):
            edges = np.array(cell.get_edge_coords())
            plt.plot(*edges.T)
            plt.savefig("tmp_{:03d}.png".format(i))

        ipd.IPS()


class TestGrid3d(unittest.TestCase):

    def setUp(self):
        xx = np.linspace(-4, 4, 9)
        yy = np.linspace(-4, 4, 9)
        zz = np.linspace(-4, 4, 9)

        mg = np.meshgrid(xx, yy, zz, indexing="ij")

        self.mg = mg

    def test_create_cells(self):
        grid = met.Grid(self.mg)

        self.assertEqual(list(grid.cells[0].vertex_nodes[0].coords), [-4.0, -4.0, -4.0])
        self.assertEqual(list(grid.cells[0].vertex_nodes[3].coords), [-4.0, -3.0, -3.0])

    def test_plot(self):
        # create images where each new cell is shown
        grid = met.Grid(self.mg)
        l1 = len(grid.cells)

        childs1 = grid.cells[0].make_childs()

        self.assertEqual(len(grid.ndb.levels[1]), 19)

        l2 = len(grid.cells)
        self.assertEqual(len(childs1), 8)
        self.assertEqual(l2, l1 + len(childs1))

        expected_vertices = np.array([[-4.0, -4.0, -4.0],
                                      [-4.0, -4.0, -3.5],
                                      [-4.0, -3.5, -4.0],
                                      [-4.0, -3.5, -3.5],
                                      [-3.5, -4.0, -4. ],
                                      [-3.5, -4.0, -3.5],
                                      [-3.5, -3.5, -4.0],
                                      [-3.5, -3.5, -3.5]])
        self.assertTrue(np.all(childs1[0].get_vertex_coords() == expected_vertices))

        childs2 = childs1[0].make_childs()
        self.assertEqual(len(grid.ndb.levels[2]), 19)

        self.assertEqual(childs1[0].child_cells, childs2)
        self.assertEqual(childs2[0].parent_cell, childs1[0])

        self.assertEqual(len(grid.cells), l1 + len(childs1) + len(childs2))

        if 0:
            plot_cells = grid.cells[:1] + [grid.cells[-16]] + grid.cells[-8:]

            plot_cells3d(plot_cells, imax=None, show=True, all_points=grid.all_mg_points)


class MeshRefinement2d(unittest.TestCase):

    def setUp(self):
        xx = np.linspace(-4, 4, 9)
        yy = np.linspace(-4, 4, 9)

        mg = np.meshgrid(xx, yy, indexing="ij")

        self.mg = mg

    def test_refinement(self):

        grid = met.Grid(self.mg)

        ndb = grid.ndb

        ndb.apply_func(met.func_circle)
        grid.classify_cells_by_homogenity()

        ic = grid.inhomogeneous_cells[0]

        # there are 12 inhomogeneous cells (manually verified)
        self.assertEqual(len(ic), 12)

        a_in0 = ndb.get_inner()
        a_out0 = ndb.get_outer()

        b_in0 = ndb.get_inner_boundary()
        self.assertEqual(b_in0.shape, (2, 5))

        b_out0 = ndb.get_outer_boundary()
        self.assertEqual(b_out0.shape, (2, 16))

        # plot inner and outer points (level 0)
        plt.plot(*a_out0, "bo", alpha=0.2, ms=5)
        plt.plot(*a_in0, "ro", alpha=0.2, ms=5)

        plt.plot(*b_out0, "bo", ms=3)
        plt.plot(*b_in0, "ro", ms=3)

        plt.title("levels 0")
        plt.savefig("level0.png")

        # -----
        self.assertEqual(grid.max_level, 0)
        grid.divide_boundary_cells()
        self.assertEqual(grid.max_level, 1)
        ndb.apply_func(met.func_circle)
        grid.classify_cells_by_homogenity()

        a_in1 = ndb.get_inner()
        a_out1 = ndb.get_outer()

        b_in1 = ndb.get_inner_boundary()
        self.assertEqual(b_in1.shape, (2, 12))

        b_out1 = ndb.get_outer_boundary()
        self.assertEqual(b_out1.shape, (2, 20))

        # plot inner and outer points (level 1)
        plt.cla()

        plt.plot(*a_out1, "go", alpha=0.2, ms=5)
        plt.plot(*a_in1, "mo", alpha=0.2, ms=5)

        plt.plot(*b_out1, "go", ms=3)
        plt.plot(*b_in1, "mo", ms=3)

        plt.title("levels 0, 1")
        plt.savefig("level1.png")
        plt.show()
        ipd.IPS()


def plot_cells2d(cells, fname=None, show=False):
    for i, cell in enumerate(cells):
        edges = np.array(cell.get_edge_coords())
        plt.plot(*edges.T)
        if fname is not None:
            # expect something like "tmp_{:03d}.png"
            plt.savefig(fname.format(i))

    if show:
        plt.show()


def plot_cells3d(cells, ax=None, fname=None, show=False, imax=None, all_points=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection='3d')

    if all_points is not None:
        ax.plot(*all_points, '.', ms=1, color="k")

    for i, cell in enumerate(cells):
        edges = np.array(cell.get_edge_coords())

        for j, e in enumerate(edges):
            ax.plot(*e.T)

        if fname is not None:
            # expect something like "tmp_{:03d}.png"
            plt.savefig(fname.format(i))

        if imax is not None and i >= imax:
            break

    if show:
        plt.show()





