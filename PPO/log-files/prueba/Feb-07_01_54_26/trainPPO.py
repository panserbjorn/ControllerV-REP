#Code for PPO use with V-REP
#Author Joaquín Silveira
#Based on Patrick Coady Implementation of PPO

import numpy as np
from policy import Policy
from value_function import NNValueFunction
from utils import Logger, Scaler
from datetime import datetime
# import os
import scipy.signal
import argparse
from mySimulatedEnv import myEnv
from bestAcumulator import BestAcumulator

def init_env(env_name):
	'''
	Inicialize my environment and return dimension of observation and action spaces. 

	Args:
		Env_name: str environment name (e.g. "SecondModel")
	Returns: 3-tuple
		Environment (object)
		Number of observation dimension (int)
		Number of action dimensions (int)
	'''
	env = myEnv()
	obs_dim = len(env.observation_space())
	act_dim = len(env.action_space())

	return env, obs_dim, act_dim

def run_initial_samples(env, policy, scaler, sampleFile):
	obs = env.reset()
	#TODO terminar esto después de hacer el resto!

def run_episode(env, policy, scaler):
	'''
	Run singe episode 

	Args:
		env: environment to interact with simulation
		policy: policy object with sample() method
		scaler: scaler object, used to scale/offset each observation dimension to a similar range

	Returns: 4-tuple of NumPy arrays
		observes: shape = (episode len, obs_dim)
		actions: shape = (episode len, act_dim)
		rewards: shape = (episode len, )
		unscaled_obs: useful for training scaler, shape = (episode len, obs_dim)
	'''
	obs = env.reset()
	observes, actions, rewards, unscaled_obs = [], [], [], []
	done = False
	step = 0.0
	scale, offset = scaler.get()
	#TODO Verificar si esto es necesrio!
	scale[-1] = 1.0 # don't sclae time step feature
	offset[-1] = 0.0 #don't offset time step feature
	while not done : 
		obs = np.array(obs, dtype=np.float64).reshape((1,-1))
		obs = np.append(obs, [[step]], axis=1) #add time step feature
		unscaled_obs.append(obs)
		#TODO Verificar que esto sea correcto. 
		obs = (obs - offset) * scale # center and scale observations
		observes.append(obs)
		action = policy.sample(obs).reshape((1, -1)).astype(np.float64)
		actions.append(action)
		obs, reward, done = env.step(action)
		if not isinstance(reward, float):
			reward = np.asscalar(reward)
		rewards.append(reward)
		step += 0.05
	return (np.concatenate(observes), np.concatenate(actions),
			np.array(rewards, dtype=np.float64), np.concatenate(unscaled_obs))
def run_policy(env, policy, scaler, logger, numEpisodes, acumulator):
	'''
	Run policy and collect data for minimum of min_step and min_episodes

	Args: 
		env: environment to interact with simulation
		policy: policy object with sample() method
		scaler: scaler object, used to sclae/offset each observation dimension to a similar range
		logger: logger object, used to save stats from episodes
		numEpisodes: roral episodes to run

	Returns: list fo trajectory dictionaries, list length = number of episodes
		'observes': NumPy aray of states fron episode
		'actions': NumPy array of actions from episode
		'rewards': NumPy array of (un-discounted) rewards from episode
		'unscaled_obs': NumPy array of unscaled observations from episode
	'''
	total_steps = 0
	trajectories = []
	for e in range(numEpisodes):
		observes, actions, rewards, unscaled_obs = run_episode(env, policy, scaler)
		# print([np.argmax(t) for t in actions])
		total_steps += observes.shape[0]
		trajectory = {	'observes': observes,
						'actions': actions,
						'rewards': rewards, 
						'unscaled_obs': unscaled_obs
						}
		acumulate = {'actions': [np.argmax(r) for r in actions], 'reward': sum(rewards)}
		acumulator.next_actions(acumulate)
		trajectories.append(trajectory)
	unscaled = np.concatenate([t['unscaled_obs'] for t in trajectories])
	scaler.update(unscaled) # update running statistics for scaling observations
	logger.log({'_MeanReward': np.mean([t['rewards'].sum() for t in trajectories]),
				'Steps': total_steps})
	return trajectories

def discount(x, gamma):
	'''
	Calulate discounted forward sum of a sequence ar each point
	'''
	return scipy.signal.lfilter([1.0],[1.0, - gamma], x[::-1])[::-1]

def add_disc_sum_rew(trajectories, gamma):
	'''
	Adds discounted sum of rewards to all time steps of all trajectories

	Args:
		trajectories: as returned by run_policy()
		gamma: discount

	Returns: 
		None (mutates trajectories dictionary to add 'disc_sum_rew')
	'''
	for trajectory in trajectories:
		if gamma < 0.999:  # don't scale for gamma ~= 1
			rewards = trajectory['rewards'] * (1 - gamma)
		else:
			rewards = trajectory['rewards']
		disc_sum_rew = discount(rewards, gamma)
		trajectory['disc_sum_rew'] = disc_sum_rew

def add_value(trajectories, val_func):
	'''
	Adds estimated value to all time steps of all trajectories

	Args: 
		trajectories: as returned by run_policy()
		val_func: object with predict() method, takes observations and returns predicted state value

	Returns: 
		None (mutates trajectories dictionary to add 'values')
	'''
	for trajectory in trajectories:
		observes = trajectory['observes']
		values = val_func.predict(observes)
		trajectory['values'] = values

def add_gae(trajectories, gamma, lam):
	''' 
	Add generalized advantage estimator. 
	https://arxiv.org/pdf/1506.02438.pdf

	Args:
		trajectories: as returned by run_policy must include 'values' key from add_values().
		gamma: reward discount
		lam: lambda (see paper).
			lam=0 : use TD residuals
			lam=1 : A = Sum Discounted Rewards - V_hat(s)

	Returns:
		None (mutates trajectories dictionary to add 'advantages')
	'''
	for trajectory in trajectories:
		if gamma < 0.999:  # don't scale for gamma ~= 1
			rewards = trajectory['rewards'] * (1 - gamma)
		else:
			rewards = trajectory['rewards']
		values = trajectory['values']
		# temporal differences
		tds = rewards - values + np.append(values[1:] * gamma, 0)
		advantages = discount(tds, gamma * lam)
		trajectory['advantages'] = advantages

def build_train_set(trajectories):
	'''

	Args:
		trajectories after processing by add_disc_sum_rew(), add_value() and add_gae()

	Returns: 4-tuple of NumPy arrays
		observes: shape = (N, obs_dim)
		actions: shape = (N, act_dim)
		advantages: shape = (N,)
		disc_sum_rew: shape = (N,)
	'''
	observes = np.concatenate([t['observes'] for t in trajectories])
	actions = np.concatenate([t['actions'] for t in trajectories])
	disc_sum_rew = np.concatenate([t['disc_sum_rew'] for t in trajectories])
	advantages = np.concatenate([t['advantages'] for t in trajectories])
	# normalize advantages
	advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-6)

	return observes, actions, advantages, disc_sum_rew

def log_batch_stats(observes, actions, advantages, disc_sum_rew, logger, episode):
	""" Log various batch statistics """
	logger.log({'_mean_obs': np.mean(observes),
				'_min_obs': np.min(observes),
				'_max_obs': np.max(observes),
				'_std_obs': np.mean(np.var(observes, axis=0)),
				'_mean_act': np.mean(actions),
				'_min_act': np.min(actions),
				'_max_act': np.max(actions),
				'_std_act': np.mean(np.var(actions, axis=0)),
				'_mean_adv': np.mean(advantages),
				'_min_adv': np.min(advantages),
				'_max_adv': np.max(advantages),
				'_std_adv': np.var(advantages),
				'_mean_discrew': np.mean(disc_sum_rew),
				'_min_discrew': np.min(disc_sum_rew),
				'_max_discrew': np.max(disc_sum_rew),
				'_std_discrew': np.var(disc_sum_rew),
				'_Episode': episode
				})

def main(env_name, num_episodes, gamma, lam, kl_targ, batch_size):
	'''
	Main training loop 

	Args:
		env_name: Robot model name
		num_episodes: maximum umber of episodes to run (int)
		gamma: reward discount factor (float)
		lam: lambda for Generalized Advantage Estimate
		kl_targ: D_KL target for policy update [D_KL(pi_old || pi_new)]
		bath_size: number of episodes per policy training batch
	'''
	env, obs_dim, act_dim = init_env(env_name)
	obs_dim += 1 # add 1 to obs dimension for time step feature (see run_episode())
	now = datetime.utcnow().strftime("%b-%d_%H:%M:%S").replace(":","_")  # create unique directories
	logger = Logger(logname=env_name, now=now)
	pathFolder = logger.pathFolder
	scaler = Scaler(obs_dim)
	val_func = NNValueFunction(obs_dim)
	policy = Policy(obs_dim, act_dim, kl_targ)
	acumulator = BestAcumulator()
	#TODO agregar la parte de sampling una vez que todo ande

	# run a few episodes of untrained policy to initialize scaler:
	run_policy(env, policy, scaler, logger, 5, acumulator)
	episode = 0
	while episode < num_episodes:
		trajectories = run_policy(env, policy, scaler, logger, batch_size, acumulator)
		episode += len(trajectories)
		add_value(trajectories, val_func) # add estimated values to episodes
		add_disc_sum_rew(trajectories, gamma) # calculate discounted sum of Rs
		add_gae(trajectories, gamma, lam) # calculate advantage
		# concatenate all episodes into single NumPy arrays
		observes, actions, advantages, disc_sum_rew = build_train_set(trajectories)
		# add various stats to train log:
		log_batch_stats(observes, actions, advantages, disc_sum_rew, logger, episode)
		policy.update(observes, actions, advantages, logger)  # update policy
		val_func.fit(observes, disc_sum_rew, logger)  # update value function
		logger.write(display=True)  # write logger results to file and stdout
	acumulator.save(pathFolder)
	logger.close()
	policy.close_sess(pathFolder)
	val_func.close_sess(pathFolder)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=('Train policy on V-REP environment '
												  'using Proximal Policy Optimizer'))
	parser.add_argument('env_name', type=str, help='Robot model name', default="SecondModel")
	parser.add_argument('-n', '--num_episodes', type=int, help='Number of episodes to run',
						default=1000)
	parser.add_argument('-g', '--gamma', type=float, help='Discount factor', default=0.995)
	parser.add_argument('-l', '--lam', type=float, help='Lambda for Generalized Advantage Estimation',
						default=0.98)
	parser.add_argument('-k', '--kl_targ', type=float, help='D_KL target value',
						default=0.003)
	parser.add_argument('-b', '--batch_size', type=int,
						help='Number of episodes per training batch',
						default=20)

	args = parser.parse_args()
	main(**vars(args))