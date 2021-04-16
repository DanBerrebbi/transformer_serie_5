

#dnet=$PWD/model_serie
dnet=$PWD/model_checkpoint
josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/
data=$josep/data
fref=$data/clean.$corpus.en-fr.fr.tst

input = $dnet/corpus.out_k5_avg_alpha0.7

$input > python3 $tokenizer -tok_config $data/BPE_config -detok | sacrebleu --force $fref > $input.bleu