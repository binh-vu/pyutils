#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from utils import random
from nose.tools import *


def test_choice_noreplace_with_prob():
    a = [0, 1, 2, 3, 4, 5]
    p = [5, 8, 10, 2, 9, 20]
    p = [float(x) / sum(p) for x in p]

    seed = 1210
    random_state = random.RandomState(seed=seed)
    random_state.set_choice_parameters(a, p)

    np_rand = np.random.RandomState(seed=seed)
    for _ in xrange(100):
        ok_(np.array_equal(random_state.choice(2, replace=False), np_rand.choice(a, 2, replace=False, p=p)))
        ok_(np.array_equal(random_state.choice_p_backup, random_state.choice_p))

def test_choice_noreplace_heavytest():
    a = 400000
    p = [np.random.randint(0, 10000) for _ in xrange(a)]
    total_p = sum(p)
    p = [float(x) / total_p for x in p]

    seed = 1210
    random_state = random.RandomState(seed=seed)
    random_state.set_choice_parameters(a, p)

    np_rand = np.random.RandomState(seed=seed)
    for k in [2, 5, 11]:
        for _ in xrange(500):
            ok_(np.array_equal(random_state.choice(k, replace=False), np_rand.choice(a, k, replace=False, p=p)))
            ok_(np.array_equal(random_state.choice_p_backup, random_state.choice_p))
