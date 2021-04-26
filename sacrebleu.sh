

josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/
data=$josep/data
tokenizer=tools/tokenizer.py
fref=$data/clean.news-commentary-v14.en-fr.fr.tst

sort -g model_serie_plein/news-commentary-v14.out_k5_alpha0.7 | cut -f 2 | python3 $tokenizer -tok_config $data/BPE_config -detok | sacrebleu --force $fref > model_serie_plein/news-commentary-v14.out_k5_alpha0.7.bleu

cat model_serie_plein/news-commentary-v14.out_k5_alpha0.7.bleu
