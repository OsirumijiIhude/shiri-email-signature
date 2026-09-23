#!/usr/bin/env python3
"""Run unchanged v6 regressions with only the approved release identity/count updated,
then run the additional logo, visual active-state and deep-link checks."""
from pathlib import Path
import argparse,json
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--chromium',default='/usr/bin/chromium');a=p.parse_args()
source=(HERE/'test_polish_v6.py').read_text()
assert "page.locator('.brand-original img').count()==39" in source
source=source.replace("page.locator('.brand-original img').count()==39","page.locator('.brand-original img').count()==34")
source=source.replace('studio-polish-seo-v6-20260922','brands-nav-v7-20260923').replace('all 39 real logos','all 34 approved logos').replace('original profile slide','updated brands view').replace('v6 identity','v7 identity').replace('polish-v6-report.json','full-v7-report.json').replace('CMA_V6_QA','CMA_V7_FULL_QA')
ns={'__name__':'v7_full_regression','__file__':str(HERE/'test_polish_v6.py')}
exec(compile(source,str(HERE/'test_polish_v6.py'),'exec'),ns)
ns['run'](a.directory.resolve(),a.chromium)
from test_brand_nav_v7 import run
run(a.directory.resolve(),a.chromium)
qa=a.directory/'__qa';full=json.loads((qa/'full-v7-report.json').read_text());focused=json.loads((qa/'brands-nav-v7-report.json').read_text())
combined={'version':'brands-nav-v7-20260923','origin':'local HTTP release server','original_artwork':True,'passed':full['passed']+focused['passed'],'failed':full['failed']+focused['failed'],'errors':full['errors']+focused['errors'],'suites':[{'report':'full-v7-report.json','passed':full['passed'],'failed':full['failed']},{'report':'brands-nav-v7-report.json','passed':focused['passed'],'failed':focused['failed']}]}
(qa/'report.json').write_text(json.dumps(combined,indent=2)+'\n')
print('CMA_V7_ALL_QA '+json.dumps(combined),flush=True)
