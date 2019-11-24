import numpy as np
import nujo as nj
import nujo.optim as optim

# Define the net and optimizer
net = nj.Linear(3, 6) >> nj.Linear(6, 2) >> nj.Linear(2, 1)
optimizer = optim.GradientDescent(net.parameters, lr=0.005)

# Training loop
def train(net, x, y, num_epochs):
    for epoch in range(1, num_epochs+1):

        # Forward
        output = net(x)
        # Compute Loss
        loss = (1/x.shape[0])*(output-y)**2
        
        # Print the loss every 10th epoch for monitoring
        if epoch % 10 == 0:
            print('EPOCH:', epoch, '| LOSS: ', np.mean(loss.value))
        
        # Backprop
        loss.backward()
        
        # Update
        optimizer.step()
        
        # Zero grad
        optimizer.zero_grad()

if __name__ == '__main__':
    # Create example data
    x = np.random.rand(30, 3)
    y = x@[[2], [3], [4]] - 10
    x, y = nj.Constant(x), nj.Constant(y)

    # Train
    train(net, x, y, 100)
