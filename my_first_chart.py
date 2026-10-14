import matplotlib.pyplot as plt

x_code = [1, 2, 3, 4, 5]
y_code = [10, 20, 30, 40, 50]
fig, ax = plt.subplots()
ax.plot(x_code, y_code)

ax.set_title("my_first_chart")
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
plt.show()