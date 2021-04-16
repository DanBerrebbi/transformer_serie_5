

#dnet=$PWD/model_serie
dnet=$PWD/model_checkpoint
josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/
data=$josep/data

input = $dnet/Europarl.out_k5_avg_alpha0.7    # il s'appelle Europarl mais ya les 3 premiers corpus dedans
fref = $dnet/reference

# jointure fichiers de reference :
for corpus in  ECB EMEA Europarl ; do
  cat $data/clean.Europarl.en-fr.fr.tst >> $fref


done


$input > python3 $tokenizer -tok_config $data/BPE_config -detok | sacrebleu --force $fref > $input.bleu