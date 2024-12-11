import conductor_quantum.client as ConductorQuantum
import numpy as np
import torch


client = ConductorQuantum.ConductorQuantum(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDExNzg0Njg0OTgyOTU2MTI1MDA4NSIsImV4cCI6MjA0OTIxNjI4NH0.IaMlpgjWWKSoHGQOl2uxu803llQ-J5xRalRcP9sIS-E")

# Create numpy array
arr = np.array([[1, 2, 3], [4, 5, 6]])

# Create pytorch tensor
tensor = torch.tensor([[1, 2, 3], [4, 5, 6]])

# Execute
result = client.models.execute(model="coulomb-blockade-peak-detector", data=arr)
print(result)

result = client.models.execute(model="coulomb-blockade-peak-detector", data=tensor)
print(result)
