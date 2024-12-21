# Spawn Gradient Descent (SpGD)
*Official Python implementation of the manuscript "Spawning Gradient Descent (SpGD): A Novel Optimization Framework for Machine Learning and Deep Learning" by Moeinoddin Sheikhottayefe, Zahra Esmaily, and Fereshte Dehghani.*

## Overview
Spawning Gradient Descent (SpGD) is a novel optimization algorithm that improves gradient-based methods by addressing common challenges such as zigzagging, suboptimal initialization, and manual learning rate tuning. SpGD introduces dynamic learning rate adjustment through Augmented Gradient Descent (AGD), controlled randomization for better exploration, and optimized movement patterns for enhanced convergence. It achieves remarkable accuracy on benchmarks, such as a near-zero error (1.7e-11) on convex functions like Quadratic, and significantly better proximity to global optima on non-convex functions like Ackley. SpGD also excels in deep learning tasks, achieving faster convergence and higher accuracy—e.g., 85% accuracy on CIFAR-10 in just 20 epochs using DenseNet-19, demonstrating its efficiency in large-scale neural network training and challenging optimization tasks.

---

## Provided Methods
The implementation includes the following optimization methods:
- Adabelief
- Adam
- Nadam
- RAdam
- Momentum
- SRSGD
- RMSprop
- GD (Gradient Descent)
- SpGD (Proposed Method)

---

## Evaluation of Optimization Methods

### Fixed Starting Point
To evaluate the runtime and minimum distance to the answer for various methods with a fixed starting point, run the following code:

```bash
python Compare_Fix_Init_Point.py
```

By default, a simple quadratic function is used as the test function, with the initial starting point set to `[0.0, 0.5]`. However, you can select any of the following functions:
- Naive_Quadratic (default)
- Matyas
- Rosenbrock
- Ackley
- Schaffer
- Rastrigin
- Levy

For most functions, the starting point should be selected within the range of 0.0 to 1.0 or within the defined bounds for them.

You can specify these arguments using `--function_name` and `--initial_point` as follows:

```bash
python Compare_Fix_Init_Point.py --function_name <function_name> --initial_point <initial_point>
```

If you encounter the issue: *"A module that was compiled using NumPy 1.x cannot be run in NumPy 2.0.0 as it may crash,"* use `numpy==1.26.4`.  
If you encounter an error during execution, especially for the Rastrigin function in the proposed method, disable the break command.

#### Plot of Points for the Quadratic Function
**Points obtained by various methods on the quadratic function with a fixed starting point of `[0.3, 0.5]` over 27 steps:**

<p align="center">
  <img src="Images/Quadratic/ADABELIEF_bw_zoomed.png" alt="ADABELIEF" width="250" />
  <img src="Images/Quadratic/ADAM_bw_zoomed.png" alt="ADAM" width="250" />
  <img src="Images/Quadratic/NADAM_bw_zoomed.png" alt="NADAM" width="250" />
</p>
<p align="center">
  <img src="Images/Quadratic/RADAM_bw_zoomed.png" alt="RADAM" width="250" />
  <img src="Images/Quadratic/MOMENTUM_bw_zoomed.png" alt="MOMENTUM" width="250" />
  <img src="Images/Quadratic/SRSGD_bw_zoomed.png" alt="SRSGD" width="250" />
</p>
<p align="center">
  <img src="Images/Quadratic/RMSPROP_bw_zoomed.png" alt="RMSPROP" width="250" />
  <img src="Images/Quadratic/Gradient_Descent_bw_zoomed.png" alt="GD" width="250" />
  <img src="Images/Quadratic/PROPOSED_bw_zoomed.png" alt="SPGD" width="250" />
</p>

#### Plot of Points for the Ackley Function
**Points obtained by various methods on the Ackley function with a fixed starting point of `[0.3, 0.5]` over 27 steps:**

<p align="center">
  <img src="Images/Ackley/ADABELIEF_bw_zoomed.png" alt="ADABELIEF" width="250" />
  <img src="Images/Ackley/ADAM_bw_zoomed.png" alt="ADAM" width="250" />
  <img src="Images/Ackley/NADAM_bw_zoomed.png" alt="NADAM" width="250" />
</p>
<p align="center">
  <img src="Images/Ackley/RADAM_bw_zoomed.png" alt="RADAM" width="250" />
  <img src="Images/Ackley/MOMENTUM_bw_zoomed.png" alt="MOMENTUM" width="250" />
  <img src="Images/Ackley/SRSGD_bw_zoomed.png" alt="SRSGD" width="250" />
</p>
<p align="center">
  <img src="Images/Ackley/RMSPROP_bw_zoomed.png" alt="RMSPROP" width="250" />
  <img src="Images/Ackley/Gradient_Descent_bw_zoomed.png" alt="GD" width="250" />
  <img src="Images/Ackley/PROPOSED_bw_zoomed.png" alt="SPGD" width="250" />
</p>

---

### Random Starting Points
To evaluate the average runtime and minimum distance to the answer for various methods with random starting points over 100 iterations, run the following code:

```bash
python Compare_SpawnGD_Fix_InitPoint.py
```

By default, a simple quadratic function is used as the test function. However, you can change this by selecting the desired function name as follows:

```bash
python Compare_SpawnGD_Random_InitPoint.py --function_name <function_name>
```

#### Time Efficiency Evaluation
To better compare convergence speeds, we considered the time required for each optimizer to reach a specified distance (epsilon) from the optimal solution. Each optimizer was executed 100 times for each benchmark function, and the average execution time was recorded. By default, epsilon was set to 0.01 for convex functions and 0.1 for non-convex functions.
To evaluate the average runtime with consideration of an epsilon distance to the answer for various methods with random starting points over 100 iterations, run the following code:

```bash
python Compare_SpawnGD_Random_InitPoint_ٍEps_toMin.py
```

---

## SpGD in Deep Learning Models
SpGD showcases its effectiveness in deep learning by addressing common challenges such as slow convergence and entrapment in local minima. The proposed optimizer was integrated into **ResNet-20** and **DenseNet-19** models and evaluated on the **CIFAR-10** and **Fashion-MNIST** datasets, two widely used benchmarks in image classification, to compare its performance against other optimizers in deep learning tasks.
### Implementation and Experimentation
Our implementation is based on the existing code from the [SRSGD](https://github.com/minhtannguyen/SRSGD) method. The SpGD optimizer is defined in the `spawngd.py` file located in the *optimizers* folder.

To evaluate the average runtime and minimum distance to the optimal solution for various optimizers, you can run the following code:

```bash
python Compare_SpawnGD.py
```

In these experiments, SpGD employs only its spawning step, while the adaptive learning rate mechanism is excluded for simplicity. During spawn steps, a single spawn point is generated. The experimental pattern consists of a standard SGD step followed by an SGD with spawning step. 

### Findings
The spawning step improves exploration during optimization, enabling more effective exploitation in subsequent SGD steps. An alternative version of our optimizer, **spawngdMS**, introduces more frequent spawning steps relative to SGD steps. This version, along with the standard SpGD, can be found in the *optimizers* folder.

### Results
SpGD demonstrates remarkable improvements in both convergence speed and accuracy:
- **CIFAR-10**: Achieved 85% accuracy on DenseNet-19 after only 28 epochs.
- **Fashion-MNIST**: Reached 93% accuracy on ResNet-20 in just 25 epochs.

These results highlight the significant impact of the spawning step in improving exploration and efficiency during training, making SpGD a powerful alternative to traditional optimization methods for deep learning tasks.
<p align="center">
  <img src="Images/Deep_Plot_Images/Cifar10_Densenet.jpg" alt="Cifar10_Densenet" width="400", height="400" />
  <img src="Images/Deep_Plot_Images/FashionMnist_Resnet.jpg" alt="FashionMnist_Resnet" width="400", height="400" />
</p>
