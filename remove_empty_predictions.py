

with open('/nfs/RESEARCH/crego/projects/PrimingNMT-2/stovec/clean.ECB.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.sim') as f:
    lines_sim = f.readlines()
    f.close()

with open('PLEIN_BLEU/ECB.out_k5_alpha0.7.sorted') as f:
    lines_pred = f.readlines()
    f.close()

with open('/nfs/RESEARCH/crego/projects/PrimingNMT-2/data/clean.ECB.en-fr.fr.tst') as f:
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