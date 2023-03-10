import random


# alpha: selfish miners mining power (percentage),
# gamma: the ratio of honest miners choose to mine on the selfish miners pool's block
# N: number of simulations run
def Simulate(alpha, gamma, N, seed):
    # DO NOT CHANGE. This is used to test your function despite randomness
    random.seed(seed)

    # the same as the state of the state machine in the slides
    state = 0
    # the length of the blockchain that is published
    ChainLength = 0
    # the revenue of the selfish mining pool
    SelfishRevenue = 0

    PoolHiddenChain= 0
    # A round begin when the state=0
    for i in range(N):
        r = random.random()
        if state == 0:
            # The selfish pool has 0 hidden block.
            PoolHiddenChain = 0
            if r <= alpha:
                # The selfish pool mines a block.
                # They don't publish it.
                state += 1
                PoolHiddenChain += 1
                # made it here
            else:
                # The honest miners found a block.
                # The round is finished : the honest miners found 1 block
                # and the selfish miners found 0 block.
                state = 0
                ChainLength+=1 #maybe add this
                #made it here

        elif state == 1:
            # The selfish pool has 1 hidden block.
            if r <= alpha:
            #The selfish miners found a new block.
            # Write a piece of code to change the required variables.
                state += 1
                PoolHiddenChain += 1
            # You might need to define new variable to keep track of the number of hidden blocks.
            else:
                state = -1
                PoolHiddenChain -= 1
                ChainLength +=1
                # made it here

        # Write a piece of code to change the required variables.

        elif state == -1:
            # It's the state 0' in the slides (the paper of Eyal and Gun Sirer)
            # There are three situations!
            # Write a piece of code to change the required variables in each one.
            if r <= alpha:
                state = 0
                SelfishRevenue += 2
                ChainLength+=1
                # made it here
            elif r <= alpha + (1 - alpha) * gamma:
                state = 0
                SelfishRevenue += 1
                ChainLength += 1 #maybe add this
            else:
                state = 0
                ChainLength += 1  # maybe add this

        elif state == 2:
            # The selfish pool has 2 hidden block.
            if r <= alpha:
                state += 1
                PoolHiddenChain+=1
            else:
                state = 0
                SelfishRevenue += 2
                ChainLength += 2
                PoolHiddenChain-=2
        # The honest miners found a block.

        elif state > 2:
            if r <= alpha:
            # The selfish miners found a new block
                state += 1
                PoolHiddenChain += 1
            else:
                state -= 1
                SelfishRevenue += 1
                PoolHiddenChain -= 1
                ChainLength+=1
                #publish enough to stay ahead by 1

    return float(SelfishRevenue) / ChainLength


