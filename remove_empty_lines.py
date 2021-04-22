

with open('data_corpus/val_sim') as f:
    lines_sim = f.readlines()
    f.close()
with open('data_corpus/val_src') as f:
    lines_src = f.readlines()
    f.close()
with open('data_corpus/val_tgt') as f:
    lines_tgt= f.readlines()
    f.close()
with open('data_corpus/val_pre') as f:
    lines_pre = f.readlines()
    f.close()


src, tgt, sim, pre = [], [], [], []

for i, line in enumerate(lines_sim):
    if line != '\n' :
        src.append(lines_src[i])
        tgt.append(lines_tgt[i])
        pre.append(lines_pre[i])
        sim.append(lines_sim[i])


with open('data_corpus/val_src_plein', 'w') as f:
    for line in src:
        f.write(line)

with open('data_corpus/val_sim_plein', 'w') as f:
    for line in sim:
        f.write(line)

with open('data_corpus/val_pre_plein', 'w') as f:
    for line in pre:
        f.write(line)

with open('data_corpus/val_tgt_plein', 'w') as f:
    for line in tgt:
        f.write(line)



print(50*"%")

print("val ok")




with open('data_corpus/trn_sim') as f:
    lines_sim = f.readlines()
    f.close()
with open('data_corpus/trn_src') as f:
    lines_src = f.readlines()
    f.close()
with open('data_corpus/trn_tgt') as f:
    lines_tgt= f.readlines()
    f.close()
with open('data_corpus/trn_pre') as f:
    lines_pre = f.readlines()
    f.close()


src, tgt, sim, pre = [], [], [], []

for i, line in enumerate(lines_sim):
    if line != '\n' :
        src.append(lines_src[i])
        tgt.append(lines_tgt[i])
        pre.append(lines_pre[i])
        sim.append(lines_sim[i])


with open('data_corpus/trn_src_plein', 'w') as f:
    for line in src:
        f.write(line)

with open('data_corpus/trn_sim_plein', 'w') as f:
    for line in sim:
        f.write(line)

with open('data_corpus/trn_pre_plein', 'w') as f:
    for line in pre:
        f.write(line)

with open('data_corpus/trn_tgt_plein', 'w') as f:
    for line in tgt:
        f.write(line)


print(50*"%")
print("trn ok")