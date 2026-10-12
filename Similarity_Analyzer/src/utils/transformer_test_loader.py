import pandas as pd
from torch.utils.data import Dataset, DataLoader


class FunctionPairDataset(Dataset):

    def __init__(self, csv_path):
        df = pd.read_csv(csv_path)

        self.texts_a = df["code_a"].tolist()
        self.texts_b = df["code_b"].tolist()

        self.pair_ids = list(zip(df["function_a_id"], df["function_b_id"]))

    def __len__(self):
        return len(self.texts_a)

    def __getitem__(self, idx):
        return (
            self.texts_a[idx],
            self.texts_b[idx],
            self.pair_ids[idx]
        )


def get_loader(csv_path, batch_size=32):
    dataset = FunctionPairDataset(csv_path)

    def collate(batch):
        a, b, ids = zip(*batch)
        return list(a), list(b), list(ids)

    return DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=collate)