import glob
import pandas as pd

# Список файлов в директории
file_list = glob.glob("out2/*.csv")

# Чтение файлов и объединение их в один DataFrame, отсекая заголовок
df = pd.concat([pd.read_csv(f, header=0) for f in file_list], ignore_index=True)

# Сохранение объединенного DataFrame в файл
df.to_csv("out2/reviews_list.csv", index=False)
