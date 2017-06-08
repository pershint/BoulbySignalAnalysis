import numpy as np
import ROOT

def CLGraph(data):
    bs,b1 = np.sort(np.array(data)), np.array(data)*0+1
    x68 = bs[int(len(bs)*.683)]
    x95 = bs[int(len(bs)*0.95)]
    x,y = [],[]
    xOld,cnt = 0,0
    tot = float(np.sum(b1))
    hc = ROOT.TH1D('hc','hc',np.max(data),0+0.5,np.max(data)+0.5)
    gc = ROOT.TGraph()
    CLLines = ["l68":ROOT.TLine(),"l95":ROOT.TLine()]
    for key in CLLines:
        CLLines[key].SetY1(0.0)
        CLLines[key].SetY2(1e6)

    l68.SetX1(100.)
    l68.SetX2(100.01)
    l68.SetY1(0.)
    l68.SetY2(100.)

    l68 = ROOT.TLine()
    l68.SetX1(100.)
    l68.SetX2(100.01)
    l68.SetY1(0.)
    l68.SetY2(100.)

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
    return gc, l68, l95

if __name__ == "__main__":
    print("AAH")
