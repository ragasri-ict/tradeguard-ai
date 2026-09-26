import pandas as pd
import glob
import os


RAW_FOLDER = "data/raw"
OUTPUT_FILE = "data/raw/nifty_data.csv"


def main():

    print("\n================================")
    print("NIFTY DATA COMBINER")
    print("================================\n")

    # Find all NIFTY historical CSV files
    pattern = os.path.join(
        RAW_FOLDER,
        "NIFTY 50_Historical_PR_*.csv"
    )

    files = glob.glob(pattern)

    if not files:
        print("No NIFTY historical files found.")
        return

    print("NIFTY files found:")
    
    for file in files:
        print(" -", os.path.basename(file))

    all_data = []

    for file in files:

        print(
            "\nReading:",
            os.path.basename(file)
        )

        try:

            df = pd.read_csv(
                file,
                skipinitialspace=True
            )

            # Remove unwanted spaces
            df.columns = [
                str(col).strip()
                for col in df.columns
            ]

            # Find date column
            date_column = None

            for col in df.columns:

                if str(col).strip().lower() == "date":
                    date_column = col
                    break

            if date_column is None:

                print(
                    "WARNING: Date column not found."
                )

                continue

            # Find close column
            close_column = None

            for col in df.columns:

                if str(col).strip().lower() == "close":
                    close_column = col
                    break

            if close_column is None:

                print(
                    "WARNING: Close column not found."
                )

                continue

            # Rename required columns
            df = df.rename(
                columns={
                    date_column: "Date",
                    close_column: "Close"
                }
            )

            # Convert date
            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce"
            )

            # Convert close
            df["Close"] = pd.to_numeric(
                df["Close"],
                errors="coerce"
            )

            # Remove invalid rows
            df = df.dropna(
                subset=["Date", "Close"]
            )

            # Keep required columns
            df = df[
                ["Date", "Close"]
            ]

            all_data.append(df)

            print(
                "Rows:",
                len(df)
            )

        except Exception as e:

            print(
                "ERROR reading file:",
                e
            )

    if not all_data:

        print("\nNo valid NIFTY data found.")
        return

    # Combine all files
    combined = pd.concat(
        all_data,
        ignore_index=True
    )

    # Remove duplicate dates
    combined = combined.drop_duplicates(
        subset=["Date"]
    )

    # Sort by date
    combined = combined.sort_values(
        "Date"
    ).reset_index(drop=True)

    # Calculate NIFTY return
    combined["nifty_return"] = (
        combined["Close"]
        .pct_change()
        * 100
    )

    # Save
    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n================================")
    print("NIFTY COMBINATION COMPLETED")
    print("================================")

    print(
        "\nTotal rows:",
        len(combined)
    )

    print(
        "Start date:",
        combined["Date"].min()
    )

    print(
        "End date:",
        combined["Date"].max()
    )

    print(
        "\nCreated:"
    )

    print(
        "✓",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()