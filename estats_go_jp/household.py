import os

import pandas as pd
import requests


class Household:
    def __init__(self):
        self.res = []

    def fetch(self):
        self.res = requests.get(
            "http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
            f"?appId={os.getenv('APP_ID')}&lang=J&statsDataId=0003000808"
        ).json()["GET_STATS_DATA"]["STATISTICAL_DATA"]

    @property
    def value(self) -> pd.DataFrame:
        df = pd.DataFrame(self.res["DATA_INF"]["VALUE"])
        return df.rename(columns={c: c.replace("@", "") for c in df.columns})

    @property
    def classes(self) -> list:
        return self.res["CLASS_INF"]["CLASS_OBJ"]

    @property
    def classnames(self) -> list:
        return [{"id": c["@id"], "name": c["@name"]} for c in self.classes]

    def get_class_values(self, id_):
        return [r[1].iloc[1] for r in self.get_class(id_).drop_duplicates().iterrows()]

    def get_class(self, id_):
        for c in self.classes:
            if c["@id"] == id_:
                if isinstance(c["CLASS"], dict):
                    df = pd.DataFrame([c["CLASS"]])
                elif isinstance(c["CLASS"], list):
                    df = pd.DataFrame(c["CLASS"])

                df = df.rename(columns={"@code": c["@id"], "@name": c["@name"]})
                return df[[c["@id"], c["@name"]]]

    def dataframe(self):
        df = self.value
        for cls in self.classes:
            df = (
                df.merge(self.get_class(cls["@id"]), on=cls["@id"])
                .drop(columns=[cls["@id"]])
            )
        df = df.rename(columns={"$": "値", "unit": "単位"})
        return df[[*[c["@name"] for c in self.classes], "単位", "値"]]
