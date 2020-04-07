import os
import re

from github import Github
import requests
import pandas as pd


def validate_columns(columns_all):
    """
    Compares the contents of the family columns.csvs , looking for issues
    """
    unique_column_names = {}

    issues = {"repeated 'title' column entry": {}}

    has_issues = False
    for family, df in columns_all.items():

        # Checks against unique item names
        for item in list(df["title"].unique()):
            if item in unique_column_names.keys():
                has_issues = True
                if item in issues["repeated 'title' column entry"].keys():
                    issues["repeated 'title' column entry"][item].append(family)
                else:
                    issues["repeated 'title' column entry"][item] = [family]
            else:
                unique_column_names[item] = family

    if has_issues:
        return issues
    else:
        return None

def scan():
    TOKEN = os.getenv("GITHUB_TOKEN", None)

    if TOKEN is None:
        raise Exception("Failed to get github token")

    g = Github(TOKEN)

    codelists_all = {}
    columns_all = {}
    components_all = {}

    all_issues = {}

    with open("./families.txt") as f:
        for family_url in f:

            family_url = str(family_url).strip()

            print("Getting", family_url)
            family_repo = g.get_repo(family_url)

            codelists_all[family_url] = []
            columns_all[family_url] = []
            components_all[family_url] = []

            # Get the codelist.csv names
            for c in family_repo.get_contents("/reference/codelists"):

                c = str(c)
                if ".csv" in c:
                    name = c.split("/")[-1].split("?")[0].rstrip('")')
                    codelists_all[family_url].append(name)

            # Get columns info
            columns_path = [str(x).split('path="')[1].rstrip('")') for x in family_repo.get_contents("/reference") if "columns.csv" in str(x)][0]
            column_url = "https://raw.githubusercontent.com/{}/master/{}".format(family_url, str(columns_path).strip())
            column_df = pd.read_csv(column_url)
            columns_all[family_url] = column_df

            # Get component info
            component_path = [str(x).split('path="')[1].rstrip('")') for x in family_repo.get_contents("/reference") if "components.csv" in str(x)][0]
            component_url = "https://raw.githubusercontent.com/{}/master/{}".format(family_url, str(component_path).strip())
            component_df = pd.read_csv(component_url)
            components_all[family_url] = component_df

    all_issues["Column file issues"] = validate_columns(columns_all)

    return all_issues
