"""Render a finished local run without changing labels, prompts, or raw outputs."""
import argparse
import csv
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--portfolio',type=Path);args=parser.parse_args()
    folder=ROOT/'docs/real-model-evaluation'
    r=json.loads((folder/'report.json').read_text(encoding='utf-8'))
    cases={c['id']:c for c in json.loads((folder/'cases.json').read_text(encoding='utf-8'))}
    rows=[json.loads(line) for line in (folder/'outputs.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(rows)==80 and len(cases)==40
    summary=r['summary'];b=summary['baseline'];g=summary['grounded']
    interpretation='Both prompts matched the required short answer in 35 of 40 cases. The baseline returned “Not specified” on the five missing-evidence cases, which fails the fixed abstention label despite communicating absence. The grounded prompt used the required abstention label but omitted USD on all five rent-increase answers. Citation formatting and extra sources account for much of the difference in joint passes. The longer prompt did not improve strict joint compliance in this run.'
    pct=lambda n: f'{n/40:.1%}'
    md=['# Real-model results: local Llama 3.2','',f"Run completed {r['finished_at']}. Model `{r['model']}`, digest `{r['model_digest']}`, quantization `{r['model_details']['quantization_level']}`.",'','40 authored cases across eight categories; two frozen prompts; 80 measured local inference calls. No fixture answers were used as model responses.','', '| Measure | Baseline | Grounded |','|---|---:|---:|']
    for title,key in [('Strict joint passes','passed'),('Strict answer matches','strict_answer_matches'),('Exact citation-set matches','citation_set_matches'),('Provider errors','errors')]:
        md.append(f'| {title} | {b[key]}/40 | {g[key]}/40 |')
    md += [f"| Median local wall time | {b['median_wall_ms']/1000:.2f} s | {g['median_wall_ms']/1000:.2f} s |",'', '## Category results','', '| Category | Baseline joint passes | Grounded joint passes |','|---|---:|---:|']
    for category in b['by_category']:
        md.append(f"| {category} | {b['by_category'][category]['passed']}/5 | {g['by_category'][category]['passed']}/5 |")
    md += ['', '## What the score means','', 'A joint pass requires a strict accepted-answer match and the exact expected citation set. Extra citations, bracket-wrapped IDs, and otherwise correct verbose answers can fail this contract. This is not a semantic hallucination or general intelligence score. The two prompts are compared as written; they were not tuned against these outputs.','', '## Inspect the evidence','', '- [Method and reproduction](README.md)', '- [Full report](report.json)', '- [Every input and accepted answer](cases.json)', '- [Raw model outputs, token counts, errors, and timings](outputs.jsonl)', '- [Frozen prompts, model digest, and settings](manifest.json)', '- [Failure table](failures.csv)', '', '## Limits', '']+['- '+w for w in r['warnings']]
    md += ['', '## Failure analysis', '', interpretation]
    (folder/'results.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    with (folder/'failures.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['case_id','category','variant','answer','expected_answers','citations','expected_citations','strict_answer_match','citation_set_match','error'])
        for row in rows:
            if row['grade']['passed']:continue
            c=cases[row['case_id']];o=row['output'] or {}
            writer.writerow([row['case_id'],row['category'],row['variant'],o.get('answer'),json.dumps(c['accepted_answers']),json.dumps(o.get('citations')),json.dumps(c['expected_citations']),row['grade']['strict_answer_match'],row['grade']['citation_set_match'],row['error']])
    if not args.portfolio:return
    import shutil
    target=args.portfolio/'dist/evaluation'
    target.mkdir(parents=True,exist_ok=True)
    for name in ['report.json','manifest.json','cases.json','outputs.jsonl','failures.csv']:
        shutil.copyfile(folder/name,target/name)
    esc=html.escape
    category_rows=''.join(f"<tr><th scope='row'>{esc(k.replace('_',' '))}</th><td>{b['by_category'][k]['passed']}/5</td><td>{g['by_category'][k]['passed']}/5</td></tr>" for k in b['by_category'])
    # Display contrasting failure types rather than selecting only favourable outputs.
    picks=[]
    for condition in [lambda x: x['grade']['strict_answer_match'] and not x['grade']['citation_set_match'],lambda x: x['category']=='missing_evidence' and not x['grade']['strict_answer_match'],lambda x: x['grade']['passed']]:
        selected=next((x for x in rows if condition(x)),None)
        if selected:picks.append(selected)
    examples=''
    for row in picks:
        c=cases[row['case_id']]
        examples+=f"<details><summary>{esc(row['case_id'])} / {esc(row['variant'])} / {'joint pass' if row['grade']['passed'] else 'contract failure'}</summary><p><strong>Question:</strong> {esc(c['question'])}</p><pre>{esc(json.dumps(row['output'],indent=2))}</pre><p><strong>Accepted answers:</strong> {esc(', '.join(c['accepted_answers']))}<br><strong>Required citations:</strong> {esc(json.dumps(c['expected_citations']))}<br>Answer match: {row['grade']['strict_answer_match']}; citation set match: {row['grade']['citation_set_match']}.</p></details>"
    section=f'''<section id="real-evaluation" class="real-evaluation shell" aria-labelledby="real-evaluation-title"><div class="section-top"><div><span class="label">MEASURED NOVEMBER 18, 2026 / LOCAL INFERENCE</span><h2 id="real-evaluation-title">A real model. A visible scorecard.</h2></div><p>Llama 3.2 · 3.2B · Q4_K_M<br>40 cases / two prompts / 80 calls</p></div><p class="eval-intro">I ran the installed Llama model through Ollama on a fixed, synthetic challenge set. The questions cover missing evidence, conflicting versions, calculations, document instructions, and citation rules. Every model response is available below.</p><div class="metric-table"><table><caption>One response per case and prompt; strict output-contract scoring</caption><thead><tr><th scope="col">Measure</th><th scope="col">Baseline prompt</th><th scope="col">Grounded prompt</th></tr></thead><tbody><tr><th scope="row">Answer + citation contract passes</th><td>{b['passed']}/40 ({pct(b['passed'])})</td><td>{g['passed']}/40 ({pct(g['passed'])})</td></tr><tr><th scope="row">Strict answer matches</th><td>{b['strict_answer_matches']}/40</td><td>{g['strict_answer_matches']}/40</td></tr><tr><th scope="row">Exact citation-set matches</th><td>{b['citation_set_matches']}/40</td><td>{g['citation_set_matches']}/40</td></tr><tr><th scope="row">Provider errors</th><td>{b['errors']}</td><td>{g['errors']}</td></tr><tr><th scope="row">Median local wall time</th><td>{b['median_wall_ms']/1000:.2f} s</td><td>{g['median_wall_ms']/1000:.2f} s</td></tr></tbody></table></div><p class="eval-caveat">These are strict task-compliance results, not semantic accuracy or a hallucination rate. A correct answer with an extra source or bracket-wrapped ID can fail. “Not specified” also fails the fixed “Insufficient evidence” label. Local timings depend on this machine and do not describe the hosted app.</p><details class="category-breakdown"><summary>Inspect all eight categories</summary><div class="metric-table"><table><thead><tr><th scope="col">Category</th><th scope="col">Baseline</th><th scope="col">Grounded</th></tr></thead><tbody>{category_rows}</tbody></table></div></details><div class="eval-examples"><h3>Read the answers behind the score</h3>{examples}</div><div class="eval-downloads"><a href="evaluation/report.json" download>Full result JSON <i class="bi bi-download" aria-hidden="true"></i></a><a href="evaluation/outputs.jsonl" download>All 80 raw outputs <i class="bi bi-download" aria-hidden="true"></i></a><a href="evaluation/cases.json" download>Dataset and labels <i class="bi bi-download" aria-hidden="true"></i></a><a href="evaluation/manifest.json" download>Prompts and model digest <i class="bi bi-download" aria-hidden="true"></i></a><a href="https://github.com/charanneelam123-dot/llm-evaluation-mlops/blob/main/docs/real-model-evaluation/README.md" target="_blank" rel="noopener">Method and reproduction <i class="bi bi-arrow-up-right" aria-hidden="true"></i></a></div><p class="evidence-note">Small authored challenge set: five related cases per category, a single local run, no prompt tuning after seeing results, and no external benchmark claim. This tests grounded answering and output contracts; it does not evaluate agent tool selection.</p></section>'''
    page=args.portfolio/'dist/index.html';text=page.read_text(encoding='utf-8')
    if 'id="real-evaluation"' not in text:text=text.replace('<section id="case-studies"',section+'<section id="case-studies"')
    text=text.replace('Prepared outputs test the evaluation harness. Live-model quality and latency benchmarks are still pending.','The hosted app uses prepared outputs. A separate local Llama 3.2 run below records 80 real inference calls.')
    text=text.replace('No real-model quality or latency result is claimed.','A separate local Llama 3.2 evaluation now records 80 real inference calls across 40 cases; the scorecard above publishes every output and its limits.')
    text=text.replace('<link rel="stylesheet" href="case-studies.css">','<link rel="stylesheet" href="case-studies.css"><link rel="stylesheet" href="evaluation.css">')
    text=text.replace('<a href="#work">Work</a>','<a href="#work">Work</a><a href="#real-evaluation">Evaluation</a>')
    page.write_text(text,encoding='utf-8')
    current=page.read_text(encoding='utf-8')
    current=current.replace('<div class="eval-examples"><h3>',f'<p class="eval-intro">{esc(interpretation)}</p><div class="eval-examples"><h3>')
    page.write_text(current,encoding='utf-8')
    js=args.portfolio/'dist/app.js';code=js.read_text(encoding='utf-8').replace('Prepared outputs test the evaluation harness. Live-model quality and latency benchmarks are still pending.','The hosted app uses prepared outputs. A separate local Llama 3.2 run below records 80 real inference calls.');js.write_text(code,encoding='utf-8')

if __name__=='__main__':main()
