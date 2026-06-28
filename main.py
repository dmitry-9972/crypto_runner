from interface import Interface
from comparer import Comparer

comparer = Comparer()
comparer.refresh_all_exchanges_and_prices()
short_dict_for_interface = comparer.prepare_sorted_data_for_interface()


if __name__ == "__main__":
    app = Interface(short_dict_for_interface, comparer)
    app.mainloop()