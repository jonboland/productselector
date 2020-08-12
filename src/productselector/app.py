import itertools
from pathlib import Path

import pandas as pd
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, RIGHT


FILE_NAME = "securitycameras2.csv"
CURRENCY = "£"
MAX_RESULTS = 5

PATH = Path(__file__).resolve().parent / FILE_NAME


class ProductSelector(toga.App):
    def startup(self):
        """Construct and show the application."""
        if FILE_NAME.endswith(".csva"):
            self.df = pd.read_csv(PATH)
        else:
            self.df = pd.read_excel(PATH, sheet_name="Sheet1")
        self.df.sort_values(["Rating"], inplace=True, ascending=False)
        self.df.set_index(self.df.columns[0], inplace=True)

        self.choices = {}.fromkeys(self.df.columns[2:])

        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 640))

        features_label = [
            toga.Label(
                f"Select the {self.df.index.name} features you require:",
                style=Pack(text_align=LEFT, padding_bottom=10),
            )
        ]

        box_style = Pack(direction=ROW, padding_top=10)
        label_style = Pack(flex=1, padding_right=20, text_align=RIGHT)

        self.select_boxes = [
            toga.Box(
                style=box_style,
                children=[
                    toga.Label(feature, style=label_style),
                    toga.Selection(
                        on_select=self.select_feature, items=["N", "Y"], id=feature
                    ),
                ],
            )
            for feature in self.choices
        ]

        get_results = [
            toga.Button(
                label="Get Recommendations",
                on_press=self.generate_results,
                style=Pack(flex=1, padding_top=20),
            )
        ]

        self.results = [
            toga.MultilineTextInput(style=Pack(flex=1, padding_top=20), readonly=True)
        ]

        reset = [
            toga.Button(
                label="Reset All",
                on_press=self.reset_all,
                style=Pack(flex=1, padding_top=20),
            )
        ]

        self.main_window.content = toga.Box(
            style=Pack(direction=COLUMN, padding=30),
            children=features_label
            + self.select_boxes
            + get_results
            + self.results
            + reset,
        )

        self.main_window.show()

    def select_feature(self, selection):
        self.choices[selection.id] = selection.value

    def generate_results(self, button):
        subset_dict = self.filter_products()
        if not subset_dict:
            self.results[0].value = (
                "Unfortunately no products match your criteria.\n"
                "Please remove one or more feature requirements and try again."
            )
        else:
            self.results[0].value = "\n".join(
                f"{k} - {CURRENCY}{v}" for k, v in subset_dict.items()
            )

    def filter_products(self):
        subset = self.df
        for category, choice in self.choices.items():
            if choice == "Y":
                subset = subset[(subset[category] == "Y")]
        subset_dict = subset["Price"].to_dict()
        if MAX_RESULTS:
            subset_dict = dict(itertools.islice(subset_dict.items(), MAX_RESULTS))
        return subset_dict

    def reset_all(self, button):
        for box in self.select_boxes:
            box.children[1].items = ["N", "Y"]
        self.results[0].value = None


def main():
    return ProductSelector()
