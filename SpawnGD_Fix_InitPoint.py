import numpy as np
from math import sqrt
from numpy import asarray
from numpy import arange
from numpy import meshgrid
from matplotlib import pyplot as plt
from time import time
import argparse
import os


epsilon = 0.000 # can be near zero instead of 0
# number of steps
n_iter = 27
# steps size
alpha = 0.02
# factor for average gradient
beta1 = 0.9
# factor for average squared gradient
beta2 = 0.999
# define the step size
step_size_gd = 0.01
step_size_momentom = 0.01
step_size_rmsprop = 0.01
step_size_srsgd = 0.01
step_size_proposed = 0.01
# define momentum
momentum = 0.3
# momentum for rmsprop
rho = 0.99
# number of exponentialy produced random samples
SpawnSize = 5
# initial_point = [0.0, 0.5]

############################### gradient descent algorithm ##################################
def gradient_descent(bounds, n_iter, step_size_gd):
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list
    solutions.append(x.copy())

    # run the gradient descent
    for itr in range(n_iter):
        dist_to_ans = abs(objective(x) - final_answer_value)
        if (dist_to_ans <= epsilon):
            print("gradient iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for GD:", dist_to_ans)

        g = derivative(x)
        for i in range(bounds.shape[0]):
            # take a step
            x[i] = x[i] - step_size_gd * g[i]
        x = asarray(x)
        solutions.append(x.copy())

    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


############################ gradient descent with tuned step size ###############################
def gradient_descent_by_tune_stepsize(bounds, n_iter, step_size_gd):
	solutions = list()
	x = initial_point.copy()
	# Add initial point to solutions list
	solutions.append(x.copy())
	step_size_gd = [0.01, 0.01]
	v = np.zeros((bounds.shape[0], 1))
	B = 0.1

	# run the gradient descent
	for itr in range(n_iter):
		dist_to_ans = abs(objective(x) - final_answer_value)
		if (dist_to_ans <= epsilon):
			print("gradient tuned step iterations", itr)
			break
		else:
			print("iter: (", itr, ")  distance to answer for GD tuned step:", dist_to_ans)

		g = derivative(x)
		g_sign = np.sign(g)

		for i in range(bounds.shape[0]):
			x[i] = x[i] - step_size_gd[i] * g[i]
		x = asarray(x)

		g_solution = derivative(x)
		g_solution_sign= np.sign(g_solution)

		for i in range(bounds.shape[0]):
			if(g_sign[i] == g_solution_sign[i]):
				step_size= step_size_gd[i]*0.2
				step_size_gd[i] = step_size + step_size_gd[i]
			else:
				step_size_gd[i]=  step_size_gd[i]/2

		g = g_solution
		g_sign = g_solution_sign
		solutions.append(x.copy())

	return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


################################# proposed method (Spgd) algorithm #################################
def proposed(bounds, n_iter, step_size_proposed):
    solutions = list()
    TheBest = initial_point.copy()
    # Add initial point to solutions list to show initial point in plot
    solutions.append(TheBest.copy())

    n_iter_temp = 3
    Iteration = 9
    step_size_gd = [0.01, 0.01]

    for k in range(Iteration):
        temp_solutions = list()
        x = TheBest

        g = derivative(x)
        g_sign = np.sign(g)

        for itr in range(n_iter_temp):
            # dist_to_ans = abs(objective(TheBest) - final_answer_value)
            # # dist_to_ans = abs(objective(x) - final_answer_value)
            # if (dist_to_ans <= epsilon):
            #     print("proposed iterations", k, itr)
            #     break
            # else:
            #     print("iter: (", k, itr, ")  distance to answer for proposed:", dist_to_ans)
            
            for i in range(bounds.shape[0]):
                x[i] = x[i] - step_size_gd[i] * g[i]

            x = asarray(x.copy())
            temp_solutions.append(x)

            g_solution = derivative(x)
            g_solution_sign= np.sign(g_solution)

            for i in range(bounds.shape[0]):
                if(g_sign[i] == g_solution_sign[i]):
                    step_size = step_size_gd[i] * 0.2
                    step_size_gd[i] = step_size + step_size_gd[i]
                else:
                    step_size_gd[i] = step_size_gd[i] / 2
            
            g = g_solution
            g_sign = g_solution_sign


        solutions = solutions + temp_solutions
        TheBest = temp_solutions[-1]
        temp_dif = temp_solutions[-1] - temp_solutions[-3]
        length,  next_sign = abs(temp_dif), np.sign(temp_dif)

        eggs = np.zeros([length.shape[0], SpawnSize], dtype=float)
        for i in range(length.shape[0]):
            eggs[i, :] = temp_solutions[-1][i] + next_sign[i] * \
                np.random.exponential(scale=length[i], size=SpawnSize)        

        eggsoutput = [objective(eggs[:, i])
                      for i in range(SpawnSize)] + objective(TheBest)
        ind = np.argmin(eggsoutput)
        TheBest = np.append(eggs, np.asarray(TheBest).reshape((TheBest.shape[0], 1)), axis=1)[:, ind]
        solutions.append(TheBest)

    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


################################### ADAM algorithm #######################################
def adam(bounds, n_iter, alpha, beta1, beta2, eps=1e-8):
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list
    solutions.append(x.copy())
    # initialize first and second moments
    m = [0.0 for _ in range(bounds.shape[0])]
    v = [0.0 for _ in range(bounds.shape[0])]

    # run the gradient descent updates
    for itr in range(n_iter):

        dist_to_ans = abs(objective(x) - final_answer_value)
        if (dist_to_ans <= epsilon):
            print("adam iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for adam:", dist_to_ans)

        # calculate gradient g(t)
        g = derivative(x)
        # build a solution one variable at a time
        for i in range(bounds.shape[0]):
            # m(t) = beta1 * m(t-1) + (1 - beta1) * g(t)
            m[i] = beta1 * m[i] + (1.0 - beta1) * g[i]
            # v(t) = beta2 * v(t-1) + (1 - beta2) * g(t)^2
            v[i] = beta2 * v[i] + (1.0 - beta2) * g[i]**2
            # mhat(t) = m(t) / (1 - beta1(t))
            mhat = m[i] / (1.0 - beta1**(itr+1))
            # vhat(t) = v(t) / (1 - beta2(t))
            vhat = v[i] / (1.0 - beta2**(itr+1))
            # x(t) = x(t-1) - alpha * mhat(t) / (sqrt(vhat(t)) + ep)
            x[i] = x[i] - alpha * mhat / (sqrt(vhat) + eps)
        # keep track of solutions
        solutions.append(x.copy())

    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


################################# SimpleRADAM algorithm ##################################
def simpleradam(bounds, n_iter, alpha, beta1, beta2):
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list
    solutions.append(x.copy())
    # initialize first and second moments
    m = [0.0 for _ in range(len(x))]
    v = [0.0 for _ in range(len(x))]

    # initialize warm-up steps
    warmup_steps = 1000  # Adjust as needed

    # run the gradient descent updates
    for itr in range(n_iter):

        dist_to_ans = abs(objective(x) - final_answer_value)
        if dist_to_ans <= epsilon:
            print("simple radam iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for simple radam:", dist_to_ans)

        # calculate gradient g(t)
        g = derivative(x)
        # apply warm-up to the learning rate
        if itr < warmup_steps:
            lr = alpha * (itr + 1) / warmup_steps
        else:
            lr = alpha

        # build a solution one variable at a time
        for i in range(len(x)):
            # m(t) = beta1 * m(t-1) + (1 - beta1) * g(t)
            m[i] = beta1 * m[i] + (1.0 - beta1) * g[i]
            # v(t) = beta2 * v(t-1) + (1 - beta2) * g(t)^2
            v[i] = beta2 * v[i] + (1.0 - beta2) * g[i]**2
            # mhat(t) = m(t) / (1 - beta1(t))
            mhat = m[i] / (1.0 - beta1**(itr+1))
            # vhat(t) = v(t) / (1 - beta2(t))
            vhat = v[i] / (1.0 - beta2**(itr+1))
            # x(t) = x(t-1) - alpha * mhat(t) / (sqrt(vhat(t)) + epsilon)
            x[i] = x[i] - lr * mhat / (sqrt(vhat) + epsilon)

        # keep track of solutions
        solutions.append(x.copy())
        
    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


################################### NADAM algorithm #######################################
def nadam(bounds, n_iter, alpha, beta1, beta2, eps=1e-8):
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list
    solutions.append(x.copy())
    
    # initialize first and second moments
    m = [0.0 for _ in range(bounds.shape[0])]
    v = [0.0 for _ in range(bounds.shape[0])]

    # run the gradient descent updates
    for itr in range(n_iter):
        dist_to_ans = abs(objective(x) - final_answer_value)
        if (dist_to_ans <= epsilon):
            print("nadam iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for nadam:", dist_to_ans)

        # calculate gradient g(t)
        g = derivative(x)
        # build a solution one variable at a time
        for i in range(bounds.shape[0]):
            # m(t) = beta1 * m(t-1) + (1 - beta1) * g(t)
            m[i] = beta1 * m[i] + (1.0 - beta1) * g[i]
            # v(t) = beta2 * v(t-1) + (1 - beta2) * g(t)^2
            v[i] = beta2 * v[i] + (1.0 - beta2) * g[i]**2
            
            # Compute bias-corrected moments
            mhat = m[i] / (1.0 - beta1**(itr+1))
            vhat = v[i] / (1.0 - beta2**(itr+1))
            
            # Include the Nesterov momentum term
            mhat_next = beta1 * mhat + ((1.0 - beta1) * g[i]) / (1.0 - beta1**(itr+1))
            
            # Update parameters with Nesterov momentum
            x[i] = x[i] - alpha * mhat_next / (sqrt(vhat) + eps)
            
        solutions.append(x.copy())

    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


################################## RADAM algorithm ######################################
def radam(bounds, n_iter, alpha, beta1, beta2, eps=1e-8):
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list to show initial point in plot
    solutions.append(x.copy())

    # initialize first and second moments
    m = [0.0 for _ in range(len(x))]
    v = [0.0 for _ in range(len(x))]

    # compute the maximum length of the approximated SMA
    rho_inf = 2 / (1 - beta2) - 1

    # run the gradient descent updates
    for itr in range(1, n_iter + 1):
        dist_to_ans = abs(objective(x) - final_answer_value)
        if dist_to_ans <= epsilon:
            print("radam iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for radam:", dist_to_ans)

        # calculate gradient g(t)
        g = derivative(x)
        
        # build a solution one variable at a time
        for i in range(len(x)):
            # Update momentum and variance
            m[i] = beta1 * m[i] + (1.0 - beta1) * g[i]
            v[i] = beta2 * v[i] + (1.0 - beta2) * g[i]**2

            # Bias correction
            mhat = m[i] / (1.0 - beta1**itr)
            vhat = v[i] / (1.0 - beta2**itr)
            
            # Compute the length of the approximated SMA
            rho_t = rho_inf - 2 * itr * beta2**itr / (1.0 - beta2**itr)
            
            if rho_t > 5:
                # Compute variance rectification term
                rt = sqrt(((rho_t - 4) * (rho_t - 2) * rho_inf) / 
                         ((rho_inf - 4) * (rho_inf - 2) * rho_t))
                # Compute adaptive learning rate
                denominator = (sqrt(vhat) + eps)
                # Update with rectified variance
                x[i] = x[i] - alpha * rt * mhat / denominator
            else:
                # SGD-like update when variance estimate is not reliable
                x[i] = x[i] - alpha * mhat

        solutions.append(x.copy())
        
    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


# ################################ Momentum algorithm ################################
def Momentum(bounds, n_iter, step_size_momentom):
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list
    solutions.append(x.copy())

    change = 0.0
    # run the gradient descent updates
    for itr in range(n_iter):
        dist_to_ans = abs(objective(x) - final_answer_value)
        if (dist_to_ans <= epsilon):
            print("Momentum iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for Momentum:", dist_to_ans)

        # calculate gradient g(t)
        g = derivative(x)
        new_solution = list()
        for i in range(bounds.shape[0]):
            # calculate update
            new_change = step_size_momentom * g[i] + momentum * change
            # take a step
            solution = x[i] - new_change
            # store solution
            new_solution.append(solution)
            # save the change
            change = new_change
        # store the new solution
        x = asarray(new_solution)
        solutions.append(x)

    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


############################## RMSPROP algorithm ####################################
def rmsprop(bounds, n_iter, step_size_rmsprop, rho):
    solutions = list()
    x = initial_point.copy()
    solutions.append(x.copy()) # This line is added to show init point in plot
    # list of the average square gradients for each variable
    sq_grad_avg = [0.0 for _ in range(bounds.shape[0])]


    # run the gradient descent
    for itr in range(n_iter):

        dist_to_ans = abs(objective(x) - final_answer_value)
        if (dist_to_ans <= epsilon):
            print("rmsprop iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for rmsprop:", dist_to_ans)

        # calculate gradient
        g = derivative(x)
        # update the average of the squared partial derivatives
        for i in range(g.shape[0]):
            # calculate the squared gradient
            sg = g[i]**2.0
            # update the moving average of the squared gradient
            sq_grad_avg[i] = (sq_grad_avg[i] * rho) + (sg * (1.0-rho))
        # build solution
        new_solution = list()
        for i in range(bounds.shape[0]):
            # calculate the learning rate for this variable
            alpha = step_size_rmsprop / (1e-8 + sqrt(sq_grad_avg[i]))
            # calculate the new position in this variable
            value = x[i] - alpha * g[i]
            new_solution.append(value)
        # store the new solution
        x = asarray(new_solution)
        solutions.append(x)

    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


################################### AdaBelief algorithm #######################################
def adabelief(bounds, n_iter, alpha, beta1, beta2, eps=1e-16):
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list
    solutions.append(x.copy())    
    # initialize first and second moments
    m = [0.0 for _ in range(bounds.shape[0])]
    s = [0.0 for _ in range(bounds.shape[0])]

    # run the gradient descent updates
    for itr in range(n_iter):
        dist_to_ans = abs(objective(x) - final_answer_value)
        if (dist_to_ans <= epsilon):
            print("adabelief iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for adabelief:", dist_to_ans)

        # calculate gradient g(t)
        g = derivative(x)
        # build a solution one variable at a time
        for i in range(bounds.shape[0]):
            # Update biased first moment estimate
            m[i] = beta1 * m[i] + (1.0 - beta1) * g[i]
            
            # Update biased second raw moment estimate
            s[i] = beta2 * s[i] + (1.0 - beta2) * (g[i] - m[i])**2 + eps
            
            # Compute bias-corrected first moment estimate
            mhat = m[i] / (1.0 - beta1**(itr+1))
            
            # Compute bias-corrected second raw moment estimate
            shat = s[i] / (1.0 - beta2**(itr+1))
            
            # Update parameters
            x[i] = x[i] - alpha * mhat / (sqrt(shat) + eps)
            
        solutions.append(x.copy())

    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


################################## SRSGD algorithm ######################################
def srsgd(bounds, n_iter, step_size_srsgd, restarting_iter=100): #Restarts every (default 100) iterations
    solutions = list()
    x = initial_point.copy()
    # Add initial point to solutions list
    solutions.append(x.copy())
    
    # Initialize momentum buffer
    momentum_buffer = x.copy()
    iter_count = 1
    
    # Run the gradient descent updates with scheduled restarts
    for itr in range(n_iter):
        dist_to_ans = abs(objective(x) - final_answer_value)
        if dist_to_ans <= epsilon:
            print("srsgd iterations", itr)
            break
        else:
            print("iter: (", itr, ")  distance to answer for srsgd:", dist_to_ans)
            
        # Calculate gradient
        g = derivative(x)
        
        # Calculate momentum coefficient
        momentum = (iter_count - 1.0) / (iter_count + 2.0)
        
        # Update solution with momentum
        new_x = x.copy()
        for i in range(len(x)):
            # v_{t+1} = p_t - lr*g_t
            buf1 = x[i] - step_size_srsgd * g[i]
            # p_{t+1} = v_{t+1} + momentum*(v_{t+1} - v_t)
            new_x[i] = buf1 + momentum * (buf1 - momentum_buffer[i])
            momentum_buffer[i] = buf1
            
        x = new_x
        
        # Update iteration counter and check for restart
        iter_count += 1
        if iter_count >= restarting_iter:
            iter_count = 1
            momentum_buffer = x.copy()
            
        solutions.append(x.copy())
        
    return solutions, abs(np.float_(solutions[-1]) - final_answer_value)


############################################ show_contour ###############################################
def show_contour(obj_func, solutions, func_name):
    
    # # Create and save color plots (both normal and zoomed)
    # for is_zoomed in [False, True]:
    #     plt.figure()
    #     plt.contourf(x, y, obj_func, levels=50, cmap='jet')
    #     solutions = asarray(solutions)
    #     plt.plot(solutions[:, 0], solutions[:, 1], '.-', color='w')
    #     # Plot initial point in red
    #     plt.plot(initial_point[0], initial_point[1], 'r.', markersize=8)
    #     if args.function_name == "Rosenbrock" or args.function_name == "Levy":
    #         plt.plot(1, 1, '.-', color='r')
    #     else:
    #         plt.plot(0, 0, '.-', color='r')
    #     plt.xlabel('x')
    #     plt.ylabel('y')
    #     plt.title(f'{args.function_name} _ {func_name}')
        
    #     if is_zoomed:
    #         # Calculate zoom boundaries based on initial point and min  point
    #         if args.function_name == "Rosenbrock" or args.function_name == "Levy":
    #             x_min, x_max = initial_point[0] - 0.3, 1.1
    #             y_min, y_max = initial_point[1] - 0.3, 1.1
    #         else:
    #             x_min, x_max = -0.1, initial_point[0] + 0.1
    #             y_min, y_max = -0.1, initial_point[1] + 0.1

    #         plt.xlim(x_min, x_max)
    #         plt.ylim(y_min, y_max)
    #         zoom_suffix = '_zoomed'
    #     else:
    #         zoom_suffix = ''
            
    #     os.makedirs(f'plots_{args.function_name}', exist_ok=True)
    #     plt.savefig(f'plots_{args.function_name}/{func_name}_color{zoom_suffix}.png', dpi=300, bbox_inches='tight')
    
    # Create and save black and white plots (both normal and zoomed)
    init_value = objective(initial_point)
    
    for is_zoomed in [False, True]:
        solutions = asarray(solutions)
        plt.figure()
        contours = plt.contour(x, y, obj_func, levels=50)
        levels = contours.levels
        closest_level = min(levels, key=lambda x: abs(x - init_value))
        
        # Clear the current contours
        for coll in contours.collections:
            coll.remove()
        
        # Redraw contours with different colors
        for level in levels:
            if abs(level - closest_level) < 1e-10:  # Use small epsilon for floating point comparison
                plt.contour(x, y, obj_func, levels=[level], colors='red', linewidths=1)
            else:
                plt.contour(x, y, obj_func, levels=[level], colors='black', linewidths=1)
        
        plt.plot(solutions[:, 0], solutions[:, 1], '.-', color='blue', linewidth=1.5, markersize=4)
        # Plot initial point in red
        plt.plot(initial_point[0], initial_point[1], 'r.', markersize=8)
        if args.function_name == "Rosenbrock" or args.function_name == "Levy":
            plt.plot(1, 1, 'r*', markersize=6)
        else:
            plt.plot(0, 0, 'r*', markersize=6)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(f'{args.function_name} _ {func_name}')
        
        if is_zoomed:
            # Calculate zoom boundaries based on initial point and min  point
            if args.function_name == "Rosenbrock" or args.function_name == "Levy":
                x_min, x_max = initial_point[0] - 0.3, 1.1
                y_min, y_max = initial_point[1] - 0.3, 1.1
            else:
                x_min, x_max = -0.1, initial_point[0] + 0.1
                y_min, y_max = -0.1, initial_point[1] + 0.1            
            plt.xlim(x_min, x_max)
            plt.ylim(y_min, y_max)
            zoom_suffix = '_zoomed'
        else:
            zoom_suffix = ''

        os.makedirs(f'plots_{args.function_name}', exist_ok=True)
        plt.savefig(f'plots_{args.function_name}/{func_name}_bw{zoom_suffix}.png', dpi=300, bbox_inches='tight')

 #########################################################################################################
    # CALL ALGORITHMS And SHOW RESULTS
 #########################################################################################################

if __name__ == "__main__":
    import os
    print("Current working directory:", os.getcwd())
    parser = argparse.ArgumentParser()
    parser.add_argument("--function_name", type=str, default="Naive_Quadratic", 
                        help="The function name that is used for results evaluation. Options: Naive_Quadratic, Matyas, Rosenbrock, Ackley, Schaffer, Rastrigin, Levy")
    parser.add_argument("--initial_point", type=float, nargs=2, default=[0.3, 0.5], help="Two floats as initial point. Defaults are: 0.0, 0.5 ")

    args = parser.parse_args()
    print("Test Function is: ",  args.function_name, " And  Initial point is: ",  args.initial_point)
    initial_point = [args.initial_point[0], args.initial_point[1]]

    # ******************** Stretched Quadratic Function *************************
    if args.function_name == "Stretched_Quadratic":

        def objective(funcargs):
            return (1.0 / 500)*(funcargs[0]**2.0) + (1.0 / 400)*(funcargs[1])**2.0

        def derivative(funcargs):
            return asarray([funcargs[0] * (2.0 / 500), funcargs[1] * (2.0 / 400)])


    # ******************** Matyas Function *************************
    elif args.function_name == "Matyas":

        def objective(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            return 0.26*(x**2.0 + y**2.0) - 0.48*(x*y)

        def derivative(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            return asarray((0.52*x - 0.48*y,  0.52*y - 0.48*x))


    # ******************** Ackley Function *************************
    elif args.function_name == "Ackley":
            
        def objective(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            return -20 * np.exp(-0.2 * np.sqrt((x**2 + y**2) / 2)) - np.exp((np.cos(2 * (np.pi) * x) + np.cos(2 * (np.pi) * y)) / 2) + 20 + np.exp(1)

        def derivative(funcargs):
            a = 0.2
            b = 0.5
            c = 2 * np.pi
            x = funcargs[0]
            y = funcargs[1]
            term1 = (2 * c / 5) * y * np.exp(-a * np.sqrt(0.5 * (x**2 + y**2)))
            term2 = (x / np.sqrt(2 * (x**2 + y**2))) * \
                np.exp(-a * np.sqrt(0.5 * (x**2 + y**2)))
            term3 = 0.5 * c * np.sin(c * x) * np.exp(b *
                                                    (np.cos(c * x) + np.cos(c * y)))

            df_dx = term1 + term2 + term3

            term1 = (2 * c / 5) * x * np.exp(-a * np.sqrt(0.5 * (x**2 + y**2)))
            term2 = (y / np.sqrt(2 * (x**2 + y**2))) * \
                np.exp(-a * np.sqrt(0.5 * (x**2 + y**2)))
            term3 = 0.5 * c * np.sin(c * y) * np.exp(b *
                                                    (np.cos(c * x) + np.cos(c * y)))

            df_dy = term1 + term2 + term3

            return asarray([df_dx, df_dy])


    # ******************** Rosenbrock Function ************************* 
    elif args.function_name == "Rosenbrock":

        def objective(funcargs):
            x = funcargs[0]
            y = funcargs[1]   
            b = 10
            f =  (x-1)**2 + b*(y-x**2)**2
            return f

        def derivative(funcargs):
            b = 10
            x = funcargs[0]
            y = funcargs[1]
            df_dx=2*(x-1) - 4*b*(y - x**2)*x
            df_dy=2*b*(y-x**2)
            return asarray([df_dx, df_dy])


    # ******************** Schaffer Function ***************************
    elif args.function_name == "Schaffer":
        
        def objective(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            return 0.5 + (np.sin(np.sqrt(x**2 + y**2))**2 - 0.5) / (1 + 0.001 * (x**2 + y**2))**2

        def derivative(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            r = np.sqrt(x**2 + y**2)
            df_dx = (2 * x * np.cos(r) * np.sin(r)) / ((1 + 0.001 * r**2)**3) - (x * np.sin(r)**2) / (r * (1 + 0.001 * r**2)**2)
            df_dy = (2 * y * np.cos(r) * np.sin(r)) / ((1 + 0.001 * r**2)**3) - (y * np.sin(r)**2) / (r * (1 + 0.001 * r**2)**2)
            
            return np.array([df_dx, df_dy])

    # ******************** Rastrigin Function ***************************
    elif args.function_name == "Rastrigin":
        
        def objective(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            A = 10
            return 2*A + (x**2 - A*np.cos(2*np.pi*x)) + (y**2 - A*np.cos(2*np.pi*y))

        def derivative(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            A = 10
            dx = 2*x + 2*A*np.pi*np.sin(2*np.pi*x)
            dy = 2*y + 2*A*np.pi*np.sin(2*np.pi*y)
            return np.array([dx, dy])

    # ******************** Levy Function ***************************
    elif args.function_name == "Levy":
        
        def objective(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            w1 = 1 + (x - 1)/4
            w2 = 1 + (y - 1)/4
            term1 = np.sin(np.pi*w1)**2
            term2 = (w1-1)**2 * (1 + 10*np.sin(np.pi*w1 + 1)**2)
            term3 = (w2-1)**2 * (1 + np.sin(2*np.pi*w2)**2)
            return term1 + term2 + term3

        def derivative(funcargs):
            x = funcargs[0]
            y = funcargs[1]
            # Using numerical differentiation for more stable results
            h = 1e-8  # Small step size for numerical differentiation
            dx = (objective([x + h, y]) - objective([x - h, y])) / (2*h)
            dy = (objective([x, y + h]) - objective([x, y - h])) / (2*h)
            return np.array([dx, dy])

    # ******************** Default Function ***************************
    else:
        print("Default function is: Naive_Quadratic")

        def objective(funcargs):
            return funcargs[0]**2.0 + 3*(funcargs[1])**2.0

        def derivative(funcargs):
            return asarray([funcargs[0] * 2.0, funcargs[1] * 6.0])
        

#############################################
    if args.function_name == "Rosenbrock":
        final_answer = [1, 1]
        final_answer_value = 0
        # define range for Rosenbrock is a little more because of final answer that place in [1,1] and we want to show it properly in plot
        bounds = asarray([[-1.0, 1.2], [-1.0, 1.2]])        
    elif args.function_name == "Rastrigin":
        final_answer = [0, 0]
        final_answer_value = objective(final_answer)
        # bounds = asarray([[-5.12, 5.12], [-5.12, 5.12]])
        bounds = asarray([[-2.0, 2.0], [-2.0, 2.0]])

    elif args.function_name == "Levy":
        final_answer = [1, 1]
        final_answer_value = objective(final_answer)
        # bounds = asarray([[-10.0, 10.0], [-10.0, 10.0]])
        bounds = asarray([[-3.0, 3.0], [-3.0, 3.0]])

    else:
        final_answer = [0, 0]
        final_answer_value = objective(final_answer)
        # define range for others
        bounds = asarray([[-1.0, 1.0], [-1.0, 1.0]])

    # sample input range uniformly at 0.1 increments
    xaxis = arange(bounds[0, 0], bounds[0, 1], 0.1)
    yaxis = arange(bounds[1, 0], bounds[1, 1], 0.1)
    # create a mesh from the axis
    x, y = meshgrid(xaxis, yaxis)
    funcargs = [x, y]

    objective_func = objective(funcargs)
#############################################


    runtimes_proposed = list()
    runtimes_gd = list()
    runtimes_gd_tuned_step = list()
    runtimes_adam = list()
    runtimes_simpleradam = list()
    runtimes_nadam = list()
    runtimes_radam = list()
    runtimes_momentum = list()
    runtimes_rmsprop = list()
    runtimes_adabelief = list()
    runtimes_srsgd = list()

    dists_pro = list()
    dists_gd = list()
    dists_gd_tuned_step = list()
    dists_adam = list()
    dists_simpleradam = list()
    dists_nadam = list()
    dists_radam = list()
    dists_moment = list()
    dists_rmsp = list()
    dists_adabelief = list()
    dists_srsgd = list()


    # perform the proposed
    start_pro = time()
    solutions, dist_pro = proposed(bounds, n_iter, step_size_proposed)
    runtimes_proposed.append(time()-start_pro)
    dists_pro.append(dist_pro)
    show_contour(objective_func, solutions, str('PROPOSED'))

    # perform the gradient descent
    start_gd = time()
    solutions, dist_gd = gradient_descent(bounds, n_iter, step_size_gd)
    runtimes_gd.append(time()-start_gd)
    dists_gd.append(dist_gd)
    show_contour(objective_func, solutions, str('Gradient Descent'))

    # perform the gradient descent with tune stepsize
    start_gd_tuned_step = time()
    solutions, dist_gd_tuned_step = gradient_descent_by_tune_stepsize(bounds, n_iter, step_size_gd)
    runtimes_gd_tuned_step.append(time()-start_gd_tuned_step)
    dists_gd_tuned_step.append(dist_gd_tuned_step)
    show_contour(objective_func, solutions, str('Gradient Descent tuneed stepsize'))

    # perform the adam
    start_adam = time()
    solutions, dist_ada = adam(bounds, n_iter, alpha, beta1, beta2)
    runtimes_adam.append(time()-start_adam)
    dists_adam.append(dist_ada)
    show_contour(objective_func, solutions, str('ADAM'))

#   # perform the simpleradam
#     start_simpleradam = time()
#     solutions, dist_sprada = simpleradam(bounds, n_iter, alpha_radam, beta1, beta2)
#     runtimes_simpleradam.append(time()-start_simpleradam)
#     dists_simpleradam.append(dist_sprada)
#     show_contour(objective_func, solutions, str('SP-RADAM'))

    # perform the nadam
    start_nadam = time()
    solutions, dist_nad = nadam(bounds, n_iter, alpha, beta1, beta2)
    runtimes_nadam.append(time()-start_nadam)
    dists_nadam.append(dist_nad)
    show_contour(objective_func, solutions, str('NADAM'))

    # perform the radam
    start_radam = time()
    solutions, dist_rada = radam(bounds, n_iter, alpha, beta1, beta2)
    runtimes_radam.append(time()-start_radam)
    dists_radam.append(dist_rada)
    show_contour(objective_func, solutions, str('RADAM'))


    # perform the momentum
    start_moment = time()
    solutions, dist_mom = Momentum(bounds, n_iter, step_size_momentom)
    runtimes_momentum.append(time()-start_moment)
    dists_moment.append(dist_mom)
    show_contour(objective_func, solutions, str('MOMENTUM'))

    # perform the rmsprop
    start_rms = time()
    solutions, dist_rms = rmsprop(bounds, n_iter, step_size_rmsprop, rho)
    runtimes_rmsprop.append(time()-start_rms)
    dists_rmsp.append(dist_rms)
    show_contour(objective_func, solutions, str('RMSPROP'))

    # perform the adabelief
    start_adabelief = time()
    solutions, dist_adab = adabelief(bounds, n_iter, alpha, beta1, beta2)
    runtimes_adabelief.append(time()-start_adabelief)
    dists_adabelief.append(dist_adab)
    show_contour(objective_func, solutions, str('ADABELIEF'))

    # perform the srsgd
    start_srsgd = time()
    solutions, dist_srsgd = srsgd(bounds, n_iter, step_size_srsgd)
    runtimes_srsgd.append(time()-start_srsgd)
    dists_srsgd.append(dist_srsgd)
    show_contour(objective_func, solutions, str('SRSGD'))

    # show the plot
    plt.show()

    dict = {'RunTime_Proposed': runtimes_proposed,
            'RunTime_GD': runtimes_gd,
            'RunTime_GD_Tuned_Step': runtimes_gd_tuned_step,
            'RunTime_Adam': runtimes_adam,
            'RunTime_spRAdam': runtimes_simpleradam,
            'RunTime_Nadam': runtimes_nadam,
            'RunTime_RAdam': runtimes_radam,
            'RunTime_Momentum': runtimes_momentum,
            'RunTime_Rmsprop': runtimes_rmsprop,
            'RunTime_AdaBelief': runtimes_adabelief,
            'RunTime_SRSGD': runtimes_srsgd,

            'dis_Proposed': dists_pro,
            'dis_GD': dists_gd,
            'dis_GD_Tuned_Step': dists_gd_tuned_step,
            'dis_Adam': dists_adam,
            'dis_spRAdam': dists_simpleradam,
            'dis_Nadam': dists_nadam,
            'dis_RAdam': dists_radam,
            'dis_Momentum': dists_moment,
            'dis_Rmsprop': dists_rmsp,
            'dis_AdaBelief': dists_adabelief,
            'dis_SRSGD': dists_srsgd,
}

    print("RUNTIME  MEAN     ==> \n",
        "  Proposed:   ", np.mean(dict['RunTime_Proposed']),
        "  GD:   ", np.mean(dict['RunTime_GD']),
        "  GD_Tune_Step", np.mean(dict['RunTime_GD_Tuned_Step']),
        "  Adam:   ", np.mean(dict['RunTime_Adam']),
        "  SpRAdam:   ", np.mean(dict['RunTime_spRAdam']),
        "  Nadam:   ", np.mean(dict['RunTime_Nadam']),
        "  RAdam:   ", np.mean(dict['RunTime_RAdam']),
        "  Momentum:   ", np.mean(dict['RunTime_Momentum']),
        "  Rmsprop:   ", np.mean(dict['RunTime_Rmsprop']),
        "  AdaBelief:   ", np.mean(dict['RunTime_AdaBelief']),
        "  SRSGD:   ", np.mean(dict['RunTime_SRSGD']),
        )
    print("RUNTIME  VARIANCE ==> \n",
        "  Proposed:   ", np.var(dict['RunTime_Proposed']),
        "  GD:   ", np.var(dict['RunTime_GD']),
        "  GD_Tune_Step:", np.var(dict['RunTime_GD_Tuned_Step']),
        "  Adam:   ", np.var(dict['RunTime_Adam']),
        "  SpRAdam:   ", np.var(dict['RunTime_spRAdam']),
        "  Nadam:  ", np.var(dict['RunTime_Nadam']),
        "  RAdam:   ", np.var(dict['RunTime_RAdam']),
        "  Momentum:   ", np.var(dict['RunTime_Momentum']),
        "  Rmsprop:   ", np.var(dict['RunTime_Rmsprop']),
        "  AdaBelief:   ", np.var(dict['RunTime_AdaBelief']),
        "  SRSGD:   ", np.var(dict['RunTime_SRSGD']),
        )
    print("DISTANCE  MEAN    ==>\n",
        "  Proposed:   ", np.mean(dict['dis_Proposed']),
        "  GD:   ", np.mean(dict['dis_GD']),
        "  GD_Tune_Step:", np.mean(dict['dis_GD_Tuned_Step']),
        "  Adam:   ", np.mean(dict['dis_Adam']),
        "  SpRAdam:   ", np.mean(dict['dis_spRAdam']),
        "  Nadam:   ", np.mean(dict['dis_Nadam']),
        "  RAdam:   ", np.mean(dict['dis_RAdam']),
        "  Momentum:   ", np.mean(dict['dis_Momentum']),
        "  Rmsprop:   ", np.mean(dict['dis_Rmsprop']),
        "  AdaBelief:   ", np.mean(dict['dis_AdaBelief']),
        "  SRSGD:   ", np.mean(dict['dis_SRSGD']),
        )
    print("DISTANCE VARIANCE ==> \n",
        "  Proposed:   ", np.var(dict['dis_Proposed']),
        "  GD:   ", np.var(dict['dis_GD']),
        "  GD_Tune_Step:", np.var(dict['dis_GD_Tuned_Step']),
        "  Adam:   ", np.var(dict['dis_Adam']),
        "  SpRAdam:  ", np.var(dict['dis_spRAdam']),
        "  Nadam:   ", np.var(dict['dis_Nadam']),
        "  RAdam:   ", np.var(dict['dis_RAdam']),
        "  Momentum:   ", np.var(dict['dis_Momentum']),
        "  Rmsprop:   ", np.var(dict['dis_Rmsprop']),
        "  AdaBelief:   ", np.var(dict['dis_AdaBelief']),
        "  SRSGD:   ", np.var(dict['dis_SRSGD']),
        )
