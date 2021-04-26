sort -g model_serie_plein/news-commentary-v14.out_k5_alpha0.7 > PLEIN_BLEU/news-commentary-v14.out_k5_alpha0.7.sorted

python3 remove_empty_predictions.py
