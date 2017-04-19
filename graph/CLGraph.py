import numpy as np
import ROOT

def CLGraph(data):
    bs,b1 = np.sort(data), data*0+1
    x,y = [],[]
    xOld,cnt = 0,0
    tot = float(np.sum(b1))
    hc = ROOT.TH1D('hc','hc',np.max(data),0+0.5,np.max(data)+0.5)
    gc = ROOT.TGraph()

    for i,idx in enumerate(bs):
        print 'a',idx,i
        if xOld != idx:
            if xOld != 0:
                print idx,i
                hc.Fill(idx,i/tot)
                gc.SetPoint(cnt,idx,i/tot*100.)
                cnt+=1
        xOld = idx

    gc.Draw('al')
    return gc

if __name__ == "__main__":
    print("AAH")
