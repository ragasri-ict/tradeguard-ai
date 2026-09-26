import pandas as pd
import glob
import os


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

INPUT_FOLDER = "data/raw/events"
OUTPUT_FILE = "data/raw/company_events.csv"


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def main():

    print("\n================================")
    print("COMPANY EVENTS COMBINER")
    print("================================\n")

    # Find all CSV files inside events folder
    files = glob.glob(
        os.path.join(INPUT_FOLDER, "*.csv")
    )

    if not files:
        print("ERROR: No CSV files found.")
        print("Put your NSE Company Announcements and")
        print("Company Actions CSV files inside:")
        print(INPUT_FOLDER)
        return

    print("Files found:")
    for file in files:
        print(" -", os.path.basename(file))

    all_data = []

    # --------------------------------------------------
    # READ EACH FILE
    # --------------------------------------------------

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

            print("Columns:")
            print(list(df.columns))

            # --------------------------------------------------
            # FIND DATE COLUMN
            # --------------------------------------------------

            date_column = None

            possible_date_columns = [
                "Broadcast Date",
                "Date",
                "BROADCAST DATE",
                "EVENT DATE",
                "Event Date",
                "Record Date",
                "Ex Date"
            ]

            for col in df.columns:

                if str(col).strip().lower() in [
                    x.lower()
                    for x in possible_date_columns
                ]:
                    date_column = col
                    break

            # --------------------------------------------------
            # FIND SYMBOL
            # --------------------------------------------------

            symbol_column = None

            possible_symbol_columns = [
                "Symbol",
                "SYMBOL",
                "NSE Symbol",
                "Security"
            ]

            for col in df.columns:

                if str(col).strip().lower() in [
                    x.lower()
                    for x in possible_symbol_columns
                ]:
                    symbol_column = col
                    break

            # --------------------------------------------------
            # FIND COMPANY
            # --------------------------------------------------

            company_column = None

            possible_company_columns = [
                "Company Name",
                "COMPANY NAME",
                "Company",
                "Name"
            ]

            for col in df.columns:

                if str(col).strip().lower() in [
                    x.lower()
                    for x in possible_company_columns
                ]:
                    company_column = col
                    break

            # --------------------------------------------------
            # FIND SUBJECT
            # --------------------------------------------------

            subject_column = None

            possible_subject_columns = [
                "Subject",
                "SUBJECT",
                "Purpose",
                "PURPOSE"
            ]

            for col in df.columns:

                if str(col).strip().lower() in [
                    x.lower()
                    for x in possible_subject_columns
                ]:
                    subject_column = col
                    break

            # --------------------------------------------------
            # CREATE STANDARD DATAFRAME
            # --------------------------------------------------

            clean_df = pd.DataFrame()

            # Date
            if date_column is not None:

                clean_df["date"] = pd.to_datetime(
                    df[date_column],
                    errors="coerce"
                )

            else:

                print("WARNING: Date column not found.")
                continue

            # Symbol
            if symbol_column is not None:

                clean_df["symbol"] = (
                    df[symbol_column]
                    .astype(str)
                    .str.strip()
                )

            else:

                clean_df["symbol"] = ""

            # Company
            if company_column is not None:

                clean_df["company"] = (
                    df[company_column]
                    .astype(str)
                    .str.strip()
                )

            else:

                clean_df["company"] = ""

            # Subject
            if subject_column is not None:

                clean_df["subject"] = (
                    df[subject_column]
                    .astype(str)
                    .str.strip()
                )

            else:

                clean_df["subject"] = ""

            # --------------------------------------------------
            # EVENT TYPE
            # --------------------------------------------------

            filename = os.path.basename(file).lower()

            if "action" in filename:

                clean_df["event_type"] = "Corporate Action"

            else:

                clean_df["event_type"] = "Corporate Announcement"

            # --------------------------------------------------
            # DETAILS
            # --------------------------------------------------

            clean_df["details"] = (
                clean_df["subject"]
            )

            # Source
            clean_df["source"] = "NSE"

            # Keep only valid dates
            clean_df = clean_df.dropna(
                subset=["date"]
            )

            print(
                "Valid rows:",
                len(clean_df)
            )

            all_data.append(clean_df)

        except Exception as e:

            print(
                "ERROR reading file:",
                e
            )

    # --------------------------------------------------
    # COMBINE ALL FILES
    # --------------------------------------------------

    if not all_data:

        print("\nNo valid data found.")
        return

    combined = pd.concat(
        all_data,
        ignore_index=True
    )

    # --------------------------------------------------
    # KEEP ONLY 2023-2025
    # --------------------------------------------------

    combined = combined[
        (combined["date"] >= "2023-01-01") &
        (combined["date"] <= "2025-12-31")
    ]

    # --------------------------------------------------
    # CLEAN SYMBOLS
    # --------------------------------------------------

    combined["symbol"] = (
        combined["symbol"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------

    combined = combined.drop_duplicates()

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------

    combined = combined.sort_values(
        ["date", "symbol"]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------
    # FINAL INFORMATION
    # --------------------------------------------------

    print("\n================================")
    print("COMPANY EVENTS COMPLETED")
    print("================================")

    print("\nTotal rows:", len(combined))

    if len(combined) > 0:

        print(
            "Start date:",
            combined["date"].min()
        )

        print(
            "End date:",
            combined["date"].max()
        )

        print(
            "Companies:",
            combined["symbol"].nunique()
        )

        print("\nSymbols found:")

        for symbol in sorted(
            combined["symbol"].dropna().unique()
        ):

            if symbol != "":

                print("✓", symbol)

    print("\nCreated:")
    print("✓", OUTPUT_FILE)


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    main()