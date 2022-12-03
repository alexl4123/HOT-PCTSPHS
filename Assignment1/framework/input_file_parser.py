"""
This file contains the methods and functions for loading and parsing the input files
"""

import os
import sys
import random
import logging

import networkx as nx
import matplotlib.pyplot as plt

from pathlib import Path

from framework.constants import logger_name
from framework.instance import Instance

logger = logging.getLogger(logger_name)


class Input_File_Parser:

    def __init__(self, input_file_path):
        self._input_file_path = input_file_path

    def load_and_parse_input_file(self, debug=False):
        """
            Simple load and parse procedure
            No error checking or fallback provided
        """

        logger.debug(self._input_file_path)

        basename_stem = Path(self._input_file_path).stem
        instance_name = basename_stem.split("_")
        instance_name.pop(0)
        instance_name = ('_'.join(instance_name))


        input_file = open(self._input_file_path, "r")

        first_line = input_file.readline()

        parts = first_line.split(' ')

        num_hotels = int(parts[0])  # hotel number
        total_hotels = num_hotels + 1  # hotel number incl. hotel 0
        num_customers = int(parts[1])  # customer number
        num_edges = int(parts[2])  # edge number

        c1_L = int(parts[3])  # max allowed duration of the trip
        c2_D = int(parts[4])  # max performable trip number
        c3_P = int(parts[5])  # min prize count to collect

        logger.debug(num_hotels)
        logger.debug(num_customers)
        logger.debug(num_edges)
        logger.debug(c1_L)
        logger.debug(c2_D)
        logger.debug(c3_P)

        # Initialize instance
        instance = Instance(c1_L, c2_D, c3_P, basename_stem, instance_name)

        self._parse_hotels(input_file, instance, total_hotels)
        self._parse_customers(input_file, instance, num_customers)
        self._parse_edges(input_file, instance, num_edges)

        input_file.close()

        instance.precompute_all_nearest_neighbors()

        return instance

    def _parse_hotels(self, input_file, instance, total_hotels, debug=False):
        # Parse Hotels
        for i in range(total_hotels):
            fee = int(input_file.readline())
            instance.add_hotel(fee)

    def _parse_customers(self, input_file, instance, num_customers, debug=False):

        for i in range(num_customers):
            unparsed = input_file.readline()
            # Remove all leading and trailing white spaces
            split = unparsed.strip().split(' ')
            prize = int(split[0])
            penalty = int(split[1])

            instance.add_customer(prize, penalty)

    def _parse_edges(self, input_file, instance, num_edges, debug=False):
        for i in range(num_edges):
            unparsed = input_file.readline()

            split = unparsed.strip().split(' ')
            vertex_a_number = int(split[0])

            split.pop(0)
            split = (' '.join(split)).strip().split(' ')

            vertex_b_number = int(split[0])

            split.pop(0)
            weight = int(' '.join(split).strip())

            logger.debug("A:" + str(vertex_a_number) + "::B::" + str(vertex_b_number) + "::WEIGHT::" + str(weight))

            instance.add_edge(vertex_a_number, vertex_b_number, weight)
