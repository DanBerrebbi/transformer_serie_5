import sys
import os
import logging
import torch
import math
import numpy as np
import glob


def numparameters(model):
    npars = 0  # pars
    nbytes = 0  # bytes
    for name, param in model.named_parameters():
        if param.requires_grad:  # learnable parameters only
            npars += param.numel()
            nbytes += param.numel() * param.data.element_size()  # returns size of each parameter
            logging.debug("{} => {} = {} x {} bytes".format(name, list(param.data.size()), param.data.numel(),
                                                            param.data.element_size()))

    name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    if nbytes == 0:
        i = 0
    else:
        i = int(math.floor(math.log(nbytes, 1024)))
        p = math.pow(1024, i)
        nbytes /= p
    size = "{:.2f}{}".format(nbytes, name[i])

    return npars, size


def load_checkpoint(suffix, model, optimizer, device):
    step = 0
    files = sorted(glob.glob("{}.checkpoint_????????.pt".format(suffix)))  ### I check if there is one model
    if len(files) == 0:
        logging.info('No model found')
        sys.exit()

    file = files[-1]  ### last is the newest
    checkpoint = torch.load(file, map_location=device)
    step = checkpoint['step']
    model.load_state_dict(checkpoint['model'])
    optimizer.load_state_dict(checkpoint['optimizer'])
    logging.info('Loaded model/optimizer step={} from {}'.format(step, file))
    return step, model, optimizer  ### this is for learning


def save_checkpoint(suffix, model, optimizer, step, keep_last_n):
    checkpoint = {'step': step, 'model': model.state_dict(), 'optimizer': optimizer.state_dict()}
    torch.save(checkpoint, "{}.checkpoint_{:08d}.pt".format(suffix, step))
    logging.info('Saved {}.checkpoint_{:08d}.pt'.format(suffix, step))
    files = sorted(glob.glob(suffix + '.checkpoint_????????.pt'))
    while keep_last_n > 0 and len(files) > keep_last_n:
        f = files.pop(0)
        os.remove(f)  ### first is the oldest
        logging.debug('Removed checkpoint {}'.format(f))


def load_model(suffix, model, device, fmodel=None):
    if fmodel is not None:
        if not os.path.isfile(fmodel):
            logging.error('No model found')
            sys.exit()
    else:
        files = sorted(glob.glob("{}.checkpoint_????????.pt".format(suffix)))  ### I check if there is one model
        if len(files) == 0:
            logging.info('No checkpoint found')
            sys.exit()
        fmodel = files[-1]  ### last is the newest
    checkpoint = torch.load(fmodel, map_location=device)
    step = checkpoint['step']
    model.load_state_dict(checkpoint['model'])
    logging.info('Loaded model step={} from {}'.format(step, fmodel))
    return step, model


def prepare_source(batch_src, idx_pad, device):
    src = [torch.tensor(seq) for seq in batch_src]  # [bs, ls]
    src = torch.nn.utils.rnn.pad_sequence(src, batch_first=True, padding_value=idx_pad).to(device)  # [bs,ls]
    msk_src = (src != idx_pad).unsqueeze(-2)  # [bs,1,ls] (False where <pad> True otherwise)
    return src, msk_src


def prepare_prefix(batch_pre, idx_pad, device):
    pre = [torch.tensor(seq) for seq in batch_pre]  # [bs, lp]
    pre = torch.nn.utils.rnn.pad_sequence(pre, batch_first=True, padding_value=idx_pad).to(device)  # [bs,lp]
    return pre


def prepare_target(batch_tgt, idx_pad, idx_sep, idx_msk, do_mask_prefix, device):
    tgt = [torch.tensor(seq[:-1]) for seq in batch_tgt]  # delete <eos>
    tgt = torch.nn.utils.rnn.pad_sequence(tgt, batch_first=True, padding_value=idx_pad).to(device)
    ref = [torch.tensor(seq[1:]) for seq in batch_tgt]  # delete <bos>
    ref = torch.nn.utils.rnn.pad_sequence(ref, batch_first=True, padding_value=idx_pad).to(device)
    if do_mask_prefix:
        ref = mask_prefix(ref, idx_sep, idx_msk)
    msk_tgt = (tgt != idx_pad).unsqueeze(-2) & (
                1 - torch.triu(torch.ones((1, tgt.size(1), tgt.size(1)), device=tgt.device),
                               diagonal=1)).bool()  # [bs,lt,lt]
    return tgt, ref, msk_tgt


def mask_prefix(ref, idx_sep, idx_msk):
    # ref is [bs,lt]: idx_pref0 idx_pref1 ... idx_sep idx_tgt0 idx_tgt1 ... <eos> <pad> ...
    # replace tokens of prefix by idx_msk if not present in target
    ind_sep = (ref == idx_sep).nonzero(as_tuple=True)[1]  # [bs] position of idx_sep tokens in ref (one per line)
    assert ref.shape[0] == ind_sep.shape[
        0], 'each reference must contain one and no more than one idx_sep tokens {}!={}'.format(ref.shape,
                                                                                                ind_sep.shape)

    for b in range(ind_sep.shape[0]):
        # logging.info('[prev] ref_b = {}'.format(ref[b].tolist()))
        ind = ind_sep[b].item()
        prefix = ref[b, :ind].tolist()
        target = set(ref[b, ind + 1:].tolist())
        for i in range(len(prefix)):
            if prefix[i] not in target:
                # logging.info('masking i={} idx={} idx={}'.format(i, prefix[i], ref[b][i]))
                ref[b][i] = idx_msk
        # logging.info('[post] ref_b = {}'.format(ref[b].tolist()))
    return ref


##############################################################################################################
### Endcoder_Decoder -> OK #########################################################################################
##############################################################################################################
class Encoder_Decoder(torch.nn.Module):
    # https://www.linzehui.me/images/16005200579239.jpg
    def __init__(self, n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout, share_embeddings, src_voc_size,
                 tgt_voc_size, idx_pad):   # on ne touche pas a src_voc_size car c'est juste le vocabulaire d'une langue, pas du tout la longueur de la phrase
        super(Encoder_Decoder, self).__init__()
        self.idx_pad = idx_pad     # c'est juste un index qui dit ce qu'on met comme indice quand on veut mettre <pad>
        self.src_emb = Embedding(src_voc_size, emb_dim, idx_pad)
        self.sim_emb = Embedding(src_voc_size, emb_dim, idx_pad)   # src_voc_size
        self.pre_emb = Embedding(tgt_voc_size, emb_dim, idx_pad)   # tgt_voc_size
        self.tgt_emb = Embedding(tgt_voc_size, emb_dim, idx_pad)
        if share_embeddings:   # a quoi sert cette ligne ???
            self.tgt_emb.emb.weight = self.src_emb.emb.weight

        self.add_pos_enc = AddPositionalEncoding(emb_dim, dropout, max_len=5000)
        self.stacked_encoder_src = Stacked_Encoder_src(n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.stacked_encoder_sim = Stacked_Encoder_sim(n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.stacked_encoder_pre = Stacked_Encoder_pre(n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.stacked_decoder = Stacked_Decoder(n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.generator = Generator(emb_dim, tgt_voc_size)

    def forward(self, src, sim, pre, tgt, msk_src,msk_sim, msk_pre, msk_tgt):
        # src is [bs,ls]
        # tgt is [bs,lt]
        # msk_src is [bs,1,ls] (False where <pad> True otherwise)
        # mst_tgt is [bs,lt,lt]
        ### encoder sim #####
        sim = self.add_pos_enc(self.sim_emb(sim))  # [bs,ls,ed]
        z_sim = self.stacked_encoder_sim(sim, msk_sim)  # [bs,ls,ed]
        ### encoder sim #####
        src = self.add_pos_enc(self.src_emb(src))  # [bs,ls,ed]
        z_src = self.stacked_encoder_src(src, msk_src, z_sim, msk_sim)  # [bs,ls,ed]
        ### encoder pre #####
        pre = self.add_pos_enc(self.pre_emb(pre))  # [bs,ls,ed]
        z_pre = self.stacked_encoder_pre(pre, msk_pre, z_sim, msk_sim)  # [bs,ls,ed]
        ### decoder #####
        tgt = self.add_pos_enc(self.tgt_emb(tgt))  # [bs,lt,ed]
        z_tgt = self.stacked_decoder(tgt, msk_tgt, z_src, msk_src, z_pre, msk_pre)  # [bs,lt,ed]
        ### generator ###
        y = self.generator(z_tgt)  # [bs, lt, Vt]
        return y  ### returns logits (for learning)

    def encode_src(self, src, msk_src, z_sim, msk_sim):               # je trouve la fonction encode et la fonction decode redondante avec forward
        src = self.add_pos_enc(self.src_emb(src))  # [bs,ls,ed]
        z_src = self.stacked_encoder_src(src, msk_src, z_sim, msk_sim)  # [bs,ls,ed]
        return z_src

    def encode_sim(self, sim, msk_sim):               # je trouve la fonction encode et la fonction decode redondante avec forward
        sim = self.add_pos_enc(self.sim_emb(sim))  # [bs,ls,ed]
        z_sim = self.stacked_encoder_sim(sim, msk_sim)  # [bs,ls,ed]
        return z_sim

    def encode_pre(self, pre, msk_pre, z_sim, msk_sim):               # je trouve la fonction encode et la fonction decode redondante avec forward
        pre = self.add_pos_enc(self.pre_emb(pre))  # [bs,ls,ed]
        z_pre = self.stacked_encoder_pre(pre, msk_pre, z_sim, msk_sim)  # [bs,ls,ed]
        return z_pre

    def decode(self, tgt, msk_tgt, z_src, msk_src, z_pre, msk_pre):
        assert z_src.shape[0] == tgt.shape[0]  ### src/tgt batch_sizes must be equal
        # z_src are the embeddings of the source words (encoder) [bs, sl, ed]
        # tgt is the history (words already generated) for current step [bs, lt]
        tgt = self.add_pos_enc(self.tgt_emb(tgt))  # [bs,lt,ed]
        z_tgt = self.stacked_decoder(tgt, msk_tgt, z_src, msk_src, z_pre, msk_pre)  # [bs,lt,ed]
        y = self.generator(z_tgt)  # [bs, lt, Vt]
        y = torch.nn.functional.log_softmax(y, dim=-1)
        return y  ### returns log_probs (for inference)


##############################################################################################################
### Embedding RAS ################################################################################################
##############################################################################################################
class Embedding(torch.nn.Module):
    def __init__(self, vocab_size, emb_dim, idx_pad):
        super(Embedding, self).__init__()
        self.emb = torch.nn.Embedding(vocab_size, emb_dim, padding_idx=idx_pad)
        self.sqrt_emb_dim = math.sqrt(emb_dim)

    def forward(self, x):
        return self.emb(x) * self.sqrt_emb_dim


##############################################################################################################
### PositionalEncoding RAS #######################################################################################
##############################################################################################################
class AddPositionalEncoding(torch.nn.Module):
    def __init__(self, emb_dim, dropout, max_len=5000):
        super(AddPositionalEncoding, self).__init__()
        assert emb_dim % 2 == 0, 'emb_dim must be pair'
        self.dropout = torch.nn.Dropout(dropout)
        pe = torch.zeros(max_len, emb_dim)  # [max_len=5000, ed]
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)  # [max_len, 1]
        div_term = torch.exp(torch.arange(0, emb_dim, 2).float() * (-math.log(10000.0) / emb_dim))  # [ed/2]
        pe[:, 0::2] = torch.sin(position * div_term)  # [max_len, 1] * [1, ed/2] => [max_len, ed] (pairs of pe)
        pe[:, 1::2] = torch.cos(position * div_term)  # [max_len, 1] * [1, ed/2] => [max_len, ed] (odds of pe)
        pe = pe.unsqueeze(0)  # [1, max_len=5000, ed]
        self.register_buffer('pe',
                             pe)  # register_buffer is for params which are saved&restored in state_dict but not trained

    def forward(self, x):
        bs, l, ed = x.shape
        x = x + self.pe[:, :l]  # [bs, l, ed] + [1, l, ed] => [bs, l, ed]
        return self.dropout(x)


##############################################################################################################
### Stacked_Encoder SRC -> OK ##########################################################################################
##############################################################################################################
class Stacked_Encoder_src(torch.nn.Module):
    def __init__(self, n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(Stacked_Encoder_src, self).__init__()
        self.encoderlayers = torch.nn.ModuleList(
            [Encoder_src(ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout) for _ in range(n_layers)])
        self.norm = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, src, msk_src, z_sim, msk_sim):
        for i, encoderlayer in enumerate(self.encoderlayers):
            src = encoderlayer(src, msk_src, z_sim, msk_sim)  # [bs, ls, ed]
        return self.norm(src)


##############################################################################################################
### Stacked_Encoder SIM -> OK ##########################################################################################
##############################################################################################################
class Stacked_Encoder_sim(torch.nn.Module):
    def __init__(self, n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(Stacked_Encoder_sim, self).__init__()
        self.encoderlayers = torch.nn.ModuleList(
            [Encoder_sim(ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout) for _ in range(n_layers)])
        self.norm = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, sim, msk_sim):
        for i, encoderlayer in enumerate(self.encoderlayers):
            sim = encoderlayer(sim, msk_sim)  # [bs, ls, ed]
        return self.norm(sim)


##############################################################################################################
### Stacked_Encoder PRE -> OK ##########################################################################################
##############################################################################################################
class Stacked_Encoder_pre(torch.nn.Module):
    def __init__(self, n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(Stacked_Encoder_pre, self).__init__()
        self.encoderlayers = torch.nn.ModuleList(
            [Encoder_pre(ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout) for _ in range(n_layers)])
        self.norm = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, pre, msk_pre, z_sim, msk_sim):
        for i, encoderlayer in enumerate(self.encoderlayers):
            pre = encoderlayer(pre, msk_pre, z_sim, msk_sim)  # [bs, ls, ed]
        return self.norm(pre)


##############################################################################################################
### Stacked_Decoder -> OK ##########################################################################################
##############################################################################################################
class Stacked_Decoder(torch.nn.Module):
    def __init__(self, n_layers, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(Stacked_Decoder, self).__init__()
        self.decoderlayers = torch.nn.ModuleList(
            [Decoder(ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout) for _ in range(n_layers)])
        self.norm = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, tgt, msk_tgt, z_src, msk_src, z_pre, msk_pre):
        for i, decoderlayer in enumerate(self.decoderlayers):
            #tgt = decoderlayer(tgt, msk_tgt, z_src, msk_src, z_sim, msk_sim, z_pre, msk_pre)
            tgt = decoderlayer(z_src, z_pre, tgt, msk_src, msk_pre, msk_tgt)
        return self.norm(tgt)


##############################################################################################################
### Encoder SRC -> BUEN ##################################################################################################
##############################################################################################################
class Encoder_src(torch.nn.Module):
    def __init__(self, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(Encoder_src, self).__init__()
        self.multihead_attn_self = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.multihead_attn_enc_sim = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.feedforward = FeedForward(emb_dim, ff_dim, dropout)
        self.norm_att_self = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_att_enc_sim = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_ff = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, src, msk_src, z_sim, msk_sim):
        # NORM
        tmp1 = self.norm_att_self(src)
        # ATTN over source words
        tmp2 = self.multihead_attn_self(q=tmp1, k=tmp1, v=tmp1, msk=msk_src)  # [bs, ls, ed] contains dropout
        # ADD
        tmp = tmp2 + src

        # NORM
        tmp1 = self.norm_att_enc_sim(tmp)
        # ATTN over sim words : q are sim words, k, v are src words
        tmp2 = self.multihead_attn_enc_sim(q=tmp1, k=z_sim, v=z_sim, msk=msk_sim)  # [bs, lt, ed] contains dropout
        # ADD
        tmp = tmp2 + tmp

        # NORM
        tmp1 = self.norm_ff(tmp)
        # FF
        tmp2 = self.feedforward(tmp1)  # [bs, ls, ed] contains dropout
        # ADD
        z = tmp2 + tmp
        return z



##############################################################################################################
### Encoder SIM -> BUEN ##################################################################################################
##############################################################################################################
class Encoder_sim(torch.nn.Module):
    def __init__(self, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(Encoder_sim, self).__init__()
        self.multihead_attn_self = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.feedforward = FeedForward(emb_dim, ff_dim, dropout)
        self.norm_att_self = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_ff = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, sim, msk_sim):
        # NORM
        tmp1 = self.norm_att_self(sim)
        # ATTN over source words
        tmp2 = self.multihead_attn_self(q=tmp1, k=tmp1, v=tmp1, msk=msk_sim)  # [bs, ls, ed] contains dropout
        # ADD
        tmp = tmp2 + sim

        # NORM
        tmp1 = self.norm_ff(tmp)
        # FF
        tmp2 = self.feedforward(tmp1)  # [bs, ls, ed] contains dropout
        # ADD
        z = tmp2 + tmp
        return z



##############################################################################################################
### Encoder PRE ->  BUEN ##################################################################################################
##############################################################################################################
class Encoder_pre(torch.nn.Module):
    def __init__(self, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(Encoder_pre, self).__init__()
        self.multihead_attn_self = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.multihead_attn_enc_sim = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.feedforward = FeedForward(emb_dim, ff_dim, dropout)
        self.norm_att_self = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_att_enc_sim = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_ff = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, pre, msk_pre, z_sim, msk_sim):
        # NORM
        tmp1 = self.norm_att_self(pre)
        # ATTN over source words
        tmp2 = self.multihead_attn_self(q=tmp1, k=tmp1, v=tmp1, msk=msk_pre)  # [bs, ls, ed] contains dropout
        # ADD
        tmp = tmp2 + pre

        # NORM
        tmp1 = self.norm_att_enc_sim(tmp)
        ################################# CROSS ATTN 1 #####################################################
        # ATTN over sim words : q are sim words, k, v are sim words
        tmp2 = self.multihead_attn_enc_sim(q=tmp1, k=z_sim, v=z_sim, msk=msk_sim)  # [bs, lt, ed] contains dropout
        # ADD
        tmp = tmp2 + tmp

        # NORM
        tmp1 = self.norm_ff(tmp)

        # FF
        tmp2 = self.feedforward(tmp1)  # [bs, ls, ed] contains dropout
        # ADD
        z = tmp2 + tmp
        return z



##############################################################################################################
### Decoder -> OK ##################################################################################################
##############################################################################################################
class Decoder(torch.nn.Module):
    def __init__(self, ff_dim, n_heads, emb_dim, qk_dim, v_dim, dropout):

        super(Decoder, self).__init__()
        self.multihead_attn_self = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.multihead_attn_enc_src = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.multihead_attn_enc_pre = MultiHead_Attn(n_heads, emb_dim, qk_dim, v_dim, dropout)
        self.feedforward = FeedForward(emb_dim, ff_dim, dropout)
        self.norm_att_self = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_att_enc_src = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_att_enc_pre = torch.nn.LayerNorm(emb_dim, eps=1e-6)
        self.norm_ff = torch.nn.LayerNorm(emb_dim, eps=1e-6)

    def forward(self, z_src, z_pre, tgt, msk_src, msk_pre, msk_tgt):
        # NORM
        tmp1 = self.norm_att_self(tgt)
        # ATTN over tgt (previous) words : q, k, v are tgt words
        tmp2 = self.multihead_attn_self(q=tmp1, k=tmp1, v=tmp1, msk=msk_tgt)  # [bs, lt, ed] contains dropout
        # ADD
        tmp = tmp2 + tgt


        # NORM
        tmp1 = self.norm_att_enc_src(tmp)
        ################################# CROSS ATTN 2 #####################################################
        # ATTN over src words : q are words from the previous layer, k, v are src words
        tmp3 = self.multihead_attn_enc_src(q=tmp1, k=z_src, v=z_src, msk=msk_src)  # la query reste tmp1 car tmp1 est la variable en sortie du précédent layer
        # ADD
        tmp = tmp3 + tmp

        # NORM
        tmp1 = self.norm_att_enc_pre(tmp)
        ################################# CROSS ATTN 1  #####################################################
        # ATTN over src words : q are words from the previous layer, k, v are src words
        tmp3 = self.multihead_attn_enc_pre(q=tmp1, k=z_pre, v=z_pre, msk=msk_pre)  # la query reste tmp1 car tmp1 est la variable en sortie du précédent layer
        # ADD
        tmp = tmp3 + tmp

        # NORM
        tmp1 = self.norm_ff(tmp)
        # FF
        tmp2 = self.feedforward(tmp1)  # [bs, ls, ed] contains dropout
        # ADD
        z = tmp2 + tmp
        return z




##############################################################################################################
### MultiHead_Attn RAS ###########################################################################################
##############################################################################################################
class MultiHead_Attn(torch.nn.Module):
    def __init__(self, n_heads, emb_dim, qk_dim, v_dim, dropout):
        super(MultiHead_Attn, self).__init__()
        self.nh = n_heads
        self.ed = emb_dim
        self.qd = qk_dim
        self.kd = qk_dim
        self.vd = v_dim
        self.WQ = torch.nn.Linear(emb_dim, qk_dim * n_heads)
        self.WK = torch.nn.Linear(emb_dim, qk_dim * n_heads)
        self.WV = torch.nn.Linear(emb_dim, v_dim * n_heads)
        self.WO = torch.nn.Linear(v_dim * n_heads, emb_dim)
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, q, k, v, msk=None):
        # q is [bs, lq, ed]
        # k is [bs, lk, ed]
        # v is [bs, lv, ed]
        # msk is [bs, 1, ls] or [bs, lt, lt]
        if msk is not None:
            msk = msk.unsqueeze(1)  # [bs, 1, 1, ls] or [bs, 1, lt, lt]
        bs = q.shape[0]
        lq = q.shape[1]  ### sequence length of q vectors (length of target sentences)
        lk = k.shape[1]  ### sequence length of k vectors (may be length of source/target sentences)
        lv = v.shape[1]  ### sequence length of v vectors (may be length of source/target sentences)
        ed = q.shape[2]
        if not bs == v.shape[0] == k.shape[0] :
            K = bs // v.shape[0]
            v = torch.repeat_interleave(v, K, dim = 0)    # je peux faire un repeat_interleaves car c'est le même vecteur pre pour les K options du beam search
            k = torch.repeat_interleave(k, K, dim = 0)
        assert self.ed == q.shape[2] == k.shape[2] == v.shape[2]
        assert lk == lv  # when applied in decoder both refer the source-side (lq refers the target-side)
        Q = self.WQ(q).contiguous().view([bs, lq, self.nh, self.qd]).permute(0, 2, 1,
                                                                             3)  # => [bs,lq,nh*qd] => [bs,lq,nh,qd] => [bs,nh,lq,qd]
       
        K = self.WK(k).contiguous().view([bs, lv, self.nh, self.kd]).permute(0, 2, 1,
                                                                             3)  # => [bs,lk,nh*kd] => [bs,lk,nh,kd] => [bs,nh,lk,kd]
        V = self.WV(v).contiguous().view([bs, lv, self.nh, self.vd]).permute(0, 2, 1,
                                                                             3)  # => [bs,lv,nh*vd] => [bs,lv,nh,vd] => [bs,nh,lv,vd]
        # Scaled dot-product Attn from multiple Q, K, V vectors (bs*nh*l vectors)
        Q = Q / math.sqrt(self.kd)
        s = torch.matmul(Q, K.transpose(2,
                                        3))  # [bs,nh,lq,qd] x [bs,nh,kd,lk] = [bs,nh,lq,lk] # thanks to qd==kd #in decoder lq are target words and lk are source words
        if msk is not None:
            if msk.shape[0] != bs :
                K = bs // msk.shape[0]
                msk = torch.repeat_interleave(msk, K, dim = 0)
            s = s.masked_fill(msk == 0, float('-inf'))  # score=-Inf to masked tokens
        w = torch.nn.functional.softmax(s, dim=-1)  # [bs,nh,lq,lk] (these are the attention weights)
        w = self.dropout(w)  # [bs,nh,lq,lk]

        z = torch.matmul(w, V)  # [bs,nh,lq,lk] x [bs,nh,lv,vd] = [bs,nh,lq,vd] #thanks to lk==lv
        z = z.transpose(1, 2).contiguous().view([bs, lq, self.nh * self.vd])  # => [bs,lq,nh,vd] => [bs,lq,nh*vd]
        z = self.WO(z)  # [bs,lq,ed]
        return self.dropout(z)


##############################################################################################################
### FeedForward RAS ##############################################################################################
##############################################################################################################
class FeedForward(torch.nn.Module):
    def __init__(self, emb_dim, ff_dim, dropout):
        super(FeedForward, self).__init__()
        self.FF_in = torch.nn.Linear(emb_dim, ff_dim)
        self.FF_out = torch.nn.Linear(ff_dim, emb_dim)
        self.dropout = torch.nn.Dropout(dropout)  # this regularization is not used in the original model

    def forward(self, x):
        tmp = self.FF_in(x)
        tmp = torch.nn.functional.relu(tmp)
        tmp = self.dropout(tmp)
        tmp = self.FF_out(tmp)
        tmp = self.dropout(tmp)
        return tmp


##############################################################################################################
### Generator RAS ################################################################################################
##############################################################################################################
class Generator(torch.nn.Module):
    def __init__(self, emb_dim, voc_size):
        super(Generator, self).__init__()
        self.proj = torch.nn.Linear(emb_dim, voc_size)  # [bs, Vt]

    def forward(self, x):
        y = self.proj(x)
        return y


