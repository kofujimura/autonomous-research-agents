"""Small actual-target implementation check; never a complete main analysis."""
from build_population import build
from predict_fixed import predict
from draw_audits import make
from audit_inference import run

manifest='data/population-pipeline-check-v1.json'
build(manifest)
model='results/pipeline-check/model-tessera-broad'
predict('results/source-models-v2/logistic-broad-tessera',manifest,model)
draws='results/pipeline-check/audit-draws'
make(manifest,draws)
run(model,draws+'/manifest.json','results/pipeline-check/inference',max_units=2)
