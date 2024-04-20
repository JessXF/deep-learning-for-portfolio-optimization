import torch
from dataloader import train_loader, val_loader
from model import ConvNet, SharpLoss
import logging
from tqdm import tqdm
from hyperparams import num_epochs, lr, print_freq, input_channels, hidden_channels
import matplotlib.pyplot as plt

logging.basicConfig(format="%(asctime)s-%(message)s",
                    level=logging.INFO, datefmt="%H:%M:%S")
# logging.getLogger().setLevel(logging.DEBUG)

torch.random.manual_seed(3)

torch.autograd.set_detect_anomaly(True)


def train(
    train_loader, val_loader, model, num_epochs=10, lr=1e-1, print_freq=100
):
    """
    Model training loop
    """

    logging.info("Start training...")
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-2)
    lossfn = SharpLoss()
    train_losses = []
    val_losses = []
    for epoch in tqdm(range(num_epochs)):
        logging.debug(f"Trainging epoch {epoch}")
        model.train()

        total_train_loss = 0
        for batch_idx, (x, y) in enumerate(train_loader):
            optimizer.zero_grad()
            weights = model(x)
            loss = lossfn(weights, y)
            logging.debug(f"weights: {weights[0]}")
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()
        avg_loss = total_train_loss / batch_idx
        train_losses.append(avg_loss)

        logging.debug(f"Validating epoch {epoch}")
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for batch_idx, (x, y) in enumerate(val_loader):
                weights = model(x)
                logging.debug(f"weight: {weights[0]}")
                loss = lossfn(weights, y)
                logging.debug(f"loss: {loss}")
                total_val_loss += loss.item()
            avg_val_loss = total_val_loss / batch_idx
            val_losses.append(avg_val_loss)
    logging.info("Training finished!")
    logging.debug(f"Train loss: {train_losses}")
    logging.debug(f"Validation loss: {val_losses}")
    fig, ax = plt.subplots()
    ax.set_title("Learning Curve")
    ax.plot(train_losses, label="Train Loss")
    ax.plot(val_losses, label="Validation Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()
    plt.show()

    return model


model = ConvNet(input_channels, hidden_channels, output_dim=4)

model = train(train_loader, val_loader, model, num_epochs, lr, print_freq)

# Save the model
torch.save(model.state_dict(), "model.pth")


# Load the model
# model = ConvNet(input_channels, hidden_channels, output_dim=4)
# model.load_state_dict(torch.load("model.pth"))
