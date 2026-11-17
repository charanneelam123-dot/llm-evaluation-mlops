from fastapi import Header,HTTPException
from pydantic import BaseModel,Field
from platform_common import application,bounded,create,read,operator
from evaluator import CASES,PROMPTS,evaluate

app=application('LLM Evaluation & MLOps','Versioned evaluation cases, deterministic graders, MLflow tracking and operational metrics.')


class Evaluation(BaseModel):
    live:bool=False
    limit:int=Field(default=12,ge=1,le=12)


class Compare(BaseModel):
    left_id:str
    left_token:str
    right_id:str
    right_token:str


@app.get('/api/dataset')
def dataset():return {'cases':[{k:c[k] for k in ('id','question','context','expected')} for c in CASES],'prompts':PROMPTS}


@app.post('/api/evaluate',status_code=201)
def run(body:Evaluation,x_admin_token:str=Header(default='')):
    if body.live:operator(x_admin_token)
    with bounded():
        try:report=evaluate(body.live,body.limit)
        except ValueError as error:raise HTTPException(422,str(error)) from None
        return create(report)


@app.get('/api/runs/{run_id}')
def get_run(run_id:str,x_run_token:str=Header(default='')):return read(run_id,x_run_token)


@app.post('/api/compare')
def compare(body:Compare):
    left,right=read(body.left_id,body.left_token),read(body.right_id,body.right_token)
    if left['dataset_sha256']!=right['dataset_sha256'] or left['mode']!=right['mode']:
        raise HTTPException(422,'Only matching datasets and execution modes can be compared')
    return {'left':left['id'],'right':right['id'],'deltas':{variant:{key:right['summary'][variant][key]-value for key,value in values.items()} for variant,values in left['summary'].items()}}
