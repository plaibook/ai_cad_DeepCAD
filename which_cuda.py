import torch 
print("is_available: ", torch.cuda.is_available())
print("version of cuda: ", torch.version.cuda)  # Should display '11.7'
