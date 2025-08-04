from aicb.data_prep.awel_reader import AwelReader

import pandas as pd

data = pd.read_csv("../data/2023_originalfile_nonicknames.csv")

data.head()["gesprek anoniem"][0]

len(data)

cols = data["gesprek anoniem"]

reader = AwelReader("../data/2023_originalfile_nonicknames.csv")

conversations = reader.load_conversations()

print(cols[0])

c = conversations[50]
c.messages

print(c.raw)
