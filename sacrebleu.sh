

#dnet=$PWD/model_serie
dnet=$PWD/model_checkpoint
josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/
data=$josep/data

   # il s'appelle Europarl mais ya les 3 premiers corpus dedans

# jointure fichiers de reference :
for corpus in  ECB EMEA Europarl ; do
  cat $data/clean.Europarl.en-fr.fr.tst >> model_checkpoint/reference

done


model_checkpoint/Europarl.out_k5_avg_alpha0.7 >> python3 $tokenizer -tok_config $data/BPE_config -detok | sacrebleu --force model_checkpoint/reference > model_checkpoint/Europarl.out_k5_avg_alpha0.7.bleu