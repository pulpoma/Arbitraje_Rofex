def plot_prices(dataframe):
    import matplotlib as plt
    # plt.figure(figsize=(18, 10))
    x = dataframe.index
    y_bid = dataframe['bid'].loc[x]
    y_offer = dataframe['offer'].loc[x]
    y_last = dataframe['last'].loc[x]

    plt.plot(x, y_bid, color='red', marker='o', label='Bid - Colocadora')
    plt.plot(x, y_offer, color='green', marker='X', label='Offer - Tomadora')
    plt.plot(x, y_last, color='black', linestyle='dashed', alpha=0.5, label='last')

    plt.title('Futuros')
    plt.xlabel('Future Contract')
    plt.ylabel('Precio')

    plt.legend()
    plt.tight_layout()
    plt.show()