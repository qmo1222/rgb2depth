import torch
import torch.utils.data as data
from torchvision import transforms
from NYUDepth import NYUDepth
from metrics import mre, delta


def eval(test_loader, model, device):
    mse = torch.nn.MSELoss()
    mae = torch.nn.L1Loss()

    with torch.no_grad():
        rmse_loss = 0
        mae_loss = 0
        mre_loss = 0
        delta1_loss = 0
        delta2_loss = 0
        delta3_loss = 0
        for i, (img, depth) in enumerate(test_loader):
            img, depth = img.to(device).float(), depth.to(device).float()
            depth = depth.unsqueeze(1)
            output = model(img)
            rmse_loss += mse(output, depth) * test_loader.batch_size
            mae_loss += mae(output, depth) * test_loader.batch_size
            mre_loss += mre(output, depth) * test_loader.batch_size
            delta1_loss += delta(output, depth, 1) * test_loader.batch_size
            delta2_loss += delta(output, depth, 2) * test_loader.batch_size
            delta3_loss += delta(output, depth, 3) * test_loader.batch_size

        N = len(test_loader) * test_loader.batch_size
        rmse_loss = torch.sqrt(rmse_loss/N)
        mae_loss = mae_loss / N
        mre_loss = mre_loss / N
        delta1_loss = delta1_loss / N
        delta2_loss = delta2_loss / N
        delta3_loss = delta3_loss / N

        print('RMSE: %f' % (rmse_loss,))
        print('MAE: %f' % (mae_loss,))
        print('MRE: %f' % (mre_loss,))
        print('Delta1: %f' % (delta1_loss,))
        print('Delta2: %f' % (delta2_loss,))
        print('Delta3: %f' % (delta3_loss,))


if __name__ == "__main__":
    opt = TrainOptions().parse()

    batch_size = opt.batch_size
    model_path = opt.load_model
    model = torch.load(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    train_dataset = NYUDepth(root=opt.dataroot,
                             mode='train')
    test_dataset = NYUDepth(root=opt.dataroot,
                            mode='test')
    train_loader = data.DataLoader(train_dataset,
                                   batch_size=batch_size)
    test_loader = data.DataLoader(test_dataset,
                                  batch_size=batch_size)
    print('Size of training dataset:', len(train_dataset))
    print('Evaluating training dataset...')
    eval(train_loader, model, device)
    print('Size of testing dataset:', len(test_dataset))
    print('Evaluating testing dataset...')
    eval(test_loader, model, device)
