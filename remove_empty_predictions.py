

with open('/nfs/RESEARCH/crego/projects/PrimingNMT-2/stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.sim') as f:
    lines_sim = f.readlines()
    f.close()

with open('model_serie/Europarl.out_k5_alpha0.7') as f:
    lines_pred = f.readlines()
    f.close()

with open('/nfs/RESEARCH/crego/projects/PrimingNMT-2/data/clean.Europarl.en-fr.fr.tst') as f:
    lines_ref = f.readlines()
    f.close()


ref, pred = [], []
for i, line in enumerate(lines_sim):
    if line != '\n' :
        ref.append(lines_ref[i])
        pred.append(lines_pred[i])


with open('PLEIN_BLEU/ref.tst', 'w') as f:
    for line in ref:
        f.write(line)

with open('PLEIN_BLEU/pred.tst', 'w') as f:
    for line in pred:
        f.write(line)