

#dnet=$PWD/model_serie
dnet=$PWD/model_checkpoint
josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/
data=$josep/data
tokenizer=$josep/MiNMT/tools/tokenizer.py

   # il s'appelle Europarl mais ya les 3 premiers corpus dedans

# jointure fichiers de reference :
for corpus in  ECB EMEA Europarl ; do
  cat $data/clean.$corpus.en-fr.fr.tst > model_checkpoint/reference

done

#cp model_checkpoint/Europarl.out_k5_avg_alpha0.7 Europarl.out_k5_avg_alpha0.7.trans
# model_checkpoint/Europarl.out_k5_avg_alpha0.7
cat model_checkpoint/Europarl.out_k5_avg_alpha0.7 | python3 $tokenizer -tok_config $data/BPE_config -detok > model_checkpoint/Europarl.out_k5_avg_alpha0.7.trans

#| sacrebleu --force model_checkpoint/reference > model_checkpoint/Europarl.out_k5_avg_alpha0.7.bleu