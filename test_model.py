import numpy as np
from sklearn.ensemble import RandomForestClassifier
X = np.array([[90, 14, 150], [85, 15, 160], [95, 13, 170], [150, 10, 240], [200, 9, 260], [180, 11, 220]])
y = np.array([0, 0, 0, 1, 1, 1])
model = RandomForestClassifier(random_state=42)
model.fit(X, y)
print(model.predict([[100, 12, 120]]))
