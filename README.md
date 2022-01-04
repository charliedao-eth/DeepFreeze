# DeepFreeze

How much would you pay to remove 1 ETH from circulating supply for 1 year?

Deep Freeze is a tokenized patience protocol that enables being paid by the market to explicitly *do nothing* with an asset. No yield farming, no lending, no staking. Be paid to do nothing, and thus keep ETH out of circulation. This enables _implicit_ yield for raw ETH held in cold storage.

## Links 

Full white paper available at: https://charliedao.eth.limo/DeepFreeze/DeepFreeze_Simulations.html

A simulations report analyzing 5 different potential "market patience" profiles is available: https://charliedao.eth.limo/DeepFreeze/DeepFreeze_Simulations.html

## Intro

Deep Freeze is an in-development protocol for storing long-term holdings within a user generated smart contract. These “freezers” serve as on-chain cold storage. Users can (but are not required to) add a custom password-hash pair to protect these long term holdings. If they get hacked, their wallet will get drained by the hackers, but ownership of the freezer can be safely transferred to a new wallet, protecting their long term holdings, by using the password-hash (and a private transaction to prevent front-running by the hackers).

This is a great solution for those who dislike the poor UX of hardware wallets, but don’t want to trust a custodian like Coinbase with their assets or juggle multiple accounts. 

But what if you want to protect your long term holdings while also generating yield? 

Currently, you can trust your assets to a smart contract that pays extrinsic yield, such as AAVE which generates yield from collateralized borrowing of assets. AAVE then gives you a derivative version of your asset (e.g., deposit ETH and get AAVE’s aETH) and you can put that derivative token in long term storage. It’s value (in ETH terms) will grow over time at some variable rate.

This works now, many do it, but it does expose you to a few types of risk. 

(1) The ever-present smart contract risk.

There could be a bug in the code and the protocol gets hacked. Although for a blue chip like AAVE, this risk is very low and they’re trusted with billions of dollars of assets accordingly.

(2) Risk to yield. 

Yield generating protocols are actively managed. Many use upgradeable proxy contracts. As they release new upgraded versions of their offerings, the market will react. If you have your assets in AAVE V2 (released 12/2020), as they launch AAVE V3 (released 11/2021) the market will shift to using V3. AAVE V2 depositors will generate less yield, and many will migrate accordingly. This exposes you to the headache of also migrating or exposes you to potential issues with AAVE doing the migration for you (see: upgradeable proxy contracts and (1)). 

Again, AAVE is a blue chip DeFi protocol trusted with billions of dollars. It’s probably one of the safest places in all of DeFi to store assets. This is not an attack on AAVE, the writers of this paper are active AAVE users and fans of the protocol. The point is *extrinsic* yield has risks that make them less suitable for long term holdings (e.g., multi-year)- not only smart contract risks (which can be minimized) but also risk to yield that requires the user to do something (e.g., migrate).

Deep Freeze solves this problem using a game theory approach that tokenizes patience. The more patient you are, the more you can earn. You earn it all upfront. What you do with your yield is up to you. The yield is intrinsic. But the value of that yield, is market determined- are you more patient than the average investor? Are you more patient than the market as a whole?

## Concept [Shortened from white paper]

Alice has 100 ETH. She doesn’t really need 100 ETH in her hot wallet, she can probably get by with 10 ETH in her everyday account(s) and 90 ETH in long term storage. She considers herself very patient and wants to try out Deep Freeze.

She goes to the Deep Freeze site and creates a Freezer with a 90 ETH deposit. She goes ahead and adds a password-hash to protect it as well (this is optional). She goes to an online keccak hash calculator (you can play with one [here](https://emn178.github.io/online-tools/keccak_256.html), go ahead type some words and see the hash) and gives the freezer the hash:

ee42aa7ea02389608005edf2e64e2b0f425680c27835914d855f036b61f24b58

She safely writes down the English phrase that generates this hash when passed to any Keccak-256 calculator (including the one that is built into Ethereum). Even if you hack Alice, you aren’t going to get her 90 ETH unless you can figure out what words in the English language hash to that value. Good luck, quantum computers have not broken Keccak-256 yet.

Her long term assets are safe behind (1) freezer ownership (only the owner can withdraw) and (2) the English phrase that generates the hash she provided.

Now Alice needs to decide- how patient is she? 

Deep Freeze enables her to lock her ETH for any desired amount of time and get the “freezer” version of her asset as yield – ETH generates frETH. This yield is intrinsic and paid upfront. But it’s still a gamble on her own patience because early withdrawals are penalized.

![image](https://user-images.githubusercontent.com/96018507/148110869-914960bf-af91-40c7-bc50-08407cf87ae9.png)

She decides to lock her 90 ETH for 3 years. She receives (90 * 3 years) = 270 frETH.

Her lock is initiated with a 20% penalty on Day 0. Her break-even day is 67% of her lock time, here, 2 years later, or Day 730, where the cost is the same as her initial yield (270 frETH). At the end of her lock time, 3 years later, or Day 1095, she has earned all her yield and it costs 0 frETH to unlock.

| Minted | Day 0 Withdraw Cost | Day 365 Withdraw Cost | Day 730 Withdraw Cost | Day 912 Withdraw Cost| Day 1095 Withdraw Cost |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| 270 frETH   | 324 frETH   | 297 frETH   | 270 frETH   | 135 frETH   | 0 frETH     |


Her early withdrawal cost depends on if she is before or after her break-even day. It is a simple linear function of her progress toward either the breakeven day or her final day (whichever hasn’t happened yet). The penalty decreases slowly until the breakeven day, afterwards, her profit rises extremely quickly. This is to maximize the incentive of waiting the entire lock period.

## FAQs

### Why would frETH be valued?

1 frETH = 1 ETH removed from market for 1 year

Who benefits when ETH is removed from the market for 1 year? 

All holders of ETH benefit! Reducing the available supply of ETH, puts upward pressure on the price of ETH.

Bob has 20 ETH and $4000 USDC. If ETH is $4,000, he can buy 1 ETH, taking 1 ETH off the market for as long as he wants and putting a small upward pressure on ETH’s price. If frETH is 0.02 ETH; he could instead buy 50 frETH. Remember what a frETH is: 

1 frETH = 1 ETH removed from market for 1 year

Bob buying 50 frETH is equivalent to paying to remove 50 ETH from the market for 1 year. This directly increases the cost for Alice to withdraw early and indirectly puts upward pressure on the price of ETH.

Now of course, there’s no guarantee that 50 frETH grows in value the way 1 ETH might grow in value. But it’s the kind of game theory that brings investors that want to manipulate short term supply, gamble on the aggregate of people’s individual patience (will Alice withdraw early and sell?), and profit from high volume trading between pairs of assets (here, frETH / ETH).

In summary, Deep Freeze creates a pure free market for tokenized patience itself. Non-users of Deep Freeze can engage in this market, hoard frETH to increase the cost of impatience (early withdrawal) and profit both directly from trading frETH and indirectly by reducing the supply of ETH available in other markets- similar to how staked ETH is expected to reduce the circulating supply of ETH.

### What Happens if frETH is dumped?

The price of frETH plummets, that’s what happens! But remember:

1 frETH = [1 ETH removed from market for 1 year]

This will never change – it is the essence of how frETH is valued. To get a better understanding of how a natural equilibrium will be found (as a function of the market’s reaction to changing prices of patience), review this diagram:

![image](https://user-images.githubusercontent.com/96018507/148112271-f1b763e2-d7d8-4678-8650-e0dbcc8ae087.png)

The cheaper the frETH, the cheaper impatience. The cheaper impatience, the more early withdrawals we’ll see. Early withdrawals that pay penalties burn frETH. Burnt frETH forces a corresponding amount of ETH to be patient. This ETH that is forced to be patient reduces circulating supply, which puts upward pressure on the price of ETH. Higher priced ETH also incentivizes early withdrawals. This causes a feedback loop of more frETH burnt to withdraw ETH early. All this burnt frETH increases the price of frETH, which incentivizes more patience and more locking of ETH to create more frETH. A natural equilibrium is found between these counteracting forces. Long term, frETH becomes a volatility absorber for ETH itself.

### Why isn't ETH in freezers staked somewhere?

DeFi teaches us that all yield is good yield, and that stacking sources of yield is the smartest use of money. But this is a fundamental misunderstanding of financial theory. The fundamental theory of finance is to maximize *risk adjusted* yield. There is a market for *provably lowest possible risk yield*. This is why truly trustless staked ETH will one day compete with US treasury bonds as a global reserve asset. But until then, a large amount of the 118M+ ETH circulating is held *raw*. Held because, eventually, its price will go up. Much of this is held in centralized exchanges or in long term "cold storage". Earning no yield and difficult to estimate how much exists in this status.

This raw ETH is the target market for Deep Freeze. We do not expect frETH to compete with higher risk, higher yield opportunities to use ETH. But by tokenizing patience, we create an opportunity for the market to pay people who store ETH raw, to "lock in" that they will hold that raw ETH out of circulating supply with evidence of doing so on-chain. And because Deep Freeze is a provably lowest risk (and optionally password-hash protected) smart contract that is compatible with cold storage, we expect the market will pay relatively well to have ETH out of circulating supply and to have that information on-chain. 

## Revenue/Governance

Deep Freeze will be a 0 governance, 0 administrative protocol. It will be immutable upon launch with the FRZ revenue token. The protocol will have a fixed fee structure to generate revenue to stakers of the FRZ token. A diagram of Alice’s deposit is included here: 

![image](https://user-images.githubusercontent.com/96018507/148113289-6e2fb61d-2547-477a-9b41-2e3ad63e51f6.png)

Stakers of the FRZ token will receive 2 forms of revenue. 

1. frETH penalties

The frETH penalty for withdrawals (up to 20%) is frETH taken out of the market- it only exists because someone has locked ETH and made their frETH available for purchase. Half of this frETH penalty (half the amount above frETH minted originally) is paid to stakers of the Deep Freeze revenue token FRZ. The other half is burned, offering a small deflationary pressure to offset frETH minting inflation.

2. ETH withdrawals

To further incentivize patience, a small 0.25% fee is applied to all early withdrawals and paid to directly to stakers of FRZ. This is binary, only completed lock cycles (and of course, deposits that never decide to lock to get frETH) avoid the fee.


