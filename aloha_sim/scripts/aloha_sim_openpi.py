import sys
import os

sys.path.insert(0, os.path.expanduser('~/code/aloha_sim'))

from dm_control import viewer
import numpy as np
from aloha_sim import task_suite
from openpi_client import image_tools
from openpi_client import websocket_client_policy


class Pi0Policy:
    """Policy class that queries Pi0 server for actions."""
    
    def __init__(self, client, task_prompt, replan_frequency=10, execute_steps_per_action=5):
        """
        Args:
            client: WebsocketClientPolicy instance
            task_prompt: Task instruction string
            replan_frequency: Query Pi0 every N steps
            execute_steps_per_action: Hold each action for N steps
        """
        self.client = client
        self.task_prompt = task_prompt
        self.replan_frequency = replan_frequency
        self.execute_steps_per_action = execute_steps_per_action
        
        # State
        self.action_buffer = None
        self.action_index = 0
        self.current_action = None
        self.step_counter = 0
        self.action_hold_counter = 0
        
    def process_observation(self, obs):
        """Convert ALOHA sim observation to Pi0 format."""
        try:
            # Extract images
            img_overhead = obs['overhead_cam']
            img_worms_eye = obs['worms_eye_cam']
            img_wrist_left = obs['wrist_cam_left']
            img_wrist_right = obs['wrist_cam_right']
            
            # Extract joint states
            joint_positions = obs['joints_pos']
            
            # Create Pi0 observation
            observation = {
                "state": joint_positions.astype(np.float64),
                "images": {
                    "cam_high": np.transpose(
                        image_tools.convert_to_uint8(
                            image_tools.resize_with_pad(img_overhead, 224, 224)
                        ), (2, 0, 1)
                    ),
                    "cam_low": np.transpose(
                        image_tools.convert_to_uint8(
                            image_tools.resize_with_pad(img_worms_eye, 224, 224)
                        ), (2, 0, 1)
                    ),
                    "cam_left_wrist": np.transpose(
                        image_tools.convert_to_uint8(
                            image_tools.resize_with_pad(img_wrist_left, 224, 224)
                        ), (2, 0, 1)
                    ),
                    "cam_right_wrist": np.transpose(
                        image_tools.convert_to_uint8(
                            image_tools.resize_with_pad(img_wrist_right, 224, 224)
                        ), (2, 0, 1)
                    ),
                },
                "prompt": self.task_prompt,
            }
            return observation
        except KeyError as e:
            print(f"Missing observation key: {e}")
            print(f"Available keys: {obs.keys()}")
            return None
    
    def __call__(self, timestep):
        """Policy function called by the viewer every step."""
        obs = timestep.observation
        
        # Query Pi0 every replan_frequency steps
        if self.step_counter % self.replan_frequency == 0:
            print(f"\n=== Step {self.step_counter}: Replanning ===")
            
            # Process observation
            pi0_obs = self.process_observation(obs)
            if pi0_obs is None:
                return np.zeros(14)  # ALOHA has 14D action space
            
            try:
                # Get action chunk from Pi0
                action_chunk = self.client.infer(pi0_obs)["actions"]
                self.action_buffer = action_chunk
                self.action_index = 0
                self.action_hold_counter = 0
                print(f"Received {self.action_buffer.shape[0]} actions from Pi0")
            except Exception as e:
                print(f"Error querying Pi0: {e}")
                return np.zeros(14)
        
        # Get next action from buffer every execute_steps_per_action steps
        if self.action_hold_counter % self.execute_steps_per_action == 0:
            if self.action_buffer is not None and self.action_index < len(self.action_buffer):
                self.current_action = self.action_buffer[self.action_index]
                self.action_index += 1
                print(f"  Step {self.step_counter}: Using action {self.action_index}/{len(self.action_buffer)}")
        
        # Hold the current action for multiple steps
        if self.current_action is not None:
            action = self.current_action
        else:
            action = np.zeros(14)
        
        # Increment counters
        self.step_counter += 1
        self.action_hold_counter += 1
        
        # Handle episode end
        if timestep.last():
            print(f"\n{'='*60}")
            print(f"Episode ended at step {self.step_counter}")
            print(f"Final reward: {timestep.reward}")
            print(f"{'='*60}\n")
            self.reset()
        
        return action
    
    def reset(self):
        """Reset policy state for new episode."""
        self.action_buffer = None
        self.action_index = 0
        self.current_action = None
        self.step_counter = 0
        self.action_hold_counter = 0


def main():
    # Create ALOHA sim environment
    env = task_suite.create_task_env('TowelFoldInHalf', time_limit=80.0)
    
    # Connect to Pi0 server
    client = websocket_client_policy.WebsocketClientPolicy(host="localhost", port=8001)
    
    # Create policy
    policy = Pi0Policy(
        client=client,
        task_prompt="fold the towel in half",
        replan_frequency=10,
        execute_steps_per_action=10
    )
    
    # Launch viewer
    print("=" * 60)
    print("Launching ALOHA Sim with Pi0 Policy")
    print("=" * 60)
    print(f"Task: {policy.task_prompt}")
    print(f"Replanning frequency: every {policy.replan_frequency} steps")
    print(f"Action hold duration: {policy.execute_steps_per_action} steps")
    print("Make sure Pi0 server is running on localhost:8001")
    print("=" * 60)
    
    viewer.launch(env, policy=policy)


if __name__ == "__main__":
    main()