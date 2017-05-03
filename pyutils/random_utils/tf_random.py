#!/usr/bin/python
# -*- coding: utf-8 -*-

import tensorflow as tf

# %%

class CudaRandomState(object):

    def __init__(self, max_draw, seed=None):
        self.seed = seed
        self.graph = tf.Graph()

        with self.graph.as_default():
            # Load variable to calculate the prob
            # self.prob = tf.placeholder(tf.float32, shape=(1, None))
            self.prob = tf.Variable(p_single)
            self.multinomial = tf.multinomial(self.prob, max_draw)
            self.uniform = tf.random_uniform((max_draw,), minval=0, maxval=1)

            # Load session
            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
            self.session = tf.Session(config=config)

    def choice(self, size=None, replace=True):
        assert replace is False, 'Not support True yet'
        return self.session.run(self.multinomial)

if __name__ == '__main__':
    rand = CudaRandomState(5)

    # %%

    import numpy as np

    a = 500000
    p = [np.random.randint(0, 10000) for _ in xrange(a)]
    total_p = sum(p)
    p = np.asarray([float(x) / total_p for x in p]).reshape((1, -1))

    # %%

    with rand.graph.as_default():
        print rand.session.run(rand.multinomial, feed_dict={
            rand.prob: p
        })

    # %%
