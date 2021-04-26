sort -g model_serie/ECB.out_k5_alpha0.7 > PLEIN_BLEU/ECB.out_k5_alpha0.7.sorted

python3 remove_empty_predictions.py
