import unittest,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from analyze import parse_stats,branches,cpu_rows,memory_rows
class AnalysisChecks(unittest.TestCase):
 def test_final_dump_does_not_mix_prior_metrics(self):
  self.assertEqual(parse_stats('---------- Begin Simulation Statistics ----------\na 1\nb 2\n---------- Begin Simulation Statistics ----------\na 3\n'),{'a':3.})
 def test_branch_counter_ratio(self):
  rows=branches();self.assertEqual(len(rows),20)
  first=rows[0];self.assertAlmostEqual(first['ipc'],.115598);self.assertAlmostEqual(first['branch_mispredict_ratio'],8004838/72497095)
 def test_workbook_means(self):
  rows=cpu_rows();self.assertEqual(len(rows),25);self.assertAlmostEqual(rows[0]['mean_ipc'],.6102458)
 def test_memory_sweep_and_known_mean(self):
  rows=memory_rows();self.assertEqual(len(rows),370)
  cfg='m5out_TASK:1_cacheline_sz:32_l1d_assoc:1'
  values=[r['ipc'] for r in rows if r['configuration']==cfg]
  self.assertEqual(len(values),5);self.assertAlmostEqual(sum(values)/5,1.0046512)
  self.assertTrue(all(math.isfinite(r[k]) for r in rows for k in ['ipc','l1d_miss_rate','l2_miss_rate','dram_bytes_per_second']))
if __name__=='__main__':unittest.main()
