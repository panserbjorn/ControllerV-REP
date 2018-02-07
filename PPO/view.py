
import numpy as np
#from gym import wrappers
from policy import Policy
from value_function import NNValueFunction
import scipy.signal
from utils import Logger, Scaler
from datetime import datetime
import os
import argparse
import signal
from mySimulatedEnv import myEnv
from tensorflow.python.tools import inspect_checkpoint as chkp

def run_episode(env, policy, scaler):
	
	obs = env.reset()
	observes, actions, rewards, unscaled_obs = [], [], [], []
	done = False
	step = 0.0
	scale, offset = scaler.get()
	
	scale[-1] = 1.0  # don't scale time step feature
	offset[-1] = 0.0  # don't offset time step feature
	while not done :
		obs = np.array(obs, dtype=np.float64).reshape((1, -1))
		obs = np.append(obs, [[step]], axis=1)  # add time step feature
		unscaled_obs.append(obs)
		obs = (obs - offset) * scale  # center and scale observations
		observes.append(obs)
		action = policy.sample(obs).reshape((1, -1)).astype(np.float64)
		# print("Esta es la acción: ", action)
		actions.append(action)
		obs, reward, done = env.step(action)
		if not isinstance(reward, float):
			reward = np.asscalar(reward)
		rewards.append(reward)
		step += 0.05
	print("Acciones: ", list(map(lambda x: np.argmax(x), actions)))
	return (np.concatenate(observes), np.concatenate(actions),
			np.array(rewards, dtype=np.float64), np.concatenate(unscaled_obs))

def run_policy(env, policy, scaler, episodes):
	
	total_steps = 0
	trajectories = []
	for e in range(episodes):
		observes, actions, rewards, unscaled_obs = run_episode(env, policy, scaler)
		total_steps += observes.shape[0]
		trajectory = {'observes': observes,
					  'actions': actions,
					  'rewards': rewards,
					  'unscaled_obs': unscaled_obs}
		trajectories.append(trajectory)
	unscaled = np.concatenate([t['unscaled_obs'] for t in trajectories])
	scaler.update(unscaled)  # update running statistics for scaling observations
	# logger.log({'_MeanReward': np.mean([t['rewards'].sum() for t in trajectories]),
				# 'Steps': total_steps})

	return trajectories


def main(folderName):

	# folderName = './log-files/SecondModel/Jan-30_20_38_36'
	# chkp.print_tensors_in_checkpoint_file("{}/value_function.ckpt".format(folderName), tensor_name='', all_tensors=True)

	env = myEnv()
	obs_dim = len(env.observation_space())
	act_dim = len(env.action_space())
	obs_dim += 1  # add 1 to obs dimension for time step feature (see run_episode())
	scaler = Scaler(obs_dim)

	policy = Policy(obs_dim, act_dim, 0.003)
	policy.restore(folderName)

	trajectories = run_policy(env, policy, scaler, episodes=20)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Viewer for custom policy learning')
	parser.add_argument('folderName', type=str, help='folder of the policy log')
	args = parser.parse_args()
	main(**vars(args))