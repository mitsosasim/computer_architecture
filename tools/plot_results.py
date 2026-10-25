"""Plot archived gem5 results, not new simulation measurements."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def plot(results,output):
    output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,name):
        fig.suptitle('Archived course simulations · reanalysis',fontsize=10,color='#526578',y=1.02)
        fig.savefig(output/(name+'.png'),dpi=160,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');x=np.arange(5)
    for i,p in enumerate(['STATIC','LOCAL','GAg','PAg']):
        rows=[r for r in results['branches'] if r['predictor']==p];ax.bar(x+(i-1.5)*.19,[r['ipc'] for r in rows],.19,label=p)
    ax.set(xticks=x,xticklabels=[f'Benchmark {i}' for i in range(1,6)],ylabel='IPC',title='Branch predictor comparison');ax.legend();save(fig,'branch-prediction')
    fig,axes=plt.subplots(2,3,figsize=(12,6),layout='constrained')
    for ax,param in zip(axes.flat,['LSQ_ENTRIES','ROB_ENTRIES','FUINT_NUM','FUCOM_NUM','FUFP_NUM','FULS_NUM']):
        rows=[r for r in results['cpu'] if r['parameter'].split()[0]==param]
        ax.plot([r['value'] for r in rows],[r['mean_ipc'] for r in rows],'o-',color='#256b8c');ax.set(title=param,xlabel='Resource count',ylabel='Mean IPC');ax.grid(alpha=.2);ax.set_ylim(0,1)
    save(fig,'cpu-resources')
    rows=[r for r in results['memory'] if r['task']==1]
    fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');x=np.arange(3)
    for i,a in enumerate([1,2,4,8]):
        values=[next(r['ipc'] for r in rows if r['parameters']['cacheline_sz']==str(b) and r['parameters']['l1d_assoc']==str(a)) for b in [32,64,128]]
        ax.bar(x+(i-1.5)*.19,values,.19,label=f'{a}-way' if a>1 else 'Direct mapped')
    ax.set(xticks=x,xticklabels=['32','64','128'],xlabel='Cache line size [bytes]',ylabel='Mean IPC across five benchmarks',title='L1 cache configuration sweep');ax.legend();save(fig,'cache-lines')
    rows=[r for r in results['memory'] if r['task']==2]
    fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
    for rp,marker in [('FIFORP','o'),('LRURP','s'),('RandomRP','^')]:
        for clus,color in [('mostly_excl','#26728a'),('mostly_incl','#ad6640')]:
            rs=[r for r in rows if r['parameters']['rp_type']==rp and r['parameters']['l2_clus']==clus]
            ax.scatter([int(r['parameters']['l2_sz'].removesuffix('kB')) for r in rs],[r['ipc'] for r in rs],marker=marker,color=color,label=f'{rp} / {clus}',alpha=.8)
    ax.set(xlabel='L2 capacity [kB]',ylabel='Mean IPC',title='L2 capacity, replacement, and inclusion policy');ax.legend(fontsize=8);save(fig,'l2-policies')
    rows=[r for r in results['memory'] if r['task']==3]
    fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    for pref in ['StridePrefetcher','TaggedPrefetcher']:
        rs=sorted([r for r in rows if r['parameters']['l2_pref']==pref],key=lambda r:int(r['parameters']['pref_deg']))
        for ax,key in zip(axes,['ipc','dram_bytes_per_second']):ax.plot([int(r['parameters']['pref_deg']) for r in rs],[r[key]/(1e9 if key.startswith('dram') else 1) for r in rs],'o-',label=pref)
    axes[0].set(ylabel='Mean IPC',title='Instruction throughput');axes[1].set(ylabel='Mean DRAM bandwidth [GB/s]',title='Memory traffic')
    for ax in axes:ax.set(xlabel='Prefetch degree',xticks=[1,2,3,4]);ax.legend(fontsize=8);ax.grid(alpha=.2)
    save(fig,'prefetchers')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=ROOT/'build/results.json');p.add_argument('--output',type=Path,default=ROOT/'build/plots');a=p.parse_args();plot(json.loads(a.input.read_text()),a.output)
