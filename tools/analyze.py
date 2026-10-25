"""Rebuild analysis from archived simulator statistics and the CPU workbook."""
import argparse,csv,gzip,json,re,statistics
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assignments'
KEYS={'ipc':'system.cpu.ipc','l1d_miss_rate':'system.cpu.dcache.overallMissRate::total','l2_miss_rate':'system.l2cache.overallMissRate::total','dram_bytes_per_second':'system.mem_ctrl.dram.bwTotal::total'}
def parse_stats(text):
    result={}
    for line in text.splitlines():
        if 'Begin Simulation Statistics' in line:result={}
        fields=line.split()
        if len(fields)>1:
            try:result[fields[0]]=float(fields[1])
            except ValueError:pass
    return result

def branches():
    text=(A/'01_branch_prediction/all_stats.txt').read_text()
    rows=[];predictor=None;benchmark=None;lines=[]
    def finish():
        if benchmark and predictor:
            values=parse_stats('\n'.join(lines))
            rows.append(dict(predictor=predictor,benchmark=benchmark,ipc=values['system.cpu.ipc'],branch_mispredict_ratio=values['system.cpu.commit.branchMispredicts']/values['system.cpu.branchPred.lookups']))
    for line in text.splitlines():
        if 'PREDICTOR' in line:
            finish();benchmark=None;lines=[];predictor=line.split()[0]
        elif 'Begin Simulation Statistics benchmark' in line:
            finish();benchmark=re.search(r'benchmark\d+',line)[0];lines=[]
        else:lines.append(line)
    finish()
    if len(rows)!=20:raise ValueError(f'Expected 20 branch runs, got {len(rows)}')
    return rows

def cpu_rows():
    ns={'t':'urn:oasis:names:tc:opendocument:xmlns:table:1.0','o':'urn:oasis:names:tc:opendocument:xmlns:office:1.0'}
    with ZipFile(A/'02_cpu_resources/sim2_stats.ods') as z:root=ET.fromstring(z.read('content.xml'))
    result=[]
    for row in root.findall('.//t:table-row',ns):
        values=[]
        for c in row:
            if not c.tag.endswith('table-cell'):continue
            v=c.get('{'+ns['o']+'}value',' '.join(c.itertext()).strip())
            values.extend([v]*min(int(c.get('{'+ns['t']+'}number-columns-repeated','1')),64))
        if len(values)<8:continue
        try:bench=[float(v) for v in values[2:7]];stored=float(values[7]);value=float(values[1])
        except ValueError:continue
        avg=statistics.mean(bench)
        if abs(avg-stored)>1e-6:raise ValueError('Workbook mean does not match benchmark cells')
        result.append(dict(parameter=values[0],value=value,**{f'benchmark{i+1}':b for i,b in enumerate(bench)},mean_ipc=avg))
    return result

def memory_rows():
    rows=[]
    for path in sorted((A/'03_memory_hierarchy/data').glob('benchmark*.jsonl.gz')):
        with gzip.open(path,'rt') as f:
            for line in f:
                record=json.loads(line);v=parse_stats(record['stats']);cfg=record['configuration']
                # Split on known parameter-key boundaries to preserve underscores.
                params={}
                for match in re.finditer(r'(?:^|_)(TASK|cacheline_sz|l1d_assoc|l2_sz|l2_assoc|rp_type|l2_clus|l2_pref|pref_deg):',cfg):
                    tail=cfg[match.end():];end=re.search(r'_(?:TASK|cacheline_sz|l1d_assoc|l2_sz|l2_assoc|rp_type|l2_clus|l2_pref|pref_deg):',tail)
                    params[match[1]]=tail[:end.start()] if end else tail
                rows.append(dict(benchmark=path.name.split('.')[0],configuration=cfg,task=int(params['TASK']),parameters=params,**{k:v[key] for k,key in KEYS.items()}))
    counts={task:sum(r['task']==task for r in rows) for task in (1,2,3)}
    if counts!={1:60,2:270,3:40}:raise ValueError(f'Incomplete sweep: {counts}')
    return rows

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def run(output):
    output.mkdir(parents=True,exist_ok=True)
    branch,cpu,memory=branches(),cpu_rows(),memory_rows()
    write_csv(output/'branches.csv',branch);write_csv(output/'cpu.csv',cpu)
    write_csv(output/'memory.csv',[{k:v for k,v in r.items() if k!='parameters'} for r in memory])
    grouped={}
    for row in memory:grouped.setdefault(row['configuration'],[]).append(row)
    means=[]
    for cfg,rows in sorted(grouped.items()):
        if len(rows)!=5 or len({r['benchmark'] for r in rows})!=5:raise ValueError('Incomplete benchmark group '+cfg)
        means.append(dict(configuration=cfg,task=rows[0]['task'],parameters=rows[0]['parameters'],**{k:statistics.mean(r[k] for r in rows) for k in KEYS}))
    result=dict(branches=branch,cpu=cpu,memory=means,scope='Reanalysis of archived results; not new gem5 simulation runs')
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Analyzed {len(branch)} branch runs, {len(cpu)} CPU workbook rows, and {len(memory)} memory runs / {len(means)} configurations.')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build');args=p.parse_args();run(args.output)
