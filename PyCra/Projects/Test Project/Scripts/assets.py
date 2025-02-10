"""
Includes all needed import modules for all files
"""

import pygame as pg
pg.init()
pg.font.init()
pg.joystick.init()
from pygame._sdl2 import Window, Renderer, Image, Texture
import numpy as np
from glm import vec2, vec3, vec4, normalize, length, cos, sin, atan, ceil, degrees, distance, dot, abs
from math import inf
import sys
import os
import screeninfo
from random import random, randint, choice, choices, seed
from time import time, perf_counter, sleep
from tkinter import filedialog
from copy import copy
import ctypes
import hid
import subprocess
import shutil
import pickle
import gzip
import shlex
import winreg
import types
import importlib.util

RUN_BY_PROJECT = False
if os.path.basename(os.path.dirname(__file__)) == "Scripts":
    project_root = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(project_root)
    RUN_BY_PROJECT = os.path.basename(project_root) != "PyCra"
    os.chdir(project_root)
RUN_BY_ENGINE = not RUN_BY_PROJECT
