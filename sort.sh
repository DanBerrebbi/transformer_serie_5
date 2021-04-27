sort -g model_serie/Europarl.out_k5_alpha0.7 > PLEIN_BLEU/Europarl.out_k5_alpha0.7.sorted

python3 remove_empty_predictions.py
