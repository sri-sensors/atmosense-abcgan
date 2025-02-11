import unittest
import os
from abcgan import persist
from abcgan import model
import abcgan.mean_estimation as me
import abcgan.constants as const
import torch

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.join(dir_path, 'data')
# ensure data directory is present
if not os.path.exists(dir_path):
    os.mkdir(dir_path)

fname = 'test'
param_file = os.path.join(dir_path, fname + '.pt')
info_file = os.path.join(dir_path, fname + '.json')


def gen_modules():
    tgen = me.Transformer()
    gen = model.Generator(tgen)
    tcrit = me.Transformer()
    crit = model.Critic(tcrit)
    return gen, crit

# generate fake inputs


def test_modules(gen, crit):
    n_batch = 10
    n_alt = const.max_alt
    n_bv_feat = const.n_bv_feat
    n_dr_feat = const.n_driver_feat

    driver_src = torch.zeros(n_batch, n_dr_feat)
    bv_src = torch.zeros(n_batch, n_alt, n_bv_feat)

    gen_output = gen(driver_src, bv_src)
    gen_valid = not gen_output.isnan().any().item()
    crit_output = crit(bv_src, driver_src, bv_src)
    crit_valid = not crit_output.isnan().any().item()
    return gen_valid, crit_valid


class Persist(unittest.TestCase):

    def test_persist(self):
        if os.path.exists(param_file):
            os.remove(param_file)
        if os.path.exists(info_file):
            os.remove(info_file)
        gen, crit = gen_modules()
        persist.persist(gen, crit, fname, dir_path)
        self.assertTrue(os.path.exists(param_file))
        self.assertTrue(os.path.exists(info_file))

    def test_recreate(self):
        if not os.path.exists(param_file):
            gen_in, crit_in = gen_modules()
            persist.persist(gen_in, crit_in, fname, dir_path)
        gen, crit = persist.recreate(fname, dir_path)
        # test that loaded modules are working
        gen_valid, crit_valid = test_modules(gen, crit)
        self.assertTrue(gen_valid)
        self.assertTrue(crit_valid)


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
