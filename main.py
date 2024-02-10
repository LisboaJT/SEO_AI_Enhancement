import pandas as pd
from utils import main
from config import CSV_INPUT_PATH


if __name__ == "__main__":
    df = pd.read_csv(CSV_INPUT_PATH)
    main(df)
