import pandas as pd
import glob
import os

RAW_FOLDER = "data/raw/sector"
OUTPUT_FILE = "data/raw/sector_data.csv"


def main():

    print("\n================================")
    print("SECTOR DATA COMBINER")
    print("================================\n")

    # Find all sector historical CSV files
    pattern = os.path.join(
        RAW_FOLDER,
        "NIFTY *_Historical_PR_*.csv"
    )

    files = glob.glob(pattern)

    if not files:
        print("No sector historical files found.")
        return

    print("Sector files found:")

    for file in files:
        print(" -", os.path.basename(file))

    all_data = []

    for file in files:

        print("\nReading:", os.path.basename(file))

        try:

            df = pd.read_csv(
                file,
                skipinitialspace=True
            )

            # Clean column names
            df.columns = [
                str(col).strip()
                for col in df.columns
            ]

            # Find index name column
            index_column = None

            for col in df.columns:

                if str(col).strip().lower() in [
                    "index name",
                    "index"
                ]:
                    index_column = col
                    break

            # Find date column
            date_column = None

            for col in df.columns:

                if str(col).strip().lower() == "date":
                    date_column = col
                    break

            # Find close column
            close_column = None

            for col in df.columns:

                if str(col).strip().lower() == "close":
                    close_column = col
                    break

            # Check required columns
            if date_column is None:

                print("WARNING: Date column not found.")
                continue

            if close_column is None:

                print("WARNING: Close column not found.")
                continue

            # If Index Name is not present,
            # get sector name from filename
            if index_column is None:

                sector_name = (
                    os.path.basename(file)
                    .split("_Historical")[0]
                    .strip()
                )

                df["Index Name"] = sector_name

            else:

                df = df.rename(
                    columns={
                        index_column: "Index Name"
                    }
                )

            # Rename columns
            df = df.rename(
                columns={
                    date_column: "Date",
                    close_column: "Close"
                }
            )

            # Convert Date
            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce"
            )

            # Convert Close
            df["Close"] = pd.to_numeric(
                df["Close"],
                errors="coerce"
            )

            # Remove invalid rows
            df = df.dropna(
                subset=[
                    "Date",
                    "Close"
                ]
            )

            # Keep required columns
            df = df[
                [
                    "Index Name",
                    "Date",
                    "Close"
                ]
            ]

            all_data.append(df)

            print("Rows:", len(df))

        except Exception as e:

            print(
                "ERROR reading file:",
                e
            )

    # Check if any valid data was found
    if not all_data:

        print("\nNo valid sector data found.")
        return

    # Combine all files
    combined = pd.concat(
        all_data,
        ignore_index=True
    )

    # Remove duplicate sector/date rows
    combined = combined.drop_duplicates(
        subset=[
            "Index Name",
            "Date"
        ]
    )

    # Sort data
    combined = combined.sort_values(
        [
            "Index Name",
            "Date"
        ]
    ).reset_index(
        drop=True
    )

    # Calculate sector daily return
    combined["sector_return"] = (
        combined
        .groupby("Index Name")["Close"]
        .pct_change()
        * 100
    )

    # Save combined file
    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # Final output
    print("\n================================")
    print("SECTOR COMBINATION COMPLETED")
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
        "Number of sectors:",
        combined["Index Name"].nunique()
    )

    print("\nSectors found:")

    for sector in sorted(
        combined["Index Name"].unique()
    ):

        print("✓", sector)

    print("\nCreated:")

    print("✓", OUTPUT_FILE)


if __name__ == "__main__":
    main()