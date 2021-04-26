

#dnet=$PWD/model_serie
dnet=$PWD/model_checkpoint
josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/
data=$josep/data
tokenizer=../tools/tokenizer.py
fref=$data/clean.ECB.en-fr.fr.tst


sort -g pred.tst | cut -f 2 | python3 $tokenizer -tok_config $data/BPE_config -detok | sacrebleu --force ref.tst > ECB_plein.bleu
