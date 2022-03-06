def calculateWithdrawCost(progress, tokenMinted):
    if progress >= 100:
        return 0
    elif progress <= 67:
        return tokenMinted + (
            (((20 * tokenMinted) / 100) * (100 - ((progress * 3) / 2))) / 100
        )
    else:
        return (tokenMinted * (100 - ((progress - 67) * 3))) / 100
