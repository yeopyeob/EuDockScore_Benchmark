"""Finetune the model on predicting FNAT"""
import warnings
from Bio import BiopythonDeprecationWarning

# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", BiopythonDeprecationWarning)
import torch
import torch.utils as utils
import torch.nn as nn
from eudockscore.equiformer_v2_resi.model_v2_new import EuBERT
from eudockscore.equiformer_v2_resi.data_new import EDN_Transform
import torch_geometric

# from atom3d.datasets import LMDBDataset
from atom3d.datasets import LMDBDataset

# Silence tokenizer warnings
import logging

# import warnings

logging.disable(logging.WARNING)
warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings('ignore', message="/home/kimlab5/mmcfee/")
import traceback

fnat_model = EuBERT().to("cuda").train().float()
# fnat_model = torch.compile(fnat_model)
# Load checkpoint
try:
    check = torch.load("checkpoint.pth")
    fnat_model.load_state_dict(check["model_state_dict"])
except Exception:
    print("No checkpoint found", flush=True)

# Load data
train_dataset = LMDBDataset(
    "./edn_data/train_lmdb",
    transform=EDN_Transform(
        True,
        csv_file="./train_gdock_no_ab_large.csv",
        nlp_model="./pretrained",
    ),
)

train_dl = torch_geometric.loader.DataLoader(
    train_dataset, batch_size=5, shuffle=True, num_workers=4
)
val_dataset = LMDBDataset(
    "./edn_data/val_lmdb",
    transform=EDN_Transform(
        True,
        csv_file="./val_gdock_no_ab_large.csv",
        nlp_model="./pretrained",
    ),
)

val_dl = torch_geometric.loader.DataLoader(
    val_dataset, batch_size=5, shuffle=True, num_workers=4
)

# Optimizer
optimizer = torch.optim.Adam(fnat_model.parameters(), lr=1e-3)

# Configuration for training
MAX_EPOCHS = 50
SAVE_EPOCHS = 1
SAVE_PATH = "./fnat_model.pth"

# Logging
running_train = []
running_val = []
train_losses = []
val_losses = []
train_acc = []
val_acc = []
running_train_acc = []
running_val_acc = []

# Loss function
loss_func = nn.CrossEntropyLoss(
    weight=torch.tensor([1.0, 1.0]).to("cuda"),
)

softmax = nn.Softmax(dim=-1)

for epoch in range(MAX_EPOCHS):
    running_train = []
    running_val = []
    running_train_acc = []
    running_val_acc = []
    for i, batch in enumerate(train_dl):
        try:
            batch = batch.to("cuda")
            outputs = fnat_model(batch)  # seq=batch.seq.to("cuda"))
        except Exception:
            # traceback.print_exc()
            continue

        # Compute loss and gradients
        optimizer.zero_grad()
        try:
            # print(batch.label.squeeze())
            loss = loss_func(outputs.float(), batch.label.to("cuda").squeeze().long())
            print(loss)
        except Exception:
            # traceback.print_exc()
            continue

        # Do backprop
        # torch.nn.utils.clip_grad_norm_(fnat_model.parameters())
        if not torch.isnan(loss):
            loss.backward()
            optimizer.step()
            running_train.append(loss.item())
            probs = softmax(outputs)
            preds = torch.argmax(probs, dim=-1)
            check = preds.view(-1) == batch.label.to("cuda").squeeze().view(-1)
            good_point_idx = batch.label.to("cuda").long() != -100
            good_point_idx = good_point_idx.nonzero(as_tuple=True)[0]
            check = check.float()
            acc = torch.mean(check[good_point_idx])
            running_train_acc.append(acc.item())
        # Periodically check val loss and save model:
        if (i + 1) % 100 == 0:
            train_losses.append(sum(running_train) / len(running_train))
            running_train = []
            train_acc.append(sum(running_train_acc) / len(running_train_acc))

            # Check val loss
            fnat_model.eval()
            for ii, batch_val in enumerate(val_dl):
                # Only check a random 10k examples
                if (ii + 1) == 100:
                    break
                try:
                    with torch.no_grad():
                        batch_val = batch_val.to("cuda")
                        outputs_val = fnat_model(batch_val)
                        # seq=batch_val.seq.to("cuda"),
                except Exception:
                    # print(traceback.print_exc(), flush=True)
                    continue

                # Compute loss and gradients
                try:
                    loss_val = loss_func(
                        outputs_val.float(),
                        batch_val.label.squeeze().long(),
                    )
                except Exception:
                    # print(traceback.print_exc(), flush=True)
                    continue

                if not torch.isnan(loss_val):
                    running_val.append(loss_val.item())
                    print(loss_val.item(), flush=True)
                    probs_val = softmax(outputs_val)
                    preds_val = torch.argmax(probs_val, dim=-1)
                    check_val = preds_val.view(-1) == batch_val.label.to(
                        "cuda"
                    ).squeeze().view(-1)
                    check_val = check_val.float()
                    # Ignore bad data points
                    good_point_idx = batch_val.label.to("cuda").long() != -100
                    good_point_idx = good_point_idx.nonzero(as_tuple=True)[0]
                    acc_val = torch.mean(check_val[good_point_idx])
                    running_val_acc.append(acc_val.item())

            # Get the total val loss
            val_losses.append(sum(running_val) / len(running_val))
            running_val = []
            val_acc.append(sum(running_val_acc) / len(running_val_acc))
            running_val_acc = []
            running_train_acc = []

            # Reset the model to train model
            fnat_model.train()

            # Record current losses
            with open("train_losses.txt", "a") as f_train:
                f_train.write(str(train_losses[-1]) + "\n")
            with open("val_losses.txt", "a") as f_val:
                f_val.write(str(val_losses[-1]) + "\n")
            with open("train_acc.txt", "a") as f_train_acc:
                f_train_acc.write(str(train_acc[-1]) + "\n")
            with open("val_acc.txt", "a") as f_val_acc:
                f_val_acc.write(str(val_acc[-1]) + "\n")

            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": fnat_model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "loss": train_losses[-1],
                },
                "./saved_models/fnat_" + str(epoch) + "_" + str(i + 1) + ".pth",
            )

    if epoch % SAVE_EPOCHS == 0 and epoch != 0:
        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": fnat_model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "loss": train_losses[-1],
            },
            SAVE_PATH,
        )
