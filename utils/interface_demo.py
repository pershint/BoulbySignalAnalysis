# coding: utf-8
import WATCHMAKERSInterface as wmi
import pandas as pd
import uproot
import matplotlib.pyplot as plt
import seaborn as sns
import LikelihoodCalculator as lc

sns.set_context("poster")

loader = wmi.WATCHMAKERSLoader("/home/onetrueteal/share/WATCHMAN/WATCHMAN_ForLeon/WbLS_3pct_QFitResults/")
pos = loader.OpenMergedData("IBDPositron_LIQUID_ibd_p").get("data")
neu = loader.OpenMergedData("IBDNeutron_LIQUID_ibd_n").get("data")
Tl208 = loader.OpenMergedData("208Tl_PMT_CHAIN_232Th_NA").get("data")

print(pos.keys())
pos_pe = pos.get('pe').array()
plt.hist(pos_pe,bins=30,range=(0,200))
plt.show()

pos_truez = pos.get('mcz')
pos_qz = pos.get('zQFit')
pos_truez_arr = pos_truez.array()
pos_qz_arr = pos_qz.array()
plt.hist(pos_truez_arr-pos_qz_arr)

pos_truex = pos.get('mcx')
pos_qx = pos.get('xQFit')
pos_truex_arr = pos_truex.array()
pos_qx_arr = pos_qx.array()
plt.hist(pos_truex_arr-pos_qx_arr)

pos_truey = pos.get('mcy')
pos_qy = pos.get('yQFit')
pos_truey_arr = pos_truey.array()
pos_qy_arr = pos_qy.array()
plt.hist(pos_truey_arr-pos_qy_arr)
plt.show()
