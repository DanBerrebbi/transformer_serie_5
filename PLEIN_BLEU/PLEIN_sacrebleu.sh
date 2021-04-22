

#dnet=$PWD/model_serie
dnet=$PWD/model_checkpoint
josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/
data=$josep/data
tokenizer=tools/tokenizer.py
fref=$data/clean.Europarl.en-fr.fr.tst

ref | python3 $tokenizer -tok_config $data/BPE_config -detok > ref_detok

sort -g ref | cut -f 2 | python3 $tokenizer -tok_config $data/BPE_config -detok | sacrebleu --force $ref_detok > Europarl_plein.bleu
