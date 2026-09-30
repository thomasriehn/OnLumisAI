"""Import approved local media; private originals never enter public/ or Git."""
from pathlib import Path
import argparse, json, shutil, re, html
parser=argparse.ArgumentParser();parser.add_argument('workspace',type=Path);args=parser.parse_args()
workspace=args.workspace.resolve();root=Path(__file__).resolve().parents[1]
source=workspace/'output/video/onlumis-playbooks';private=root/'private/demo';public=root/'public/media'
(private/'assets').mkdir(parents=True,exist_ok=True);(private/'playbooks').mkdir(exist_ok=True);public.mkdir(parents=True,exist_ok=True)
page=(source/'VIDEOS.html').read_text()
base='<base href="/demo/dateien/">'
if '<head>' in page: page=page.replace('<head>','<head>'+base,1)
else: page=re.sub(r'(<html\b[^>]*>)',lambda m:m[1]+base,page,count=1,flags=re.I)
(private/'VIDEOS.html').write_text(page)
for name in ['ABLAUF.md','BEOBACHTUNGEN.md','PRUEFPROTOKOLL.md','LIESMICH.md','SHA256SUMS.txt']:
 shutil.copy2(source/name,private/name)
manifest=json.loads((source/'ablauf.json').read_text());catalogue=[]
for item in manifest:
 id=item['id'];report=json.loads((source/'reports'/f'{id}.json').read_text());video=source/Path(report['output']).name
 shutil.copy2(video,private/video.name);shutil.copy2(source/'assets'/f'{id}_titel.png',private/'assets'/f'{id}_titel.png')
 card=next(x for x in re.findall(r'<article>.*?</article>',page,re.S) if f'>{id}</p>' in x)
 note=re.search(r'<p class="note">(.*?)</p>',card,re.S)
 sec=round(float(report['video_probe']['format']['duration']))
 catalogue.append({'id':id,'version':f"V{item['version']}",'title':item['title'],'file':video.name,'poster':f'assets/{id}_titel.png','duration':f'{sec//60}:{sec%60:02d}','questions':[x['question'] for x in item['prompts']],'closing':item['closing_question'],'note':html.unescape(re.sub('<.*?>','',note[1])) if note else '', 'retake':report.get('retake_date')=='2026-09-30','pdf':item['source_file']})
for p in (workspace/'Daten').glob('OnLumis_Playbook_*.pdf'):shutil.copy2(p,private/'playbooks'/p.name)
(root/'src/data/demo-catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n')
explainer=workspace/'output/video/onlumis-servicetechniker-erklaervideo'
shutil.copy2(explainer/'OnLumisAI_Erklaervideo_Servicetechniker_mit_Thumbnail.mp4',public/'service-erklaervideo.mp4')
# Source image pixels remain unchanged; the browser receives optimized variants via next/image.
for name,original in [('service-cover',explainer/'OnLumisAI_Thumbnail_Servicetechniker_E37.png'),('service-screen',source/'qa/V1_02-q1.png'),('vertrieb-screen',source/'qa/V1_03-q1.png'),('support-screen',source/'qa/V1_04-q1.png')]:shutil.copy2(original,public/(name+'.png'))
# Optional text alternative for the complete narration, without guessed word timings.
(public/'service-transkript.txt').write_text((explainer/'Sprechertext.txt').read_text())
print(f'{len(catalogue)} private videos, three playbooks and public service media imported.')
